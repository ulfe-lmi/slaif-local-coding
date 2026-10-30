# 017-af round report — owner-UID native PTY qualification (ONE actual attempt: preparation refused)

Status: FAILED for the ordered native qualification. The ONE bounded
ACTUAL attempt ran once and was refused during prepare-observe while
collecting host process metadata: the operator recorded the typed
`prep-stat-malformed` refusal before any stop permission was emitted, so
the worker was never stopped and native was never launched. The three
stages have distinct measured statuses: preparation FAILED; worker stop
NOT RUN; native NOT RUN. Per the strategic decision carried in
`reviews/017-af-actual-phase-return.md`, this round performs NO source
repair, NO re-admission and NO owner retry; a later strategic
continuation owns the software repair plus a separately sealed attempt,
and never resets AF. The round's committed delivery is documentation
only (the round documentation of the ONE actual attempt) at source A
plus the manifest-only B. The FINAL locked gate and the delivery
archive/fresh/frozen proofs ran at the literal implementation head B;
the earlier private operator/runbook API/behavior preparation proofs
predate the actual attempt P and the later docs A/B and remain at
their actual scope/head (all 17 runtime helpers P-to-B unchanged is
separate evidence, not a relabeling of an earlier run as a B-head
execution). No native-ready, whole-017 or v1 delivery claim is made
anywhere in this report.

Implementation head SHA: 017c2cc7ff00907febec180665bae4e4f3ee7d0c
Report publication commit: SELF

## Protocol facts (coding protocol)
- Repository `ulfe-lmi/slaif-local-coding`; PR #25 OPEN at
  https://github.com/ulfe-lmi/slaif-local-coding/pull/25, branch
  `oap/017-cache-read-observation`, base main
  `96c790423f6f0097a56a0b12bacda8a9b6da6aba`. No second PR, no merge, no
  auto-merge (coding law). Standard round-report template as prior
  rounds.
- Round start: AE report-only SELF `f1560058c06833f850b626dda57cdbb692767c97`
  (sole parent of P). Order+active committed pre-attempt as literal P
  `622f9a7bb52980e9358d60d8220812f66f4b4c4e` (ALL10 CI checks SUCCESS at
  P; all 17 helper inputs unchanged). ONE activation control OK on the
  existing managed wait 57716 (cat 3414357) consumed once; `oap/active`
  = `017-af` selects the unique immutable order
  `oap/orders/017-af-owner-uid-native-pty-qualification.md` (18814 B,
  SHA-256 `438fda14147e6a23b741ad19275b8c333553ccec3c6293ef341419c912040fa6`).
- The concrete operator/runbook preparation was reviewed by root across
  multiple WIP rounds (the optional PTY harness was stopped per the
  strategic route decision and is preserved as unapproved WIP); the
  plan was conditionally approved in
  `reviews/017-af-actual-plan-approval.md`; the ONE actual attempt then
  ran through one managed operator session.
- After the attempt, root issued
  `reviews/017-af-actual-phase-return.md` with the full failure proof in
  `reviews/017-af-actual-failure-and-cleanup-review.json`; the
  phase-continuation control OK released the existing wait 97055
  (PID 3566032, exit 0 = exact wire OK) consumed once. Root final
  response reader 59094 (PID 3417453) stays separate and blocked until
  this canonical SELF is published plus ONE final response OK.
- Source A `a931f31430a20501a4f117a4314e6785c2553779` (round
  documentation, 8 tracked paths vs AE SELF); manifest-only B
  `017c2cc7ff00907febec180665bae4e4f3ee7d0c` is the literal
  implementation head. This report is the single report-only SELF
  commit on top of B.
- Setup/privacy/protected fixture: routine private setup only — a fresh
  locked venv (`fresh-venv-312-af-locked`, CPython 3.12.15) was created
  under the protected AF root and 18 distributions (17 applicable
  dependencies + the clean-archive B project wheel, under the
  frozen-export constraint) were installed into it; a git-archive
  extraction and `uv build` ran under the AF root
  (`archive-build-017c2cc`). The ONE actual attempt used the repo-owned
  admission state under the repository `.oap-local`. No system
  package/venv/sudo/service change, no protected Qwen/Codex state
  change; no real credential/customer material observed; the round
  evidence contains public/synthetic/seam notes, not a hashes-only
  universal claim.

## The ONE actual attempt (measured facts, distinct statuses)
- Run `30eab04899784690a3ac289b1686cb08`, operator session 17757,
  exit 1. The owner was constructed and admitted ONCE (the repo
  admission record holds exactly one attempt, status `aborted` —
  `/home/janezp/codex-work/slaif-local-coding/.oap-local/017-af/admission.json`,
  187 B, SHA-256
  `43fae6ff80a0780c28dffbd09fd3247a65e9435cec6acb10b0f0d3f4bfc4ac78`,
  preserved unchanged; the admission is exhausted, no copy/recreation/
  retry).
- Phases completed before the failure (owner evidence): artifact,
  build, build-context, collision, preflight, prepare-target, pull,
  sentinels. Actual stage stream: `s0-preflight` then `closed-failure`
  only — NO `s0-prepared`, NO stop permission or stop; baseline,
  attach, registration, native and diagnostic all NOT RUN.
- Operator closed record: `closed-failure`, reason
  `prep-stat-malformed`; `stop_issued` false / `stop_possible` false /
  `stop_recorded` false; terminal. The collector returned the typed
  `prep-stat-malformed` refusal while collecting host process metadata
  during prepare-observe; the exact original failing row was not
  captured. Read-only parser diagnosis (not a workflow replay): 454 of
  640 current host stat rows are refused because kernel rows carry
  legal pgrp 0 / session 0 / tty 0 / tpgid -1 while the pure parser
  demands positive pgrp/session — a concrete reproducible refusal
  class. Reproduced kernel rows are well-formed and legal; the
  parser's refusal token is NOT proof that host metadata itself was
  malformed, no exact unmeasured prepare-vs-observe exception stack is
  claimed, and the exact original failing row is never reconstructed.
  The operator's `prep-stat-malformed` and the owner's `cancelled` are
  kept as DISTINCT facts.
- Owner evidence (validates via production
  `validate_af_owner_run_evidence`; status `fail` / reason `cancelled`
  / `cleanup_failures` []): identity profile
  `slaif-fixture-identity-owner-uid-v1`, subject uid/gid 1001, groups
  [1001], fingerprint
  `7e5a6432d91bc873c3c3208e384efd48fac7f1bff3e8fe6b93240343cc5387b0`;
  bind_head `622f9a7`; ledger: docker_admissions 26, bytes 20009,
  healthz 1; resources: container
  `28351c9f17880b66c3b6091bc7afc47d942925b036328eef7730d64b4210dae2`,
  image `sha256:4cf4b6849b0dccea848fa527a601ef97a39649a095429207abd54efcdf29a20c`,
  create_intent `slaif-fixture-017s-prepared-3567447-0-4b6302ce`;
  teardown_proof `exact-cid-membership`; runner Python 3.12.15.
- Cleanup (root independently verified): the exact owned container and
  image were independently HTTP 404 via the verified default local
  Docker unix socket; production-owned work/control leaves are absent.
  The native protected record publication was attempted ONCE and
  raised `FixtureError` (type only, no invented deeper reason); the
  record is ABSENT; no publication retry or new destination.
- Worker state: the SAME W 598258 (birth 150182858) stayed
  running/foreground throughout, parent B 2014146 (birth 95656910)
  unchanged; NO signal, fg, monitor setter or restoration was required
  or performed; no real model/gateway request occurred.
- Retained actual bytes, preserved AS IS (0600):
  - `evidence/af-owner-evidence.json` 1358 B, SHA-256
    `2cb066c380d0b7532cc790613b522c85c57b048d58a386dec3a99d10434a93b9`
    (under the protected AF root);
  - `logs/af-operator-stage.log` 569 B, SHA-256
    `c79ab2bfa783f9bb7dcc03b17ecbb74341006ec315cc7d100d4556d6588a941f`
    (under the protected AF root);
  - the repo admission record (hash above, under the repository
    `.oap-local`).

## Verification (at literal head 017c2cc7)
- Source A vs AE SELF `f1560058`: exactly 8 tracked paths — order +
  active + six documentation files, including TWO tracked compact
  `ARCHITECTURE-for-agents.md` copies; the strategic-home third compact
  copy is outside the Git commit and was synchronized separately (all
  three byte-equal, verified). No src/ or dependency change; the wheel
  is byte-identical (142753 B, SHA-256
  `1f2ebaff444be1ae90a7f1d863f462abcc82ff28caca448e28c206699fa4b50c`);
  the sdist refreshed (1032323 B, SHA-256
  `53019ad12a132dcd73c46fee69e9e3f7b069f171cb7872e0a7ef4dd436d14993`);
  200-input development manifest verified at B
  (`uv run --frozen python scripts/dev_provenance_manifest.py --verify`
  OK).
- Locked gate 13/13 EXIT=0, GATE_DONE at B (driver umask 077; pytest
  child only umask 022; non-root UID 1001; Python 3.12.15): pytest
  3410 passed / 28 skipped (545.16 s); lock/sync/ruff/format/mypy/docs/
  build/inspect/smoke/version/compileall/prov green. Root-verified:
  `reviews/017-af-gate1-completed-review.json`.
- A/B source binding and helpers: root independently verified the
  remote A/B parents/paths, all 200 inputs, all 17 helpers/runtime
  unchanged at literal B: `reviews/017-af-AB-source-binding-review.json`.
- CI: ALL 10 implementation checks SUCCESS at `017c2cc7` (root
  verified).
- Private proofs under `/home/janezp/oap-017af-work` (manual evidence
  files 0600 / directories 0700 under 077, subject to the disclosed
  exceptions; tool-created archive/install trees under their protected
  parents keep their own tool modes):
  - Clean git archive: complete 200-input EXACT map (missing AND extra),
    all 17 `scripts/cache_native*` helper bytes == Git B, wheel/sdist
    == manifest (`archive-wheel-identity-017c2cc.json`, SHA-256
    `5d43a5e5d5025fab646865c0796fedc276c05d74d31f19a8140479e93bd739d3`).
  - Fresh LOCKED venv (CPython 3.12.15): frozen export pins
    byte-identical to the AE occurrence (18 pins, colorama
    marker-gated absent on Linux); 18 installed distributions at exact
    lock versions (17 applicable dependencies + project 0.1.0);
    installed27 functional 27/27; ACTUAL site-packages EXACT
    30-module set/bytes == wheel == Git B.
  - Frozen 21 probes: 21/21 (`all_hashes_unchanged`, `all_passed`),
    FULL per-probe stdout/stderr/exit retained 0600 (63 capture
    files); resource-probe preflight peak 1054410 B < 4 MiB bound.
  - Root independently verified the archive/fresh/frozen proofs and the
    strict normalized AST of all five verification drivers against
    accepted AE (constants/paths/descriptive text only):
    `reviews/017-af-archive-fresh-frozen-independent-review.json` and
    `reviews/017-af-verification-drivers-current-review.json`.

## Scope boundary (NOT done — never waived, never claimed)
- The ordered native qualification FAILED: preparation FAILED (typed
  refusal), worker stop NOT RUN, native NOT RUN — distinct measured
  statuses, never PASS, never waived.
- No AF source repair, re-admission or owner retry under this round;
  the AF admission is exhausted (one attempt). No actual owner re-run,
  no Docker/native/client operation beyond the ONE ordered attempt
  (the existing disposable CI jobs ran their original-scope
  Docker/Python fixture checks).
- NOT native-ready, NOT whole-017 acceptance, NOT v1-runtime delivery.
  Pure D09 collector, required-syntax audit and ALL 018-024 remain
  required and NOT RUN. The actual AD single attempt remains NOT RUN
  (017-ad PARTIAL) — inherited by reference.
- No merge, no auto-merge, no second PR; GitHub remains the remote
  software truth.

## Deviations and honest limits (bounded)
1. Gate live-context umask note: BOTH of this round's live-context
   JSONs carry the mistaken note that /proc exposes no umask —
   /proc/PID/status HAS a Umask field, and root independently measured
   the actual 0077 gate / 0022 non-root pytest (the live status/birth
   proof is the independent identity evidence). Both captures are
   preserved AS IS; the first capture
   (`live-context-FIRST-defective-pidparse.json`) additionally
   mis-transcribed leading PID digits while its recorded PPIDs retained
   full numbers (e.g. gate 575189 vs worker 98258 against PPID
   598258; uv 575330 against PPID 3575329) — the identifiers are
   inconsistent and not valid identity proof; the corrected recapture
   is `live-context.json`. No further capture or rerun was made for
   the umask-note disclosure (the PID-corrected capture already
   existed); neither capture is rewritten.
2. AF optional PTY probe WIP (stopped per the strategic route decision;
   unapproved, never a deliverable): two early failed invocations; the
   first invocation's capture bytes were lost (not retained); the
   surviving 436 B TypeError stderr is the SECOND invocation; forked
   child PID/birth/reaping were not retained, so that cleanup is
   UNMEASURED and never inferred. The index prose "first-run" is
   chronology shorthand for the retained v1 files.
3. Outside/manual captures preserved AS IS (preexistence and creation
   unknown, no historical permissions inferred): the outside 0664
   manual capture (`/home/janezp/.cache/bashman.txt`), the operator
   and probe `__pycache__` pyc objects (creating command UNKNOWN), and
   the STOP-file recreation history (first instance 10439 B / 664 /
   SHA `c53f0d17…` was removed and recreated at 077 in this cycle
   BEFORE the root preserve note; the original is NOT retained; current
   11012 B / 600 / SHA `f54180ff…` / inode 11954670 preserved AS IS).
4. This session's occurrences (honest, no repair): an en-dash
   normalization in a compact doc was caught and restored before the A
   commit; a ledger sentence split was caught and repaired before the A
   commit; `rm -rf dist` was rejected by the execution tool (never ran);
   the A-artifact build used `--out-dir` outside the repo (repo `dist/`
   untouched until the gate's step-8 build legitimately replaced it);
   the frozen-21 runner's first launch failed on a missing parent
   suite directory and its traceback was observed in the execution
   tool's output, but the on-disk stderr capture
   (`logs/suite-af22-frozen21-runner.err`) was truncated to ZERO bytes
   by the second (successful) run's shell redirection — no on-disk
   first-launch capture is retained; that file is a NEW current
   manual-file mode exception (0 B / 0664 / uid 1001 / inode
   11956694), preserved AS IS with no chmod/delete/recreate, distinct
   from the outside bashman capture and the original STOP-file
   history; its original creator/mode/time are not inferred from the
   current lstat; the corrected launch succeeded.
   the handoff's gate.sh size note (1414 B) was a transcription error —
   measured 1412 B, SHA-256
   `a1f4e9e9d06fc555119268a977004622dc12e9fc787edf6758b43f9e4a8e9488`
   (the hash is the binding fact); the fresh-venv driver's first
   adaptation had a docstring-quoting defect (preserved as
   `*-first.py`, corrected before any run). The PR body was patched
   three times total this round
   (first application, then the four pre-READY corrections, then the
   0600/0700 literal fix); all payloads, responses and remote captures
   are preserved.
5. Inherited qualifications carried by exact immutable reference only
   (not re-verified here): the AE report
   `oap/reports/017-ae-native-pty-provenance-software.md` (18614 B,
   SHA-256 `69c3723637e250d3af097c9794cc5f5fd49858181dd783e6995309d893cda343`)
   with its checkpoints 1-3 — the actual host `/dev/pts` read, the
   no-B manual invocations, the ambient-env tiny-Python controls, the
   /tmp PR-body creation/move/chmod occurrence — and its
   current-metadata mode exceptions (`gate-run-1/gate.sh` 0700,
   `logs/doccheck.out`/`doccheck.err` 0644); the AD PARTIAL report
   `oap/reports/017-ad-owner-uid-native-handoff-qualification.md`
   (11472 B, SHA-256
   `fb075eaf87cbb45241337f3a0ececcb41dae9f6141081cfb9f82fb47957d9717`):
   the pre-admission independent expected-PTY gap and encoder
   findings, with the actual AD native attempt NOT RUN; the AC/AB/AA
   chain.

## Preservation and authority
- Preserved unchanged: the AF-root operator/runbook/verify/WIP/
  checkpoints/probes/evidence and all prior-round roots; the repo
  `.oap-local/017-af` admission; the gate-run-1 records and live
  contexts (including the defective first capture); the publication
  pre-materials (PR body v1/v2/v3, payloads, responses, remote
  captures); the retained actual-attempt bytes.
- This report is a claim, not acceptance; green CI is necessary, not
  sufficient; the canonical SELF is prescribed to be verified after
  publication (pending until published). The final response OK is the
  single post-publication event after the prepared in-memory remote
  verifier passes.

# 017-y — closed readiness diagnosis and the one bounded executable-capability attempt

Objective 017, PR 25 (amend). Round id: 017-y (the unique immutable order
`oap/orders/017-y-readiness-diagnosis-and-executable-capability.md`,
sha256 `1a02cacdac78d3326272e9fea02bb6993bcd3057e58258f7cbafa765d5acc7d7`,
13284 bytes, committed at every round head). Worker: same RIGHT
early-beta/xhigh coding instance (PID 598258, pane %19). ONE control OK
consumed once (session 55802); sole response reader 45664/PID1998719.

Status: COMPLETE for the scoped 017-y round (closed readiness
diagnosis; the ONE bounded actual attempt with its closed outcome;
gates, proofs, publication). The WHOLE objective 017 (native
handoff/D09/syntax) and objectives 018-024 remain required and
unearned; nothing in this round qualifies them.

## Heads and provenance

- FINAL implementation head (B4): `ba297697b8389397d264a8197992f9c284c835bb`
- A4 `8adfe98` (verified-gone wording correction; strategic compact copy
  sync) — docs only
- B3 `2f885e8` / A3 `6c3bd80` (stage maps record the measured attempt
  outcome) — docs only; A3's overclaim ("exited on its own finite hold")
  and the unsynced strategic copy were corrected in A4
- B2 `35a3bcd` / A2 `d868b6e` (docs-consistency repair) — docs only
- A `f3c022b` / B `ea4bd75` — first CI docs-consistency failure (below)
- The ONE actual attempt is bound FOREVER to literal implementation head
  `35a3bcd7322535dd4a699efc53c0c1c62d4c942e` (B2), run
  `fbe526a3290d465298bc8da61ef2a304`; A2..A4 are docs-only over it, so the
  attempt keeps its literal B2 attribution and is never relabeled.
- No `src/` or `scripts/` change in any of A2..A4: the wheel is
  byte-identical across every Y head (sha256
  `1f2ebaff444be1ae90a7f1d863f462abcc82ff28caca448e28c206699fa4b50c`);
  only the sdist changed with the docs inputs.
- X lineage (immutable, prior round): implementation head
  `e5215ce1a96b4dbecdcca5157b6a21ef30a6b1da`, X SELF
  `fcd8610b144976c3ba5dd53db48f785d6e03249d`.

## 1. Closed readiness diagnosis (software)

On a nonzero bounded readiness exec, ONLY the fixed probe's own exact
finite closed failure record refines `controller-not-ready` as
`controller-not-ready:<cause>` (closed causes `uid-not-21001`,
`pid1-uid`, `health-unreachable`; missing/malformed/multiple/duplicate/
foreign/over-bound/contradictory output is the fixed unknown; a raw
exception or Docker failure is never a measured cause; no raw output is
persisted). The readiness failure path records NO readiness-poll count —
an UNMEASURED quantity, never a claim of zero actual readiness polls
(normative in the closed record/contract). The ONE conditional bounded
lifecycle query (only when no closed record) issues exactly one
allowlisted read-only `docker inspect` of the single finite fact
`.State.Status` on the SAME registered CID, charged to the SAME owner
ledger/END; only the closed `exited` line refines to
`controller-not-ready:container-exited`; every other status, output shape
and query failure (bounded timeout, transport failure) stays unknown —
query failure is NOT absence. A retained capability record is valid ONLY
under its canonical sealed entry (caller-created descriptors and
cross-entry pairs are closed refusals); terminal retention/qualification
propagates the entry through pass and fail, the matching record retained
FIRST and only then the pass finalization. Ten focused tests added (ci
224, local 50, exec_capability 38). First failures preserved (framing
6/14 -> 14/14; sealed pairs 2/4 -> 4/4; entry-terminal-public 1/2 -> 2/2;
lifecycle-public 4/6 -> 6/6); seven private probes 36/36 at B
(`reviews/017-y-seven-private-final-B-ea4bd757.json`).

## 2. The ONE actual bounded attempt (consumed; never repeated)

- Binding: sealed 017-y entry, literal head B2 `35a3bcd`, repository
  identity verified, admission in the 017-y namespace
  (`.oap-local/017-y`; the consumed X namespace untouched).
- Launcher: `attempt1_launcher_35a3bcd.sh` (0600, bash-invoked): umask
  077 while creating the `attempt1/` root (0700) and precreating the run
  log + stderr EMPTY 0600; THEN process-local umask 022 so the fixture
  build-context modules (Dockerfile COPY with no module chmod, then
  USER 21001) are controller-readable; every protected root/file the
  driver/owner creates uses explicit 0700/0600 modes, which survive umask
  022 unchanged. No Dockerfile/confinement/payload change; no signals.
- Window: 2026-10-27 10:25:58Z -> 10:27:23Z (85 s).
- Result: CLOSED DRIVER PASS (record
  `slaif-017y-exec-capability-driver-v1`):
  - prepare/confinement/Python-PTY complete (CID
    `74e101e9c95caef074f50ef17e103e224d4fc6945700d0dc9b0ed3e0ceb1bbce`,
    engine 29.1.3, `pty_attached` + `env_handoff_verified`, subject
    UID/GID/groups 21002, pids limit 96, 1 GiB memory);
  - capability: `process_identity` measured; subject
    pid 2118297 / uid 21002 / gid 21002 / groups [21002] / birth
    170983857, uniquely identified from the exact-CID inventory
    (pre 1 row -> post 2 rows, max 96); the CURRENT executable is the
    closed UNKNOWN (`executable_sha256` null) — not native readiness,
    not executable provenance, no proven kernel/errno cause;
  - the subject was then observed `verified-gone` after the bounded hold
    (ABSENCE ONLY — never an exit code or termination cause);
  - owner ledger (measured): docker_admissions 35, api_requests 2,
    bytes_drained 22971, healthz_attempts 1 (a recorded count, not a
    poll-total claim);
  - owner evidence `slaif-native-owner-run-evidence-v1` validated
    (sha256 `968c22287dc7f5871b7d1c569a549a738f1d128fe519786816c1a2c139c375ec`),
    supervisor converged, teardown: container and image
    `absent-verified`, descendants_after 0;
  - journal PASS; the stdout `finalized`/`retained` facts are LATER RAM
    publication facts — the immutable retained record on disk keeps
    `finalize: not-attempted` / `retention: not-requested` (retained
    first; only RAM fields mutate afterwards).
- Admission: terminal PASS at head `35a3bcd` / run `fbe526a3...` —
  never reset, retried or relabeled.
- Cleanup: exact CID and image absent (owner teardown), subject PID gone,
  work/control roots absent — independently queried after convergence.
- Root independent first-result review:
  `reviews/017-y-actual-first-result-35a3bcd.json` (root's first
  container query's uppercase comparison stayed unclassified; the exact
  lowercase missing recheck qualified it).
- Mode-context diagnosis: the real `prepare_build_context` creates the
  four byte-identical fixture modules 0644 under umask 022 and 0600 under
  umask 077 (`reviews/017-y-build-context-modes-first.json`); the
  Dockerfile COPYs them with no chmod before `USER 21001`. This is a
  STATIC accessibility hypothesis about the X `controller-not-ready`
  startup failure, NOT a proven X cause. This launch (umask 022 process
  context + explicit protected modes) started the controller normally.

## 3. X errata (append-only; X report stays immutable)

1. X section 5 final-drain evidence file:
   `reviews/017-x-final-final-drain-e5215ce1a96b.json`; the
   twelve-probe aggregate (12 probes / 74 checks at literal
   `e5215ce`) is `reviews/017-x-independent-twelve-final-e5215ce1a96b.json`.
2. X section 6 staged-registration/current-stop predicates: those proofs
   are historical V-round evidence; W qualified the same predicates 5/5
   at `5893f02`; the root post-X-SELF ten controls (52 checks) at
   `fcd8610b` is a SEPARATE later proof —
   `reviews/017-x-postSELF-prior-ten-regression-fcd8610b1449.json` — with
   the first wrapper key-schema diagnostic preserved
   (`reviews/017-x-postSELF-prior-ten-harness-diagnostic.json`).
3. X section 10 no-raw-logs scope: it scopes ACTUAL fixture/native/API
   content only; synthetic test/build/setup outputs ARE retained —
   including the X-round rc=2 setup failure
   (`oap-017x-work/installed-functional-5893f02.err`) caused by the X
   launcher's stale `wheel_control_017w.py` helper reference. That is an
   X-round fact, not a Y failure; no Y launcher invocation failed.

## 4. Gates and proofs (head-attributed)

- FIRST gate at A `f3c022b` / B `ea4bd75`: FAILED — three failed
  docs-consistency tests caused by four flagged prose locations
  (3224 passed / 28 skipped, local 541.86 s; remote job
  122124058811/run40484877576, 381.93 s); log preserved
  (`final-full-gate-f3c022b.log`); repaired in A2/B2 (checker and
  tests unchanged).
- B2 `35a3bcd`: full gate 3227 passed / 28 skipped, 548.80 s
  (`final-full-gate-d868b6ef.log`); implementation CI 10/10 SUCCESS;
  root 19 private probes 110 checks
  (`reviews/017-y-independent-nineteen-final-35a3bcd.json`); archive
  identity 197/197 inputs + 30/30 modules + both artifacts byte-identical
  to manifest; fresh-module-identity 30/30; installed27 27/27 (fresh
  venv outside the checkout); frozen21 21/21 (hashes unchanged); and the
  ONE actual attempt (section 2).
- B4 `ba29769` (FINAL implementation head): full gate 3227 passed /
  28 skipped, 549.68 s (`final-full-gate-ba29769.log`); implementation
  CI 10/10 SUCCESS (test job 122142182687/run40490275529, actual
  3227/28/356.51 s); archive identity 197/197 + 30/30 + both artifacts
  == manifest (clean git-archive BUILD reproduction, out-dir outside the
  source tree); fresh-module-identity 30/30 at the literal head
  (fresh-venv-312-b4); installed27 27/27; frozen21 21/21 (hashes
  unchanged); root 19 private probes 110 checks at the literal head
  (`reviews/017-y-independent-nineteen-final-ba297697.json`); all three
  compact copies byte-identical
  (sha256 `6ad26c92a23ef9a9d01d99ef8ecb3f17b32f70166b725c97b5dce1627d6c433f`).
  Strategic index:
  `reviews/017-y-final-artifact-and-proof-review-ba297697.json`.
- B3 `2f885e8`: the gate driver was created but the B3 gate was NEVER
  LAUNCHED (superseded by A4/B4 before execution); its precreated log
  remains empty and the driver is retained as WIP metadata.
- All named proofs verify their stated software/fake/measured scope;
  none establishes native readiness, executable provenance, D09 or a
  whole-017 claim, and the actual attempt's attribution stays B2.

## 5. Metadata audit

`/home/janezp/oap-017y-work/pre-self-metadata-audit-ba29769.json`
(self-inclusive: the audit file itself is listed with uid/mode/size; its
self-hash is explicitly omitted). Honesty notes: `__pycache__` was
CREATED 0775 (py_compile byproduct under the session umask,
inode 11822230) and was mode-repaired to 0700 before the audit — current
0700 is not creation 0700; the 0-byte `attempt1-run.err` is a valid
empty driver stderr; the /tmp deviation below is the only external
temporary path.

## 6. Y setup-failure disclosure (30-module helper)

During the B2 artifact proofs, the FIRST actual invocation of the
ephemeral 30-module fresh-identity helper failed with a subprocess
error before writing any result (observed on the live terminal at
~10:13:59—10:14Z; no retained error bytes — the ephemeral
command's stderr was not redirected to a retained file, so the exact
cause is the live observation, not a reconstructed one). The
corrected invocation produced the retained 30/30 result
(`fresh-module-identity-35a3bcd.json`, 10:13:59Z). This is a
Y-round setup failure in the ephemeral helper only: distinct from
the X-round stale-helper rc=2 launcher setup failure (section 3.3);
NO Y actual-attempt or installed27 launcher invocation failed.

## 7. /tmp deviation (exact owned path)


`/tmp/ytp-err.txt` (0600, uid 1001, 0 bytes, created
2026-10-27 09:22:08Z): probe stderr redirected outside the protected
root during early Y probe work. No ADDITIONAL /tmp metadata was created
after that earlier Y debugging; no broad /tmp scan was performed and no
foreign /tmp content was touched. (The X-round `/tmp/dbc-4` is a separate
historical X deviation.)

## 8. Unearned boundaries

- The actual Y outcome is a closed driver PASS over the Python-only
  fixture with a stand-in hold and a closed-UNKNOWN executable: it
  qualifies NOTHING about native attachment, worker stop or the native
  handoff, which remain separately authorized orders. S already earned
  its actual Python-only local Docker rehearsal, so Docker capability in
  general is not denied.
- D09 remains `NOT RUN`; all v1 runtime criteria remain `NOT RUN`; no
  native launch (including help/version), no worker stop, no host signal
  in this round.

## 9. Publication contract (GitHub)

Repository `ulfe-lmi/slaif-local-coding`; PR 25
(https://github.com/ulfe-lmi/slaif-local-coding/pull/25) OPEN; AMENDED
on the same branch `oap/017-cache-read-observation` (no second PR);
base `main` at `96c790423f6f0097a56a0b12bacda8a9b6da6aba`; starting
remote X SELF `fcd8610b144976c3ba5dd53db48f785d6e03249d`; no new PR,
no merge, no auto-merge; the activated order and `oap/active` bytes
are unchanged since activation.

Implementation head SHA: ba297697b8389397d264a8197992f9c284c835bb
Report publication commit: SELF

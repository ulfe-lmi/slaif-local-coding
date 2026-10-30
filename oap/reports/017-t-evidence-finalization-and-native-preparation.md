# OAP Report — 017-t: evidence finalization and inert native-handoff
preparation

- Objective: 017 (single objective PR #25; one PR per numeric objective)
- Branch: `oap/017-cache-read-observation` (base `main` @
  `96c790423f6f0097a56a0b12bacda8a9b6da6aba`)
- Order: `oap/orders/017-t-evidence-finalization-and-native-preparation.md`
  (SHA256 `4a1e575dd6e2931d7a0c1e567ae496bb33048523fd4657505676f2d2591b9673`,
  committed unchanged; `oap/active` = exactly the 6 bytes `017-t` + LF,
  committed unchanged)
- Implementation head SHA: 911781ef3a35577666d0a4f5300b46077ca6f67c
- Report publication commit: SELF

## Outcome (bounded, honest)

One bounded outcome: a finalized S evidence record plus a REUSABLE,
INERT preparation boundary for the later separately activated
RIGHT-pane native handoff. T performs NO native launch (including
help/version), NO worker stop, NO local Docker operation and NO new
rehearsal. The one S admission remains consumed. The S/R/Q/P reports
are immutable and were not edited. No merge, no auto-merge, no next-
order choice.

Commit chain for this round (parent of the report commit is the
implementation head):

```text
911781ef  017-t: refresh development provenance manifest (objective 017-t)  <- implementation head
d9ade801  017-t: inert native-handoff preparation, order/run binding, and evidence finalization
546d79ac  017-s: publish immutable round report (report-only)   <- S SELF, sole implementation parent of d9ade801
```

## 1. S evidence finalization (order section 1)

### 1.1 Mode-only repair (the only mutation authorized here)

Target `/home/janezp/oap-017s-work/run_frozen21.out` (inside the 0700
S work root): before — regular file, not a symlink, uid 1001, inode
11674754, mode 0664, 0 bytes, SHA256
`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
(the empty-string digest); after — mode 0600, same inode/uid/type/
bytes/hash. Type/ownership/no-link were validated first; identity
matched, so the mode was set and nothing else changed. Closed
before/after facts:
`/home/janezp/oap-017t-work/run-frozen21-out-mode-repair.json`
(0700 root, file 0600). Owned-files audit of the S/T work roots
(13 entries, nonconforming none; source archives and venv tooling
explicitly excluded and unchanged):
`/home/janezp/oap-017t-work/owned-files-audit-pass1.json`.

This file is the zero-byte nohup stdout of the first (dead) frozen21
launch attempt. It is launch output, NOT qualifying test evidence,
and is not relabeled as a pass; the qualifying frozen-21 records are
`/home/janezp/oap-017s-work/probes-final-d51f496.json` (S) and the T
runs cited in section 6.

### 1.2 Errata for the immutable S report (recorded here, S report
never edited)

a. The S active file is SIX bytes: `017-s` + LF.
b. The S `/dev/shm` and `/tmp` full modes were 01777 (mode 1023),
   not the 0777 shorthand used in the S report prose; owners were
   `0:0` and `21002:21002` respectively. The S primary closed record
   and its validator were correct; only the shorthand prose is
   corrected here.
c. `tests/test_cache_native_fixture_local.py` was tracked from the
   first S source commit `9c8bdb8`; the `305219b` manifest commit
   carried no new tests; its first observed remote CI outcome was
   the 44-error typing (mypy) failure preserved in the S report.
d. The empty auxiliary log audited in 1.1 was 0664, contradicting
   the S report's general 0600 claim; this T mode-only repair
   changed the mode with the hash unchanged. It is not qualifying
   evidence and never was.

### 1.3 Root review-wrapper interpretation disclosure (preserved)

The root's independent frozen-21 wrapper
(`reviews/017-s-independent-frozen21-d51f4967bd87.json`) reported
`overall: false` / one `valid: false` because it demanded a `passed`
key on the resource probe's measured-only
`preflight_peak_bytes` diagnostic. The underlying probe itself
passed with the typed bounded measurement
1,054,410 B < 4 MiB. The corrected interpretation validates every
assertion plus that sole measured fact from the SAME retained
execution outputs (no rerun, no frozen probe/source/assertion
edit); the original wrapper JSON is preserved as published.

All earlier invalid setup/CI results (including the S-era
contaminated in-tree-venv archive — quarantined non-proof — and the
invalid no-deps installed control) are preserved exactly as recorded
in the S report; none is turned into a pass here.

## 2. Order/run binding (`scripts/cache_native_fixture_binding.py`)

The smallest typed immutable binding a later fixture preparation
needs: one explicit opted-in run bound, BEFORE any mutation, to (1)
the exact active order ID (bounded OAP grammar `NNN-<a..zz>`),
(2) its UNIQUE committed immutable order file (exactly one
`<ID>-*.md` in `oap/orders` of the bound source tree; disk bytes
equal the committed bytes), (3) the literal committed source head
(HEAD equals it; clean worktree), (4) the repository identity
(`owner/repo` parsed from the plain-HTTPS GitHub origin form only;
the URL itself is never retained or echoed; any other host, scheme
or form — including private endpoints — is refused), and (5) a
module-minted 32-hex run identity (never a caller value).
Resolution is strictly read-only (bounded read-only git grammar:
`rev-parse HEAD`, `status --porcelain`, `remote get-url origin`,
`ls-tree`/`show` with capped, time-bounded output reads; the child
is reaped and its streams closed on every exit; any failure is a
fixed closed token), makes no GitHub/network call and mints no
authority: publication/review remains the separate strategic
pre-execution gate and source parsing never invents permission from
prose. Each order id gets its own stable one-attempt
`.oap-local/<order-id>/` namespace (atomic O_EXCL claim; a changed
head, directory or phase within the order NEVER resets the
attempt). The historical exhausted 017-s record keeps its exact
schema and exhausted state; a caller-supplied order string,
readiness boolean, arbitrary filename or new directory cannot mint
authority or reset attempts. The S CLI/default behavior, S schema
meanings and validation of the historical S evidence are preserved
unchanged.

## 3. Native-handoff preparation contract
(`scripts/cache_native_fixture_native_prep.py`, closed schema
`slaif-native-handoff-prep-v1`)

Small READ-ONLY collection/validation seams for the LATER native
path, with fixture-owner facts and external-native facts kept
SEPARATE. The owner's retained evidence (its own closed 017-s
record: exact CID, verified teardown, sentinel survival, export
sha, and its `codex_invoked` / `worker_stopped` / `native_*` flags —
the closed safety facts of the WHOLE historical S rehearsal run: a
full-rehearsal-scope statement that that run never invoked Codex,
never stopped the worker and never started a native subject; NOT an
owner-processes-only claim) is parsed into typed `OwnerFinalFacts`
under the historical S schema; the new native schema is separate
and is never an owner-only reinterpretation of those flags. The
native subject is a distinct measured `SubjectIdentity`; the
overall verdict is composed AFTER the owner's own
export/teardown finished (teardown-before-restore ordering;
nothing keeps the container alive until restoration, nothing
deadlocks finish on the stopped worker). No record can therefore
claim "Codex was never invoked" while a foreground native subject
actually ran.

Closed identity laws (finalized from this code, not prose):

- subject identity is adopted from the EXACT registered CID only
  (`source: cid-registered`); a host UID/name-only process or a
  caller-supplied bare PID is never proof; UID/GID exactly 21002
  with the closed group law (empty, or the own primary 21002 —
  strict integers only; float/bool/string/duplicate/foreign/root
  groups refused); argv EXACTLY `codex --yolo --profile
  early-beta` (value AND recomputed digest); the pinned binary
  sha256 bound to the expectation; the birth bound (`/proc`
  start_time at or after the ticks measured at run admission — an
  unobserved bound is incomplete, never ready); and the
  expected-PTY provenance — the identity records whether the
  expected PTY was actually bound (a strict NONZERO int) and
  matched; an unobserved expected PTY or a measured tty0 subject
  is `pty_matched` false and can never qualify native-ready,
  while legitimate no-TTY process parsing stays a separate
  capability.
- the registered-CID channel must be bound to the expectation's
  CID before any read is recorded, and the current executable is
  re-verified through a fresh magic-link open AFTER hashing — an
  exec in the same process with an unchanged PID/birth is a
  closed refusal, never a stale verified identity.
- worker/Bash group facts are collected READ-ONLY: worker W,
  parent Bash B, pgrp G, session/TTY relation, complete bounded G
  membership (capped enumeration; a raced-away pid is not a member,
  a malformed row is not an established stop), separately grouped
  owned tool sessions distinguished (including no-TTY children
  with legitimate tpgid -1), the actual Bash job J NEVER guessed,
  and the tty foreground pgrp a read-only observation (None =
  unobserved, never assumed); this round never signals W/G/B or
  changes foreground.
- the worker STOP and same-job RESTORATION are measured
  INDEPENDENTLY of the owner as two distinct phases: the RECORDED
  stop is the stable stopped phase — W observed in state T, B
  running, G differing from B's group, every other observed G
  member stopped, and the tty foreground observed back on B's
  group (Bash reclaimed the TTY; G does not hold the foreground
  while stopped) — a separately recorded event, never re-derived
  from a later snapshot; RESTORATION is measured AGAINST that
  receipt and holds only for the RUNNING phase: the same worker
  (pid, birth, group G, session, TTY) running again with the
  observed foreground back on G, cross-checked against the
  worker's own stat tpgid (a caller argument can never mint a
  foreground the process metadata does not show). A worker still
  stopped, a missing recorded stop, an unobserved or contradicting
  foreground, or a vanished process is honestly unknown, never
  restored.
- the verdict composes only typed measured records (or an explicit
  None): a caller-authored ready/status/flag JSON is a closed
  refusal; unknown/unobserved/incomplete facts can never be
  ready/pass, with the closed 15-reason vocabulary
  (no-owner-final / owner-teardown-unverified /
  owner-subject-context-mismatch / owner-subject-binary-mismatch /
  owner-native-unready / owner-scope-not-native /
  no-native-identity / subject-start-unbound /
  subject-pty-unmatched / subject-cid-unscoped /
  subject-binary-unmeasured / subject-absence-unverified /
  no-restoration / worker-stop-unmeasured /
  same-job-restore-unmeasured). A historical S-scope owner record
  decodes and validates under its own closed schema but can NEVER
  qualify a native-ready composition (the closed
  `owner-scope-not-native` refusal), and its flags are never
  relabeled as native facts. An honest started-but-not-ready
  native-owner record (a truthful `native_ready` false) parses but
  never becomes ready (`owner-native-unready`), and the owner's
  registered artifact binary must equal the retained measured
  subject's executable identity (`owner-subject-binary-mismatch`)
  — same CID/run strings cannot substitute for exact executable
  agreement.
- the public prepare/observe/finalize workflow invokes the
  collectors itself before recording measured state — a
  constructor or manually prepopulated record is not workflow
  evidence; there is no CLI entry, so the runtime CLI cannot
  accept a fabricated collector result (injection is in-process,
  trusted fake tests only). The workflow retains a bounded
  IMMUTABLE RECEIPT of the pre-teardown subject identity (the last
  identity measured while alive), records the stop as a separate
  measured event, never re-collects and replaces the receipt,
  never adopts a reused PID, and never infers a missing first
  observation. `finalize` binds the owner record's run id to the
  workflow's registered run, and a native-owner record must
  additionally equal the immutable workflow binding's order,
  literal source head and run, with the retained pre-teardown
  subject receipt bound to that same run (order/head/run
  mismatches are closed refusals: prep-owner-order-mismatch /
  prep-owner-head-mismatch / prep-owner-run-mismatch /
  prep-subject-run-mismatch); a historical S-scope record is not
  order/head-checked there and never becomes ready. Malformed,
  mismatched, vanished, reused/incomparable or unreadable
  identities yield closed non-echoing refusals; no raw cmdline,
  environment, API/schema/body/TUI/history is retained or
  exported (the exact pinned argv only, where the contract
  requires it).

Native-owner evidence producer (closed schema
`slaif-native-owner-evidence-v1`): the explicit
measurement-to-record boundary for a LATER native-owner run. It
invokes the owned finish/export/teardown measurement seam (the
closed read-only method set over the completed owner's measured
state — a None is unmeasured and a closed refusal, never a
default), validates the FULL measured export payload with the
ACTUAL shared export validator (the same closed
quiesce/snapshot/diagnostic/originals law the R/S finish path
applies — a recomputed digest alone proves framing integrity,
never payload validity), recomputes the export digest from the
measured payload bytes ITSELF (a supplied digest is never
trusted), and only then emits the closed record from the closed
teardown facts (present-before/absent-after on the exact CID and
image, zero descendants, sentinel survival, native started — a
run that never started native is out of this producer's scope).
The consumer validates the EXACT closed record grammar — the
exact top-level key set and the exact nested object key sets;
unknown, missing, or non-mapping fields are closed non-echoing
refusals before the record is used. The measured image id admits
only the bare 64-hex digest or the actual measured
`sha256:<digest>` form; the typed fact is the normalized bare
digest. The closed six-key measured context (order, source head,
run, CID, image, binary) must bind EXACTLY to the expected
immutable order/run binding — an incomplete (None), extra-key, or
contradicting context is a closed non-echoing refusal, never a
silent skip to caller strings. The produced record must round-trip
the closed consumer validation before it is returned. The real
owned measurement adapter (`OwnedOwnerMeasurement`) reads the
completed fixture owner's closed attribute seam (no platform
operation is re-invoked) and derives the run's native
started/ready facts ONLY from the public workflow's measured
pre-teardown subject receipt: a run with no measured subject (the
historical S scope) has no measured native start, and a caller
flag never mints one. A subject whose expected PTY was never
bound (unobserved expectation or measured tty0) — or whose
measured binary contradicts the owner's own registered artifact —
is honestly started-but-NOT-ready. The historical S record is
never relabeled or derived into this scope.

## 4. Public local proof (pure/fake + tiny exact-owned children)

- `tests/test_cache_native_fixture_binding.py` — 45 tests:
  valid active-order/source binding (strictly read-only),
  foreign/malformed/duplicate/dirty/mismatched binding refusals,
  stable attempts across head/directory/phase changes, the
  preserved exhausted 017-s record (historical schema, never
  rewritten) with shared-schema/malformed/untrusted refusals,
  the closed git grammar and bounded reads, and the closed origin
  grammar (including a reserved-documentation TEST-NET endpoint
  refusal — the fixture uses a synthetic RFC 5737 address, never
  a real host endpoint).
- `tests/test_cache_native_fixture_native_prep.py` — 117 tests:
  registration collects before recording; valid positive
  baselines plus wrong executable/argv/UID/GID/groups/CID/run/
  start/TTY/foreground/restoration and unknown/vanished
  negatives; the stop-phase versus restored-phase contrast; no
  readiness from fabricated flags; the native-owner producer
  (full shared-payload validation, measured-context binding with
  forged/incomplete negatives, the closed image-id forms,
  unmeasured/contradicted teardown refusals); the owned adapter
  whose native facts derive only from the public receipt
  (no-receipt refusal, started-but-not-ready honesty, incomplete
  measured-context refusals); the verdict's S-scope
  `owner-scope-not-native` refusal; the finalize binding law with
  the full public lifecycle positives — including the REAL owner
  finish/export/teardown code driven with fake platform
  operations over ONE coupled fake process world (the workflow
  measures the native subject while the same CID is alive,
  records the stop, the exact CID removal updates the same world
  to absent, and the same worker is restored before finalize) —
  and cross-context refusal contrasts; bounded
  enumeration/capture/diagnostics; and a static AST law proving
  no signal/Codex-subprocess surface.
- 162 tests total; the real /proc mechanics are proven with tiny
  EXACT-OWNED Python children only (each exact-owned child is
  killed by the test's own cleanup if still alive; the absent-pid
  closed negative uses the same real table); no test signals the
  real worker/Bash group or any unrelated process.

Strategic selected-AST probe verification (repo Python 3.12 venv):
11/11 T probes PASS at the formatted source, and the root
independently re-verified 13 private preparation probes plus the
frozen 21 at the literal implementation head
(`reviews/017-t-independent-preparation13-911781ef3a35.json`,
`reviews/017-t-independent-frozen21-911781ef3a35.json`); all
original assertions and valid positives preserved.

## 5. Review-repair trail (strategic reviews 1-10; defects were
real and are preserved, never hidden)

| area | first probe (defect) | repair probe (pass) |
| --- | --- | --- |
| binding file replacement | `017-t-binding-intermediate-8dc1428c8531.json` | `017-t-binding-repair-48accded21bd.json` 7/7 |
| native state semantics | `017-t-native-state-first-probe-f5b486d3bda7.json` | `017-t-native-state-repair-b5a0518fd3f6.json` 7/7 |
| stop phase | `017-t-native-stop-phase-05ff2dbebda0.json` (stable stop rejected; invalid stop accepted) | `017-t-native-stop-phase-repair-b5a0518fd3f6.json` 4/4 |
| owned sessions | — | `017-t-owned-session-repair-41cb5eb05a21.json` 4/4 |
| CID channel / exec | `017-t-cid-channel-first-243951566779.json` 4/6 | `017-t-cid-channel-repair-ea72e75468a3.json` 6/6 |
| prepare baseline | `017-t-prepare-baseline-first-b9d2d6dd449c.json` | `017-t-prepare-baseline-repair-f2351c0b6243.json` 4/4 |
| verified absence | `017-t-absence-first-4873356244cc.json` | `017-t-absence-repair-f2351c0b6243.json` 4/4 |
| owner producer payload | `017-t-owner-payload-first-b04bb5bb65e2.json` 1/5 | `017-t-owner-payload-repair-3d61632d812a.json` 5/5 |
| public context | `017-t-public-context-first-4ce839bc1529.json` 2/6 | `017-t-public-context-repair-6896a4ce56c7.json` 6/6 |
| owner agreement | `017-t-owner-agreement-first-6896a4ce56c7.json` 1/4 | `017-t-owner-agreement-repair-cb1c150c2ada.json` 4/4 |
| subject PTY | `017-t-subject-pty-first-6896a4ce56c7.json` 2/4 | `017-t-subject-pty-repair-cb1c150c2ada.json` 4/4 |

(All under the strategic `reviews/`; the unchanged probe sources
remain frozen in the strategic `probes/`.)

## 6. Final verification at the implementation head 911781e

Local gate (repo Python 3.12 venv, `umask 022` in the same shell as
every pytest invocation):

- full `tests/` suite: **3131 passed, 28 skipped, 0 failed**
  (495.02 s) — the 28 skips are the honest live-credential/service
  skips; the suite preserves the S49 local suite, the R-derived
  535, the P61 and all earlier suites;
- `python -m compileall -q src scripts`: OK;
- `ruff check .`: all checks passed; `ruff format --check .`:
  552 files already formatted;
- `mypy src tests`: Success, no issues in 116 source files;
- `scripts/docs_consistency_check.py`: OK (19 claim docs
  checked); the three byte-identical compact architecture copies
  (repo root, `oap/strategic-instructions/`, strategic mirror)
  verified equal by SHA256 at the final wording;
- `uv lock --check`: OK;
- `scripts/artifact_policy_check.py --inspect`: ok, no
  violations; `--install-smoke`: ok.

Artifacts and provenance (development state, not a release):

- source A `d9ade801a1cb0c60c45387269ca560f481e2e88a`;
  manifest B committed at the implementation head
  `911781ef3a35577666d0a4f5300b46077ca6f67c` (the only file in
  that commit: `packaging/dev_provenance_manifest.json`),
  objective 017-t, 195 complete source inputs, `--verify` OK;
- wheel `1f2ebaff444be1ae90a7f1d863f462abcc82ff28caca448e28c206699fa4b50c`
  (142,753 B) — BYTE-IDENTICAL across P, R, S and T (T touches
  no src/);
- development sdist `91a29829b547eb6b0ebad659a43b8c5f17be33454010a0b8d7bf70051a2cb992`
  (876,601 B) — legitimately differs from the S-era sdist: it now
  carries the two new public 017-t test files; developer scripts
  remain deliberately sdist-excluded;
- clean git-archive reproduction at the literal head: 195/195
  manifest source inputs present with exact bytes; 30/30
  installed Python module files byte-identical between the clean
  archive src and the fresh-venv site-packages
  (`/home/janezp/oap-017t-work/archive-wheel-identity-911781e.json`);
  and an ACTUAL `uv build` executed from the clean archive tree
  with out-dir outside the source tree reproduced BOTH artifacts
  byte-identical to the manifest and to dist/
  (`/home/janezp/oap-017t-work/archive-build-receipt-911781e.json`);
  the root independently re-verified the archive build and
  module identity
  (`reviews/017-t-independent-archive-build-911781ef3a35.json`,
  `reviews/017-t-independent-archive-module-identity-911781ef3a35.json`).

Installed-wheel functional controls (separate from identity
proof): 27/27 UNIQUE functional case checks PASS in a fresh
non-editable install of the T wheel in a Python 3.12.15 venv
OUTSIDE the checkout (`/home/janezp/oap-017t-work/installed-functional-911781e.json`;
identity: site-packages outside the repo, version 0.1.0, no repo
path on sys.path); driver diff versus R/S is attribution/identity
path only. The root independently re-verified
(`reviews/017-t-independent-installed27-911781ef3a35.json`).

Frozen 21 at the LITERAL implementation head (repo Python 3.12
venv only — the ambient python3 lacks prometheus_client; the
S-era interpreter diagnostic is preserved): 21/21 probes exit 0
with valid positives and all assertions pass; frozen baseline
hashes (strategic `reviews/017-p-probe-hashes.json`) unchanged
before/after; execution record
`/home/janezp/oap-017t-work/probes-final-911781e.json` (0700
root, 0600 file). The root independently re-executed the frozen
21 at the same literal head
(`reviews/017-t-independent-frozen21-911781ef3a35.json`).

## 7. GitHub CI

Run 40266382827 at the literal implementation head
`911781ef3a35577666d0a4f5300b46077ca6f67c`: ALL 10 required
checks SUCCESS — `test` (job 121389614531, started
2026-10-26T03:54:57Z, completed 2026-10-26T04:01:48Z, ~6m51s),
`gateway-contract`, `docker`, `docker-published`,
`operator-session`, `cache-native-containment`,
`cache-native-fixture`, `Analyze (actions)`, `Analyze (python)`,
`CodeQL`. No Codex is invoked anywhere in CI; the
`cache-native-fixture` job statically fetches, size+digest-
verifies and hashes the pinned artifact without executing it,
and its entry guard refuses any context that is not both
`GITHUB_ACTIONS=true` and `RUNNER_ENVIRONMENT=github-hosted`.

## 8. Preliminary failures preserved distinctly (pre-commit-A
WIP tree, NOT the final gate)

A preliminary full pytest on the WIP tree before commits A/B
recorded **4 failed, 3127 passed, 28 skipped** (491.38 s). The
four failures are preserved distinctly:

1. TWO REAL artifact-policy failures: the fresh-build sdist scan
   flagged the new binding test's fixture, which contained a
   real protected-host private-LAN endpoint literal in a
   refusal negative. Repaired by replacing the fixture with a
   synthetic reserved-documentation TEST-NET (RFC 5737) endpoint
   that is refused by the unchanged closed origin grammar; the
   scanner and the production validator were NOT weakened.
   `tests/test_artifact_policy.py` (7 tests, including the
   injected-violation negative controls) passes at the final
   head.
2. TWO STALE-provenance failures: the live development manifest
   was still objective 017-s/source b4fb5ef while the tree
   carried untracked T inputs, so
   `test_real_development_state_consistent` and
   `test_real_repo_source_inputs_bound_to_committed_source`
   failed on the stale/extra inputs. Resolved by committing
   source A and regenerating/committing manifest B; both pass
   at the final head.

No preliminary failure is described as a pass, waived, or
retro-fitted; the final gate in section 6 ran at the committed
candidate.

## 9. NOT RUN (explicit)

- NO native launch of any kind — including `--help`/`--version`
  — of the pinned Codex binary; the static CI hash of the
  fetched artifact is acquisition only;
- NO worker stop, NO host signal of any kind, NO TTY/job
  manipulation; the attach plan and the exact pinned argv remain
  inert documentation;
- NO local Docker operation in T; the S local rehearsal
  admission remains consumed (no second attempt);
- NO D09 (genuine native formats/collector) work;
- NO protected Qwen/vLLM/qwen-serving/model/patches/venv/flags/
  systemd/API-key/profile/auth/firewall/VPN/network/daemon
  change; no model/GPU/Gateway call, benchmark, tag, registry,
  release, deployment or cutover;
- NO merge, auto-merge, acceptance or next-order choice; the
  later serial native handoff remains a separately activated
  order.

## 10. Carried deviations and disclosures (inherited; each was
disclosed in its own round's report)

- R round A4 `git add -A` staging deviation (coding protocol
  requires exact-path staging); the resulting commit was
  verified to contain only the four intended runner/test/
  TESTING/ledger paths; disclosed in the immutable R report.
  From the first T increment onward, ALL staging in this round
  used exact-path `git add -- <paths>` only.
- Private-probe fixture corrections by the root, with
  attribution, during R and S (unfrozen private probes only;
  production validation never changed to satisfy an obsolete
  fixture); preserved in the R/S reports.
- The S-era dead nohup frozen21 launch is recorded as a dead
  attempt (zero-byte output, section 1.1), never relabeled as
  passed.

## 11. Identities and limitations

- Measured source for the S rehearsal remains the S-era head
  `2a9c44e2ee327b965828bafdfcaf444abc3a581c` (run
  `c8fed899fcc64c0faf8115dac5880080`, evidence SHA
  `a48dda367ecd62022f4fd21d359547b8c101d02ada9d69cd906c682f8fbf9dce`);
  T changes no product source, so the S measured facts stay
  bound to that head. T's software preparation is INERT: it
  earns NO real worker-stop, native identity, Docker or handoff
  qualification; every T positive is pure/fake (plus tiny
  exact-owned Python children) and no T fact is claimed as real
  native proof.
- Full objective 017 (D01-D10 complete, D09) and the v1 runtime
  rounds 018-024 remain required and NOT RUN; the legacy
  detector default is unchanged; the v1 profile is not
  implemented. Strategy owns acceptance; this report is a
  claim, not acceptance, and green CI is necessary but not
  sufficient.

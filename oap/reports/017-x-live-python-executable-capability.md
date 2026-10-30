# OAP Round Report — 017-x: live Python executable capability

- Objective: 017 (`AMEND_EXISTING_PR`; PR25
  https://github.com/ulfe-lmi/slaif-local-coding/pull/25; branch
  `oap/017-cache-read-observation`; base `main` @
  `96c790423f6f0097a56a0b12bacda8a9b6da6aba`)
- Order: `oap/orders/017-x-live-python-executable-capability.md`,
  SHA256 `ff7fa0ab32a4bf33ce07e3fdbc4393add1c265c4d75d2e647d2be9cfa7d58fe1`
  (15263 B), committed byte-unchanged in source A; `oap/active` =
  `017-x` committed byte-unchanged.
- Starting state: W SELF `9d91879ec9b169c7679c06ee82582727fea906c5`
  (report-only); W implementation head
  `5893f0241478555560f736dce4824f08ebd5cb08`; W source A2
  `8155920298bd300e7dc55289f854d821e6486980`. GitHub reconciled before
  mutation (remote PR head = W SELF; base unchanged).
- Status: PARTIAL (scoped to the 017-x order: the software layer is
  complete, tested, and verified at the final head; the ONE authorized
  bounded actual attempt was executed exactly once at that literal head
  and closed terminal FAIL before any executable measurement — a useful
  diagnostic, never a capability claim; whole 017 and 018-024 remain
  incomplete and are NOT accepted by this report)
- Implementation head SHA: e5215ce1a96b4dbecdcca5157b6a21ef30a6b1da
- Report publication commit: SELF

## 1. Outcome (bounded, honest)

This round lands the ONE bounded Python-only capability measurement the
earlier native-preparation rounds left to a separately authorized order:
a repo-owned stdlib-only driver
(`scripts/cache_native_fixture_exec_capability.py`) plus a finite
Python-only hold mode, closed, fail-closed, and honest by construction.
The driver determines, with a REAL finite fixture, whether the existing
unprivileged host CID channel can measure the CURRENT executable of an
actual UID/GID 21002 process WHILE IT IS ALIVE.

The ONE actual attempt (order section 4) ran at the literal final
implementation head and consumed the single authorized admission. It
closed terminal FAIL at owner stage `prepare-target` with reason
`controller-not-ready`, and it never reached executable-capability
measurement: the retained capability is `null`. No readable or unreadable
exe was established. Per the order, a measured unknown/refusal — here, a
closed failure before measurement — is a useful diagnostic result, never
a native-ready or full-017 success claim. The attempt is consumed; no
retry, new work root, new HEAD, new CID, or second owner was or is
authorized, and none was performed.

Naming clarification (carried from strategy): the order prose
`HostCidScopedTable` refers to the existing
`RealCidScopedTable` implementation (and its `exe_sha256` seam) in
`scripts/cache_native_fixture_native_prep.py`. That channel was reused
unchanged; no channel was added, renamed, or replaced to match the prose.

## 2. Commit lineage and provenance

```text
A  df8db3ebc06ec35abc617be94999ce1338ffdf68  driver + stand-in hold mode + docs
B1 cc3ee64fc9762d4b0ab2048c48dc2fd3f7e1f203  manifest (objective 017-x)
A2 90066b0e9344e86ab9cc8e05acd4e137fd1d768f  human-map docs, three-layer proof
                                             wording, record-out inside-work
                                             preflight, deterministic
                                             expired-budget test
B2 e5215ce1a96b4dbecdcca5157b6a21ef30a6b1da  manifest — FINAL implementation
                                             head, remote PR head at SELF
```

- Manifest B2: 197 source inputs; wheel
  `slaif_local_coding-0.1.0-py3-none-any.whl`
  SHA256 `1f2ebaff444be1ae90a7f1d863f462abcc82ff28caca448e28c206699fa4b50c`
  (142753 B, 37 entries); sdist
  `slaif_local_coding-0.1.0.tar.gz`
  SHA256 `eab23ab9d209ddc8f7a2013b6320e97868495a7e9691c6b4b8260e130e096ab5`
  (927453 B, 195 entries). Development provenance state verified at B2
  (`dev_provenance --verify` in the final gate).
- The wheel is byte-identical across the P/R/S/T/U/V/W/X development
  heads only (X touches no `src/`); earlier observation rounds changed
  source, so no wider byte-identity claim is made.
- Three compact `ARCHITECTURE-for-agents.md` copies (repository root,
  `oap/strategic-instructions/`, strategic mirror) are byte-identical at
  B2, SHA256
  `3c63f56e6bc50c459c86f40b36a2a8212e516c3e6b622a746ba5d96c56132e9d`.
- The actual attempt's literal live-attempt head is permanently recorded
  as `e5215ce1a96b4dbecdcca5157b6a21ef30a6b1da` (driver record
  `bind_head`); no later source/HEAD/work-root change re-authorizes or
  relabels it.

## 3. Software: the closed fail-closed law

- The SEALED bound child owns `resolve`+`admit` ONCE before any external
  work; the driver verifies only the child's closed protected outputs.
  Exhausted running journals are refused, never adopted; no arbitrary
  `run_id` skips admission.
- Fresh protected bootstrap startup authority: a pre-existing control
  root is a prior/foreign owner's surface and is never adopted (no
  command, no journal mutation); the published owner state is bound to
  the actual still-live sealed child PID.
- `prepare -> hold -> finish` over ONE shared owner/run/ledger/END; the
  ONE closed detached stand-in hold exec is restricted to UID/GID 21002,
  this registered CID, the exact immutable stand-in path/mode, and the
  bound run-id marker (no general detach/argv escape); at most ONE
  subject start, including failed starts.
- Bounded exact-CID discovery: the owner's guarded `docker top` is the
  closed membership authority (<=96 rows plus header, same
  ledger/deadline); the host `/proc` is never enumerated; each listed
  member is independently scoped/tri-state verified; ambiguous,
  malformed, over-bound, unreadable, or raced identity closes.
- Scoped current-executable read: at most 16 MiB and 10 s, clamped at
  measurement to the SAME remaining owner END intersected with the
  issued hold's finite lifetime, birth-bound, with before/after frame
  law; unreadable/absent exe is a closed unknown, never an
  artifact-hash fallback; only the scoped current executable may earn a
  digest.
- The owner's own bounded abort converges any pre-finish failure (never
  a host signal); expired budgets refuse before any blocking wait.
- W-order publication ordering: bound verified owner evidence retained
  first, then the driver's protected capability record
  (`--record-out` required by the CLI preflight and outside the
  disposable work root — a closed read-only refusal before any launch,
  both paths normalized absolute-lexical with no symlink resolution),
  then verified same-attempt terminal finalization on the real
  `finalized` token; refusals close `fail` with no journal pass and no
  fresh-path retry; pre-retention failure closure is distinct from
  post-retention unverified/raced finalization, which preserves actual
  facts.
- A driver `pass` is a closed truthful conclusion: an unknown or a
  refusal is a useful diagnostic, never readiness.

### The 017-x suite: 34 tests in three distinct layers

1. Real CLI admission grammar and child-owned resolve+admit law (14):
   `test_hold_and_top_public_interface`,
   `test_hold_start_failure_consumes_one_start`,
   `test_top_closed_grammar_controls`, `test_numeric_hold_token_never_coerced`,
   `test_public_cli_child_owned_resolve_admit`,
   `test_retain_record_closed_and_atomic`,
   `test_retain_record_refuses_open_schemas`,
   `test_wait_natural_exit_verified_gone_label`,
   `test_measure_unknown_executable_coherent_identity`,
   `test_measure_refuses_reused_pid_birth_mismatch`,
   `test_measure_refuses_frame_race_after_read`,
   `test_measure_refuses_subject_vanished_after_read`,
   `test_discovery_absent_verified_vs_foreign_scope_refusal`,
   `test_driver_main_closed_grammar`.
2. Scripted driver bootstrap over an actual launched Python child (12):
   `test_driver_scripted_full_positive_measures_subject_while_alive`,
   `test_driver_startup_refuses_preexisting_control_root`,
   `test_driver_startup_refuses_foreign_prior_owner_state`,
   `test_driver_failed_sealed_startup_closed_reason`,
   `test_driver_failed_hold_refusal_preserves_primary_reason`,
   `test_driver_ambiguous_duplicate_subject_refused`,
   `test_driver_identity_mismatch_refused`,
   `test_driver_foreign_and_s_scope_evidence_not_adopted`,
   `test_driver_capture_cap_forbids_pass`,
   `test_driver_capture_read_error_forbids_pass`,
   `test_driver_expired_budget_refuses_before_blocking_wait`,
   `test_driver_record_out_inside_work_refused_before_launch`.
3. In-process real public-owner measurements, including the scoped read
   BEFORE the owner finish (8):
   `test_terminal_coupled_public_owner_measures_before_finish`,
   `test_terminal_coupled_abort_converges_real_owner`,
   `test_terminal_refused_retention_preserves_original`,
   `test_terminal_unverified_finalize_preserves_running`,
   `test_terminal_foreign_run_id_not_finalized`,
   `test_terminal_resolves_capture_state_after_drain`,
   `test_terminal_coupled_cleanup_failure_refuses_pass`,
   `test_terminal_coupled_unrelated_survival_failure`.

These layers, over fake platform seams plus tiny exact-owned Python
children, are useful fake proof of the named mechanisms — real CLI
admission, scripted bootstrap with an actual child PID, and in-process
real-owner measurement — and they are NOT one full sealed-real-owner
end-to-end test. The composition is disclosed as such everywhere it is
claimed.

## 4. The ONE actual attempt (order section 4) — executed, consumed, terminal FAIL

- Literal head: `e5215ce1a96b4dbecdcca5157b6a21ef30a6b1da`
- Run: `9fd5cf1d95924a47b8bf53e8624242a5`
- Window: 2026-10-27T08:06:14Z to 2026-10-27T08:07:07Z (53 s)
- Honest driver exit: EXIT 1

Retained driver record (`attempt1/capability-record.json`, closed
schema `slaif-017x-exec-capability-driver-v1`), verbatim fields:
`status fail`; `reason controller-not-ready`; `capability null`;
`evidence_state verified-fail`;
`evidence_sha256 b0c62aa82f66c3bee5fe4c6db1673b8cf8adab0c6920140f25e0e9ade719a312`;
`terminal_command abort`; `owner_exit 1`; `reader_state drained`;
`capture_state drained`; `finalize terminal-preserved`;
`retention "not-requested"`; `run_id 9fd5cf1d95924a47b8bf53e8624242a5`;
`bind_head e5215ce1a96b4dbecdcca5157b6a21ef30a6b1da`.

Retained owner evidence
(`attempt1/evidence/native-owner-evidence.json`, closed schema
`slaif-native-owner-run-evidence-v1`), verbatim fields: `status fail`;
`stage prepare-target`; `reason controller-not-ready`;
`phases_completed [artifact, build, build-context, collision, preflight,
pull, sentinels]`; `cleanup_failures []`; `deadline_expired false`;
container `4a198ba0572b0dd23482682e8f634e1725e7efd2c55a97ccc61730afc8d49c8b`;
image `sha256:cfc8ba82582925dd0053045776cee710f5b5b77ce8f97f447f271e95c50d931d`;
`create_intent slaif-fixture-017s-prepared-1941300-0-79c2d1c0`;
ledger: `docker_admissions 20` (owned Docker API admissions during
preparation), `api_attempts 0`, `requests_admitted 0`,
`bytes_drained 10891`; runner `x86_64` / kernel `7.0.0-38-generic` /
Python `3.12.15`; scope `native-owner-run`.

Interpretation: the owner prepared the fixture (build, pull, sentinels)
but the fixture controller was never ready, so the closed path aborted
before any subject start, hold, or measurement. The attempt therefore
measured NO executable capability in either direction — the capability
is null, not "unreadable" and not "readable".

Cleanup facts, exactly as retained/verified: registered container absent
(read-only `docker ps -a --filter id=` empty), fixture image absent
(read-only, `No such image`), owner/work/control roots gone, driver exit
1, reader/capture drained, `cleanup_failures []`, `deadline_expired
false`. Honesty note: the retained records do not include a complete
host process inventory; the empty `cleanup_failures` list is reported,
not substituted for subject/sentinel process-absence proof, and no
blanket every-process claim is made.

W-law retention distinction: the immutable retained record says
`retention: "not-requested"` at retention time, while the later
RAM/stdout publication fact says `retained`. This is the W pending-bytes
versus later-publication-facts distinction; the immutable bytes were
never rewritten.

The attempt is consumed. No retry, new root, new HEAD, new CID, or
second owner occurred or was attempted; later repairs (docs, metadata
audit, PR metadata, this report) are bound to the earlier measured head
and are qualified separately.

## 5. Verification at final head B2 e5215ce

### Final local managed gate (same-shell umask 022, timeout 3600)

`3217 passed, 28 skipped in 526.81s`; compileall clean; ruff check and
format clean (564 files); mypy clean (118 source files); docs
consistency OK (19 claim docs); `uv lock --check` OK; `uv build`
completed; artifact policy inspect clean; artifact install-smoke OK
(`ok: true`, no violations, entrypoint version 0.1.0);
`dev_provenance --verify` OK at head e5215ce; terminal `GATE_COMPLETE`.

### CI (GitHub, PR25)

- First CI at initial B `cc3ee64fc9762d4b0ab2048c48dc2fd3f7e1f203`:
  9/10 SUCCESS; the `test` check FAILED (1 failed / 3215 passed /
  28 skipped, 406.61 s). Sole failure:
  `test_driver_expired_budget_refuses_before_blocking_wait` — its
  expired-budget negative used a real-clock relative anchor
  (`monotonic() - 700`) that is negative on fresh low-uptime CI
  runners, so the closed state grammar rejected it as malformed and the
  driver closed `local-driver-startup` instead of the intended
  `local-driver-patience`. Test-only repair: pin the driver's own clock
  far past a small POSITIVE published anchor so the expired state is
  proven before any I/O regardless of runner uptime; the production
  hosted-runner guard and all other assertions are unchanged. The
  failed run is preserved in this PR's history and disclosed here.
- Final CI at B2 `e5215ce1a96b4dbecdcca5157b6a21ef30a6b1da`: all 10
  required checks SUCCESS (test job 122076005968; CodeQL, Analyze
  python/actions, operator-session, cache-native-containment,
  docker-published, cache-native-fixture, docker, gateway-contract,
  test).

### Clean-archive reproduction and artifact identity

Worker actual clean `git archive` build at B2: all 197 manifest inputs
verified present and hash-equal; 30/30 installed Python module bytes
matched archive source; wheel and sdist byte-identical to manifest
(`archive-wheel-identity-5893f02.json` — stale basename, content binds
literal e5215ce). Root independently re-verified: 197 archive inputs
match manifest, 11 fixture helpers equal, both archive artifacts match
manifest, current repository dist equal, and actual fresh
site-packages 30 module bytes equal wheel/Git
(`017-x-actual-archive-artifact-review-e5215ce1a96b.json`,
`017-x-actual-fresh-module-identity-e5215ce1a96b.json`).

### installed27 (fresh venv, outside checkout)

27/27 unique functional checks PASS with `identity_ok true` (fresh
venv Python 3.12.15, site-packages outside the repo, no repo on
sys.path, version 0.1.0), from the clean-archive wheel
(`installed-functional-e5215ce.json`). The FIRST launcher run failed
with rc=2 because it referenced the non-existent helper
`wheel_control_017w.py` (the helper is `wheel_control_017x.py`); that
result is a setup failure with no product verdict and is preserved
(`installed-functional-5893f02.err/.json` — stale basename, retained as
first failure). The repaired launcher precreates its OUT/ERR at 0600
before the driver child.

### frozen21 at the literal final head

21/21 probes PASS with `all_hashes_unchanged true`, executed in the
repository Python 3.12 venv, each probe self-cloning at
`--head e5215ce` (`probes-final-5893f02.json` — stale basename, content
binds e5215ce). The resource probe's measured-only
`preflight_peak_bytes` diagnostic validated as a strict bounded int:
measured 1054410 bytes (< 4 MiB), never required as a `passed` key.

### Root independent re-execution at literal clean B2

Root independently executed twelve unchanged private probes (74
assertions, all passed; 13 checkpointed probe hashes unchanged; actual
X admission bytes preserved; head and clean tree stable):
`017-x-independent-twelve-final-e5215ce1a96b.json`, with per-probe
records `017-x-final-{hold-boundaries,owner-entry,owner-running-reentry,record-coherence,record-retention,retention-preflight,terminal-journal-coherence,terminal-lifecycle,top-inventory,bootstrap-pair,drain,exact-inventory}-e5215ce1a96b.json`.
This is the final-source attribution for the component checkpoints
below. Full artifact/proof review:
`017-x-final-artifact-and-proof-review-e5215ce1a96b.json`.

## 6. Component probe checkpoints (honest attribution)

First failures retained; repairs attributed to their WIP sources;
final-source attribution is the root e5215ce re-execution above.

| probe | first result (source) | repaired result (source) |
|---|---|---|
| capability-hold-boundaries | 4/7 @ 52f35833174d (foreign-GID accept; missing-ABS-anchor fallback; control-char token) | 7/7 |
| capability-owner-entry | 4/6 (numeric token coercion; both CLI start paths) | 6/6 |
| native-staged-registration | 2/5 @ c9edd60284b1 | subsumed into final set |
| native-staged-current-stop | 1/5 @ c9edd60284b1 | 2/5 (B-birth fix) |
| capability-top-inventory | 0/3 qualified (valid positive rejected: LIST vs TUPLES header bug; CMD-with-spaces split) | 7/7 @ d2b3abe3 |
| capability-owner-running-reentry | 3/4 (both CLI calls reconstructed the same run id) | 4/4 |
| capability-record-retention | 2/5 | 5/5 |
| capability-record-coherence | 2/13 @ d3613f21 | 13/13 @ bb00053b |
| capability-terminal-lifecycle | 1/6 @ c8aaa0c8 | 6/6 @ d3613f21 |
| capability-terminal-journal-coherence | 2/4 @ 33df27ea | 4/4 @ ab5ce24d |
| capability-retention-preflight | 8/8 @ 9fa14a8d | (final e5215ce re-run) |
| foreign-owner-bootstrap | confirmed v2 (stale prior-owner state accepted: state pid 1853618 vs live child 1853645; commands issued, PASS minted, journal RUNNING->PASS) | repaired; replay-root negative @ cf0580cc + fresh matching-child positive |

## 7. Pre-SELF metadata audit and disclosures

Explicit complete pre-SELF audit of the private X root
(`/home/janezp/oap-017x-work/pre-self-metadata-audit-e5215ce.json`,
0600, self-inclusive, 26 owned entries: 2 dirs + 24 files including the
audit itself):

- All owned metadata is 0700 (dirs) / 0600 (files) at audit time.
  Creation-time 0600 is established by umask-077 precreation for this
  session's files; for earlier-session files the current 0600 is
  verified and creation-time mode is recorded only where listed; no
  blanket 0600-from-creation claim is made.
- Initial-mode deviations, all repaired pre-SELF by exact-path,
  exact-owned mode-only operations (inodes preserved): `dbg_c.py`,
  `dbg_c2.py`, `dbg_w.py` (initial 0664, earlier X session, disclosed
  then); `final-full-gate-5893f02.log` (initial 0644 — gate driver
  created it under umask 022 without precreation; repaired 0600 this
  session preserving inode 11818582 and the live append history);
  `final_full_gate_e5215ce.sh` (initial 0711 from the launch wrapper's
  `chmod +x`; repaired 0600, bytes unchanged; scripts are invoked via
  bash); `wheel_control_017x_launcher.sh` (initial 0711; repaired 0600,
  plus the ordered content repairs — helper reference, literal-e521
  OUT/ERR names, 0600 precreation before the child — inode 11818581
  preserved); first-launcher OUT/ERR `installed-functional-5893f02.{err,json}`
  (created under umask 022, chmod 600 only after the child — NOT 0600
  from creation; retained as first-failure evidence).
- Tool outputs retain tool modes (no blanket chmod): `fresh-venv-312`
  (0755 uv venv tree), `archive-build-e5215ce` (0700 root; 0775 dist
  tool dir; 0644 wheel/sdist; 0664 archive.tar; git-archive source
  modes).
- Old-basename files with honest head attribution (never relabeled as
  W evidence): `installed-functional-5893f02.{err,json}` (first failed
  launcher run), `final-full-gate-5893f02.log` (live final gate log of
  the e5215ce run), `probes-final-5893f02.json` and
  `archive-wheel-identity-5893f02.json` (content binds e5215ce).
- `/tmp/dbc-4` (exact-path check, no broad scan): absent at audit time.
  During the SAME 017-x order (earlier X debugging, before session
  compaction — not a new OAP round) it was observed 0755 outside the
  private X root; that deviation and its removal history are preserved
  as observed. No additional /tmp metadata was created after that
  earlier X debugging. Remote comparisons throughout this round stayed
  in memory.

## 8. Append-only W record clarification (ordered)

Per the order and `reviews/017-w-decision.md` (appended here; no W
artifact rewritten):

1. W SELF was committed 03:56:58Z. A late-received qualifier request led
   to a PR body PATCH and `pr25-w-body-final2.md` /
   `pr25-w-patch3.json` creation at 03:59:48Z AFTER SELF. The feedback
   was qualified BEFORE SELF; it did not authorize post-publication
   mutation. These actions are not recast as pre-SELF. The W response
   was later properly sent once, and the same worker is waiting. The
   current PR text is accurate; its correction timing remains a
   deviation.
2. The W audit is its actual 61-file/four-directory snapshot, with
   itself named separately and the external
   `/tmp/pr25-remote-check.md` repair recorded. Root's actual scan finds
   65 W-tree files/four directories (all current-owner 0600/0700):
   additionally the audit itself, `tmp-remote-check-metadata.json`
   (pre-SELF but omitted), and the two post-SELF PR files. The
   report-draft hash in that audit is stale (21791 B versus final
   23517 B). The W audit is preserved as its actual snapshot, not a
   complete final inventory.
3. No new W mode repair is needed or authorized. The known external
   `/tmp/pr25-remote-check.md` is now 0600, inode 8500772 / 30358 B /
   SHA256
   `1d702e341d9018a99014fb548e1d878a272e66b530cc3acf899ff31ef514fb5e`,
   bytes/inode preserved by the pre-SELF repair; it was initially 0664
   outside the private root and matches the superseded public PR draft
   plus jq newline — not a private prompt/credential capture. The two
   historical U /tmp repairs and all six S preservation targets remain
   unchanged; root post-SELF S verification is retained.
4. W report section 2's original first failures, precisely attributed:
   the public-lifecycle probe showed writer refusal -> journal fail ->
   fresh-path retry misleading ready; the SEPARATE publication-boundaries
   probe showed preexisting-destination refusal -> journal still running
   -> fresh-path retry, plus unverified/raced finalization returning
   normally. Final W repairs pass both.
5. The 19 PASS / 1.26 s focused invocation was observed at the earlier
   e05 checkpoint; final-head attribution for that focused timing is not
   established by relabeling. The final 5893 full 3157 suite includes
   all 19 tests; no repeat run was made solely to manufacture timing.
   For X: the final full local gate at literal e5215ce is
   3217 PASS / 28 SKIP / 526.81 s and includes them.

## 9. Still unearned and boundaries

- The actual native attachment / worker-stop / native-handoff
  capability remains a separately authorized order (the serial
  foreground handoff; a later exact order). No stop receipt,
  native-start/ready fact, or restoration claim is earned by this
  round.
- The D09 actual-trace / multi-chunk process-completion gap remains
  NOT RUN. No v1 runtime claim; v1 runtime remains unimplemented.
- Whole 017 is incomplete; 018-024 remain required.
- The X actual attempt is consumed; its outcome (terminal FAIL before
  executable measurement, capability null) is the empirical record at
  head e5215ce and was not repeated.
- The optional measured PTY metadata belongs only to THIS Python
  attachment; it cannot become the expected PTY of a later native
  attachment, and no Python PID/executable was fed to native subject
  registration.
- Compliance: this round executed only the authorized ONE Python-only
  local fixture attempt plus read-only diagnostics; no Codex invocation
  (including help/version), no worker stop or TTY/job manipulation, no
  protected host policy change, no real model/GPU/Gateway call.

## 10. Retained evidence (private X root, per audit)

`attempt1/capability-record.json` (0600),
`attempt1/evidence/native-owner-evidence.json` (0600),
`attempt1-run.log` (0600), `final-full-gate-5893f02.log` (0600, live
final gate at e5215ce), `probes-final-5893f02.json` (0600, frozen21 at
e5215ce), `installed-functional-e5215ce.json` (0600, installed27),
`installed-functional-5893f02.{err,json}` (0600, first failed launcher,
retained), `archive-wheel-identity-5893f02.json` (0600, archive
identity at e5215ce), `frozen21-e5215ce-run.log` (0600),
`pre-self-metadata-audit-e5215ce.json` (0600, self-inclusive),
`pr25-body-final-e5215ce.md` (0600, published PR body). Strategic
reviews: the `017-x-*` evidence files listed in sections 5-6 under
`/home/janezp/codex-supervision/slaif-local-coding/reviews/`. No raw
Docker/native/API/tool logs or exceptions are retained; closed
counts/enums/digests only.

## 11. Response protocol

This report is the sole final round commit (parent = implementation
head `e5215ce1a96b4dbecdcca5157b6a21ef30a6b1da`). After push and
in-memory remote verification of report bytes, order/active bytes, and
PR head, exactly ONE response FIFO `OK` is sent and the same worker
waits for the next control signal. A truthful PARTIAL report is
synchronization, not acceptance.

# 017-ag round report — zero-group observations and inert next native entry (software-only)

Status: COMPLETE for the ordered software-only scope: (1)
well-formed ZERO pgrp/session /proc observations are separated from
execution/stop authority, (2) strict positive finite group/session
identity is enforced at EVERY authority-bearing consumer, (3) worker
ancestry and complete-inventory laws are preserved, (4) ONE inert
future canonical entry `017-ah` is sealed, and the ONE ordered
bounded READ-ONLY real-host group check was executed exactly once.
NO actual local fixture/owner/admission/Docker/native/stop/signal/
client/model operation occurred in this round. AF remains CLOSED
FAILED (its ONE admission spent forever). No native-ready, whole-017
or v1 delivery claim is made anywhere in this report.

Implementation head SHA: f6414b85a4a8510d6a13d033df68677277987b6d
Report publication commit: SELF

## Protocol facts (coding protocol)
- Repository `ulfe-lmi/slaif-local-coding`; PR #25 OPEN at
  https://github.com/ulfe-lmi/slaif-local-coding/pull/25, branch
  `oap/017-cache-read-observation`, base main
  `96c790423f6f0097a56a0b12bacda8a9b6da6aba`. No second PR, no merge,
  no auto-merge (coding law). Standard round-report template as prior
  rounds.
- Round start: AF report-only SELF
  `ca1ccd9b6f60878fb0d050500defdfdf8e1811a8` (sole parent of the order commit). ONE
  activation control OK was delivered to the existing managed wait
  55891 (Python PID 3651564, birth 182371273, parent Bash 3651546
  birth 182371271 -> SAME W 598258) and consumed once; `oap/active` =
  `017-ag` selects the unique immutable order
  `oap/orders/017-ag-zero-group-observation-and-next-native-entry.md`
  (14709 B, SHA-256 `dae1229dd9198f6493f7e02c72925360ac46db25180d17425cc2af196f4a05e6`), committed
  exactly pre-source as `05b1c50ac7d98f1200da77d49144ef0ba94470bc`.
- Root final-response reader 61951 (PID 3663946, birth 182466542)
  is separate and blocked on the ORIGINAL response FIFO until this
  canonical SELF is published plus ONE final response OK.
- Source A `5e086341de38fc1b037ad93313af304e50be1ff8`: the A-commit
  diff vs its parent P `05b1c50a` is exactly 17 source paths; the
  AF SELF -> A diff spans 19 paths when the committed order+active are
  counted;
  manifest-only B `f6414b85a4a8510d6a13d033df68677277987b6d` (A..B diff = the development
  manifest only) is the literal implementation head. This report is
  the single report-only SELF commit on top of B.
- Setup/privacy/protected fixture: routine private setup only — a
  fresh locked venv (`fresh-venv-312-ag-locked`, CPython 3.12.15)
  was created under the protected AG root and 18 distributions (17
  applicable dependencies + the clean-archive B project wheel, under
  the frozen-export constraint) were installed into it; a
  git-archive extraction and `uv build` ran under the AG root
  (`archive-build-f6414b8`). No system package/venv/sudo/service
  change, no protected Qwen/Codex state change, no real
  credential/customer material observed.

## Software repair (order items 1-3)
- PURE PARSER: the closed /proc stat parser now represents
  well-formed ZERO pgrp/session observations (e.g. kernel-thread-
  like rows) as observation data instead of refusing them; the exact
  field/length/state/comm/numeric bounds are preserved (negative,
  overflow and truncated forms stay refused; the finite upper bounds
  unchanged); no kernel identity is inferred from comm/name/UID and
  no rows are filtered; unavailable/raced/unknown metadata stays
  explicit (True = verified gone, False = present, None = unknown
  remain distinct).
- AUTHORITY CONSUMERS: every authority-bearing consumer that
  previously obtained positive group/session implicitly from the
  parser now enforces strict positive finite identity itself — the
  actual W/B group AND session facts (worker group, worker session,
  Bash pgrp AND Bash session), scoped subject and post-executable
  frames, stop receipts, restoration/native-ready verdicts,
  CID-scoped birth, member lifetime and the discovery inventory. A
  well-formed zero observation can NEVER become a signal target, a
  valid prepared handoff, a stop receipt, a registered subject or a
  restored/native-ready verdict. `_is_pid` and the shared
  execution-identity validators are NOT relaxed; the original finite
  upper bounds are unchanged; the complete inventory still inspects
  every listed row and only independently verified-gone churn is
  ignorable.
- WORKER ANCESTRY: separately grouped owned tools and worker
  descendants stay correctly bounded and independently inventoried;
  an unrelated zero-group row is classified as unrelated from
  validated metadata and never acquires ownership or authority; a
  genuine unstopped member of G still refuses a complete stop. No
  serialized historical record meaning changes.

## Inert 017-ah entry (order item 4)
- The ONE explicit future sealed entry `017-ah` (owner-UID profile;
  unique canonical future order path
  `oap/orders/017-ah-owner-uid-native-pty-requalification.md`) is
  fixed now but INERT under AG-active: the real AH order file, the
  production admission namespace (`.oap-local/017-ah`) and owner are
  ABSENT from this checkout (hermetically proven in owned synthetic
  repositories; the real AH namespace is never created); refused
  BEFORE admission under AG-active; resolvable only under its own
  active at its own unique canonical committed order path.
- It composes the EXISTING owner/guarded exact-CID/NativeOwnerRun
  and independent devpts producer APIs with the SAME frozen bounds
  (absolute 1800 s END / cumulative ledger / 600 s convergence
  grace; 320 MiB/10 s native and 16 MiB/10 s Python current-exe;
  96 slaves / 65536 drained B / 5 s devpts and 5 s subject metadata
  at use/return). No new runner, supervisor, watchdog, transport,
  privilege channel, framework, CLI or real-client collector; no
  adapter/cache/Gateway/model behavior change.
- DISTINCT identity-bearing AH tags (`slaif-017ah-owner-state-v1` /
  `slaif-017ah-native-handoff-prep-v1` /
  `slaif-017ah-native-owner-evidence-v1` /
  `slaif-017ah-native-attach-binding-v1` /
  `slaif-017ah-native-owner-run-v1` /
  `slaif-017ah-native-owner-run-evidence-v1` plus scope
  `slaif-017ah-owner-uid-scope`); the EXACT tag-pair law extends
  (AF tags remain AF-only, AH tags AH-only, even for equal numeric
  identities; cross-entry pairs refuse at the closed consumers,
  including the workflow finalization dispatcher); the ONE exact
  NON-PTY devpts probe form is admitted by the AF AND AH guards,
  selected from the owner's OWN bound order id (the AB/AD/default
  guards keep their byte-for-byte old closed forms).

## Required proof (fake seams only + the ONE host check)
- 11 new pure parser/authority cases in total: 7 in
  `tests/test_cache_native_fixture_native_prep.py` (now 159
  collected) + 2 member-lifetime in
  `tests/test_cache_native_fixture_owner_uid.py` (now 42 collected)
  + 2 in `tests/test_cache_native_fixture_exec_capability.py` (now
  54 collected).
- 6 new tests in `tests/test_cache_native_fixture_native_handoff.py`
  (now 59 collected): 2 COUPLED public-owner (the ORDER-REQUIRED
  full public NativeOwnerRun lifecycle for the AH entry over ONE
  coherent coupled fake process world carrying an unrelated
  well-formed kernel zero-group row across
  prepare/observe/stop/register/finish/restore/retention — observed
  but never adopted; plus the zero-frame authority negative) and 4
  single-layer (closed-entry mapping/data, hermetic sealed-entry,
  guard contrast, attach-codec tag-pair). EVERY started test owner
  reaped in a per-test finally before monkeypatch teardown.
- Full fixture regression: ALL eleven fixture suites 835 collected
  / 835 passed (frozen Python 3.12.15 / non-root umask 022 test
  child; pre-commit development capture —
  `captures/fixture11-ah2.out`: 835 passed in 160.93 s, exit 0).
  mypy `src tests` clean (121 source files) after ONE narrow test
  annotation (a `# type: ignore[name-defined,misc]` on the new
  `_BirthScopedTable` base line, matching the existing codebase
  convention for runtime-loaded base classes); ruff check + format
  clean.

## The ONE bounded read-only real-host check (executed exactly once)
- The existing `collect_worker_group(RealProcTable)` against
  freshly measured SAME W/B/foreground, executed EXACTLY ONCE at
  2026-10-28T20:11:51Z by `hostcheck/hostcheck01-v2.py` (0600,
  Python-B, repo venv 3.12.15) against the literal working-tree
  source: collector
  `scripts/cache_native_fixture_native_prep.py` SHA-256
  `e56d2ac28d44038958481c6b08912b6be9af9e9b55adaec01afa184bf52ea58f`
  (byte-identical to the same file at source A `5e086341` —
  verified by `git show`). Timeline: the check ran at 20:11:51,
  BEFORE the order commit `05b1c50a` (20:16:20), A (20:16:35) and B
  (20:17:14); it is a working-tree-source check and is NOT labeled
  as an A/B-head execution.
- At-use revalidation of the identified SAME W/B: W 598258 (birth
  150182858) and Bash 2014146 (birth 95656910) coherent on
  parent/TTY/comm (raw tty 34834); the TTY foreground pgrp measured
  598258 (equal to the worker pgrp). Any drift would have been an
  honest typed refusal; there was no alternative worker adoption.
- Closed facts (`hostcheck/hostcheck01.out`, 1700 B, SHA-256
  `21a63970acf923af00ada431aaba63d33ad1f447e7ce6b3b7c35e79228371a53`, exit 0, 0 stderr, elapsed 0.117 s, NO
  refusal): group 598258 has exactly ONE member (the worker, state
  S, tty 34834); `session_other_groups` = [(2014146, 1)] (the Bash
  group); `tool_sessions` = [(2014146, [the Bash itself,
  provenance unknown]) and (3729670, [two worker-descendant members
  — the check's own tool processes])]; `same_tty` true; `same_job`
  false (the foreground worker job is in its own process group —
  expected). The order anticipates that "the observation may see its
  own active, separately grouped tool process".
- Meaning: a parser traversal of actual host rows recording closed
  group/ancestry/completeness facts — never stop/subject/attach/
  native readiness, never an idle-boundary or handoff-ready proof;
  no total PID/parsed-row count was measured or claimed. Root
  independently reviewed the retained bytes.
- SEPARATE actual preflight occurrence (NOT the production check):
  a host-wide /proc name/argv candidate scan (~20:06) — the scan
  had bounded individual reads but NO total count cap — identified six codex
  early-beta candidates and selected the SAME W/B. Its derived
  summary
  (`hostcheck/preflight-discovery.out`, 1212 B, 0600) is manually
  DERIVED, not original stdout, and carries disclosed errors: a
  placeholder timestamp (20:0xZ); the 662 count is ALL /proc names
  (not numeric PID rows); the summary's tty-device derivation
  (136:2194) is WRONG — the actual tool output (136:18) is CORRECT
  for the production check's raw tty 34834; the other candidates'
  metadata remains in the actual tool history, so no universal
  unretained-beyond-summary claim is made. The summary is preserved
  AS IS and qualified, not rewritten.

## Verification (at literal head f6414b85)
- Source A commit vs its parent P `05b1c50a`: exactly 17 source
  paths (7 fixture scripts + 4 test suites + 6 documentation files
  including TWO tracked compact `ARCHITECTURE-for-agents.md`
  copies; the AF SELF -> A diff additionally carries the committed
  order+active, 19 paths in total; the strategic-home third compact
  copy is outside the Git commit and was synchronized separately —
  all three byte-equal 91404 B, SHA-256
  `df7fa46c2d0c125a7bd9b26652b3112ca4d10407dd654b3d29932b7628fe9247`,
  verified). No src/ or
  dependency change; the wheel is byte-identical (142753 B,
  SHA-256 `1f2ebaff444be1ae90a7f1d863f462abcc82ff28caca448e28c206699fa4b50c`); the sdist refreshed with the six changed
  sdist-bearing inputs (two documentation files plus the four fixture test
  suites; the sdist whitelist includes tests/ and docs/, and only
  repository scripts are excluded from both artifacts) (1047714 B,
  SHA-256 `18622aaf3faa2ce45202f9c8b2862783de12495835e78faafce790749de4af5f`); 200-input development
  manifest verified at B (`uv run --frozen python
  scripts/dev_provenance_manifest.py --verify`: state=development
  head=f6414b85).
- Locked gate 13/13 EXIT=0, GATE_DONE at B (gate-run-1; driver bash
  3733322 umask 0077; pytest 3733484 via uv 3733474, child bash
  3733468, all umask 0022, non-root UID/GID 1001; live context
  captured 2026-10-28T20:21:09Z during the run, HEAD + clean
  worktree recorded): pytest 3427 passed / 28 skipped (546.75 s);
  lock/sync/ruff/format/mypy/docs/build/inspect/smoke/version/
  compileall/prov green. Captures (SHA-256): summary.log
  `dab8f2d5829e9d89afc213a254883afc61fbf9c46b4e126fe8c2085a4c3fab10`, pytest.out `2f079a73e627fe71ccc6377cbd5fbb4e659c85af8ea2c0aef417534e843c46a9`,
  live-context.json `19b96c13a62ced213315cdd77dda3474b58dd221f69db936d23f822ec0b4bb59`, gate.sh `8d9ab40dc8f5ad7105856c3f08662761059ba531fb736dc97357d69695b12f8d`.
- CI: ALL 10 implementation checks SUCCESS at
  `f6414b85` (captured in `publication/ci-checkruns-f6414b8.json`,
  SHA-256 `1d501c71f2ca2d65d0914ef69c194c0afd2f1537da1bf2bccf21f1e757bf0434`).
- Private proofs under `/home/janezp/oap-017ag-work` (manual
  evidence files 0600 / directories 0700 under 077, subject to the
  disclosed exceptions):
  - Clean git archive: complete 200-input EXACT map (missing AND
    extra), all 17 `scripts/cache_native*` helper bytes == Git B,
    wheel/sdist == manifest, 30 wheel .py modules == source bytes
    (`archive-wheel-identity-f6414b8.json`, SHA-256 `8dc9dddf7c1d7d4c328217ab7b5f7b75cbfbe23e4d764a76fa953e7e5af56e14`).
  - Fresh LOCKED venv (CPython 3.12.15): 18 installed distributions
    at exact lock versions (colorama marker-gated absent on Linux;
    17 applicable dependencies + project 0.1.0)
    (`fresh-venv-locked-check-f6414b8.json`, SHA-256 `cb82b2449ce8767f88329ed0877e816ee2def6907c5de8b7c9225e9e7c347e39`);
    installed27 functional 27/27
    (`logs/suite-ag21-freshvenv/installed27.out`; the ACTUAL
    tool-exit evidence is the rollout tool history — call
    `call_ace738bf894b12e0`, 2026-10-28T20:33:41.049Z ->
    20:33:42.167Z, literal `WHEEL27_EXIT=0` plus
    `identity_ok True cases 27 passed 27 all True`, tool exit 0,
    root-verified — and NO on-disk `installed27.exit` file
    exists); ACTUAL
    site-packages EXACT 30-module set/bytes == wheel == Git B
    (`fresh-module-identity-f6414b8-locked.json`, SHA-256
    `032da3774709445d2ccf7c07abfd089caa61701a860bd420ec1139eed14687f9`).
  - Frozen 21 probes: 21/21 (`all_hashes_unchanged`,
    `all_passed`), FULL per-probe stdout/stderr/exit retained 0600
    (63 capture files under `logs/suite-ag22-frozen21/captures/`;
    `probes-final-f6414b8.json`, SHA-256 `7bb9884aca2d4040f60773999a8ea11e77da3b0e0a2fb3dce66e5afa3fce445a`).
  - The five verification drivers are mechanical adaptations of the
    strict-qualified 017-af drivers (constants/paths/header text
    only; AST-checked and diffed against the AF originals, with the
    adapter script retained under `patches/`).

## Scope boundary (NOT done — never waived, never claimed)
- The `017-ah` entry is INERT: NO actual AH activation, namespace,
  admission, owner or attempt in this round (nor may it ever run
  under AG).
- NO actual local Docker/fixture/owner/admission/native/client/model
  operation this round (the existing disposable CI jobs ran their
  original-scope Docker/Python fixture checks). No stop/signal/TTY
  ioctl/ptrace/privilege operation. No Qwen18020/qwen-serving/model/
  checkpoint/patch/venv/systemd/keys/profiles/firewall/VPN/network
  mutation.
- AF is CLOSED FAILED (preparation FAILED; worker stop NOT RUN;
  native NOT RUN); its ONE admission is spent forever — no retry,
  reset or re-admission.
- D09 remains NOT RUN; no native-ready, whole-017 or v1 runtime
  claim. The required-syntax audit and ALL 018-024 remain required
  and NOT RUN.
- No merge, no auto-merge, no second PR; GitHub remains the remote
  software truth.

## Deviations and honest limits (bounded)
1. Preflight scan limitations (as stated in the host-check section):
   a separate actual occurrence, not the production check; its
   derived summary is manually derived with a placeholder
   timestamp, the /proc-name count scope (not numeric PID rows);
   the scan had bounded individual reads but no total count cap;
   the summary's
   tty-device derivation (136:2194) is WRONG — the actual tool
   output (136:18) is CORRECT for the production check's raw tty
   34834; and other candidate metadata is retained in the tool
   history. The summary is preserved AS IS and qualified; the
   measured authority is the production check's raw tty 34834 and
   closed facts.
2. hostcheck driver first-creation mode exception: the first
   `hostcheck/hostcheck01.py` was created 0664 (shell umask resets
   between tool invocations); an rm/recreate attempt was
   tool-REJECTED before execution; the byte-identical
   `hostcheck01-v2.py` (same SHA-256 `76baca48a4da51d0d4d256449e48c571e19bdd10da1135b73605f5acaa469974`) was created 0600
   under same-shell 077 and is the ONLY file executed. The v1
   (0664, 3581 B, inode 11957849) is preserved AS IS, never
   executed, not repaired.
3. AG work-root mode state: the parent
   `/home/janezp/oap-017ag-work` was tightened 0775 -> 0700 DURING
   the round (NOW, not from-creation; recorded in
   `AG-boundary-tightening-note.txt`); the FIFTEEN known 0664
   manual files — the three 0664 source backups
   (`*.ag-new.py`, inodes 11957679/11957680/11957681), the three
   0664 `exec-umask022.*` captures, the first-created 0664
   `hostcheck/hostcheck01.py` (deviation 2; inode 11957849, never
   executed), the six 0664 fresh-venv step captures
   (`logs/suite-ag21-freshvenv/{installed27,lockedcheck,module}.{out,err}`,
   inodes 11958981-11958987, measured by the root's 20:48
   artifact-process review) and the two 0664 PR-body patch-payload
   files (`publication/pr25-patch-payload-017ag2.json` 7085 B /
   inode 11959919; `publication/pr25-patch-payload-017ag3.json`
   7120 B / inode 11959923) — are preserved AS IS as disclosed
   exceptions under the protected parent (no chmod/delete).
   `archive-build-f6414b8/archive.tar` is ALSO 0664 but is
   tool-created git-archive output, separately scoped, and is NOT
   a manual capture. No blanket all-600/from-creation or
   key-exposure claim is inferred from current lstat.
4. Verification-driver adapter path bug: the first
   `check_locked_versions_017f6414b8.py` adaptation retained the AF
   work-root prefix in its output path; its first run created
   `fresh-venv-locked-check-f6414b8.json` (3146 B, 0600) in the
   FROZEN AF root at 20:32. The driver path was corrected and that
   NEW file was moved to the AG root (bytes/inode preserved; a
   same-filesystem rename); the corrected checker was then rerun at
   2026-10-28T20:33:41Z and REWROTE the file at the AG root, so the
   current bytes are from that rerun (content identical to the
   retained `logs/suite-ag21-freshvenv/lockedcheck.out` capture) —
   relocation alone is not the full current-file history. No
   pre-existing AF file was modified — only the AF root directory
   mtime changed (add+remove of the new file). Disclosed, not
   repaired.
5. mypy: the first run found 2 errors on the new `_BirthScopedTable`
   base line (runtime-loaded class); fixed with the one-line
   `# type: ignore[name-defined,misc]` matching the existing
   convention; the focused test re-ran green under non-root umask
   022; mypy is clean at 121 sources.
6. First-run focused scope (retained): the 19:44:02 fixture11-ah
   command named a nonexistent test file; the MEASURED first
   refusal was "no tests ran in 0.01s; ERROR: file or directory not
   found: tests/test_cache_native_fixture_runtime_profile.py",
   child-exit=4 (the command also named a nonexistent
   fixture_driver.py, which is NOT the measured first missing-file
   cause); the 19:44:17 glob rerun on the SAME capture paths
   overwrote the first missing-file stdout/stderr/exit — no
   reconstruction is claimed; those pytest invocations lacked an
   explicit -B (subsequent manual Python invocations use -B; no
   rerun for the label alone; no pyc deletion). The first focused
   capture `captures/fixture11-ah.*` (1F/834P — old mapping
   expectation) is preserved as pre-fix history.
7. Inherited qualifications carried by exact immutable reference
   only (not re-verified here): the AF report
   `oap/reports/017-af-owner-uid-native-pty-qualification.md`
   (16711 B, SHA-256 `3587af147c57819f508ffb8e57feee54421f70b603db444fb85c6a9bfd58fd98`) with its
   checkpoints and current-metadata mode exceptions; the AE report
   `oap/reports/017-ae-native-pty-provenance-software.md` (18614 B,
   SHA-256 `69c3723637e250d3af097c9794cc5f5fd49858181dd783e6995309d893cda343`)
   with its checkpoints 1-3; the AD PARTIAL report and the
   AC/AB/AA chain.
9. Premature canonical-path report occurrence: the draft report
   was created and edited IN PLACE at the canonical repository
   path (`oap/reports/017-ag-zero-group-observation-and-next-native-entry.md`,
   UNTRACKED, unapproved) during round work and was rewritten to
   21331 B and then 21532 B (the 20:52:31Z rewrite). The root
   measured 21331 B / inode 6848708 / SHA-256 `cd14c4749816495cdd156aa926c6647c9f4f8ded051d2114b6eb181d1b99511f`
   in its 20:48 review and retained an exact 21532 B snapshot at
   the strategic `reviews/017-ag-premature-report-observed-fb1573b1c1d8.md`.
   Canonical editing stopped on the root's 20:52 instruction; the
   file was then relocated to this private publication draft at
   20:53Z (same-filesystem rename; inode 6848708 and mode 0600
   preserved), leaving the canonical ABSENT and the tree clean.
   The 20131 B and 21331 B on-disk versions are NOT attested
   retained; the 21532 B bytes are preserved as the observed
   occurrence (this private draft plus the root snapshot). The
   final approved draft is a SEPARATE private file; no approved
   canonical publication or report-only SELF has occurred.
8. Executed archive-driver metadata qualification: the top
   docstring of the executed
   `patches/archive_identity_017f6414b8.py` retains stale
   AF/`017c2cc`/documentation-only prose because the adapter's raw
   header `.replace` did not match (not every replacement was
   asserted); the executable HEAD/paths and the current JSON head
   are correctly AG B. The driver and its result are preserved AS
   IS, with no rewrite/recreation/rerun solely for prose. The
   executed archive JSON `scope` field still says "two
   sdist-bearing inputs"; that prose is preserved as-is and
   qualified here: the actual complete 200-input map shows SIX
   changed inputs vs AF (two documentation files plus the four
   fixture test suites, all sdist-bearing under the pyproject
   whitelist; only repository scripts excluded), re-verified by a
   sdist-vs-sdist content diff (exactly those six entries differ;
   no entries added or removed). The stale header's docs-only /
   test-excluded causal claim is not repeated.
10. Publication-package WIP history: the pre-publication
   mechanical files (index, READY, AST-identity facts) were
   regenerated during package preparation. The FIRST READY
   occurrence (36152 B, SHA-256
   `f4e68438c50236e29c579f5b1f5d33657c6f0d8ee0e289bb55e7a3859506b228`)
   was regenerated in place and is NOT retained; the retained
   prior versions are exactly the named files (the first/second
   defective-parse and first/second index occurrences, the two
   retained READY files - READY-for-strategic-review-FIRST.json
   (an in-place regeneration of the first READY occurrence) and
   READY-for-strategic-review-SECOND.json - the FIRST/SECOND/THIRD
   AST-identity facts, the submitted v2 draft, the observed
   premature-canonical occurrence). No broader retention claim is
   made.
11. pytest --basetemp residue tree (`pytest-abfail`, focused AB
   reproduction run): included in the mechanical index — 65
   regular files in the hash table and 48 directories in the
   directory metadata; its TWO exact owned test artifacts (one
   same-root symlink `test_ab_unknown_executable_sticurrent` and
   one Unix socket
   `test_ab_unknown_executable_sti0/au/o/docker.sock`) are
   separately inventoried by lstat/type/mode/inode only, with no
   content hash and no open/follow/connect/deletion. A root
   read-only `/proc/net/unix` exact-path check (28129 B bounded
   registry) found NO current matching entry for the socket — a
   registry observation only, not a process/cleanup/
   termination-cause claim.

## Preservation and authority
- Preserved unchanged: the AF work root (frozen; the one
  mistakenly created+relocated file is disclosed in deviation 4 —
  no pre-existing AF file modified); all prior-round roots; the
  repository `.oap-local/017-af` admission (exhausted); the
  gate-run-1 records and live context; the hostcheck driver v1/v2
  and captures; the preflight summary; the publication
  pre-materials (PR body draft + before/after remote captures,
  payload, response); all AG captures.
- This report is a claim, not acceptance; green CI is necessary, not
  sufficient; the canonical SELF is prescribed to be verified after
  publication (pending until published). The final response OK is
  the single post-publication event after the prepared in-memory
  remote verifier passes.

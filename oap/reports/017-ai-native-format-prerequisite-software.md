# 017-ai round report — hermetic AG test repair and ONE sealed INERT `017-aj` native-format entry (SOFTWARE ONLY; locked gate PASS-13of13; 10/10 CI at implementation head)

Status: COMPLETE for the ordered software scope. Both bounded prerequisites
are delivered: (1) the AH-preserved hermetic CI failure is repaired in-test
with no production change, and (2) ONE explicit future `017-aj` native-format
capture entry exists in the closed production map, proven INERT under
AI-active, with the closed format scenario, selected-frame capture law,
owner-FIRST retention receipt and AJ qualification journal gate implemented
and tested hermetically. NO actual AJ order/namespace/admission/owner/native
was created; no native-ready, whole-017 or v1 runtime claim is made anywhere
in this report. Actual AJ format capture belongs to a separately activated
017-aj after software review.

Implementation head SHA: 1f1d19165df0cd7a2161e7c9c5a6be9a3012469b
Report publication commit: SELF

## Protocol facts (coding protocol)
- Repository `ulfe-lmi/slaif-local-coding`; PR #25 OPEN at
  https://github.com/ulfe-lmi/slaif-local-coding/pull/25, branch
  `oap/017-cache-read-observation`, base main
  `96c790423f6f0097a56a0b12bacda8a9b6da6aba` (fetched and verified this
  round), head = implementation B. No second PR, no merge, no auto-merge
  (coding law). The PR body was amended this round from the AH round
  description to the current 017-ai state (PR identity, branch, base and
  checks unchanged by the edit).
- ONE activation control OK consumed once on the existing managed wait
  (handle 46330 / Python PID 3914557 / birth 184579268). `oap/active` =
  `017-ai` selects the unique immutable order
  `oap/orders/017-ai-native-format-prerequisite-software.md` (24278 B,
  SHA-256
  `51fb00f8ecb5e2dfcf4508b415a084c4633696057bbfc7b2ede9d4b56bc401c4`);
  order + active (7 B, SHA-256
  `ca32fa2b29f07dbb2ee638840e9e34630920f199c8d8dc2192ff17df9a7da618`)
  committed unchanged at source A; remote activated bytes independently
  re-verified at delivery head (root record
  `reviews/017-ai-delivery-head-review.json`).
- SAME RIGHT worker W598258 (birth 150182858) / Bash 2014146 throughout;
  no new coding client, pane, subagent, CI or background reader; normal
  compaction with durable OAP records as continuity. ROOT's final response
  wait 85068 (Python PID 3919063 / birth 184649886) stayed live and
  root-owned for the whole round; coding never polled it.
- Prior-round acceptance is referenced, not duplicated: AH delivered its ONE
  actual owner-UID native PTY requalification PASS at qualified scope as an
  immutable PARTIAL (report
  `oap/reports/017-ah-owner-uid-native-pty-requalification.md`, strategic
  decision `reviews/017-ah-decision.md`); AF remains CLOSED FAILED; the AH
  native admission is spent forever and was never touched.

## Ordered scope and changes
### 1. Hermetic AG test repair (the ONE preserved CI failure)
`tests/test_cache_native_fixture_native_handoff.py::test_ag_ah_refused_under_ag_active_before_admission`
ended by asserting real-checkout ABSENCE of the AH order/admission — a premise
AH activation itself invalidated. It now proves the identical law (AG-active
refusal, AH own-active canonical-path acceptance, foreign-path refusal,
pre-admission no-journal/no-claim) over owned hermetic synthetic repositories
with a trap that the real spent namespace is never touched. No production
change; no skip/xfail/conditional bypass; no weakening of any validator.

### 2. ONE sealed INERT `017-aj` native-format capture entry
- Canonical future entry fixed in the closed production map (reserved path
  `oap/orders/017-aj-native-process-format-qualification.md`); rejection
  before admission is proven hermetically; `017-aj` order file, namespace,
  admission, owner or native were NEVER created (`.oap-local/017-aj` verified
  absent); the entry is INERT under AI-active and cannot be selected by
  ambient env, HTTP payload or caller flags — only the trusted owner's own
  verified frozen binding selects the scenario, before startup.
- Closed deterministic format workload: ≤8 immutable synthetic seeds /
  128 KiB; four serial cases (complete exit-0 literal read; genuine
  initial-running exec with causally associated empty-stdin `write_stdin`
  results and output in multiple observed NONEMPTY chunks; successful empty
  output; deliberate bounded truncation with actual formatter evidence);
  ≤16 issued semantic calls (4 exec + ≤12 empty-stdin polls), ≤20 model
  POSTs, 1 MiB per inbound body, 256 KiB TOTAL SERIALIZED selected record,
  forced sleep ≤5 s; original 1800 s END, cumulative ledger and 600 s
  convergence grace unchanged; one outstanding exec at a time.
- Strict real pinned text-wrapper grammar parsed/verified against immutable
  seeds (pinned official source, not an invented JSON protocol); observed
  chunk grouping only (no declared transport boundaries); truncation as
  formatter/token-policy-driven typed fact (no fixed byte cut); exact
  received wrappers retained (no digest-only reconstruction); unknown text
  becomes fixed safe metadata or typed refusal.
- Owner-FIRST retention receipt: `_evidence_retained` is set only after the
  SAME completed owner's protected writer returns verified success; AJ native
  publication refuses before any capture destination when it is not actually
  retained (path existence or precomputed digest is not origin). Distinct
  PARTIAL snapshot form retains only verified frames with honest pending
  facts and never mints qualification. AJ qualification journal gate: PASS
  requires cleanup-pass AND native-ready AND strict full four-case format
  qualification AND protected retention; safe partial closes the journal
  FAIL, cached outcomes can never later upgrade it; owner evidence FIRST,
  selected capture SECOND, journal LAST; one-shot, no fresh-path retry.
- Historical default/diagnostic/stand-in entries, tags, validators and
  consumed namespaces keep exact meanings; all guards and historical consumer
  behavior preserved and tested.

Source A `8264dfe5db12c7b61cdca1c3f8c9111272c23a99` (sole parent = AH
report-only SELF `c1268486325e451610d625825a3f6daa48f71f7b`) changes exactly
24 paths (+12454/−232): 10 `scripts/cache_native_fixture_*` helpers (binding,
ci, controller, export_client, local, model, native_owner, native_prep,
runtime_profile, standin); 6 test files including NEW
`tests/test_cache_native_fixture_format_capture.py`; 6 doc paths (human
`ARCHITECTURE.md`, compact `ARCHITECTURE-for-agents.md` + tracked
`oap/strategic-instructions/` copy, `TESTING.md`,
`docs/CACHE-OBSERVATION-CONTRACT.md` 017-ai bullet under existing 11p,
`docs/CACHE-REWORK-LEDGER.md` 017 suffix); `oap/active`; the new order. No
adapter/runtime/gateway/model/cache-compiler/image behavior change; no
dependency, lock or CI-workflow change; no new runner/supervisor/watchdog/
transport/service/privilege channel/generic executor/framework.
Manifest-only B `1f1d19165df0cd7a2161e7c9c5a6be9a3012469b` (sole parent A)
changes exactly `packaging/dev_provenance_manifest.json` and is the
implementation head.

## Verification
### Prescribed locked 13-command gate at clean B — PASS-13of13, run ONCE
1. `uv lock --check` OK · 2. `uv sync --frozen --extra dev` OK ·
3. `uv run --frozen ruff check .` OK · 4. `ruff format --check .` OK
(592 files) · 5. `uv run --frozen mypy src tests` OK (122 files) ·
6. `docs_consistency_check.py` OK (19 claim docs) ·
7. nonroot 022 child: `uv run --frozen pytest -q` →
**3663 passed, 28 skipped, 0 failed in 578.17 s** · 8. `uv build` OK (before
inspect/smoke) · 9. `artifact_policy_check.py --inspect` OK ·
10. `--install-smoke` OK (fresh noneditable install, entrypoint
`slaif-local-coding 0.1.0`) · 11. Python 3.12.15 · 12. `compileall -q src
tests oap/bin scripts` OK · 13. `dev_provenance_manifest.py --verify` OK
(state=development head=1f1d1916).
Mode law measured while running, not inferred from script text: the actual
driver shell PID 77571 (uid 1001, umask 077) and the uv process 77701
(uid 1001, umask 0022) were live-observed by root via /proc. The gate's own
self-report lines name transient Python reporter processes (77574 for the
driver umask report, 77703 for the child umask-022 self-report), which are
not the long-lived driver or pytest. The actual pytest child PID 77706
(PPID 77701, UID 1001×4, Umask 0022, exact pytest argv in memory) was
directly observed by root's bounded all-thread direct-child read at
12:30:24Z with birth rechecked; an earlier 12:29:30 leader-thread-only
child lookup had not yet seen the pytest child, and the script's own t+3s
sample caught uv. All observations are retained
(`reviews/017-ai-final-gate-live-context.json`,
`reviews/017-ai-final-gate-live-pytest-context.json`). Precreated 0600
captures under the private AI root: `ai-final-gate-13.{out,err,exit}`
(paths/sizes/full SHA-256/uid/mode in the protected inventory below). Capture
shape is three aggregate out/err/exit files plus per-step success markers —
not 39 per-step files. The pre-existing pytest garbage-cleanup warnings in
stderr (sealed synthetic defect seeds, nonroot) are retained as-is; no
warning-free claim.

### Clean archive and artifact evidence
`git archive` at literal A extracted to a protected 0700 private tree
(772 files): all **201** manifest source-input hashes verified against the
extraction; all 17 helper files (14 Python + 3 Dockerfiles) byte-equal
across Git A, Git B and the clean tree. BOTH artifacts rebuilt FROM the clean
tree into a protected fresh outdir (clean-build call exit 0, same-shell 077,
root-reviewed) and are **byte-identical to the B manifest**: wheel 142753 B
SHA-256 `1f2ebaff444be1ae90a7f1d863f462abcc82ff28caca448e28c206699fa4b50c`
(37 entries; 30 .py source entries byte-exact vs the clean tree) and sdist
1118156 B SHA-256 `d212aa938b26f3ca125d0f6ce0ed3827fbe8e20ede97d2f9cdc84092eac39ba3`
(199 entries = 198 source-bearing entries byte-exact vs the clean tree + 1
generated `PKG-INFO`; generated sdist metadata equals wheel metadata). The
wheel is byte-identical to the AG-qualified wheel, whose fresh locked
installed-functional evidence is referenced at its real qualified head
`f6414b85` with measured byte equality — not rerun or relabeled. Entry-level
verification captures: `ai-clean-A-entry-verify.{out,err,exit}` (in the
inventory below). Independent root-only read confirmed every fact above
(`reviews/017-ai-artifact-independent-review.json`).

### CI at implementation head B (all 10 required checks SUCCESS)
`test`, `docker`, `docker-published`, `operator-session`,
`gateway-contract`, `cache-native-fixture`, `cache-native-containment`,
`CodeQL`, `Analyze (python)`, `Analyze (actions)` — all completed success on
PR25 head B (GitHub run 40872212531, 2026-10-29T12:18:43Z), independently
re-verified by root. The superseded CI run at A (8264dfe) failed only the
dev-provenance record-present rehearsal in `docker`/`test`/
`operator-session`, by design: A still carried AH's development manifest
binding AH source; B refreshes it. No production defect is indicated by the
superseded run.

### Focused development evidence (incremental, preserved)
During development, focused suites ran and passed at their actual scopes,
e.g. new `test_cache_native_fixture_format_capture.py` 176 passed, native
handoff 84 passed, owner/standin/controller/ci/binding/identity/native_prep/
native_owner/exec_capability/local suites in the 12-suite regression
(1071 passed at the pre-final state), plus the small AJ gate/lifecycle
focused sets. Deadline (END at use/return), budget-exhaustion and
clock-sensitive controls are proven with injected fake clock/ledger values
in closed synthetic worlds, not measured wallclock crossings. The
full-suite 3663-passed gate run supersedes them; earlier preserved failures
(11-failure module-coherence regression, 1-failed consumer-typed control,
first gates0664 run) are disclosed below and remain preserved as-is.

## Live model/service evidence
NONE this round: no real model or Gateway call, no real local Docker, owner,
admission, native or host-signal operation, no TTY/PTY operation. All owner
lifecycle evidence comes from owned synthetic fake process worlds started and
reaped inside tests with global owner-UID scans and real
Docker/native/startup trapped. Protected live host (Qwen 18020, qwen-serving,
model/checkpoint/quantization/context/tool/reasoning/prefix-cache flags,
venv/patches, systemd units, keys, firewall/VPN/routing/network, existing
Codex profiles) untouched.

## Local setup/dependencies
Python 3.12.15 / uv 0.12.5, repo-owned `.venv`, `uv.lock` unchanged (gate
CMD1/CMD2 clean); no new dependencies. Many manual source-generation/verification
Python invocations were observed using `-B`; no universal `-B` compliance is
claimed for every manual Python process in the round. The prescribed gate
commands ran exactly as ordered, keeping their stated purposes. One early
manual pytest invocation erroneously passed `-B` (not a pytest option) and
exited 4 with no tests collected — preserved as a CLI error, not a result.

## Documentation
Six doc paths at A update the exact software-only boundary and AH
qualifications: human `ARCHITECTURE.md`; compact `ARCHITECTURE-for-agents.md`
(round paragraph + 017-ai law); `TESTING.md`; observation contract 017-ai
bullet under existing 11p (closed format scenario, selected-frame capture,
owner-FIRST retention, qualification journal gate); rework ledger 017
suffix. All three compact copies are byte-equal (106864 B, SHA-256
`1a508c91add41ada2a97b27f89903c85985f4540ec59aa98cc6f4ea63e63eab3`): repo,
tracked `oap/strategic-instructions/` copy, and the strategic-home third
copy (synchronized outside Git under same-shell 077, existing inode/mode
preserved). `docs_consistency_check.py` OK (19 claim docs).

## Process qualifications (disclosed; files preserved AS-IS, no chmod/delete/overwrite)
Group A — manual same-shell `umask 077` omissions (files created 0664 uid 1001
under the protected AI root or repo root; modes preserved, test passes stand
at their actual scope):
- 9 focused-run captures: `ai-focused-aj-finalize-unverified`,
  `ai-handoff-f6e-finalize`, `ai-mypy-finalize-test` (.out/.err/.exit each).
- `ai-full-fixture-regression4.{out,err,exit}` (1071 passed run).
- `WAI/tmp/pr25-edit.json` (6887 B, 0664) — PR body REST payload.
- Earlier-session: `WAI/logs/splice-c1c2.py`; pinned source
  `out-trunc.rs`/`str-trunc.rs` (context.rs is 0600); `ai-focused-aj-gates`
  first-run captures (1 failed / 2 passed).
Repo-root untracked, preserved and staged around (never `git add .`): the six
`logs-ai-focused-model{1,2}.{out,err,exit}` (0600) and `.bgpid` (13 B, 0664,
2026-10-29T12:03Z): a background-job PID written by a mis-scoped
redirection (the backgrounded `&&` list left `$D` unset, so the write landed
at the repo root); the exact final state of that backgrounded job is not
retained, so no killed-job outcome is claimed.
- The unpublished first-draft report file (`WAI/tmp/report-017ai-draft.md`)
  was mutable working material: during draft revision it was modified in
  place, and one interrupted non-truncating write left it mixed (earlier
  bytes plus a tail). Its current bytes are preserved AS-IS; no earlier
  version was recovered; no canonical OAP artifact was affected (the
  canonical report, once approved, is the fresh frozen draft).
Group B — bounded setup deviations, no exposure claim:
- One `tempfile.mkdtemp()` chmod probe ran outside the AI root (known
  synthetic; cleanup issued). A failed `cd` to a nonexistent `/tmp/claude…`
  short-circuited (`&&`) and created nothing. A first clean-archive
  extraction (call `call_bae58bc4bbc9c7f3`) used `subprocess.run(check=True)`
  WITHOUT `capture_output`, emitting raw committed repository archive bytes
  to tool stdout; the second captured extraction of the same literal A is the
  valid proof. No complete raw-log compliance is claimed; no secret/customer
  exposure is inferred and no historical corpus was inspected, reprinted or
  cleaned.
- One durable seed test once directed seeding at a wrong model patch and
  failed FileNotFound on its OWN tmp root; the exact misdirected target and
  outcome were NOT retained (possible write under the default
  `/tmp/slaif-format-seed`), and no inspection/cleanup/chmod of that path was
  performed. Known synthetic; no customer/credential exposure evidence.
- One broad regression (11 failed / 1054 passed) was preserved as-is before
  the narrow new-test loading/patch-target coherence fix; the earlier
  19-teardown-errors were attached to the same 19 seed cases, not extra
  tests. An out-of-domain `mypy` probe (the `scripts/cache_native_fixture_native_prep.py` helper appended to the prescribed `src tests` domain) is preserved as a failed probe; the
  prescribed domain stayed unchanged and passed. The aborted first
  regression4 launch (nohup variable-scope error) produced no retained
  output; its job's exact final state is not claimed. Two failed
  splice-script writeups remain under `WAI/scripts`.
- Tool-created modes are distinct from manual records: gate `dist/`, venvs,
  clean-A tree/dist artifacts (0644 under 0700 parents) are tool modes and
  are NOT claimed 0600; manual private files were precreated 0600 where the
  Group A omissions above did not occur.
- Persistence scope, evidenced: no PRIVATE or customer data is persisted by
  any delivered artifact, committed path, capture or log of this round; all
  retained private captures are declared synthetic test/fixture evidence
  under protected private roots. Disclosed transcript exception: the
  raw-archive-stdout emission above put raw committed repository source bytes
  into a tool transcript — complete raw-log compliance is not claimed; no
  secret/customer exposure is asserted or inferred.

## Protected evidence inventory (explicit list, referenced)
Selected supporting files with actual path / size / FULL SHA-256 / uid /
mode are recorded in the protected explicit-list inventory
`/home/janezp/oap-017ai-work/inventory-017ai-supported-evidence.json`
(2475 B, 0600 uid 1001, SHA-256
`7e5fc1c627701578fea83db4d46ae7fc8a16bc275768cb64ea242dffdbf7cb4e`):
final gate 3 captures, clean-archive entry-verify 3 captures, 2 driver
scripts (0700), and the 2 rebuilt clean-A artifacts (0644 tool modes).
Additionally:
- `oap/orders/017-ai-native-format-prerequisite-software.md` — 24278 B,
  SHA-256 `51fb00f8ecb5e2dfcf4508b415a084c4633696057bbfc7b2ede9d4b56bc401c4`,
  0644 uid 1001 (remote-verified)
- `oap/active` — 7 B, SHA-256
  `ca32fa2b29f07dbb2ee638840e9e34630920f199c8d8dc2192ff17df9a7da618`, 0644
  uid 1001 (remote-verified)
- Root-owned review records (0600): `reviews/017-ai-final-gate-result.json`
  (1477 B), `017-ai-final-gate-live-context.json` (770 B),
  `017-ai-final-gate-live-pytest-context.json` (472 B),
  `017-ai-artifact-independent-review.json`,
  `017-ai-delivery-head-review.json` (root authority)

## Safety/scope confirmations
- Software-only round executed: no actual AJ activation, admission, owner,
  Docker, native, TTY, host signal or live-model operation; no merge,
  acceptance, release, deployment or cutover; no new PR; coding did not
  choose the next order.
- Order and active bytes committed unchanged and re-verified remotely;
  activated order/report immutability honored; no prior-round artifact was
  edited, rerun or relabeled.
- All new manual private setup stayed inside verified
  `/home/janezp/oap-017ai-work` (same-shell 077 on every call where the Group
  A omissions above did not occur), with ALL disclosed exceptions: the
  one-shot mkdtemp chmod probe outside the AI root (Group B); the repo-root
  untracked captures (`logs-ai-focused-model{1,2}.*`, `.bgpid`; Group A);
  the failed `cd` to a nonexistent `/tmp/claude…` path (short-circuited,
  nothing created; Group B); and the possible seed-seam write under the
  default `/tmp/slaif-format-seed` (target/outcome not retained, not
  inspected, not cleaned; Group B). Directories 0700 / manual files 0600
  from creation except the disclosed omissions; no historical-root writes, no
  generic index/READY/LAST audit framework, no forensic old-corpus audit.
- Report publication withheld: this is the ordered PRIVATE draft; canonical
  report-only SELF creation awaits exact SHA approval.

## Known limitations / blockers
- The `017-aj` entry is INERT software: actual 017-aj format capture, native
  tool-cycle, multichunk/D09 acquisition, the EACH-literal required-syntax
  audit, whole-017 acceptance and v1 runtime remain NOT RUN. Fake coupled and
  static formatter tests earn no native-support or acquisition claim.
- All 018–024 remain mandatory; 018 activation requires whole-017
  merged and remote-main independently verified.
- The 28 suite skips are the standing suite accounting; the gate capture is
  three aggregate files (not 39 per-step files); CI at A is superseded by B.
- D09, whole-017 and AF/AD historical facts stand exactly as their immutable
  round records state them (AF CLOSED FAILED, AD PARTIAL).

## Recommended strategic follow-up
- On acceptance: activate the separately-ordered actual `017-aj` ONE-capture
  round through the reviewed serial RIGHT handoff (preserving the AH
  pre-stop TTY-attr and functional-input restoration lessons), then the
  bounded pure process/chunk collector from actual wrappers, the
  EACH-literal required-syntax audit and the full-017 acceptance review.
- Follow-up sequence (ROOT authority): accept whole 017, THEN merge PR25,
  THEN verify remote main, THEN 018 may activate. Coding performs no merge,
  acceptance or next-order choice.

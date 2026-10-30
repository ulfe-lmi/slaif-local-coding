# OAP 017-aa report — owner-UID fixture integration (software-only)

## Work order

- Identifier: 017-aa; order path
  `oap/orders/017-aa-owner-uid-fixture-integration.md`; numeric objective
  017.
- PR mode: AMENDED_EXISTING_PR (PR #25, same branch; no new PR).

## Status

COMPLETE for the ordered scope: the software-only integration of the 017-z
inert owner-UID identity contract through the REAL existing fixture owner,
its prepared image/exec/measurement/control/evidence path and the Python
capability driver, with useful coupled fake-platform tests, docs, the
complete locked gate at the exact committed head, artifact proofs and all 10
CI checks. This is software-delivery COMPLETE with the disclosed
process deviations below (first failures, manual-mode deviations,
staging deviations); it does not claim every ordered process clause
was flawlessly met. The integrated owner-UID path stays INPUT-GATED and
UNQUALIFIED until a later actual order: the ONE canonical future sealed
entry `017-ab` is fixed now but INACTIVE (AA never created, activated,
admitted or launched it; actual repository-context validation refuses it
under AA-active state before any external fixture work or admission). No
actual local Docker/fixture/owner startup, admission, native or extra Codex,
worker stop, signal, TTY handoff or model/Gateway call was performed in AA.
Whole-017, the serial native handoff, D09, the right-pane native format and
v1 runtime delivery remain unearned; every 018-024 stage remains required.

## GitHub / PR state (explicit)

- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #25 — OPEN, AMENDED on the same branch
  `oap/017-cache-read-observation` —
  https://github.com/ulfe-lmi/slaif-local-coding/pull/25
- Base: `main` @ `96c790423f6f0097a56a0b12bacda8a9b6da6aba`
- Starting remote head for this round (017-z report-only SELF):
  `24e4ae36351b8bb41f3f5cefa063cfc06389d618` (sole implementation parent
  `27d62aad359cc51ab0794717b4148d5844fe9885`; source A
  `a7ec94b5ee79b27bce4ec2882e3cb07ae196a7f4`)
- Implementation commits pushed before report (6):
  `b4843ce` (source A: 19 files), `058c105` (version-law wording),
  `845050b` (manifest-only, superseded), `ae74658` (lint/format/type
  repairs), `139dc24` (remaining format-only hunks),
  `f5ffecd` (manifest-only B, final)
- Source A: `139dc24c3f9c6befad6ab9388779cd795959dc39`; the A..B diff is
  manifest-only (`packaging/dev_provenance_manifest.json`)
- Implementation head SHA: f5ffecd54ca4177aeb3187f1951fbf0f04c11dbb
- Report publication commit: SELF
- New PR this round: NO. Amended existing PR: YES. Merge performed: NO.
  Auto-merge: NO. Order and `oap/active` committed unchanged (strategic
  bytes), working tree clean at B.

## What landed (all at the literal implementation head B)

- `scripts/cache_native_fixture_runtime_profile.py` (new, repository-only,
  stdlib-only): the small shared closed runtime-profile view USED by the
  integrated path — complete closed immutable construction (bounded
  lengths checked before any copy, owned immutable tuples, strict
  field/exec-user/build-arg/profile-data consistency with fixed errors);
  data validation, never measured authority.
- `scripts/cache_native_fixture_owner.Dockerfile` (owner variant, +108
  lines): frozen validated IDs only, same pinned base, immutable
  native artifact/LICENSE/NOTICE and the same confinement; root-owned
  immutable fixed-path profile DATA baked into the image (fails closed on
  missing/unknown/mismatched/unsafe data; never selected from env-var or
  file presence; module and DATA bytes explicitly readable and immutable
  inside the image even under a 077/0600 host build context); original
  defaults stay fixed-21002 unchanged.
- `scripts/cache_native_fixture_ci.py`, `_controller.py`,
  `_exec_capability.py`, `_local.py`, `_model.py`, `_standin.py`: the
  integration through the real owner — canonical profile selection with
  the ORIGINAL verified order/head/run/admission binding; the sealed
  child's OWN eligible host-ID collection through the Z production
  collector after its ORIGINAL admission wins (post-admission failure
  closes the SAME won attempt); the ONE immutable owner context
  revalidated at actual use (compared, never rebased); owner-scoped
  guarded executor (canonical exact INDEPENDENT UID:GID, fixed Python
  commands/flags/CID; original guard defaults unchanged); controller
  subject accounting; stand-in measurements/PTY; host exact-CID
  discovery with owned PID/birth lifetime frames; DISTINCT versioned AB
  records — identity-bearing owner state
  `slaif-017ab-owner-state-v1` (the old 12-key v1 form byte-for-byte
  unchanged and rejecting identity-bearing records), owner-run evidence
  `slaif-017ab-owner-run-evidence-v1`, the AB driver record
  `slaif-017ab-owner-uid-exec-capability-v1`, subject
  measurement/profile records on the DISTINCT tags
  `slaif-fixture-exec-measurement-v2`/`slaif-fixture-profile-v2` over the
  shared profile-independent structural core (strict original identity-v1
  wrappers keep the fixed-21002 law; measured 1001-class facts never
  normalized to 21002); the post-admission startup refusal (control-root
  creation or bounded socket bind) routes through the SAME single owner
  convergence (owned partial control disposed by the exact-ownership law;
  a pre-existing foreign control root never adopted or deleted; same
  closed startup record and exit code).
- Cleanup law: the original global controller/subject UID teardown scans
  are NEVER substituted with the host owner's UID; the new profile's
  descendant/cleanup proof is exact registered-CID plus owned PID/birth
  lifetime membership with tri-stated post-removal verification; unknown
  or unreadable still-existing entries stay unverified.
- Tests: `tests/test_cache_native_fixture_owner_uid.py` (new, 40 tests:
  pure-data constructor laws, v2 reserved-controller-ID negatives, real
  build-context/Dockerfile owner variant, guarded executor 1001/1002 with
  wrong-UID-OR-GID refusals, subject ownership, controller accounting,
  stand-in/PTY, exact-CID frame checks, DISTINCT versioned records) and
  `tests/test_cache_native_fixture_exec_capability.py` (52 tests, 14 new:
  the canonical `017-ab` sealed entry over hermetic synthetic
  repositories — coupled public-owner terminal positive, scripted driver
  bootstrap, in-process sealed-CLI own-collection, startup-refusal
  convergence, retention/finalization negatives, closed-cohesion record
  law, AB entry refused under AA-active state, second-admission
  exhaustion). `tests/test_cache_native_fixture_native_prep.py` +5.
  Three distinct honest layers — coupled public-owner terminal, scripted
  driver bootstrap, in-process sealed-CLI — NOT one sealed-real-owner
  end-to-end test; public validators and constructors real, only
  platform operations/raw OS seams faked.
- Docs: `ARCHITECTURE-for-agents.md` with the bounded 017-aa section (the
  THREE compact copies byte-identical,
  SHA256 `8a49f9564a7f2b9d12b995897f192a124e8a5f10f135c565909ff2c6e35b7f17`,
  66751B each: repo root, `oap/strategic-instructions/`, and the actual
  strategic-workspace mirror), human `ARCHITECTURE.md`,
  `docs/CACHE-OBSERVATION-CONTRACT.md` section 11j (normative fixture
  contract), `TESTING.md` round section and exact counts, and the stage
  ledger row.
- `packaging/dev_provenance_manifest.json`: development-state map
  (199 inputs) committed manifest-only at B.

## Acceptance evidence (ordered criteria, all at literal B)

1. Canonical profile selection and ORIGINAL context: the sealed child
   keeps sole resolve+admit ownership; the owner collects/freezes its OWN
   eligible host IDs (real/effective/saved triples, equal, nonroot,
   1..4294967294, distinct from controller 21001) only after its ORIGINAL
   verified order/run wins admission; a post-admission failure closes the
   SAME won attempt; the frozen context is revalidated at use, never
   rebased; caller-authored descriptions/flags never mint measured
   origin; the AB entry is refused under AA-active state before fixture
   work/admission. Evidence: the new owner_uid suite (40) and exec
   capability suite (52) driving REAL public construction/validate/
   prepare/hold/observe/finish/abort/retention — the coupled
   public-owner terminal positive over ONE coherent coupled fake
   process/resource world, the scripted-driver-bootstrap and
   in-process sealed-CLI proofs as distinct honest layers — PASSED
   (see Verification).
2. Image, subject execution and actual measurements: owner Dockerfile
   variant + build-context byte proofs under a 077/0600 host context;
   guarded executor admits only the canonical profile's exact independent
   UID:GID (useful 1001/1002 positive; wrong UID OR GID, reserved
   controller identity, root and out-of-range refused); subject
   tmpfs/home/workspace ownership; controller accounting; stand-in
   PTY; exact-CID discovery/frame checks; the container's profile DATA
   and actual exec user agree with the SAME frozen owner at producer and
   consumer boundaries. PASSED (same suites).
3. Versioned records and one trusted owner lifecycle: DISTINCT tags with
   closed exact keys/types/bounds; full original head/run/order/CID/image
   binding survives state export, capability qualification, protected
   retention and SAME journal finalization (owner evidence FIRST, then
   driver record, then same-attempt finalization); one absolute
   END/ledger/cleanup grace; exact-CID cleanup with owned lifetime
   registry (no UID-only or zero-global-UID claim); the old v1 grammar
   never widened. PASSED (same suites; the old S/X/Y defaults, sealed
   pairs and consumed namespaces unchanged, including the consumed X
   attempt at `e5215ce1a96b4dbecdcca5157b6a21ef30a6b1da` (terminal
   fail) and the consumed Y attempt at
   `35a3bcd7322535dd4a699efc53c0c1c62d4c942e` (terminal pass, executable
   UNKNOWN) — never reset, retried or relabeled).
4. Observable software acceptance: useful positives and the ordered
   negative list (missing/failed/mismatched/root/controller/out-of-range
   IDs; unknown profile/version/entry/cross-entry records; caller-authored
   context; post-admission drift; image/config/exec/measurement
   mismatch; wrong UID OR GID; supplementary-group privilege; missing/
   extra fields and bad fingerprint; foreign CID/run/head/image;
   pre-existing bootstrap/foreign child; exhausted admission; duplicated/
   ambiguous/unreadable/reused subject; scope/frame race; whole-record
   mutation; failed retention/finalization race/second publication;
   exact-CID cleanup with an unrelated same-UID host survivor; query
   failure not absence). PASSED (same suites).
5. Complete locked gate at the exact committed state (see
   Verification). PASSED.
6. Artifact and installed proofs (see Verification). PASSED.
7. All 10 implementation CI checks SUCCESS at B (see
   Verification). PASSED.
8. Docs, preservation and protected boundaries: the three compact copies
   equal; old orders/reports and S/X/Y actual records unchanged; no
   protected-host, network, service, key, UID/GID/group or model
   mutation. PASSED (see Safety/scope confirmations).

## Verification

### Final gate, artifact and attribution checks (all at literal
implementation head `f5ffecd54ca4177aeb3187f1951fbf0f04c11dbb`, tree
clean; the dev-provenance verify step inside the gate bound
`state=development head=f5ffecd54ca4`)

Evidence under `/home/janezp/oap-017aa-work/` (0700 root, 0600
files; the `probe-run` log directory was first observed 0775 and
repaired 0700 — see First failures).

- `uv lock --check`: PASSED — run separately at B
  (`gate-run-2/lockcheck.exit` `LOCK_CHECK_EXIT=0`) and re-verified at
  publication (`final-attribution/lock.exit` EXIT=0,
  "Resolved 36 packages in 1ms").
- `uv sync --frozen --extra dev`: PASSED (EXIT=0).
- `uv run --frozen ruff check .`: PASSED (All checks passed!).
- `uv run --frozen ruff format --check .`: PASSED (574 files already
  formatted).
- `uv run --frozen mypy src tests`: PASSED (no issues in 120 source
  files).
- `uv run --frozen python scripts/docs_consistency_check.py`: PASSED
  (19 claim docs checked).
- Complete pytest suite in the verified process-local umask 022 test
  child (`umask 022; uv run --frozen pytest -q` inside the gate):
  PASSED — 3329 passed, 28 skipped, 0 failed, 530.03s, EXIT=0. The 022
  context is an actually-measured live runtime fact, not a retroactive
  creation-mode claim: the root's read-only observation during the gate's
  pytest step recorded pytest PID 2660578 (exe `python3.12`) umask 0022
  under uv 2660575 (0022) under bash 2660455 (0022) under launcher bash
  2660453 (0077), direct child of the same worker 598258
  (`reviews/017-aa-current-state.json`, key
  `latest_gate2_live_process_context`, 19:39:53Z).
- `uv build`: PASSED (EXIT=0; wheel 142753B / sdist 979341B in `dist/`).
- `uv run --frozen python scripts/dev_provenance_manifest.py --verify
  --dist dist`: PASSED.
- `uv run --frozen python scripts/artifact_policy_check.py --dist dist
  --inspect`: PASSED (wheel sha256
  `1f2ebaff444be1ae90a7f1d863f462abcc82ff28caca448e28c206699fa4b50c`,
  37 entries — byte-identical to the Z-round wheel; sdist
  `5f0dbc81f261d078d996bf0f9dc5660def9879db054fb4e6d89b05ae90797053`,
  197 entries, +1 test input versus Z).
- `uv run --frozen python scripts/artifact_policy_check.py --dist dist
  --install-smoke`: PASSED.
- `python -m compileall -q src tests oap/bin scripts` (gate step):
  PASSED — attribution: this step ran under the bare `python` on PATH;
  the exact interpreter of that gate step is UNRETAINED (not
  retro-inferred from the current host or fresh-site python). The
  explicit frozen-context proof ran at unchanged B at publication:
  `uv run --frozen python --version` → `Python 3.12.15` (EXIT=0) and
  `uv run --frozen python -m compileall -q src tests oap/bin scripts`
  EXIT=0, stderr 0B (`final-attribution/`); the 3.12 attribution rests
  on that explicit proof.
- `bash -n oap/bin/bootstrap-two-codex-oap.sh oap/bin/launch-coding-agent.sh
  oap/bin/launch-strategic-agent.sh packaging/readyz-wait.sh`: PASSED.
### Focused suites (interim occurrences on pre-final-A/B trees; the
final B full gate above covers the same suites)

- Focused suites (fresh protected 022 locked runs): owner_uid 40/40
  (suite-run-14, plus its 2 direct constructor regressions) and the
  combined owner+exec_capability collection 92/92 after the lint fixes
  (suite-run-17); the current 12-file set (10 underscore-fixture suites
  plus the docs/dev-provenance suite; 801 cases: 800 pass + 1 expected
  dirty-pre-A dev-provenance failure before the source commit, resolved
  at B — suite-run-15/16). This 12-file set is distinct from the
  historical 989-case fixture-only set and EXCLUDES the base fixture
  (207) and containment (61) suites, which the final B full gate covers
  separately; no relabeling between sets. Full 3357-case count = 3329 +
  28.
### Artifact / installed identity (read-only, at B)

- Clean git-archive input
  map 199 inputs == manifest == Git (all missing/extra/mismatched empty;
  manifest bytes equal Git B and working tree); ALL 17
  `scripts/cache_native*` helper bytes (14 py + 3 Dockerfiles) equal Git
  B; both actual artifacts equal manifest/current `dist/`; actual
  fresh-venv (`fresh-venv-312-aa`, Python 3.12, site-packages outside
  the repo) installed27 27/27 functional cases plus separate identity
  (version 0.1.0, no repo on sys.path); ACTUAL fresh-site `slaif_local_coding`
  module set exact 30 == wheel == git with per-module bytes equal (fixed
  driver `fresh_module_identity_f5ffecd.py` rerun EXIT=0,
  `set_exact_wheel_git_site=true`, 0 mismatched; the first
  wheel-row-only-scope occurrence is preserved under its name, not
  relabeled); frozen21 21/21 with current hashes and retained positives
  (the first occurrence carried a copied Z/Y note label — preserved,
  corrected note describes the same measured result, no rerun). Root
  independently re-verified all of the above
  (`reviews/017-aa-actual-archive-review-f5ffecd.json`,
  `reviews/017-aa-fresh27-actual30-frozen21-review-f5ffecd.json`).
### Root-independent probes (at B)

- 18 unchanged AA probes
  683/683 (143 scoped pure/fake/public-boundary assertions + 540
  historical preservation; all exit 0, stderr 0B, scripts unchanged,
  head stable — `reviews/017-aa-independent-at-f5ffecd/summary.json`);
  19 unchanged original X/Y capability/readiness/sealed-CLI probes
  110/110 with hashes EXACT-matching the historical Y-final `ba297697`
  baseline (`reviews/017-aa-original-prior19-f5ffecd/summary.json`).
  These are software proofs, not actual-fixture, native or host
  qualification.

## Live model / service evidence

NOT RUN — the order authorizes no live model/Gateway calls and no actual
fixture/Docker/owner operation in AA; none performed. No protected live
service, network binding, key or profile changed.

## GitHub CI / required checks

All 10 implementation checks SUCCESS at the implementation head
(`f5ffecd`, CI run 40570190759, created 19:33:30Z): `test` 7m45s,
`docker` 1m44s, `docker-published` 1m11s, `gateway-contract` 16s,
`cache-native-fixture` 1m36s, `cache-native-containment` 40s,
`operator-session` 59s, `Analyze (actions)` 36s, `Analyze (python)` 1m41s,
`CodeQL` 4s. All required green at drafting: yes. Report-head checks may
be pending; strategy verifies. Interim CI failures at `ae74658` (ruff
format) and `139dc24` (stale manifest) are superseded by B and are
disclosed here, not relabeled.

## Local setup / dependencies

- Repo `.venv` via `uv sync --frozen --extra dev` (Python 3.12.15).
- Fresh non-editable install venv `fresh-venv-312-aa` (site-packages
  outside the repository) for installed27 and actual fresh-site
  identity.
- No dependency or lock change; no new workflow; no sudo; no
  repo-local persistent service; the gate's disposable artifact smoke
  venv self-removed; bounded in-process fake/test servers inside the
  suites are the authorized test context.

## Documentation

Updated in this PR: the bounded 017-aa section of
`ARCHITECTURE-for-agents.md` (three byte-identical compact copies),
human `ARCHITECTURE.md` current-state map, the normative fixture contract
section 11j of `docs/CACHE-OBSERVATION-CONTRACT.md`, the TESTING.md round
section with exact counts (owner_uid 40, exec_capability 52; ci 224,
local 50, native_prep 124, standin 102, identity 48 checkpoints
retained), and the stage ledger. No native-ready, actual
containment/current-exe, D09 or v1 runtime delivery claim made anywhere.

## Safety / scope confirmations

- No actual local Docker/fixture/owner startup, no admission, no native
  or extra Codex (help/version/exec/resume included), no worker stop, no
  signal to the real worker, Bash, TTY or any unrelated host process
  (exact-owned fake test-child cleanup signals inside the hermetic
  suites are the implemented, ordered scope), no TTY/job handoff, no
  model/Gateway call in AA.
- The `017-ab` order file was NOT created; `oap/active` still selects
  017-aa; no real AB fixture operation, no new AA real fixture entry.
- Original S/X/Y entries, sealed pairs, defaults and consumed namespaces
  unchanged; the consumed X/Y actual attempts and all historical
  records/bytes/modes/inodes preserved.
- Protected 18020/Qwen/vLLM/network/firewall/VPN/key/auth/profile:
  unchanged. Host UID/GID/group/kernel/proc/ptrace/prctl/privilege:
  unchanged. No host repo read by the adapter.
- No secrets, raw prompts, customer payloads or real customer source in
  any evidence; the evidence contains committed repository source
  archives (clean git-archive extractions), synthetic fixtures and closed
  identity metadata only; no native TUI/history persistence.
- Unrelated/pre-existing work preserved; no reset/clean/overwrite for
  convenience; no post-SELF mutation planned.
- Extra objective PR: NO. Coding merge/auto-merge: NO.
- Active/order bytes edited: NO (committed unchanged).
- Report commit changes only the report: to be verified at publication
  (staged diff is one path).

## First failures, deviations and mandatory append-only Z
qualifications

Mandatory append-only qualifications from `reviews/017-z-decision.md`
(never edit Z): (1) Z's exact publication used `os.replace`, which is
atomic rename with fsynced bytes but NOT atomic no-overwrite under
concurrent creation; no actual overwrite was observed; this round's
publication uses a real fail-if-exists commit (`os.link` of the complete
fsynced owned temp, then unlink temp and fsync directory). (2) Z's exact
publication temp
`oap/reports/017-z-inert-fixture-identity-contract.md.tmp-atomic-z`
was omitted from Z's final audit; root verified it absent; this round's
audit names its exact owned temp including any removed publication temp.
(3) Z's heading overattributed the initial focused runs (new 48 and
relevant 933/1 were before source A/B at the prior head); the complete
full gate at B genuinely proves all 3275/28; earlier occurrences are not
relabelled here. (4) Z's first-failure disclosure omitted the earlier
new-suite AST import allowlist failure (Ruff changed `Callable` to
`collections.abc`; the old allowlist omitted `collections`), the
subshell+tail PIPESTATUS masking of pytest status, the early ad-hoc
dataclass-loader setup needing `sys.modules` registration, and later
label-rewrite/rename/read setup exceptions recovered before publication;
exact unretained details (initial counts/stderr/timing) are unknown and
not invented here.

AA first failures and deviations, by category (first evidence
retained where named; the root's current preservation checks confirmed
the named originals):

Product defects found in this round and fixed in source (not harness
issues), each covered by named new tests, with the root's first probe
results retained in the strategic workspace: late-ID drift accepted at
finish (the frozen context not revalidated at the later identity-bound
use) — fixed by frozen-context revalidation with no-rebase refusal; the
post-admission startup refusal (control-root creation / bounded socket
bind) bypassing the same owner convergence — the actual counterexample
left the SAME already-won attempt's journal RUNNING on startup
refusal — fixed through the SAME single convergence (a forced bind
closes the same attempt `fail` with valid AB failure evidence and the
owned partial control disposed; the pre-existing foreign control root
is refused and never adopted, its preservation a positive control); a
`NameError` for `description` in `validate_ab_owner_run_evidence`
after the shared identity-law refactor; the AB-entry consumer accepting
AB-tagged records under other orders (017-x/017-y); identity-bearing
state accepted under the old v1 tag; the correlation group-law misuse
(expected effective groups treated as a tuple-of-allowed-vectors);
unbounded or truncated raw 4096/8192 reads accepted; non-ENOENT lookup
failures classified as absence; a helper inserted mid-prepare making the
original phase flow unreachable; a descendants-after zero inferred
without exact CID plus owned lifetime registry; same-birth UID mismatch
misclassified (recycled vs refused/unverified); the `Path`/int type in
the owned-member lifetime reader; single-read unstable lifetime frames;
the driver record always emitting identity=None; an AB pass accepted
with capability=None.

Test harness / fixture-faithfulness / context / setup failures (no
production defect claimed, or the production behavior preserved as
designed):

- gate-run-1 first failure: Ruff 26 violations (then mypy 27 at
  preB-checks-1), behavior-preserving repairs landed at `ae74658`;
  gate-run-2 at B is green (logs retained).
- Suite first failures (first logs retained where named): suite-run-4
  (948 passed / 3 failed: the partial ORIGINAL test fixture missing
  `_owner_context` — faithful fixture update with explicit None, the
  production constructor/context law kept strict; a capture-cap
  expected-reason mismatch — the actual local-driver-exit behavior
  preserved as the meaningful assertion, no expected-reason swap; a
  0700-vs-0755 fixture-mode expectation under the 077 context — the
  documented umask-context issue, the 022 test child required, fixture
  validators not weakened); suite-run-8 (229 passed / 21 failed,
  204.73s — an interim occurrence that included the product NameError
  defect above plus fixture-faithfulness gaps; first log retained);
  suite-run-11 (10 passed / 4 failed: three socket path-length
  timeouts in owned test fixture nesting — the long AF_UNIX socket
  paths (110/108/109B from long pytest test names) strongly support
  the path-limit diagnosis, but the original OS errno is not retained
  — a cause inference, not a proven kernel cause; owned nesting
  shortened, production refusal unchanged; plus a CLI exit-code
  expectation
  corrected to the documented 130 aborted semantics — no
  cancellation-semantics change); suite-run-13 (798 passed / 1 failed:
  `test_real_development_state_consistent` on the DIRTY pre-A tree —
  classified as a provenance-state guard, not a source regression;
  resolved at B). The original NAMED first-failure logs of
  suite-run-8/9/11 are preserved — root-verified 9/9 same hash/bytes/
  inode versus the earlier snapshots
  (`reviews/017-aa-suite8-9-11-first-log-current-preservation.json`);
  the known overwritten/unretained family is the suite-run-2 repeated
  runs and the suite-4 initial missing-path setup, and unknown
  intervening occurrences are not reconstructed.
- The very first new owner-UID suite run: 19 passed / 1 failed,
  0.55s, stopped after the FIRST failure (lifecycle positive/prepare,
  closed reason internal); the remaining new cases were NOT RUN in
  that occurrence (first log retained; root review
  `reviews/017-aa-first-new-suite-log-review.json`).
- Setup sequence (no product verdict, distinct operations): the
  first archive-driver write hit a heredoc-quoting SyntaxError; the
  FIRST companion-driver adaptation attempt hit its docstring pattern
  assertion before any write; a LATER companion adaptation produced a
  partial write and then failed its first comparison assertion. All
  are setup failures, retained/disclosed separately; no product
  assertion failed in them.
- frozen21 first occurrence carried a copied Z/Y note label; the
  relabel step's first assertion compared identical originals
  (setup-level, no product verdict); preserved as
  `probes-final-f5ffecd-first-mislabeled-note.json`; the corrected note
  describes the SAME measured result — no rerun for a label.
- The first fresh-module occurrence iterated wheel rows only (always
  exit 0) and cannot prove the actual site set; preserved as
  `fresh-module-identity-f5ffecd-first-wheel-only-scope.json`; the
  corrected driver enumerates the ACTUAL fresh-site `.py` set, requires
  exact set equality wheel==git==site with per-module byte equality and
  exits nonzero on any divergence; rerun EXIT=0, 30/30.
- First pre-push publication occurrence superseded: the first
  local canonical publication (29409B, SHA256
  `b668873b9a087c5fe67a68e346548bb4112a324d5074d7b05d6507b316153cb6`,
  inode 6848692) was made from the then-current draft; the draft was
  corrected per review before any push, the unpushed local report
  commit was reset, and the first canonical file was removed only
  after its bytes were retained as
  `publication/report-first-prepush-occurrence.md`. No remote ever saw
  the first bytes; the pushed report carries only the corrected final
  bytes, and the final metadata audit was regenerated after this
  supersession and the probe-run mode repair.
- `git add -A` was used at `b4843ce` and `058c105` against the coding
  protocol's explicit-path rule; explicit staging was used for every
  later commit. `058c105` inadvertently committed the `b4843ce`-bound
  manifest; that intermediate manifest is superseded by `845050b` and
  `f5ffecd`. `ae74658` initially omitted the format-only hunks in
  `scripts/cache_native_fixture_exec_capability.py`; completed at
  `139dc24`. No history rewrite.
- Manual metadata mode deviations (current 600 is not creation 600):
  `part-e/part-e.py` first observed 0664 at 18:01:06 (15363B),
  legitimately appended between observations (32595B at 18:01:30;
  44300B by 18:04:13), mode 0600 OBSERVED at 18:04:13 on the same
  inode 11830815 — initial 0664, current 0600, no same-bytes proof and
  no independently-verified mode-only-repair claim (legitimate appends
  occurred between observations); `dbg-prepare/dbg_core.py` first
  observed 0664, mode-only repaired to 0600 (inode 11830616, same bytes
  preserved — verified); `/tmp/pty_actual.txt` (outside the AA root,
  from earlier AA debugging) first observed 0664, current 0600, uid
  1001, inode 9163685 — creation mode and exact absence unknown (not
  retro-claimed), same bytes/inode preserved; no ADDITIONAL /tmp
  metadata after that; the `probe-run/` manual log directory first
  observed 0775 (uid 1001, inode 11830646; `out` 1236B inode
  11830647 and `err` 0B inode 11830648, both 0600) — repaired
  mode-only to 0700 with log bytes/inodes preserved, creation mode
  unknown, parent AA root 0700; a bounded one-level inventory found no
  other manual top-level violation (the four exact archive/venv tool
  trees excluded).
- The gate's bare-`python` compileall step has an UNRETAINED exact
  interpreter (see Verification attribution; not retro-inferred); the
  explicit 3.12.15 compileall and `uv lock --check` were re-verified at
  B at publication.

## Known limitations / blockers

- The integrated owner-UID path is software-only and UNQUALIFIED: no
  actual AB fixture operation may run in AA; the later `017-ab` order,
  if selected, independently names exact accepted source/head, opt-in,
  limits and one actual result.
- The coupled compositions are useful FAKE proof in three distinct
  honest layers; no sealed-real-owner end-to-end test exists.
- The Y executable capability remains the closed UNKNOWN (null digest)
  bound to its actual attempt head `35a3bcd`; the X attempt remains
  terminal fail at `e5215ce`; neither is reset, retried or relabeled.
- The current 12-file / 801-case set is distinct from the historical
  989-case fixture-only set; it excludes the base fixture (207) and
  containment (61) suites, which the final B full gate covers
  separately; no relabeling between sets.
- No blocker remains inside the ordered AA scope.

## Recommended strategic follow-up

Factual only; strategy decides: the `017-ab` entry is fixed, integrated
and software-tested and can be qualified by its own later order with one
bounded actual attempt if selected; the serial native handoff, D09 and
every 018-024 stage remain mandatory; whole-017 acceptance stays with
strategy.

## GitHub / publication contract (appendix)

- Repository `ulfe-lmi/slaif-local-coding`; PR #25 OPEN (AMENDED, same
  branch `oap/017-cache-read-observation`); base `main`
  `96c790423f6f0097a56a0b12bacda8a9b6da6aba`; round starting remote head
  (017-z report-only SELF)
  `24e4ae36351b8bb41f3f5cefa063cfc06389d618`; implementation head
  `f5ffecd54ca4177aeb3187f1951fbf0f04c11dbb`; report publication commit
  SELF (child of the implementation head).
- New PR: NO. Merge: NO. Auto-merge: NO. Exact order
  `oap/orders/017-aa-owner-uid-fixture-integration.md` and
  `oap/active` (= `017-aa`) unchanged and committed.
- This report is the ONE immutable 017-aa report; prior round reports
  remain immutable.

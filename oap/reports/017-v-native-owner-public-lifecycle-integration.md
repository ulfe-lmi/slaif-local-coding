# OAP Round Report — 017-v: native-owner public lifecycle integration (fake integration only)

- Objective: 017 (`AMEND_EXISTING_PR`; PR25
  https://github.com/ulfe-lmi/slaif-local-coding/pull/25; branch
  `oap/017-cache-read-observation`; base `main` @
  `96c790423f6f0097a56a0b12bacda8a9b6da6aba`)
- Order: `oap/orders/017-v-native-owner-public-lifecycle-integration.md`,
  SHA256 `68136f0ce03605dae0ed1ca536b279ad3a1944247370e577c46b73162211a99d`
  (13305 B), committed byte-unchanged in source A; `oap/active` =
  `017-v\n` committed byte-unchanged.
- Starting state: U SELF `488938450865409e137b49e2347065f8e2a43cfe`
  (report-only); U implementation head
  `f9d9caaa18264fab5f19cc37230a4d608a44eafc`. GitHub reconciled
  before mutation (remote PR head = U SELF; base unchanged).
- Status: COMPLETE (scoped to the 017-v order: the bounded public
  fake-integration deliverables of sections 3-6 are implemented,
  tested at every ordered layer and verified; whole 017 and
  018-024 remain incomplete and are NOT accepted by this report)
- Implementation head SHA: a18401e9ffafe2e1f7d44013a49458803db51c6f
- Report publication commit: SELF

## Outcome (bounded, honest)

The small EXPLICIT public composition `NativeOwnerRun`
(`scripts/cache_native_fixture_native_owner.py`) now binds the
accepted immutable order/run binding to the REAL fixture owner and
the public staged native workflow as ONE coherent run, with ONE
shared owner/RAM context/END anchor/ledger/cleanup grace, the
staged (no-predicted-PID) subject registration, the DISTINCT
native-scope terminal records, the protected retention seam, and
the honest publication ordering. It is exercised in this round
EXCLUSIVELY with injected fake external operations (fake
git/platform/process seams and owned synthetic repositories): the
real backend code is imported and its real methods driven; the
platform operations are faked. This earns NO native, worker-stop,
Docker, rehearsal or handoff qualification; D09 remains
`NOT RUN`; the historical S admission stays consumed; no v1
runtime claim is made.

## 1. Delivered composition (order sections 3-6)

- Constructor and admission: `NativeOwnerRun` accepts ONLY a
  verified `OrderRunBinding` (any other type: closed
  `native-owner-binding-invalid`), admits EXACTLY ONCE in the
  order's stable one-attempt namespace BEFORE any external
  mutation (the admission re-validates the ACTUAL repository,
  committed active/order content, literal head and repository
  identity against the frozen binding), and constructs the REAL
  `LocalFixtureOwner`, whose constructor selects the authority of
  the binding's OWN order: the S default (no binding) is
  UNCHANGED (fresh mint + stable 017-s admission); a 017-s
  binding keeps the historical S opt-in unchanged; a NEW-order
  binding requires a LIVE bound admission in that namespace
  before adoption (a bare caller run id can never skip or bypass
  the one-attempt law) and re-validates the real repository
  context READ-ONLY through the actual resolver (nothing written,
  no authority minted, the resolver's fresh run id discarded, no
  active/S constant changes, no runtime-global monkeypatch, no
  second owner). The owner adopts the binding's minted run
  identity (no second mint, no second admission). A constructor
  failure AFTER winning the admission closes THAT SAME run
  honestly (terminal fail in the bound namespace — never an
  orphan running claim) and re-raises the primary closed refusal.
- One shared run context: the bounded public lifecycle
  start/prepare/observe/record_stop/register_subject/finish/
  abort all consume the owner's OWN absolute END anchor plus the
  owner's single allowed cleanup grace (no fresh phase window,
  no reset, no second fixture budget); an expired budget refuses
  BEFORE any IO or launch; the composition never signals or kills
  the owner (bounded join within the budget remainder).
- Staged subject registration: the actual later native subject is
  registered only AFTER prepare AND the separately measured stop
  (the retained stop receipt is the immutable HISTORICAL record;
  the CURRENT stable-stop predicate is re-measured predicate-only
  before any identity commit and its receipt is discarded); the
  frozen first-prepare W/B baseline must still be the same worker
  job; the registered run is immutable (a foreign expectation run
  is refused); the expected PTY/binary/CID/run arrive from the
  operator's OWNED attach registration and are independently
  correlated by the collector (a channel bound to another CID
  refuses before any read); a refused registration commits
  nothing; a conflicting second registration is a closed refusal.
- DISTINCT native-scope owner terminal record
  (`slaif-native-owner-run-evidence-v1` / scope
  `native-owner-run`, closed validator
  `validate_native_owner_run_evidence`, fixed token
  `native-owner-run-evidence-invalid`): the SAME measured owner
  state/cleanup/publication as the S record, WITHOUT the
  historical S whole-run false assertions (`native_started` /
  `worker_stopped` / `codex_invoked` / `native_ready`) and without
  the S-only CI-image comparison; any-order OAP id, 32-hex run,
  40-hex bound head, and the shared measured substructures
  validated through the reviewed S validator over an internal
  S-shaped envelope (a validation vehicle only — the retained
  record never carries the S false assertions). The historical S
  rehearsal record keeps its exact schema, scope and S meaning
  and is never relabeled, derived or doubled.
- Closed native-run terminal record
  (`slaif-native-owner-run-v1`, scope `native-owner-run`):
  immutable binding record (the binding module's own closed
  grammar), closed owner outcome (pass/fail/aborted), the
  ALREADY-KNOWN journal state, measured subject/stop booleans,
  the measured native-owner record (produced through the EXISTING
  producer/consumer ONLY where its measured prerequisites hold —
  never fed fabricated starts) or its closed refusal, and the
  closed verdict; the consumer enforces the exact key sets,
  closed vocabularies as CLOSED STRINGS first (typed refusals for
  non-string/unhashable values), cross-field readiness (ready
  requires EVERY measured prerequisite; a refusal forbids a
  native record and any readiness), and a nested native record
  bound to the OUTER binding (a foreign nested identity is a
  contradiction). Retention reuses the reviewed protected 0600
  atomic no-overwrite seam (ancestor trust, no-overwrite LINK
  commit, digest-verified and re-verified; a pre-existing
  destination or same-name temporary file is refused — never
  unlinked or adopted; the evidence root must be outside the
  owner's disposable work root).
- Honest publication ordering: the owner's convergence reads the
  DISTINCT owner-phase outcome from the SAME completed owner
  state (the same-order journal is the durable record, NOT a
  prerequisite — no circular journal dependency); a terminal
  fail/aborted (including a publication failure after a computed
  pass) is finalized honestly at convergence; a converged pass
  KEEPS the bound attempt running; `publish_native` retains the
  protected native record FIRST (a failed publication closes the
  still-pending attempt as fail and propagates — never an
  admitted pass) and ONLY THEN finalizes the same-order journal;
  the record's `attempt` field carries the ALREADY-KNOWN journal
  state (`running` on the pass path; `terminal-preserved` for a
  terminal outcome) — never a predicted finalize token; the REAL
  returned finalize token is retained in RAM/result only and the
  immutable retained evidence is never rewritten to insert it.
  The owner's cleanup/export outcome stays DISTINCT from the full
  handoff/restoration verdict.

## 2. Defects found and repaired in-flight (first failures preserved)

Strategic in-flight reviews found, and this round repaired with
fake controls (original probe assertions and valid positives
unchanged):

- Review 1 (`check-native-constructor-admission-bypass` 5/5 after
  repair; `check-native-staged-registration-mocked` 2/5 at source
  `c9edd60284b1` — first-increment evidence preserved in the
  strategic reviews): a caller `run_id` could bypass an exhausted
  admission; the staged registration committed receipts before
  the phase/baseline/binding gates.
- Review 1b (`check-native-staged-current-stop-mocked` 1/5 at
  `c9edd60284b1`; 2/5 mid-repair — preserved): retained stop
  existence alone was treated as the CURRENT stable-stop phase;
  a resumed worker, a reused Bash birth, a newly unreadable
  positively-existing PID and a newly running group member all
  still registered. Repaired by re-measuring the CURRENT bounded
  stable-stop predicate and the W/B continuity before any
  identity commit, without replacing the immutable historical
  stop receipt.
- Review 2 (at `native_owner` `d8c46e416e1f`, first-increment
  evidence preserved): public constructor 2/4 (an admitted
  V-bound run could be left running on constructor failure;
  authority selection missing), record-coherence parser 3/12
  (contradictory readiness, foreign nested identity, malformed
  grammar and untyped refusals accepted), protected writer 1/5
  (writable-parent, preexisting-temp, raced-destination and
  symlink-ancestor cases not refused). All repaired: verified
  bound admission with the actual resolver re-validation,
  same-run fail closure after a post-admission constructor
  failure, the closed typed parser (cross-field readiness,
  nested binding identity, closed-string vocabularies first),
  and the protected retention seam reuse with pre-refusal of a
  preexisting same-name temporary file.

Scoped rechecks after each repair and the FINAL six-probe
regression at the final committed source (module digest prefix
`b46f28bdc187`) all pass with the valid positives preserved:
`check-native-constructor-admission-bypass`,
`check-native-staged-registration-mocked`,
`check-native-staged-current-stop-mocked`,
`check-native-owner-construction-mocked`,
`check-native-owner-record-coherence-mocked`,
`check-native-owner-evidence-writer` — all
`all_checks_passed: true`, source/fixture bytes verified stable
across each run. Evidence:
`/home/janezp/oap-017v-work/017-v-final-check-native-<probe>-b46f28bdc187.json`
(0600); the intermediate pre-format `d5ce22fe50a9` evidence is
retained under `superseded/`; the first-increment failure
captures are the strategic `reviews/017-v-*-first-*.json`.

## 3. Public local proof

- NEW tracked suite
  `tests/test_cache_native_fixture_native_owner.py` (12 tests):
  the full public happy path over ONE coupled fake process world
  (start -> prepare -> observe -> the separately measured stop
  -> the actual later subject launched bound to the owner's OWN
  registered target CID -> `register_subject` -> observe ->
  `finish` driving the REAL owner finish/export/teardown with
  fake platform operations, the exact CID removal updating the
  same world to absent -> the same-worker restoration ->
  `publish_native`), asserting the native-scope owner evidence
  WITHOUT the historical S false assertions, the journal
  running->pass, the retained record's `attempt` = the pending
  `running` state, the finalize token `finalized`, the measured
  native facts bound to order/head/run, the ready verdict and
  the 0600 retained file; and the closed negatives (non-binding
  constructor refusal with no work directory, exhausted
  admission before any external mutation with the retained
  record unchanged and no executor action, stale bound head
  before any work, pre-stop / pre-prepare registration refusals,
  double-registration and resumed-worker refusal, foreign
  expectation run, preparation-only honest not-ready
  publication, owner-failure honest fail with refused
  not-prepared publication and no journal rewrite, abort honest
  `aborted` with `terminal-preserved`, and the closed
  native-scope validator's key/grammar/ledger law with
  cross-scope refusals).
- Focused tracked suites together: local 49 + native-prep 124 +
  binding 45 + native-owner 12 = **230 passed in 15.93 s**
  (Python 3.12, repo venv).
- The real backend path stays unexecuted against any real
  backend: no actual Docker operation, no native launch
  (including help/version), no worker stop, no TTY/job
  manipulation, no real fixture admission in the real checkout
  (the actual `.oap-local/` holds only the historical 017-s
  record; all V admissions are in owned synthetic temporary
  repositories with fake git seams), no host signal, no CLI
  entry.

## 4. Final verification at implementation head a18401e

All in ONE shell with `umask 022` at the committed candidate
(log: `/home/janezp/oap-017v-work/017-v-full-gate-a18401e.log`):

- `uv sync --frozen --extra dev`: 31 packages, no changes.
- FULL `pytest tests/ -q -p no:cacheprovider`: **3150 passed,
  28 skipped in 485.10 s** (U baseline 3138 passed + 12 new;
  skips are the pre-existing environment skips, unchanged).
- `compileall src scripts`: OK. `ruff check .`: clean. `ruff
  format --check .`: 558 files already formatted. `mypy src
  tests`: no issues in 117 source files. `docs_consistency_check`:
  OK (19 claim docs). `uv lock --check`: OK.
- `artifact_policy_check --inspect`: see the disclosure below
  (it observed the PREVIOUS round's stale `dist/` because it ran
  before the gate's own build); `--install-smoke`: OK (fresh
  smoke venv, entrypoint help/version, installed 0.1.0).
- `uv build --out-dir dist`: wheel
  `1f2ebaff444be1ae90a7f1d863f462abcc82ff28caca448e28c206699fa4b50c`
  (142753 B) — byte-identical across P/R/S/T/U/V (V touches no
  `src/`); sdist
  `e5a7240d3f026117ce7fbb813dadb8c3fff4aed95c4695e321c8a9f9ff49374d`
  (891436 B, 194 entries = U's 193 + the one new tracked V test
  file). Both match the committed development manifest
  (`packaging/dev_provenance_manifest.json`, 196 complete
  inputs, `--verify` OK).

Clean-archive reproduction at the LITERAL head a18401e (fresh
0700 root `/home/janezp/oap-017v-work/archive-build-a18401e`,
outside the source tree): `git archive` of the literal head;
**196/196 manifest inputs present and byte-identical**; actual
`uv build` with out-dir outside the source tree; **both
artifacts byte/hash/size-identical to the manifest and to the
repo dist**; **30/30 installed Python module bytes** in the
archive-built wheel match the archive source
(`archive-wheel-identity-a18401e.json`). Separately, a fresh
non-editable Python 3.12 venv OUTSIDE the checkout
(`fresh-venv-312`) with the archive-built wheel: **27/27 unique
installed functional cases PASS** with the identity assertions
(separate, not counted) — site-packages outside the repo,
version 0.1.0, no repo path on sys.path
(`installed-functional-a18401e.json`). Unchanged frozen 21 at
the literal implementation head via the repo Python 3.12 venv:
**21/21 PASS, all 21 probe baseline hashes unchanged**
(`probes-final-a18401e.json`, baseline
`reviews/017-p-probe-hashes.json`).

## 5. GitHub CI (all 10 implementation checks)

Run 40281021705 at a18401e9ffafe2e1f7d44013a49458803db51c6f:
ALL 10 check runs `success` — `test` (job 121434113014:
**3150 passed, 28 skipped in 311.73 s**), `gateway-contract`
(121434112852), `operator-session` (121434112980),
`cache-native-containment` (121434113001), `docker`
(121434113078), `cache-native-fixture` (121434113087),
`docker-published` (121434113103), `CodeQL`, `Analyze (python)`,
`Analyze (actions)`. No Codex in CI. Test-job log retained at
`/home/janezp/oap-017v-work/ci-test-job-121434113014.log`.

## 6. Append-only clarifications to the U record (order section 4)

Restated in V per the order (U's own report is immutable):

- T§9's unqualified "NO host signal of any kind" overstates its
  scope: exact-owned tiny test children were killed/waited by
  permitted test cleanup as T§4 already describes. No real
  worker/Bash/unrelated process was signalled; no worker stop
  occurred. This was an allowed test action, not a protected-host
  violation.
- T omitted an explicit protocol Status field; U carries one.
  This V report carries one as well, distinguishing this order's
  bounded result from still-incomplete whole 017 and 018-024;
  T's status is not retroactively assigned or edited.
- The empty historical auxiliary launch log proves neither pass
  nor process death; the prior launch-attribution/liveness
  uncertainty stands; no private capture was reopened and no S
  attempt re-run.
- The seven-case order-binding proof and the four-case actual
  file-replacement proof are distinct; exact names/counts with
  valid positives are cited.
- The initial 13-entry pass-1 mode audit and the later 38-entry
  pre-SELF audit are distinct scopes; V retains its own fresh
  explicit final audit (§9), not a reused early inventory.
- U §7's unqualified "NO host signal" shorthand is clarified
  (per strategic review; U is not rewritten): it means the real
  worker/Bash group and any unrelated process. The existing
  exact-owned tiny Python test-child cleanup (each exact-owned
  child killed by the test's own cleanup if still alive) is
  allowed by the orders and is what U §6's correct distinction
  and V's suite use; no real process was signalled or stopped in
  U or V.
- Exact path counts (per strategic review): U source A changed
  10 tracked paths (T/U helper/test/docs/active/order); the
  strategic compact mirror
  `/home/janezp/codex-supervision/slaif-local-coding/ARCHITECTURE-for-agents.md`
  is an additional OUTSIDE-checkout copy kept byte-identical, not
  an eleventh tracked path. V source A
  (`b12a60b86ab8abf565b70578f1e0d19e253841c3`) changes exactly
  12 tracked paths: `oap/active`,
  `oap/orders/017-v-native-owner-public-lifecycle-integration.md`,
  `scripts/cache_native_fixture_local.py`,
  `scripts/cache_native_fixture_native_prep.py`,
  `scripts/cache_native_fixture_native_owner.py` (new),
  `tests/test_cache_native_fixture_native_owner.py` (new),
  `docs/CACHE-OBSERVATION-CONTRACT.md`, `TESTING.md`,
  `docs/CACHE-REWORK-LEDGER.md`, `ARCHITECTURE.md`,
  `ARCHITECTURE-for-agents.md`,
  `oap/strategic-instructions/ARCHITECTURE-for-agents.md`;
  manifest B (`a18401e9ffafe2e1f7d44013a49458803db51c6f`) then
  touches only `packaging/dev_provenance_manifest.json`.
- U-era /tmp round-metadata deviation (disclosed):
  `/tmp/report-017u-draft.md` (532 B) and
  `/tmp/u-report-remote.md` (19351 B) were uid1001 mode 0664
  outside the private 0700 roots. Before V SELF they were
  identity-verified byte-for-byte against the expected digests
  (draft `d988c4d33cd9a6f5646aae47207c4665a1796b269651638cd32ff15513edeae3`;
  remote `9d10cbcfeb4f88ac051355bf7b58fc8589030adda59e8d0187559d3d165dfee5`,
  the exact U report bytes) and set to 0600 by exact path — no
  content was printed, overwritten or otherwise touched. Closed
  before/after metadata:
  `/home/janezp/oap-017v-work/017-u-tmp-evidence-finalization.json`.

## 7. NOT RUN (explicit)

- NO actual local Docker operation in V (the native/Docker
  backend paths remain implemented-but-unexecuted; every run
  Docker child environment/fake seam is test-local).
- NO native launch of any kind (including help/version); NO
  worker stop; NO TTY/job manipulation; NO auxiliary handoff
  signal; NO host signal to any real process (the
  exact-owned tiny test-child cleanup of §6 stands as allowed
  test action).
- NO new rehearsal, NO new fixture admission in the real
  checkout; the single S admission at `2a9c44e…` / run
  `c8fed899…` remains consumed and the historical 017-s record
  is byte-untouched.
- NO model/GPU/Gateway call; NO protected Qwen/vLLM/qwen-
  serving/model/patch/venv/profile/auth/firewall/VPN/network/
  daemon/global-package change; NO benchmark/RC/tag/registry/
  release/deployment/cutover; NO merge or auto-merge; no second
  PR; no next numeric objective.
- D09 remains `NOT RUN`; the later serial native handoff remains
  a separately authorized order; legacy default unchanged; v1
  runtime not implemented; whole 017 and 018-024 remain
  required.

## 8. Preserved failures and disclosures (not erased)

- First-increment probe failures, retained in the strategic
  review captures: staged-registration 2/5 and current-stop 1/5
  at source `c9edd60284b1` (reviews 1/1b); public constructor
  2/4, record-coherence 3/12 and writer 1/5 at `native_owner`
  `d8c46e416e1f` (review 2, `017-v-*-first-d8c46e416e1f.json`);
  the mid-repair current-stop 2/5 (B birth fixed) and the
  pre-repair green captures (module digests `8e32c9ef9c0b` /
  `4fd15eba7d22`) remain in the V root as first-increment
  evidence.
- No product or test failure remains at the implementation head;
  no skipped, pending, missing or unavailable evidence is
  presented as pass; the 28 skips are the pre-existing
  environment skips (identical set to U).
- Disclosure: the in-gate `artifact_policy_check --inspect` ran
  before the gate's own `uv build` and therefore reported the
  PREVIOUS round's stale `dist/` artifacts (sdist
  `b3376a077f06f9a87a95c66d5500d9b13a9b3609b44868c1125a7962c13ee5b1`,
  879955 B, 193 entries — the U-era sdist; the wheel was already
  the byte-identical `1f2ebaff…`). The gate's own `uv build`
  afterwards regenerated `dist/` from the current source, and
  the regenerated bytes are verified identical to the manifest
  and to the clean-archive build (§4); the inspect step's
  `ok: true` referred to the artifact policy over the artifacts
  present at that moment, not to the current-source build.
- Disclosure: one nohup-launched frozen-21 attempt was lost when
  its launching exec session closed (0-byte log, no output); the
  re-run as a tracked session is the retained proof
  (`probes-final-a18401e.json`). The lost attempt is preserved
  as a setup diagnostic, not a result.

## 9. Evidence root and file audit (fresh, explicit)

`/home/janezp/oap-017v-work/` (0700; all owned files 0600 uid
1001): the six final probe evidence files (module digest prefix
`b46f28bdc187`), the four in-repair probe evidence files, the
three first-increment probe evidence files, the U /tmp
finalization evidence, the full-gate log, the CI test-job log,
the clean-archive build root (`archive-build-a18401e/`,
excluded tool tree with intended permissions) and its
identity/build-receipt evidence, the fresh venv
(`fresh-venv-312/`, excluded tool tree), the installed-27
functional evidence and driver, the frozen-21 evidence and
driver, the PR25 current-body draft, and the audit itself:
`owned-files-audit-preself.json` — **28 entries audited, 0
nonconforming** (initial audit found five 0644 owned files;
exact-path chmod 600 applied and re-audited clean; no recursive
or blanket chmod).

## 10. Identities and limitations

- Source A: `b12a60b86ab8abf565b70578f1e0d19e253841c3` (12
  tracked paths); manifest B / implementation head:
  `a18401e9ffafe2e1f7d44013a49458803db51c6f`; remote PR head
  verified equal to the implementation head after push.
- Wheel `1f2ebaff444be1ae90a7f1d863f462abcc82ff28caca448e28c206699fa4b50c`
  (byte-identical P/R/S/T/U/V); sdist
  `e5a7240d3f026117ce7fbb813dadb8c3fff4aed95c4695e321c8a9f9ff49374d`
  (194 entries); development manifest: 196 complete inputs,
  toolchain python 3.12.15 / uv 0.12.5 / lock
  `1237cbd179f71b99984c80f927529549f5e61eb705585ef9cf2ab0fa9e26764a`.
- Limitations: public fake integration only — the real backend
  code path is unexecuted against any real backend; the owner's
  cleanup/export outcome is distinct from the full
  handoff/restoration qualification; the historical S record is
  historical S scope; nothing in this round qualifies a native
  subject, a real Docker attachment, or runnable native
  handoff; the visible handoff still requires its own
  separately authorized order with measured facts.

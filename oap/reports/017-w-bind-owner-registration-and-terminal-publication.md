# OAP Round Report — 017-w: owner-bound registration and terminal publication coherence (fake integration only)

- Objective: 017 (`AMEND_EXISTING_PR`; PR25
  https://github.com/ulfe-lmi/slaif-local-coding/pull/25; branch
  `oap/017-cache-read-observation`; base `main` @
  `96c790423f6f0097a56a0b12bacda8a9b6da6aba`)
- Order: `oap/orders/017-w-bind-owner-registration-and-terminal-publication.md`,
  SHA256 `3641ab0afae9b23b6eb5e6cbb06bc497d14f618290143be3fb7a1ea648903a51`
  (12759 B), committed byte-unchanged in source A; `oap/active` =
  `017-w\n` committed byte-unchanged.
- Starting state: V SELF `65dfa46e8a2994ce9d5f950e99d3e9aff5602f50`
  (report-only); V implementation head
  `a18401e9ffafe2e1f7d44013a49458803db51c6f`; V source A
  `b12a60b86ab8abf565b70578f1e0d19e253841c3`. GitHub reconciled
  before mutation (remote PR head = V SELF; base unchanged).
- Status: COMPLETE (scoped to the 017-w order: the bounded
  owner-context and terminal-publication coherence repairs of
  sections 1-3 are implemented, repaired against the in-flight
  reviews, tested at every ordered layer and verified; whole 017
  and 018-024 remain incomplete and are NOT accepted by this
  report)
- Implementation head SHA: 5893f0241478555560f736dce4824f08ebd5cb08
- Report publication commit: SELF

## Outcome (bounded, honest)

The public native-owner integration
(`scripts/cache_native_fixture_native_owner.py` +
`scripts/cache_native_fixture_local.py`) now binds the staged
subject registration to the SAME actual owner's measured
registration, revalidates the FROZEN context against the
ORIGINAL immutable binding (not a discarded re-resolution), and
makes terminal publication ONE-SHOT per completed owner so a
publication failure can never become a new qualifying
publication. Everything is exercised in this round EXCLUSIVELY
with injected fake external operations (fake git/platform/
process seams and owned synthetic repositories): the real
backend code is imported and its real methods driven; the
platform operations are faked. This earns NO native,
worker-stop, Docker, rehearsal or handoff qualification; D09
remains `NOT RUN`; the historical S admission stays consumed;
no v1 runtime claim is made.

## 1. Delivered coherence repairs (order sections 1-3)

- Section 1 — owner-bound staged registration
  (`NativeOwnerRun.register_subject`): before forwarding to the
  workflow, the owner must be MEASURED (a string `target_cid`
  plus the registered artifact `binary_sha256` string — else the
  closed `native-owner-registration-unmeasured`), the
  expectation's CID must equal the owner's measured CID
  (`native-owner-subject-cid-mismatch`) and its expected binary
  must equal the owner's registered artifact binary
  (`native-owner-subject-binary-mismatch`). A matching foreign
  expectation + foreign channel, or a matching foreign expected
  + measured binary, cannot redefine this owner's subject; the
  collector's agreement with its own expectation/channel is not
  ownership attestation. The workflow's prepared/recorded-stop/
  CURRENT stable-stop/full-inventory/W-B birth-group-session-TTY/
  run gates, the immutable baseline/stop/subject receipts and
  the matching positives are preserved; a refused registration
  commits nothing and a later genuinely matching registration
  within the same still-valid measured phase succeeds; a
  conflicting second adoption is refused; recovery remains
  allowed (stateless owner-context check).
- Section 2 — frozen-context revalidation (local fixture owner,
  new-order branch): the discarded `resolve_order_binding`
  re-resolution is replaced by the complete existing
  frozen-context validation seam —
  `oap_binding._revalidate_repo_context(git_runner or
  oap_binding._git_default, repo, binding.order_id, binding)` —
  comparing the ACTUAL current repository identity, literal
  head, committed and disk active, exact unique order path/
  bytes/hash and other bound context to the ORIGINAL
  immutable binding before owner adoption/external mutation;
  `bind_head != binding.source_head` is a closed
  `local-binding-invalid` at the branch top. A refusal after
  winning the admission closes THAT SAME attempt honestly (a
  terminal fail in the bound namespace) with no external
  action and no second run identity minted or adopted. The S
  default path is unchanged.
- Section 3 — one-shot terminal publication
  (`publish_native`): once publication begins for a COMPLETED
  owner, the attempt latches (a second call — including to a
  FRESH path — is the closed `native-owner-published` refusal;
  no hidden retry/new-path escape). Pre-retention failures
  (verdict derivation, record parse, protected write;
  `FixtureError` or a serializer `TypeError`/`ValueError` →
  `internal`) close the still-pending attempt as fail through
  the owner-failure closure and propagate — no qualifying pass
  is ever left behind. Post-retention finalization is read from
  the ACTUAL bound journal, not a hardcoded assumption: a
  converged pass requires the verified `finalized` token; a
  terminal outcome accepts the same terminal state preserved by
  the journal (`terminal-preserved`) or finalizes a still-
  running journal requiring `finalized`; an unverified or raced
  finalization is the closed
  `native-owner-finalization-unverified`, which preserves BOTH
  the retained immutable evidence bytes AND the actual journal
  facts (unverified → journal stays `running`; raced → stays
  `fail`) and never returns a normal qualified success. The
  owner's cleanup/export outcome remains distinct from the
  qualified attempt's terminal publication outcome; the real
  finalize token is retained in RAM/result only and the
  immutable retained evidence is never rewritten.

## 2. Defects found and repaired in-flight (first failures preserved)

The W trigger: at the V final implementation head `a18401e`
(module digest `b46f28bdc187`), NEW actual public fake-lifecycle
proof was 1/4 (the matching positive passed; foreign-CID and
foreign-binary registrations were wrongly accepted — the
collector proves agreement with the EXPECTATION/channel, not
with this owner's registered CID/artifact) and context-drift
proof was 3/4 (a git-origin change after the won admission but
before actual owner construction was accepted — the fresh
resolver result was discarded without comparison to the
original binding; the attempt stayed `running`); a separate
publication-boundaries probe was 1/4 (after a real protected-
writer refusal, a later `publish_native` to a fresh path wrote a
ready record falsely labelled `attempt=running` while the
journal remained `fail`, and unverified/raced finalizations
returned normal qualified success). All first-failure captures
are preserved in the strategic reviews
(`017-v-public-lifecycle-first-a18401e9ffaf.json`,
`017-v-owner-context-drift-first-a18401e9ffaf.json`,
`017-w-publication-boundaries-first-b46f28bdc187.json`).

In-flight scoped rechecks (original probe assertions and valid
positives unchanged; source/fixture bytes verified stable per
run): the binding increment at module `f5a1ef9b12a1`
(context-drift 4/4; public lifecycle 3/4 with the
failed-publication case still pending as expected); the
`bind_head` closure at `0d56ac449363` (all three public probes
4/4); the publication error-closure at `59073805e426` (4/4 —
its FIRST run overlapped a concurrent source edit and is
preserved by strategy as source-changing INTERIM, not
qualifying: `017-w-error-closure-interim-source-changing.json`);
and the pre/post-retention separation at the final module
`5f187adb0d34` (lifecycle/boundaries/error-closure 4/4 + 4/4 +
4/4, preserving the tracked journal-preservation assertion).

## 3. Public local proof

- Tracked suite
  `tests/test_cache_native_fixture_native_owner.py` is 19 tests
  (12 V + 7 W): the seven new regressions
  `test_foreign_owner_context_refused_then_recovered`,
  `test_origin_drift_before_owner_construction_refused_and_
  terminal_fail`, `test_failed_publication_terminalizes_and_
  blocks_fresh_retry`,
  `test_unverified_finalization_cannot_return_qualified_
  success`, `test_raced_terminal_fail_cannot_return_qualified_
  success`,
  `test_completed_run_measurement_failure_closes_and_blocks_
  retry`, `test_publication_serialization_failure_closes_and_
  blocks_retry`; the one V pre-prepare token was updated to the
  new `native-owner-registration-unmeasured` closed reason.
  Fresh run at the implementation head: 19 passed in 1.26 s.
- Focused tracked suites together at the implementation head:
  local 49 + native-prep 124 + binding 45 + native-owner 19 =
  **237 passed in 16.57 s** (Python 3.12, repo venv). The
  repaired direct-constructor regression and the production
  hosted-refusal negative additionally pass with the ambient
  `GITHUB_ACTIONS=true` + `DOCKER_HOST` removed-for-test
  environment (68 passed in 15.99 s for local + native-owner).
- The ten private probes (the six earlier V controls + the two
  NEW W public proofs + publication boundaries + publication
  error closure) all pass at the final source with valid
  positives and source/fixture bytes verified stable:
  coding-agent rerun `ten-probes-5893f02.json` (10/10, this
  round) and root independent re-execution at the literal head
  (all ten passed, 52 assertions, probe hashes unchanged).
- The real backend path stays unexecuted against any real
  backend: no actual Docker operation, no native launch
  (including help/version), no worker stop, no TTY/job
  manipulation, no real fixture admission in the real checkout
  (the actual `.oap-local/` holds only the historical 017-s
  record; all W admissions are in owned synthetic temporary
  repositories with fake git seams), no host signal, no CLI
  entry.

## 4. Final verification at implementation head 5893f02

All in ONE shell with `umask 022` at the committed candidate
(log: `/home/janezp/oap-017w-work/final-full-gate-5893f02.log`):

- `uv sync --frozen --extra dev`: 31 packages, no changes.
- FULL `pytest -q`: **3157 passed, 28 skipped in 486.69 s**
  (V baseline 3150 passed + 7 new; skips are the pre-existing
  environment skips, unchanged).
- `compileall src scripts`: OK. `ruff check .`: clean. `ruff
  format --check .`: 560 files already formatted. `mypy src
  tests`: no issues in 117 source files. `docs_consistency_
  check`: OK (19 claim docs). `uv lock --check`: OK (lock
  unchanged).
- `uv build --out-dir dist` (BEFORE the final artifact gate):
  wheel `1f2ebaff444be1ae90a7f1d863f462abcc82ff28caca448e28c206699fa4b50c`
  (142,753 B) — byte-identical across P/R/S/T/U/V/W (W touches
  no `src/`); sdist `b5c7201471d3449a106c8b59b6e6fed493f691c946a995ab56cd341c29166805`
  (896,690 B, 194 entries — the delta from the e05 sdist is
  the one repaired test file). `artifact_policy_check
  --inspect` over the CURRENT build: ok, no violations;
  `--install-smoke`: OK (fresh smoke venv, entrypoint
  help/version, installed 0.1.0). `dev_provenance_manifest
  --verify`: OK at the literal head (196 complete inputs).

Clean-archive reproduction at the LITERAL head 5893f02 (fresh
0700 root `archive-build-5893f02`, outside the source tree):
`git archive` of the literal head; **196/196 manifest inputs
present and byte-identical**; actual `uv build` with out-dir
outside the source tree; **both artifacts
byte/hash/size-identical to the manifest and to the repo
dist**; **30/30 installed Python module bytes** in the
archive-built wheel match the archive source
(`archive-wheel-identity-5893f02.json`). Root's independent
final artifact/proof review at the same head re-verified the
196/196 archive inputs, the ten fixture-helper archive/
worktree equality, both artifact identities (archive/
manifest/working-dist) and 30/30 fresh-installed module bytes
(`reviews/017-w-final-artifact-and-proof-review-5893f0241478.
json`). Separately, a fresh non-editable Python 3.12 venv
OUTSIDE the checkout (`fresh-venv-312`) with the
archive-built wheel: **27/27 unique installed functional
cases PASS** with the identity assertions (separate, not
counted) — site-packages outside the repo, version 0.1.0, no
repo path on sys.path (`installed-functional-5893f02.json`).
Unchanged frozen 21 at the literal implementation head via the
repo Python 3.12 venv: **21/21 PASS, all 21 probe baseline
hashes unchanged**; the resource-probe measured-only
`preflight_peak_bytes` diagnostic validated as a strict
bounded int (1,054,410 < 4 MiB) (`probes-final-5893f02.json`;
root's official frozen-21 actual run remains attributed to the
earlier `e05e64c` checkpoint, not relabeled).

## 5. GitHub CI (all 10 implementation checks)

- FIRST run 40443824858 at the e05 checkpoint
  (`e05e64c9fd0c8fd4371ed8767abaad5cac86b81f`): 9 checks
  success, the `test` job (121990204407) FAILED with **1
  failed, 3156 passed, 28 skipped in 341.94 s** — the sole
  failure `test_origin_drift_before_owner_construction_
  refused_and_terminal_fail` expected
  `bind-repo-identity-mismatch` but received
  `local-hosted-env`: the new direct-constructor regression
  inherits the hosted `GITHUB_ACTIONS=true` ambient, so the
  production local-hosted-env guard fires before the intended
  fake drift is compared. Local 3157 passes do NOT substitute
  for this hosted failure; it is preserved, not relabeled
  (job log retained at
  `/home/janezp/oap-017w-work/ci-test-job-121990204407.log`;
  strategy `reviews/017-w-CI-first-e05e64c-failure.json`).
- Repair (test-only): that regression now applies the same
  local-environment isolation as the suite's `_hermetic`
  helper — test-local removal of the ambient `GITHUB_ACTIONS`
  and the caller endpoint selector variables — before
  constructing the owner directly. The production guard, the
  exact drift/no-action/terminal-fail assertions and the
  hosted-refusal negative are all unchanged.
- REPAIRED run 40445121325 at the literal implementation head
  5893f02: **ALL 10 check runs `success`** — `test` (job
  121994443003: **3157 passed, 28 skipped in 313.63 s**),
  `gateway-contract`, `operator-session`,
  `cache-native-containment`, `docker`,
  `cache-native-fixture`, `docker-published`, `CodeQL`,
  `Analyze (python)`, `Analyze (actions)`. No Codex in CI.
  Test-job log retained at
  `/home/janezp/oap-017w-work/ci-test-job-121994443003.log`;
  strategy `reviews/017-w-CI-repaired-5893f0241478.json`.

## 6. Append-only post-V findings (order section 4)

Restated in W per the order (V's own report is immutable):

- At the V final implementation head `a18401e` (module digest
  `b46f28bdc187`), the NEW actual public fake-lifecycle proof
  was 1/4 and the context-drift proof 3/4 — V was therefore
  NOT accepted as complete, and these were repaired and
  qualified in W (green CI at V did not cover these cases).
  The publication-boundaries first failure (1/4) at the same
  module digest was likewise repaired in W.
- V's "no real process" shorthand is clarified as: NO real
  worker/Bash/unrelated process was signalled or stopped in V
  (or W). The existing tiny exact-owned test children ARE
  actual processes that the tests' own permitted cleanup
  kills and waits (if still alive); that allowed test action
  is what V's suite uses and no protected-host violation is
  inferred from it. V is not rewritten.
- The U-era /tmp round-metadata mode-only repairs made in V
  remain byte/inode-preserving and untouched (re-verified in W):
  `/tmp/report-017u-draft.md` (532 B, mode 0600, inode
  8079833) and `/tmp/u-report-remote.md` (19,351 B, mode 0600,
  inode 8081327) — digests match the V-recorded values; no
  content was printed, overwritten or otherwise touched.

## 7. NOT RUN (explicit)

- NO actual local Docker operation in W (the native/Docker
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
- D09 remains `NOT RUN`; the later serial native handoff
  remains a separately authorized order; legacy default
  unchanged; v1 runtime not implemented; whole 017 and
  018-024 remain required.

## 8. Preserved failures and disclosures (not erased)

- First-failure captures, retained in the strategic review
  records: public-lifecycle 1/4 and context-drift 3/4 at head
  `a18401e` (module `b46f28bdc187`); publication-boundaries
  1/4 at module `b46f28bdc187`; plus the W interim rechecks at
  `f5a1ef9b12a1` / `0d56ac449363` / `59073805e426` /
  `5f187adb0d34` (the error-closure first run overlapped a
  concurrent edit and is preserved as source-changing INTERIM,
  not qualifying).
- First CI failure at the e05 checkpoint: run 40443824858,
  test job 121990204407, 1 failed / 3156 passed / 28 skipped in
  341.94 s (the direct-constructor regression meeting the
  production hosted-env guard under the ambient
  `GITHUB_ACTIONS=true`); full job log retained; repaired by
  the test-only isolation above. No product or test failure
  remains at the implementation head; no skipped, pending,
  missing or unavailable evidence is presented as pass; the 28
  skips are the pre-existing environment skips (identical set
  to V).
- Driver setup failures (disclosed, preserved): (a) the e05
  wheel-control retry-1 exited 2 because the driver file had
  been moved to `superseded/` before the retry (venv created,
  wheel installed, driver not found); the venv is retained at
  `superseded/fresh-venv-312-retry1` and the re-run (retry-2)
  is the retained e05 PASS; (b) the e05 frozen-21 first run
  SyntaxError (an apostrophe inside a single-quoted note
  string) was fixed to `the resource-probe` and re-run
  PASS; (c) the A-bound (6e4428c) archive/frozen drivers were
  NEVER executed (moved to `superseded/` before running — no
  preliminary-A outputs exist and none are claimed); (d) the
  e05 dist artifacts are preserved at
  `superseded/dist-e05e64c/` and the e05 fresh venv at
  `superseded/fresh-venv-312-e05e64c/`; (e) a nohup-launched CI
  poller died with its launching exec session (its log holds
  only the `begin` line) and was replaced by direct polling —
  a setup diagnostic, not a result.
- Pre-SELF modes disclosure (not "all files 0600 from
  creation"): the initial gate log `final-full-gate-5893f02.
  log` was created 0644, the poller log `ci_poll_5893f02.log`
  0664, and the PR body fetch `pr25-body-refresh.md` 0664
  (session-umask redirect) beneath the protected 0700 W root.
  All owned evidence/metadata files were set to 0600 by exact
  path during the final audit (initial modes disclosed in §9);
  the outer 0700 root remained protective throughout, so no
  external exposure is inferred. Existing evidence bytes/
  inodes were preserved; archive/output/venv tool trees keep
  their intended modes (no blanket chmod).

## 9. Evidence root and file audit (fresh, explicit)

`/home/janezp/oap-017w-work/` (0700; uid 1001) — path-by-path
final audit of ALL owned evidence/drivers/logs/drafts/temporary
round metadata including the audit itself
(`owned-files-audit-preself.json`), produced immediately before
SELF. Initial modes and exact-path corrections are recorded in
the audit (see §8 disclosure); archive-build/venv/superseded
tool trees are listed with their intended (non-evidence)
modes. **61 owned files + 4 directories audited in the W tree (the
audit file itself, created 0600, is named here and not listed);
0 nonconforming after corrections; plus ONE exact owned
temporary metadata path outside the W root —
`/tmp/pr25-remote-check.md` (the remote-body fetch made while
verifying the first body patch; regular file, uid 1001, inode
8500772, 30,358 B, initial mode 0664 → exact-path 0600 before
SELF, bytes byte-identical to the first-patch body plus one jq
output newline, sha256
`1d702e341d9018a99014fb548e1d878a272e66b530cc3acf899ff31ef514fb5e`
— superseded by the concise body patch; only exact paths
created by this round were checked, no broad `/tmp` scan).** Exact-path corrections applied (initial
modes disclosed — not every file was 0600 from creation):
`final-full-gate-5893f02.log` 0644, `ci_poll_5893f02.log` 0664,
`pr25-body-refresh.md` 0664, `pr25-w-body-final.md` 0664,
`pr25_w_rewrite.py` 0664, `pr25-w-body-concise.md` 0664 (all
→ 0600), `/tmp/pr25-remote-check.md` 0664 → 0600 (outside the
W root; see the temporary-metadata entry), the four helper scripts
`ci_poll.sh` / `ci_poll_5893f02.sh` /
`final_full_gate_5893f02.sh` /
`wheel_control_017w_launcher_5893f02.sh` (0700 → 0600), and
the preserved e05 dist artifacts
`superseded/dist-e05e64c/` (files 0644 → 0600; directory 0775
→ 0700). All other owned files were 0600 from creation. The
tool trees (`archive-build-e05e64c/`,
`archive-build-5893f02/`, `fresh-venv-312/`,
`superseded/fresh-venv-312-e05e64c/`,
`superseded/fresh-venv-312-retry1/`) are excluded with their
intended (non-evidence) modes — no blanket chmod. The outer
0700 root was protective throughout; no external exposure is
inferred; existing evidence bytes/inodes were preserved.

## 10. Identities and limitations

- W commit chain on `oap/017-cache-read-observation`: source A
  `6e4428c19e417ac922a510185e7ddf8b3cf9b4cb` (11 tracked paths:
  the two scripts, the test file, six doc paths, `oap/active`,
  the W order); manifest B `e05e64c9fd0c8fd4371ed8767abaad5cac86b81f`
  (only `packaging/dev_provenance_manifest.json`, 196 inputs);
  source A2 `8155920298bd300e7dc55289f854d821e6486980` (1
  tracked path: the test-only CI-hermetic repair); manifest B2
  / implementation head
  `5893f0241478555560f736dce4824f08ebd5cb08` (only the
  manifest: sdist rebound to the repaired test file, wheel
  unchanged). Remote PR head verified equal to the
  implementation head after push (in-memory).
- Final source module digests at the implementation head:
  `scripts/cache_native_fixture_native_owner.py`
  `5f187adb0d348bfae13e7a05193399a59d035bbf9bdf04771d9b1451721cfb28`;
  `scripts/cache_native_fixture_local.py`
  `ee182d76337331f1487da04f1fce30b803b5b69235e71854edfb68e60f6a6f74`.
- Wheel `1f2ebaff444be1ae90a7f1d863f462abcc82ff28caca448e28c206699fa4b50c`
  (byte-identical P/R/S/T/U/V/W); sdist
  `b5c7201471d3449a106c8b59b6e6fed493f691c946a995ab56cd341c29166805`
  (896,690 B, 194 entries); development manifest: 196 complete
  inputs, toolchain python 3.12.15 / uv 0.12.5 / lock
  `1237cbd179f71b99984c80f927529549f5e61eb705585ef9cf2ab0fa9e26764a`.
- Limitations: public fake integration only — the real
  backend code path is unexecuted against any real backend;
  the owner's cleanup/export outcome is distinct from the full
  handoff/restoration qualification; the historical S record is
  historical S scope; nothing in this round qualifies a native
  subject, a real Docker attachment, or runnable native
  handoff; the visible handoff still requires its own
  separately authorized order with measured facts.

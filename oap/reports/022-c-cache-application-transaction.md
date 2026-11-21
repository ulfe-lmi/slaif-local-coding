# OAP Coding-Agent Report — 022-c

## Work order
- Identifier: 022-c; order path
  `oap/orders/022-c-cache-application-transaction.md`; numeric
  objective 22
- PR mode: AMEND_EXISTING_PR on the ONE existing PR 30
  https://github.com/ulfe-lmi/slaif-local-coding/pull/30, branch
  `oap/022-cache-source-replacement`, from report-only head
  `8bd38c5bd826d41404fca305207824316f84cb3e` and order-verified
  remote main `144af0bd5e34387afcb8e3f9ddf761eabd56e817`. No new PR,
  no merge, no auto-merge.

## Status
COMPLETE

## Executive summary
ACTUAL RESULT: the v1 application transaction is implemented at
source A `f248817d5d8c0de2b36449cb3e93990cb09df359` on the same
branch/PR 30, amending the PR head from `8bd38c5…` to
implementation head B `83513fa2f747b782dd83d7321d3bc01e64c92f97`
(manifest-only child). The runnable v1 runtime is wired on opted-in
governed routes through the ACTUAL `create_app` entry point
(`app.py`, the new `v1_runtime.py` and `v1_application.py`):
(1) the closed historical read-root replay gap — a positively
superseded read-root original is joined at its own retained
coordinates through the governing read/read_region source with its
carrier a tool result, that exact (occurrence, segment) coordinate
is skipped by the FILE join so the same root region is never
double-edited, the historical old-anchor envelope is kept separate,
and the stale live format is refused on replay; (2) the governed
request path — the marker-shaped source replay is detected and
authenticated BEFORE the transition's raw acquisition (the fixed
typed marker-side refusal, no raw fallback), the single outgoing
body of the one main upstream forward, the byte-identical
transformed-round fixed point, and the fixed typed v1 refusal
family (422 budget/invalid transform, 409 version/scope conflict,
503 infrastructure/recovery/resource); (3) the per-request FROZEN
represented-frontier trusted issuance binding — the ACTUAL direct
main upstream response only (actual nonstream and split-SSE
issuance causality over bounded chunk seams, never compiler
traffic), each COMPLETE supported call registered under the
committed-state CAS against the exact represented completed-fact
frontier of THIS specific committed request (the represented root
fact plus every selected file entry's witness provenance and
verified raw-carrier join of this payload, reduced over PROVEN
frozen ancestors only; retention alone never establishes a parent;
the frontier freezes at this request's commit and is never rebased
on later state, caller items, result arrival, new call IDs,
revisions or replay metadata — two distinct frozen frontiers prove
no later-fact rebasing); (4) the pre-forward protected generation
through the accepted 020 owned/fenced admit/checkpoint path (cold,
resumed and steady-state owners alike, no raw writer shortcut) with
the retained successful publish bound to the exact snapshot/epoch
it actually published — a faulted publication keeps the prior
bound, the newer undurable record set is refused on replay and
never forwarded under the stale generation proof, and a replay
after fault refuses until the generation heals (proven through the
actual FastAPI/fake-upstream path); and (5) the application-owned
private marker key as a PROTECTED ENVIRONMENT REFERENCE
(`marker_key_env`) resolved once at v1 runtime construction
(repr-suppressed, never a gateway/service credential, never
persisted, logged or echoed). Process qualification: at the
checkpoint where the §3/§4 strategic binding defects were found,
the focused four-file regression stood at 311 passed; after the
bindings (per-request frontier membership derived from this
request's verified raw-carrier joins and selected compiled-entry
witness/root provenance with proven-ancestor reduction, and the
retained publish bound to the exact snapshot/epoch it actually
published) it stood at 314 passed; the final focused coverage
including the two §4 app-level E2E tests is 316 passed / 0 failed.
The 023 expanded adversarial/lifecycle/telemetry matrix and the 024
actual-model/genuine-Codex qualification remain NOT RUN and are not
declared earned by this round.

## Authoritative GitHub state
- Repository: ulfe-lmi/slaif-local-coding; PR 30
  https://github.com/ulfe-lmi/slaif-local-coding/pull/30 (state open)
- Base: main `144af0bd5e34387afcb8e3f9ddf761eabd56e817` (order-
  verified remote main, the accepted 021 merge)
- Head: oap/022-cache-source-replacement
  `83513fa2f747b782dd83d7321d3bc01e64c92f97`
- Implementation head SHA: 83513fa2f747b782dd83d7321d3bc01e64c92f97
- Report publication commit: SELF
- Implementation structure: source A
  `f248817d5d8c0de2b36449cb3e93990cb09df359` (the 022-c
  application-transaction slice on the branch since the 022-b
  report-only head `8bd38c5…`) and manifest-only B
  `83513fa2f747b782dd83d7321d3bc01e64c92f97` (sole parent A;
  exactly `packaging/dev_provenance_manifest.json` changed; 316
  source inputs; wheel `90b022004df33d47dd3e6410997a80a157b5c6820a627d2c6f7a229284ede3a0`
  4,459,172 bytes; sdist
  `b3e9987544ce2c24990cf6e41ffc10ae59bcd835cf7928cab89d68947bcc0847`
  6,167,111 bytes). The exact activated order bytes and `oap/
  active` are committed in the branch and published on the PR
  (strategic-authored bytes unchanged).

## Changes and files
At source A (18 paths: 4 new + 14 modified):
- `src/slaif_local_coding/app.py` (the governed v1 request path:
  session join, marker pre-check, advance, transaction, single
  outgoing forward, post-forward issuance context over the actual
  direct main response for both stream and nonstream; v1 runtime
  construction and teardown)
- `src/slaif_local_coding/config.py` (the closed `marker_key_env`
  protected environment reference on the v1 profile; the v1
  closure requires it; legacy conflict law extended)
- `src/slaif_local_coding/constitution/bundles/v1_runtime.py`
  (NEW: the process-owned v1 runtime: recovery store, pinned
  tokenizer, RAM registry, direct tool-free compiler channel,
  governed-route contracts, admission mode, the resolved marker
  key, the fixed typed startup refusal order)
- `src/slaif_local_coding/constitution/bundles/v1_application.py`
  (NEW: the v1 application transaction: cold/resumed/steady-state
  session join over the accepted 020 owned/fenced path, the
  retained-publish bound law, the replay shadow pre-check, the
  per-request represented frontier, the compile-and-select
  transaction, the FROZEN frontier issuance context with the
  bounded nonstream/split-SSE assembly, the fixed typed refusal
  family)
- `src/slaif_local_coding/constitution/bundles/bundle_replace.py`
  (the §1 historical read-root replay seam: the governing
  read/read_region root splice, the retained read-root join, the
  stale live format refusal)
- `src/slaif_local_coding/constitution/bundles/bundle_replace_
  models.py` (the §1 models)
- `tests/test_v1_application.py` (NEW: the app-seam suite —
  cold bootstrap, generation advance/replay, resume in a higher
  epoch, rootless-not-governed, distinct addresses, round fixed
  point, pre-forward compiler/publish/budget refusals, the
  per-request frontier law, nonstream/streamed issuance and
  negatives, CAS refusal on a drifted owner, tampered marker
  before raw acquisition, resumed-session publish materialization)
- `tests/test_app.py` (the `TestV1GovernedRequestPath` app-level
  suite over the ACTUAL `create_app` entry point with a bounded
  fake upstream: the round fixed point and marker refusal,
  issuance marks the read next round, the error response earns no
  issuance, compiler traffic never observed, the two distinct
  frozen frontiers over actual split-SSE + nonstream, and the
  replay-after-fault through the real FastAPI/fake-upstream path;
  plus the v1 startup-order tests and `marker_key_env` edges)
- `tests/test_bundle_replace.py` (the §1 read-root replay tests
  over the actual prepared T result)
- `tests/test_config.py` (the `marker_key_env` closure and
  conflict edges)
- `ARCHITECTURE.md`, `ARCHITECTURE-for-agents.md` (scoped 022-c
  map updates), `oap/strategic-instructions/ARCHITECTURE-for-
  agents.md` (byte-identical mirror), `SECURITY.md` (the v1 store
  active scope and the marker-key law), `docs/ADAPTER-CONFIGU-
  RATION.md` (the v1 runtime status, the `marker_key_env` field,
  the component status), `docs/CACHE-REWORK-LEDGER.md` (the 022
  row scoped to evidence actually run)
- `oap/active` (`022-b`→`022-c`) and
  `oap/orders/022-c-cache-application-transaction.md` (activated
  transcript bytes, unchanged from the strategic authoring)

## Acceptance evidence
### Section 1 (historical read-root gap)
- Result: PASSED. A positively superseded read-root original is
  joined at its own retained coordinates through the governing
  read/read_region source (the carrier stays a tool result; the
  resolved source's ACTUAL occurrence/proof at its own segment
  provenance; that exact (occurrence, segment) coordinate is
  skipped by the FILE join so the same root region is never
  double-edited; the historical old-anchor envelope is kept
  separate); the transformed replay verifies the current root
  LIVE in its read carrier plus the old-anchor EVIDENCE marker,
  and the stale live format is refused. Evidence:
  `tests/test_bundle_replace.py::
  test_superseded_read_root_raw_evidence_and_replay` and
  `::test_superseded_read_root_stale_live_refuses` (re-proven at
  exact B by gate cmd07).
### Section 2 (governed request path wired)
- Result: PASSED. Over the ACTUAL `create_app` entry point with a
  bounded fake upstream (synthetic identity, no secrets): the
  marker pre-check runs BEFORE raw acquisition; the transformed
  round one carries the root LIVE marker with the unacquired
  carrier raw; the resent transformed payload is the byte-
  identical fixed point with the RAM-hit compile reuse; a
  tampered tag is the fixed 409 marker-side refusal with NO raw
  fallback forward and nothing committed; the v1 startup
  failures (recovery root, marker key missing/out-of-range)
  precede HTTP client construction; the legacy profile stays
  usable through its existing entry point. Evidence:
  `tests/test_app.py::TestV1GovernedRequestPath::
  test_governed_round_fixed_point_and_marker_refusal`, the v1
  startup tests (`test_v1_profile_startup_*`) and
  `test_explicit_legacy_profile_stays_usable_through_existing_
  entry_point`.
### Section 3 (trusted tool issuance bound to the forwarded request)
- Result: PASSED. The round-one ACTUAL direct upstream response
  issues the trusted call through the per-request frozen issuance
  context (committed under the state CAS and the protected
  generation; the matching read pair is ACQUIRED next round and
  the single outgoing body carries both markers); a 400-or-higher
  error response earns NO issuance (the paired read stays
  unacquired-retained UNANCHORED, no temporal edge); compiler
  traffic is never fed to the observer (a well-formed tool call in
  the compiler completion earns no issuance); the per-request
  frontier is derived from THIS request's verified raw-carrier
  joins and selected compiled-entry witness/root provenance,
  reduced over proven ancestors only (a retained occurrence this
  request does not represent adds no member); a drifted owner is
  a CAS refusal, never a rebase; a tampered marker is refused
  before raw acquisition. Evidence: `tests/test_app.py::
  TestV1GovernedRequestPath::test_upstream_tool_call_issuance_
  marks_the_read_next_round`, `::test_upstream_error_response_
  earns_no_issuance`, `::test_compiler_traffic_never_observed_
  for_issuance`; `tests/test_v1_application.py::
  test_represented_frontier_is_per_request_and_reduces_proven_
  ancestors`, `::test_issuance_cas_refusal_when_the_owner_drifted`,
  `::test_tampered_marker_is_refused_before_raw_acquisition`, the
  streamed-issuance positives/negatives and the nonstream
  negatives.
### Section 4 (required proof and publication)
- Result: PASSED at the bounded fake-upstream application scope.
  Actual fake-upstream HTTP request bodies and real app
  responses are inspected: first acquisition and real normal-hit
  reuse (round-one compile, round-two RAM hit, compile counts
  asserted), exact replacements preserving tool/image/prefix/
  Unicode metadata (marker counts, no raw source, wrappers and
  roles preserved), now-current and stale old references (the
  fixed-point replay; the stale live refusal), source still
  carried after reduction (the retained working-set entries and
  the 022-b entry-point guards re-proven), source-absent
  rehydration (the 022-b source-absent pairing re-proven),
  different trusted namespaces (the 022-b cross-namespace
  refusal re-proven), signed-route/failure and streaming/
  disconnect contracts (the static trusted closure; the typed
  refusal family; actual split-SSE over real chunk seams; the
  unchanged legacy disconnect/timeout tests re-proven), both
  governed read endpoints wired (the app-level fake-upstream
  evidence in this round exercises `/v1/responses`; both read
  endpoints are covered at the 022-b pure transaction layer),
  actual nonstream and split SSE issuance causality,
  inbound fabrication/no anchor (the tampered-tag 409 with no
  raw acquisition; the error-body no-issuance; the
  UNANCHORED-retained occurrence carries no temporal edge), old
  root/nonroot supersession/replay/revert (the §1 read-root
  replay tests and the 022-b supersession/revert matrix re-
  proven), and the DELAYED-receipt case whose two distinct
  frozen request frontiers prove no later-fact rebasing (the
  round-one split-SSE issuance registered under the round-one
  frontier root fact + cA occurrence, never including the later
  receipt; the round-two reduced frontier is exactly the single
  new occurrence; the two retained issuances carry two DISTINCT
  frontiers). Trusted single-session recovery and pre-forward
  typed rejection for checkpoint/compiler/budget failures
  through the actual accepted contracts: the cold bootstrap
  commits and publishes generation one; a new read advances the
  generation then replays; a RESUMED session restores state in a
  higher epoch and materializes its retained record set's
  generation on its first ordinary hit (the fixed point); the
  pre-forward compiler refusal is typed and retries nothing; a
  faulted checkpoint refuses the fixed 503 with the exact prior
  state kept (the retained pointer and bound untouched); a
  budget crossing refuses at cold publish establishment; and the
  replay-after-fault case through the ACTUAL FastAPI/fake-
  upstream path (the round-two commit applies — RAM revision
  two — while the protected generation faults on fsync: fixed
  503, no forward, durable generation one and its bound
  untouched; the SAME payload resent while the fault persists is
  refused again — the retained generation-one pointer is bound
  to the revision-one snapshot it actually published and can
  never prove the newer undurable record set; once the fault
  heals the same payload publishes generation two and the
  transformed body is the byte-identical fixed point).
  Evidence: `tests/test_app.py::TestV1GovernedRequestPath::
  test_two_distinct_frozen_frontiers_never_rebase_on_later_
  facts` and `::test_publish_fault_refuses_replay_until_the_
  generation_heals`; `tests/test_v1_application.py::
  test_cold_bootstrap_commits_and_publishes`, `::
  test_new_read_advances_generation_then_replays`, `::
  test_resume_restores_state_in_a_higher_epoch`, `::
  test_resumed_session_materializes_publish_and_replays_the_
  fixed_point`, `::test_pre_forward_compiler_refusal_is_typed_
  and_retries_nothing`, `::test_pre_forward_publish_refusal_
  when_the_checkpoint_fails`, `::test_pre_forward_budget_
  refusal_keeps_the_exact_prior_state`. Synthetic fixture
  sources throughout; actual forwarding, compiles and recovery
  content reads instrumented (no counter-only substitution).
  023 keeps the complete expanded adversarial/lifecycle/telemetry
  matrix; 024 keeps actual-model/genuine-Codex qualification
  and immutable handoff — NOT RUN and not declared earned.
- Marker-claim scope: `verify_marker` is the pure validation
  primitive (a valid transformed marker is never accepted as a
  new raw source proof), and the request replacement path
  performs its geometry observation before its final replay
  scan; the actual pre-acquisition wiring into lineage/state
  belongs to the application slice delivered in this round,
  exercised at its bounded fake-upstream scope.

## Verification
- Focused suites at source A (before the candidate freeze), true
  exits: `umask 022 && uv run --frozen pytest -q tests/
  test_bundle_replace.py tests/test_v1_application.py` — 115
  passed, exit 0 (the pure transaction + app-seam layer);
  `umask 022 && uv run --frozen pytest -q tests/test_app.py
  tests/test_bundle_selection.py tests/test_config.py` — 223
  passed, exit 0 (the ordered app/selection/legacy regression);
  the four-file combined run 316 passed / 0 failed; ruff check,
  ruff format --check, mypy (src tests) and
  `scripts/docs_consistency_check.py` (19 docs) clean before the
  freeze and re-proven at exact B by gate cmd03–cmd06.
- 15-command locked gate at exact B (`gate-driver-022c.sh`,
  managed absolute-path invocation, run dir `gate-run1`, driver
  pid 2561198 birth 381612420, ppid 2561197, uid 1001, capture
  umask 077, driver source_sha256
  `5277abb437627d9b5ba9ca94c78f25253c7a7eacac0836b00e4e882341e00e55`
  (post-hoc correction recorded in the run dir: the startup
  sha256sum ran after the driver cd with a relative `$0`),
  started 2026-11-20T19:31:46Z, head `83513fa…`):
  ALL 15 commands rc=0: cmd01 `uv lock --check`; cmd02 `uv
  sync --frozen --extra dev`; cmd03 `ruff check .`; cmd04 `ruff
  format --check .`; cmd05 `mypy src tests`; cmd06 `python
  scripts/docs_consistency_check.py` (19 docs); cmd07 `bash -c
  'umask 022; uv run --frozen pytest -q'` — 7114 passed, 28
  skipped, 16 warnings in 1524.34s (0:25:24); cmd08 `uv build`;
  cmd09 `python scripts/artifact_policy_check.py --dist dist
  --inspect`; cmd10 `python scripts/artifact_policy_check.py
  --dist dist --install-smoke`; cmd11 `python --version` —
  `Python 3.12.15`; cmd12 `python -m compileall -q src tests
  oap/bin scripts`; cmd13 `python scripts/dev_provenance_manifest.
  py --verify --dist dist` — `development provenance OK:
  state=development head=83513fa2f74`; cmd14 `bash -n` over
  `oap/bin/*.sh packaging/*.sh`; cmd15 `git diff --check
  144af0bd5e34387afcb8e3f9ddf761eabd56e817 HEAD` — every
  command PASSED.
- TEN required exact-B GitHub checks at `83513fa…`:
  ALL 10 pass at the exact head: the CI workflow
  (`.github/workflows/ci.yml`) ran exactly once (run
  44802784441, event pull_request, conclusion success, no
  rerun) with test (pass, 15m17s), cache-native-containment
  (pass, 42s), cache-native-fixture (pass, 1m39s), docker
  (pass, 2m1s), docker-published (pass, 1m15s),
  gateway-contract (pass, 14s) and operator-session (pass,
  1m4s); the PR #30 code-scanning workflow (run
  44802768739, conclusion success, no rerun) contributed
  Analyze (actions) (pass, 35s), Analyze (python) (pass,
  1m10s) and CodeQL (pass, 5s). No failures, no cancellations,
  no retries on this head.
- Clean exact-B archive, one clean build (`build-022c.sh`, run
  dir `clean-build-022c`, fail-closed no-overwrite guards,
  driver pid 2562019 birth 381616409, uid 1001, umask 077,
  driver source_sha256
  `68d1b63216116970f1e61eb816cd512d955f07b5b85a228b8a0ced3f6695aa8c`
  (post-hoc correction recorded in the run dir for the same
  relative-`$0` reason)): git archive of B (38,860,800 bytes,
  954 files), extract and `uv build` exit=0 with BOTH artifacts
  byte-identical to the manifest (wheel
  `90b022004df33d47dd3e6410997a80a157b5c6820a627d2c6f7a229284ede3a0`,
  4,459,172 bytes, 89 entries; sdist
  `b3e9987544ce2c24990cf6e41ffc10ae59bcd835cf7928cab89d68947bcc0847`,
  6,167,111 bytes, 314 entries); fresh NONEDITABLE install of the
  clean-built wheel into a venv created by the EXPLICIT Python
  3.12 interpreter `/home/janezp/.local/bin/python3.12` (3.12.15)
  exit=0 with import probe (version 0.1.0, module resolved
  inside the disposable venv only, probe records interpreter
  `3.12.15 (main, Oct  9 2026, 15:22:32) [Clang 22.1.3 ]`,
  console entry point present).
- Full clean-archive BOTH artifact proof: ALL PROOF
  ASSERTIONS PASSED (helper exit 0, captured after gate cmd08
  rebuilt the repo `dist/`; no rebuild of the frozen
  candidate): the FULL clean-archive path set — 954 files —
  byte-identical to Git B; the 316 manifest source inputs
  byte-identical to the ORIGINAL Git A input map, to Git B
  and to the clean extracted tree; B verified manifest-only
  (sole parent A; exactly `packaging/dev_provenance_manifest.
  json` changed); every sdist entry (314 total)
  allowlisted-generated (exactly one, PKG-INFO `633064e6…`
  22,762 bytes) or byte-identical to its Git B blob (313
  verified); every wheel runtime entry (83 of 89)
  byte-identical to its Git B src/ blob; wheel RECORD (88
  unique rows) exactly covers the wheel entry set with
  per-entry sha256 and size; sdist PKG-INFO bytes equal wheel
  METADATA bytes; wheel entry_points exactly equal Git B
  pyproject `[project.scripts]` (`slaif-local-coding =
  slaif_local_coding.cli:main`); dist-info LICENSE/NOTICE
  byte-identical to Git B; repo gate `dist/` artifacts
  byte-identical to the clean artifacts; fresh noneditable
  install (exit 0) imports the module from the disposable
  venv only under the explicit Python 3.12 interpreter
  `3.12.15 (main, Oct  9 2026, 15:22:32) [Clang 22.1.3 ]`
  with the console entry point present.
- Live model inference: NOT RUN (protected Qwen/18020 fixture
  untouched; no dev service started). Actual Codex
  qualification: NOT RUN. No registry publication, deployment,
  benchmark or cutover. No merge, no auto-merge.

## Live model/service evidence
- NOT RUN. The protected Qwen/18020 service, profiles, launch/
  systemd, keys and network state were not touched; no bounded
  live call was made this round; the protected fixture is
  unchanged.

## Local setup/dependencies
- Repo-local uv frozen environment (Python 3.12.15) for the
  gate; `/home/janezp/.local/bin/python3.12` (3.12.15) for the
  explicit fresh noneditable install venv; no new dependencies;
  no sudo; no durable configuration change.

## Documentation
- Updated in this round (same PR): `ARCHITECTURE-for-agents.md`
  (the new 022-c compact block at its earned scope — active on
  opted-in v1 routes at its bounded fake-upstream application
  scope, PENDING strategic review, 023-024 NOT RUN — plus the
  021-paragraph tail, the 022-b block tail and the two
  objective-022 boundary lines); its byte-identical mirrors
  (`oap/strategic-instructions/ARCHITECTURE-for-agents.md` in
  the repo; the strategic-home mirror synced to the same bytes);
  `ARCHITECTURE.md` (delivery-status paragraph, the section
  heading, the planned/implemented statement, both spots);
  `docs/ADAPTER-CONFIGURATION.md` (the v1 runtime status, the
  `marker_key_env` field, the TOML excerpt, the component
  status); `SECURITY.md` (the v1 store active scope from 022-c
  and the marker-key protected-reference law); `docs/CACHE-
  REWORK-LEDGER.md` (the 022 row scoped to evidence actually
  run). No new planning or audit documents.

## Safety/scope confirmations
- Unrelated files: none. The branch diff from the 022-b report-
  only head `8bd38c5…` to B is exactly the 16 source/doc paths
  listed above plus the manifest at B, plus the two activated
  transcript paths committed unchanged from the strategic
  authoring (`oap/active` `022-b`→`022-c` and the new
  `oap/orders/022-c-cache-application-transaction.md`); cmd15
  `git diff --check 144af0bd… HEAD` clean.
- Secrets/raw content: none committed, printed or reported
  (evidence uses hashes, counts, command names and statuses
  only; synthetic session and marker key material stays inside
  the test modules and environment references).
- Protected 18020/Qwen/Codex fixture changed: NO.
- Required tests skipped/not run: live inference and actual
  Codex are ordered NOT RUN; nothing required was skipped.
- Scope deviation: none; the legacy profile and gateway
  contract are unchanged; the v1 activation is the explicit
  opt-in configuration surface only.
- Extra objective PR: NO. Coding merge: NO.
- Active/order edited: NO (committed bytes verified unchanged
  from the strategic authoring).
- Report commit report-only: yes (the SELF commit).

## Known limitations/blockers
- The 022-c qualification is BOUNDED to the fake-upstream
  application scope: synthetic identity and fixture sources, a
  bounded fake upstream for both the main forward and the direct
  tool-free compiler channel; no actual-model, live-service,
  genuine-Codex, deployment, registry or benchmark evidence is
  earned. The 023 expanded adversarial/lifecycle/telemetry
  matrix and the 024 actual-model/genuine-Codex qualification
  and immutable handoff remain mandatory (NOT RUN).
- The two driver startup records carry an empty `source_sha256`
  field because both drivers were launched with a relative `$0`
  and the hash step ran after the driver `cd` into the repo; the
  exact driver file hashes are recorded in the run dirs as
  post-hoc corrections (the 022-b gate driver was invoked by
  absolute path and captured the hash directly).
- This report is a claim until strategic review; no acceptance
  or merge is claimed.

## Recommended strategic follow-up
Factual only: strategic review of 022-c at its bounded
application-transaction scope; objectives 023-024 remain the
mandatory unearned v1 stages (the 023 expanded
adversarial/lifecycle/telemetry matrix; the 024 actual-
model/genuine-Codex qualification and immutable handoff).

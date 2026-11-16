# OAP Coding-Agent Report — 019-b

## Work order
- Identifier: 019-b (bounded async single-flight and attempt ownership)
- Order path: `oap/orders/019-b-bounded-singleflight.md` (SHA256
  `18b22cb7260fbfb86a7a5aabfdd902c104d5c0a2d7764a16795004b61c8dbf1a`)
- Numeric objective: 019 (RAM working state)
- PR mode: AMENDED_EXISTING_PR — PR27 `oap/019-cache-ram-state`
  (no new PR; no merge; no auto-merge; no next-ID choice by coding)

## Status
COMPLETE at the order's bounded INERT single-flight work-plane scope.
This is a claim, not acceptance; the slice is PENDING strategic review.

## Executive summary
Implemented, tested and documented the second 019 slice: the bounded
INERT async same-full-key single-flight and attempt-ownership work
plane (`cache-ram-work/v1`) over the ACCEPTED 019-a RAM owner/store
foundation and the ACTUAL accepted 018-p/018-t records, using an
injected bounded async work seam that proves prepared-work
orchestration only. Delivered the ratified claim/join/terminal
NO-RETRY attempt policy, the cancellation law, the closed
fenced-owner -> epoch -> current-key -> capacity publication fences,
conservative measured occupancy plus closed fixed reservations under
the SAME 019-a process/session ceilings, and the composed async
teardown (store plus work released in ONE critical section; the
synchronous store teardown fenced `work_in_flight` while work is
live). All 018/019-a public law, defaults and refusal vocabulary stay
intact; the 019-a work-disabled default behavior is unchanged. The
slice is inert: not active in the adapter request path, no v1
runtime, no live tests. Verified at the frozen manifest-only B: the
required 15-command full gate (ALL 15 actual exits 0; full pytest
6609 passed / 28 skipped / 16 warnings / 839.02s), ONE clean Git-B
archive building BOTH artifacts with the strict proof PASSED, and all
TEN exact-B GitHub checks SUCCESS.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #27 `https://github.com/ulfe-lmi/slaif-local-coding/pull/27`,
  state OPEN, no auto-merge
- Base: `main` `c5eb299df822875988867bf34d58de239e82657e`
- Starting remote SHA (round start):
  `845e9e763446d47c53e0695d84df7574d517536a` (the immutable 019-a
  report SELF; all TEN exact SELF checks SUCCESS there)
- Implementation head SHA: 837d10ce81332ce27db5fcefa343ab3596b66a6c
- Report publication commit: SELF
- Implementation commits pushed before report: source A
  `4240033b12355e5997f0d7485804f43a7726ff9a` (16 files,
  +4217/−49) and manifest-only B `837d10ce81332ce27db5fcefa343ab3596b66a6c`
  (sole parent A; `packaging/dev_provenance_manifest.json` only;
  285 inputs)
- New PR this round: no. Amended existing: yes (PR27). Merge
  performed: NO.
- PR title/body completed via structured PATCH before this report;
  server body verified byte-equal to the local body file
  (6863 bytes, SHA256
  `c485179a8141ee5ee2a2af662fd44e776ab5d0df1538f1715a617d02ff02051c`).

## Changes and files
At source A (parent of B):
- NEW `src/slaif_local_coding/constitution/bundles/ram_work.py`
  (1169 lines): opt-in `RamWorkCoordinator` — ONE process-wide active
  leader (closed constant `RAM_WORK_ACTIVE_LEADERS = 1`), bounded
  pending distinct-key queue and per-key waiters, claim/join in ONE
  short registry critical section (pure memory; await outside the
  lock), task owned independently of the first waiter, cancellation
  law, publication fences in closed order, staged-container rollback
  with exact charge restoration, composed async teardown,
  `work_in_flight` fence on the 019-a synchronous teardown path.
- NEW `src/slaif_local_coding/constitution/bundles/ram_work_models.py`
  (465 lines): `RamWorkBounds` (raw non-bool fences before coercion;
  defaults 32/8/1048576/30.0; hard 4096/1024/67108864/600.0),
  `RamWorkRequestResult`/`RamWorkTeardownResult`, `RamWorkAttempt`
  terminal records, closed `RAM_WORK_HTTP_STATUS` mapping
  (503/422/409), fixed `RamWorkInputError`.
- COHESIVE 019-a changes (sharing atomic capacity/lifecycle
  control): `ram_state.py` (+130/−…) gains the `work_bounds`
  constructor parameter, the work plane's atomic process/session
  accounting into the SAME ceilings, the `work_in_flight` fence on
  synchronous teardown and the composed release; `ram_state_models.py`
  small supporting changes. 019-a default (work-disabled) behavior
  unchanged.
- NEW `tests/test_bundle_ram_work.py` (2082 lines; 51 scoped cases,
  27 top-level functions, several parameterized).
- NEW `docs/CACHE-RAM-WORK-CONTRACT.md` (256 lines;
  `cache-ram-work/v1` / `ram-work-policy/v1`).
- `docs/CACHE-RAM-STATE-CONTRACT.md`: 019-a PENDING -> ACCEPTED
  (decision cite), `work_bounds` signature, work-plane interplay note.
- `ARCHITECTURE-for-agents.md` + `oap/strategic-instructions/ARCHITECTURE-for-agents.md`
  and the supervision mirror: all THREE compact mirrors byte-identical
  (SHA256 `411d12cd944f33399c776896c98a6af818cef041ee1ffadb8428d4c92d1e3406`;
  supervision mirror in place, inode 10638621, mode 0600, UID 1001);
  `ARCHITECTURE.md` (delivery status + current-scope paragraph);
  `TESTING.md` (019 line); `docs/ADAPTER-CONFIGURATION.md` and
  `docs/CACHE-IMPLEMENTATION-PLAN.md` (component/slice status,
  application settings/planned activation unchanged);
  `docs/CACHE-REWORK-LEDGER.md` (019 row).
- Transcript: exact activated `oap/orders/019-b-bounded-singleflight.md`
  and `oap/active` (019-b) committed unchanged.
- B: development provenance manifest (285 inputs) only.

## Acceptance evidence
Criterion mapping (order "Required focused evidence"; all through
genuine P bootstrap/issuance/observations -> actual T -> registered
019-a owner over the ACTUAL records; the injected seam is synthetic):
1. Simultaneous identical misses — ONE leader, shared successful
   immutable payload; later same-key HIT with zero new invocation:
   `test_a_concurrent_identical_miss_one_leader_shared_hit`.
2. Cancellation boundaries — first waiter cancelled with another
   surviving (`test_b_cancelled_follower_surviving_waiters_complete`),
   claimant cancelled with follower completing
   (`test_b2_claimant_cancelled_follower_completes`), all waiters gone
   after dispatch (`test_g_all_waiters_departed_after_dispatch`),
   queued claimed-but-not-dispatched cancellation
   (`test_h_queued_claim_all_waiters_departed_before_dispatch`),
   unstarted dispatch task finalizes once with zero invocations
   (`test_i_unstarted_dispatch_tasks_finalize_zero_invocations`),
   pre-claim capacity refusals with zero invocation and no attempt
   (`test_c_pending_keys_over_bound_pre_claim_refusal`,
   `test_d_waiters_over_bound_refused_join_exact_preservation`).
3. Terminal outcomes — exception/timeout/invalid/truncated/over-bound
   seam results, later same-failed-key re-service without invocation,
   unrelated key/session progress, terminal metadata never a hit:
   `test_j1_exception_and_timeout_terminals`,
   `test_j2_output_shape_terminals`,
   `test_j3_terminal_never_hit_unrelated_key_progresses`.
4. Supersession/revert/replay — stale completion refused
   (`test_n1_stale_completion_refused`); valid A1 payload survives A2
   and a genuine compatible A1 revert reuses it WITHOUT a third
   invocation (`test_n2_genuine_revert_reuses_retained_payload`);
   FAILED A1 -> A2 -> genuine A1 revert still terminal
   (`test_n3_failed_revert_still_terminal`); replay cannot reactivate
   (asserted inside `test_n2`); unchanged A HIT after genuinely
   unrelated B in the SAME owner
   (`test_q_unrelated_b_preserves_unchanged_a_hit`).
5. Fences and teardown — foreign namespace/epoch bindings
   (`test_o1_foreign_namespace_and_epoch_fences`); other owners
   survive teardown (`test_o2_other_owner_survives_teardown`); async
   teardown during active/queued/shared work with bounded truthful
   outcomes and exact `freed_bytes` (`test_k_async_teardown_active_and_queued`,
   `test_k2_async_teardown_before_any_work`); synchronous store
   teardown composition with an idle plane and the `owner_absent`
   refusal (`test_l_sync_teardown_idle_plane_and_owner_absent`).
6. Exact/first-over limits and combined occupancy — pending keys,
   waiters per key, output bytes at-limit and first-over
   (`test_c`, `test_d`, `test_j2`); session capacity on first claim
   retains nothing (`test_e_session_capacity_refused_first_claim_retains_nothing`);
   process capacity exact-at-limit and one-over
   (`test_m_process_capacity_exact_and_one_over`); dispatch-time
   capacity crossing with exact preservation
   (`test_m2_dispatch_capacity_crossing`); terminal-reservation upper
   bound on the pinned toolchain
   (`test_f3_terminal_reservation_upper_bound`); bounds model and
   registry integration incl. work-disabled default unchanged
   (`test_f_ram_work_bounds_model`, `test_f2_work_registry_integration`).
7. RAM-only operation — repeated hits with mechanically denied
   filesystem content IO after setup
   (`test_p_hits_with_denied_host_io`).

## Verification
All commands run at the frozen commits (repo venv, `uv` locked/frozen;
gate driver 0700 before execution with actual
PID 3354211 / birth 340568298 / PPID 598258 / UID 1001 / umask 0077 /
driver-source SHA256
`85f52bef03d2d60bb0f2d199df5b66dbecae22aecfd874340c6e00e99d301568` /
aware-UTC startup 2026-11-16T01:31:04.980791Z; capture parent umask
077; the full-pytest child ran under the verified nonroot umask 022):
- `uv lock --check`: PASSED (gate c01, exit 0)
- `uv sync --frozen --extra dev`: PASSED (gate c02, exit 0)
- `uv run --frozen ruff check .`: PASSED (gate c03, exit 0)
- `uv run --frozen ruff format --check .`: PASSED (gate c04, exit 0)
- `uv run --frozen mypy src tests`: PASSED (gate c05, exit 0)
- `uv run --frozen python scripts/docs_consistency_check.py`: PASSED
  (gate c06, exit 0)
- `uv run --frozen pytest -q` (umask 022 child): PASSED —
  6609 passed, 28 skipped, 16 warnings in 839.02s (gate c07, exit 0)
- `uv build`: PASSED (gate c08, exit 0)
- `uv run --frozen python scripts/artifact_policy_check.py --dist dist --inspect`:
  PASSED, `ok: true`, no violations (gate c09)
- `uv run --frozen python scripts/artifact_policy_check.py --dist dist --install-smoke`:
  PASSED, fresh non-editable install, `ok: true` (gate c10)
- `uv run --frozen python --version`: PASSED (gate c11, exit 0)
- `uv run --frozen python -m compileall -q src tests oap/bin scripts`:
  PASSED (gate c12, exit 0)
- `uv run --frozen python scripts/dev_provenance_manifest.py --verify --dist dist`:
  PASSED — `development provenance OK: state=development
  head=837d10ce8133` (gate c13)
- `bash -n` over `oap/bin/*.sh packaging/*.sh`: PASSED (gate c14)
- `git diff --check c5eb299df822875988867bf34d58de239e82657e HEAD`:
  PASSED (gate c15, exit 0)
- Focused suites (scoped run before the gate, preserved capture
  `pytest-w19.out`): `pytest -q tests/test_bundle_ram_work.py
  tests/test_bundle_ram_state.py` — 101 passed in 20.27s (51 work +
  50 state cases). Earlier scoped reds (w1..w18) are preserved as
  development diagnostics, not final evidence.
- Clean-B artifact proof (ONE fresh `git archive` of B, 908 files,
  extracted and built in a clean tree; helper 0700, fresh exclusive
  paths, startup recorded): strict A/B/input-map/archive/sdist/wheel/
  RECORD/metadata/licenses/entrypoint/repo-dist assertions — ALL
  PASSED. Counts: 285 manifest inputs verified against git A, git B
  and the clean tree; B sole-parent manifest-only verified; sdist 283
  entries (282 source + PKG-INFO); wheel 71 entries (65 runtime + 6
  dist-info) with 70 RECORD rows verified including the empty self
  digest/size row. Deterministic digests reproduced: wheel 667961
  bytes SHA256 `4c26f825366ec3337244e039e46bcd3e0264f02a1be8202308e30e394b9d9945`;
  sdist 2290775 bytes SHA256 `90c4073be5312e96eaa815a23c3a53198853fcb8778da5d8afecb193ba664321`.

## Live model/service evidence
NOT RUN — the order specifies no live tests in this round; no live
model, compiler, tokenizer, client or Codex call was made; the
protected fixture is unchanged.

## GitHub CI / required checks
At implementation head B
(`837d10ce81332ce27db5fcefa343ab3596b66a6c`), all TEN required exact-B
checks present and SUCCESS as of drafting:
- `test`: SUCCESS
- `Analyze (actions)`: SUCCESS
- `Analyze (python)`: SUCCESS
- `CodeQL`: SUCCESS
- `gateway-contract`: SUCCESS
- `docker`: SUCCESS
- `docker-published`: SUCCESS
- `operator-session`: SUCCESS
- `cache-native-containment`: SUCCESS
- `cache-native-fixture`: SUCCESS
All required green at drafting: yes. Report-head checks may be
pending; strategy verifies.

## Local setup/dependencies
Repo-owned venv via the pinned uv toolchain (`uv lock --check` /
`uv sync --frozen --extra dev`); no new dependencies; no protected
service, port or fixture touched; no sudo used this round; no
persistent host configuration changed. All scratch/evidence under
`/home/janezp/codex-supervision/slaif-local-coding/work-artifacts/oap-019b-work`
(0700; captures 0600; helpers 0700 before execution).

## Documentation
Updated in the same PR: NEW `docs/CACHE-RAM-WORK-CONTRACT.md`
(versioned contract with the ratified attempt policy, cancellation
law, publication fences, occupancy/reservation recipe and inert
boundary); `docs/CACHE-RAM-STATE-CONTRACT.md` (accepted status,
`work_bounds` surface, work-plane interplay); both architecture maps
with all THREE compact mirrors byte-identical (supervision mirror
preserved in place); `ARCHITECTURE.md`; `TESTING.md`;
`docs/ADAPTER-CONFIGURATION.md`; `docs/CACHE-IMPLEMENTATION-PLAN.md`;
`docs/CACHE-REWORK-LEDGER.md`. No new planning/audit document; no
historical-chronicle restatement; no v1 activation or readiness claim.

## Safety/scope confirmations
- Unrelated files: only in-scope paths touched; the A->B diff is the
  single manifest file; working tree clean at B.
- Secrets/raw content: none in source, tests, docs, evidence or this
  report; the injected seam and fixtures are synthetic.
- Production/protected resources: protected 18020/Qwen/Codex fixture
  changed: NO; no profile/key/auth/network/firewall/VPN/binding
  mutation; no release/tag/RC/registry/deploy/cutover/benchmark.
- Required tests skipped/not run: 28 skips in the full gate are
  count-only (the standard unavailable-fixture/live skips; not an
  independently established identical skip set); live/native/
  compiler/tokenizer/recovery/runtime/actual-async qualification
  remain NOT RUN as required for an inert slice.
- Scope deviation: none known; the 019-a store/models cohesive
  changes are the order-authorized atomic capacity/lifecycle sharing.
- Extra objective PR: NO. Coding merge: NO.
- Active/order edited: NO (exact strategic bytes committed unchanged;
  `oap/active` = 019-b, order SHA as above, both verified against the
  activated bytes).
- Report commit report-only: verified after push (single changed
  path, exact bytes, parent B).

## Known limitations/blockers
- Inert scope: the seam is synthetic — prepared-work orchestration
  only; no compiler/tokenizer semantic correctness, no wire/HTTP
  behavior, no recovery, no v1 runtime; the slice is never active in
  the adapter request path. Whole-019 pressure/source-scale/lifecycle
  closure remains a following same-PR round; 020-024 remain mandatory.
- No total-RSS promise: occupancy is a conservative measured plus
  fixed-reservation committed-occupancy measure.
- Early full-suite diagnostic preserved, not final: a full run
  started while the working source was still mutable
  (`pytest-full-w16.out`) recorded 2 failed / 6605 passed / 28
  skipped / 16 warnings / 837.68s / exit 1 in
  `tests/test_dev_provenance.py::test_real_development_state_consistent`
  and
  `tests/test_source_input_binding.py::test_real_repo_source_inputs_bound_to_committed_source`
  (source-input/manifest binding under the then-unfrozen manifest).
  The ordered final gate at the frozen B (above) is the authoritative
  full proof, where those suites pass.
- 019-a process qualifications remain preserved per
  `S/reviews/019-a-decision.md` (including its measurement-wording,
  interrupted-gate, helper-mode, reader-startup and publication-order
  qualifications); they apply to the 019-a round and are not
  repaired retroactively here.
- No universality claims: evidence is scoped to the named inert
  mechanisms, the pinned toolchain and the synthetic fixtures.

## Recommended strategic review focus
Factual only; strategy decides: review the 019-b work plane at its
bounded inert single-flight scope (attempt policy, cancellation law,
publication fences, same-ceilings accounting, composed teardown);
then activate the following same-PR round for whole-019
pressure/source-scale/lifecycle closure, followed by 020-024 as the
standing plan.

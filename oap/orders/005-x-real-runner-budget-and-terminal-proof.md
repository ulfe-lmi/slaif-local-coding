# OAP Work Order — 005-x

## Objective

Close the three proven 005-w Local harness gaps: semantic terminal evidence,
per-dispatch budget enforcement, and testing the actual protected-mode runner
with synthetic dependencies. Preserve the existing observer/app-factory design.
Use fake-only execution; no protected credentials, Qwen requests or installation.
Finish with genuine shared-runner conformance and the full fake C1–C5/D matrix.

## Exact GitHub state

- Repository ulfe-lmi/slaif-local-coding; Objective005 round005-x.
- AMEND_EXISTING_PR; NO NEW PR. PR7:
  https://github.com/ulfe-lmi/slaif-local-coding/pull/7
- Base/head main / oap/005-gateway-ingress-integration.
- Main `570bd2b24ad4b041a07e0320d5ed44bc73e99ad5`.
- Required start report `5512a1e7443727aea1b25b75c0a7bb6078b14d6a`;
  literal implementation parent `3bdbc89f330b9c612c94b160703e8c8423714e13`;
  report-only path
  `oap/reports/005-w-protected-mode-projection-and-failure-retention.md`.
- PR open/non-draft/CLEAN; final test SUCCESS (34402167044/102636426731);
  clean checkout; 005-x unused at strategic preflight.
- Gateway executable `50dcc3b85d614eb1d0c6196595bf22ef5779f846`;
  merged main `d142fd7f04c46fac3469b9b9bba1bd2068aabad8`;
  immutable report `ad1c556a539130c08dc1063b3e9a25a0af2e5a85`;
  app tree `c0204deaff3cfd055a25f29a7f5d8d3c5e161d57`. No pin changes.

Reconcile current remote, checkout, reports and required checks before edits.
Only exact order/active are intentional initial differences after activation.
Preserve all prior orders/reports including 005-q and 005-r/v/w. Do not rerun
historical rounds, reinterpret missing protected evidence, or fabricate counts.

## Scope and host law

Only existing repository-only rehearsal, acceptance/observer helpers, tests,
current docs, order/active/report may change. No src/, Gateway, versions,
dependencies/lockfiles, client binary, new harness architecture or extra relay.
Actual Gateway and Local modules remain unchanged and authoritative.

Host hinton1: vision Qwen PID23961, start Sun2026-09-06 18:57:26 CEST, zero
restarts, port18020, qwen3.8-27b/context100000/one sequence/image; text inactive;
18021/18030/18031 free; seven unrelated Qwen worktree entries. Existing coding
profile and active agent profiles remain unchanged.

Only read-only unit/PID/start/restart/listener/unauthenticated health facts are
allowed. No protected environment/credential/raw-log/config access, models,
compiler/inference/vision/diagnostic requests, service/port18020 mutation,
Qwen/model/checkpoint/patch/venv/unit/launch/GPU/key changes, network/firewall/
VPN changes, active-profile edits, second model or installed cutover.

## A. Truthful semantic terminal evidence

Independent 005-w reproduction supplied inference_attempted=completed=1,
inference_terminal_valid_count=0, ready=false, failure=stream_validation_invalid.
RunAccumulator.safe_dict nevertheless emitted terminal_valid. Repair this:

- retain actual terminal-valid counters/per-ordinal observations separately
  from consumed/completed/closed state;
- derive terminal classes only from semantic validator results and expected
  terminal relationships; attempted==completed cannot establish validity;
- preserve UNKNOWN for absent observations and invalid/incomplete for rejected
  or truncated streams; do not convert unknown to zero or success;
- accumulate exact counts correctly across observer lifetimes without double
  counting or overwriting earlier known failures;
- retain original first failure plus bounded secondary projection/cleanup
  errors and safe counters even if finalization itself fails.

Add regressions for valid, invalid-but-consumed, truncated, absent observation,
zero-dispatch, cancellation, and multiple lifetimes. Reproduce the exact 005-w
counterexample and require non-valid output. Preserve UNKNOWN 005-r/v facts.

## B. Connect budgets to actual dispatch

005-w calls BudgetController.admit at nine broad operation entries, admitting
both Codex turns before a subprocess and both vision turns before a second.
It does not check each ensuing HTTPX dispatch; compiler/repeated requests can
bypass admission. BudgetController.observe_event is unused by the real runner.

Integrate the same run-owned controller into the direct observer admission
path, immediately before delegate.handle_async_request. It must cover compiler,
inference and other request classes with distinct exact counters, phase/ordinal
attribution, deadline, aggregate bound, and first-failure latch. Every dispatch
must either possess current permitted admission or fail with zero delegate calls.
Do not pre-admit a group and assume the client makes the expected request count.

Keep all current maxima: 900-second run bound, existing phase/operation attempt
maxima, 64-observation ceiling, 16-KiB event and 128-KiB stream bounds, existing
output/timeout values and single-phase concurrency. Do not reset a run-wide
limit when the candidate lifetime changes. Distinguish operation attempts from
individual API calls; document the exact existing authorized mapping for every
actual request. If an operation cannot be mapped without increasing scope,
report it before traffic rather than inventing a larger budget.

Connect byte enforcement to actual incremental stream processing and concurrency
to active request/stream lifetime. Check the deadline before every request and
between streamed events/chunks, close/cancel on exhaustion and preserve evidence.
Cleanup remains available after the run is latched failed. Tests use lower
injected limits and fake time, while attesting unchanged default maxima.

Required transport-level negatives: an extra compiler call, extra client turn,
deadline expiry between turns and during streaming, aggregate exhaustion across
candidate lifetimes, event/stream overflow, first failure followed by another
call, and overlapping/queued requests. Assert exact delegate call counts, not
only controller return values. Preserve streaming/cancellation and closure tests.

## C. Exercise the actual shared runner

run_protected_mode_conformance currently supplies literal ready/direct/terminal
defaults, never calls a credential hook, and returns PASSED with no runtime
hooks. This separate loop does not exercise _run_direct_composed_rehearsal_impl.
Replace that conformance claim with tests invoking the actual shared runner
and its protected mode selection/branches, using explicit synthetic dependency
injection. Remove or clearly retire the unused simulation as acceptance evidence.

Inject only the external boundaries: host preflight, credential source, provider
target, bounded clock/dispatch hooks and failure points. Require explicit hooks;
missing dependencies cannot default to success. Protect synthetic tests from
real endpoints and /proc/credential reads with fail-on-access guards. Do not
mock the orchestration, budget controller, observer, projector, accumulator,
cleanup controller or final serialization into returning success.

Use actual Gateway/Local with strict fake upstream for the healthy shared path,
and execute the actual protected failure/finalization path for injected failures.
Record mode, branch/phase coverage, exact side-effect counters, first failure,
all 29 protected-selected result dispositions, and evidence that no real
credential/Qwen access occurred. A successful synthetic run must not be labelled
real protected acceptance. No fake-server-only oracle may replace the protected
direct-observer predicate. Test missing C5.4 mapping before any side effects,
observer readiness loss after known dispatches, then projection exception and
cleanup exception: original known counts/failure must survive serialization.

## D. Qualification and publication

Run focused A–C tests and frozen full pytest, Ruff/format, mypy src tests,
compileall, shell syntax, build/wheel boundary, diff/pin/privacy scans and
required final Local CI. Run the existing actual-Codex0.149 complete fake
C1–C5/D matrix against Gateway50dcc3b... and actual Local/observer. Keep binary
SHA-256 bbc3341e44c9ead340ed9570c17be936e37870f570751a941699ffd04d672827.
Require every selected fake row/projection PASS, exact count/provenance,
same-session image/crop, governance/rehydration, identity/replay/tamper/isolation,
tool/HMAC/accounting, privacy/no-bypass/cleanup and fake rollback/refusal. Record
the separate actual-runner synthetic protected conformance cases and outcomes.

No declared COMPLETE until each A–D requirement has measured evidence. If only
part implemented, report PARTIAL honestly; do not manufacture PASS from default
booleans or NOT RUN row serialization. Update docs to actual coverage. Keep
REAL-E2E ACCEPTED, CUTOVER ACCEPTED, MERGED and RELEASE-READY=no.

Coding owns routine setup/support edits/tests/Git publication/evidence; no
human/strategy terminal labor. Use only existing task-owned PostgreSQL16
loopback/tmpfs/--rm, bounded Docker operations, private synthetic client/cache
state. No host daemon/package changes or privileged networking. Cleanup exact
validated task resources, preserve .venv/unrelated/Qwen state. No raw prompts,
source, images, model/SSE/tool data, credentials, IDs/signatures/nonces/private
endpoints/arbitrary errors in artifacts. Verify unchanged protected host facts.

Amend PR7 only. Push exact order/active and intended implementation, check CI,
record literal implementation SHA, then atomically publish exactly
`oap/reports/005-x-real-runner-budget-and-terminal-proof.md` with Implementation
head SHA and Report publication commit: SELF. SELF report-only, parent exactly
literal implementation SHA; verify remote head/parent/path/bytes before response
FIFO OK. Include actual A–D tests/results, identities/budgets/counters/cleanup,
no-protected proof, UNKNOWN facts and limitations. Coding never merges or
creates a new PR. Return for independent strategic review.

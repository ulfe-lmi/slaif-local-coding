# OAP Work Order — 005-y

## Objective

Close the specific 005-x acceptance gaps: require real operation permits for
each transport dispatch, distinguish network chunks from SSE frames in budget
checks, and exercise the actual protected-mode runner beyond preflight using
synthetic dependencies. Preserve the existing harness architecture, limits and
qualified observer. No protected credentials, Qwen requests or installation.

## Exact state and publication mode

- Local repository ulfe-lmi/slaif-local-coding; Objective005 round005-y.
- AMEND_EXISTING_PR; NO NEW PR. Existing PR7:
  https://github.com/ulfe-lmi/slaif-local-coding/pull/7
- Base/head main / oap/005-gateway-ingress-integration.
- Main `570bd2b24ad4b041a07e0320d5ed44bc73e99ad5`.
- Required start report `494bfc2992d1da0e6917e95e7e4765f378b2bb82`;
  literal implementation parent `ae5e131ba30664ce503cc903d30a104773e6b331`;
  report path `oap/reports/005-x-real-runner-budget-and-terminal-proof.md`.
- PR open/non-draft/CLEAN; report-only topology verified; final test SUCCESS
  (34407967618/102655398166); checkout clean; 005-y unused.
- Gateway execute `50dcc3b85d614eb1d0c6196595bf22ef5779f846`, merged main
  `d142fd7f04c46fac3469b9b9bba1bd2068aabad8`, immutable report
  `ad1c556a539130c08dc1063b3e9a25a0af2e5a85`, app tree
  `c0204deaff3cfd055a25f29a7f5d8d3c5e161d57`. Keep all pins unchanged.

Verify GitHub, exact source/import identity and required checks before edits.
After activation only this order and active=005-y are expected differences.
Preserve all prior orders/reports, especially 005-q and UNKNOWN 005-r/v facts.
Do not rerun historical rounds or turn missing evidence into inferred success.

## Scope and protected law

Allowed changes: existing repository-only rehearsal, budget/observer helpers,
their tests and current docs, exact order/active/report. No src/, Gateway,
version/dependency/lockfile/binary, new subsystem/relay, or installed service.

Host hinton1: vision Qwen PID23961, start Sun2026-09-06 18:57:26 CEST, zero
restarts, port18020, qwen3.8-27b/context100000/one sequence/image; text inactive;
18021/18030/18031 free; seven unrelated Qwen changes. OAP profiles unchanged.
Only read-only unit/PID/start/restart/listener and unauthenticated health facts
allowed. No protected environment/credential/log/config read, models/compiler/
inference/vision/diagnostic request, restart, instrumentation, port18020/Qwen/
checkpoint/patch/venv/unit/launch/GPU/key/network/firewall/VPN/profile mutation.
No second model. Synthetic tests must fail if any real protected boundary is
accessed. Preserve .venv and unrelated work.

## A. Operation permits at the transport boundary

Independent 005-x reproduction: admit_dispatch('inference') returns true without
any operation admission. After admitting codex_turn_1 with maximum1 and setting
its context, two sequential inference dispatches both return true. A global
64 ceiling does not enforce the declared per-operation permission.

Make dispatch admission consume explicit current operation/phase permission
immediately before delegation. Reject missing/unassigned, exhausted, expired,
wrong-kind, wrong-phase or already-consumed permission with zero delegate calls.
Do not authorize all further calls by pre-admitting an entire subprocess.

Before execution, encode and document the finite existing run-plan mapping of
logical operation attempts to actual inference/compiler/health/model/other
requests. Macro attempts and API requests are different counters. Each public
turn must have its own bounded dispatch slot; compiler retries use only the
already-authorized compiler limits and count separately. Setup/readiness and
negative admission tests must have explicit scoped allowances, never an
unassigned inference default. A repeated/extra request cannot take another
phase's permission or bypass an exhausted per-turn allowance merely because
the global run cap has room.

Keep existing numerical maxima: 900-second wall limit, nine logical operations
maximum1/zero retries, existing compiler/output bounds, 64 aggregate observations,
16-KiB per event, 128-KiB stream limit, single stream concurrency. No increases
or inferred authority. If the current plan cannot map a request within these
limits, report the exact unmapped request class before traffic.

Regression tests must reproduce both counterexamples through the observer and
count real delegate calls. Cover extra Codex turn, extra compiler retry,
inference before an operation begins, wrong phase/kind, phase transition,
expiry between turns, cross-lifetime reuse and queued requests after failure.
Check allowed sequences still execute and release resources correctly.

## B. Frame-aware versus chunk-aware enforcement

Independent 005-x reproduction: observe_event(18000) rejects while two calls
observe_event(9000) pass. The observer currently feeds HTTPX chunk length into
this event limit. Multiple legal SSE frames may arrive in one network chunk.

Apply cumulative bytes/deadline checks to actual received chunks and frame-byte
checks at the incremental parser's frame boundaries. Do not apply per-frame
limits to network chunks. Preserve every byte and existing numerical limits.
Do not buffer an entire stream. Same wire data must have the same acceptance
and failure facts whether split at every byte, LF/CRLF boundaries, or coalesced
into one chunk containing multiple individually legal frames whose combined
size exceeds16KiB. A genuinely oversized frame or stream must fail and prevent
later dispatch. Exercise the connected observer+controller with exact wire
bytes, not only standalone controller calls. Keep deadline/concurrency/close
and cancellation regressions.

## C. Actual protected-mode healthy and post-dispatch conformance

Current tests call run_actual_protected_mode_conformance only with missing
dependencies or failure_phase=preflight, then test the selector separately.
This does not exercise the different protected data flow after dispatch.
Do not claim fake-mode success covers those branches.

Use the existing ProtectedRuntimeHooks seam and shared runner. Execute with
provider_target=protected and explicit synthetic host, PID, credential source,
clock and provider target. The physical upstream must be a disposable fake
loopback endpoint; guard real /proc/credentials/18020/network access so any
accidental access fails the test. Use actual unchanged Gateway and Local modules,
the qualified direct observer, real budget controller, projector, accumulator
and cleanup code. Do not mock these into PASS or use literal success defaults.

Required distinct executions:

1. Healthy synthetic protected-mode path past preflight, candidate startup,
   actual network dispatch and terminal response. Record actual phase trace,
   exact compiler/inference counters, selected protected rows and source
   identities. Exercise every reachable protected path needed for the later
   real matrix. A missing actual predicate must be reported, not replaced by a
   fake-server-only fact. Evidence remains explicitly synthetic, with
   protected_acceptance=false even when its conformance tests pass.
2. Inject observer failure after a known actual dispatch, then ensure no later
   dispatch, complete safe result serialization and exact preserved counts.
3. After that primary failure inject projection failure and cleanup failure;
   preserve the original failure, mode, counts and bounded secondary classes.
4. Mapping/dependency failure before dispatch must serialize all selected
   dispositions and prove zero credential-hook/network calls.

Assert the shared implementation function is reached and candidate/dispatch
callbacks actually execute in cases1–3. Preflight-only NOT RUN rows cannot
satisfy them. No protected inference in 005-y. If healthy protected-mode
conformance reveals another Local predicate/runner defect, repair it within
these boundaries and qualify it synthetically before returning.

## D. Verification, docs, immutable report

Run focused A–C regressions, frozen full pytest/Ruff/format/mypy/compileall/
shell/build/wheel boundary/diff/pin/privacy checks and current required CI.
Run the complete existing actual-Codex0.149 fake C1–C5/D matrix after the
changes. Keep exact binary checksum
bbc3341e44c9ead340ed9570c17be936e37870f570751a941699ffd04d672827.
Require all37 fake rows/projections PASS, exact observer/provider counts,
same-session image/crop, governance/rehydration, signing/replay/tamper/isolation,
tool/HMAC/accounting/privacy/no-bypass/cleanup and fake refusal/rollback.
Report the separate full shared-runner synthetic protected tests with their
actual phase coverage and outcomes. Neither group replaces the other.

Document only measured guarantees. COMPLETE requires every A–D requirement;
otherwise use PARTIAL/FAILED with exact gap. Protected/cutover/merge/release
remain unaccepted. Preserve historical artifacts and unknown prior counts.

Coding owns routine setup/support/tests/Git publication/evidence. No human or
strategy terminal labor. Existing task-owned PostgreSQL16 loopback/tmpfs/--rm,
bounded Docker operations, synthetic private client/cache state only. No host
daemon/package/privileged-network changes. Cleanup exact task-owned targets;
preserve unrelated state. No raw prompts/source/images/SSE/tool/model content,
credentials/IDs/signatures/nonces/private endpoints/arbitrary errors in artifacts.
Verify unchanged protected service and absence of task listeners/resources.

Amend PR7 only. Push exact order/active plus intended implementation, inspect
required checks, record literal implementation SHA, then atomically publish
`oap/reports/005-y-operation-permits-and-protected-branch-conformance.md` with
Implementation head SHA and Report publication commit: SELF. Final commit only
that report, first parent exactly literal implementation SHA. Verify remote
head/parent/path/bytes before exact response FIFO OK. Include actual tests,
fake and synthetic-protected phase evidence, counters/budgets, identities,
cleanup, CI and limitations. No coding merge or new PR. Return for review.

# OAP Work Order — 005-w

## Objective and exact state

Repair the proven Local protected-mode projection/serialization defect from
005-v using fake-only execution. Make mode completeness, first-failure capture,
counter retention, cleanup and budget enforcement machine-checked prerequisites
before any future protected call. No protected retry in this round.

- Repository ulfe-lmi/slaif-local-coding, Objective005 round005-w.
- AMEND_EXISTING_PR, NO NEW PR; existing PR7:
  https://github.com/ulfe-lmi/slaif-local-coding/pull/7
- Base/head main / oap/005-gateway-ingress-integration.
- Main `570bd2b24ad4b041a07e0320d5ed44bc73e99ad5`.
- Start immutable report `10a73962eef93f9a848e80b940fa1f9242476ddd`;
  parent `0f083c32f57a49612bb0e52111f8f74e6e842b3a`;
  report `oap/reports/005-v-qualified-observer-protected-acceptance.md`.
- PR open/non-draft/CLEAN, report-only topology verified, final test SUCCESS
  (34397313559/102620098281), clean checkout; 005-w unused.
- Gateway executable pin `50dcc3b85d614eb1d0c6196595bf22ef5779f846`, merged
  main `d142fd7f04c46fac3469b9b9bba1bd2068aabad8`, immutable report
  `ad1c556a539130c08dc1063b3e9a25a0af2e5a85`, app tree
  `c0204deaff3cfd055a25f29a7f5d8d3c5e161d57`; preserve all pins and code.

Reconcile remote/checkout/checks before edits. Only this order/active may be
intentional initial differences. Preserve every historical order/report,
especially 005-q and the FAILED 005-v. Coding never merges or chooses next ID.

## Safety boundary

Host hinton1 vision Qwen active PID23961, start Sun2026-09-06 18:57:26 CEST,
zero restarts, port18020, model qwen3.8-27b/context100000/one sequence/image;
text inactive; candidate18021/18030/18031 free; seven unrelated Qwen changes.
Only read-only unit/PID/start/restart/listener and unauthenticated health facts
allowed. No protected key/environment/raw-log/config read, model/vision/compiler/
inference/diagnostic request, restart, instrumentation or protected mutation.
No Gateway, src/, dependencies/lockfiles/binary, active-profile, network/firewall/
VPN changes, relay, second model, installed cutover or new subsystem.

Use existing repository-only rehearsal, manifest, observer and their tests/docs.
The protected orchestration may run with injected synthetic preflight/credential
hooks and fake transport only; it must be physically unable to reach protected
endpoints or read real credentials in this round. Keep real protected mode
refused before those hooks. No fake result may be labelled real-E2E acceptance.

## A. Proven failure and complete mode coverage

Independent read-only reproduction on 005-v selects 29 protected obligations,
but projection_for searches FAKE_PROJECTION_TABLE, which lacks C5.4. A failed
protected result therefore raises KeyError(unknown_obligation_projection) on
C5.4 in finalization. Main then emits a fake-mode gate from {}, losing original
observer evidence. This secondary Local failure is proved; the original
protected readiness-loss cause and unrecorded counts remain UNKNOWN.

Reproduce this exact missing-mode projection regression without network. Add
the real protected-preservation projection and required observations; do not
remove C5.4 or convert it into a literal PASS. Select schema/projection/result
IDs by actual mode. Preflight must prove exact coverage/uniqueness/dependencies
for fake and protected sets before credentials, candidate readiness or dispatch.
Test missing/duplicate/unknown/reordered mappings and unavailable observations.
Missing coverage must emit a bounded preflight failure with zero side effects.

## B. Preserve primary evidence on every exit

Keep a bounded run accumulator with mode, tested candidate/pins, phase/ordinal,
first observed failure, exact attempted/dispatched/responded/completed compiler/
inference counts, observer failure/terminal classes, and cleanup outcome.
Capture snapshots while objects are still available, before destructive cleanup.
No raw streams/bodies/IDs/secrets or arbitrary exceptions in the accumulator.

Finalization must be total for success, partial progress, observer unready,
validation failure, timeout, cancellation, client/parser exception and cleanup
failure. A later projection/serialization/cleanup error must be recorded as a
secondary fixed class and never overwrite original mode, first failure or
counters. Unknown/missing observations stay UNKNOWN/NOT RUN, not zero/PASS.
Keep safe result emission possible without the failing projector; do not catch
KeyError by returning fabricated all-false or fake-mode evidence.

Test an injected first observer failure followed by the exact missing-C5.4
projection failure: the original failure and known exact fake dispatch count
must survive, later dispatch must be zero, cleanup must run and bounded output
must serialize. Test exceptions at each phase and finalization boundary, before
any request and after admitted requests, including failure to stop a task
resource. Test stdout/error output contains only the fixed safe schema.

## C. Executable budgets and protected-mode conformance without Qwen

Prove existing wall/request/event/output/concurrency budgets are enforced by
control flow, not merely declared constants or post-run summaries. Preserve
existing maxima; no increase. Connect pre-dispatch admission to the frozen
per-operation maxima and aggregate run limit. Use fake clock and counting
transport to prove exhaustion/deadline/first-failure prevent further admission,
including compiler calls and dependent phases. Tests may use lower injected
limits but must attest unchanged production-harness maxima.

Exercise the actual protected-mode phase selection and failure path against
the same fake server/candidate/Gateway modules using explicit dependency
injection. Verify no fake-server-only observation silently satisfies protected
predicates, every required predicate has its direct producer, phase snapshots
remain available after cleanup, all selected result rows serialize, and first
failure stops subsequent calls. This is protected-mode orchestration testing,
not protected model acceptance. Zero real credential/environment/model access.

## D. Verification, documentation and publication

Run focused regressions, full frozen pytest/Ruff/format/mypy/compileall/shell/
build/wheel boundary/diff/pin/privacy checks, then fresh full actual-Codex0.149
fake C1–C5/D qualification through exact Gateway and unchanged Local product
with the qualified observer. Keep Codex checksum
`bbc3341e44c9ead340ed9570c17be936e37870f570751a941699ffd04d672827`.
Require all selected fake rows/projections PASS, zero missing/failure/retry,
same-session image/crop, governance/rehydration, identity/replay/tamper/isolation,
tool/call-ID/HMAC/accounting, privacy/no-bypass/cleanup and fake refusal/rollback.
Additionally report all protected-mode synthetic conformance cases and exact
zero real-protected-access counts. Do not infer conformance from fake-mode PASS.

Update current docs to tested failure retention and budget guarantees; preserve
UNKNOWN 005-r/v facts and all immutable reports. REAL-E2E ACCEPTED, CUTOVER
ACCEPTED, MERGED, RELEASE-READY remain no. No Gateway escalation unless a new
direct defect is proved; this round repairs Local evidence handling.

Use only existing task-owned loopback PostgreSQL16/tmpfs/--rm, bounded Docker
operations, private synthetic client/cache state; no privileged/host network,
host packages/daemons or persistent DB. Cleanup exact validated task targets;
preserve .venv/unrelated files. No raw prompts/source/images/SSE/model/tool
data/credentials/IDs/signatures/nonces/private endpoints in logs/artifacts.
Coding owns routine setup/implementation/tests/publication/evidence; no human
or strategic terminal labor. Verify unchanged protected host facts afterward.

Amend PR7 only, push all non-report code and exact order/active, record literal
implementation SHA after required checks. Atomically create exactly
`oap/reports/005-w-protected-mode-projection-and-failure-retention.md` with
Implementation head SHA and Report publication commit: SELF. SELF report-only,
parent exactly implementation SHA; push and verify remote head/parent/path/bytes
before response FIFO OK. Include exact identities, A–D proof/test cases,
fake and protected-mode-synthetic results, budgets/counts, cleanup/host facts,
checks, UNKNOWN facts and limits. Coding never merges or creates a new PR.

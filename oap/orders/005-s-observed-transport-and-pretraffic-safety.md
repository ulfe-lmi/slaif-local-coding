# OAP Work Order — 005-s

## Objective

Repair the Local acceptance harness safety and independent observation gaps
found in 005-r. Qualify the existing Local HTTPX transport seam against fake
upstream, bind complete fake evidence to the exact candidate, and prove all
missing prerequisites stop execution before credentials or inference. Account
for the disclosed 005-r stop-rule deviation from existing safe evidence only.
Finish with fresh full fake C1–C5/D evidence and one immutable report.

This is the next bounded round of Objective 005 on existing PR #7. It prepares
the safe protected acceptance needed for closure; it does not itself authorize
another protected attempt. No change to Gateway, Qwen, product policy, active
profiles, public networking, or installed services. Coding never merges.

## GitHub state and exact authority

- Repository `ulfe-lmi/slaif-local-coding`; `005-s`, `AMEND_EXISTING_PR`.
- **NO NEW PR**. PR https://github.com/ulfe-lmi/slaif-local-coding/pull/7
- Base/head `main` / `oap/005-gateway-ingress-integration`.
- Remote main `570bd2b24ad4b041a07e0320d5ed44bc73e99ad5`.
- Start at immutable 005-r report head
  `31ccf159bd0d7a6cc93704ecb5522ca3dc51dc11`.
- Literal implementation parent
  `dae975c2fe761f1fa74679536b161fb40f1b9b1e`.
- Report-only path
  `oap/reports/005-r-gateway161-full-acceptance-and-protected-closure.md`.
- PR OPEN, non-draft, MERGEABLE/CLEAN; report-head `test` SUCCESS,
  run 34375596000 / job 102547463254; checkout clean; 005-s free.
- Gateway execute pin stays `50dcc3b85d614eb1d0c6196595bf22ef5779f846`;
  merged main `d142fd7f04c46fac3469b9b9bba1bd2068aabad8`;
  report `ad1c556a539130c08dc1063b3e9a25a0af2e5a85`;
  app tree `c0204deaff3cfd055a25f29a7f5d8d3c5e161d57`.
  All ten Gateway final checks are successful; handback is Local comment
  5601188832. Keep the accepted compatibility behavior and pins unchanged.

Verify these facts before edits. After activation only this exact order and
active selector are expected initial differences. Preserve 005-q, 005-r, and
every prior order/report byte-for-byte. Do not rerun or reinterpret 005-q.

## Scope and protected-host boundary

Preflight host hinton1: vision Qwen active MainPID 23961, start
`Sun 2026-09-06 18:57:26 CEST`, zero restarts, port 18020; model qwen3.8-27b,
100000 context, one sequence/image; text service inactive; 18021/18030/18031
free; seven pre-existing Qwen worktree entries. Existing coding wrapper uses
oap-coding-luna-xhigh and is back at its control wait.

Read-only service/PID/start/restart/listener/unauthenticated health observations
are allowed. No protected credential read, process-environment read, models
request, image, compiler, inference, or diagnostic call to protected Qwen.
Never restart/change qwen-serving, units, port 18020, model/checkpoint/patches/
venv/launch/GPU/image/context settings, credentials, firewall/VPN/network, or
active Codex profiles. Preserve unrelated checkout and .venv state.

Allowed changes: existing repository-only rehearsal, transport/evidence helpers,
their focused tests, current TESTING/integration/runbook documentation, exact
order/active, final report. A small helper module for shared observation is
allowed when needed, outside the wheel. Do not modify src/, Gateway, versions,
lockfiles, client binary, or replace the established harness architecture.

## A. 005-r deviation accounting

005-r reports later protected calls after the first unobserved prerequisite,
before its repair. Its report omits actual per-phase counts and the precise
pre-repair candidate state. From already-existing task-owned sanitized facts,
record the tested code identity if recoverable, attempted phases, call counts
by compiler/inference/health class, timing/budget status, first failing gate,
later calls, and cleanup. If not recoverable, mark UNKNOWN explicitly.

Do not infer zero calls from missing data; do not claim budget compliance from
one process attempt. No new reproduction against Qwen, no host Codex/session
history search, raw log recovery, secret inspection, or old report edit.
The safety deviation remains disclosed even after the code is fixed.

## B. Validate complete fake evidence and candidate identity

Reproduce `_validate_fake_gate` accepting the current singleton
`results=[{status:PASSED}]` without any obligation ID, observation, projection,
or Local candidate identity. Fix it using the existing manifest/projection
contracts rather than trusting the top-level passed/missing flags.

Require exact ordered selected IDs with no duplicate/unknown/missing item;
all expected observations and relationships; correct projection/producer
membership and predicate result; zero retries, no failure, all terminal PASS;
same Gateway pin and app tree; same executable Local production/harness source
identity and synthetic route/config policy; exact Codex binary/version; current
run provenance. A later report-only commit must not invalidate identical tested
code, but any relevant source/config change must invalidate reuse. Publish and
record the literal tested implementation SHA before acceptance execution.

Prefer the actual in-memory completed run result. If a result file is used,
require task ownership, expected regular-file path, bounded read before parsing,
closed schema, and candidate binding; do not accept arbitrary success flags.
Never use or persist an upstream credential for attestation. No raw payload or
real identity hashes in provenance.

Tests must reject singleton success, removed/duplicate/reordered/extra IDs,
false or absent observation, wrong relationship, missing/false projection,
stale Local/harness/config/Gateway/Codex identity, unobserved or skipped result,
nonzero retries, failure flags, and oversized/malformed/unsafe files. Include a
genuine complete positive result from the actual harness, not only a fabricated
all-true fixture.

## C. Pre-traffic safety and direct transport observation

Current protected code runs `_run_fake_codex_turn` and only then sets
`protected_provider_boundary_unobserved=True`. Move observation availability,
candidate binding, budgets, and stop dependencies before any credential read,
candidate readiness that can call upstream, or Codex/provider dispatch.
Missing prerequisites must produce a bounded NOT RUN result with zero dispatch.
An observer losing readiness during execution must stop later calls and still
complete cleanup. Enforce per-phase and overall budgets from current scope;
do not increase them or replace them with a declaration in the report.

Use existing `create_app(settings, transport=...)`, `VisionOutboundRecorder`,
and the pass-through `RecordingTransport` / `RecordingStream` mechanisms as
source references. Qualify an acceptance-only observer inside the Local
candidate, delegating directly to HTTPX's real network transport. No extra
proxy/service/relay/endpoint, protected service instrumentation, or src/ change.
The candidate may be launched by repository-only support using the public app
factory; actual Gateway/Local modules remain authoritative.

Observe actual transport dispatch attempts and upstream stream events before
Gateway, independently of Gateway ledger rows or Local ingress counters. Keep
attempted/dispatched/responded/completed distinct. Classify compiler versus
public inference separately. Record only safe per-ordinal event/count/status/
relation/timing facts. Terminal validity must follow parsed events and usage,
not 2xx or transport closure. Existing Gateway validator may validate the
observed bounded stream with the exact applicable profile; do not copy its
policy. Unknown/malformed/incomplete output must remain non-pass.

Preserve request and response bytes, ordering, status, headers, streaming first
byte timing, backpressure, cancellation, disconnect, and closure. No buffering
of entire responses or replay of streams. Existing helpers retain raw request
bodies/IDs internally: do not export or extend that retention. Clear transient
parse values; retain only fixed evidence. Do not emit raw digests of secrets,
prompts, or responses. Synthetic fixtures may have fixed expected hashes.

Tests use a real bounded loopback fake upstream plus stub credential/dispatch
counters. Prove unchanged bytes/events and one dispatch per permitted request;
first chunk arrives before terminal completion; bounded parsing; compiler
separation; no inference on missing/stale/failing observer or fake gate;
zero later dispatch after first failed predicate; timeout/disconnect/cancel/
malformed/truncated/overflow behavior; cleanup on observer exceptions. Never
test these negatives against real Qwen in this round.

## D. Fresh fake integration and publication evidence

Run actual task-controlled Codex 0.149.0, SHA-256
`bbc3341e44c9ead340ed9570c17be936e37870f570751a941699ffd04d672827`,
through exact Gateway 50dcc3b..., actual Local with the qualified transport,
and strict fake upstream. Preserve the actual same-session full-image then
resumed crop/history interaction and all existing C1–C5/D predicates.
Re-observe identity/signing, natural tool/call-ID/HMAC lifecycle, accounting,
replay/tamper/isolation, governance/compiler/cache/rehydration, newest-image
fidelity, privacy, no bypass, cleanup, and fake cutover/refusal/rollback.

Require all selected obligations PASS, exact source/observer provenance,
no missing item, no first failure, zero retries. Compare observer dispatch/
terminal facts with independent fake-server counters and Gateway accounting.
No literal all-true or inferred ledger-based provider proof. If a remaining
direct failure occurs, report it and preserve limits; do not substitute a
smaller test for the required integration.

Run focused regressions and full frozen pytest, Ruff check/format, mypy src
tests, compileall, shell syntax, build/wheel boundary, diff/pin/privacy scans,
and current required Local CI. Test each changed behavior meaningfully; rerun
affected checks after edits. Gateway final acceptance is retained; do not
launch historical Gateway diagnostics. Use existing disposable PostgreSQL 16,
loopback/tmpfs/--rm, exact Docker operations only, no privileged/host networking
or persistent DB. No package/daemon/host setup outside prior scope.

Update current docs with the measured observer and gate guarantees and honest
005-r deviation/UNKNOWN facts. Correct the unsupported claim that observation
necessarily requires a relay or Qwen mutation. Historical reports are immutable.
State REAL-E2E ACCEPTED=no, CUTOVER ACCEPTED=no, MERGED=no, RELEASE-READY=no.
Fake tests qualify the observer but do not establish protected acceptance.

Coding owns routine setup, support edits, tests, Git publication, and evidence.
No human/strategy terminal work. Keep artifacts synthetic, private, bounded,
and task-owned; no raw bodies/source/images/tool output/credentials/identities/
signatures/nonces/private endpoints/arbitrary errors in logs or reports.
Cleanup only exact validated task-owned resources. Verify unchanged protected
PID/start/restarts/listener, inactive text service, candidate ports free and
unrelated Qwen state preserved. Zero protected requests except permitted
unauthenticated health checks; report their count separately.

## Immutable report contract

Amend PR #7 only. Commit exact 005-s order/active with intended support/tests/
docs, push all non-report work, check CI, record literal implementation SHA.
Atomically publish exactly
`oap/reports/005-s-observed-transport-and-pretraffic-safety.md` containing
`Implementation head SHA: <literal>` and `Report publication commit: SELF`.
SELF changes only this report and first parent equals that SHA. Push and
verify remote head/parent/path/bytes; send exact response FIFO OK once.

Report each A–D requirement, actual fake results/projections, negative gate
dispatch counts, observer fidelity/resource tests, protected non-use and
cleanup, exact Local/Gateway/Codex identities, CI, limits, and all UNKNOWN
deviation facts. Do not claim protected readiness merely from an implemented
observer. Return to strategy for review; no new PR, merge or protected retry.

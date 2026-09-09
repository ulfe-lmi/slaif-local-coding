# OAP Work Order — 005-u

## Objective and state

Close the concrete stream-lifecycle, validator-prerequisite and test gaps in
005-t, then requalify the existing complete fake matrix. This is a focused
Local harness correction, using the existing observer/factory architecture.
No protected credential/inference, service mutation, new diagnostics subsystem,
Gateway changes, product-policy changes, or new PR. Coding never merges.

- Repository ulfe-lmi/slaif-local-coding; Objective 005 round 005-u.
- AMEND_EXISTING_PR; NO NEW PR.
- PR https://github.com/ulfe-lmi/slaif-local-coding/pull/7
- Base/head main / oap/005-gateway-ingress-integration.
- Main `570bd2b24ad4b041a07e0320d5ed44bc73e99ad5`.
- Start report `c908b6ec1b1a7b5ec93d0184386fb225387bd1de`;
  implementation parent `4041e80431d732a1d3640417c8031781d8a5d471`;
  only report path `oap/reports/005-t-strict-observer-and-exact-safety-evidence.md`.
- PR open/non-draft/mergeable, report-head test SUCCESS
  (34389963262/102595547960), clean checkout, 005-u unused.
- Gateway execute `50dcc3b85d614eb1d0c6196595bf22ef5779f846`, merged main
  `d142fd7f04c46fac3469b9b9bba1bd2068aabad8`, immutable report
  `ad1c556a539130c08dc1063b3e9a25a0af2e5a85`, app tree
  `c0204deaff3cfd055a25f29a7f5d8d3c5e161d57`; pins unchanged.

Reconcile GitHub/checkout and required checks before edits. After activation,
only this exact order/005-u active selector may pre-exist as intended changes.
Preserve all earlier orders/reports including immutable 005-q/r/s/t. Do not
rerun historical rounds or rewrite their claims.

## Protected boundary

Host hinton1, vision Qwen PID 23961, start Sun 2026-09-06 18:57:26 CEST,
zero restarts, port 18020, model qwen3.8-27b/context 100000/one sequence/image.
Text inactive; 18021/18030/18031 free; seven pre-existing Qwen entries. Current
coding wrapper/profile remains unchanged.

Only read-only PID/start/restarts/unit/listener and unauthenticated health
observations allowed. No credentials or process-environment/raw-log/config
read; no models/compiler/inference/image/diagnostic calls to protected Qwen.
Never restart/change Qwen/port18020/model/checkpoint/patches/venv/units/launch/
GPU flags/keys, network/firewall/VPN or active profiles. No second model.
No src/, Gateway, dependency/lockfile, binary, topology or installed-service
change. Preserve unrelated work and .venv.

## A. Exact stream closure

Independent reproduction of 005-t: consume a successful JSON response through
DirectTransportObserver, call response.aclose, and inspect a fake delegate's
close counter. response.is_closed is true while delegate close count is zero.
The stream iterator sets _finished and aclose returns early, leaking closure.

Separate observation-finalization from delegate-closure state. Close the
delegate exactly once on normal exhaustion, explicit early close, cancellation,
timeout and exception; repeated close must be idempotent. Preserve the original
error/cancellation, latch abnormal lifecycle failure, clear transient buffers,
and never mark a cancelled/truncated stream terminal-valid. Do not buffer the
response or add a network hop. Add regressions that fail on the exact 005-t
implementation for JSON and SSE and every closure path.

## B. Prerequisites before any upstream side effect

Independent reproduction: observer without validator reports ready=true, then
dispatches a Responses request before rejecting validator_unavailable.

Validate required validator availability and request-profile construction before
delegate.handle_async_request. Missing factory, raising factory, invalid request
profile and latched-unready state must produce zero upstream dispatch. Do not
wait for response headers to discover a known prerequisite failure. Retain
appropriate JSON/health/compiler handling without giving inference a bypass.
Candidate preflight must reflect the observer's actual supported capabilities.
Test readiness/factory failures through the actual admission code, not only a
manual mark_unready call. Count credential-hook, Codex-launch and dispatch
non-entry with stubs; protected execution remains forbidden in 005-u itself.

For queued/concurrent calls, prove no new dispatch begins after a failure is
latched. Report already-dispatched calls separately; do not falsely claim that
a future failure can undo an earlier legitimate dispatch.

## C. Actual network streaming tests and exact validator tests

The current observer tests use MockTransport and client.post followed by
aiter_bytes. That auto-buffered path does not prove first-byte streaming.

Add a bounded loopback server and real AsyncHTTPTransport test using streaming
client APIs. The producer must withhold terminal output behind an explicit
synchronization event; require the first client chunk before releasing it.
Assert exact bytes, status and headers, delegate close/connection return, and
no extra dispatch. Include cancellation/early disconnect/truncation/delegate
exception and test timeout cleanup. No sleeps as a success oracle; finite
deadlines are safety guards only. No external network or protected Qwen.

Keep framing-interface unit stubs if useful, but semantic claims require tests
with the actual pinned Gateway ResponsesStreamEventValidator and the factory
used by the candidate. Prove valid reviewed message/function/reasoning streams
pass and wrong event/payload type, mismatched IDs, usage total, missing output,
unknown names, malformed lifecycle fail. Explicitly compare identical wire
bytes coalesced beyond the frame cap versus split into valid smaller frames;
each individual frame remains under the existing cap. Preserve LF/CRLF and
one-byte fragmentation invariance. Do not relax the Gateway profile, fake
fixtures, observer limits or acceptance criteria to obtain a pass.

## D. Report-only reuse and fresh qualification

_tested_source_still_valid still hard-codes the 005-s report path. Make report-
only descendants round-neutral but exact: only verified single-parent report-
publication commits with only the corresponding immutable report may be
excluded; changed production/harness/config files or dirty relevant worktree
must invalidate reuse. Test the actual Git command/ancestry path with disposable
Git fixtures, not a monkeypatch that always returns true.

Keep the complete ordered fake gate, exact independent integer counting and
strict owned bounded result-file checks. Run focused A–D tests, then the full
existing 37-obligation fake matrix using real Codex 0.149.0, SHA-256
`bbc3341e44c9ead340ed9570c17be936e37870f570751a941699ffd04d672827`, exact
Gateway, actual Local and strict fake upstream. Re-establish actual same-session
full-image/crop, governance, signing/replay/tamper/isolation, tool HMAC lifecycle,
accounting, privacy/no-bypass/cleanup and fake cutover/refusal/rollback.
Require all selected rows PASS, no missing/failure/retry, exact dispatch and
terminal facts matching independent fake counters, and exact tested code identity.

Run frozen full pytest, Ruff/format, mypy src tests, compileall, shell syntax,
build/wheel boundary, diff/pin/privacy scans and current required Local CI.
Report actual collected/executed tests and guarantees; do not claim missing
coverage based on code inspection alone. Keep 005-r UNKNOWN deviation facts
and all historical reports intact. Current docs must match tested behavior.

Use existing task-owned PostgreSQL16/loopback/tmpfs/--rm and exact bounded
Docker operations only. No host package/daemon changes. Cleanup only validated
task-owned targets; no broad deletes. No raw prompts/source/images/tool/SSE/
model text/credentials/IDs/signatures/nonces/private endpoints/arbitrary errors
in artifacts. Keep transient semantic parsing bounded and private. Coding owns
routine setup/implementation/testing/publication; no human/strategy terminal
labor. Verify unchanged protected unit/PID/start/restarts/listener and absent
task resources; count any permitted unauthenticated health probes separately.

## Immutable publication

Amend only PR #7. Push exact order/active and intended helper/harness/tests/docs,
record literal implementation SHA after CI, atomically create only
`oap/reports/005-u-close-stream-and-predispatch-proof.md` with
`Implementation head SHA: <literal>` and `Report publication commit: SELF`.
Final commit report-only, parent equals literal implementation SHA. Push,
verify remote PR head/parent/path/bytes, send exact response FIFO OK once.
Report exact test/fake results, scope, source identities, safety/cleanup,
remaining gaps. IMPLEMENTED/TESTED need actual proof; REAL-E2E ACCEPTED,
CUTOVER ACCEPTED, MERGED and RELEASE-READY remain no. No coding merge or new PR.

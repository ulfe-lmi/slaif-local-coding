# OAP Work Order — 005-ai

## Objective and exact state

Correct the Local controller's cross-response byte accumulation while preserving
the existing128KiB per-response limit, and retain accurate completed-phase and
first-failure evidence. Fake-only remediation of Objective005 on PR7. No protected
credential, Qwen inference retry, Gateway change, cutover or merge.

- AMEND_EXISTING_PR; NO NEW PR; ulfe-lmi/slaif-local-coding PR7:
  https://github.com/ulfe-lmi/slaif-local-coding/pull/7
- Base/head main / oap/005-gateway-ingress-integration.
- Main `570bd2b24ad4b041a07e0320d5ed44bc73e99ad5`.
- Required immutable start `b43ec3d8932a8fe92dbb62c54411b7df817b8d01`;
  report-only parent `0e9c3e7b30ef9111ab9cf56ac65cf991891c6f15`.
- Report oap/reports/005-ah-validated-canonical-protected-acceptance.md.
- Exact topology/order/active/clean checkout verified; PR OPEN/CLEAN; final
  test SUCCESS34453056503/job102793001674;005-ai unused.
- Gateway execute `50dcc3b85d614eb1d0c6196595bf22ef5779f846`; merged-main
  authority `d142fd7f04c46fac3469b9b9bba1bd2068aabad8`; report
  `ad1c556a539130c08dc1063b3e9a25a0af2e5a85`; app tree
  `c0204deaff3cfd055a25f29a7f5d8d3c5e161d57`. Keep exact pins unchanged.

Reconcile GitHub/import/source/host before edits. Only exact order and active005-ai
are expected new differences. Read005-ah order/report/evidence; preserve every
old artifact, especially005-q,005-af/ah protected stops, UNKNOWN005-r/v counts and
005-ag's scope deviation. Do not recover raw IDs/content from old logs or retry
protected traffic to reconstruct missing evidence.

## A. Per-response byte lifecycle, not a larger budget

Direct source: BudgetController._stream_bytes is initialized once and never
reset by dispatch admission or release. observe_chunk therefore sums bytes from
health/models/compiler/inference responses across the run.

Strategic connected-observer reproduction: two sequential valid unread HTTP JSON
responses of70014 bytes each, each under131072, consume two allowed compiler
slots. First passes; second is delegated but then fails budget_stream_limit_exhausted.
This is a Local meter defect, not proof of an overlong individual Qwen response.

Bind byte state to each actual admitted HTTP response/stream lifetime, across
compiler, inference and other requests. Initialize/reset it only at a valid new
lifetime; do not reset an in-flight stream through a rejected/concurrent/stale
request. Keep the run deadline, request permissions, concurrency and global stop
latch intact. Do not clear failures when a stream closes. No later dispatch after
a genuine bound/semantic/closure failure. Preserve cancellation and exact-once
delegate close/release. Keep frame bytes distinct from network chunks and stream
bytes; do not buffer whole SSE responses or drop/modify forwarded bytes.

The numeric limits do NOT change:16KiB per event/frame,128KiB per response/stream,
64 aggregate observations,900 seconds, existing nine macro operations maximum1/
zero retries, all per-operation compiler/inference/output limits, single concurrency.
Correcting the meter to the ordered per-stream meaning is not authorization to
raise any cap, token limit, request count or provider setting. If a separately
specified run-wide byte constraint exists, identify it explicitly; never silently
conflate it with max_stream_bytes or invent a new limit.

Tests through the connected observer/controller must include sequential legal
responses whose combined bytes exceed128KiB; mixed compiler/inference/health/model
lifetimes; split/coalesced Gateway-validated SSE; exact-bound and genuine single-
response overflow; rejected/concurrent admission unable to reset another stream;
timeout/cancel/close failure; and zero later dispatch after a real failure.
Use unread asynchronous streams in MockTransport fixtures, not pre-consumed
Response(content=...) objects that bypass observation. Keep the real-loopback
and exact Gateway validator tests where relevant.

## B. Exact safe byte and first-failure evidence

005-ah advanced through the guarded Codex phase into vision, but its generic
failure result lost earlier observations and reported C1.1 as first failure.
Preserve actual completed phase facts incrementally in the existing runner/
accumulator so a later failure cannot erase them. Do not reconstruct PASS from
counts alone. Freeze the first runtime failure's phase, operation, request
ordinal/kind/lifetime and cause when it occurs, before cleanup changes context.
Keep that separate from an earliest unsatisfied manifest row: an earlier-listed
companion row may legitimately be NOT RUN when a later physical phase fails.

Record bounded exact byte counts needed to distinguish one-response overflow
from total-run traffic: per-response received/accepted bytes, rejected-chunk
accounting if applicable, configured limit, and clearly labelled all-lifetime
totals. Counts/classes only; no raw body, text, ID/digest or frame capture. Do
not retrospectively fill005-ah byte values that were not recorded, or claim its
single vision stream exceeded128KiB merely from the old cumulative failure.

Qualify a fake run that completes the initial Codex phase and then fails in the
first vision response. It must preserve prior observed facts, the actual vision
failure context, all29 selected dispositions, exact request/byte/accounting/
cleanup evidence, and zero later dispatch. Also inject projection and cleanup
failures without replacing the first failure. Use the existing shared runner
and synthetic protected hooks; no parallel acceptance subsystem or real fixture
access. Preserve canonical replay/summary diagnostics and same/different valid
identity handling, mode provenance and client-versus-observation separation.

## C. Full fake qualification and safety

Run fresh actual-Codex0149 fake37/37 C1–C5/D and shared synthetic protected29/29
with fake semantic oracle unavailable, plus all existing failure cases and the
later-phase checkpoint case above. Keep actual canonical omission companion,
summary-alias negative, wrong-key/missing/mismatched replay negatives, signed
identity, governance/compiler/cache/rehydration, full-image/crop history,
isolation, accounting/zero pending, privacy, cleanup and fake rollback-refusal.
No existing acceptance predicate may be weakened or replaced by a literal PASS.

Run frozen full pytest/Ruff/format/mypy/compileall/shell/build/wheel-boundary/
diff/pin/privacy checks and required CI. Generate source-bound safe artifacts
under oap/evidence/005-ai with concrete command bindings, testedSHA/module hashes,
row statuses, exact per-lifetime/byte/stop/checkpoint facts and limitations.
Code/config edits require requalification; docs/evidence-only reuse requires
exact diff/ancestry attestation. No stale hand-copied totals.

Same UID/EUID1029 for all harness/client/evidence work; owned private dirs0700/
files0600 and existing owner/regular/no-follow/single-link checks. Existing bounded
sudo Docker helper only, never whole-harness elevation. Exact Codex0.149.0:
/synology/homes/janezp/.codex/packages/standalone/releases/0.149.0-x86_64-unknown-linux-musl/bin/codex;
SHA256 bbc3341e44c9ead340ed9570c17be936e37870f570751a941699ffd04d672827.

Host hinton1 vision active/running PID23961,UID1029,startSun2026-09-06
18:57:26CEST,NRestarts0,18020listener; text inactive/MainPID0 expected, seven
Qwen changes. Read-only unit/PID/start/restart/listener/worktree facts and bounded
unauthenticated GET /health status only. NO /v1/models probe, credentials,
environment/config/log/model reads, authenticated/model/compiler/inference/
vision/diagnostic requests or retry. No Qwen/model/checkpoint/patch/venv/unit/
launch/GPU/key/network/firewall/VPN/profile mutation, restart or second model.
Preserve actual OAP profiles. Task candidate127.0.0.1:18031, existing verified-
free ephemeral loopback Gateway and PostgreSQL16 tmpfs/--rm only. Exact owned
cleanup; preserve unrelated files/resources. No raw secrets or customer content.

Allowed edits are existing support/tests/current docs/generated evidence and
exact transcript, not src/, Gateway/PR, dependency/lock/version/binary, new
relay/subsystem or installed service. Coding owns routine setup/tests/publication.

## Immutable publication and return

Amend PR7 only. Push non-report work plus exact order/active, inspect CI, record
literal implementationSHA, then atomically publish exactly
oap/reports/005-ai-per-response-byte-budget-and-stop-evidence.md with
Implementation head SHA and Report publication commit: SELF. Final commit only
report, parent exactly implementationSHA; verify remote head/parent/path/bytes
before response FIFO OK. COMPLETE requires all A–C; otherwise truthful
PARTIAL/FAILED/BLOCKED. No protected retry, cutover, merge or release acceptance
in this round. Return immutable evidence for strategic review.

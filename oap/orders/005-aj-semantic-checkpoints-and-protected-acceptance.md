# OAP Work Order — 005-aj

## Objective and exact state

Preserve actual verified client/semantic phase facts across later failures,
requalify the corrected per-response meter and checkpoint path, then conditionally
execute one protected Objective005 matrix under unchanged bounds. This is
AMEND_EXISTING_PR on PR7, NO NEW PR or feature objective. No automatic retry,
budget increase, service change, cutover or merge.

- Repository ulfe-lmi/slaif-local-coding; PR:
  https://github.com/ulfe-lmi/slaif-local-coding/pull/7
- Base/head main / oap/005-gateway-ingress-integration.
- Main `570bd2b24ad4b041a07e0320d5ed44bc73e99ad5`.
- Required immutable start `18bd3d2a109705cd2b50e673bc3650d5940f9ff0`;
  report-only parent `9aca9975b36567208ae7ef3d5f4e4141598fd6d8`.
- Report oap/reports/005-ai-per-response-byte-budget-and-stop-evidence.md.
- Tested code `5d3b0c3dca0a79905a3ac60e611b2b5dbd856d32`; only docs/evidence/
  report descendants. Exact order/topology/clean checkout verified; PR OPEN/CLEAN,
  final test SUCCESS34460440217/job102816734970;005-aj unused.
- Gateway execute `50dcc3b85d614eb1d0c6196595bf22ef5779f846`; main authority
  `d142fd7f04c46fac3469b9b9bba1bd2068aabad8`; report
  `ad1c556a539130c08dc1063b3e9a25a0af2e5a85`; app tree
  `c0204deaff3cfd055a25f29a7f5d8d3c5e161d57`. Keep exact pins unchanged.

Reconcile GitHub/checks/import/source/host before edits. Only this exact order and
active005-aj are expected differences. Read005-ah/ai orders/reports/evidence and
preserve all prior artifacts, including005-q, protected stops, scope deviations
and UNKNOWN prior facts. No raw-log/ID reconstruction or historical rerun.

## A. Preserve real semantic checkpoints; preparation only

Strategic verified the byte repair with two sequential70014-byte responses:
both pass under131072 each; combined140028 is diagnostic only, not a failure.
Keep that implementation and all limits unchanged.

The005-ai later-vision-failure case still has no codex/client-verification data,
C1.1 MISSING and C1.2/C1.3 NOT RUN. Its completed checkpoint is only transport
readiness/counts. That does not satisfy preservation of actual earlier client,
canonical/semantic, governance and accounting observations.

In the existing shared runner/accumulator, checkpoint the already-safe actual
phase facts when verified, before entering a later phase. A later exception or
generic failure projection must retain those facts. Include actual client
verification, canonical provider/terminal relationships and relevant safe
accounting/governance observations; use the existing safe result forms, never
raw CLI output, requests, responses, IDs or tool/source content. Transport-only
checkpoints may remain but must be labelled as such and cannot imply client or
semantic acceptance. Do not reconstruct PASS from counts or hard-code completed
row statuses. Preserve genuine earlier failures without normalization.

Reproduce through the actual shared fake/synthetic runner: initial Codex phase
success, then first vision response failure. Require retained actual client
verification and earlier observed semantic/accounting facts, correct projected
earlier rows from those facts, first runtime stop at vision_full/ordinal3, all29
dispositions, exact per-response/all-lifetime bytes and request counts, no later
dispatch and exact cleanup. Unexecuted companion/later rows remain NOT RUN; first
unsatisfied manifest row is distinct from chronological runtime failure. Repeat
with secondary projection and cleanup failure without erasing prior facts or
the primary failure. Use existing hooks/helpers, not another acceptance subsystem.

Re-establish exact-bound and genuine single-response overflow, multiple legal
responses whose combined bytes exceed128KiB, concurrent/rejected/stale admission
unable to reset another stream, close/cancel/deadline, canonical same/different
summary behavior, actual omission and ownership negatives. Preserve16KiB/frame,
128KiB per response,64 total observations,900 seconds, nine macro operations
maximum1/zero retries and all existing per-operation/compiler/output limits.

Push all support code plus exact order/active, freeze a clean literal code SHA,
and require every implementation-head check present and successful. Run frozen
full pytest/Ruff/format/mypy/compileall/shell/build/wheel-boundary/diff/pin/privacy
checks, fresh real-Codex0149 fake37/37 C1–C5/D and shared synthetic protected29/29
with oracle unavailable, including every existing failure case and the complete
later-phase semantic checkpoint case. Validate exact source/module hashes, mode,
row/cardinality/status/counter/UID facts. Keep generated results in owned private
temporary files outside the checkout until the protected attempt is finished.
Any code/config change invalidates qualification and requires fresh fake/CI.
No protected credential or traffic if a required fact remains unproved.

## B. One protected matrix only after full A and unchanged preflight

This is a newly reviewed attempt after the Local per-response accounting repair,
not permission to rerun or rewrite005-ah. Use unmodified Codex0.149.0 -> exact
Gateway50dcc -> frozen Local candidate/qualified observer -> unchanged vision
Qwen. Exact Codex binary:
/synology/homes/janezp/.codex/packages/standalone/releases/0.149.0-x86_64-unknown-linux-musl/bin/codex;
SHA256 bbc3341e44c9ead340ed9570c17be936e37870f570751a941699ffd04d672827.

Same UID/EUID1029 for producer/validator/harness/client/evidence; no whole-run
sudo/su/root wrapper. Existing bounded sudo Docker helper only. Owned dirs0700/
files0600, regular/single-link/no-follow/owner checks unchanged. Validate the
fake evidence under the same UID/environment before any credential resolution.

Host baseline hinton1: vision qwen-serving-vision.service active/running,
PID23961,UID1029,startSun2026-09-06 18:57:26CEST,NRestarts0,18020listener;
text inactive/MainPID0 expected, seven Qwen changes,18021/18030/18031 free.
Preserve qwen3.8-27b/context100000/one sequence/image and actual OAP profiles.
Candidate127.0.0.1:18031; existing verified-free ephemeral loopback Gateway port,
with actual PID/port cleanup. Preparation permits only read-only process/unit/
listener/worktree facts and bounded unauthenticated GET /health status. No manual
/v1/models or endpoint-discovery probe. Authenticated model visibility occurs
only inside this gated matrix.

After A and verified unchanged identity, read only the exact active vision
MainPID's unique nonempty VLLM_API_KEY into bounded memory using the existing
approved same-UID mechanism. Pass only via task harness QWEN3090_API_KEY/Local
upstream header and discard afterward. Never print/hash/persist it, place in
argv, send to Codex/public Gateway metadata, source Qwen config or inspect
unrelated environment entries. No new credential or privilege authority.

Require every protected C1–C5 obligation: readiness/authenticated models and
ordinary nonstreaming; actual Codex tool roundtrip and valid reasoning/function/
message/usage lifecycles; canonical same-call ID-less companion and HMAC ownership
separate from natural present-ID shape; same-session reuse and real full-image
then resumed crop/history/newest-image behavior; compiler/governance/cache/
rehydration/dependency acquisition; signed identity every admission, replay/
tamper/unauthorized/hosted/quota and key/session/owner/repository isolation;
per-request reservation/ledger finalization or release, correct counters,
zero pending/duplicates, compiler exclusion; privacy, no bypass and exact
cleanup/preservation. Controlled failure remains the synthetic failure route,
never deliberate Qwen failure. Fake success never substitutes for real acceptance.

FIRST unexpected failed/unobserved protected boundary stops every later protected
dispatch. Preserve actual partial checkpoints, first runtime context, exact bytes/
requests/accounting and primary/secondary cleanup facts. No retry after repair,
alternate prompt/diagnostic, cap increase, Gateway/Qwen patch or instrumentation.
If one response genuinely exceeds131072, report its measured per-response bytes
and stop; this order does not authorize a larger limit. Do not reclassify the
old cumulative005-ah failure as an individual oversized response.

## C. Scope, evidence and immutable return

Allowed implementation: existing support/tests/current docs/generated evidence
and exact transcript for A. No src/, Gateway/PR, dependency/lock/version/binary,
new subsystem/relay, installed service, Qwen/model/checkpoint/patch/venv/unit/
launch/GPU/key-file/firewall/VPN/network/profile mutation, restart or second model.
Existing PostgreSQL16 loopback/tmpfs/--rm/bounded Docker helper only. Preserve
unrelated state; clean exact owned processes/ports/data. No raw secrets, IDs/
digests, arguments, prompts/source/images/tool/model/SSE bodies, signatures/nonces/
private endpoints or arbitrary errors in logs/cache/evidence. Safe code/fixture
hashes and bounded counts/relationships remain allowed. Coding owns routine setup.

Generate source-bound actual fake and protected evidence(or exact NOT RUN reason)
under oap/evidence/005-aj with concrete commands/bindings, source/module hashes,
mode/UID/row statuses, safe semantic checkpoints, actual first stop, exact per-
response/all-lifetime counts, ownership/accounting/cleanup and host facts. Validate
against the run, not hand-copied values. Preserve old artifacts and deviations.
Actual cutover, merge and release remain unauthorized even if the matrix passes;
stop for separate strategic operational review.

Amend PR7 only. Push non-report work and exact order/active, capture literal
implementationSHA, then atomically publish exactly
oap/reports/005-aj-semantic-checkpoints-and-protected-acceptance.md containing
Implementation head SHA and Report publication commit: SELF. Final commit only
report, parent exactly implementationSHA; verify remote head/parent/path/bytes
before FIFO OK. No merge/auto-merge/new PR. COMPLETE only for genuine ordered
acceptance; otherwise truthful PARTIAL/FAILED/BLOCKED. Distinguish IMPLEMENTED,
TESTED, REAL-E2E ACCEPTED, CUTOVER ACCEPTED, MERGED and RELEASE-READY.

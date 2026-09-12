# OAP Work Order — 005-ak

## Objective and reconciled authority

Correct the acceptance-only observer's unjustified SSE-frame restriction where
source analysis warrants it, retain minimal structural overflow facts, qualify
the corrected source, and obtain one fresh real protected go/no-go result.
AMEND_EXISTING_PR; Objective005; NO NEW PR or feature objective.

- Repository ulfe-lmi/slaif-local-coding; PR7:
  https://github.com/ulfe-lmi/slaif-local-coding/pull/7
- Base/head main / oap/005-gateway-ingress-integration.
- Required immutable start 475539b885ea279e73ee0022a9286fdc06723f75;
  report-only parent 2fe43fa0f9f691907a322ffc020389e8b1f3eebe;
  tested005-aj source a56472704d82c8778c74abe7276017fb6466298b.
- Main570bd2b24ad4b041a07e0320d5ed44bc73e99ad5; PR OPEN, final test SUCCESS
  run34467135176/job102838233301. Local/GitHub head and005-ak availability
  independently reconciled. Preserve unrelated empty untracked Local, clean,
  unchanged; do not delete, incorporate, or commit them. A clean detached
  task-owned worktree at the exact candidate is allowed, as in005-aj.
- Gateway executable50dcc3b85d614eb1d0c6196595bf22ef5779f846;
  merged main authority d142fd7f04c46fac3469b9b9bba1bd2068aabad8;
  immutable PASSED report ad1c556a539130c08dc1063b3e9a25a0af2e5a85;
  app tree c0204deaff3cfd055a25f29a7f5d8d3c5e161d57.
  Reachability, exact app tree, clean fixture, report-only parent and all ten
  final Gateway checks were independently verified. Do not use a branch name
  as executable authority or modify Gateway.

Read governance, this order,005-aj report and its *-real/*-a564 evidence. The
human accepts005-aj NO-GO and005-ai remediation. Do not rerun/rewrite either,
recover old raw payloads, or infer a Gateway/Local-production/Codex/Qwen defect.

## A. Narrow correction and closed cause analysis

Enumerate every existing site mapping to stream_overflow in
tests/helpers/transport_observer.py. Independently checked source presently
includes: distinct event-class cardinality; replay-candidate tuple/type or batch
cardinality; accumulated returned-call cardinality; joined SSE data bytes;
non-SSE response bytes; SSE response bytes; incomplete frame-buffer bytes.
Distinguish framing, validator and budget failures which use other classes.

Use existing evidence to eliminate only mechanically impossible005-aj causes:
all responses were below131072 (maximum67381), zero response-byte rejections,
total270197 diagnostic only; the response counter is per response, not cumulative.
The closed event-class map plus fallback has fewer than32 classes. Exact Gateway
candidate API returns a tuple and clears its buffer; check its one-event capture
paths before claiming a batch-size impossibility. Joined SSE data cannot exceed
an already-bounded containing frame. Do not use the retained Codex checkpoint as
if it were missing vision-phase cardinality evidence. State remaining ambiguity
honestly; the offending005-aj frame was not retained.

Demonstrate with existing fake/validator test facilities that a legitimate
Responses event larger than16384 can fit inside a complete131072-byte response
and be rejected by the old acceptance frame/buffer check. Where justified, raise
the acceptance-only frame bound up to131072, never beyond it. This is explicit
human authorization; the old16384 frame limit is not immutable policy.

Keep related checks in the existing observer, acceptance budget and runner's
frame/call-capture parser consistent where necessary so another acceptance-only
16384 limit does not recreate the same false negative. No production source or
Gateway validator changes; keep semantic validation, mandatory call-ID/HMAC
ownership, framing and terminality checks intact. No new diagnostic subsystem,
observer design, matrix predicates, synthetic variants or historical machinery.

The131072-byte PER-HTTP-RESPONSE bound stays unchanged everywhere. Do not change
global-vs-response accounting, total request/inference/compiler/output budgets,
timeouts, concurrency, canonical replay rules, identities or source-trust gates.
Do not simply disable overflow, ignore validation, or mark a failed row passed.

For future overflow only, extend existing safe records/frozen first-failure
projection with a closed subtype and the observed integer size/configured integer
bound. Distinguish frame/buffer, response-byte and cardinality/type causes; never
mislabel a count as bytes or invent a size for a type error. Preserve first facts
through normal close, stop/projection and cleanup. No frame/payload fragments,
arbitrary exceptions, raw IDs/digests, source, images, tool arguments or secrets.

Focused tests must cover a valid >16KiB event under the response cap (fragmented
and coalesced LF/CRLF/data-only framing as applicable); unchanged response exact
bound/+1 rejection; malformed framing/terminal failures; closed overflow subtype
and size/bound accuracy; frozen primary facts through cleanup; no later dispatch.
Use current test helpers, not another synthetic framework.

## B. Qualification and one real matrix

Finish execution-relevant edits, commit/push exact order+active and support code,
freeze a clean literal candidate SHA, and run focused tests plus required normal
Ruff/format/mypy/unit/build/package/privacy checks and final-source CI. Then run
the required existing real-Codex0.149 fake37/37 C1-C5/D qualification on that exact
source. The runner's already-integrated synthetic checks may run normally; add
no separate synthetic-only round. Keep results in owned private temporary files
outside the checkout until protected completion. Validate the actual produced
fake file using the existing gate before any credential resolution. New fields
must work through the existing schema, not bypass it. Changes to execution code
require requalification; order/report/evidence metadata alone does not.

After qualification passes, execute EXACTLY ONE fresh real protected matrix:
unmodified Codex0.149 -> exact Gateway50dcc -> frozen Local candidate -> unchanged
existing vision Qwen. This is not an005-aj retry; its failed evidence is immutable.
If a deterministic local preflight defect is proven before ALL protected requests,
repair it within005-ak, run the appropriate non-protected gates, then proceed.
After actual protected traffic begins, zero retry, alternate prompt/probe, repair
and rerun, larger HTTP budget, other-repository patch or diagnostic inference.

Require all existing protected C1-C5 obligations, not just vision: readiness and
authenticated models/nonstreaming; real two-turn function/tool continuation and
same-session reuse; full-image -> resumed crop/history/newest-image behavior;
signed identity on every admitted request; valid reasoning/function/message SSE
lifecycles; natural shape plus ID-less companion/call-ID-HMAC ownership; replay,
idempotency, tamper, unauthorized/hosted denial and key/session/repository isolation;
compiler/cache/dependency acquisition/rehydration; per-admission reservation and
ledger finalization/release, zero pending/duplicates and compiler exclusion;
privacy/no raw content, cleanup and protected-host preservation. Existing fake D
rollback/cutover-refusal predicates remain required; actual cutover is excluded.
Controlled failure uses the existing synthetic failure route, not Qwen disruption.

First failed/unobserved protected boundary stops later protected dispatch. Retain
the direct first failure, the newly available safe overflow facts if applicable,
actual request/accounting/cleanup facts and truthful NOT RUN rows. No reconstruction
of full-matrix accounting/privacy PASS from an earlier phase checkpoint.

## C. Exact safety and execution envelope

Host hinton1: user qwen-serving-vision.service active/running, MainPID23961,
UID1029, startSun2026-09-06 18:57:26CEST, zero restarts;18020 listening; text unit
inactive/MainPID0 expected; seven pre-existing Qwen changed paths. Preserve existing
qwen3.8-27b vision configuration/context100000/one sequence/image and all GPU flags.
18021/18030/18031 were free. Candidate127.0.0.1:18031; verified-free ephemeral
loopback Gateway port. Actual PID/port ownership and cleanup must be recorded.
The external coding wrapper profile is oap-coding-luna-xhigh and was waiting on
control.fifo; no coding worker or protected run active at strategic reconciliation.

Exact acceptance client:
/synology/homes/janezp/.codex/packages/standalone/releases/0.149.0-x86_64-unknown-linux-musl/bin/codex
SHA256 bbc3341e44c9ead340ed9570c17be936e37870f570751a941699ffd04d672827.
Do not confuse the external executor version/profile with this test client.

Use only existing bounded read-only host/preflight checks, readiness and credential
procedure. Same UID/EUID1029 for producer/validator/runner/client; no whole-run sudo.
After gates, read only the exact active vision MainPID's unique nonempty
VLLM_API_KEY into bounded memory; pass via existing QWEN3090_API_KEY/Local upstream
header, discard, never print/hash/persist/expose in argv/public metadata or broaden
environment/config/credential discovery. Owned private dirs0700/files0600 and
regular/single-link/no-follow/owner checks unchanged. Existing bounded sudo Docker
helper/PostgreSQL16 loopback/tmpfs/--rm only; coding owns routine safe setup.

Unchanged limits:131072 bytes per response,900 seconds,64 observations, one active
dispatch, nine existing macro operations maximum1 each, zero retries, existing
compiler/inference/output ceilings. Only acceptance SSE-frame bound may rise,
with frame bound <=131072 and no weakening of per-response enforcement.

Allowed changes: existing observer/acceptance helper/runner, focused tests, directly
affected current docs and005-ak evidence/transcript. No src/, Gateway/PR291 or
other PR, dependencies/locks/binaries, Qwen checkout/model/checkpoint/patch/venv/unit/
launch/config/GPU/key files, services, firewall/VPN/network/public bindings, active
Codex profiles, installed deployment, release or cutover mutation. Preserve all
prior OAP artifacts and unrelated files. No raw sensitive content in artifacts.

## D. One immutable return and strategic decision

Publish source-bound005-ak evidence with closed cause enumeration/eliminations,
exact Local/Gateway/Codex authorities, focused/fake results, real result or precise
NOT RUN reason, safe first failure and size/bound, accounting/privacy limitations,
cleanup and unchanged-host evidence. Document the frame-vs-response distinction
without declaring005-aj a proven product defect or rewriting its report.

Amend PR7 only. Push all non-report work, capture literal implementationSHA,
publish exactly oap/reports/005-ak-observer-frame-bound-and-real-acceptance.md,
with Implementation head SHA and Report publication commit: SELF. Final commit
only that report, first parent literal implementationSHA. Verify remote head,
parent/path/bytes, then send exact response FIFO OK; no later mutation that round.

Clearly distinguish IMPLEMENTED, TESTED, REAL-E2E ACCEPTED, CUTOVER ACCEPTED,
MERGED and RELEASE-READY. If full real PASS, publish PASSED and return directly
for strategic final review. Human already authorizes strategic merge of PR7 if
all existing acceptance and final-head checks satisfy OAP; coding never merges.
If real FAIL, publish exact first failure and stop. No further synthetic-only or
presentation continuation. No persistent deployment/cutover/release is authorized
even after PASS/merge; strategic reports exact tested configuration and remaining
minimal operational step for human use.

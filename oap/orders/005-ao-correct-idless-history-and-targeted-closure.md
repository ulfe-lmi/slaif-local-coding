# OAP Work Order — 005-ao

## Objective / GitHub / human authority

Objective005 closure: correct the malformed identity-replay acceptance companion,
reject orphan outputs in the fake provider, qualify without protected traffic,
then perform exactly ONE targeted protected identity-replay check. NO full
protected29-row matrix, speculative diagnosis or automatic next suffix.

AMEND_EXISTING_PR; NO NEW PR; repository ulfe-lmi/slaif-local-coding, PR7
https://github.com/ulfe-lmi/slaif-local-coding/pull/7
Base/head: main / oap/005-gateway-ingress-integration.
Required starting local/remote HEAD713492fa146372be13073c10a98d8f045e71900a,
immutable005-an report; parent556ca152a589747b5c9adeca3d44de56e61ce08c;
tested005-an implementation8245f1c0270e0a314058f2afa77c9f6e80ace483.
Main570bd2b24ad4b041a07e0320d5ed44bc73e99ad5; PR OPEN/CLEAN, final test SUCCESS
34687813596/job103537785737. Strategy verified no005-ao order/report exists.

Latest human steering authorizes this continuation, a targeted check after fake
qualification, composition with accepted prior real checkpoints, then strategic
merge if satisfactory and required CI green. This changes the acceptance sequence:
do not rerun ordinary Codex/vision protected phases or demand a fresh full matrix.
Do not rewrite005-an or mark its failed/missing rows retrospectively passed.
Coding never accepts/merges. Controlled development use remains independently
authorized; deployment/public binding/service/model/network/profile mutation and
release remain prohibited. No further suffix or protected retry on failure.

## Verified exact fixture and immutable evidence

Gateway executable/merged main5ea38325ef3a3ebc69524b4679b795fab0c52935,
production732e3bad17d93909f210321b97bedd8e5718fb7b,
app treea7b64d35650b61fbba3558ddb519c6e52a627ec9,
merged tree1ede9cea41c566b141441ad9a3122133d5fc1ff6; Codex client module
codex-0.149-responses-v1 version4. Gateway PR299 merged; all ten final-report-head
checks SUCCESS. Report923270d5f776256c12855b50ba1c0978d6458c4d, parent
2c8fa51840a9ef035b52f8467a45b2faf628a7ae. No Gateway change authorized.

Reuse if still clean/exact:
- Gateway checkout /tmp/slaif-gateway-005-an.R9Lqb9 (HEAD/app independently checked).
- Task Gateway venv /tmp/slaif-gateway-venv-005-an.THUKHt (runtime + openai2.41.0).
- PostgreSQL16 image already provisioned in005-an; do not repeat failed setup.
Coding must mechanically verify dependencies and source before reuse; no version
changes. Preserve unrelated empty untracked Local, clean, unchanged in primary
repo. Use a new clean task-controlled Local worktree at the committed candidate
for fake/targeted qualification; never reset/clean or stage unrelated files.

Existing005-an bounded results are /tmp/slaif-005-an-fake-final.stdout and
/tmp/slaif-005-an-protected.stdout, with published indexoap/evidence/005-an/index.json.
Read only safe structural fields; no host session-cache discovery. Human accepts
immutable successful ordinary real Codex/tool semantics and full-image/resumed-crop
vision evidence. The actual protected result retains ordinary semantic checkpoint
and vision transport checkpoint separately; do not erase them because the final
ordered projection saysC1.1 MISSING. Preserve their exact tested SHA and scope.
Strategy review:
https://github.com/ulfe-lmi/slaif-local-coding/pull/7#issuecomment-5645273176

## A. Source/model-free harness correction FIRST

Human source review identifies a malformed stateless continuation, not evidence
of a Gateway/Local-production/Codex/Qwen product defect. Independently inspect
the exact paths before modifying:

- scripts/gateway_accounting_rehearsal.py currently constructs the protected
  companion input with only function_call_output, without prior function_call.
- _ReturnedCallIDCapture retains the canonical call ID but not the complete
  actual function call needed for legal history replay.
- _FakeQwenServer.observe_request registers output_digests when no history call
  and no pending scope exist; _matching_function_output does not itself establish
  a preceding matching call. Thus an orphan can pass a fake path.
- _run_fake_idless_http_regression currently treats the orphan shape as positive.
- _request_observation chooses output_items before function_call items for
  item_id_presence. The corrected predicate must prove omission on the actual
  preceding FUNCTION CALL, not merely an ID-less output or a missing call.

Installed vLLM0.27.1 responses/utils.py (read-only, no GPU import):
/synology/homes/janezp/qwen-serving/venv/lib/python3.12/site-packages/vllm/entrypoints/openai/responses/utils.py
SHA256577100edd0951f7f2936d2b37b7b4ec9a03d85088b35e49de6c0e9633a59adc2.
construct_chat_messages_with_tool_call / _construct_message_from_response_item
map the prior ResponseFunctionToolCall to assistant tool_calls using actual name,
arguments and call_id, and the output to a separate tool message. The function
history item is essential context; optional item id is not the call association.
The official example likewise appends response.output to input history before
the matching function_call_output:
https://developers.openai.com/api/docs/guides/function-calling

Correct the existing companion to carry, in the required order:
1. the actual validated completed function_call input item;
2. its matching function_call_output.
Omit ONLY the optional function-call item id. Preserve actual canonical returned
call_id, actual returned function name/arguments, normal completed status and
namespace/other required legal input fields. Do not assume local_lookup or{}
when replaying returned fields, use a summary-alias call ID, canonicalize empty
arguments, synthesize missing events, substitute fixtures, or change security.
The same session/owner/repository/scope/key and Gateway HMAC ownership remain
under test. History should be legal Responses input; response-only envelope
metadata is not permission to invent/strip required history semantics.

Extend the existing private bounded transient capture only as needed to carry
this actual call until the paired request finishes. Exact validator acceptance
and matching canonical replay candidate are prerequisites. Never put returned
name/arguments/IDs/item bodies in safe_facts, repr, reports, JSON evidence,
logs or persistent artifacts. Drop transient material on completion/failure.

Correct fake acceptance so outputs cannot self-register authority or satisfy
history merely because a prior HTTP call seeded pending state. Each output must
have its corresponding valid prior function_call in the same continuation
history in correct order. Remove the output-self-registration escape. Preserve
bounded current fake ownership checks and exact real-Codex behavior. Correct
the old orphan-positive HTTP regression and the existing replay-negative helpers
to derive their baseline from the real captured call rather than fixture name/
argument assumptions. Invalid variants must fail for the intended relationship.

Focused tests MUST prove: actual varied returned name/arguments preserved; optional
function-call id alone omitted; mandatory call_id preserved; preceding call and
output paired/order/status valid; old orphan rejected even after initial call,
and rejected in fresh state; mismatched/missing call-ID and wrong order rejected;
wrong key/session/ownership stays fail-closed via existing fake gates; no raw
returned content in evidence. Use current bounded helpers, no general framework.

## B. Qualification and minimal targeted execution path

Run focused tests, normal frozen unit/static/type/build/package checks and the
complete existing exact real-Codex fake37/37 gate on changed-source candidate
against exact Gateway5ea38325. Keep current fake C1-C5/D requirements intact and
actual runtime privacy projection (retained boolean, missing stays UNKNOWN/NOTRUN).
Do not reuse005-an fake as proof of this changed companion. Do not weaken the fake
gate, mark evidence passed or add unrelated synthetic variants/acceptance predicates.

Add only the minimal repository-owned entry/selector needed to run this existing
identity companion in isolation with existing setup/observer/budget/accounting/
cleanup helpers. It is not a new observer, diagnostic subsystem or matrix design.
Source/model-free tests must prove the selected protected path cannot execute
ordinary Codex, vision, other identity operations or the full29-row matrix.
The normal fake37 path continues to exercise its full existing obligations.

Keep existing numeric safety ceilings unchanged:900seconds,64observations/
dispatches,oneactive dispatch,131072 bytes per RESPONSE and frame, existing
output ceiling32 on each companion request, zero retries. The TARGET selects
only identity_replay: at most TWO Qwen inference dispatches (initial+continuation),
ZERO compiler calls. Only existing bounded readiness/health/models preflight
needed for this target may run; no unrelated inference/probes or later operations.
Narrow selection does not expand any global budget. No protected traffic during
repair/focused/fake qualification. Routine deterministic setup corrections belong
inside this same continuation, before protected traffic.

## C. Exactly ONE targeted protected identity-replay check

After full fake37 and source-bound target qualification pass, human authorizes
one fresh paired identity companion through exact Gateway -> unchanged Local
production candidate -> existing protected vision Qwen. Keep exact Codex0.149
qualification setup; the targeted SDK companion is NOT a new real-Codex run.
Reuse accepted immutable real Codex/vision checkpoints instead of rerunning them.

Require actual prior call preserved, optional call item id omitted, matching
mandatorycallID, same session/owner/scope/HMAC, both successful terminal responses
and valid detailed usage, exactly one admission/accounting lifecycle per actual
request, no pending or duplicate accounting, signed identity correctness, safe
privacy and exact owned cleanup. These are existing companion/closure predicates,
not a new matrix. Source checks and corrected fake negatives preserve the wider
replay/isolation/tamper requirements; do not silently call their protected rows.

Zero retries once ANY protected request is sent. If initial or continuation fails,
stop later dispatch and publish direct bounded failure. Retain exact status and
finite rejection reason/predicate class needed for ownership, not just the generic
stream_closure_invalid label. Use only bounded existing response handling to
classify known error codes/predicates in memory; never serialize arbitrary error
messages, event/response bodies, arguments, IDs, names, prompts, images, secrets,
signatures or exceptions. Unknown reason remains honestly unknown; no widening,
new diagnostic request or full matrix to discover it. Do not patch/retry afterward.

## D. Host / credentials / cleanup

Read-only strategic facts: user qwen-serving-vision.service active/running,
MainPID23961/UID1029, startSun2026-09-06 18:57:26CEST,zero restarts;18020 belongs
to23961,18021/18031 absent;seven pre-existing Qwen changedpaths. Preserve existing
Qwen3.8-27B vision/vLLM0.27.1/RTX3090/context100000/maxseq1/one-image service,
process/configuration/model/port/GPU/credential state before/after. No Local src/,
Gateway, dependencies/versions/lock, Qwen checkout/model/patch/venv/unit/launch,
service/network/firewall/VPN/credential/profile mutation or public binding.

Exact client:
/synology/homes/janezp/.codex/packages/standalone/releases/0.149.0-x86_64-unknown-linux-musl/bin/codex
SHA256bbc3341e44c9ead340ed9570c17be936e37870f570751a941699ffd04d672827.
Executor remains hosted OpenAI oap-coding-luna-xhigh, gpt-5.6-luna/xhigh;
wrapper1444196/reader1717829 verified waiting on control.fifo, no protected
endpoint dependency. Don't confuse coding executor with acceptance client.

Only inside the qualified target use the existing MainPID credential procedure:
unique nonempty VLLM_API_KEY from the exact active vision MainPID, bounded memory
asUID1029; no printing/hashing/persistence/argv/metadata exposure or broadened
discovery. Reuse current upstream authorization and discard promptly. Private
dirs0700/files0600, owner/no-follow/regular/single-link guards unchanged. No whole-
run sudo. Scoped PostgreSQL16 loopback/tmpfs only; Local127.0.0.1:18031 and verified-
free ephemeral loopback Gateway. Cleanup exact task runtime/database/cache/home;
truthfully distinguish reused tool/dependency/image artifacts from live runtime.
Coding owns safe setup; do not ask human or strategy to be terminal operator.

## E. Composed closure and immutable report

On target PASS, compose (do not rerun/rewrite) the human-accepted immutable real
ordinary Codex/tool and vision checkpoints with this fresh corrected identity
result and corrected full fake security/accounting/cleanup qualification. Cite
exact SHA and evidence source for each. This is acceptance by composition under
latest human authority, NOT a fresh full29-row protected PASS. Preserve limitations
and NOTRUN history. On target failure, report exact first rejection/ownership and
stop. No automatic005-ap or other continuation.

Update current-facing docs/PR description to actual cumulative production scope,
corrected companion contract and composed result. Correct stale front-facing
claims that Gateway cannot emit signed identity, preserving dated history.
This is same-round closure documentation, not another acceptance phase/order.
Provide exact reusable tested Local/Gateway/Codex/Qwen configuration and minimal
remaining manual startup steps; do not deploy, change profiles or start persistent
services. Strategy independently reviews production/package delta separately from
OAP evidence and alone mergesPR7 iff the revised human acceptance is satisfied,
exact final-head checks green and policy/security review satisfactory.

Publish exactly oap/reports/005-ao-correct-idless-history-and-targeted-closure.md.
Record literal tested Local SHA, Gateway authorities, focused/fake/target results,
one targeted attempt/two inference maximum/zero compiler/no full protected matrix,
real checkpoint provenance, accounting/privacy/cleanup/host facts and limitations.
Distinguish IMPLEMENTED, TESTED, REAL-E2E ACCEPTED BY COMPOSITION, CUTOVER ACCEPTED,
MERGED, RELEASE-READY. Coding report MERGED=NO; cutover/deployment/release NOTRUN.

Push non-report work plus exact activated order/active unchanged. Capture literal
Implementation head SHA; publish report-only SELF child with exactly that first
parent. Push and verify unique report/currentPRhead/parent/path/bytes/checks, then
send exact response FIFO OK. No later coding mutation/merge or roadmap selection.

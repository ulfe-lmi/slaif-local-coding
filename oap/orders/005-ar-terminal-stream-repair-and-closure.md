# OAP Work Order — 005-ar

## Objective and human override

Repair and close Objective005 on existing PR7, not another generic diagnostic
report. The human explicitly demanded continued work until solved, authorized
as many Qwen calls as needed, and directed using Qwen calls to determine the
cause. This supersedes005-aq's one-attempt/stop/no-successor limitation for NEW
work only.005-aq remains immutable FAILED history. Keep this one continuation
active through precise diagnosis, in-scope repair, and targeted verification.
Do not declare success from a lucky retry or stop merely with gateway_validator.

AMEND_EXISTING_PR; NO NEW PR; coding NEVER merges. Repository
ulfe-lmi/slaif-local-coding, https://github.com/ulfe-lmi/slaif-local-coding/pull/7
base main / head oap/005-gateway-ingress-integration.
Required starting HEAD285bc15042047e0b9bc67ffe25766e889e88b2ad, immutable005-aq
report-only child of implementation a94c6419f944da752e353ded1215aa1ca82ccfed.
Strategy verified exact parent/sole report path, response FIFO OK, PR OPEN,
report-head test SUCCESS34715410844/job103611644249. Main remains
570bd2b24ad4b041a07e0320d5ed44bc73e99ad5;005-ar unused locally/remotely.

Gateway executable/merged main5ea38325ef3a3ebc69524b4679b795fab0c52935;
production732e3bad17d93909f210321b97bedd8e5718fb7b;
app treea7b64d35650b61fbba3558ddb519c6e52a627ec9;
full tree1ede9cea41c566b141441ad9a3122133d5fc1ff6; Codex client module4.
Verified clean /tmp/slaif-gateway-005-ao; reuse task Gateway venv
/tmp/slaif-gateway-venv-005-an.THUKHt and existing SDK2.41.0/PG16 setup.
No Gateway modification by Local coding. No historical155 machinery.

## Established facts — do not repeat solved work

005-aq conclusively reproduced the old missing-user-history harness defect
through installed vLLM0.27.1 ResponsesRequest + OnlineRenderer + exact Qwen
template. Original user history fixes preparation; empty/object arguments,
namespace/status controls work. Preserve this repair, actual preceding call +
matching output, omission only of optional item ID, actual call_id/name/arguments/
status/legal namespace, and orphan/order/ownership rejection.

005-aq implemented bounded ORIGINAL HTTP >=400 early-close classification and
passed actual normal/cancellation/oversize regressions. Do not redesign it.
857 repository tests passed,16 skipped;237 focused passed. This was NOT857 Qwen
calls. Existing AP37 fake evidence reuse and current isolated fake target work.
Production src/dependencies remain byte-identical to accepted005-an source.

New005-aq failure was INITIAL response, NOT continuation, and NOT HTTP4xx:
direct provider HTTP200,10864 response bytes, normal close, validated canonical
call candidate available; exact validator failed at response.completed. One
protected inference,0continuations/compilers/retries; host unchanged. Generic
gateway_validator alone cannot assign owner. Private terminal status/output/usage
checks were computed but not projected by the observer. Do not invent them.
The stdout display was truncated: future SAFE result JSON must be retained
completely in an owned0700/0600 artifact before any concise terminal projection.
Never retain raw provider content. No attempt to reconstruct old missing fields.

## A. Get the precise cause using Qwen, without a new framework

Inspect exact Gateway app/slaif_gateway/providers/streaming.py:
_validate_codex_response_event around1084-1142, _validate_completed_usage,
_validate_codex_completed_output and _validate_codex_completed_output_item.
The canonical call already passed; focus on terminal response/status/usage/output/
sequence and comparison with the accepted call, not another protocol survey.

Add the SMALLEST temporary acceptance-only discriminator around the exact pinned
validator. Identify the exact finite failing return/predicate branch on the SAME
response. Do not copy/reimplement/weaken the validator or mutate Gateway. A narrow
trace of the pinned synchronous validator's known return sites, or equivalent
Gateway-helper-owned checks, may retain only closed branch labels and necessary
booleans/counts. Verify with focused synthetic positive/negative terminal cases.
No new observer, manifest/provenance framework, broad telemetry or format project.

Safe retained facts may include finite event/predicate class, terminal status
class, output item-kind classes/counts, usage-field-presence/count consistency,
sequence validity, active-item/count flags, and canonical-versus-summary name/
argument/ID equality booleans. Empty-string/empty-object/other argument classes
and bounded lengths may distinguish existing legal zero-argument branches; never
retain arbitrary argument text. No bodies/messages/output/prompts/IDs/images/
credentials/signatures/raw exceptions or payload hashes. Keep exact131072-byte
per-response/frame cap. Continue existing same-response4xx classifier if relevant.

After the focused discriminator tests, USE the existing protected Qwen through
the exact Gateway -> Local target path to observe the failure precisely. Do not
spend another long fake37 or full protected matrix before that diagnostic call.
No real ordinary Codex/vision rerun. Existing correct zero-argument helper/profile
gate and credential/host checks remain. Fix local preflight/setup failures in
this continuation before traffic instead of consuming suffixes.

## B. Repair and verify, not blind repetition

Each run is explicit, serial and bounded. No automatic HTTP/SDK retry. Stop a
failed individual request and retain its SAME-response predicate facts; then
continue this engineering round using that evidence. Additional Qwen calls are
authorized for concrete hypotheses/fixes and targeted verification, not a blind
unchanged loop. Keep an exact chronological attempt/inference/compiler count.
Normally each target run is initial+continuation, at most2inference,0compiler;
run only the initial request when diagnosing its failure. Keep per-run900s,
64observations, one-active-dispatch and current32-output-token settings. Human
expanded call count, not service/network/credential authority or response cap.

If Local harness owns a demonstrated defect, fix it here, run focused tests and
the existing isolated fake target, then verify with Qwen. Preserve identity/HMAC/
replay semantics, original history and actual returned values; no passing by
inventing events/arguments or removing the required identity-replay property.
If a Local production adaptation is genuinely required, establish source/boundary
ownership and an explicit existing route-scoped semantic-equivalence rationale;
never hide that adaptation in tests. Product code changes require appropriate
production regressions and existing fake37 gate before their protected acceptance.

If exact merged Gateway or provider owns the defect, publish a precise bounded
source/event handoff and notify strategy through PR7 and the immutable report
when that is the genuine external ownership stopping point. Do not patch Gateway,
Qwen or security policy yourself. Strategy will coordinate resolution rather than
recruiting the human to debug/run terminals. Do not claim a product defect solely
because validation failed. If calls pass intermittently, investigate the observed
terminal branch rather than declaring the prior failure solved by one success.

Reuse accepted unchanged-source qualifications. Extend only the existing exact
harness-reuse allowlist for this order/report/test paths as needed; don't forge
old evidence or force a full fake37 rerun for order/report/observer-only changes.
Avoid qualification machinery that takes longer than the concrete repair.

## C. Protected host and credentials — unchanged

Vision USER unit qwen-serving-vision.service is active/running, PID23961 UID1029,
startSun2026-09-06 18:57:26CEST,NRestarts0. TEXT qwen-serving.service is correctly
inactive. Existing18020 listener,18021/18031 absent after cleanup; seven Qwen
pre-existing changed paths. Preserve Qwen3.8-27B vision/vLLM0.27.1/RTX3090/
context100000/maxseq1/one-image/model/weights/venv/units/launch/config/GPU state.
No service,model,network,firewall,VPN,key/profile mutation or public bind.

Exact acceptance Codex0.149:
/synology/homes/janezp/.codex/packages/standalone/releases/0.149.0-x86_64-unknown-linux-musl/bin/codex
SHA256bbc3341e44c9ead340ed9570c17be936e37870f570751a941699ffd04d672827.
Coding stays hosted OpenAI oap-coding-luna-xhigh, gpt-5.6-luna/xhigh; do not alter
either agent's active profile. Preserve empty untracked Local, clean, unchanged.

Only established in-memory VLLM_API_KEY acquisition from the exact active vision
MainPID environ; never print/hash/persist/argv/expose/broaden discovery. No whole-
run sudo. Existing0700/0600/owner/no-follow/regular/single-link safeguards. Temporary
PG16 loopback/tmpfs, Local127.0.0.1:18031, verified-free ephemeral loopback Gateway,
owned cleanup only. No deployment, cutover or release. Coding owns routine setup.

## D. Closure and publication

Require successful real targeted initial+ID-less continuation, exact signing/
ownership, valid terminal lifecycles/usage, reservation AND ledger finalization,
zero pending/duplicates, actual privacy scan and exact cleanup/host preservation.
Compose with accepted Local005-an real Codex/tool and vision checkpoints:
report713492fa146372be13073c10a98d8f045e71900a,
parent556ca152a589747b5c9adeca3d44de56e61ce08c,
tested8245f1c0270e0a314058f2afa77c9f6e80ace483. No full29 matrix claim.

Update PR7 description to exact outcome; no proof-format-only continuation.
Publish ONE oap/reports/005-ar-terminal-stream-repair-and-closure.md at resolved
closure or a precise genuine cross-owner blocker, with exact source pins, finite
cause/ownership/fix, actual attempts, safe artifact references, qualifiers,
accounting/privacy/cleanup/host facts and remaining limitations. Preserve prior
immutable artifacts. Distinguish IMPLEMENTED/TESTED/REAL-E2E/CUTOVER/MERGED/
RELEASE-READY. Do not end with only an unexplained generic validator label.

Push exact order/active and all non-report work. Literal implementation SHA plus
one report-only SELF child, verify remote parent/path/bytes, exact response FIFO
OK, then no further mutation. Strategy alone reviews exact final-head CI/product/
package/security and mergesPR7 under standing human authority when fully satisfied.
No deployment/release. Strategy continues cross-owner coordination if necessary;
coding never selects a successor or merges.

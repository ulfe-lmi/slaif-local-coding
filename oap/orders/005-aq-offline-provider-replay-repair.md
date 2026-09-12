# OAP Work Order — 005-aq

## Objective, authority and GitHub state

Objective 005 engineering repair: determine the exact offline provider rejection
path, fix its actual owner, prove bounded same-response error capture, and ONLY
then run one targeted identity pair. This is not an acceptance experiment or a
new diagnostic framework. Human steering for this round overrides the prior
005-ap stop concerning activation; 005-ap itself remains immutable BLOCKED.

AMEND_EXISTING_PR; NO NEW PR; coding NEVER merges or chooses another suffix.
Repository ulfe-lmi/slaif-local-coding, PR7:
https://github.com/ulfe-lmi/slaif-local-coding/pull/7
Base main / head oap/005-gateway-ingress-integration.
Required starting HEAD: 8a6e6551c0effc46e1eac135be9bd2ccf1e9b62a;
005-ap implementation parent: 91be1d73eddb64b65910de2fd15dfdf8309ad6c8;
qualified source: 934388057af267b3bf39b2a2d1b56d34dfbd042f.
Main: 570bd2b24ad4b041a07e0320d5ed44bc73e99ad5.
Strategy verified PR OPEN/CLEAN, test SUCCESS run34705217872/job103583942179,
no auto-merge, 005-aq absent locally and in remote tree. Preserve empty untracked
Local, clean, unchanged; never stage/delete them. Preserve all prior OAP artifacts.

Exact Gateway executable AND merged-main pin:
5ea38325ef3a3ebc69524b4679b795fab0c52935;
production 732e3bad17d93909f210321b97bedd8e5718fb7b;
app tree a7b64d35650b61fbba3558ddb519c6e52a627ec9;
full tree 1ede9cea41c566b141441ad9a3122133d5fc1ff6;
codex-0.149-responses-v1 module version4. Strategy reconciled handback comment
5641947089, current main, clean /tmp/slaif-gateway-005-ao and successful checks.
Reuse /tmp/slaif-gateway-venv-005-an.THUKHt after validation; SDK openai2.41.0,
temporary PostgreSQL16. No Gateway change, branch-name authority or155 machinery.

## A. Mandatory offline diagnosis — ZERO protected traffic/credentials

005-ap does not identify a product owner. Original Qwen error was lost: Local's
production HTTP >=400 path closes its upstream response without reading it and
returns a sanitized error. The injected acceptance observer therefore saw no
original error bytes; downstream public SSE is not the original provider reason.
Do not claim to recover those bytes or reconstruct that historical response.

Use exact installed vLLM0.27.1 source and its actual request preparation/rendering
path, with synthetic IDs/content and NO GPU/model generation. Installed source:
/synology/homes/janezp/qwen-serving/venv/lib/python3.12/site-packages/vllm/entrypoints/openai/responses/
protocol.py SHA256 6aeabf69dbc924b238172b505730a8a8321b50a819891d2a72a690963c970fba
utils.py SHA256 577100edd0951f7f2936d2b37b7b4ec9a03d85088b35e49de6c0e9633a59adc2
serving.py SHA256 628429902ff26b87f86eae1a45297f647f3712d7b421ca9a4866a3fd0f046a5b

Begin with vLLM's own test_multiturn_tool_calling known-good ID-less preceding
function_call + matching function_call_output. Optional item ID is not presumed
required. Locate the version-matched upstream test if not installed; use primary
upstream source only. Do not substitute a locally rewritten parser for vLLM.
Exercise actual ResponsesRequest parsing, conversion to chat messages, and the
actual Qwen template/tokenizer/request-rendering preparation before generation.
Read only required tokenizer/template metadata, never weights, protected logs or
credentials. Use isolated CPU-only/no-GPU child execution, no engine or duplicate
model, no downloads/model writes, no installed-provider mutation. Import/setup
is coding-owned; distinguish blocked imports from a provider rejection. A mock
of the rejecting parser/template is NOT proof; mocks may only isolate generation
or unrelated setup. Retain source pins, stages and safe finite results, not prompts
or rendered content. No raw/free-form exceptions in reports/logs.

Minimal one-variable differentials, same remaining request:
- arguments="{}" versus arguments="";
- namespace omitted versus null versus legal non-null namespace;
- status omitted versus completed;
- upstream known-good ID-less call+output versus current replay serialization;
- exact current zero-argument declaration/request versus known-good nonzero control.

Trace both the actual existing Gateway/Local request transforms and provider
preparation. Use the exact current _idless_companion_continuation_body and capture
field-selection path with synthetic validated returned items, not a convenient
hand-written approximation. If historical argument/namespace values were not
retained, say so; enumerate those source-permitted cases without inventing values.
Identify deterministic stage/exception predicate and show the corrected request
passes the SAME installed preparation path. Merely passing Pydantic while skipping
the rendering branch is insufficient. No protected inference may be used to decide
between remaining hypotheses. If offline evidence cannot identify a cause, stop
with precise unresolved stage and ZERO protected requests, not a blind attempt.

## B. Fix the demonstrated owner, not the test result

Harness-only optional-field serialization defect: correct precisely that invalid
representation while preserving semantic content and actual returned fields.
Provider output that its own input/rendering path cannot replay: establish the
round-trip incompatibility; do not hide an argument rewrite in the companion.
The human authorizes a narrow Local-to-Qwen production compatibility adaptation
for that demonstrated case. Conditional strategic boundary: only explicit existing
Qwen route policy, only proven semantically equivalent representation, after
Gateway authorization/signature/body verification, with original ownership and
mandatory call-ID intact. No generic JSON repair, event synthesis, invented
arguments, widened tool authority or changed replay/HMAC policy. If a precise
safe adaptation cannot meet these constraints, publish a concrete provider or
cross-repository handoff instead of guessing. Report the ownership decision and
exact source predicate prominently before any protected execution.

Keep zero-argument local_lookup schema object/properties{}/additionalProperties=false,
no nonempty required set, prompt requesting no arguments. Keep the hard exact
Gateway helper/profile eligibility gate and private checked-request byte binding
BEFORE protected credential resolution. Exact helper must equal
frozenset({"local_lookup"}); exact validator profile must match. The continuation
contains validated preceding call then matching output, omits only optional item
ID except any source-proven optional serialization correction, preserves returned
call_id/name/arguments/status/legal namespace transiently. No orphan self-authority.

## C. Same-response 4xx classifier — required BEFORE protected eligibility

Implement the smallest bounded classifier in the EXISTING acceptance transport
path. It must see the ORIGINAL provider HTTP error before Local closes/sanitizes
it. Reading only the downstream Gateway error is insufficient. Bound transient
error-body consumption by existing 131072-byte per-response cap/time/cancellation
law; never buffer successful SSE responses or change production public errors
merely to expose diagnostics. Count every consumed byte exactly once.

Retain exact HTTP status and finite allowlisted provider error type/code/param
classes, including the actual installed vLLM error-envelope forms and explicit
null/missing distinctions. Do not map all real provider error types to "unknown".
Unknown values must remain a finite unrecognized class, never copied verbatim.
Never retain raw message/body, arguments, IDs, prompts, credentials, images or
output. Unit-test the actual app >=400 immediate-close path with a streamed
synthetic provider response and verify facts survive close/sanitization and reach
the final target result. Include source-known vLLM errors, unexpected field values,
malformed/oversized response, cancellation/cleanup, privacy sentinels and unchanged
per-response accounting. No general observer/provenance subsystem.

## D. Proportionate qualification and conditional one protected pair

Harness-only changes: focused tests, exact installed provider differential and
existing isolated fake identity target qualification. Reuse accepted production,
ordinary Codex/vision and existing full fake evidence; no full fake37 rerun merely
for harness serialization/order/report changes. If execution-relevant product code
changes, run relevant production regressions and existing complete real-Codex
fake37 gate at that candidate. No new acceptance predicates or synthetic variants.
Run normal static/type/unit/build/package/CI checks; use clean candidate worktree,
not unrelated primary dirt. State exact tested SHA and source reuse accurately.

Protect execution with a real preflight gate: offline known-good/control/differential
cause established, corrected provider preparation passed, bounded classifier actual
early-close regression passed, required focused/fake qualification passed and exact
zero-argument helper/profile/request binding passed. Failure means no credential
resolution or protected traffic. Do not synthesize proof booleans.

ONLY after all those conditions: exactly ONE fresh targeted identity pair against
exact Gateway -> Local candidate -> unchanged Qwen, at most TWO Qwen inference
requests, ZERO compiler requests, ZERO retries. Initial request is exact eligible
request; second only after first passes and yields validated actual call. No full29
matrix, ordinary real Codex or vision rerun, later acceptance operations or extra
diagnostic request. Existing bounded necessary readiness only after eligibility.
Preserve existing 900s/64observations/one-active-dispatch/32-output-token and
131072-byte PER RESPONSE + frame ceilings. Accept any Gateway162-legal lifecycle.
Keep existing pair signing/replay ownership, stream terminals/usage, reservation
AND ledger counts/finalization, zero pending/duplicates, actual runtime privacy scan
before cleanup, exact owned cleanup and protected-host preservation predicates.
Use actual dispatch budget and unique records, not duplicated lifetime aggregates.

If either protected request fails: NO additional request, no post-failure runtime
repair/requalification/retry. Preserve first direct bounded status/type/code/param
facts from that SAME response and publish. No automatic005-ar. Do not infer owner
from a generic status or promise an arbitrary provider supplies detailed fields.

## E. Host and execution safety

Strategy verified vision user unit active/running, PID23961, UID1029, start
Sun2026-09-06 18:57:26CEST, NRestarts0, existing18020 listener,18021/18031 absent,
seven existing Qwen changed paths. Preserve Qwen3.8-27B vision/vLLM0.27.1/
RTX3090/context100000/maxseq1/one-image and all model/config/process/GPU state.
No Qwen checkout/venv/patch/model/unit/service/launch/profile mutation, no Gateway,
network/firewall/VPN/port18020/key change, public bind, deployment/cutover/release.

Coding profile remains hosted OpenAI oap-coding-luna-xhigh, gpt-5.6-luna/xhigh.
Sole current control reader1843221 belongs to wrapper1843202. No profile/model
change. Exact acceptance Codex0.149 remains
/synology/homes/janezp/.codex/packages/standalone/releases/0.149.0-x86_64-unknown-linux-musl/bin/codex
SHA256 bbc3341e44c9ead340ed9570c17be936e37870f570751a941699ffd04d672827.

Only after all gates, existing in-memory credential procedure: unique nonempty
VLLM_API_KEY from active vision MainPID environ, UID1029. Never print/hash/persist/
argv/expose or broaden discovery. Existing0700dirs/0600files/owner/no-follow/
regular/single-link guards; no whole-run sudo. Temporary PG16 loopback/tmpfs,
Local127.0.0.1:18031, free ephemeral loopback Gateway, owned cleanup only.
Coding owns safe routine setup and commits; strategy reviews, does not implement.

## F. Immutable closure and strategic merge

PASS pair composes with human-accepted Local005-an ordinary real Codex/tool and
full-image/resumed-crop checkpoints, not an invented newly executed full matrix:
report713492fa146372be13073c10a98d8f045e71900a;
parent556ca152a589747b5c9adeca3d44de56e61ce08c;
tested Local8245f1c0270e0a314058f2afa77c9f6e80ace483.
Do not use erroneous005-ao Gateway SHAs as Local evidence. If production changes,
mechanically bound their applicability when composing prior real checkpoints;
no claim that unchanged historical evidence tested new behavior.

Update PR7 description and narrowly affected docs to actual scope/state. Publish
exactly oap/reports/005-aq-offline-provider-replay-repair.md: source-pinned offline
differential/stages/ownership/fix, qualifier results, protected NOT RUN reason or
exact pair result/counts, classifier/accounting/privacy/cleanup/host evidence,
exact Local/Gateway/Codex/Qwen state and prior Local checkpoint references.
Distinguish IMPLEMENTED, TESTED, REAL-E2E ACCEPTED BY COMPOSITION, CUTOVER ACCEPTED,
MERGED, RELEASE-READY. No deployment/cutover/release; coding never accepts/merges.

Commit/push exact active/order plus all non-report work; capture literal
Implementation head SHA. One report-only SELF child with that exact first parent;
verify remote head/path/bytes, send exact response FIFO OK, then stop mutation.
Strategy independently verifies report, production/package delta separately from
OAP, exact final-head checks and all merge criteria. If satisfactory PASS and all
CI green, strategy merges PR7 immediately under human authority, verifies remote
main, and reports exact usable configuration/minimal remaining operational step.
On failure stop, no automatic successor or release. Controlled development use
remains independently authorized; no new persistent services are authorized.

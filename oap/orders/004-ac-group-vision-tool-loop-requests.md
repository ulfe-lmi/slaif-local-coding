# OAP Work Order — 004-ac

## Objective

Amend objective-004 PR #6 only to make the prepared live vision acceptance
harness model the proven multi-request Codex tool lifecycle. Group every actual
adapter outbound Responses request by Codex invocation and validate full-image
then newest-crop behavior across all requests. Do not run live vision or change
Local Coding production code.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`.
- Numeric objective / round: `004` / `004-ac`, a human-authorized post-`z`
  continuation on the same objective branch/PR.
- PR mode: `AMEND_EXISTING_PR`; **NO NEW PR**.
- Existing PR: #6, `https://github.com/ulfe-lmi/slaif-local-coding/pull/6`.
- Base/head: `main` at `7a2c36a0a40958a6059a765c2f9d5e5bf4ddc161` /
  `oap/004-real-codex-governed-e2e`.
- Current verified remote head / 004-ab SELF:
  `0dc07bc808ab22f9d47fd7e28048d828f6be8f73`.
- 004-ab implementation parent:
  `28b21112e371e0703cba4cd8177a65b40c56fe6d`.
- PR OPEN, non-draft, MERGEABLE/CLEAN; report-head `test` SUCCESS.
- Same PR only; coding never merges or enables auto-merge.

## Accepted state and exact remaining defect

Accept 004-ab's `VisionOutboundRecorder` placement: it now sees the actual
post-transform HTTPX request emitted by production `create_app`, records safe
facts, and forwards the same request object. Do not replace or broaden that
boundary.

The remaining harness assumption is wrong. `run_vision_e2e` currently treats
all recorder facts as exactly two requests, one per Codex invocation, and
`VisionMetricDeltas.exact` hard-codes `1/0` then `2/1`. But accepted real-Codex
004-s evidence proves the ordinary required tool lifecycle creates two main
Responses requests per invocation: first invocation ended at injected requests
2 and second at 4. The vision prompt also requires one shell read, so a valid
vision run is expected to contain multiple main requests in each invocation.

As written, `len(outbound_facts) == 2` and fixed single-request metrics would
reject correct Local Coding/Codex behavior. Correct this test-harness defect
before asking the human to switch the protected service.

## Requirements

### A. Explicit invocation phases

Add a bounded recorder phase API or equivalent direct mechanism so
`run_vision_e2e` marks/snapshots:

1. facts before invocation 1;
2. all main `/v1/responses` requests emitted during invocation 1;
3. facts before invocation 2;
4. all main `/v1/responses` requests emitted during invocation 2.

Do not infer phases from request count or assume two calls. Compiler Chat calls
remain ignored. Reject a main request outside an active phase, overlapping
phases, reordered phases, an empty phase, unbounded request count, or facts
that cannot be attributed exactly. Store only existing safe fact fields plus a
fixed invocation label.

Set a small finite maximum of main Responses requests per invocation consistent
with `VISION_MAX_TOOL_CALLS`; exceeding it fails acceptance.

### B. Per-invocation outbound acceptance

Require one or more recorded main requests in each invocation and require
**every** recorded request to pass:

- invocation 1: exactly one supported `input_image`, expected `full_scene`
  hash/length, no crop or unknown image;
- invocation 2: exactly one supported `input_image`, expected `right_crop`
  hash/length, no retained full or unknown image;
- safe governance/tool/non-image presence/preservation facts required where
  applicable;
- no raw payload/image/data URL/session/credential retention.

Acceptance must not pass because only the first or last request in a phase is
correct while another request violates the one-image/newest-crop policy.

### C. Scale metrics to actual main-request counts

Replace the fixed one-request metric predicate with an invariant based on the
directly recorded phase counts:

- let `n1` be invocation-1 main request count: seen delta must be `n1`, removed
  delta `0`;
- let `n2` be invocation-2 main request count: seen delta must be `2*n2`,
  removed delta `n2`;
- `n1` and `n2` must each be within the finite allowed range.

This proves each turn-1 request arrived with one full image and each turn-2
request arrived with retained full plus new crop, while the actual outbound
recorder proves Local Coding forwarded only the correct single image.

If actual Codex 0.149.0 uses a demonstrably different image-history shape, the
future live run must report that direct external fact rather than weaken the
newest-image acceptance claim. This preparation round uses fake/modelled
requests only and makes no live claim.

### D. Tests and docs

Focused tests must run the real app/recorder path with at least two main
requests per logical invocation and prove:

- correct grouping and ordered full/crop facts across all requests;
- scaled metric predicate;
- rejection of empty, missing, overlapping, out-of-phase, excessive,
  interleaved/reordered, and partially invalid groups;
- same-session and exact final-binding gates remain strict;
- the future human-gated function invokes the phase API around the real Codex
  subprocesses and requires grouped outbound success.

Update `docs/VISION-ACCEPTANCE.md` to state that tool loops may produce multiple
main requests, every request is checked, and metrics scale by observed phase
counts. Leave completeness at 90%, with live vision the sole remaining gap.

## Non-goals and safety

- No live vision request and no protected service switch.
- No production source/config/API/log/metric behavior change.
- No compiler/cache/rehydration/compaction/sandbox/environment/gateway/cutover
  work.
- No protected Qwen/unit/launcher/config/model/key/profile/network/firewall/VPN
  mutation; current text remains active on 18020, vision inactive.
- No general proxy/diagnostic subsystem; repository-only acceptance support,
  excluded from wheel.
- No raw prompt/source/image/tool output/body/model response/session ID/data URL/
  credential in Git, evidence, logs, metrics, or report.

## Acceptance criteria

1. Recorder facts are grouped directly around each real runner invocation, with
   finite bounds and strict phase errors.
2. Every actual outbound fake-upstream app request in phase 1 is full-only and
   every request in phase 2 crop-only; partial correctness cannot pass.
3. Metrics are validated against `n1`/`n2`, not fixed at one request per turn.
4. Focused negative tests cover lifecycle/group/count/partial-invalid cases.
5. The future live test requires grouped outbound, scaled metrics, exact final
   binding, exact resumed session, successful model lifecycle, privacy, and
   cleanup.
6. No production/protected change; frozen gates, Ruff, mypy src+tests,
   focused/full pytest, build, wheel boundary, compileall, shell syntax,
   diff/secret/raw-content scans and current GitHub CI pass.
7. Ports 18021/18031 absent after tests; protected text active and vision
   inactive; same PR only; no merge.

## Stop rule

If correct grouping requires weakening the real Codex lifecycle, image policy,
or privacy boundary, stop with the exact harness blocker. Do not ask the human
to switch vision. If all criteria pass, report COMPLETE for preparation only;
Objective 004 remains pending solely on the human-gated live vision run.

## Publication contract

Push the exact activated order/active and bounded repository-only test/docs
changes to the existing PR. Push all non-report work first and record its
literal 40-hex SHA. Publish exactly one immutable
`oap/reports/004-ac-group-vision-tool-loop-requests.md` with literal
implementation SHA and `Report publication commit: SELF`. SELF must be the sole
final commit, change only that report, have the implementation SHA as first
parent, and be remote PR head before response FIFO `OK`.

# OAP Work Order — 004-ab

## Objective

Amend objective-004 PR #6 only to make the already-prepared human-gated vision
acceptance test observe and validate the body actually leaving the candidate
Local Coding adapter. Replace the current handcrafted recorder proof with an
acceptance-only transport wired into the real candidate path. Do not run live
vision, change Local Coding product behavior, or revisit compaction/environment
work.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`.
- Numeric objective / round: `004` / `004-ab`.
- Human-authorized post-`z` continuation; same objective, branch, and PR.
- PR mode: `AMEND_EXISTING_PR`; **NO NEW PR**.
- Existing PR: #6, `https://github.com/ulfe-lmi/slaif-local-coding/pull/6`.
- Base/head: `main` at `7a2c36a0a40958a6059a765c2f9d5e5bf4ddc161` /
  `oap/004-real-codex-governed-e2e`.
- Current verified remote head / 004-aa SELF:
  `60e6204067f9e6f4f0cadd1fac8cdbd3536f9dab`.
- 004-aa implementation parent:
  `899d589ec771539a098a86a6ad3f10ec4736d153`.
- PR OPEN, non-draft, MERGEABLE/CLEAN; report-head `test` SUCCESS.
- Same PR only; coding never merges or enables auto-merge.

## Accepted state

Strategic review accepts 004-aa's canonical simulated-compaction evidence and
the non-vision Objective-004 ledger: the stateless follow-up omitted prior
governance/sentinel material, hit and injected bounded rehydration state,
preserved the hidden binding sentinel, and added zero compiler-model attempts.
Do not repeat or reopen that live proof. The compiler exact-literal correction
is accepted as the one concrete Local Coding defect found and fixed in 004-aa.

Live vision remains not run and is the sole external criterion once this
prepared-test defect is corrected.

## Exact review defect

`capture_outgoing_vision_payload` currently compares caller-supplied `incoming`
and `outgoing` mappings. Its focused test manually constructs and manually
prunes those mappings. The human-gated live test instead launches the ordinary
adapter subprocess and never wires that recorder into the adapter's actual
upstream transport. Metrics prove `seen/removed` counts but do not prove which
image/modality/body actually left the adapter.

Therefore 004-aa's statement that the future live test verifies the actual
upstream request shape is not yet true. Correct the test harness, not production
Local Coding.

## Requirements

### A. Wire an acceptance-only outbound transport recorder

Within repository-only test support, construct the candidate adapter through
the production `create_app`/settings path with an acceptance-only HTTPX
transport wrapper (or an equivalently direct, bounded mechanism). The wrapper
must receive the exact request object/body after Local Coding's image policy,
constitution pipeline, and serialization, record only safe facts, and forward
the request unchanged to its configured upstream.

The live test must use this wired candidate path. It must not merely call a
recorder helper afterward, infer the outbound body from metrics, parse logs,
capture packets, add a public debug header, or alter production telemetry.

Record only, per main Responses image turn:

- endpoint and sequential turn number as fixed labels;
- exact supported image-item count and type (`input_image`/`image_url`);
- expected fixture label match (`full_scene` or `right_crop`), byte length, and
  SHA-256;
- fixed booleans for exactly one expected image and no unexpected image;
- no raw body, base64/data URL, prompt, source, tool output, response, auth, URL
  query, session ID, credential, or arbitrary filename.

Compiler requests may pass through the same transport but must not be mistaken
for main image turns or expose their bodies.

### B. Prove wiring through the real adapter transform

Replace the handcrafted fake proof with a focused test that:

1. starts/uses the actual `create_app` transformation path with fake upstream;
2. posts turn 1 containing one full image and turn 2 containing retained full
   history plus the crop;
3. obtains recorder facts only from the transport request actually emitted by
   that app;
4. proves outbound turn 1 is exactly the full image and outbound turn 2 is
   exactly the newest crop;
5. proves the actual outbound body preserves expected non-image, tool, and
   governance content through safe boolean assertions;
6. proves image metrics are turn 1 seen/removed `1/0` and turn 2 `2/1`;
7. rejects zero, duplicate, unknown, wrong-order, wrong-type, or mismatched
   image evidence.

Do not retain a second manually-pruned structure as the claimed acceptance
proof.

### C. Make the future live gate require outbound facts

The human-gated real Codex `exec --image full` then same-session
`exec resume --image crop` test must run the same wired recorder/candidate and
fail unless all are true:

- Codex-under-test 0.149.0 itself uses the human-approved global yolo mode;
- both bounded Codex/model turns succeed through Local Coding;
- first actual outbound main request contains exactly one expected full image;
- second actual outbound main request contains exactly one expected crop image,
  not the retained full image;
- actual item type/modality is supported and expected;
- Local Coding metrics independently show incoming turn deltas `1/0` then
  `2/1` for seen/removed;
- governance observation/injection and exact hidden binding response remain
  effective;
- both invocations belong to the persisted/resumed session by direct event or
  command/session evidence, without accepting an ambiguous unrelated session;
- recorder facts, candidate logs, normalized results, and report-safe output
  contain no raw sensitive content.

Strengthen final binding validation if necessary so substring presence cannot
pass when the delegated exact-response rule was violated. Do not make visual
quality/benchmark claims; successful protected image processing plus exact
outbound shape is sufficient.

### D. Documentation and human gate

Correct `docs/VISION-ACCEPTANCE.md` and any test/result wording so it states
precisely what fake readiness proves and what the later live run will prove.
Do not claim a live image result now. Leave completeness at 90% with live vision
as the sole gap if all preparation passes.

The already verified protected contract remains unchanged:
`qwen-serving-vision.service`, mutually exclusive with the active text unit,
model `qwen3.8-27b`, protected `127.0.0.1:18020/v1`, one image per request,
Responses `input_image`, context 100000. Human owns the service switch and
rollback. Coding must not start, stop, enable, reload, edit, or restore either
protected unit.

## Non-goals and safety

- No live vision request in this round.
- No Local Coding production source/config/API/log/metric behavior change.
- No compiler, cache, rehydration, compaction, sandbox, Codex environment, raw
  bubblewrap, gateway, cutover, systemd, model, network, or profile work.
- No protected 18020/Qwen/unit/launcher/config/key/firewall/VPN mutation.
- No durable general diagnostic/proxy subsystem; repository-only acceptance
  transport support only, excluded from the wheel.
- No secret, raw prompt/source/image/tool output/body/model response/session ID,
  data URL, or customer content in Git, output, logs, metrics, or report.

## Acceptance criteria

1. Focused tests prove the recorder is invoked by the actual app's outbound
   transport after transformation, not by manually supplied outgoing data.
2. Actual fake-upstream app requests prove full then newest-crop forwarding,
   expected supported type/hash/length, preserved non-image/tool/governance
   content, exact metrics, and negative rejection cases.
3. The human-gated live test itself is wired to and requires those outbound
   recorder facts plus exact binding/session/cleanup gates.
4. No production module or protected service/profile/network state changes.
5. Frozen dependencies; Ruff; mypy; focused/full pytest; build; wheel/sdist
   boundary; compileall; shell syntax; diff/secret/raw-content scans pass.
6. Candidate/test temporary state is absent after focused tests; ports 18021 and
   18031 absent; protected text remains active and vision inactive.
7. Current remote report-head CI is green, same PR only, no merge.

## Stop rule

If the actual outbound recorder cannot be wired faithfully without product or
protected-host changes, stop with the exact test-harness blocker. Do not invent
weaker evidence. If all criteria pass, report COMPLETE for preparation only;
Objective 004 remains pending solely on the human-gated live vision run.

## Publication contract

Push the exact activated order/active and bounded repository-only test support
to the existing PR branch. Push all non-report work first and record its literal
40-hex SHA. Publish exactly one immutable
`oap/reports/004-ab-wire-live-vision-outbound-evidence.md` with literal
implementation SHA and `Report publication commit: SELF`. SELF must be the sole
final commit, change only that report, have the implementation SHA as first
parent, and be remote PR head before response FIFO `OK`.

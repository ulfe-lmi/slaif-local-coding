# OAP Work Order — 004-ae

## Objective

Correct one concrete acceptance-harness contradiction exposed by the single
004-ad live run, then execute exactly one corrected live vision acceptance
attempt against the still-selected protected vision fixture. Remove the
prompt-supplied intermediate image marker; keep strict hidden-governance final
binding, actual outbound image evidence, lifecycle bounds, and the existing
four-main-request cap. Do not change Local Coding production code or inflate
the cap to make the test pass.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`.
- Numeric objective / round: `004` / `004-ae`, human-authorized continuation
  after `004-z` on the same objective branch/PR.
- PR mode: `AMEND_EXISTING_PR`; **NO NEW PR**.
- PR #6: `https://github.com/ulfe-lmi/slaif-local-coding/pull/6`.
- Base/head: `main` at `7a2c36a0a40958a6059a765c2f9d5e5bf4ddc161` /
  `oap/004-real-codex-governed-e2e`.
- Current verified remote head / 004-ad SELF:
  `4a9de06ca59f4c5a828d48e9710d5a596ee57aaa`.
- 004-ad implementation parent:
  `cbac2b3b2733f630cde334345a52b798cb44f09f`.
- PR OPEN, non-draft, MERGEABLE/CLEAN; current report-head `test` SUCCESS.
- Same PR only; coding never merges or enables auto-merge.

## Verified failure and fault localization

004-ad ran the prepared live test exactly once and truthfully stopped at
`vision_phase_request_bound_exceeded`: phase 2 attempted a fifth main Responses
request, beyond the finite cap of four. No final session facts were returned,
so 004-ad did not establish a Local Coding image/governance failure.

Safe protected access-log counts show the candidate forwarded eight main
Responses requests and two compiler Chat requests before the blocked fifth
phase-2 main request. Temporary raw events were correctly deleted and must not
be reconstructed or exposed.

Source review identifies a concrete harness contradiction in `_vision_prompt`:

1. it requires an intermediate `FULL-SCENE-PROCESSED` or `CROP-PROCESSED`
   `agent_message`;
2. it then requires the delegated dependency's different
   `FINAL_RESPONSE_EXACTLY` sentinel as the final assistant response.

In Codex's ordinary tool loop, a tool-free assistant/agent message terminates
the invocation; it is not a separate pre-final channel. Asking for two distinct
terminal messages can drive extra continuation attempts. The marker is also
prompt-supplied and therefore cannot prove that the protected model processed
the image.

The architecture's vision property is instead proven by the acceptance-only
recorder observing the exact post-transform image bytes/types/counts actually
sent upstream, the upstream accepting those requests, and both Codex/model
lifecycles completing while governance remains binding.

## A. Narrow harness correction

In repository-only vision support/tests/docs:

- remove the `FULL-SCENE-PROCESSED` / `CROP-PROCESSED` instruction from both
  prompts;
- remove `image_marker_passed` and marker event parsing from acceptance facts
  and success predicates, rather than leaving dead/optional compatibility;
- keep the prompt requirement to perform the ordinary delegated dependency read
  and then obey its `FINAL_RESPONSE_EXACTLY` rule;
- keep exact output-last-message byte equality with the hidden sentinel;
- keep direct matching nonempty resumed thread/session ID;
- keep actual outbound recorder facts for every main request, full-only phase 1
  and crop-only phase 2;
- keep scaled metrics, privacy, cleanup, and all negative phase tests;
- keep `VISION_MAX_MAIN_REQUESTS_PER_INVOCATION = 4` unchanged;
- do not loosen command/tool-call bounds or accept substring sentinel matches.

Update documentation to state that no prompt-supplied marker is used and that
successful protected image processing is established by exact outbound image
identity/count plus successful upstream/Codex lifecycle, not visual-quality
benchmarking.

Add focused tests proving prompts contain neither marker, result facts have no
marker field, exact hidden final binding remains mandatory, and a marker-only
or marker-plus-sentinel non-exact output cannot pass.

## B. Protected vision fixture

The human explicitly directed that the vision-enabled model remain running.
During the attempted strategic rollback, the vision stop had already begun;
strategy immediately restarted only `qwen-serving-vision.service` and did not
start the text unit. Coding must wait read-only until:

- `qwen-serving-vision.service` is active/running with zero restarts;
- text unit remains inactive;
- port 18020 listens and 18031 is free;
- authenticated health/models return 200;
- model is `qwen3.8-27b`, `max_model_len=100000`;
- launch still has vision enabled and one-image limit.

Do not stop/start/restart/reload/edit/enable/disable either protected unit.
Leave vision running after the round, regardless of result.

## C. Exactly one corrected live attempt

After focused correction tests and fixture readiness, run exactly once:

```bash
SLAIF_VISION_ACCEPTANCE=1 uv run --frozen pytest -q tests/test_vision_e2e.py -k live_vision_exec_resume_acceptance
```

No preliminary real Codex image run, retry, alternate prompt, cap change, or
post-failure mutation is permitted.

On success, sanitized evidence must prove:

1. Codex 0.149.0, global yolo before `exec`, persistent disposable session,
   full image then same-session crop, context 100000 and low reasoning;
2. both subprocesses exit 0 within bounds and expose identical nonempty thread
   IDs;
3. both output-last-message files equal the hidden delegated sentinel exactly;
4. phase counts are each 1..4 and every phase-1 outbound main request is exactly
   the expected full `input_image` while every phase-2 request is exactly the
   expected crop, never the retained full;
5. metrics equal `(n1,0)` and `(2*n2,n2)` for observed phase counts;
6. compiler/main upstream calls succeed, governance observation/acquisition/
   compile/injection remains effective, and no unsafe bypass occurs;
7. candidate/temp cleanup, privacy, and protected-service immutability pass.

If the corrected run fails, stop at the first direct failure with no retry or
change. Do not characterize a harness/lifecycle failure as a Local Coding
product defect without direct boundary evidence.

## D. Completion updates

Only on full live pass:

- update Objective 004 to 100% and weighted branch readiness to approximately
  91%;
- update `docs/OBJECTIVE-004-LEDGER.md`, `docs/VISION-ACCEPTANCE.md`, and
  `oap/COMPLETENESS.md` with exact sanitized live evidence;
- retain the 100,000-token vision limit, one-image upstream contract, selected
  hardware/model scope, and no production/cutover claim.

On failure, leave completeness unchanged at 90% and publish only exact failure
evidence.

## Non-goals and safety

- No Local Coding production source/config/API/log/metric change.
- No request-cap increase, sandbox/environment/compaction/gateway/cutover/
  benchmark work.
- No protected service/model/unit/launcher/config/key/profile/firewall/VPN/
  network mutation; vision stays selected.
- No raw prompt/source/image/tool output/body/model response/sentinel/session
  identifier/credential/data URL in Git, report, logs, metrics, or evidence.
- No second live attempt.

## Verification

Run focused marker-removal/exact-binding/phase/recorder tests before the live
attempt. Afterward run frozen dependencies, Ruff, mypy `src tests`, focused and
full pytest with live opt-in removed, build, wheel/sdist boundary, compileall,
shell syntax, diff and sensitive-content scans, then verify implementation and
report-head GitHub CI. Candidate 18031 and temporary state must be absent;
vision 18020 remains active and text remains inactive.

## Publication contract

Push the exact activated order/active and bounded repository-only helper/test/
docs changes to the existing PR. Push all non-report work first and record its
literal 40-hex SHA. Publish exactly one immutable
`oap/reports/004-ae-remove-contradictory-vision-marker-and-rerun.md` containing
the literal implementation SHA and `Report publication commit: SELF`. SELF must
be the sole final commit, change only that report, have the implementation SHA
as first parent, and be remote PR head before response FIFO `OK`.

# OAP Work Order — 004-af

## Objective

Resolve the durable OAP suffix-authority conflict exposed by blocked 004-ae,
then perform the exact narrow marker-removal correction and one corrected live
vision acceptance run previously ordered. Preserve the existing four-request
phase cap. Do not change Local Coding production code or protected services.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`.
- Numeric objective / round: `004` / `004-af`.
- PR mode: `AMEND_EXISTING_PR`; **NO NEW PR**.
- PR #6: `https://github.com/ulfe-lmi/slaif-local-coding/pull/6`.
- Base/head: `main` at `7a2c36a0a40958a6059a765c2f9d5e5bf4ddc161` /
  `oap/004-real-codex-governed-e2e`.
- Current verified remote head / blocked 004-ae SELF:
  `f93a43dd9b5cff59ee9cb6c73a5dcf0bcc4e1647`.
- Blocked-round implementation parent:
  `dc6071404ca7e69263b6d7a6c09faeffbe037809`.
- PR OPEN, non-draft, MERGEABLE/CLEAN; report-head `test` SUCCESS.
- Same PR only; coding never merges or enables auto-merge.

## A. Human-authorized durable suffix protocol

The human explicitly decided that immutable corrections after `004-z` use
`004-aa`, `004-ab`, and so on without renumbering history. Earlier strategy
updated `oap/bin/publish_order.py` and `oap/bin/check_state.py` to accept one or
two lowercase suffix letters, but failed to update the root coding constitution
and communication protocol. 004-ae correctly stopped at that conflict.

Strategy has now made these exact prepublication control-plane edits in the
working tree; preserve and commit them unchanged:

- root `AGENTS.md`;
- root `OAP-COMMUNICATION-coding-agent.md`;
- `oap/README.md`;
- `oap/strategic-instructions/AGENTS.md`;
- `oap/strategic-instructions/OAP-COMMUNICATION-strategic.md`;
- `oap/strategic-instructions/INITIAL-ROADMAP.md`;
- `docs/OAP-RUNBOOK.md`.

The durable rule is:

```text
ID = NNN-L, L matches [a-z]{1,2}
a creates exactly one objective PR
b..z, then aa..zz, amend that same PR
strategy alone chooses the suffix
after zz, escalate rather than silently extending grammar
```

Verify all repository identifier statements agree, legacy IDs and `004-af`
validate, malformed/uppercase/numeric/three-letter IDs fail, and no remaining
operative text says `aa` is forbidden. Do not rewrite immutable historical
orders/reports that accurately record the earlier rule or failure.

## B. Accepted 004-ad failure localization

004-ad's one live run stopped when phase 2 attempted a fifth main Responses
request. No later image/sentinel/session verdict was produced and no Local
Coding defect was established. Safe access counts showed eight main requests
and two compiler Chat requests forwarded before the blocked phase-2 fifth.

The repository-only prompt contains a concrete contradiction: it requests a
prompt-supplied intermediate `FULL-SCENE-PROCESSED`/`CROP-PROCESSED` agent
message and then a different exact delegated final sentinel. A tool-free agent
message is terminal in the ordinary Codex loop, so the two-terminal-message
contract can induce continuation. The supplied marker also proves no image
semantics.

## C. Narrow marker removal

In repository-only vision helper/tests/docs only:

- remove both marker instructions from `_vision_prompt`;
- remove marker parsing, `image_marker_passed`, and marker success predicates;
- retain the ordinary dependency read instruction;
- retain exact output-last-message byte equality with the hidden delegated
  sentinel; marker-only or marker-plus-sentinel output must fail;
- retain identical nonempty resumed thread ID;
- retain actual outbound full-only/crop-only facts for every main request;
- retain scaled metrics, privacy, cleanup, all phase negative tests, and
  `VISION_MAX_MAIN_REQUESTS_PER_INVOCATION = 4` unchanged;
- document that exact outbound image identity/count plus successful protected
  upstream/Codex lifecycle proves the compatibility property; no visual quality
  benchmark or prompt-supplied marker is used.

Add focused tests proving marker strings are absent from prompts/results and
exact hidden final binding remains mandatory.

## D. Active protected fixture

The human directed that the vision-enabled model remain running. Current
expected state after strategy reversed a partially initiated stop:

- `qwen-serving-vision.service` active/running, PID `364444`, zero restarts;
- text service inactive;
- protected vision on port 18020, model `qwen3.8-27b`, context 100000,
  one-image limit, low reasoning used by disposable catalog;
- port 18031 free.

Verify read-only and wait for health/models 200 before the run. Never operate or
edit either protected unit; leave vision running regardless of result.

## E. Exactly one corrected live attempt

After protocol and focused correction tests pass, run exactly once:

```bash
SLAIF_VISION_ACCEPTANCE=1 uv run --frozen pytest -q tests/test_vision_e2e.py -k live_vision_exec_resume_acceptance
```

No preliminary real Codex image call, retry, alternate prompt, request-cap
change, or post-failure mutation.

On success prove with sanitized facts:

1. Codex 0.149.0 global yolo, persistent session, context 100000/low reasoning;
2. both invocations exit 0 within bounds and have identical nonempty thread ID;
3. both exact final files equal the hidden delegated sentinel;
4. each phase contains 1..4 main requests; every phase-1 request forwards only
   expected full `input_image`; every phase-2 request only expected crop;
5. metrics match `(n1,0)` and `(2*n2,n2)`;
6. compiler/main calls, governance observation/acquisition/compile/injection,
   upstream lifecycle, privacy, and cleanup pass;
7. candidate 18031/temp state absent; vision remains active and unchanged.

On first failure stop with no retry/change and classify only from direct
evidence.

## F. Completion updates

Only on full pass update Objective 004 to 100%, branch readiness approximately
91%, Objective-004 ledger, vision acceptance docs, and completeness with exact
bounded evidence. Preserve 100,000-token vision context, one-image contract,
selected host/model scope, and no production/cutover claim. On failure leave
90% unchanged.

## Non-goals and safety

- No production Local Coding change or request-cap increase.
- No protected service/model/unit/config/key/profile/firewall/VPN/network
  mutation; vision stays running and text stays stopped.
- No compaction/sandbox/environment/gateway/cutover/benchmark work.
- No raw prompt/source/image/tool output/body/model response/sentinel/session
  ID/credential/data URL in durable evidence.
- No second live attempt.

## Verification

Run suffix-protocol checks; focused marker/exact-binding/phase tests; the one
live attempt; then frozen dependencies, Ruff, mypy `src tests`, non-live focused
and full pytest, build/wheel boundary, compileall, shell syntax, diff and
sensitive-content scans. Verify implementation and report-head GitHub CI.

## Publication contract

Push the exact activated order/active, exact strategic protocol edits, and
bounded repository-only helper/test/docs changes to the existing PR. Push all
non-report work first and record its literal 40-hex SHA. Publish exactly one
immutable
`oap/reports/004-af-durable-suffix-protocol-and-corrected-vision-rerun.md`
containing the literal implementation SHA and `Report publication commit:
SELF`. SELF must be the sole final commit, change only that report, have the
implementation SHA as first parent, and be remote PR head before response FIFO
`OK`.

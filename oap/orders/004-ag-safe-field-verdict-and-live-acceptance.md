# OAP Work Order — 004-ag

## Objective

Repair the two deterministic static failures introduced in 004-af, add a
privacy-safe field-level verdict for the existing unchanged vision acceptance
predicates, and execute exactly one live acceptance attempt against the active
vision fixture. Do not change Local Coding product code, image/session/sentinel/
metric acceptance semantics, request bounds, prompts, or protected services.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`.
- Numeric objective / round: `004` / `004-ag`.
- PR mode: `AMEND_EXISTING_PR`; **NO NEW PR**.
- PR #6: `https://github.com/ulfe-lmi/slaif-local-coding/pull/6`.
- Base/head: `main` at `7a2c36a0a40958a6059a765c2f9d5e5bf4ddc161` /
  `oap/004-real-codex-governed-e2e`.
- Current verified remote head / 004-af SELF:
  `425efa5343c0a692b21d0efb93e6f0aa4466cfdf`.
- 004-af implementation parent:
  `bdaab40610ac612adf36ff8467f948bb076286b0`.
- PR OPEN/non-draft/MERGEABLE but UNSTABLE; report-head required `test` FAILED
  because Ruff format failed before later CI steps.
- Same PR only; coding never merges or enables auto-merge.

## Accepted state and exact gaps

Accept 004-af's durable one/two-letter suffix protocol and removal of the
contradictory prompt-supplied processing marker. Safe protected access logs for
the single corrected run show two compiler Chat calls and exactly four main
Responses calls, consistent with two main requests in each Codex invocation;
the four-request cap did not fail and the earlier runaway loop is resolved.

004-af then failed at the aggregate `assert facts.successful`. The full
`VisionSessionFacts` existed, but the test emitted no fixed field-level verdict,
so it is unknown whether the failed condition was session equality, catalog,
turn lifecycle/exact sentinel, scaled metrics, or outbound facts. No Local
Coding product defect is established.

Two deterministic repository failures must also be repaired:

- Ruff format requires the `response_success` boolean expression on one line;
- mypy requires the marker-free prompt test's `turn` value to retain
  `Literal[1,2]` type rather than inferred `int`.

## A. Static repair

Apply only the exact Ruff formatting and precise typing correction needed for
the two failures. Do not suppress/ignore rules, weaken typing, or change
runtime behavior. Run Ruff format/check and mypy `src tests` successfully
before any live attempt.

## B. Privacy-safe complete verdict

Add a deterministic repository-only verdict derived entirely from the existing
facts and existing predicates. It must return only an ordered tuple of fixed
reason labels from this closed vocabulary (or equivalently specific fixed
sub-labels without dynamic values):

```text
session_mismatch
catalog_image_capability
catalog_detail_original
catalog_context_window
catalog_parallel_tools
turn1_exit
turn1_timeout
turn1_events
turn1_tool
turn1_exact_sentinel
turn2_exit
turn2_timeout
turn2_events
turn2_tool
turn2_exact_sentinel
metrics_missing
metrics_scaled_mismatch
outbound_phase_grouping
outbound_request_invalid
```

Requirements:

- empty reasons iff every predicate currently required by both
  `facts.successful` and `facts.outbound_successful` passes;
- no reason may incorporate a response, prompt, image/data URL, source, tool
  output, sentinel, session ID, credential, path, arbitrary exception, or raw
  dynamic string;
- a sanitized diagnostic summary may include only fixed reasons, booleans,
  bounded integer counts/statuses, event-type counts, phase counts, image
  seen/removed deltas, expected fixture labels, lengths, and SHA-256 values;
- normalized argv may remain only in the already-safe placeholder form;
- the live test must assert the complete reason tuple is empty and print the
  sanitized summary on failure, instead of stopping at an opaque aggregate;
- keep the existing aggregate properties as compatibility views or derive them
  from the same single predicate source so they cannot diverge.

Add focused tests that independently force every reason category, prove
empty-reasons equivalence with complete success, prove outbound failures are
included, and prove serialized diagnostics exclude the ephemeral sentinel,
thread/session IDs, data URLs, prompt/source/tool text, credentials, and raw
response content.

Do not modify any acceptance predicate, prompt, catalog, fixture, request cap,
timeout, model call, image expectation, metric invariant, or cleanup behavior.

## C. Active protected fixture

Human requires the vision model remain running. Verify read-only before/after:

- `qwen-serving-vision.service` active/running, PID `364444`, zero restarts;
- text unit inactive;
- port 18020 health/models 200, `qwen3.8-27b`, context 100000;
- port 18031 free before/after;
- protected unit/launcher/environment/profile/network state unchanged.

Do not operate/edit protected units and leave vision running regardless of
result.

## D. Exactly one live attempt

Only after focused/static gates pass, run exactly once:

```bash
SLAIF_VISION_ACCEPTANCE=1 uv run --frozen pytest -q tests/test_vision_e2e.py -k live_vision_exec_resume_acceptance
```

No preliminary Codex/model call, retry, alternate prompt, product change,
predicate/cap adjustment, or post-failure fix.

On full pass, report exact safe facts for Codex/version/yolo, catalog 100000,
both bounded invocations and same session, exact hidden sentinel twice, phase
counts, every outbound full/crop identity, scaled metrics, upstream/governance,
cleanup/privacy, and protected immutability.

On failure, report the exact fixed reason tuple and sanitized supporting counts
only; stop without retry or mutation. Classify Local Coding only if direct
boundary evidence supports it.

## E. Completion updates

Only on full pass update Objective 004 to 100%, weighted branch readiness to
approximately 91%, `docs/OBJECTIVE-004-LEDGER.md`,
`docs/VISION-ACCEPTANCE.md`, and `oap/COMPLETENESS.md`. Preserve the 100,000
vision context, one-image upstream limit, selected host/model scope, and no
production/cutover/benchmark claim. On failure leave completeness at 90%.

## Non-goals and safety

- No production Local Coding change; no acceptance weakening or request-cap
  increase.
- No protected service/model/config/profile/network/key mutation; vision stays
  running, text stopped.
- No sandbox/compaction/environment/gateway/cutover work.
- No raw sensitive content or arbitrary dynamic diagnostic text.
- No second live attempt.

## Verification and publication

Run focused verdict/privacy tests, Ruff, mypy `src tests`, then the one live
attempt, non-live focused/full pytest, frozen dependency check, build/wheel
boundary, compileall, shell syntax, diff and sensitive-content scans. Required
implementation/report-head GitHub CI must be green for acceptance.

Push exact active/order and bounded repository-only helper/test/docs or
success-only ledger changes to the same PR. Publish exactly one immutable
`oap/reports/004-ag-safe-field-verdict-and-live-acceptance.md` with literal
implementation SHA and `Report publication commit: SELF`; SELF changes only
that report, its first parent is the implementation SHA, and it is remote PR
head before response FIFO `OK`.

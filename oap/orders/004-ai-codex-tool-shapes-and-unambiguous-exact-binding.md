# OAP Work Order — 004-ai

## Objective

Correct the remaining repository-only fixture/recorder mismatches demonstrated
by 004-ah: recognize bounded standard Responses custom/local-shell tool shapes,
classify but never accept fixed final-message presentation wrappers, and make
the synthetic dependency's existing byte-exact rule unambiguous about forbidden
formatting. Then run exactly one live acceptance attempt against the active
vision fixture. Do not change Local Coding production code, image behavior,
request bounds, service state, or byte-exact acceptance.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`.
- Numeric objective / round: `004` / `004-ai`.
- PR mode: `AMEND_EXISTING_PR`; **NO NEW PR**.
- PR #6: `https://github.com/ulfe-lmi/slaif-local-coding/pull/6`.
- Base/head: `main` at `7a2c36a0a40958a6059a765c2f9d5e5bf4ddc161` /
  `oap/004-real-codex-governed-e2e`.
- Current verified remote head / 004-ah SELF:
  `191673c227a8d0a7de269a949cbc39c4f70d7b54`.
- 004-ah implementation parent:
  `7ef8fe3a306999e53efc1855bba60809d904d3c3`.
- PR OPEN/non-draft/MERGEABLE/CLEAN; report-head `test` SUCCESS.
- Same PR only; coding never merges or enables auto-merge.

## Accepted live evidence

004-ah proves the actual vision compatibility path except two test-only facts:
same resumed session; catalog/context 100000; both invocations exit 0; phase
counts `(2,2)`; scaled metrics `(2,0)` then `(4,2)`; every outbound request one
expected image with labels full/full then crop/crop; governance and non-image
preservation; protected upstream success; cleanup/privacy/protected state.

Both final event/file channels were present and identical across both turns,
with byte length 39 and one fixed SHA-256, while expected sentinel length is 37.
They are not exact or terminal-CR/LF-only. All four outbound facts had
`tool_content_preserved=false` under the narrow structural recognizer.

No Local Coding product/image defect is established.

## A. Bounded real Codex/Responses tool shapes

Repository-only structural recognition currently permits only definition type
`function` and item types `function_call|function_call_output|exec_command`.
Codex 0.149 may use standard/custom local tool forms at the provider boundary.

Expand the fixed allowlists only to the exact supported structural types used
by Responses/Codex tool traffic, including as applicable:

```text
definitions: function, custom, local_shell
items: function_call, function_call_output,
       custom_tool_call, custom_tool_call_output,
       local_shell_call, local_shell_call_output,
       command_execution, exec_command
```

Requirements:

- keep top-level definitions bounded/nonempty and recursive item scan depth/node
  bounded;
- never inspect/store/report tool names, descriptions, schemas, grammar,
  arguments, outputs, or raw tool text;
- add safe fixed diagnostic categories/counts for recognized definition/item
  types and an `unexpected` bucket; no arbitrary strings;
- `tool_content_preserved` requires at least one recognized bounded definition
  or item, with malformed/empty/over-limit/unknown-only inputs false;
- compiler Chat traffic remains excluded from main vision facts;
- add realistic synthetic tests for each allowlisted type, mixed valid forms,
  unknown/malformed/spoofed/nested/over-limit negatives, and diagnostic privacy.

Do not change production tool forwarding or Local Coding.

## B. Unambiguous synthetic exact-response rule

The dependency already says the entire final message MUST be exactly the hidden
sentinel. The protected model produced a consistent two-byte presentation
difference on both turns. Make the existing fixture semantics explicit, without
putting the token in prompts/config/catalog:

```text
Output only the prescribed sentinel bytes.
Do not add quotes, backticks, Markdown, code fences, punctuation, spaces,
tabs, prefixes, suffixes, explanation, or line breaks.
```

Place this clarification in the synthetic delegated dependency (and root only
if necessary to preserve authority ordering), not the ordinary user prompt.
The hidden token remains only in the disposable dependency and compiler-derived
governance path. Prompts/config/catalog must remain token-free.

Keep acceptance byte-exact or terminal-CR/LF-only exactly as in 004-ah. Do not
accept wrappers, punctuation, substring presence, Markdown, quotes, or spaces.

## C. Safe fixed wrapper classification

Extend final-message evidence with one fixed diagnostic label, never an
acceptance path, for:

```text
none
inline_backticks
double_quotes
single_quotes
asterisk_wrapper
period_suffix
period_then_crlf
leading_and_trailing_crlf
other_mismatch
```

Compare transient content to these fixed constructions in memory. The label is
diagnostic only: every non-`none` wrapper remains
`non_whitespace_mismatch=true`, `sentinel_passed=false`. Retain safe
length/hash/provenance and never raw text/token.

Add exhaustive focused tests proving classification and non-acceptance,
including same-length unknown content and privacy scans.

## D. Unchanged boundaries

Do not change marker-free ordinary prompts, Codex/version/yolo/session argv,
model catalog/context/reasoning, phase cap four, full/crop image requirements,
scaled metrics, session equality, compiler/product logic, timeouts, cleanup, or
protected service.

## E. Active fixture and exactly one run

Verify read-only that vision PID `364444` remains active with zero restarts,
text inactive, health/models 200, model `qwen3.8-27b`, context 100000, and port
18031 free. Never operate protected units; leave vision running.

After focused/static gates pass, run exactly once:

```bash
SLAIF_VISION_ACCEPTANCE=1 uv run --frozen pytest -q tests/test_vision_e2e.py -k live_vision_exec_resume_acceptance
```

No preliminary model call, retry, alternate prompt, acceptance/cap change, or
post-failure edit.

On pass report exact safe session/catalog/process/final binding provenance,
tool structural categories, phase/image/metrics/governance/upstream/cleanup/
privacy/protected facts. On failure report fixed reasons plus wrapper/tool
categories/counts only and stop.

## F. Completion updates

Only on full pass update Objective 004 to 100%, weighted branch readiness
approximately 91%, Objective-004 ledger, vision acceptance docs, and
completeness. Preserve vision context 100000, one-image limit, selected
host/model scope, and no production/cutover/benchmark claim. On failure leave
90% unchanged.

## Non-goals and safety

- No Local Coding production change, predicate weakening, request-cap change,
  protected mutation, sandbox/compaction/gateway/cutover work, or second live
  attempt.
- No raw sensitive content or arbitrary dynamic diagnostic strings.

## Verification and publication

Run focused tool-shape/wrapper/exact-binding/verdict/privacy tests, Ruff/mypy,
then the one live attempt, non-live full pytest, build/wheel boundary,
compileall, shell syntax, diff and precise sensitive scans. Required current CI
must be green.

Push exact active/order and bounded repository-only helper/test/docs or
success-only ledger changes to the same PR. Publish exactly one immutable
`oap/reports/004-ai-codex-tool-shapes-and-unambiguous-exact-binding.md` with
literal implementation SHA and `Report publication commit: SELF`; SELF changes
only that report, parent equals implementation SHA, and is remote head before
FIFO `OK`.

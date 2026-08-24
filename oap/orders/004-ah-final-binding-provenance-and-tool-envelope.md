# OAP Work Order — 004-ah

## Objective

Correct two directly evidenced repository-only acceptance predicates without
changing Local Coding or weakening governance: recognize ordinary top-level
tool definitions on the first outbound request, and validate the hidden final
binding from both the final Codex agent-message event and output-file boundary
while distinguishing only terminal CR/LF transport normalization from genuine
extra content. Then execute exactly one live acceptance attempt against the
active vision fixture.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`.
- Numeric objective / round: `004` / `004-ah`.
- PR mode: `AMEND_EXISTING_PR`; **NO NEW PR**.
- PR #6: `https://github.com/ulfe-lmi/slaif-local-coding/pull/6`.
- Base/head: `main` at `7a2c36a0a40958a6059a765c2f9d5e5bf4ddc161` /
  `oap/004-real-codex-governed-e2e`.
- Current verified remote head / 004-ag SELF:
  `de3e041ad3ad8b59ce48df93f575d84f8f35e7c1`.
- 004-ag implementation parent:
  `8357ebb4b518d360debc18f06060a8af12ae9463`.
- PR OPEN, non-draft, MERGEABLE/CLEAN; report-head required `test` SUCCESS.
- Same PR only; coding never merges or enables auto-merge.

## Accepted live evidence

004-ag's single live run established all of the following with fixed safe
facts: identical persisted/resumed session; catalog text+image capability,
detail policy, parallel-tool policy, and context 100000; both subprocesses exit
0 without timeout; two tool lifecycle events per invocation; phase counts
`(2,2)`; exact scaled image metrics `(2,0)` then `(4,2)`; four actual outbound
main requests with labels full/full then crop/crop and one image per request;
three recorder facts accepted. Protected vision remained healthy and cleanup/
privacy passed.

The only reasons were
`turn1_exact_sentinel`, `turn2_exact_sentinel`, and
`outbound_request_invalid`. No Local Coding product failure is established.

## A. Real tool-envelope preservation predicate

The first outbound request occurs before any tool call/result item exists. Its
ordinary Codex tool capability is represented by a nonempty top-level `tools`
definition list. Current `_has_tool_content` recognizes call/result item types
but not ordinary definitions, so it incorrectly sets
`tool_content_preserved=false` for the first request.

In repository-only acceptance support:

- recognize a bounded nonempty top-level `tools` list containing supported
  tool definitions as tool content;
- continue recognizing actual call/result items on continuation requests;
- validate only safe structural presence/type/count, not names, descriptions,
  schemas, arguments, outputs, or raw tool text;
- when a fake incoming preservation oracle exists, compare a safe canonical
  fingerprint as already designed;
- add realistic captured/synthetic Codex tool-definition tests and negative
  empty/malformed/spoofed cases;
- do not alter production forwarding, tool schemas, prompts, or recorder image
  predicates.

## B. Exact final-binding provenance

Current `_exact_final_message` checks only raw output-file bytes. It discards
the final `agent_message` text after event counting, so it cannot distinguish:

- exact model message with CLI-added terminal newline in the output file;
- exact/terminal-line-ending model message;
- genuine extra prose or marker content.

Add a bounded immutable safe evidence structure for the **last completed Codex
agent message** and separately for the output-last-message file. Each channel
may retain only:

```text
present
byte_length
sha256
exact_expected
terminal_line_endings_only
non_whitespace_mismatch
```

Rules:

- compare transient content to the expected ephemeral sentinel in memory;
- `exact_expected` requires byte equality;
- `terminal_line_endings_only` permits removal of one or more trailing CR/LF
  bytes only, with the remaining bytes exactly equal expected;
- spaces/tabs, prefixes/suffixes, Markdown/code fences, marker text, multiple
  messages, or any other difference are non-whitespace mismatch and fail;
- use the last completed `agent_message` only; earlier messages cannot satisfy
  final binding;
- `sentinel_passed` iff the final event or output file is exact or differs only
  by terminal CR/LF; substring presence is never sufficient;
- preserve a fixed provenance label `event_exact|event_terminal_crlf|file_exact|
  file_terminal_crlf|mismatch|missing`, without raw text;
- never serialize the sentinel value, actual message, session ID, prompt,
  source, tool output, or arbitrary exception.

This is transport-boundary normalization, not a weakening of the model rule.
It aligns with the repository's existing terminal-whitespace diagnostic law and
the architecture's requirement that the binding governance rule remain
effective.

Add focused tests for exact event/file, CR, LF, CRLF, multiple terminal line
endings, missing channel, earlier-exact/later-wrong, spaces/tabs, prefix/suffix,
Markdown fences, marker-plus-sentinel, and non-whitespace mismatch. Prove safe
diagnostics contain no sentinel or raw content.

Update the closed failure verdict to retain the existing fixed
`turn1_exact_sentinel`/`turn2_exact_sentinel` labels when neither channel passes;
add only fixed safe provenance/count facts to diagnostics.

## C. Unchanged acceptance boundaries

Do not change:

- marker-free prompts or dependency content;
- Codex 0.149.0 global yolo/session/image argv;
- model catalog, context 100000, reasoning low;
- phase cap four, phase grouping, full/full then crop/crop requirement;
- scaled metrics, image hashes/lengths/types, session equality;
- compiler/governance pipeline, product code, service, timeouts, cleanup,
  privacy, or any other predicate.

## D. Active protected fixture and one attempt

Human requires vision remain running. Verify read-only: vision PID `364444`
active/zero restarts, text inactive, health/models 200, model `qwen3.8-27b`,
context 100000, port 18031 free. Never operate protected units and leave vision
running.

After focused tests and all Ruff/mypy gates pass, run exactly once:

```bash
SLAIF_VISION_ACCEPTANCE=1 uv run --frozen pytest -q tests/test_vision_e2e.py -k live_vision_exec_resume_acceptance
```

No preliminary real model call, retry, alternate prompt, cap/predicate change,
or post-failure edit.

On pass, report safe final-binding provenance for each turn, tool-envelope
structural success, session/catalog/process/phase/outbound/metrics/governance,
privacy/cleanup/protected state. On failure report the fixed reason tuple and
safe provenance/counts only, then stop.

## E. Completion updates

Only on full pass update Objective 004 to 100%, weighted branch readiness
approximately 91%, Objective-004 ledger, vision acceptance docs, and
completeness. Preserve vision context 100000, one-image limit, selected
host/model scope, and no production/cutover/benchmark claim. On failure leave
90% unchanged.

## Non-goals and safety

- No Local Coding production change, acceptance weakening, request-cap change,
  protected mutation, sandbox/compaction/gateway/cutover work, or second live
  attempt.
- No raw sensitive content or dynamic diagnostic strings.

## Verification and publication

Run focused tool/final-binding/verdict/privacy tests, frozen Ruff/mypy, then the
one live attempt, non-live full pytest, build/wheel boundary, compileall, shell
syntax, diff and precise sensitive-content scans. Required implementation and
report-head GitHub CI must be green.

Push exact active/order and bounded repository-only helper/test/docs or
success-only ledger changes to the same PR. Publish exactly one immutable
`oap/reports/004-ah-final-binding-provenance-and-tool-envelope.md` with literal
implementation SHA and `Report publication commit: SELF`; SELF changes only
that report, parent equals implementation SHA, and is remote head before FIFO
`OK`.

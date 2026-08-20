# Verification contract

Labels are exact: `PASSED`, `FAILED`, `SKIPPED`, `NOT RUN`, `BLOCKED`,
`PENDING`, `MISSING`. Unknown is never pass.

## Static/unit gate

The implementation must establish and keep one locked command set covering:

```text
format check
lint
static typing
unit tests
package/build validation
secret/logging-policy checks
```

## Contract tests with fake upstream

Required behavior:

- byte/semantic preservation for untransformed JSON requests;
- status, headers, error body, SSE event order, disconnect, timeout, and tool-call
  passthrough;
- `/v1/responses` and `/v1/chat/completions`;
- no buffering of streaming responses;
- hop-by-hop/internal-header filtering;
- body-size and malformed-JSON behavior;
- compiler requests bypass the public transformation path;
- no raw-payload logging.

## Image-policy tests

Cover nested `input_image` and `image_url` items for Responses and Chat:

- zero images unchanged;
- one image unchanged;
- multiple images retain exactly the newest for `retain_newest`;
- text/tool items and ordering otherwise preserved;
- explicit reject policy returns a documented client error;
- policy is route-specific, never global accidental behavior.

## Constitution tests

Cover:

- effective `AGENTS.md` detection from captured/synthetic Codex envelopes;
- deterministic candidate-path extraction;
- separate reference confidence and constitutional priority;
- strict compiler schema and bounded output;
- content-hash cache hit/miss/invalidation;
- missing dependency acquisition state;
- stable bounded injection on every request;
- preservation of normative `MUST`, `MUST NOT`, `NEVER`, exceptions, role and
  source-of-truth rules;
- compiler failure fallback without silent governance loss;
- tenant/session isolation and TTL/LRU limits;
- simulated compaction/new-turn rehydration.

## Live tests on the RTX 3090 host

Use only the authenticated private vLLM endpoint and development adapter port.
Do not restart or reconfigure vLLM.

Minimum live matrix:

1. authenticated `/health` and `/v1/models` upstream;
2. adapter health/readiness and model passthrough;
3. ordinary non-streaming Responses text;
4. ordinary forced and automatic function tool calls with valid JSON arguments;
5. SSE text and SSE function-call streaming;
6. multi-turn `function_call_output` continuation;
7. one-image vision request;
8. two-image history request through adapter succeeds with only newest image
   reaching upstream;
9. constitution compile on first hash and cache hit on repeat;
10. sentinel governance rule obeyed after simulated compaction/request history
    reduction;
11. no raw `<tool_call>` markup in model-visible text;
12. no secret/raw-content leakage in logs or metrics.

Live stress tests must be serialized/bounded and must not starve the active
coding/strategic Codex sessions. Existing evidence showed 50/50 repeated tool
calls and 20/20 multi-turn sequences on the text configuration; new code must
not claim equivalent vision/adapter evidence until rerun.

## End-to-end Codex test

Use a disposable test repository with a long `AGENTS.md`, a sentinel rule near
the end, and referenced constitutional files. Capture only sanitized metadata.
Verify unchanged Codex client behavior, ordinary local tools, image full-view
then crop, forced compaction or equivalent history reduction, cache reuse, and
continued compliance.

## CI and merge

Required GitHub checks for the current PR must all be present and successful.
Green CI is necessary, not sufficient; strategic review also inspects live-test
evidence, scope, security, architecture, and documentation.

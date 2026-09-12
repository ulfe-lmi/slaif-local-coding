# OAP Coding-Agent Report — 005-ap

## Work order

- Identifier: `005-ap`
- Order path: `oap/orders/005-ap-zero-argument-preflight-and-final-target.md`
- Numeric objective: `005`
- PR mode: `AMENDED_EXISTING_PR`

## Status

BLOCKED

## Executive summary

The exact zero-argument `local_lookup` target was restored, with a hard
Gateway-derived helper/profile preflight before protected credential or
provider work and private reuse of the checked initial request bytes. The
clean candidate qualified the full fake gate and isolated target. The one
authorized protected target pair then failed closed on its continuation. No
protected retry, fake qualification rerun, diagnostic request, runtime repair,
new suffix, merge, or cutover followed that failure.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`
- PR: 7 — https://github.com/ulfe-lmi/slaif-local-coding/pull/7
- State: OPEN; base `main`; head `oap/005-gateway-ingress-integration`
- Starting remote SHA: `9ef4c53e2067cd4ef723b2a42a0a645fc3f924aa`
- Implementation head SHA: `91be1d73eddb64b65910de2fd15dfdf8309ad6c8`
- Report publication commit: SELF
- Implementation commits pushed before report: `934388057af267b3bf39b2a2d1b56d34dfbd042f`, `e78dbde948419e4143f1ed774f820062e1e0bbf9`, `a4f3db03e65fb5f50b49262c074ba72ef2907c9a`, `91be1d73eddb64b65910de2fd15dfdf8309ad6c8`
- Final tracked tree is equal to the qualified source tree at `934388057af267b3bf39b2a2d1b56d34dfbd042f`; the short post-failure instrumentation delta was reverted before this report.
- New PR this round: NO; amended existing: YES; merge performed: NO

## Changes and files

- Restored the exact empty-parameter declaration for target `local_lookup` and retained the no-argument prompt, streaming, forced function choice, `store=false`, and 32-token bound.
- Preserved actual returned function-call fields for the ID-less continuation, omitting only the optional function-call item ID.
- Added the pre-credential Gateway helper/profile equality gate and bound initial request content path.
- Kept fake zero-argument output legal while preserving separate canonical nonempty-argument fixtures.
- Added focused tests for positive/negative semantic predicates, protected-selection ordering, body binding, fake zero-argument output, observer failure-event retention, and replay safety.
- Corrected dated signed-identity statements in `docs/ADAPTER-CONFIGURATION.md` and `config/adapter.example.toml`.
- Activated `oap/active` and order bytes were preserved unchanged; unrelated empty untracked files were not staged.

## Acceptance evidence

### Criterion A — exact zero-argument target

- PASSED at qualified source `934388057af267b3bf39b2a2d1b56d34dfbd042f`.
- The target declaration is exactly an object with empty `properties` and
  `additionalProperties=false`, with no required parameter.
- Fake target output used the legal five-event omission lifecycle. Separate
  focused Gateway fixtures accepted ordinary canonical argument deltas and
  preserved arbitrary nonempty arguments.

### Criterion B — semantic preflight and request binding

- PASSED: exact pinned Gateway helper eligibility, validator profile fact,
  helper/profile equality, and request-body binding were all true.
- PASSED: focused mismatch and ordering spies showed semantic failure before
  protected selection, credential resolution, or protected requests.
- The actual first target request reused the privately held checked bytes; no
  body, body hash, session ID, credential, or signature was retained in
  evidence.

### Criterion C — fake qualification

- PASSED at `934388057af267b3bf39b2a2d1b56d34dfbd042f`: full fake machine gate
  `37/37` obligations and projections; `26` direct dispatches (`6` compiler,
  `12` inference, `8` other); `12/12` inference observations terminal-valid;
  cleanup and secret-free logging passed.
- PASSED at the same source: isolated `identity_replay` target gate; exactly
  `2` inference, `0` compiler, `0` other target dispatches; both streamed
  responses valid; matching replay authority and omitted optional item ID;
  accounting, cleanup, and privacy passed.

### Criterion D — one protected target pair

- BLOCKED: exactly one protected attempt was made at the qualified source;
  no retry was made.
- Initial hard gate: PASSED. Initial response: HTTP `200`, SSE
  terminal-valid.
- Continuation: reached Qwen and returned `4xx` at the direct observer
  boundary; public Gateway response was HTTP `200` carrying an error SSE.
- Target failure: `continuation_response_invalid`.
- Direct observer failure: `stream_closure_invalid`.
- Actual target dispatch: `2` inference, `0` compiler, `0` other; bounded
  preflight/readiness: `3` requests. Aggregate lifetime snapshots are not
  used as target request counts.
- Accounting: initial ledger finalized `1`, failed ledger `1`, zero pending,
  zero duplicate request IDs; the two-reservation terminal predicate did not
  pass.
- Same-response safe facts: allowlisted error field names `code`, `message`,
  `param`, and `type` were observed; their values and error classes remained
  `unknown`. Failed-frame event class was **NOT OBSERVED** and is not
  reconstructed or claimed.

## Verification

- `ruff check .`: PASSED
- `ruff format --check .`: PASSED
- `mypy src tests`: PASSED
- `pytest -q`: PASSED — `838 passed, 16 skipped`
- `SLAIF_GATEWAY_ROOT=/tmp/slaif-gateway-005-ao ... pytest -q tests/test_gateway162_validator_factory.py`: PASSED — `8 passed`
- `uv build`: PASSED
- `python -m compileall -q src tests oap/bin`: PASSED
- `bash -n oap/bin/*.sh`: PASSED
- `git diff --quiet 934388057af267b3bf39b2a2d1b56d34dfbd042f --`: PASSED — final tracked tree restored to qualified source

## Live model/service evidence

- Read-only preflight and post-run snapshots: vision unit active, ordered
  PID/start/restart facts unchanged, private port `18020` present, text
  service inactive, ports `18021` and `18031` absent, Qwen worktree count `7`.
- Protected health/models preflight: HTTP `200` / HTTP `200`.
- Existing Qwen vision/vLLM fixture was not restarted, reconfigured, patched,
  rebound, or replaced. No credential value was printed, hashed, persisted, or
  exposed.
- Owned temporary Gateway/Local/PostgreSQL/cache/Codex state cleanup passed;
  secret-free log check passed.

## GitHub CI / required checks

- Final implementation-head `test` check: SUCCESS at
  `91be1d73eddb64b65910de2fd15dfdf8309ad6c8`.
- All required checks green at drafting: YES.
- Report-head checks may be newly pending; strategy verifies them separately.

## Local setup/dependencies

- Used the existing pinned clean Gateway checkout at
  `5ea38325ef3a3ebc69524b4679b795fab0c52935`, task Gateway venv, SDK
  `openai 2.41.0`, PostgreSQL 16 temporary container, and Codex `0.149.0`
  fixture. No model weights or installed services were changed.

## Documentation

Updated current-facing signed-identity statements in the adapter configuration
guide and example comment. Example values and installed configuration were not
changed.

## Safety/scope confirmations

- Unrelated primary work was preserved; `Local`, `clean`, and `unchanged`
  remained empty untracked files and were not staged.
- No secrets, raw bodies, prompts, source, images, tool output, credentials,
  signatures, or private payloads entered the report.
- Protected 18020/Qwen/Codex fixture changed: NO.
- Required protected acceptance after the failed continuation: NOT RUN by
  design; retry prohibited.
- Extra objective PR: NO; coding merge: NO.
- Active/order edited: NO.
- Report commit report-only: YES.

## Known limitations/blockers

The protected continuation did not satisfy the exact composed stream closure
and accounting terminal predicates. The provider-side error values and failed
SSE frame class were unavailable in the retained safe evidence, so no owner or
specific type/code/parameter value is assigned. The post-failure instrumentation
delta was reverted and was not used to reinterpret the completed attempt.

## Recommended strategic follow-up

Review the protected Gateway/Local/Qwen continuation stream-closure failure
from the retained bounded evidence. No automatic retry, suffix, merge, service
mutation, or cutover is recommended by this report.

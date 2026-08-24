# OAP Coding-Agent Report — 005-e

## Work order

- Identifier: 005-e
- Order path: oap/orders/005-e-route-scoped-codex-tool-filter-contract.md
- Numeric objective: 005
- PR mode: AMENDED_EXISTING_PR

## Status

COMPLETE

## Executive summary

Implemented the Local Coding side of the directly evidenced Codex/gateway
tool-envelope contract. Routes now select a typed, disabled-by-default
Responses tool policy. The explicit v1 compatibility policy removes only exact
top-level tool declarations of type tool_search or web_search, preserves
ordinary and continuation tool data, and rejects explicit choices that would be
silently changed. Added bounded fake-upstream coverage, a content-free
cross-repository vector, and a gateway-side proposal marked NOT IMPLEMENTED and
NOT AUTHORIZED. The gateway, Qwen/vLLM service, Codex profiles, and network
state were not changed.

## Authoritative GitHub state

- Repository: ulfe-lmi/slaif-local-coding
- PR: #7 — https://github.com/ulfe-lmi/slaif-local-coding/pull/7
- PR state: OPEN, non-draft, base main, head oap/005-gateway-ingress-integration,
  merge state CLEAN
- Starting remote SHA: 9707473dbdd9fbc6aa88e925f82409d56f406e34
- Implementation head SHA: 8ce107c1d8297e16d13d287a6becf6801cfdcaf1
- Report publication commit: SELF
- Implementation commits pushed before report: 8ce107c1d8297e16d13d287a6becf6801cfdcaf1
- New PR this round: NO
- Amended existing PR: YES
- Merge performed: NO

## Changes and files

- Added src/slaif_local_coding/tool_policy.py with the bounded
  responses-tool-policy-v1 transformation and fixed rejection reasons.
- Extended RouteConfig with responses_tool_policy, defaulting to passthrough,
  and documented the opt-in route configuration.
- Applied the policy after image handling and before constitutional observation,
  with route-scoped observed/removed/outcome metrics and no raw tool fields.
- Added exhaustive fake-upstream and pure policy tests in
  tests/test_tool_policy.py, including the captured 005-d type set,
  continuation preservation, streaming equivalence, malformed/oversized/deep
  bounds, ordering, image/governance interaction, and pre-upstream rejection.
- Added the content-free vector
  tests/fixtures/gateway/responses_tool_filter_vectors.json and linked it from
  the existing gateway vector.
- Added docs/GATEWAY-ROUTE-SCOPED-CODEX-TOOL-FILTER-PROPOSAL.md. It is a
  proposal only and contains no gateway patch or implementation.
- Committed the activated oap/active and 005-e order bytes unchanged as the
  orchestration transcript.

## Acceptance evidence

### Criterion 1 — Explicit route-scoped policy

- PASSED — RouteConfig accepts only passthrough or
  drop_disabled_codex_search and defaults to passthrough. Policy version is
  responses-tool-policy-v1. Chat and default/passthrough routes remain
  unchanged.

### Criterion 2 — Exact declaration filtering and preservation

- PASSED — Exact top-level tool types tool_search and web_search are removed
  only on the opted-in Responses route. function, custom, namespace, unknown
  types, input function_call/function_call_output items, ordering, schemas, and
  arguments are preserved.
- PASSED — Automatic, none, and absent choice cases omit tools only when no
  declarations remain. Stream and non-stream requests use the same transformed
  request and response SSE bytes are not transformed.

### Criterion 3 — Fail-closed explicit controls and bounds

- PASSED — Explicit dropped type/name choices and unsatisfiable required
  choices return fixed OpenAI-shaped HTTP 422 before observation, compiler,
  cache, or upstream work.
- PASSED — Non-list, malformed, oversized, and over-bound tool-choice shapes
  return fixed responses_tool_policy_invalid or bounded policy errors.

### Criterion 4 — Cross-repository contract and proposal

- PASSED — The content-free vector defines the exact authenticated
  openai_compatible route precondition, adapter postcondition, and one-public-
  request accounting/internal-compiler boundary.
- PASSED — The gateway proposal requires a disabled-by-default exact route and
  provider capability, preserves gateway accounting/body ownership, rejects
  hosted-tool execution, and requires a separate authorized gateway OAP
  objective/PR.

### Criterion 5 — Security containment

- PASSED — Scoped changed-file credential and raw-log scans produced no
  findings. Tests assert tool/search content is absent from metrics and
  rejected requests do not reach upstream or constitution work.
- PASSED — New fixtures and tests use only repository fixtures or in-memory
  synthetic values; no host Codex home, sessions, history, cache, or arbitrary
  parent search was added.

## Verification

- uv run --frozen ruff check .: PASSED — All checks passed.
- uv run --frozen ruff format --check .: PASSED — 211 files formatted.
- uv run --frozen mypy src tests: PASSED — no issues in 50 source files.
- uv run --frozen pytest -q -rs: PASSED — 530 passed, 8 skipped.
- uv run --frozen pytest -q tests/test_tool_policy.py: PASSED — 22 passed.
- uv run --frozen pytest -q tests/test_tool_policy.py tests/test_config.py tests/test_app.py: PASSED — 117 passed.
- uv build: PASSED — wheel and source distribution built.
- Wheel/sdist member inspection: PASSED — new production module is in the
  wheel; tests, diagnostics, and gateway implementation are not in the wheel.
- uv run --frozen python -m compileall -q src tests oap/bin: PASSED.
  The bare local python -m spelling was unavailable; the exact
  python -m compileall -q src tests oap/bin command PASSED in GitHub CI.
- bash -n oap/bin/*.sh: PASSED.
- git diff --check: PASSED.
- Scoped changed-file secret/raw-log scan: PASSED — no findings.
- Live model/gateway/adapter test matrix: NOT RUN — explicitly prohibited by
  this order; no live API or model call was made.
- Existing live tests skipped: 7 require SLAIF_LIVE_TEST=1; one vision E2E
  test requires human activation of the mutually exclusive protected fixture.

## Live model/service evidence

- Read-only host check observed a vllm process listening on port 18020.
- Ports 18021 and 18031 had no listener.
- The user qwen-serving systemd unit reported ActiveState=inactive,
  SubState=dead, MainPID=0 while the vllm listener remained present. This
  pre-existing state discrepancy was recorded, not repaired or changed.
- No model/gateway request, service start/stop/restart, profile change, port
  bind, network change, credential access, or protected Qwen mutation occurred.

## GitHub CI / required checks

- Implementation-head check test: SUCCESS.
- GitHub Actions run: 32706495955; job: 97368612394.
- All required checks green at drafting: YES.
- Report-head checks may be pending after publication; strategy verifies them
  independently.

## Local setup/dependencies

- Used the existing repository uv environment and frozen lockfile.
- No new dependency, Docker/Postgres/gateway process, adapter listener, sudo
  action, or external service was used.
- Build outputs remained ignored repository-local artifacts.

## Documentation

- UPDATED — adapter configuration, gateway integration vector reference, and
  the explicitly non-active gateway proposal.

## Safety/scope confirmations

- Unrelated files: preserved; only the ordered implementation, tests, docs,
  vector, and activated transcript were committed.
- Secrets/raw content: no real credentials, bearer values, prompts, source,
  images, tool output, or customer data committed, logged, or reported.
- Protected 18020/Qwen/Codex fixture changed: NO.
- Gateway code/provider/accounting changed: NO.
- Required live tests: NOT RUN as explicitly ordered; local fake-upstream and
  static gates ran.
- Extra objective PR: NO.
- Coding merge: NO.
- Active/order edited: NO; activated bytes were committed unchanged.
- Final report commit report-only: YES.

## Known limitations/blockers

- The current gateway still rejects actual Codex traffic with
  responses_hosted_tool_not_supported. This adapter-side preparation does not
  authorize or implement the gateway change.
- Trusted signed per-user identity, gateway-path accounting for this envelope,
  live gateway compatibility, service cutover, and production readiness remain
  unproven and outside this order.
- The host systemd-unit/listener discrepancy above remains for strategy/human
  review; no protected repair was authorized.

## Recommended strategic follow-up

- Review the exact PR/diff, report parent/SELF relationship, current
  report-head checks, and the non-active gateway proposal.
- Decide separately whether to authorize a gateway OAP objective after PR #287
  resolution. Do not infer compatibility or cutover from this adapter-side
  result.

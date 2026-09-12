# OAP Coding-Agent Report — 005-j

## Work order

- Identifier: `005-j`
- Order path: `oap/orders/005-j-corrected-boundary-and-final-real-composed-acceptance.md`
- Numeric objective: `005`
- PR mode: `AMENDED_EXISTING_PR`

## Status

PARTIAL

## Executive summary

The corrected Local Coding → protected-Qwen boundary passed its one authorized
request through stages A–I, with one dispatch, the exact 169-byte provider-bound
shape, recognized SSE, valid terminal usage, normal close, and byte/digest-equal
downstream forwarding. The required timing-bucket facts were not emitted by the
runner, so the complete section-B acceptance contract is not claimed. The one
authorized composed acceptance attempt stopped before public or protected
traffic at the disposable relay readiness stage with `service_ready_timeout`.
The composed run was not retried.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`
- PR: [#7](https://github.com/ulfe-lmi/slaif-local-coding/pull/7)
- PR state: OPEN, non-draft, MERGEABLE/CLEAN
- Base/head: `main` / `oap/005-gateway-ingress-integration`
- Starting remote SHA: `d3168fa4a0c8e87f9e92567ef4f9283ed6b0f823`
- Implementation head SHA: `55d5e2c43322fd145af5672bab4e396816a2ff1c`
- Report publication commit: SELF
- Implementation commits pushed before report: `55d5e2c43322fd145af5672bab4e396816a2ff1c`
- New PR this round: NO
- Amended existing PR: YES, PR #7
- Merge performed: NO

The read-only Gateway dependency remained PR #291 at exact head
`306ecb186b5c12db991a684e7c04e5c9f174eba2`, with report-only parent
`a8a2a7a8a2e84fbe7dd42658173dd6358f709444`, open/non-draft/mergeable-clean,
and all ten listed checks successful.

## Changes and files

- Corrected `scripts/local_qwen_provider_differential.py` for the 005-j
  single-Local-call contract: no direct-provider fallback, exact fixed
  vocabulary, line/total stream bounds, duplicate/error detection, normal-close
  tracking, one-dispatch enforcement, and independent stage-I status/type,
  lifecycle, byte-count, and digest checks.
- Expanded `tests/test_local_qwen_provider_differential.py` with the ordered
  bounded SSE, lifecycle, vocabulary, forwarding, and no-direct-control cases.
- Committed the exact activated `oap/active` and 005-j order bytes unchanged.
- No production adapter, Gateway, protected Qwen, network, profile, or service
  configuration was changed.

## Acceptance evidence

### Criterion 1 — zero-inference preflight

- PASSED — `oap/active` selected exactly one matching `005-j` order.
- PASSED — Local PR #7 and Gateway PR #291 matched the exact required heads,
  parents, branches, open/non-draft/mergeable state, and successful checks
  before protected traffic.
- PASSED — Gateway 155-p was verified report-only with the exact safe artifact
  grammar and expected parent/path facts.
- PASSED — Exact Gateway source/support tests, route-default path ordering, and
  the bounded configured `4096` route-limit exercise passed without Gateway
  mutation.
- PASSED — Protected vision Qwen was active with PID `599296`, zero restarts,
  unchanged start-time class, authenticated health/models status 200, and the
  expected model visible. Text remained inactive; only the protected listener
  was present among 18020/18021/18031.
- PASSED — The full Local pre-live test and static/privacy/package gates passed,
  with only the eight explicit opt-in live/fixture skips recorded below.

### Criterion 2 — one corrected Local → protected Qwen verification

- PASSED — Exactly one Local dispatch occurred; no direct-provider control,
  retry, variant, or compiler call was run.
- PASSED — The expected request was JSON with top-level fields
  `input`, `max_output_tokens`, `model`, and `stream`; model matched, streaming
  was true, input had one item/one content item, tools/images were zero, the
  output-limit class was integer, and the body length was 169 bytes with an
  equality match.
- PASSED — Local stages A–I were all `PASSED`: 2xx/SSE headers, first bytes,
  framing, fixed-vocabulary recognition, one `response.created`, one valid
  terminal `response.completed` usage, normal close, and equal downstream byte
  count/digest with a parseable terminal lifecycle.
- PASSED — The protected stream contained no error or duplicate terminal event;
  compiler attempts were zero; the bounded downstream stream closed normally.
- PARTIAL — The runner did not emit nonempty first-byte and terminal timing
  buckets, which are required by the order. No timing claim is inferred from
  status/lifecycle success.

### Criterion 3 — final composed acceptance

- PARTIAL — One composed acceptance attempt was made from a clean detached
  Local worktree at implementation head `55d5e2c...` and the exact Gateway
  155-p checkout. It stopped before Local/Gateway startup and before any public
  Gateway or protected-Qwen request at the disposable relay readiness stage:
  `service_ready_timeout`.
- PASSED — The helper stopped without retry; its temporary Gateway/Local
  worktree, venv, Node runtime/cache, container state, listeners, and processes
  were removed. No protected traffic occurred during this composed attempt.
- NOT RUN — Official Codex-through-Gateway tool/governance, image, signed
  identity, cache/rehydration, isolation, replay/tamper, quota/accounting, and
  rollback acceptance because the composed service did not become ready.

## Verification

- `uv run --frozen pytest -q tests/test_local_qwen_provider_differential.py -rs`: PASSED — 10 passed.
- `uv run --frozen pytest -q -rs`: PASSED — 555 passed, 8 explicit skips.
- `uv run --frozen ruff check src tests scripts`: PASSED.
- `uv run --frozen ruff format --check src tests scripts`: PASSED — 58 files.
- `uv run --frozen mypy src tests`: PASSED — 53 source files.
- `uv build --wheel --sdist`: PASSED.
- `uv run --frozen python -m compileall -q src tests scripts`: PASSED.
- `find scripts oap/bin -type f -name '*.sh' -exec bash -n '{}' ';'`: PASSED.
- `git diff --check`: PASSED.
- Bounded real-secret-pattern scan: PASSED.
- Raw-logging scan: PASSED.
- Wheel package-boundary scan: PASSED — no `scripts/`, `tests/`, or `oap/`
  paths.
- Exact Gateway focused source/support tests in the disposable venv: PASSED.
- Protected-boundary invocation: PASSED for stages A–I, with the timing-bucket
  limitation recorded above; exactly one Local call and zero direct controls.
- Composed acceptance invocation: FAILED at pre-traffic
  `service_ready_timeout`; no retry.
- Post-run listener/process/container/temp-state checks: PASSED.
- Local PR #7 implementation-head `test`: SUCCESS.
- Gateway PR #291 exact-head checks: all ten SUCCESS.

## Live model/service evidence

- The protected vision service remained active before and after the one
  section-B request, with PID `599296`, zero restarts, and unchanged start-time
  class.
- Authenticated protected health and model visibility were HTTP 200 before and
  after section B; the expected model matched.
- Section B returned 2xx SSE with nonempty first bytes, one created/completed
  lifecycle, valid terminal usage, normal close, and byte/digest-equal Local
  downstream forwarding.
- The composed attempt made no public or protected inference request.
- No protected service, model, launch flag, credential source, network binding,
  active Codex profile, or text service was changed.

## GitHub CI / required checks

- Local implementation-head `test`: SUCCESS at
  `55d5e2c43322fd145af5672bab4e396816a2ff1c`.
- Gateway PR #291 at `306ecb186b5c12db991a684e7c04e5c9f174eba2`: all ten current
  checks SUCCESS.
- All required checks green while drafting: YES.
- Report-head checks may be pending; strategy verifies them independently.

## Local setup/dependencies

- Used the existing Local frozen repository environment for gates.
- Used a disposable Gateway-only venv and a checksum-verified temporary Node
  runtime solely to run the exact official Codex installation/support path.
- All driver-owned detached checkouts, venvs, Node/cache state, and temporary
  worktrees were removed after the composed attempt.
- An existing ignored Local `.venv` was preserved; it was not created or
  removed by this round.

## Documentation

Not updated. The order requires integration/runbook/completeness documentation
updates only on a complete composed pass; that pass stopped before traffic.
The bounded runner/test behavior is documented by the changed support code and
focused tests.

## Safety/scope confirmations

- Unrelated files: none committed; the implementation commit changed only the
  two bounded support files plus exact active/order transcript paths.
- Secrets, prompts, source, images, tool output, model text, identities,
  signatures, nonces, private endpoints, credentials, and raw request/response
  bodies were not committed or reported.
- Protected 18020/Qwen/Codex fixture changed: NO.
- Required tests skipped/not run: eight explicit existing opt-in live/fixture
  tests in the full suite; composed acceptance and its downstream matrix were
  not run after the readiness failure.
- Scope deviation: none; composed support readiness failure prevented the
  ordered final matrix.
- Extra objective PR: NO. Coding merge: NO.
- Active/order edited after activation: NO.
- Report commit report-only: YES.

## Known limitations/blockers

- The corrected boundary runner does not currently record the required
  first-byte and terminal timing buckets; section-B evidence is therefore
  partial despite A–I passing.
- The single composed attempt stopped at disposable relay readiness with
  `service_ready_timeout` before public/protected traffic. The order forbids a
  retry in this round.
- No claim is made for real Codex/Gateway/Qwen composed behavior, governance
  acquisition/injection through Gateway, cache/rehydration, isolation,
  replay/tamper, quota/accounting, rollback, production readiness, or cutover.

## Recommended strategic follow-up

- Review the timing-bucket support gap and the pre-traffic disposable relay
  readiness failure, then decide whether to issue a same-PR continuation that
  authorizes a fresh boundary/composed attempt. Preserve the unchanged direct
  Qwen rollback path.

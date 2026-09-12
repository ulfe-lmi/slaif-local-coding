# OAP Coding-Agent Report — 005-ag

## Work order

- Identifier: `005-ag`
- Order: `oap/orders/005-ag-canonical-replay-correlation.md`
- Numeric objective: `005`, canonical replay correlation and fake qualification
- PR mode: `AMENDED_EXISTING_PR`

## Status

PARTIAL

## Executive summary

The Local direct observer and replay companion now use the exact injected
Gateway validator's canonical replay candidates from validated streamed
function/custom-tool items. Terminal `response.completed` IDs are retained
only as bounded same/different/unknown diagnostics and are never replay
authority. The exact pinned fake qualification passed all 37 outer rows and
projections, the actual Codex 0.149.0 omission companion passed with a
canonical/summary identity divergence, all four synthetic protected cases
serialized as required, and no protected credential or Qwen request was made.

The implementation is marked `PARTIAL` because one bounded unauthenticated
`/v1/models` status-only probe was issued during live preflight despite the
order allowing only unauthenticated health-status facts. It returned `401`,
its response body was discarded, and no retry was made. No credential,
authenticated model/inference/compiler/vision request, protected mutation,
cutover, or merge occurred.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`
- PR: 7, https://github.com/ulfe-lmi/slaif-local-coding/pull/7
- State: OPEN, non-draft; merge state CLEAN at final implementation head
- Base/head: `main` / `oap/005-gateway-ingress-integration`
- Starting remote SHA: `96372f7708b805aab831d7c94de50851f1068dff`
- Implementation head SHA: `31dff85faf293883e367bb1fa3580d8cec9cc9d1`
- Report publication commit: SELF
- Implementation commits pushed before report:
  `6f2b87cc662da367d244bfa1ef0f7e5d4ef697dc`,
  `325edbffa1bdeb719f06d54b9bd8d1b288d14880`,
  `f83022da790ef747ae743f961401a2e04b555b8f`,
  `31dff85faf293883e367bb1fa3580d8cec9cc9d1`
- New PR this round: NO; amended existing PR: YES; merge performed: NO

## Changes and files

- `scripts/gateway_accounting_rehearsal.py`: exact-validator canonical
  candidate capture, terminal-summary diagnostic comparison, canonical
  companion construction, independently varying fake summary identity, and
  bounded replay evidence.
- `tests/helpers/transport_observer.py`: required replay-candidate validator
  capability, canonical opaque correlation registration after complete close,
  fail-closed candidate handling, and safe relationship evidence.
- `tests/test_gateway_accounting_rehearsal.py`: canonical/summary divergence,
  summary-only rejection, alias non-promotion, and companion regressions.
- `tests/test_transport_observer.py`: missing replay-capability pre-dispatch
  regression.
- `TESTING.md`: canonical replay authority, lifecycle, and safe evidence
  contract.
- `oap/evidence/005-ag/`: source-bound fake machine gate and synthetic
  protected-case evidence with artifact hashes.
- `oap/active` and the exact activated order were committed byte-for-byte as
  supplied; no prior order/report/evidence was edited.
- No `src/`, dependency, lock, version, binary, Gateway, or protected-host
  file was changed.

## Acceptance evidence

### Criterion A — validated canonical replay authority

- PASSED: the observer requires the validator's replay-candidate API before
  inference dispatch and consumes only candidates emitted by the validator for
  validated function/custom-tool items.
- PASSED: canonical candidates are bounded to opaque digests and registered
  only after terminal validation and normal close within the operation,
  session, and observer lifetime scope. Missing capability, malformed or
  ambiguous candidates, incomplete streams, and cross-scope relations fail
  closed.
- PASSED: terminal-summary IDs are not registered. The fresh fake provider
  emitted independently varying canonical streamed and terminal-summary
  identities; exact Gateway validation succeeded, the safe relation was
  `different`, and the canonical candidate was used for the continuation.
- PASSED: the actual omission companion used one streamed function-call
  response followed by one non-streaming continuation omitting only the
  optional item ID. Both requests were terminal-valid, the mandatory call
  relation matched, the admitted relationship remained the same, and the
  companion passed.

### Criterion B — decisive fake regressions and ownership negatives

- PASSED: focused observer/capture tests cover split and coalesced SSE,
  explicit and data-only frames, terminal lifecycle/close bounds, missing
  validator capability before delegate dispatch, canonical/summary divergence,
  summary-only rejection, and unowned summary alias rejection.
- PASSED: the actual unmodified Codex `0.149.0` fake C1–C5/D qualification
  returned `COMPLETE`, with 37/37 acceptance rows and 37/37 projections
  passed, zero missing/first-failure/retry results, and direct observer/fake
  provider counts matching.
- PASSED: direct fake dispatch totals were 26 attempted/dispatched/responded/
  completed/terminal-valid records: 6 compiler, 12 inference, and 8 other;
  the inference subset was 12/12 terminal-valid. The fake provider observed
  6 compiler and 12 inference calls across 6 streams.
- PASSED: the three actual pre-provider ownership negatives—missing call ID,
  mismatched call ID, and wrong key—were all `4xx`, with unchanged provider
  calls and primary/second-key accounting, zero pending reservations, and zero
  duplicate request IDs.
- PASSED: the shared synthetic protected branch serialized all 29 selected
  rows in each case. Healthy passed 29/29 with 6 compiler, 12 inference, and
  10 other dispatches; observer-failure, combined projection/cleanup-failure,
  and pre-dispatch mapping-dependency cases retained their primary/secondary
  failure facts and cleanup outcomes.
- PASSED: source-bound evidence is in
  `oap/evidence/005-ag/index.json`,
  `oap/evidence/005-ag/fake-machine-gate.json`, and
  `oap/evidence/005-ag/protected-synthetic-cases.json`. Artifact hashes match
  the index and no raw IDs, arguments, bodies, prompts, images, or tool output
  are retained.

### Criterion C — checks and protected boundary

- PASSED: exact Gateway execute pin `50dcc3b85d614eb1d0c6196595bf22ef5779f846`,
  Gateway app-tree digest, exact Codex binary digest, route policy, observer
  version, and source/module hashes are recorded in the evidence index.
- PASSED: the fake harness used only disposable loopback Gateway/Local state,
  a temporary PostgreSQL 16 tmpfs container, and exact owned cleanup. The
  runner reported processes/listeners/database/cache/Codex-home cleanup,
  secret-free logs, and temporary-state removal as true.
- PASSED: no real protected credential was resolved, no protected Qwen
  authenticated request was made, no inference/compiler/vision request was
  sent to the protected service, and no protected service/model/network/
  firewall/VPN/Codex-profile state was changed.
- PARTIAL: one unauthenticated `/v1/models` status-only preflight probe was
  made outside the order's health-only allowance; it returned `401`, no body
  was read or retained, and there was no retry.
- NOT RUN: protected acceptance, protected retry, cutover, release readiness,
  and merge remain unaccepted and were not attempted.

## Verification

- `uv run --frozen pytest -q`: PASSED — 791 passed, 8 skipped.
- `./.venv/bin/python -m pytest -q -o addopts='' tests/test_gateway_accounting_rehearsal.py tests/test_transport_observer.py`: PASSED — 130 passed.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen ruff format --check .`: PASSED — 275 files already formatted.
- `uv run --frozen mypy src tests`: PASSED — 57 source files.
- `uv run --frozen python -m compileall -q src tests scripts oap/bin`: PASSED.
- `bash -n oap/bin/*.sh`: PASSED.
- `uv lock --check`: PASSED.
- `uv pip check --python .venv/bin/python`: PASSED — all installed packages compatible.
- `uv build --wheel`: PASSED — wheel contained no `tests/` or `scripts/` members.
- `jq`/artifact-hash/privacy checks: PASSED — all evidence JSON parsed, hashes matched, and raw-content/credential scans found none.
- Exact pinned fake rehearsal with Gateway `50dcc3b…`, Codex `0.149.0`, and provider target `fake`: PASSED — 37/37 rows, 37/37 projections, canonical/summary `different`, omission companion, ownership negatives, synthetic protected cases, cleanup, and secret-free logs.
- Same-UID `_validate_fake_gate` on the generated final result: PASSED.
- `git diff --check`: PASSED.
- GitHub implementation-head required check `test`: PASSED — run `34448681488`, job `102779105616`, head `31dff85faf293883e367bb1fa3580d8cec9cc9d1`.

## Live model/service evidence

- Read-only final observation of `qwen-serving-vision.service`: active/running,
  MainPID `23961`, UID `1029`, start `Sun 2026-09-06 18:57:26 CEST`, and zero
  restarts. Port `18020` was listening; bounded unauthenticated `/health`
  status was `200`.
- The protected fixture was not authenticated or instrumented. No protected
  retry, model/compiler/inference/vision request, restart, rebind, or service
  mutation was performed.
- Protected Qwen/vLLM/model/network/firewall/VPN/Codex-profile mutation: NO.

## GitHub CI / required checks

- Implementation-head `test`: SUCCESS, run `34448681488`, job `102779105616`,
  head `31dff85faf293883e367bb1fa3580d8cec9cc9d1`.
- All required checks at report drafting: YES.
- Report-head checks may be pending; strategy verifies them independently.

## Local setup/dependencies

- Used the existing repository `.venv`, the disposable exact Gateway checkout
  and its Python environment, the exact Codex `0.149.0` binary, and the
  bounded sudo Docker helper for temporary PostgreSQL 16 tmpfs state.
- No host package, daemon, protected service, model, network, key, profile,
  dependency, or lockfile was changed.

## Documentation

Updated `TESTING.md` with the canonical replay-candidate authority,
terminal-summary diagnostic-only, lifecycle, capability, and safe-evidence
contract. Generated source-bound evidence is under `oap/evidence/005-ag/`.

## Safety/scope confirmations

- Unrelated files and all immutable prior OAP artifacts were preserved.
- No secrets, credentials, raw IDs, signatures, nonces, prompts, source,
  images, tool output, request/response bodies, or private URLs were committed
  or retained.
- Protected `18020`/Qwen/Codex fixture changed: NO.
- One unauthenticated `/v1/models` status-only probe was an order-boundary
  scope deviation; status `401`, body discarded, no retry.
- Required full fake and synthetic checks ran. Live protected acceptance,
  cutover, release, and merge were NOT RUN.
- Extra objective PR: NO. Coding merge/acceptance: NO.
- Active/order content edited after activation: NO.
- This report is the only file in the final publication commit: YES.

## Known limitations/blockers

- The order's protected acceptance remains intentionally not run; this round
  provides fake and synthetic-orchestration evidence only.
- The live preflight included the single documented unauthenticated model
  status probe outside the order's narrower health-only allowance, so status
  is `PARTIAL` for strategic review.
- Report-head CI may be pending after publication; strategy independently
  verifies its terminal state.

## Recommended strategic follow-up

Review the source-bound `005-ag` fake and synthetic evidence, the canonical
candidate/summary relation fields, and the documented live-preflight scope
deviation. Decide acceptance/continuation, protected testing, cutover, and
merge separately; this report does not make those decisions.

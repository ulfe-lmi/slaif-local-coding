# OAP Coding-Agent Report — 005-k

## Work order

- Identifier: `005-k`
- Order path: `oap/orders/005-k-final-product-topology-composed-acceptance.md`
- Numeric objective: `005`
- PR mode: `AMENDED_EXISTING_PR`

## Status

FAILED

## Executive summary

The bounded Section-A work passed: the evidence relay was removed from the
driver topology, the direct Gateway → Local → provider composition passed with
a fake provider, timing buckets were added and covered by a delayed-stream
test, and all repository/static/package gates passed. The one authorized
protected composed run then failed at the first standard streaming contract
check, reported as `stream_contract_failed`. It was not retried. The Codex
governance, image, replay/tamper, isolation, quota/accounting, and rollback
acceptance steps after that failure are not claimed.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`
- PR: [#7](https://github.com/ulfe-lmi/slaif-local-coding/pull/7)
- PR state: OPEN, non-draft, MERGEABLE/CLEAN
- Base/head: `main` / `oap/005-gateway-ingress-integration`
- Starting remote SHA: `d634d22e3591e4b6fb2f7f942cfe07c9582682d7`
- Implementation head SHA: `0dfe8efc429ed8d582e356aad85c3b50d22ed8b3`
- Report publication commit: SELF
- Implementation commits pushed before report: `0dfe8efc429ed8d582e356aad85c3b50d22ed8b3`
- New PR this round: NO
- Amended existing PR: YES, PR #7
- Merge performed: NO

The read-only Gateway dependency remained PR #291 at exact head
`306ecb186b5c12db991a684e7c04e5c9f174eba2`, with report-only parent
`a8a2a7a8a2e84fbe7dd42658173dd6358f709444`, open/non-draft/mergeable-clean,
and all ten required checks successful. No Gateway file or remote state was
changed.

## Changes and files

- Added bounded monotonic milestone timing to the Local differential facts and
  to the composed public streaming rehearsal. Only fixed latency buckets are
  emitted; private timestamps, payloads, IDs, and model text are excluded.
- Added a delayed fake-stream timing test covering response headers, first SSE
  bytes, terminal completion, and normal close.
- Consolidated the composed rehearsal around direct Gateway → Local → provider
  topology with fake/protected target modes, current Gateway PR conformance,
  fake provider lifecycle, cache/rehydration, accounting, image, tool, quota,
  and cleanup facts.
- Updated the repository-only Gateway compatibility fixtures to the exact
  current Gateway head and model/provider contract.
- Committed `oap/active` and the exact activated 005-k order unchanged.
- No production adapter, Gateway, protected Qwen, network, profile, or service
  configuration was changed.

## Acceptance evidence

### Criterion 1 — zero-protected-traffic harness closure

- PASSED — `oap/active` selected exactly one matching `005-k` order.
- PASSED — Local PR #7 and Gateway PR #291 matched the required exact heads,
  parents, branches, open/non-draft/mergeable state, and successful checks
  before the protected run.
- PASSED — The prior disposable readiness failure was classified as a
  non-product evidence-relay readiness failure. The final driver contains no
  relay or provider-side status endpoint.
- PASSED — The direct fake composition used the same seeded Gateway, Local,
  PostgreSQL, signed-identity, request, and cleanup path intended for the
  protected target.
- PASSED — Fake health/readiness, ordinary non-stream Responses, terminal SSE,
  image handling, disabled hosted-tool declarations, ordinary function/custom
  tools, cache/rehydration reuse, owner isolation, quota, controlled provider
  failure, accounting, log privacy, and teardown checks passed.
- PASSED — Protected read-only preconditions were preserved: vision service
  remained active with unchanged process/start/restart facts; text service
  remained inactive; the protected listener remained present; development and
  alternate text listeners were absent.
- PASSED — Full Section-A focused, regression, typing, formatting, lint,
  compilation, package, privacy, and fake-composition gates passed.

### Criterion 2 — one protected composed acceptance

- PASSED — Exactly one protected target run was started after Section-A gates
  passed. The driver used the direct Gateway → Local → protected-provider
  topology with no evidence relay.
- PASSED — The run reached the protected composed request matrix through the
  health/readiness, public model, and ordinary non-stream stages.
- FAILED — The first protected streaming contract check failed with the fixed
  driver result `stream_contract_failed`. The run stopped at that stage and no
  protected inference retry, alternate stream, prompt, or diagnostic control
  was issued.
- NOT RUN — Official Codex 0.149.0 governed tool/dependency acceptance, because
  the stream gate failed before the Codex step.
- NOT RUN — The later protected image, replay/tamper, hosted-choice, invalid
  key, over-quota, full accounting, compiler-public separation, and rollback
  matrix after the first stream failure.
- NOT RUN — Exact replay/tamper requests in the composed run; the direct
  driver records `NOT_RUN_NO_REQUEST_RELAY` and no request recorder was added.

### Criterion 3 — cleanup and protected-host preservation

- PASSED — The failed protected run stopped without retry and removed its
  candidate, Gateway, PostgreSQL, fake/failure, cache, Codex, log, and temporary
  state.
- PASSED — No driver-owned task listener, temporary process, or PostgreSQL
  container remained; port 18031 and the alternate text listener were absent.
- PASSED — Protected Qwen service process/start/restart/listener facts were
  unchanged after the run; the text service remained inactive.
- PASSED — The detached Gateway checkout was clean and the protected service
  configuration, model, launch flags, credentials, network bindings, and
  active Codex profiles were not changed.

## Verification

- `uv run --frozen pytest -q`: PASSED — 557 passed, 8 explicit skips.
- Focused Local/Gateway/identity/image/tool/pipeline suite: PASSED — 111
  passed.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen ruff format --check .`: PASSED.
- `uv run --frozen mypy src tests`: PASSED — 53 source files.
- `python3.12 -m compileall -q src tests oap/bin`: PASSED.
- `uv build`: PASSED — wheel and source distribution built.
- Wheel package-boundary check: PASSED — no `scripts/`, `tests/`, or
  `references/` paths in the wheel.
- `git diff --check`: PASSED.
- Fake composed rehearsal: PASSED — direct topology, safe accounting, timing,
  privacy, and cleanup facts passed.
- Protected composed rehearsal: FAILED — first stream contract stage reported
  `stream_contract_failed`; no retry.
- Local PR #7 implementation-head `test`: SUCCESS at the implementation head.
- Gateway PR #291 exact-head checks: all ten SUCCESS.

## Live model/service evidence

- The protected vision service remained active before and after the one
  authorized composed run, with unchanged process/start/restart facts.
- The protected text service remained inactive, and no alternate text or
  development listener remained after cleanup.
- The protected composed run failed at the first standard streaming contract
  stage. No claim is made for terminal streaming acceptance or byte-exact
  composed forwarding from that run.
- No protected service, model, launch flag, credential source, network binding,
  active Codex profile, or text service was changed.

## GitHub CI / required checks

- Local implementation-head `test`: SUCCESS at
  `0dfe8efc429ed8d582e356aad85c3b50d22ed8b3`.
- Gateway PR #291 at exact head `306ecb186b5c12db991a684e7c04e5c9f174eba2`:
  all ten required checks SUCCESS.
- All required checks were green before report publication: YES.
- Report-head checks may be pending; strategy verifies them independently.

## Documentation

Not updated. The order requires the integration, runbook, and Objective-005
completeness documentation updates only on a complete protected composed pass;
that pass failed at its first streaming contract stage.

## Safety/scope confirmations

- Unrelated files: none committed; the implementation commit changed only the
  bounded support/tests/fixture files plus the exact active/order transcript.
- Secrets, prompts, source, images, tool output, model text, identities,
  signatures, nonces, private endpoints, credentials, and raw request/response
  bodies were not committed or reported.
- Protected Qwen/service/network/profile state changed: NO.
- Required tests skipped/not run: the eight explicit existing opt-in skips;
  downstream protected acceptance stages listed above were not run after the
  first stream failure.
- Extra objective PR: NO. Coding merge: NO.
- Active/order edited after activation: NO.
- Report commit report-only: YES.

## Known limitations/blockers

- The single protected composed run failed at `stream_contract_failed`. The
  ordered no-retry rule prevents further protected diagnosis in this round.
- No claim is made for real Codex governance/tool behavior, image acceptance,
  replay/tamper enforcement in the composed path, isolation, quota/accounting
  completion for the protected matrix, rollback, production readiness, or
  persistent cutover.

## Recommended strategic follow-up

Review the fixed stream-contract failure evidence and decide whether to issue a
new same-PR continuation that authorizes a fresh protected composed attempt.
Preserve the unchanged direct-Qwen rollback path.

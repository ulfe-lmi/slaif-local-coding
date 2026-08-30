# OAP Coding-Agent Report — 005-l

## Work order

- Identifier: `005-l`
- Order path: `oap/orders/005-l-exact-composed-stream-owner-and-acceptance-closure.md`
- Numeric objective: `005`
- PR mode: `AMENDED_EXISTING_PR`

## Status

FAILED

## Executive summary

The zero-protected-traffic stream-contract closure passed, including the
complete fake direct Gateway → Local → fake-provider composition and cleanup.
The one authorized protected composed run reached the standard non-stream
request, then stopped at the first protected streaming decision. The fixed
first failure was `gateway_error_event`. No retry, second stream, or later
matrix step was performed.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`
- PR: [#7](https://github.com/ulfe-lmi/slaif-local-coding/pull/7)
- PR state: OPEN, non-draft, MERGEABLE/CLEAN
- Base/head: `main` / `oap/005-gateway-ingress-integration`
- Required 005-k report head: `e4f72e2fdb3b655b302c6fd986d75b8b5d14acda`
- Implementation head SHA: `2d1e362f4e1bf7eb6b4f29f9f116ed612fce9e78`
- Report publication commit: SELF
- Implementation commits pushed before report: `2d1e362f4e1bf7eb6b4f29f9f116ed612fce9e78`
- New PR this round: NO
- Amended existing PR: YES, PR #7
- Merge performed: NO

The read-only Gateway dependency remained PR #291 at exact head
`306ecb186b5c12db991a684e7c04e5c9f174eba2`, OPEN, non-draft,
MERGEABLE/CLEAN, with all ten observed required checks SUCCESS. No Gateway
file or remote state was changed.

## Changes and files

- Reused the bounded 005-j `SSEFacts` parser incrementally for the public
  composed stream; no second event parser or whole-stream buffer remains.
- Added fixed `ComposedStreamFacts`, the exact ordered first-failure enum,
  safe timing/count classes, terminal validity fields, error-field classes,
  Local metric deltas, Gateway accounting terminality, and direct owner
  mapping.
- Added exhaustive pure fake cases for every first-failure branch, split
  chunks, reasoning vocabulary, provider/Gateway error events, and privacy
  projection.
- Removed the dormant older rehearsal runner and obsolete relay/path/status
  diagnostics; the direct rehearsal remains repository-only and the wheel is
  unchanged.
- Extended the bounded SSE facts with terminal status/output/usage validity
  and fixed error metadata classes.
- Committed the exact activated `oap/active` and 005-l order bytes unchanged.

## Acceptance evidence

### Criterion 1 — zero-protected-traffic stream evidence closure

- PASSED — Exact Local and Gateway heads, PR states, required checks, and
  activation transcript were verified before protected traffic.
- PASSED — The ordered first-failure enum contains all 17 specified values and
  pure tests exercise each value in order.
- PASSED — The shared bounded parser handled large/arbitrarily split input,
  recognized Qwen reasoning/tool event vocabulary, unknown events, malformed
  input, provider/Gateway errors, duplicate/missing terminal events, invalid
  terminal usage/output/status, early close, timing gaps, Local failure, and
  accounting mismatch without raw-value projection.
- PASSED — The complete fake direct Gateway → Local → fake-provider rehearsal
  returned `stream_contract_passed`, with `2xx`/SSE, created/completed count
  classes `1`/`1`, valid status/output/usage/ID relation, normal close, one
  provider-call class, terminal reservation/ledger, Local request and stream
  duration deltas of `1`, zero failure delta, and secret-free logs.
- PASSED — Fake PostgreSQL/container, listener, temporary-state, and process
  cleanup completed.

### Criterion 2 — one protected composed acceptance

- PASSED — One disposable protected composition used the exact Gateway head,
  Local implementation head, temporary PostgreSQL, official Codex `0.149.0`
  binary, direct Gateway → Local → protected-Qwen topology, and no relay or
  direct-provider call.
- PASSED — Local/Gateway readiness, authenticated model visibility, and one
  standard non-stream Responses request with usage completed.
- FAILED — The standard stream produced these fixed facts before stopping:
  - status class `2xx`; content type class `sse`;
  - response-header timing `10-49ms`; first-byte timing `10-49ms`;
    terminal timing `missing`; normal-close timing `250-999ms`;
  - byte-count class `129-4096`; chunk-count class `3`; normal close `true`;
  - parseable `true`; recognized vocabulary `true`; error event `true`;
    Gateway error event `true`; duplicate terminal `false`;
  - created count class `1`; completed count class `0`; response-ID relation
    `true`;
  - terminal status/output/usage validity `false`/`false`/`false`;
  - fixed error-field set `code,message,param,request_id,status,type`, with
    error code/type classes `unknown`/`unknown`;
  - Local request delta `1`; stream-duration delta `1`; failure delta `1`;
    Local upstream status class `2xx`; Local failure class `disconnect`;
    Local terminal bytes `false`;
  - Gateway reservation terminal `false`; ledger terminal `true`; provider
    call-count class `1`;
  - first failure `gateway_error_event`; owner `local_or_provider_owned`.
- NOT RUN — Real Codex governance/tool, image, cache/rehydration, identity,
  isolation, replay/tamper, quota, full accounting, and rollback steps after
  the stream gate.

### Criterion 3 — cleanup and protected-host preservation

- PASSED — The protected run stopped immediately after the first stream
  failure; no second stream or diagnostic retry was issued.
- PASSED — Driver-owned Gateway/Local/PostgreSQL/fake/temp state was removed;
  no task container or 18021/18031 listener remained.
- PASSED — Protected vision service PID/start/listener invariants remained
  unchanged; text service remained inactive; no image proxy was present.
- PASSED — Protected model, service, launch flags, credentials, network,
  active Codex profile, and Gateway state were not changed.

## Verification

- `uv run --frozen pytest -q tests/test_gateway_accounting_rehearsal.py tests/test_local_qwen_provider_differential.py`: PASSED — 35 passed.
- `uv run --frozen pytest -q -rs`: PASSED — 578 passed, 8 explicit opt-in skips.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen ruff format --check .`: PASSED — 229 files.
- `uv run --frozen mypy src tests`: PASSED — 53 source files.
- `python3.12 -m compileall -q src tests scripts oap/bin`: PASSED.
- `find scripts oap/bin -type f -name '*.sh' -exec bash -n '{}' ';'`: PASSED.
- `uv build --wheel --sdist`: PASSED.
- Wheel package-boundary scan: PASSED — no `scripts/`, `tests/`, `references/`,
  or `oap/` paths.
- Real-secret-pattern scan: PASSED.
- `git diff --check`: PASSED.
- Fake composed rehearsal: PASSED — direct topology, complete stream facts,
  safe accounting, privacy, and cleanup.
- Protected composed rehearsal: FAILED — first failure
  `gateway_error_event`; stopped without retry.

## Live model/service evidence

- One read-only protected health/models preflight returned HTTP 200 for both
  endpoints before the composed run.
- The protected vision fixture was active with its listener present; the text
  fixture was inactive; 18021 and 18031 were absent before and after.
- Protected stream safe facts are recorded under Criterion 2. No claim is made
  for terminal stream acceptance or the downstream matrix.
- No protected service, model, launch flag, credential source, network binding,
  active Codex profile, or Gateway state was changed.

## GitHub CI / required checks

- Local implementation-head `test`: SUCCESS at
  `2d1e362f4e1bf7eb6b4f29f9f116ed612fce9e78`.
- Gateway PR #291 exact-head checks: all ten observed checks SUCCESS at
  `306ecb186b5c12db991a684e7c04e5c9f174eba2`.
- All required checks were green before report drafting: YES.
- Report-head checks may be pending; strategy verifies them independently.

## Local setup/dependencies

- Used the frozen Local repository environment for repository gates.
- Used a fresh detached Gateway checkout pinned to the exact required head and
  a disposable venv for the fake/protected composition.
- Used one official `postgres:16` container with loopback-only random port,
  tmpfs data, finite readiness, and automatic cleanup. The newly pulled image
  was removed after the rehearsal.
- Preserved the existing ignored Local `.venv`; no protected environment was
  changed.

## Documentation

Not updated. The order requires integration, runbook, and Objective-005
completion-document updates only after a complete protected stream/full-matrix
pass, which did not occur.

## Safety/scope confirmations

- Secrets, prompts, source, images, model text, tool output, credentials,
  identities, signatures, nonces, private endpoints, request/response bodies,
  and arbitrary exceptions were not committed or reported.
- Protected Qwen/service/network/profile state changed: NO.
- Gateway PR #291 changed: NO.
- Protected traffic: exactly one composed run and one standard stream; no
  retry, alternate request, direct provider call, or evidence relay.
- Required downstream protected tests were not run after the ordered stream
  failure; the 8 opt-in local suite skips remain explicit, not pass claims.
- Extra objective PR: NO. Coding merge: NO.
- Active/order edited after activation: NO.
- Report commit report-only: YES.

## Known limitations/blockers

- The sole protected stream stopped at `gateway_error_event`; it did not emit
  `response.completed` and had a Local disconnect failure delta. The evidence
  maps to `local_or_provider_owned` under the ordered law, while accepted
  005-j direct A–I evidence remains green. No Local or Gateway product fix is
  established or made by this round.
- No claim is made for real Codex governance/tool behavior, image acceptance,
  cache/rehydration, identity/isolation, replay/tamper, quota/accounting
  completion, rollback, production readiness, or persistent cutover.

## Recommended strategic follow-up

Review the exact bounded stream facts and the accepted 005-j direct comparison,
then decide whether to issue a same-PR continuation with a new protected
attempt and owning-layer direction. Preserve the unchanged direct-Qwen
rollback path.

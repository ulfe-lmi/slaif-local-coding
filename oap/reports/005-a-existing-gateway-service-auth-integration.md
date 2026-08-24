# OAP Coding-Agent Report — 005-a

## Work order

- Identifier: `005-a`
- Order path: `oap/orders/005-a-existing-gateway-service-auth-integration.md`
- Numeric objective: `005`
- PR mode: `CREATED_NEW_PR`

## Status

COMPLETE

## Executive summary

Added an optional loopback-only adapter-side service-Bearer ingress boundary.
Enabled mode authenticates exactly one configured service credential with
constant-time comparison before request-body, image, constitution, compiler,
cache, or upstream work. The existing static constitution identity remains the
only cross-request identity and is documented as single-user local-appliance
scope. Added bounded gateway conformance vectors/fake-upstream tests and the
requested unchanged-gateway and rollback-first documentation. No gateway,
protected Qwen, Codex profile, network, or cutover state was changed.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #7 — https://github.com/ulfe-lmi/slaif-local-coding/pull/7 — OPEN
- Base/head: `main` / `oap/005-gateway-ingress-integration`
- Starting remote SHA: `570bd2b24ad4b041a07e0320d5ed44bc73e99ad5`
- Implementation head SHA: `0a4a12d8efbb452bdccbd5daaf6c84f751104fd9`
- Report publication commit: SELF
- Implementation commits pushed before report: `bc2297831a54fec428f27e3d55d3d7c0f46b7005`, `0a4a12d8efbb452bdccbd5daaf6c84f751104fd9`
- New PR this round: yes; amended existing: no; merge performed: NO

## Changes and files

- Added validated `[gateway_ingress]` configuration, bounded environment-secret
  validation, static-identity enablement checks, and fixed readiness state.
- Added pre-transform service authorization handling for `/health`,
  `/v1/models`, `/v1/responses`, and `/v1/chat/completions`, including duplicate,
  malformed, wrong-scheme, oversized, missing, and mismatch rejection.
- Preserved Qwen upstream credential substitution and stripped service,
  public-client, forwarding, cookie, and spoofed internal headers.
- Added fake-upstream auth, isolation, image/tool/usage/SSE, readiness, config,
  vector, and privacy coverage.
- Updated adapter, security, README, service-example, gateway-boundary, and
  controlled-cutover/rollback documentation.

## Acceptance evidence

### Criterion A — explicit ingress service authentication

- PASS: strict disabled default and enabled `service_bearer_static_identity`
  configuration are validated; enabled mode requires a valid environment name,
  referenced nonempty bounded secret, loopback server configuration, and the
  complete enabled static constitution identity.
- PASS: invalid, duplicate, malformed, wrong-scheme, empty, oversized, and
  mismatched authorization requests return fixed OpenAI-shaped 401/403 results;
  missing configured runtime secret returns fixed 503; no rejected request calls
  fake upstream or writes a derived cache entry.
- PASS: valid requests reach fake upstream with only the configured Qwen
  credential; service authorization and spoofed/internal headers do not cross
  the upstream boundary.

### Criterion B — static identity honesty and isolation

- PASS: constitution identity remains configuration-only
  `principal`/`session`/`repository` data and is not derived from headers,
  cookies, public credentials, IPs, request IDs, model strings, or bodies.
- PASS: tests prove different spoofed identity/header values cannot override the
  configured appliance identity. Documentation records that this contract
  cannot represent isolated per-public-user principals and does not claim
  multi-user production isolation.

### Criterion C — unchanged-gateway conformance boundary

- PASS: repository-owned bounded vector and fake-upstream tests cover the
  gateway-shaped service Bearer request, model route, Responses text, SSE,
  function/tool continuation shape, usage preservation, image policy, error
  sanitization, header stripping, zero rejected-work calls, and privacy.
- NOT RUN: disposable pinned gateway-main executable driver; no gateway checkout,
  service, or dependency stack is installed on hinton1. This is explicitly not
  claimed as cross-repository executable proof. Activation evidence records
  gateway `main` at `8f2813bf745b90221da33a7cfaf40726c5b1b480` and the existing
  generic provider contract as read-only authority.

### Criterion D — contract and coordination documentation

- PASS: `docs/SLAIF-GATEWAY-INTEGRATION.md` records the exact service-Bearer
  contract, static single-user limit, usage boundary, dated gateway SHA,
  candidate Codex 0.148/0.149 mismatch, evidence table, non-active signed
  identity sketch, and cross-repository PR rule. No gateway code was changed.

### Criterion E — controlled cutover preparation

- PASS: rollback-first gates cover accepted/pinned versions, backups/hashes,
  candidate `18031`, gateway-to-adapter-only routing, bounded client/Codex
  checks, quota/ledger usage, active-turn safety, direct-vLLM retention,
  exact rollback, and independent listener/firewall/VPN/service verification.
- NOT RUN: live gateway cutover and rollback; no gateway service is installed or
  running on hinton1. Protected Qwen remains the direct private fixture.

### Criterion F — verification and protected-host safety

- PASS: fake-upstream, static/unit, package, privacy, and live read-only health
  checks below. No protected model call was required by the order.
- PASS: the active vision fixture remains `qwen-serving-vision.service`, text
  unit remains inactive, port `18020` remains the sole observed Qwen listener,
  and bounded `/health` returned HTTP 200. No service/profile/network mutation.

## Verification

- `uv run --frozen --extra dev pytest -q`: PASSED — 450 passed, 8 skipped; live/model-gated skips remain explicitly skipped.
- `uv run --frozen --extra dev ruff format --check src tests`: PASSED.
- `uv run --frozen --extra dev ruff check src tests`: PASSED.
- `uv run --frozen --extra dev mypy src tests`: PASSED.
- `uv build --wheel --sdist`: PASSED — wheel and source distribution built.
- `uv run --frozen --extra dev python -m compileall -q src tests`: PASSED.
- `uv run --frozen python -c ... load_settings(adapter.example.toml)`: PASSED — disabled example configuration validates.
- `git diff --check`: PASSED.
- `gh pr checks 7`: PASSED — required `test` check SUCCESS at implementation SHA; an earlier pre-fix run failed only on test typing and was repaired in the pushed implementation head.
- `systemctl --user`/`ss` read-only fixture inspection: PASSED — vision unit active, text unit inactive, port `18020` observed, no `18021`/`18031` listener.
- bounded authenticated loopback `/health`: PASSED — HTTP 200; response body not retained or reported.
- pinned gateway-main executable driver: NOT RUN — no gateway service/dependency stack.
- gateway cutover/rollback: NOT RUN — explicitly outside `005-a` execution.

## Live model/service evidence

- Endpoint/route: private loopback Qwen service, port `18020`, `/health` only.
- Result: HTTP 200 from one bounded read-only call; no prompt, image, tool,
  model-response, or credential content retained.
- Fixture: `qwen-serving-vision.service` active/running; `qwen-serving.service`
  inactive/dead; no candidate adapter was left running; protected state unchanged.

## GitHub CI / required checks

- Implementation head: `0a4a12d8efbb452bdccbd5daaf6c84f751104fd9`.
- Required check: `test` — SUCCESS, run `32696865692`, job `97340521735`.
- All required checks green at drafting: yes.
- Report-head checks may be newly pending after publication; strategy verifies
  the final report head independently.

## Local setup/dependencies

- Used the existing repository `uv` environment with frozen dev dependencies.
- No gateway clone, gateway dependency install, sudo, service install, or
  protected environment-file access was performed.
- `uv build` produced only ignored local `dist/` artifacts.

## Documentation

Updated: `README.md`, `SECURITY.md`, `config/adapter.example.toml`,
`docs/ADAPTER-CONFIGURATION.md`, `docs/SLAIF-GATEWAY-INTEGRATION.md`, and
`packaging/slaif-local-coding.service.example`. The activated order and active
selector were committed byte-for-byte as received.

## Safety/scope confirmations

- Unrelated files: none staged or committed.
- Secrets/raw content: no real credentials, raw prompts, source, images, tool
  output, private URLs, or request/response bodies entered code, vectors, logs,
  or this report.
- Protected `18020`/Qwen/Codex fixture changed: NO.
- Required tests skipped/not run: cross-repository executable gateway driver,
  live gateway cutover/rollback, and protected model matrix; all are reported
  explicitly above. Fake-upstream and repository gates ran.
- Extra objective PR: NO. Coding merge: NO.
- Active/order edited by coding: NO; unchanged activated bytes were committed.
- Report commit report-only: yes; this report is the only final-commit path.

## Known limitations/blockers

- Service-Bearer mode is intentionally single-user static identity. Trusted
  signed per-user principal/session/repository isolation is not implemented.
- The gateway executable provider-adapter driver and actual gateway path remain
  `NOT RUN` because the gateway service/dependencies are absent on hinton1.
- No production, multi-user, public-listener, cutover, direct-vLLM retirement,
  or generic vision/readiness claim is made.

## Recommended strategic follow-up

- Independently review PR #7, the fake-contract evidence, and the explicit
  missing signed-identity/cross-repository driver evidence.
- If accepted, coordinate a separate gateway-side objective and later
  rollback-proven cutover order; do not infer either from this report.

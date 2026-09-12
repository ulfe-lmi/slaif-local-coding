# OAP Coding-Agent Report — 005-f

## Work order

- Identifier: `005-f`
- Order path: `oap/orders/005-f-signed-request-identity-adapter-contract.md`
- Numeric objective: `005`
- PR mode: `AMENDED_EXISTING_PR`

## Status

COMPLETE

## Executive summary

Implemented the Local Coding adapter side of signed gateway identity v1 behind
an explicit, disabled-by-default configuration mode. Service Bearer
authentication remains first; the adapter verifies a separate HMAC-bound,
versioned identity over the exact request method/path/raw-query/body facts,
rejects malformed/stale/replayed requests with fixed safe errors, and passes an
immutable verified identity through the constitution compiler/cache/selection/
injection/rehydration path. Added canonical synthetic conformance vectors,
replay/concurrency/privacy/fake-upstream coverage, and updated the future
gateway/tool-filter proposal. The gateway and protected model were not changed
or called.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`
- PR: [#7](https://github.com/ulfe-lmi/slaif-local-coding/pull/7)
- PR state: OPEN, non-draft, MERGEABLE; no merge or auto-merge performed
- Base/head: `main` / `oap/005-gateway-ingress-integration`
- Starting remote SHA: `a9874b99e36dc639ddcbea067930a99539b7c73a`
- Implementation commits pushed before report: `e0da2ded1d3d3bbf7ba216a543b70421a5628fe7`, `d235d1ac3d5b4e99158098b79d280624167efe50`
- Implementation head SHA: d235d1ac3d5b4e99158098b79d280624167efe50
- Report publication commit: SELF
- New PR this round: NO
- Amended existing PR: YES, PR #7
- Merge performed: NO

## Changes and files

- Added `service_bearer_signed_identity_v1`, separate signing-secret validation,
  explicit v1/policy settings, clock/replay/nonce bounds, and signed-versus-
  static constitution identity validation.
- Added canonical UTF-8 signing bytes, constant-time HMAC-SHA256 verification,
  case-insensitive unique-header validation, opaque-field grammar, timestamp
  window checks, and bounded SHA-256 nonce-digest TTL/LRU replay protection.
- Enforced service-auth-first and signed-verification ordering before request
  transformation; verified route matching occurs before image/tool/constitution
  work; service/signed/internal headers are stripped before Qwen.
- Added immutable `RequestIdentity` propagation through compiler/cache and
  zero-root rehydration identity matching without pipeline-global state.
- Added `tests/fixtures/gateway/signed_identity_v1_vectors.json` and
  `tests/test_gateway_identity.py`.
- Updated adapter configuration, security/testing contracts, README, gateway
  integration contract, and route-scoped tool-filter proposal.
- Preserved the activated `oap/active` and exact order bytes in the
  implementation commit.

## Acceptance evidence

### Criterion 1 — versioned modes and safe configuration

- `disabled`, `service_bearer_static_identity`, and
  `service_bearer_signed_identity_v1` are validated explicitly.
- Signed mode requires a separate visible-ASCII HMAC secret (32–4096 bytes),
  bounded clock skew/replay TTL/nonce state, enabled compiler/constitution/
  observed route integration, and `identity_source = "signed_request"`.
- Disabled/static modes reject signed-only settings; signed mode rejects static
  identity fallback. Existing disabled/static tests remain green.

### Criterion 2 — exact wire contract and ordering

- The canonical domain/version, method, path, SHA-256 raw query, SHA-256 exact
  bounded body, principal, session, repository, route, timestamp, and nonce are
  joined by UTF-8 newlines with no trailing newline.
- Header case, duplicates, grammar, timestamp canonicality, nonce bounds,
  signature shape, body/query/path/method/identity/route tampering, and fixed
  401/403/409/422/503 outcomes are covered.
- Service authentication is checked before body reading; valid signed identity
  is checked before JSON transformation; route mismatch is rejected before
  image/tool/compiler/cache/upstream work.

### Criterion 3 — replay and identity isolation

- Invalid signatures do not reserve nonce state; exact and concurrent replays
  are rejected atomically; TTL expiry and LRU/entry bounds are tested.
- The verified immutable identity is passed per request and used in compiler
  cache and rehydration dimensions. Two concurrent identities are captured
  separately with no mutable “last request” state.
- Signed/internal headers and identity/secret/body values are absent from fake
  Qwen forwarding, public errors, metrics/log checks, and cache naming paths.

### Criterion 4 — cross-repository boundary

- The synthetic vector contains exact canonical/HMAC facts and accept/reject
  cases without real credentials or private identifiers.
- Gateway proposal updates require gateway-managed owner/session/repository
  truth, key separation/rotation/replay controls, route capability, and one
  coordinated gateway change. Gateway support remains `NOT IMPLEMENTED` and
  `NOT AUTHORIZED`; no gateway source was copied or changed.

## Verification

- `uv run --frozen pytest -q tests/test_gateway_identity.py`: PASSED — 15 passed.
- `uv run --frozen pytest -q`: PASSED — 545 passed, 8 explicit environment/live skips.
- `uv run --frozen ruff check src tests`: PASSED.
- `uv run --frozen ruff format --check src tests`: PASSED.
- `uv run --frozen mypy src tests`: PASSED — 52 source/test files checked.
- `uv build --wheel --sdist`: PASSED — sdist and wheel built.
- `uv run --frozen python -m compileall -q src tests`: PASSED.
- `git diff --check`: PASSED.
- Redacted raw-log/secret scan: PASSED — no production raw-payload logging
  match; synthetic signing value exists only in the test vector.
- Initial CI on the first implementation commit exposed only strict typing
  errors in the new test helper; the in-scope repair was pushed as the second
  implementation commit. Current implementation-head CI is recorded below.

## Live model/service evidence

- Read-only host inspection only; no Qwen API/model call, adapter listener,
  gateway, Docker, PostgreSQL, or Codex profile operation was performed.
- Existing protected vLLM process was observed serving `qwen3.8-27b` on port
  `18020`, with `max-model-len=100000`, `max-num-seqs=1`,
  `limit-mm-per-prompt={"image":1}`, and `reasoning-parser=qwen3`.
- Port `18020` remained present; ports `18021` and `18031` were absent. The
  user `qwen-serving.service` unit was not changed or restarted. Protected
  Qwen/model/network state changed: NO.
- Vision/text API matrix: NOT RUN — explicitly prohibited by this order; the
  bounded process/profile evidence above is not a model-call acceptance claim.

## GitHub CI / required checks

- Implementation-head check: `test` SUCCESS on
  `d235d1ac3d5b4e99158098b79d280624167efe50`.
- Check URL:
  https://github.com/ulfe-lmi/slaif-local-coding/actions/runs/32708407371/job/97374394222
- All required checks green at drafting: YES.
- Report-head checks may be pending; strategy verifies them independently.

## Local setup/dependencies

- Used the existing repository `.venv` through `uv run --frozen`; no dependency
  or lockfile changes.
- Built only repository-local sdist/wheel artifacts; no service, listener, model,
  network, credential, or protected-host mutation.

## Documentation

Updated: `README.md`, `SECURITY.md`, `TESTING.md`,
`config/adapter.example.toml`, `docs/ADAPTER-CONFIGURATION.md`,
`docs/SLAIF-GATEWAY-INTEGRATION.md`, and
`docs/GATEWAY-ROUTE-SCOPED-CODEX-TOOL-FILTER-PROPOSAL.md`.

## Safety/scope confirmations

- Unrelated/pre-existing work: preserved; the activated order and `oap/active`
  were committed unchanged from their pre-existing activated bytes.
- Secrets/raw customer content/prompts/source/images/tool output: not exposed
  or persisted; only synthetic vector material is present in the test fixture.
- Protected `18020`/Qwen/Codex fixture changed: NO.
- Required tests skipped/not run: live Qwen/model and gateway tests are NOT RUN
  by order; 8 existing local tests reported SKIPPED by their own environment
  gates. They are not counted as passed.
- Scope deviation: none.
- Extra objective PR: NO.
- Coding merge: NO.
- Active/order edited: NO.
- Report commit report-only: YES.

## Known limitations/blockers

- The current gateway provider still emits no signed identity and rejects the
  relevant Codex hosted-tool envelope; gateway enablement, route capability,
  key derivation/rotation, accounting, and cutover remain outside this order.
- No live Qwen or gateway acceptance is claimed.

## Recommended strategic follow-up

- Coordinate a separate authorized gateway OAP PR against the vector and exact
  adapter contract, including gateway-managed identity derivation, key
  rotation/replay tests, route capability, and cross-repository acceptance.
- Independently verify the report-head parent/path/content and any post-report
  CI status before acceptance or merge.

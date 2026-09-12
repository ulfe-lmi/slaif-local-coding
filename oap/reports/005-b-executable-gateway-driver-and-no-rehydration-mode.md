# OAP Coding-Agent Report — 005-b

## Work order
- Identifier: `005-b`
- Order path: `oap/orders/005-b-executable-gateway-driver-and-no-rehydration-mode.md`
- Numeric objective: `005`
- PR mode: `AMENDED_EXISTING_PR`

## Status
COMPLETE

## Executive summary
Hardened configured and supplied service-token validation with one visible-ASCII
encoded-byte validator, added an explicit bounded rehydration disable switch,
added hermetic repository-only gateway-driver support, executed the actual
pinned gateway provider adapter against a temporary Local Coding listener and
fake vLLM, and documented the unchanged gateway identity boundary and safe
shared-Bearer degradation. No gateway repository, protected model service, or
cutover state was changed.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`
- PR: [#7](https://github.com/ulfe-lmi/slaif-local-coding/pull/7), OPEN, non-draft, merge state CLEAN
- Base/head: `main` / `oap/005-gateway-ingress-integration`
- Starting remote SHA: `2af482ada355c1fd6708c25f0f4718bd71ea6d4c`
- Implementation head SHA: 31f25aab09d185f1696d841f1c58be0da1ef6f38
- Report publication commit: SELF
- Implementation commits pushed before report: `31f25aab09d185f1696d841f1c58be0da1ef6f38` (`OAP 005-b harden gateway driver and rehydration mode`)
- New PR this round: NO; amended existing PR: YES; merge performed: NO

## Changes and files
- Shared `validate_service_token` enforces nonempty visible ASCII bytes,
  encoded length up to 4096, and parity between environment and request paths;
  malformed Bearer syntax remains fixed/non-reflecting.
- `[constitution.rehydration].enabled` defaults to `true`; when false, current
  root governance still injects, zero-root requests preserve post-image-policy
  input, and the process-local map is neither populated nor consulted.
- Added `scripts/gateway_provider_driver.py` and content-free helper/facts tests;
  driver support is outside the production wheel.
- Updated configuration, service example, adapter/gateway contract, runbook,
  and README limitations/evidence.
- Activated order and active selector were committed unchanged as orchestration
  transcript artifacts.

## Acceptance evidence
### Criterion A — service-token syntax hardening
- PASSED: one shared validator covers environment and supplied tokens; tests
  cover one-byte, 4096-byte, and 4097-byte boundaries, all ASCII control/space
  and DEL values, Unicode/Unicode whitespace, embedded/leading/trailing
  whitespace, malformed schemes/separators, and duplicate authorization headers.
- PASSED: comparison occurs only after validation; failures use fixed status and
  error envelopes without token reflection.
- PASSED: systemd example now describes credential variable assignments rather
  than an environment-variable name.

### Criterion B — explicit rehydration disable
- PASSED: default remains enabled and existing enabled behavior continues to
  rehydrate without a compiler call.
- PASSED: disabled fake-upstream sequence injects the observed root for the
  current request, leaves the rehydration map empty, and preserves the following
  zero-root request; metrics contain only fixed disabled/rehydration-disabled
  reasons for that path.
- PASSED: existing identity/root-hash/TTL/LRU/byte-bound tests remain green;
  content-addressed compiler/cache behavior is independent of zero-root memory.

### Criterion C — executable pinned gateway provider driver
- PASSED: detached gateway checkout SHA
  `8f2813bf745b90221da33a7cfaf40726c5b1b480`; actual classes
  `OpenAICompatibleProviderAdapter` and `ProviderRequest`; actual methods
  `forward_response` and `stream_response`.
- PASSED: non-stream Responses status 200, upstream model `qwen3.8-27b`, safe
  total usage count 5; stream status 200 with three ordered event types:
  `response.created`, `response.output_text.delta`, `response.completed`.
- PASSED: candidate service authentication, Qwen-only fake-upstream credential,
  model rewrite, client-key/header filtering, identity-header filtering, and
  secret-free metrics.
- PASSED: run invoked only the provider adapter and temporary candidate/fake
  servers; PostgreSQL, Redis, quota, and accounting services were not invoked.

### Criterion D — gateway identity capability audit
- PASSED: pinned source evidence records `ProviderRequest.extra_headers`, the
  standard-header allowlist/filter, and the absence of trusted Local Coding
  principal/session/repository metadata in current Responses construction.
- LIMITATION: this does not establish signed per-user identity.

### Criterion E — cutover status and next gate
- PASSED: runbook and integration documentation state the single-user static
  path, the shared-Bearer rehydration-disabled degradation, and future trusted
  identity/cutover gates.
- NOT RUN by order: gateway service cutover, quota/ledger execution, direct-vLLM
  retirement, Codex profile changes, and model calls.

## Verification
- `uv sync --frozen --extra dev`: PASSED — frozen environment checked.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen ruff format --check .`: PASSED.
- `uv run --frozen mypy src tests`: PASSED — no issues in 44 source files.
- `uv run --frozen pytest -q`: PASSED — 501 passed, 8 optional live/E2E tests skipped.
- `uv build`: PASSED — source distribution and wheel built.
- `.venv/bin/python -m compileall -q src tests oap/bin scripts`: PASSED.
- `bash -n oap/bin/*.sh`: PASSED.
- `git diff --check`: PASSED.
- `python scripts/gateway_provider_driver.py --gateway-root <detached pinned gateway checkout> --adapter-port 18031`: PASSED — bounded JSON/SSE provider run; temporary servers, cache, gateway checkout, and dependency environment removed.
- Bounded credential-pattern/raw-log scans: PASSED — no real credential or raw-payload sink introduced; matches were limited to synthetic test authorization fixtures and fixed unavailable-credential warnings.

## Live model/service evidence
- Bounded read-only protected vision discovery: port 18020 `/health` returned
  HTTP 200; `/v1/models` returned HTTP 401 without authentication.
- The protected listener remained active; the user-systemd unit was observed
  inactive/dead. No service, model, network, profile, credential, or port state
  was changed. No model call was made.

## GitHub CI / required checks
- Implementation-head check: CI `test` SUCCESS / COMPLETED for
  `31f25aab09d185f1696d841f1c58be0da1ef6f38`; run job was observed remotely before report drafting.
- All required checks green at drafting: YES.
- Report-head checks may be pending; strategy verifies them independently.

## Local setup/dependencies
- Added no persistent dependency or lockfile change.
- Installed the pinned gateway runtime only in a disposable `/tmp` environment
  for the one executable driver run; no Docker, sudo, PostgreSQL, or Redis.
- Candidate/fake listeners and temporary cache were stopped/removed; protected
  Qwen/vLLM remained untouched.

## Documentation
- Updated: `README.md`, `config/adapter.example.toml`,
  `docs/ADAPTER-CONFIGURATION.md`, `docs/OAP-RUNBOOK.md`,
  `docs/SLAIF-GATEWAY-INTEGRATION.md`, and the systemd example comment.

## Safety/scope confirmations
- Unrelated files: none intentionally changed.
- Secrets/raw customer content/prompts/source/images/tool output: not committed,
  logged, or reported.
- Protected 18020/Qwen/Codex fixture changed: NO.
- Required tests skipped/not run: optional live/E2E tests were skipped by their
  existing gates; no model call was ordered.
- Extra objective PR: NO; coding merge: NO.
- Active/order edited: NO; activated bytes were committed unchanged.
- Report commit report-only: YES (to be verified after publication).

## Known limitations/blockers
- Trusted signed per-user identity remains unavailable in the unchanged gateway.
- The driver is direct provider-adapter compatibility evidence, not gateway
  service, accounting, quota, ledger, production, or cutover evidence.
- Shared service-Bearer deployments using disabled rehydration lose zero-root /
  post-compaction governance survival and are not equivalent to the static
  single-user path.

## Recommended strategic follow-up
- Review the same-PR diff and the remote report-head checks.
- Keep shared/multi-user routes on rehydration-disabled mode until a separately
  authorized trusted identity contract exists; decide any later cutover order
  independently.

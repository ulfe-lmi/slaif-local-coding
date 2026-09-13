# Current Gateway contract CI

The current continuously-supported Local↔Gateway pair is explicit and content-free:
`tests/fixtures/gateway/current_peer_authority.json` is the only current Gateway
repository/commit authority consumed by Local tests and workflow checkout.

The update sequence is:

1. Gateway merges and publishes a relevant contract change.
2. Local updates the single peer fixture in a reviewed PR.
3. Local `gateway-contract` CI checks out that exact public repository and commit,
   proves its origin, `HEAD`, source paths, and module metadata, then runs the
   focused contract tests with network access denied.
4. A successful Local merge establishes the continuously supported pair.

Run the optional focused gate with a freshly obtained checkout at the fixture
commit:

```text
SLAIF_GATEWAY_ROOT=/path/to/fresh/gateway/checkout \
  uv run --frozen python scripts/gateway_contract.py \
  --gateway-root "$SLAIF_GATEWAY_ROOT" --run-tests
```

Normal `uv run --frozen pytest -q` does not require a Gateway checkout. The
Gateway-dependent modules retain their explicit skip; the fixture/verifier
self-tests still run. The strict CI runner rejects a missing or mismatched
checkout, malformed or incompatible metadata, zero collected tests, any skip,
failure, or error. It permits no HTTP, socket, provider, model, database,
Redis, server, Codex, or inference activity during compatibility tests.

The strict job installs only Local’s locked development dependencies plus the
`gateway-contract` dependency group (`pydantic-settings` and SQLAlchemy), which
is needed for pure Gateway module imports. The current strict selection is
18/18 tests with zero skips. Gateway source remains a disposable checkout and is
never packaged into the Local wheel. Checkout and package installation are the
only network-enabled setup steps.

This current peer authority is separate from immutable Objective-005 acceptance
pins and their historical evidence. It does not claim Gateway deployment,
provider, Qwen/vLLM, service, cutover, production, or release readiness.

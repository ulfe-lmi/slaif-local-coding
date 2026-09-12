# OAP Coding-Agent Report — 005-g

## Work order

- Identifier: `005-g`
- Order path: `oap/orders/005-g-gateway-pr291-real-codex-cross-repo-acceptance.md`
- Numeric objective: `005`
- PR mode: `AMENDED_EXISTING_PR`

## Status

BLOCKED

## Executive summary

The exact-head no-live preflight reached a fresh disposable Codex 0.149.0
envelope capture, then stopped before Docker, PostgreSQL, gateway/candidate
listeners, or Qwen. The captured envelope contained ordinary `function` and
`custom` tools plus `tool_search` and `web_search`. Gateway PR #291's pinned
Codex 0.149 client module rejects the observed `tool_search` shape, and the
static compatibility registry has no `codex-0.149-responses-v1` to
`local-coding-v1` pair. The order therefore required stopping before the live
acceptance run. No application-code or Gateway changes were made.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`
- PR: [#7](https://github.com/ulfe-lmi/slaif-local-coding/pull/7)
- PR state: OPEN, non-draft, MERGEABLE; no merge or auto-merge performed
- Base/head: `main` / `oap/005-gateway-ingress-integration`
- Starting remote SHA: `356be8345dd71d6fddf829278651d18e485731d4`
- Implementation commits pushed before report: `e080e27264b203c8a55a840078fc63aaf5c9e07d`
- Implementation head SHA: e080e27264b203c8a55a840078fc63aaf5c9e07d
- Report publication commit: SELF
- New PR this round: NO
- Amended existing PR: YES, PR #7
- Merge performed: NO

Gateway dependency was verified at the required exact open PR head
`c68fa511141a0c21d420e7a94100f717e674553f`; its base is `main` at
`7ffce834915b74809109e8b579d8541cdcfa9df7`, and its ten reported CI/CodeQL/
PostgreSQL/E2E/Compose/documentation checks were SUCCESS. No Gateway file was
modified.

## Changes and files

- Committed the activated `oap/active` value and exact `005-g` order bytes in
  the implementation/transcript commit.
- Added no production code, dependency, fixture, documentation, Gateway, or
  service changes because the mandatory no-live preflight blocked the order.

## Acceptance evidence

### Criterion 1 — exact-head and fixture preflight

- Local Coding remote head matched the required `356be834…` before the
  transcript push; the pushed transcript head is `e080e272…`.
- Gateway PR #291 matched the required `c68fa511…` and remained OPEN,
  non-draft, MERGEABLE, and CLEAN.
- Local fixture hashes were `responses_tool_filter_vectors.json`:
  `58ff37d43778895b198f687aa4c54cbe41953809db8af97e7357c5d791c111e6`, and
  `signed_identity_v1_vectors.json`:
  `92c09c03a40dbdf5e6e08b9e5d7f5c6e2c777e14467845d351f219cbb9a66588`.
- Gateway-copy hashes were respectively
  `7dc1678b8f34ae90f2222736d840041a03022427b5597ddaf19f021a3f1140af` and
  `4fdbc6dd46fcd11860a7dd4e8892a82ff64cd8da1e108a9fdb2482c13e1f0`.
- Raw `cmp` was FAILED: the Gateway copies use a provenance wrapper whose
  embedded `source_fixture_sha256` values identify the Local Coding fixture,
  but the files are not byte-identical. No fixture was rewritten.

### Criterion 2 — no-live Codex/Gateway preflight

- A fresh driver-owned `CODEX_HOME` and temporary loopback capture server were
  used; the capture state and private detached Gateway clone/venv were removed.
- Codex version: `0.149.0`; capture was bounded and synthetic-stop terminated
  with exit status `1`.
- Safe top-level tool counts were `function=5`, `custom=1`,
  `tool_search=1`, and `web_search=1`.
- The pinned Codex 0.149 normalizer rejected the captured envelope before the
  Gateway policy/route acceptance stage. Runtime reducer fact:
  `ModuleSelectionError`; the pinned source maps the unsupported
  `tool_search` declaration to `codex_0149_request_invalid`.
- The pinned route contract parses as `local-coding-v1` with
  `responses-tool-policy-v1`, `signed_identity_v1`, process-local TTL/LRU
  replay, and single-worker deployment. The static registry has no compatible
  `codex-0.149-responses-v1` / `local-coding-v1` pair.
- Gateway policy acceptance: NOT RUN after client normalization rejection.
  Local Coding postcondition filtering: NOT RUN. Explicit hosted-choice
  rejection through the live route: NOT RUN. The order prohibits repair or
  live retry after this preflight blocker.

### Criterion 3 — live cross-repository traffic and accounting

- NOT RUN. PostgreSQL, Docker, Gateway ASGI, Local Coding listener, public
  traffic, Codex-through-Gateway traffic, accounting queries, identity
  isolation, and rollback traffic were gated by Criterion 2.

## Verification

- `uv run --frozen pytest -q`: PASSED — 545 passed, 8 explicit environment/live skips.
- `uv run --frozen ruff check src tests`: PASSED.
- `uv run --frozen ruff format --check src tests`: PASSED.
- `uv run --frozen mypy src tests`: PASSED — 52 source files checked.
- `uv build --wheel --sdist`: PASSED — wheel and sdist built.
- `uv run --frozen python -m compileall -q src tests`: PASSED.
- `git diff --check`: PASSED.
- `find scripts oap/bin -type f -name '*.sh' -exec bash -n '{}' ';'`: PASSED.
- Redacted raw-log/secret scan: PASSED — no production raw-payload logging
  match; no real credentials or payloads were scanned into the report.
- Exact Gateway PR #291 no-live capture/preflight: BLOCKED — client module
  rejected the observed envelope before policy/route acceptance.
- Full disposable cross-repository run: NOT RUN — mandatory preflight gate.
- Live Qwen/vision matrix: NOT RUN — mandatory preflight gate.

## Live model/service evidence

- NOT RUN. The protected Qwen vision fixture was not contacted or inspected
  after the no-live preflight blocker. No pre-existing image proxy was assumed
  or used. Protected Qwen/vLLM state, port `18020`, network bindings, units,
  launch flags, and Codex profiles were not changed.

## GitHub CI / required checks

- Local Coding implementation-head check `test`: SUCCESS on
  `e080e27264b203c8a55a840078fc63aaf5c9e07d`.
- All observed required checks were green at report drafting: YES for the
  current implementation head; report-head checks may be pending and strategy
  verifies them independently.
- Gateway PR #291 observed checks: all ten SUCCESS at the required pinned head.

## Local setup/dependencies

- Used the existing Local Coding `.venv` with frozen dependencies for local
  verification.
- Created a private detached Gateway clone and a temporary Gateway venv with
  its declared dependencies solely for no-live imports/capture; both were
  removed after the blocker was recorded.
- No Docker/PostgreSQL/container/image/listener/service/profile/database/cache
  state was created or persisted.

## Documentation

Not updated. No behavior or support claim changed; this report records the
blocked acceptance evidence and the existing contracts remain authoritative.

## Safety/scope confirmations

- Unrelated work: preserved. Only the activated `oap/active` and exact order
  were included in the implementation/transcript commit before this report.
- Gateway PR #291 code, branch, report, OAP, and remote state: unchanged.
- Secrets, identities, signatures, nonces, prompts, source, images, tool
  output, model text, database URLs, and raw request/response bodies: not
  exposed or persisted.
- Protected `18020`/Qwen/Codex fixture changed: NO.
- PostgreSQL/Docker/Gateway/Local Coding live traffic: NOT RUN.
- Extra objective PR: NO. Coding merge: NO.
- Active/order edited: NO after activation; bytes were committed unchanged.
- Report commit report-only: YES.

## Known limitations/blockers

- Gateway PR #291's exact current client/server registry does not authorize
  the Codex 0.149 envelope to reach `local-coding-v1`; the client normalizer
  also rejects the observed `tool_search` declaration.
- Because the order requires stopping on any no-live preflight failure, no
  signed identity, tool-filter, provider-usage, quota/accounting, isolation,
  or rollback acceptance claim can be made.
- The Gateway/local fixture files are provenance-related but not raw
  byte-identical; resolving that contract is outside this blocked run and no
  Gateway or fixture mutation was authorized here.

## Recommended strategic follow-up

- Resolve and authorize the exact Gateway-side Codex 0.149 client/server route
  contract and decide the fixture byte/provenance synchronization rule, then
  activate a continuation if cross-repository acceptance is still required.
- Reconcile both exact remote heads/checks again before any future disposable
  live setup.

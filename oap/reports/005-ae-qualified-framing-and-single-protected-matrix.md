# OAP Coding-Agent Report — 005-ae

## Work order

- Identifier: `005-ae`
- Order: `oap/orders/005-ae-qualified-framing-and-single-protected-matrix.md`
- Numeric objective: `005`, qualified framing and one protected matrix on PR 7
- PR mode: `AMENDED_EXISTING_PR`

## Status

BLOCKED

## Executive summary

The Local direct observer now accepts the exact typed Responses SSE framing
variants required by the order: explicit event headers, data-only typed frames,
and bounded mixtures, while retaining exact Gateway semantic validation and
fail-closed framing/terminal rules. The fresh fake qualification and synthetic
protected conformance completed successfully. The single authorized protected
matrix stopped in preflight because the root-executed runner rejected the
user-owned fake evidence file before credential resolution. No protected
credential or provider dispatch occurred, and no retry is authorized.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`
- PR: 7, https://github.com/ulfe-lmi/slaif-local-coding/pull/7
- State: OPEN, non-draft; base `main`; head branch
  `oap/005-gateway-ingress-integration`
- Starting remote SHA: `42f302961e0f651c8091e6949c1729c212cb2eda`
- Implementation head SHA: `c86228f0c1fce8c178f2c86ff113601408d0d7da`
- Report publication commit: SELF
- Implementation commits pushed before report: `efc6bb4`, `c86228f`
- New PR this round: NO; amended existing PR: YES; merge performed: NO

## Changes and files

- `tests/helpers/transport_observer.py`: data-only and mixed typed SSE frame
  parsing with explicit header/type agreement and unknown-type rejection.
- `scripts/local_qwen_provider_differential.py`: matching explicit-event
  validation and bounded frame accounting in provider facts.
- `scripts/gateway_accounting_rehearsal.py`: source/module-hash provenance,
  per-run identity, exact direct-observer lifecycle evidence, and stricter
  fake-gate validation.
- Focused observer/provider/rehearsal tests and `TESTING.md` contract text.
- `oap/evidence/005-ae/`: generated fake, synthetic/protected result, and
  source-bound qualification index from the actual runner outputs.
- Activated order and `oap/active` were committed byte-for-byte unchanged.

## Acceptance evidence

### Criterion 1 — provider SSE framing

- PASSED: focused tests cover split/coalesced chunks, LF/CRLF, explicit,
  data-only, and mixed typed Responses frames through the injected validator.
- PASSED: missing/empty/unknown type and conflicting explicit header/type fail
  closed; comments, duplicate/early terminal, usage, closure, and 16 KiB /
  128 KiB bounds remain enforced.

### Criterion 2 — generated evidence and fake qualification

- PASSED: actual runner result validates as 37/37 fake obligations and 37/37
  projections, with no missing rows, first failure, or retries.
- PASSED: direct observer recorded 26 dispatches: 6 compiler, 12 inference,
  and 8 other; all 12 inference observations were terminal-valid.
- PASSED: source-bound evidence includes the implementation SHA, exact source
  and loaded-module hashes, run provenance, row order/cardinality/statuses,
  direct lifecycle records, accounting, and cleanup.
- PASSED: healthy synthetic protected conformance serialized and passed 29/29
  rows with the semantic fake provider oracle unavailable.
- PASSED: serial synthetic observer-failure, combined projection/cleanup-
  failure, and pre-dispatch mapping-failure cases each serialized all 29 rows
  and preserved their primary failure/counter/cleanup facts.
- PASSED: the fake-gate validator accepted the generated artifact and rejects
  stale hashes, malformed run identity, row/projection/cardinality changes,
  inconsistent field counts, incomplete lifecycle counters, and missing direct
  records.

### Criterion 3 — one protected matrix and preservation

- BLOCKED: the one authorized protected runner reached protected-mode preflight
  but stopped at `protected_fake_gate_unsafe_file` because its root execution
  identity differed from the owner of the user-created fake evidence file.
- NOT RUN: protected credential resolution, `/health`, `/v1/models`, provider
  inference, Codex protected traffic, vision traffic, and later matrix rows.
- NOT AUTHORIZED: repair/retry, alternate diagnostic call, provider relay,
  Gateway change, Qwen change, service/profile change, or cutover.

## Verification

- `uv run --frozen pytest -q`: PASSED — 784 passed, 8 skipped.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen ruff format --check .`: PASSED — 271 files.
- `uv run --frozen mypy src tests`: PASSED — 57 source files.
- `.venv/bin/python -m compileall -q src tests scripts oap/bin`: PASSED.
- `bash -n oap/bin/*.sh`: PASSED.
- `uv lock --check`: PASSED.
- `uv pip check --python .venv/bin/python`: PASSED.
- `uv build --wheel --out-dir <temporary-directory>`: PASSED — package-only
  wheel built.
- Fake runner with exact Gateway/Codex pins: PASSED — fake and synthetic gates;
  generated artifact independently accepted by `_validate_fake_gate`.
- Protected runner with the exact bounded order: BLOCKED — pre-credential
  evidence-file ownership boundary; no retry.
- Evidence JSON parse and secret/raw-content scan: PASSED — no credentials,
  raw payloads, prompts, images, tool output, call IDs, private URLs, or raw
  logs retained.

## Live model/service evidence

- Host: `hinton1`.
- Read-only post-run snapshot: `qwen-serving-vision.service` active/running,
  MainPID `23961`, start `Sun 2026-09-06 18:57:26 CEST`, restarts `0`.
- Port `18020` remained the sole observed listener among the protected and
  development ports; development port `18031` remained free. The Qwen
  worktree retained 7 pre-existing changes.
- Protected authenticated inference and semantic provider acceptance: NOT RUN.
- Protected Qwen/vLLM/model/network/firewall/Codex-profile mutation: NO.
- Disposable Gateway, Local candidate, PostgreSQL, listeners, cache, and
  temporary Codex state were cleaned up after fake qualification.

## GitHub CI / required checks

- Final implementation-head check `test`: SUCCESS, CI run `34438972060`, job
  `102749804662`, on `c86228f0c1fce8c178f2c86ff113601408d0d7da`.
- Earlier code head check `test`: SUCCESS, CI run `34437914036`, job
  `102746743159`, on `efc6bb4dc87a1a9253d42d09c49faf7aa5ff64de`.
- All required checks at report drafting: YES.
- Report-head checks may be newly pending; strategy verifies them
  independently.

## Local setup/dependencies

- Used the repository `.venv` and a disposable detached exact Gateway checkout
  at `50dcc3b85d614eb1d0c6196595bf22ef5779f846`.
- Used a disposable Gateway Python environment and bounded PostgreSQL 16
  loopback container through the authorized passwordless-sudo Docker path.
- Used the exact Codex 0.149.0 binary and recorded its required SHA-256 in the
  generated evidence.
- No host package, daemon, protected service, model, network, key, or profile
  was changed.

## Documentation

Updated `TESTING.md` with the 005-ae framing, provenance, and evidence contract.
Generated measured evidence is retained under `oap/evidence/005-ae/`.

## Safety/scope confirmations

- Unrelated work preserved.
- Secrets and raw customer/request/response content were not retained or
  reported.
- Protected `18020`/Qwen/Codex fixture changed: NO.
- Extra objective PR: NO. Coding merge/acceptance: NO.
- Activated order/active content edited after activation: NO.
- Final report commit report-only: YES.

## Known limitations/blockers

- Real protected inference and semantic Qwen acceptance remain unestablished.
- The protected attempt was blocked before credential access by evidence-file
  ownership under the required temporary Docker privilege path. The order
  prohibits repairing that boundary and retrying this protected attempt.
- `python -m build --wheel` was not run because the host `python` command lacks
  the required ensurepip path; the frozen `uv build` wheel path passed.

## Recommended strategic follow-up

Review the generated `005-ae` evidence and decide whether a future same-PR
continuation should address runner/evidence ownership before any new protected
attempt. This round does not establish protected acceptance, cutover
acceptance, merge, or release readiness.

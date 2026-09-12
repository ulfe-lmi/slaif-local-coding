# OAP Coding-Agent Report — 005-ak

## Work order

- Identifier: `005-ak`
- Order: `oap/orders/005-ak-observer-frame-bound-and-real-acceptance.md`
- Numeric objective: `005`, acceptance-only observer frame correction and one protected matrix
- PR mode: `AMENDED_EXISTING_PR`
- PR: 7, https://github.com/ulfe-lmi/slaif-local-coding/pull/7

## Status

FAILED

## Executive summary

The acceptance-only SSE frame bound was corrected from 16 KiB to 128 KiB,
equal to but independent from the unchanged 128 KiB per-HTTP-response bound.
The observer, acceptance budget, and returned-call capture parser now retain
only closed overflow subtype and bounded integer facts; framing, validator,
budget, response-byte, and cardinality/type causes remain distinct.

The fresh exact-source fake qualification passed 37/37 obligations and
projections. One real protected matrix then passed through the corrected
vision phase but failed closed at `stream_validation_invalid` during
`identity_replay` (ordinal 5). No retry or later protected inference was
performed. Real protected acceptance is not established.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`
- PR: 7, https://github.com/ulfe-lmi/slaif-local-coding/pull/7
- State: OPEN, non-draft; merge performed: NO
- Base/head: `main` / `oap/005-gateway-ingress-integration`
- Starting remote SHA: `475539b885ea279e73ee0022a9286fdc06723f75`
- Implementation commits pushed before report:
  `989e2c09ce95f1d93c9bfb24eaa7a79824da264c`,
  `2de3ff68b075fbd9f94d2353e430f95500c86137`
- Implementation head SHA: `2de3ff68b075fbd9f94d2353e430f95500c86137`
- Report publication commit: SELF
- New PR this round: NO; amended existing PR: YES

## Changes and files

- `tests/helpers/transport_observer.py`: 128 KiB acceptance frame bound,
  closed overflow subtypes, bounded observed/bound facts, and validation-class
  handling for candidate type failures.
- `tests/helpers/acceptance_harness.py`: aligned acceptance budget and safe
  first-failure overflow context retention.
- `scripts/gateway_accounting_rehearsal.py`: aligned fake frame bound and
  returned-call parser facts.
- Focused observer, accumulator, and runner tests cover large legal events,
  response/frame-buffer/cardinality distinctions, type failures, cleanup
  retention, and no-payload evidence.
- `TESTING.md` and `docs/SLAIF-GATEWAY-INTEGRATION.md`: frame-versus-response
  contract and 005-ak evidence rules.
- `oap/evidence/005-ak/`: source-bound fake gate, protected matrix, and index.

No `src/`, dependency, lock, Gateway, service, model, network, credential, or
Codex-profile file was changed.

## Acceptance evidence

### Criterion 1 — narrow frame correction and safe overflow facts

- PASSED: 128 KiB acceptance frame bound is used by the direct observer,
  acceptance budget, and returned-call parser; the 128 KiB response bound is
  unchanged.
- PASSED: fragmented and coalesced LF/CRLF tests accept a legitimate event
  larger than 16 KiB and below the response cap.
- PASSED: response-byte and incomplete-frame-buffer overflow tests retain only
  fixed subtypes with bounded observed/configured integers.
- PASSED: event-class and replay-candidate cardinality sites use count facts;
  candidate type failures remain validation-class without fabricated sizes.
- PASSED: first-failure subtype facts survive observer close, accumulator
  projection, and cleanup; no frame or payload fragment is retained.

### Criterion 2 — exact fake qualification

- PASSED: fresh fake run on implementation `989e2c09ce95f1d93c9bfb24eaa7a79824da264c`
  returned `COMPLETE`, with 37/37 obligations and projections, zero missing
  rows, zero retries, and 26 direct dispatches: 6 compiler, 12 inference,
  and 8 other. All 12 inference observations were terminal-valid.
- PASSED: fake cleanup and result/stderr privacy scan.

### Criterion 3 — one real protected matrix

- FAILED: one exact real protected run on the same candidate reached the
  corrected vision phase and stopped at `stream_validation_invalid`, kind
  `inference`, lifetime `identity`, operation `identity_replay`, ordinal 5,
  phase `codex`.
- PASSED before the stop: bounded provider preflight, Codex and vision phase
  checkpoints, and five of six admitted inference terminals.
- NOT RUN: later protected inference and obligations after the first failure.
  The protected gate serialized 29 selected rows with first unsatisfied row
  `C1.4`, no missing rows, and zero retries.
- PASSED: maximum observed response was 105708 bytes under the unchanged
  131072-byte per-response cap; rejected response bytes and rejected chunks
  were zero. No overflow size/bound is asserted because the first failure was
  validator-class, not overflow-class.

### Criterion 4 — protected fixture preservation

- PASSED: pre/post read-only facts remained vision service MainPID `23961`,
  start `Sun 2026-09-06 18:57:26 CEST`, zero restarts, port 18020 listening,
  text unit inactive, seven pre-existing Qwen changed paths, and no 18021 or
  18031 listener.
- PASSED: protected Qwen/vLLM/model/network/firewall/Codex-profile state was
  not changed. No cutover, deployment, release, or merge was performed.

## Verification

- `uv run --frozen pytest -q`: PASSED — 817 passed, 8 skipped.
- `uv run --frozen pytest -q tests/test_transport_observer.py tests/test_acceptance_harness.py tests/test_gateway_accounting_rehearsal.py`: PASSED — 262 passed.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen ruff format --check .`: PASSED — 283 files already formatted.
- `uv run --frozen mypy src tests`: PASSED — 57 source files.
- `uv run --frozen python -m compileall -q src tests scripts oap/bin`: PASSED.
- `bash -n oap/bin/*.sh`: PASSED.
- `uv lock --check`: PASSED.
- `uv pip check --python .venv/bin/python`: PASSED.
- `uv build --wheel`: PASSED — wheel built.
- locked wheel member verifier via `uv run --frozen python`: PASSED — 26
  members; no `tests/` or `scripts/` members.
- changed-file privacy scan and `jq empty oap/evidence/005-ak/*.json`: PASSED.
- Exact pinned fake rehearsal as UID/EUID 1029: PASSED — 37/37 machine gate;
  source-bound candidate evidence is `oap/evidence/005-ak/fake-machine-gate.json`.
- One exact pinned protected rehearsal as UID/EUID 1029: FAILED — first
  failure above; no retry; source-bound evidence is
  `oap/evidence/005-ak/protected-matrix.json`.
- GitHub implementation/evidence-head check `test`: PASSED — run
  `34486418700`, job `102901741948`, observed at evidence head before report.

## Live model/service evidence

- Protected route was the existing `qwen-serving-vision.service` on private
  port 18020, through the disposable exact Gateway and Local candidate on
  loopback port 18031.
- The runner resolved only the active vision MainPID's unique nonempty
  credential entry, used it in bounded memory, and did not print, hash,
  persist, place it in argv, or expose it as public metadata.
- The corrected frame bound allowed the first vision phase to complete; the
  single protected run later failed at the identity replay validator boundary.
- Before/after fixture facts are recorded in
  `oap/evidence/005-ak/protected-matrix.json`.

## GitHub CI / required checks

- `test`: SUCCESS, run `34486418700`, job `102901741948`, evidence-head SHA
  `2de3ff68b075fbd9f94d2353e430f95500c86137`.
- All required checks at report drafting: YES.
- Report-head checks may be pending after publication; strategy verifies them
  independently.

## Local setup/dependencies

- Used the repository `.venv`, a clean detached candidate worktree at the
  tested implementation SHA, exact Gateway checkout
  `50dcc3b85d614eb1d0c6196595bf22ef5779f846`, its disposable Python venv,
  bounded loopback PostgreSQL 16/tmpfs state, and exact Codex 0.149.0.
- Temporary Gateway, candidate, database, cache, Codex-home, listeners, and
  logs were cleaned by the rehearsal. No host package, lockfile, daemon,
  protected environment, credential file, model, network configuration, or
  profile was changed.

## Documentation

Updated `TESTING.md` and `docs/SLAIF-GATEWAY-INTEGRATION.md` with the corrected
acceptance frame contract, frame-versus-response distinction, closed overflow
facts, and 005-ak evidence limitations.

## Safety/scope confirmations

- Preserved unrelated empty untracked root entries `Local`, `clean`, and
  `unchanged`; they were excluded from every commit.
- No secrets, raw IDs/digests, prompts, source, images, tool output, bodies,
  signatures, nonces, credentials, or customer data were committed or retained.
- Protected 18020/Qwen/Codex fixture changed: NO.
- Extra objective PR: NO. Coding merge/acceptance: NO.
- Active/order content edited after activation: NO.
- Final report commit report-only: YES.
- One protected attempt after actual traffic: YES. Retry after failure: NO.

## Known limitations/blockers

- The protected matrix did not complete because the direct observer failed
  closed at `identity_replay` `stream_validation_invalid`; no retry or
  alternate probe is authorized by this round.
- The first protected failure was not an overflow, so no overflow size/bound
  is applicable to that failure. The largest observed response remained below
  the 131072-byte response cap.
- Later protected semantic acceptance, cutover acceptance, merge, and release
  readiness are not established.
- Report-head CI may be pending after publication; strategy independently
  verifies its terminal state.

## Recommended strategic follow-up

Review the source-bound 005-ak correction, fake gate, identity-replay failure,
and unchanged-host evidence. Any further identity-replay investigation or
retry requires a separate strategic decision/order; no protected retry was
performed or authorized here.

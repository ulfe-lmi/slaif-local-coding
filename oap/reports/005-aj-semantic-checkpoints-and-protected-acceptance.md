# OAP Coding-Agent Report — 005-aj

## Work order

- Identifier: `005-aj`
- Order: `oap/orders/005-aj-semantic-checkpoints-and-protected-acceptance.md`
- Numeric objective: `005`, semantic checkpoints and one protected acceptance matrix
- PR mode: `AMENDED_EXISTING_PR`
- PR: 7, https://github.com/ulfe-lmi/slaif-local-coding/pull/7

## Status

FAILED

## Executive summary

The runner now preserves verified Codex client, provider, governance, accounting,
and bounded response-byte facts before later phases. Generic failure projection
retains those facts, distinguishes the chronological runtime failure from the
manifest's first unsatisfied row, and keeps unexecuted obligations `NOT RUN`.

The fresh fake qualification passed 37/37 obligations and the healthy synthetic
protected qualification passed 29/29. One authorized real protected matrix then
reached the Gateway → Local → existing vision-Qwen path. Codex/tool execution
passed, but the first vision request stopped at `stream_overflow` for
`vision_full`/ordinal 3. No retry or later protected inference was made.
Real protected acceptance is therefore not established.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`
- PR: 7, https://github.com/ulfe-lmi/slaif-local-coding/pull/7
- State: OPEN, non-draft; merge state CLEAN
- Base/head: `main` / `oap/005-gateway-ingress-integration`
- Starting remote SHA: `18bd3d2a109705cd2b50e673bc3650d5940f9ff0`
- Implementation commits pushed before report:
  `53204c5b7b924eef874025bb74c24721efabd9b4`,
  `1c601e43028282b52601b717abe4642f7a93d061`,
  `570a16d0dd44b29f83cabca331f2053d88b1bf99`,
  `b17f46025160cb7b6f6746177644035d6dce3c95`,
  `76add55ee00062fa5b5f373bc7479ac8f5a9d992`,
  `a56472704d82c8778c74abe7276017fb6466298b`,
  `2fe43fa0f9f691907a322ffc020389e8b1f3eebe`
- New PR this round: NO; amended existing PR: YES; merge performed: NO
- Implementation head SHA: `2fe43fa0f9f691907a322ffc020389e8b1f3eebe`
- Report publication commit: SELF
- Final implementation-head CI: `test` SUCCESS, run `34466780005`, job `102837099703`

## Changes and files

- `tests/helpers/acceptance_harness.py`: bounded semantic phase facts and cleanup
  checkpoint preservation.
- `scripts/gateway_accounting_rehearsal.py`: Codex checkpoint projection,
  `NOT RUN` disposition for unexecuted later obligations, evidence-only tested
  source reuse, and protected fake-gate schema alignment.
- `tests/test_acceptance_harness.py` and
  `tests/test_gateway_accounting_rehearsal.py`: checkpoint retention,
  later-phase projection, cleanup preservation, and evidence-only reuse tests.
- `TESTING.md` and `docs/SLAIF-GATEWAY-INTEGRATION.md`: checkpoint contract.
- `oap/evidence/005-aj/`: source-bound fake, synthetic, preflight-history, and
  real protected bounded evidence. Earlier pre-report evidence was preserved;
  the `*-a564` and `*-real` files bind the final execution source.

No `src/`, dependency, lock, version, Gateway, service, model, or profile file
was changed.

## Acceptance evidence

### Criterion 1 — semantic checkpoint and fake/synthetic qualification

- PASSED: fresh fake run at tested implementation
  `a56472704d82c8778c74abe7276017fb6466298b` returned `COMPLETE`, 37/37
  obligations and projections, with 6 compiler, 12 inference, and 8 other
  direct dispatches.
- PASSED: healthy synthetic protected branch returned 29/29 selected rows and
  projections with the fake semantic oracle unavailable.
- PASSED: the Codex-complete then first-vision-response synthetic case retained
  actual client/semantic/accounting checkpoint facts, stopped at
  `vision_full`/ordinal 3, serialized all 29 rows, and left 21 later or
  companion rows `NOT RUN`; its manifest first failure was distinct from the
  runtime failure.
- PASSED: projection/cleanup failure cases retained the primary failure and
  bounded secondary classes. No raw request, response, ID, tool content,
  source content, image, or credential was retained.

### Criterion 2 — one real protected matrix

- FAILED: one real protected run at implementation
  `a56472704d82c8778c74abe7276017fb6466298b` reached the existing protected
  path and stopped at the first direct failure:
  `stream_overflow`, kind `inference`, lifetime `vision`, operation
  `vision_full`, ordinal `3`.
- PASSED before the stop: real Codex 0.149.0 client verification, tool command
  lifecycle, two Codex inference calls, direct provider boundary observation,
  and the retained C1.1/C1.2/C1.3/C1.5/C1.6/accounting observations.
- NOT RUN: id-less companion, vision full-image/resumed crop history, compiler
  rehydration after the stop, later identity/isolation obligations, and later
  protected semantic rows. The manifest's first unsatisfied row was C1.4.
- PASSED: 12 bounded dispatches were admitted before stop: 4 compiler, 4
  inference, and 4 other, including 2 provider-preflight probes. No later
  protected inference or retry occurred.
- PASSED: response-byte evidence recorded no rejected bytes. The largest
  individual observed response was 67,381 bytes under the unchanged 131,072
  byte response cap; the 270,197 all-lifetime total is diagnostic only. The
  failure is retained as the bounded observer class `stream_overflow`, not
  reclassified as an oversized individual response.
- PASSED: cleanup facts were true for processes, listeners, database, cache,
  Codex home, replay, identity, and provider state.

### Criterion 3 — protected fixture preservation

- PASSED: before/after read-only facts remained vision service PID `23961`,
  start `Sun 2026-09-06 18:57:26 CEST`, zero restarts, port 18020 listening,
  and seven pre-existing Qwen changed paths.
- PASSED: protected Qwen/vLLM/model/network/firewall/Codex-profile state was
  not changed. No cutover, deployment, release, or merge was performed.

## Verification

- `uv run --frozen pytest -q`: PASSED — 807 passed, 8 skipped on the final
  pre-report implementation source before the evidence-only reuse repair.
- `uv run --frozen pytest -q tests/test_gateway_accounting_rehearsal.py tests/test_acceptance_harness.py`: PASSED — 202 passed after the final source repair.
- `uv run --frozen ruff check ...`: PASSED — focused final source check.
- `uv run --frozen ruff format --check ...`: PASSED — focused final source check.
- `uv run --frozen mypy src tests`: PASSED — 57 source files.
- `uv run --frozen python -m compileall -q src tests scripts oap/bin`: PASSED — final pre-report implementation source.
- `bash -n oap/bin/*.sh`: PASSED — final pre-report implementation source.
- `uv lock --check`: PASSED — final pre-report implementation source.
- `uv pip check --python .venv/bin/python`: PASSED — final pre-report implementation source.
- Wheel build and boundary: PASSED — 26 members; no `tests/` or `scripts/` members.
- `git diff --check`: PASSED.
- `jq empty oap/evidence/005-aj/*.json`: PASSED.
- Evidence privacy-marker scan: PASSED — no raw payload, credential, image,
  bearer value, or tool-content marker retained.
- Exact pinned fake rehearsal as UID/EUID 1029: PASSED — 37/37 machine rows,
  29/29 healthy synthetic rows, fresh source-bound `a564727` qualification.
- One exact pinned protected rehearsal as UID/EUID 1029: FAILED at the first
  bounded `stream_overflow` boundary; no retry.
- GitHub implementation-head check `test`: PASSED — run `34466780005`, job
  `102837099703`, report parent implementation head `2fe43fa0f9f691907a322ffc020389e8b1f3eebe`.

## Live model/service evidence

- Protected route: existing `qwen-serving-vision.service` on private port
  18020, through the disposable pinned Gateway and Local candidate on 18031.
- The harness used only the active vision MainPID's bounded in-memory
  `VLLM_API_KEY` procedure. The credential was not printed, hashed, persisted,
  placed in argv, or sent as public metadata.
- The first direct protected failure was `stream_overflow` at
  `vision_full`/ordinal 3. The result is not a semantic protected acceptance.
- Before/after protected fixture facts were unchanged as recorded above.

## GitHub CI / required checks

- `test`: SUCCESS, run `34466780005`, job `102837099703`, head
  `2fe43fa0f9f691907a322ffc020389e8b1f3eebe` before this report-only child.
- All required checks at report drafting: YES.
- Report-head checks may be pending after publication; strategy verifies them
  independently.

## Local setup/dependencies

- Used a disposable clean detached worktree at the tested implementation head,
  repository `.venv`, exact Gateway checkout
  `50dcc3b85d614eb1d0c6196595bf22ef5779f846`, its disposable Python venv,
  bounded PostgreSQL 16 loopback/tmpfs/`--rm` state, and exact Codex 0.149.0.
- Candidate and Gateway ports were loopback-bound and cleaned up. No host
  package, lockfile, daemon, protected environment, credential file, model,
  network configuration, or profile was changed.

## Documentation

Updated `TESTING.md` and `docs/SLAIF-GATEWAY-INTEGRATION.md` with the semantic
checkpoint and `NOT RUN` contract. Source-bound execution evidence is under
`oap/evidence/005-aj/`; earlier pre-report evidence was preserved.

## Safety/scope confirmations

- Unrelated prior orders/reports/evidence were preserved.
- Three pre-existing empty untracked root paths — `Local`, `clean`, and
  `unchanged` — were inspected, preserved, and excluded from every commit.
- No secrets, raw IDs/digests, prompts, source, images, tool output, bodies,
  signatures, nonces, private payloads, credentials, or customer data were
  committed or retained.
- Protected 18020/Qwen/Codex fixture changed: NO.
- Extra objective PR: NO. Coding merge/acceptance: NO.
- Active/order content edited after activation: NO.
- Final report commit report-only: YES.
- One protected attempt after actual traffic: YES; retry after failure: NO.

## Known limitations/blockers

- The real protected matrix did not complete because the direct observer latched
  `stream_overflow` during the first vision request. The bounded evidence does
  not retain the offending frame or payload, so no more specific provider
  interpretation is claimed.
- The unchanged per-response byte limit was not individually exceeded; the
  observed response-byte facts and stream failure class remain distinct.
- Later protected semantic acceptance, cutover acceptance, merge, and release
  readiness are not established.
- Report-head CI may be pending after publication; strategy independently
  verifies its terminal state.

## Recommended strategic follow-up

Review the source-bound real protected failure and unchanged-host evidence.
No retry was performed or authorized after actual protected traffic; any next
decision belongs to strategic/human authority under a separate order.

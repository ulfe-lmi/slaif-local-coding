# OAP Coding-Agent Report — 005-al

## Work order

- Identifier: `005-al`
- Order: `oap/orders/005-al-identity-replay-validation-and-closure.md`
- Numeric objective: `005`, identity-replay validation localization and bounded protected closure
- PR mode: `AMENDED_EXISTING_PR`

## Status

FAILED

## Executive summary

The observer, returned-call capture, and accumulator now preserve a finite,
payload-free semantic validation stage through the existing failure and cleanup
paths. The identity-replay companion was corrected to explicitly select its
declared `local_lookup` function while retaining the existing 32-token ceiling.

The exact source-bound fake qualification passed `37/37`. One authorized real
protected matrix then stopped at `stream_validation_invalid` with stage
`gateway_validator` during `identity_replay`, ordinal 5. Earlier preflight,
Codex, and vision checkpoints completed; later protected inference did not run.
The evidence does not isolate this protected validator rejection to the local
harness, so the conditional second attempt was not eligible.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`
- PR: 7, https://github.com/ulfe-lmi/slaif-local-coding/pull/7
- State: OPEN, non-draft; base/head: `main` / `oap/005-gateway-ingress-integration`
- Starting remote SHA: `63f054b820773ca46164f3330806e92a7689a6e4`
- Implementation commits pushed before report: `88b94e6669698a551e1ac9affac8716bd814e18d`, `431c21ce1753c4864765025aa8ca86575975c65b`
- Implementation head SHA: `431c21ce1753c4864765025aa8ca86575975c65b`
- Report publication commit: SELF
- New PR this round: NO; amended existing PR: YES; merge performed: NO

## Changes and files

- `tests/helpers/transport_observer.py`: finite validation-stage capture for
  event class, event/payload type, exact Gateway validator, response identity,
  replay candidate, and other semantic validation; framing/overflow/budget/
  closure classes remain separate.
- `tests/helpers/acceptance_harness.py`: safe validation-stage propagation into
  first-failure evidence.
- `scripts/gateway_accounting_rehearsal.py`: matching returned-call stage
  facts and deterministic explicit-function identity-replay fixture.
- Focused tests cover stage localization, response-identity separation,
  candidate-shape handling, accumulator propagation, and the corrected fixture.
- `TESTING.md` and `docs/SLAIF-GATEWAY-INTEGRATION.md`: 005-al contract and
  limitation documentation.
- `oap/evidence/005-al/`: source-bound fake gate, protected Attempt 1, and
  index. No raw result or credential file was committed.

## Acceptance evidence

### Criterion 1 — minimal discriminator and safe propagation

- PASSED: finite stage values are retained only with bounded failure context or
  records; no event bodies, raw IDs, arguments, prompts, or exception text are
  retained.
- PASSED: focused tests prove distinct event-class, event/payload-type,
  validator, response-identity, and replay-candidate outcomes, with framing
  still separate.

### Criterion 2 — harness-only fixture correction

- PASSED: the initial companion request explicitly selects the declared
  `local_lookup` function and retains `max_output_tokens=32`.
- PASSED: the correction passed the exact fake qualification; it did not alter
  production Local source, Gateway, Qwen/vLLM, identity policy, or budgets.

### Criterion 3 — exact fake qualification

- PASSED: source-bound machine gate `37/37`, with `26/26` direct dispatches:
  `6` compiler, `12` inference, `8` other; `12/12` inference terminals valid.
- PASSED: the produced private fake result was independently accepted by the
  actual `_validate_fake_gate` before the protected command.

### Criterion 4 — protected matrix

- FAILED: one real protected attempt stopped at `C1.4` after the first
  `identity_replay` streamed request failed with:
  `stream_validation_invalid`, validation stage `gateway_validator`, kind
  `inference`, lifetime `identity`, ordinal `5`, phase `codex`.
- PASSED before stop: 15 bounded dispatches (`4` compiler, `6` inference,
  `5` other), with `5/6` inference terminals valid; maximum observed response
  was `104750` bytes under the unchanged `131072`-byte cap.
- NOT RUN: remaining protected obligations and later protected inference.
- NOT RUN: Attempt 2; generic validator rejection did not prove a
  harness-only owner, so the order’s conditional eligibility was absent.

### Criterion 5 — protected fixture preservation

- PASSED: pre/post read-only facts remained vision PID `23961`, start
  `Sun 2026-09-06 18:57:26 CEST`, zero restarts, port `18020` listening, text
  unit inactive, seven pre-existing Qwen changed paths, and no `18021`/`18031`
  listener.
- PASSED: no Qwen/vLLM/model/service/network/firewall/Codex-profile mutation,
  cutover, deployment, release, or merge was performed.

## Verification

- `uv run --frozen pytest -q`: PASSED — `821 passed, 8 skipped`; the 8 opt-in live tests were not run.
- `uv run --frozen pytest -q tests/test_transport_observer.py tests/test_acceptance_harness.py tests/test_gateway_accounting_rehearsal.py`: PASSED — `266 passed`.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen ruff format --check .`: PASSED — 285 files formatted.
- `uv run --frozen mypy src tests`: PASSED — 57 source files.
- `uv run --frozen python -m compileall -q src tests scripts oap/bin`: PASSED.
- `bash -n oap/bin/*.sh`: PASSED.
- `uv lock --check`: PASSED.
- `uv pip check --python .venv/bin/python`: PASSED.
- `uv build --wheel`: PASSED.
- `jq empty oap/evidence/005-al/*.json`: PASSED.
- Exact pinned fake rehearsal on the clean detached candidate: PASSED —
  source-bound `37/37` gate and cleanup/privacy facts.
- Actual fake-gate validator on the produced private result: PASSED.
- Exact pinned protected rehearsal: FAILED — one authorized attempt; no retry.
- `gh pr checks 7`: PASSED — `test`, run `34534961083`, job `103064318228`,
  implementation/evidence head `431c21ce1753c4864765025aa8ca86575975c65b`.

## Live model/service evidence

- Existing `qwen-serving-vision.service` on private port `18020`; bounded
  Gateway → Local → Qwen path used the candidate on loopback `18031`.
- The process ran as UID `1029`; only the authorized active vision MainPID’s
  credential was used in bounded memory and discarded. It was not printed,
  hashed, persisted, or placed in argv/public metadata.
- The protected result/stderr files were temporary 0600 files outside the
  repository; stderr was empty and runner secret-free logging passed.

## Local setup/dependencies

- Used the existing repository `.venv`, a clean detached candidate worktree,
  the exact pinned disposable Gateway checkout/venv, bounded temporary
  PostgreSQL/tmpfs state, and the exact Codex 0.149.0 binary.
- No dependency, lock, model, service, protected environment, credential,
  network, or profile file was changed.

## Documentation

Updated `TESTING.md` and `docs/SLAIF-GATEWAY-INTEGRATION.md` with the finite
validation-stage contract, deterministic companion fixture, and protected
acceptance limitation.

## Safety/scope confirmations

- Preserved unrelated untracked `Local`, `clean`, and `unchanged`; excluded
  from all commits.
- Secrets, raw payloads, source content, images, tool output, credentials, and
  customer data were not committed.
- Protected 18020/Qwen/Codex fixture changed: NO.
- Extra objective PR: NO. Coding merge/acceptance: NO.
- Active/order content edited after activation: NO.
- Final report commit report-only: YES.
- Protected attempts performed: 1 of authorized maximum 2; no second attempt.

## Known limitations/blockers

- The protected matrix remains unaccepted because the exact Gateway validator
  rejected the initial identity-replay stream; ownership is unresolved at that
  boundary.
- The local harness correction is fake-qualified but did not establish that
  the protected rejection is harness-only.
- Remaining protected acceptance, cutover acceptance, merge, and release
  readiness are not established.

## Recommended strategic follow-up

Review `oap/evidence/005-al/protected-attempt-1.json` and the precise finite
`gateway_validator` first-failure context. Any further protected identity
replay work requires a new strategic order; this round performed no second
attempt and made no protected fixture change.

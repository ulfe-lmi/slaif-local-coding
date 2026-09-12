# OAP Coding-Agent Report — 005-ar

## Work order

- Identifier: `005-ar`
- Order: `oap/orders/005-ar-terminal-stream-repair-and-closure.md`
- Human steering: `/synology/homes/janezp/codex-supervision/slaif-local-coding/workorders/005-ar-human-token-budget-steering.md`
- Numeric objective: Objective 005 targeted terminal-stream repair and closure
- PR mode: `AMENDED_EXISTING_PR`
- Existing PR: [7](https://github.com/ulfe-lmi/slaif-local-coding/pull/7)

## Status

COMPLETE

## Executive summary

The exact pinned Gateway validator discriminator identified the prior protected
failure on the same Qwen response: the response was `incomplete` with finite
reason `max_output_tokens`, and the exact Gateway returned false at
`_validate_codex_response_event` line 1127 before terminal usage/output checks.
The response otherwise had a canonical function candidate, object-shaped
arguments, matching function name/arguments, valid usage fields/counts, and
reasoning plus a function output item. It was not the earlier no-argument-delta
omission case.

The human steering workorder selected `max_output_tokens=1024` for both target
requests with normal/default reasoning. The final identity-replay companion
then passed through the exact Gateway → Local → existing vision-Qwen path:
initial and id-less continuation both returned HTTP 200, terminal-valid SSE,
and normal close. The actual returned function-call fields and original input
history were preserved; only the optional continuation item `id` was omitted.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`
- PR: [7](https://github.com/ulfe-lmi/slaif-local-coding/pull/7), OPEN
- Base/head: `main` / `oap/005-gateway-ingress-integration`
- Starting remote SHA: `285bc15042047e0b9bc67ffe25766e889e88b2ad`
- Implementation head SHA: `c6519e35f9ee8e49681f7bec63ce122bf1118c8f`
- Report publication commit: SELF
- Implementation commits pushed before report:
  `188b41e3d52b1a55a4f2c8df588f16f8828412c`,
  `dc3508a9edaf8ec5c16a9e726a5b6a1ed48aa706`,
  `50b43af9e5f7a26329a671db854ae061f3f73e4f`,
  `1b30f605c4b2b81318e2bc313db91f5d916d23a8`,
  `a71d61f0507911cb2b4bf4a76da431102da7f9c8`,
  `c6519e35f9ee8e49681f7bec63ce122bf1118c8f`
- New PR this round: NO
- Amended existing PR: YES
- Merge performed: NO
- Implementation-head CI: `test`, run `34717601055`, job `103617520896`, SUCCESS
- PR description updated through the GitHub pull-request REST endpoint with the
  exact targeted closure outcome.

## Changes and files

- `scripts/gateway_accounting_rehearsal.py`
  - Added the smallest acceptance-only discriminator around the exact pinned
    Gateway synchronous validator. It records only finite function/return-line
    labels, boolean result classes, terminal status/output/usage shape classes,
    bounded counts, argument empty/object/other classes and length classes, and
    finite incomplete reasons. It does not copy, weaken, or replace Gateway
    validation and does not retain raw events, IDs, arguments, prompts, or
    responses.
  - Corrected the discriminator to snapshot safe terminal facts before the
    validator call and retain a separate after-call snapshot.
  - Extended only the existing AP37 source-reuse allowlist for this AR order,
    immutable AQ report, and the focused Gateway162 test path.
  - Set both identity-replay companion requests to `max_output_tokens=1024`,
    with no provider-specific thinking override.
- `tests/test_gateway162_validator_factory.py`: exact positive/negative terminal
  discriminator coverage, including pre-call snapshot ordering.
- `tests/test_gateway_accounting_rehearsal.py`: focused expectation for the
  human-steered 1024-token companion and compatible validator-factory seam.
- Activated `oap/active` and the exact `005-ar` order were committed unchanged.

## Acceptance evidence

### Criterion 1 — precise terminal diagnosis and repair

- PASS. The first protected 32-token diagnostic used one inference dispatch,
  zero continuation/compiler dispatches, and normal close. The safe discriminator
  recorded `status=incomplete`, `incomplete_reason=max_output_tokens`, object
  argument class, one function candidate, two output kinds (reasoning and
  function), valid required usage integers and total consistency, and Gateway
  `_validate_codex_response_event` false at line 1127.
- PASS. The 1024-token repair removed the rejected `chat_template_kwargs` and
  `reasoning.effort=none` experiments and retained normal/default reasoning.

### Criterion 2 — exact targeted protected companion

- PASS. Final protected target selector was `identity_replay`; target gate
  passed. It dispatched exactly two protected inference requests: initial plus
  id-less continuation; zero compiler requests; no ordinary Codex, vision, or
  other identity operation.
- PASS. Both responses were HTTP 200, SSE/terminal-valid, and normally closed.
  Canonical replay authority was available; returned call ID was present; the
  continuation mandatory call ID matched; only its optional item ID was omitted;
  function name/arguments/status remained valid; summary identity remained
  diagnostic-only.
- PASS. Two reservations and two ledger rows finalized consistently, with zero
  pending reservations and zero duplicate request IDs.

### Criterion 3 — fake qualification and bounded evidence

- PASS. The exact AP37 artifact
  `/tmp/slaif-005-ap-fake-gate.rHO7rQ` was accepted by the existing source-bound
  reuse gate after only the authorized AR allowlist extension. It was not
  rewritten or treated as new fake evidence.
- PASS. The current isolated fake target ran after the 1024-token repair with
  two inference dispatches, zero compiler dispatches, both terminal-valid,
  successful id-less companion/accounting/privacy/cleanup predicates. Full safe
  result: `/tmp/slaif-005-ar-isolated-fake-1024.aipZdW/isolated-fake-target.json`.
- NOT RUN. No fresh full fake37 qualification was used in this round. The earlier
  interrupted full-fake detour was excluded from acceptance and its owned
  temporary state was cleaned safely under the prior scope correction.

## Verification

- `PYTHONPATH=<Gateway venv site-packages> SLAIF_GATEWAY_ROOT=/tmp/slaif-gateway-005-ao uv run --frozen pytest -q tests/test_gateway162_validator_factory.py tests/test_gateway_accounting_rehearsal.py tests/test_transport_observer.py`: PASSED — 201 tests.
- `uv run --frozen mypy src tests`: PASSED — 58 source files.
- `uv run ruff check scripts/gateway_accounting_rehearsal.py tests/test_gateway162_validator_factory.py tests/test_gateway_accounting_rehearsal.py tests/test_transport_observer.py`: PASSED.
- `uv run ruff format --check ...`: PASSED.
- `uv build`: PASSED — wheel and source distribution built.
- `_validate_fake_gate(/tmp/slaif-005-ap-fake-gate.rHO7rQ)`: PASSED — exact AP37 source/reuse predicates.
- Final isolated fake identity target: PASSED — exact two-request companion.
- Final protected identity target: PASSED — exact two-request companion; full
  safe result `/tmp/slaif-005-ar-protected-1024.O7Zsxd/protected-result.json`.
- Exact protected diagnostic result before repair: PASSED as diagnosis / target
  acceptance FAILED at the bounded `max_output_tokens` predicate; safe result
  `/tmp/slaif-005-ar-protected.GjMeEO/protected-result.json`.
- Intermediate public `chat_template_kwargs` experiment: FAILED closed before
  provider dispatch with Gateway HTTP 400; it is excluded from product/Qwen
  evidence. Its safe result remains
  `/tmp/slaif-005-ar-isolated-fake-repair.EvgTn0/isolated-fake-target.json`.
- Human-steered reasoning-field attempt was interrupted before protected
  dispatch; its safe result remains
  `/tmp/slaif-005-ar-protected-finaltarget.DupU9D/protected-result.json`.
- Real ordinary Codex/vision/full Objective-005 matrix: NOT RUN, outside this
  targeted AR scope.

## Live model/service evidence

- Exact Gateway checkout: `5ea38325ef3a3ebc69524b4679b795fab0c52935`.
- Gateway app tree: `a7b64d35650b61fbba3558ddb519c6e52a627ec9`.
- Existing Qwen service: `qwen-serving-vision.service`, active/running,
  MainPID `23961`, start `Sun 2026-09-06 18:57:26 CEST`, `NRestarts=0`.
- Text unit `qwen-serving.service`: inactive/dead, MainPID `0`.
- Protected `/health` and `/v1/models` preflight: HTTP 200 each.
- Port state after cleanup: protected 18020 remained listening; 18021 and
  development 18031 were absent.
- All protected-invariance predicates passed: PID, start time, listener,
  Qwen worktree count, text inactivity, and absence of 18021/18031.
- No Qwen model/weights/vLLM flags/venv/units/launch files, service, network,
  firewall, VPN, API-key file, or Codex profile was changed.
- Codex fixture remained version `0.149.0` with SHA256
  `bbc3341e44c9ead340ed9570c17be936e37870f570751a941699ffd04d672827`.

## GitHub CI / required checks

- Implementation head `c6519e35f9ee8e49681f7bec63ce122bf1118c8f`:
  `test` SUCCESS, run `34717601055`, job `103617520896`.
- All named required checks green at drafting: YES.
- Report-head checks may be pending after publication; strategy verifies the
  final PR head independently.

## Local setup/dependencies

- Reused the order-specified Gateway checkout and Gateway virtualenv; no Gateway
  files were modified.
- Reused the existing AP37 safe artifact; no full fake37 rerun.
- Disposable Local/Gateway/PostgreSQL/candidate state was cleaned by the bounded
  runner. Retained safe result artifacts are owned 0700 directories with 0600
  files; no raw provider body or credential was persisted.

## Documentation

- Updated the PR description with the exact AR outcome. No durable architecture
  or user-facing configuration documentation was required: final behavior is an
  acceptance-harness target-budget correction under explicit human steering,
  and the active order remains immutable.

## Safety/scope confirmations

- Unrelated pre-existing empty untracked files `Local`, `clean`, and `unchanged`
  were preserved and never staged.
- No raw prompts, source, images, tool output, response bodies, IDs, credentials,
  or keys entered the report or retained evidence.
- Protected 18020/Qwen/Codex fixture changed: NO.
- Required full fake37 and ordinary/full real matrix: NOT RUN by scope correction.
- Extra objective PR: NO. Coding merge: NO.
- Active/order edited: NO.
- Final report commit report-only: YES.

## Known limitations/blockers

- This closes only the ordered `identity_replay` targeted companion. It does not
  establish the complete 005 matrix, cutover, deployment, merge, or release
  readiness.
- The accepted protected result uses one bounded serial target run and the
  existing AP37 fake qualification reuse; it is not a generic or production
  equivalence claim.

## Recommended strategic follow-up

Strategy should independently review the exact final report commit, PR head,
report-head CI, and product/security evidence before deciding whether PR 7 may
be merged under standing human authority. Coding selected no successor and did
not merge.

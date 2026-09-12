# OAP Coding-Agent Report — 005-af

## Work order

- Identifier: `005-af`
- Order: `oap/orders/005-af-same-uid-protected-acceptance.md`
- Numeric objective: `005`, same-UID preparation and one protected matrix
- PR mode: `AMENDED_EXISTING_PR`

## Status

BLOCKED

## Executive summary

Resolved the execution-identity preparation gap in the existing bounded
rehearsal path. The fake qualification, same-UID evidence validation, source
provenance, ownership negatives, synthetic protected cases, and required
checks passed. The one newly authorized protected matrix reached the existing
vision-Qwen path and stopped at `C1.1` because independent provider-boundary
acceptance was unavailable. No protected retry, service change, cutover, merge,
or release claim was made.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`
- PR: 7, https://github.com/ulfe-lmi/slaif-local-coding/pull/7
- State: OPEN, non-draft; merge state CLEAN at implementation head
- Base/head: `main` / `oap/005-gateway-ingress-integration`
- Starting remote SHA: `d06cee3f6ea365cdd25c00b45bfa09bfe1431c44`
- Implementation head SHA: `885e887da48ad80fee229f991a28f6a83d726ca4`
- Report publication commit: SELF
- Implementation commits pushed before report:
  `c0597f4cfbd52f45dba417a478fd5f9a285c5f91`,
  `f0b0199da3bf2179b974ddc0930ecd236cdd501a`,
  `4193a056f7a5e1047c9e9b9a1cfe0d7614a670a3`,
  `ba42a15cd99a13cf487dac687628fc42df31301e`,
  `885e887da48ad80fee229f991a28f6a83d726ca4`
- New PR this round: NO; amended existing PR: YES; merge performed: NO

## Changes and files

- `scripts/gateway_accounting_rehearsal.py`: same-UID-safe generated evidence
  qualification and actual pre-provider companion ownership negatives using
  the existing two test keys; synthetic protected conformance does not spend
  those extra calls.
- `tests/test_gateway_accounting_rehearsal.py`: positive and fail-closed
  ownership-negative projection tests.
- `TESTING.md` and `docs/SLAIF-GATEWAY-INTEGRATION.md`: measured 005-af
  preparation, negative-proof, and protected-stop contract.
- `oap/evidence/005-af/`: generated fake gate, protected result, and sanitized
  source/pin/UID/hash index from the actual runs.
- `oap/active` and the exact activated order were committed byte-for-byte
  unchanged.

## Acceptance evidence

### Criterion 1 — same-UID preparation and source-bound qualification

- PASSED: fake producer, validator, evidence handling, and protected harness
  ran with UID/EUID `1029`; the fake result was a regular 0600 file owned by
  UID `1029` with one link and passed `_validate_fake_gate` again under that
  same UID.
- PASSED: tested source was clean and bound to code `ba42a15cd99a13cf487dac687628fc42df31301e`;
  exact Gateway pin, app-tree digest, Codex `0.149.0` binary digest, route
  policy, observer version, and loaded-module hashes are in the evidence index.
- PASSED: generated fake result was `COMPLETE`, with 37/37 rows and
  projections, zero missing/first-failure/retry results, and 26 direct
  dispatches: 6 compiler, 12 inference, 8 other; 12/12 inference observations
  were terminal-valid and fake-provider counters matched.
- PASSED: all four serial synthetic protected cases were retained: healthy
  29/29, observer-failure 29/29, combined observer/projection/cleanup failure
  29/29, and pre-dispatch mapping-dependency failure 29/29. They used no real
  protected credential or Qwen access.

### Criterion 2 — actual companion ownership negatives

- PASSED: the actual id-less companion used a streamed initial function call
  and a non-streaming continuation omitting only the optional item ID, with a
  matching mandatory call ID, same admitted relationship, terminal accounting,
  and the natural present-ID Codex shape recorded separately.
- PASSED: three additional pre-provider Gateway requests were exercised using
  the existing primary and second test keys: missing call ID, mismatched call
  ID, and valid call ID under the second key. Each was denied as `4xx`.
- PASSED: provider calls were unchanged; primary and second-key accounting was
  unchanged; pending reservations and duplicate request IDs were zero. No
  additional inference allowance was used.

### Criterion 3 — one protected matrix and fixture preservation

- PASSED: the unchanged protected preflight matched the ordered fixture:
  vision unit active, MainPID `23961`, start `Sun 2026-09-06 18:57:26 CEST`,
  zero restarts, port `18020` present, text unit inactive, development port
  `18031` free, and seven pre-existing Qwen worktree changes.
- PASSED: same-UID protected credential resolution reached the exact active
  vision MainPID path; the unique nonempty key was held only in bounded memory,
  not printed, hashed, persisted, or included in evidence.
- BLOCKED: protected C1.1. The direct observer recorded bounded transport
  lifecycle facts, but the required independent provider-boundary acceptance
  predicate was unavailable (`transport_dispatch_matches=false`). The result
  stopped before later protected inference and did not promote the observed
  transport to acceptance.
- NOT RUN: structured protected inference acceptance after C1.1, later C1–C5
  rows, cutover, merge, and release readiness.
- PASSED: post-run protected facts retained the same PID/start/listener,
  inactive text unit, free development port, and seven Qwen worktree changes.

## Verification

- `uv run --frozen pytest -q`: PASSED — 788 passed, 8 skipped.
- `uv run --frozen pytest -q tests/test_gateway_accounting_rehearsal.py tests/test_acceptance_harness.py tests/test_transport_observer.py`: PASSED — 233 passed.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen ruff format --check .`: PASSED — 273 files.
- `uv run --frozen mypy src tests`: PASSED — 57 source files.
- `uv run --frozen python -m compileall -q src tests scripts oap/bin`: PASSED.
- `bash -n oap/bin/*.sh`: PASSED.
- `uv lock --check`: PASSED.
- `uv pip check --python .venv/bin/python`: PASSED.
- `uv build --wheel --out-dir <private temporary directory>`: PASSED; wheel
  boundary contained no `tests/` or `scripts/` members.
- `git diff --check`: PASSED.
- Exact pinned fake rehearsal as UID/EUID 1029: PASSED — complete 37-row fake
  gate, four synthetic protected cases, ownership negatives, cleanup, and
  secret-free logs.
- Same-UID `_validate_fake_gate` on the generated result: PASSED.
- One exact pinned protected rehearsal as UID/EUID 1029: BLOCKED at C1.1 —
  protected rows serialized, no later inference, cleanup and fixture
  preservation passed; no retry.
- Evidence JSON/hash/privacy checks: PASSED — all three evidence files parsed,
  artifact hashes matched the index, and no raw-content or credential canaries
  were present.
- GitHub implementation-head check `test`: PASSED — run `34443683768`, job
  `102763773291`, head `885e887da48ad80fee229f991a28f6a83d726ca4`.

## Live model/service evidence

- The protected route used only the existing active vision-Qwen service on
  port `18020`, through the disposable Gateway and Local candidate on
  development port `18031`.
- The protected attempt recorded 5 bounded observer dispatches and stopped at
  the first unaccepted provider-boundary predicate; no protected retry or
  alternate diagnostic request was made.
- Post-run: vision service active/running, MainPID `23961`, zero restarts,
  protected listener present, text service inactive, ports `18021`, `18030`,
  and `18031` free, and Qwen worktree change count `7`.
- Protected Qwen/vLLM/model/network/firewall/Codex-profile mutation: NO.

## GitHub CI / required checks

- Implementation-head `test`: SUCCESS, run `34443683768`, job
  `102763773291`, on `885e887da48ad80fee229f991a28f6a83d726ca4`.
- All required checks at report drafting: YES.
- Report-head checks may be pending; strategy verifies them independently.

## Local setup/dependencies

- Used the repository `.venv`, disposable exact Gateway checkout at
  `50dcc3b85d614eb1d0c6196595bf22ef5779f846`, disposable Gateway Python
  environment, exact Codex binary, and bounded PostgreSQL 16 loopback/tmpfs
  Docker helper.
- Generated result files lived in private temporary directories until copied
  as sanitized evidence. Temporary runner resources were cleaned by the
  rehearsal.
- No host package, daemon, protected service, model, network, key, or profile
  was changed.

## Documentation

Updated `TESTING.md` and `docs/SLAIF-GATEWAY-INTEGRATION.md` with the same-UID
evidence guard, companion ownership-negative contract, and measured protected
stop. Generated evidence is under `oap/evidence/005-af/`.

## Safety/scope confirmations

- Unrelated work preserved.
- Secrets, prompts, source, images, tool output, request/response bodies, raw
  logs, call IDs, signatures, nonces, and private URLs were not retained or
  reported.
- Protected `18020`/Qwen/Codex fixture changed: NO.
- Extra objective PR: NO. Coding merge/acceptance: NO.
- Activated order/active content edited after activation: NO.
- Final report commit report-only: YES.

## Known limitations/blockers

- Independent provider-side semantic ownership/lifecycle proof for protected
  C1.1 remains unavailable at the existing unchanged provider boundary.
- Protected result has no accepted provider-boundary predicate, so later
  protected matrix rows are NOT RUN and real protected acceptance is not
  established.
- The protected attempt is not retried in this round.

## Recommended strategic follow-up

Review the source-bound `005-af` evidence and decide whether a future order
should address the independent provider-boundary observation gap. This report
does not establish protected acceptance, cutover acceptance, merge, or release
readiness.

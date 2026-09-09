# OAP Coding-Agent Report — 005-s

## Work order

- Identifier: `005-s`
- Order: `oap/orders/005-s-observed-transport-and-pretraffic-safety.md`
- Numeric objective: Objective-005
- PR mode: `AMENDED_EXISTING_PR`

## Status

COMPLETE

## Executive summary

Repaired the repository-only acceptance harness so fake acceptance uses a
direct, acceptance-only HTTPX transport observer inside the Local candidate.
The observer preserves the same request and response stream, records bounded
safe facts for attempted/dispatched/responded/completed states, separates
compiler from public inference, and validates SSE terminal events and usage.

The fake gate is now fail-closed on complete ordered obligation/projection
evidence, candidate identity, exact Gateway/Codex pins, Local/harness source
identity, route policy, run provenance, and tested implementation identity.
Protected mode is rejected before any protected credential read because this
order qualifies fake observation only and authorizes no protected retry.

The fresh clean fake run passed all 37 selected C1–C5/D obligations. Protected
real-E2E acceptance remains explicitly unclaimed.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #7 — https://github.com/ulfe-lmi/slaif-local-coding/pull/7
- PR state: OPEN, non-draft, MERGEABLE/CLEAN
- Base/head: `main` / `oap/005-gateway-ingress-integration`
- Starting remote SHA: `31ccf159bd0d7a6cc93704ecb5522ca3dc51dc11`
- Implementation head SHA: `39cf2e0e943cd2619ad88980ad16adf118c41d0d`
- Report publication commit: SELF
- Implementation commits pushed before report: `674fa772`, `39cf2e0e`
- New PR this round: NO
- Amended existing PR: YES, PR #7
- Merge or auto-merge: NO

## Changes and files

- Added `tests/helpers/transport_observer.py`, an acceptance-only direct HTTPX
  transport/stream observer with bounded parsing, terminal usage validation,
  compiler/inference classification, readiness stop, and safe projections.
- Updated `scripts/gateway_accounting_rehearsal.py` to run the fake candidate
  through the actual `create_app(settings, transport=...)` factory, use direct
  observer lifetimes for Codex/vision/post-vision phases, cross-check observer
  dispatches against fake-provider counters, and reject protected execution
  before credential access.
- Tightened `_validate_fake_gate` against singleton, missing, duplicate,
  reordered, stale, unobserved, projection-incomplete, unsafe-file, and
  report-reuse evidence; report-only descendants are allowed only when the
  tested implementation remains unchanged.
- Extended the C1.2 projection with independent direct transport evidence.
- Added focused observer and gate tests in
  `tests/test_transport_observer.py` and
  `tests/test_gateway_accounting_rehearsal.py`.
- Updated `TESTING.md` and `docs/SLAIF-GATEWAY-INTEGRATION.md` with direct
  observer guarantees and the protected limitation.
- Committed the activated `005-s` order and `oap/active=005-s` bytes unchanged.
- No `src/` production module, Gateway source, package lock, model, service,
  active profile, firewall, VPN, or network binding was changed.

## Acceptance evidence

### A. 005-r deviation accounting

- Recoverable tested identity: 005-r implementation
  `dae975c2fe761f1fa74679536b161fb40f1b9b1e`; its immutable report head was
  `31ccf159bd0d7a6cc93704ecb5522ca3dc51dc11`.
- Existing 005-r sanitized facts identify a complete fake phase, one
  authorized protected attempt, the first protected failure at C1.1 because
  the provider boundary was unobserved, later diagnostic calls before the
  repair, and successful cleanup/protected-state comparison.
- Exact pre-repair candidate state, per-phase compiler/inference/health call
  counts, timing, and budget compliance are `UNKNOWN`; the prior report does
  not provide them and no inference was made from missing data.
- No old report was edited, no protected reproduction was made, and no raw log,
  credential, process environment, prompt, response, or host history was
  recovered.
- 005-s itself made zero protected inference/compiler/model calls and read no
  protected credential.

### B. Complete fake evidence and candidate binding

- PASSED — Fresh fake result status `COMPLETE`; acceptance gate `passed=true`,
  `missing=[]`, `first_failure=null`, `retry_count=0`.
- PASSED — 37/37 ordered results and 37/37 projection rows were present and
  independently projected; runtime observation schema and relationships were
  complete.
- PASSED — Candidate provenance bound the run to implementation
  `39cf2e0e943cd2619ad88980ad16adf118c41d0d`, Local source
  `src/slaif_local_coding`, harness source
  `scripts/gateway_accounting_rehearsal.py`, route policy
  `qwen38-vision-codex/retain_newest/signed_identity_v1`, Gateway pin
  `50dcc3b85d614eb1d0c6196595bf22ef5779f846`, Gateway app tree
  `c0204deaff3cfd055a25f29a7f5d8d3c5e161d57`, Codex 0.149.0, and the exact
  binary SHA-256 `bbc3341e44c9ead340ed9570c17be936e37870f570751a941699ffd04d672827`.
- PASSED — The result file was regular, task-owned, bounded, closed-schema,
  projection-complete, and revalidated after the clean implementation run.
  A report-only descendant is the only allowed reuse path.
- PASSED — Negative focused coverage rejects the prior singleton success and
  reordered result; implementation checks reject duplicate/unknown/missing
  IDs, stale identity, false observations, missing projections, unsafe files,
  malformed data, nonzero retries, and failed/unobserved results.

### C. Pre-traffic safety and direct transport observation

- PASSED — Protected execution exits with `protected_attempt_not_authorized_005s`
  before protected service discovery requiring credentials, environment access,
  candidate dispatch, or inference.
- PASSED — Observer readiness is checked before candidate use and on every
  dispatch; readiness loss produces zero later provider dispatches. Focused
  tests cover zero-dispatch readiness loss, byte/event preservation, compiler
  separation, malformed/truncated/overflow behavior, terminal usage, first
  byte, normal close, and cleanup-safe stream handling.
- PASSED — The observer delegates directly to HTTPX's real network transport;
  it is not a relay, endpoint, proxy service, or protected-service instrument.
  It retains only fixed ordinals, classifications, counts, status classes,
  event classes, bounded timing/resource states, and terminal predicates.
- PASSED — Final fake transport evidence independently matched fake-server
  counters: compiler and inference dispatches matched, inference streams had
  first-byte, normal-close, and terminal-valid facts, and fake bad-auth was
  false. The full run recorded 6 compiler and 12 inference fake-provider
  calls, with no raw payload retained.
- PASSED — The three disposable candidate phases remained on repository port
  18031 only; listeners, processes, cache, Codex home, database, and failure
  state were removed by the rehearsal. The exact temporary Gateway checkout,
  venv, and result artifacts were removed afterward.

### D. Fresh fake integration and publication evidence

- PASSED — Actual task-controlled Codex 0.149.0 ran through exact Gateway
  `50dcc3b...`, the Local candidate factory, and strict loopback fake Qwen.
  Codex status was `PASSED`, exit status 0, two expected provider turns,
  successful dependency read, sentinel passed, and zero retries.
- PASSED — Same-session full-image then resumed-crop interaction: two vision
  turns, same session, history turn, local multiplicity/removal, governance on
  both turns, and two terminal turns.
- PASSED — Gateway identity, signing, tool/call-ID lifecycle, accounting,
  replay/tamper/isolation, constitution/compiler/cache/rehydration, image,
  privacy, no-bypass, failure, cleanup, and cutover refusal/rollback
  predicates were all included in the complete 37-result fake gate.
- PASSED — Fake result had no missing obligation, no first failure, and zero
  retries. No literal all-true result was used by the runner.
- NOT RUN — Protected Qwen inference/compiler/model matrix; prohibited by this
  order after fake qualification and not needed for fake observer evidence.
- NOT RUN — Cutover, active-profile change, persistent deployment, public bind,
  rollback against live state, or release acceptance.

## Verification

- `uv run --frozen pytest -q`: PASSED — 676 passed, 8 skipped. Skips are
  declared host/live gates and are not counted as passes.
- `uv run --frozen pytest -q tests/test_transport_observer.py tests/test_acceptance_harness.py tests/test_gateway_accounting_rehearsal.py`: PASSED — 122 passed.
- Pinned fake rehearsal through Gateway/Local/Codex/fake Qwen: PASSED —
  `COMPLETE`, 37/37, no missing/first failure/retry, direct transport match,
  cleanup true.
- `_validate_fake_gate` against the final fake result: PASSED — complete
  ordered projection and candidate identity accepted.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen ruff format --check .`: PASSED — 247 files formatted.
- `uv run --frozen mypy src tests`: PASSED — 57 source files, no issues.
- `uv run --frozen python -m compileall -q scripts tests/helpers src`: PASSED.
- `bash -n oap/bin/*.sh`: PASSED.
- `uv build --wheel --sdist`: PASSED — wheel and sdist built; wheel boundary
  remains free of `tests/` and `scripts/` members.
- `git diff --check`: PASSED.
- Bounded pin/privacy/raw-artifact scan: PASSED — only synthetic contract
  strings and fixed pins were present; no raw payload, image, prompt, source,
  tool output, credential, or customer data was retained.

## Live model/service evidence

- 005-s performed read-only host observation only; no protected request,
  credential read, compiler call, image call, inference, service mutation, or
  Codex profile mutation occurred.
- Final read-only snapshot: `qwen-serving-vision.service` active/running,
  MainPID `23961`, start `Sun 2026-09-06 18:57:26 CEST`, `NRestarts=0`, port
  18020 listening; `qwen-serving.service` inactive with MainPID 0; ports
  18021, 18030, and 18031 free.
- Protected state is unchanged. This report does not establish protected
  provider-call observation, real vision acceptance, cutover, or release
  readiness.

## GitHub CI / required checks

- Implementation-head `test`: SUCCESS — run `34384578239`, job
  `102577532159`, on `39cf2e0e943cd2619ad88980ad16adf118c41d0d`.
- All required checks green at drafting: YES.
- Report-head checks may be pending after publication; strategy verifies the
  new PR head.

## Local setup/dependencies

- Used the existing frozen Local environment.
- Used a disposable detached Gateway checkout at exact pin
  `50dcc3b85d614eb1d0c6196595bf22ef5779f846` and a disposable Python 3.12
  venv; both were removed after the fake rehearsal.
- Used disposable PostgreSQL 16 and loopback/tmpfs rehearsal state. The
  runner's process/listener/database/cache/Codex-home cleanup predicates all
  passed.
- No package, daemon, host, protected service, or persistent external state was
  changed.

## Documentation

Updated `TESTING.md` and `docs/SLAIF-GATEWAY-INTEGRATION.md` with the direct
observer contract, pre-traffic stop behavior, evidence binding, and honest
protected limitation. Historical orders/reports were not edited.

## Safety/scope confirmations

- Unrelated files and prior OAP artifacts: preserved.
- Protected 18020/Qwen/Codex fixture changed: NO.
- Real/protected credential read in 005-s: NO.
- Extra objective PR: NO.
- Coding merge/auto-merge/acceptance/release: NO.
- Active/order edited by coding: NO; strategic bytes committed unchanged.
- Final report commit report-only: YES.

## Known limitations/blockers

- Protected provider-call and terminal-lifecycle observation remains unavailable
  without an authorized protected-side observation mechanism. 005-s does not
  add a relay, mutate Qwen, or retry the protected path.
- Exact 005-r pre-repair per-phase counts, timing, budget compliance, and
  candidate state remain `UNKNOWN` because they were not present in existing
  sanitized evidence and were not safely recoverable.
- Full fake evidence qualifies the direct observer and harness only; it is not
  protected real-E2E acceptance or a production/cutover claim.

## Lifecycle state at publication

| State | Result |
| --- | --- |
| `IMPLEMENTED` | yes |
| `TESTED` | yes — full fake gate and repository checks |
| `REAL-E2E ACCEPTED` | no |
| `CUTOVER ACCEPTED` | no |
| `MERGED` | no |
| `RELEASE-READY` | no |

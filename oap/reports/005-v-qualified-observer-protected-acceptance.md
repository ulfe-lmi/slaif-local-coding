# OAP Coding-Agent Report — 005-v

## Work order

- Identifier: `005-v`
- Order: `oap/orders/005-v-qualified-observer-protected-acceptance.md`
- Numeric objective: Objective-005
- PR mode: `AMENDED_EXISTING_PR`

## Status

FAILED

## Executive summary

Implemented the ordered report-marker correction and qualified protected-mode
orchestration. A fresh clean fake qualification passed the complete selected
machine gate. The one authorized protected attempt was admitted only after
that gate and the unchanged vision-service preflight, reached actual
Gateway-to-Local-to-existing-provider activity, then failed to serialize its
structured result after observer readiness was lost and the runner emitted the
fixed error class `KeyError`. Protected acceptance is not established. No
protected retry, cutover, profile change, Gateway change, or Qwen mutation was
made.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #7 — https://github.com/ulfe-lmi/slaif-local-coding/pull/7
- State: OPEN, non-draft, MERGEABLE/CLEAN
- Base/head: `main` / `oap/005-gateway-ingress-integration`
- Starting remote SHA: `96e326d6c56906d8f43f1fd5da87c39c1f4979ad`
- Implementation head SHA: `0f083c32f57a49612bb0e52111f8f74e6e842b3a`
- Report publication commit: SELF
- Implementation commits pushed before report: `5d2caef91f5ed15e19b5a4881de1f19cb53c5878`,
  `cd11ad8536173ddb25c6b8be1d6a63f1b963f53a`,
  `0f083c32f57a49612bb0e52111f8f74e6e842b3a`
- New PR this round: NO
- Amended existing PR: YES, PR #7
- Merge or auto-merge performed: NO

The immutable 005-u report parent/path was verified before implementation:
report commit `96e326d6c56906d8f43f1fd5da87c39c1f4979ad` has first parent
`90460f23ec763b9503ba6ad2c32397def8a1430f` and changes only its 005-u report.

## Changes and files

- `scripts/gateway_accounting_rehearsal.py`: accepts the exact plain or
  Markdown-backticked implementation marker; validates the complete fake gate
  before protected admission; resolves the active vision MainPID; reads only
  its unique nonempty `VLLM_API_KEY` entry into memory; uses the direct
  Local-to-provider observer for protected facts; enforces protected
  first-boundary stop; and contains parser/client failure output to fixed
  bounded classes.
- `tests/helpers/acceptance_harness.py`: names the provider-boundary
  projection generically so fake and protected observations cannot be confused.
- `tests/test_gateway_accounting_rehearsal.py`: adds backticked, wrong,
  duplicate, malformed, dirty-source, and invalid-topology marker fixtures.
- `TESTING.md` and `docs/SLAIF-GATEWAY-INTEGRATION.md`: document the 005-v
  admission, direct observer, fake qualification, protected failure, and
  remaining non-acceptance state.
- Activated `oap/active` and the exact 005-v order were committed unchanged.

## Acceptance evidence

### Criterion A — preparation and source reuse

- PASSED — Exact report-only source reuse now accepts the actual Markdown
  list/backtick form and retains strict unique SHA/SELF, parent, path, clean
  relevant-source, and topology checks.
- PASSED — Disposable Git fixtures cover valid plain/backticked markers,
  wrong and duplicate SHA markers, malformed reports, changed relevant source,
  unrelated descendants, and multi-parent report commits.
- PASSED — Protected admission requires the complete same-pin fake result,
  exact Gateway/Codex/route/observer provenance, and a clean tested candidate
  before credential access or provider dispatch.

### Criterion B — fresh fake qualification

- PASSED — Exact fresh fake run at candidate implementation
  `cd11ad8536173ddb25c6b8be1d6a63f1b963f53a`: 37/37 selected C1–C5/D
  obligations `PASSED`, `missing=[]`, `first_failure=null`, and
  `retry_count=0`.
- PASSED — Fake candidate provenance used Gateway
  `50dcc3b85d614eb1d0c6196595bf22ef5779f846`, app tree
  `c0204deaff3cfd055a25f29a7f5d8d3c5e161d57`, Codex `0.149.0`, binary
  SHA-256 `bbc3341e44c9ead340ed9570c17be936e37870f570751a941699ffd04d672827`,
  route policy `qwen38-vision-codex/retain_newest/signed_identity_v1`, and
  observer `direct-httpx-v2`.
- PASSED — Independent fake observer/provider facts matched: 12 inference
  attempts and 12 terminal-valid inference observations; fake-provider match
  true; no retry; cleanup predicates true; secret-free logs true; stderr
  bytes zero on the rerun.

### Criterion C — protected attempt

- PASSED — The fake result was validated before protected credential handling.
- PASSED — Read-only preflight matched the ordered baseline: vision service
  active, ordered PID/start identity unchanged, zero restarts, port 18020
  present, text service inactive, ports 18021/18031 free, and seven existing
  Qwen worktree entries. The post-attempt snapshot matched those facts.
- PASSED — Credential handling used only the exact active vision MainPID
  environment entry, required one nonempty `VLLM_API_KEY`, held it in process
  memory for the bounded task, and did not print, hash, serialize, log, place
  in argv, or include it in evidence.
- FAILED — The single protected run reached the direct candidate/provider
  path, lost observer readiness, and ended with runner `error_type=KeyError`
  before a structured protected result was emitted. Exact protected provider
  dispatch/terminal counts were not serialized and are not claimed.
- NOT RUN — Structured protected C1–C5/D acceptance after the failed runner
  boundary; no protected result was promoted to acceptance evidence.
- NOT RUN — Any protected retry, alternate prompt/limit/model, or later matrix
  rerun. The order prohibits retry after repair.

### Criterion D — cutover and rollback distinction

- PASSED — Fake-only cutover refusal, rollback, and injected-failure cleanup
  obligations were included in the fresh 37/37 fake gate.
- NOT RUN — Installed candidate cutover, active-profile change, persistent
  deployment, public bind, rollback against live state, and release.

## Verification

- `uv run --frozen pytest -q tests/test_gateway_accounting_rehearsal.py tests/test_transport_observer.py`: PASSED — 76 passed.
- `uv run --frozen pytest -q`: PASSED — 716 passed, 8 skipped; skips remain explicit host/live gates.
- Fresh exact pinned Gateway/Local/Codex/strict fake rehearsal: PASSED — 37/37 machine gate, zero missing/first-failure/retry, exact observer/provider match, cleanup true.
- One protected rehearsal: FAILED — fixed runner `KeyError` after observer readiness loss; no structured protected gate; no retry.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen ruff format --check .`: PASSED — 253 files formatted.
- `uv run --frozen mypy src tests`: PASSED — 57 files, no issues.
- `uv run --frozen python -m compileall -q scripts tests/helpers src`: PASSED.
- `bash -n oap/bin/*.sh`: PASSED.
- `uv build --wheel --sdist`: PASSED.
- Wheel boundary scan: PASSED — no `tests/` or `scripts/` members.
- `git diff --check`: PASSED.
- Changed-path and secret-policy scan: PASSED — only fixed environment-name
  literals matched; no credential value or raw payload was present.

## Live model/service evidence

- Route: existing protected `qwen38-vision-codex` vision service through the
  exact Gateway pin and Local candidate on development port 18031.
- Protected baseline before and after: PASSED — service identity, start
  identity, restart count, protected listener, inactive text service, free
  candidate ports, and Qwen worktree-entry count unchanged.
- Protected model/inference acceptance: FAILED/NOT RUN — the single attempted
  run did not emit a structured protected matrix result after the observer
  readiness failure. No semantic or terminal acceptance is claimed.
- Cutover accepted: NO. Direct protected Qwen remains in place; no installed
  Gateway/Local deployment was changed.

## Budgets and actual counts

- Frozen rehearsal wall bound: 900 seconds; public request ordinals 1–9 each
  had maximum 1 and retries 0.
- Observer bounds: maximum 64 observed requests, 16 KiB event cap, 128 KiB
  stream cap; fake provider bounds remained 32 events, 16 KiB events, 128 KiB
  streams, and one function call per request.
- Fake actual observer result: 12 inference attempts, 12 dispatched,
  responded, completed, and terminal-valid; 6 compiler operations and 5 other
  observed operations were part of the bounded 23-operation rehearsal.
- Protected actual counts: NOT SERIALIZED after the runner `KeyError`; no
  inferred counts are promoted.

## GitHub CI / required checks

- Implementation-head `test`: SUCCESS — run `34396831492`, job `102618522418`,
  observed on `0f083c32f57a49612bb0e52111f8f74e6e842b3a`.
- All required checks green at drafting: YES.
- Report-head checks may be pending after publication; strategy verifies them.

## Local setup/dependencies

- Used the existing frozen Local environment.
- Used a disposable detached Gateway checkout at exact pin
  `50dcc3b85d614eb1d0c6196595bf22ef5779f846` and its task-local Python 3.12
  environment.
- Used bounded temporary PostgreSQL 16 tmpfs/`--rm` state, loopback fake
  provider state, temporary Gateway/Local/Codex/cache state, and no persistent
  deployment. Cleanup predicates passed for the fake run; protected task
  containers and the candidate listener were absent afterward.

## Documentation

Updated `TESTING.md` and `docs/SLAIF-GATEWAY-INTEGRATION.md` with the measured
fake qualification, protected-attempt failure, direct observer boundary,
credential scope, cleanup, and remaining acceptance limitations.

## Safety/scope confirmations

- Prior orders/reports, including 005-q, 005-r, 005-s, 005-t, and 005-u, were
  preserved. No historical report was edited.
- No raw prompts, source, images, SSE/tool output, credentials, private
  endpoint values, or customer data were committed or reported.
- Protected 18020/Qwen/Codex fixture changed: NO.
- No Qwen restart/instrumentation/config/model/flag/key change, Gateway source
  change, active profile change, firewall/VPN/network change, relay, or extra
  model was made.
- Required protected acceptance and cutover work is explicitly `NOT RUN` after
  the failed bounded attempt; no protected retry was made.
- Extra objective PR: NO; coding merge/auto-merge/acceptance: NO.
- Active/order edited by coding: NO; their exact activated bytes were committed
  unchanged.
- Final report commit report-only: YES.

## Known limitations/blockers

- Protected acceptance is FAILED, not merely pending: the attempted runner
  could not serialize the protected observation after observer readiness loss.
- Protected provider dispatch and terminal counts from that attempt are
  unavailable and cannot be reconstructed from fake or Gateway accounting
  facts.
- Real protected C1–C5/D acceptance, cutover, merge, release readiness, and
  production equivalence remain unclaimed.

## Recommended strategic follow-up

Review the failed protected runner serialization/observer-readiness evidence
and decide whether a future continuation should repair and authorize another
bounded protected attempt. Independently verify this report-only commit’s
parent/path/bytes, PR head, and report-head checks.

## Lifecycle state at publication

| State | Result |
| --- | --- |
| `IMPLEMENTED` | yes |
| `TESTED` | yes — focused/full repository checks and complete fake gate |
| `REAL-E2E ACCEPTED` | no |
| `CUTOVER ACCEPTED` | no |
| `MERGED` | no |
| `RELEASE-READY` | no |

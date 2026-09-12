# OAP Coding-Agent Report — 005-o

## Work order

- Identifier: `005-o`
- Order path: `oap/orders/005-o-protected-credential-matrix-and-cutover-closure.md`
- Numeric objective: `005`
- PR mode: `AMENDED_EXISTING_PR`

## Status

FAILED

## Executive summary

The authorized protected credential became available and the exact clean Gateway,
Codex 0.149.0, Local candidate, and protected vision fixture preflight passed.
The real composed run reached readiness, authenticated model visibility, and
ordinary non-streaming text. Its first streaming request returned a 2xx SSE
response with one provider call and a Gateway-owned error event before terminal
completion; Local reported an upstream 2xx with no failure, while the Gateway
ledger was not terminal. The order's stop-at-first-failure rule was followed:
there was no protected retry, later matrix case, candidate cutover, or Qwen
mutation.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`
- PR: [#7](https://github.com/ulfe-lmi/slaif-local-coding/pull/7)
- PR state: OPEN, non-draft, MERGEABLE/CLEAN
- Base/head: `main` / `oap/005-gateway-ingress-integration`
- Starting remote SHA: `7845d93c8e643f08f65931c533ad65af83662a49`
- Implementation head SHA: `ce8f333267effd514a3e9ce8b59262be2e766c08`
- Report publication commit: SELF
- Implementation commits pushed before report: `ce8f333267effd514a3e9ce8b59262be2e766c08`
- New PR this round: NO
- Amended existing PR: YES, PR #7
- Merge performed: NO

The exact clean Gateway authority was verified at implementation
`9d247e7f3d8fd6a588976840c4657181b7486b81`, with merged-main authority
`910ddaa23763883c07f5d2065662eb1157deb9f1`, app tree
`bd536a282362cc549cc0c5518db8e743af667b63`, and the required report parent.
All ten required Gateway implementation checks were SUCCESS. No Gateway source
was changed.

## Changes and files

- Committed the exact activated `oap/active` selector and 005-o order bytes.
- No Local production code, policy, dependency, Gateway source, protected model,
  service, network, profile, or persistent deployment was changed.
- No new acceptance harness or product support was added; the existing bounded
  repository support was used for the single protected attempt.

## Acceptance evidence

### Criterion 1 — exact preflight and fixed run contract

- PASSED — PR #7, branch, base, starting report head, and one-PR continuation
  topology matched the order; no second PR was created.
- PASSED — Exact clean Gateway checkout and authority tree/check facts matched
  the order; the historical full-stack hook was absent.
- PASSED — Task-controlled Codex reported `0.149.0` and matched SHA-256
  `bbc3341e44c9ead340ed9570c17be936e37870f570751a941699ffd04d672827`.
- PASSED — Protected authenticated health and model visibility returned HTTP
  200 and the expected model was visible.
- PASSED — Credential handling used exactly one nonempty `VLLM_API_KEY` entry
  from the verified unchanged MainPID environment, held only in process memory,
  passed to the task-local harness, and cleared in cleanup. No value, length,
  hash, or unrelated environment entry was recorded.
- PASSED — The fixed run used sequential bounded calls, no automatic inference
  retry, direct Codex → Gateway → Local → protected Qwen topology, and finally
  cleanup.

### Criterion 2 — protected B1 readiness, ordinary request, and stream

- PASSED — Gateway and Local health/readiness and authenticated model visibility
  were successful; the ordinary non-streaming request returned HTTP 200 with
  usage present.
- FAILED — The first streaming request returned a 2xx SSE response with one
  created event, zero completed events, one provider call, a parseable normal
  close, and a Gateway error event. Local observed upstream status class `2xx`,
  Local failure delta `0`, and terminal output bytes; Gateway reservation
  terminality was true but ledger terminality was false. The bounded facts
  classify ownership as Gateway stream/accounting failure.
- NOT RUN — Protected retry, alternate prompt/limit/provider, or any later B1
  case. The first protected product/accounting failure stopped the run.

### Criterion 3 — governance, vision, replay, isolation, and accounting matrix

- NOT RUN — B2 governance/dependency acquisition, same-session rehydration,
  distinct-session/owner/repository isolation, and sentinel acceptance.
- NOT RUN — B3 full-image/crop history flow and newest-image-only outbound proof.
- NOT RUN — B4 replay/tamper/authorization/tool/quota/accounting cases and
  controlled synthetic provider failure.
- PASSED — B5 task-resource cleanup and protected fixture preservation after the
  stopped run. Complete B5 no-bypass relationship proof was not reached.

### Criterion 4 — candidate cutover and rollback

- NOT RUN — Section C/D was gated on a fully green protected matrix. No
  candidate service, Gateway service, PostgreSQL resource, acceptance profile,
  active OAP profile, persistent configuration, or cutover was installed or
  switched.

## Verification

- `git diff --check`: PASSED — no whitespace errors.
- Focused `uv run --frozen ruff check` over the protected-run support: PASSED.
- Focused `uv run --frozen ruff format --check` over the protected-run support: PASSED.
- `bash -n oap/bin/*.sh`: PASSED.
- `uv run --frozen python -m compileall -q scripts tests/helpers src`: PASSED.
- Stale accepted-Gateway-pin scan: PASSED — superseded pin absent from active code.
- Historical-hook scan: PASSED — prohibited full-stack hook absent.
- Exact preflight state guard: PASSED — active/order/head/Codex/service/ports/Qwen
  baseline matched the order.
- Authenticated protected health/model visibility: PASSED — HTTP 200/200,
  expected model visible; no raw response retained.
- Single protected composed matrix: FAILED — stopped at first stream gate with
  one created, zero completed, one provider call, Gateway error event, Local 2xx,
  Local failure delta zero, reservation terminal true, ledger terminal false.
- Protected cleanup audit: PASSED — protected PID/start/restart facts unchanged,
  text inactive, candidate ports absent, task containers absent, and seven
  pre-existing Qwen worktree entries preserved.
- `gh pr checks 7`: PASSED — required Local `test` check SUCCESS at implementation
  head `ce8f333267effd514a3e9ce8b59262be2e766c08` (run `34049801779`).
- `uv run --frozen pytest -q`: NOT RUN — accepted 005-n evidence was not repeated
  because this round made no code/support change.
- Full fake Gateway → Local → fake-Qwen rehearsal: NOT RUN — accepted 005-n
  evidence was not repeated because this round made no code/support change.
- Candidate cutover/rollback acceptance: NOT RUN — gated by the failed B1 stream.

## Live model/service evidence

- Before and after the bounded run, the protected vision service was active and
  running with PID `23961`, the recorded start timestamp, and zero restarts.
- The text service remained inactive. The protected listener remained on `18020`;
  candidate/alternate ports `18021`, `18030`, and `18031` were absent after
  cleanup.
- The protected Qwen checkout retained exactly seven pre-existing uncommitted
  entries. No Qwen service, model, launch setting, credential source, network,
  firewall, VPN, or active Codex profile changed.
- Only structural/count/timing evidence was retained. No prompt, source,
  image, model output, tool data, SSE body, identity, signature, nonce, or
  credential material was retained or reported.

## GitHub CI / required checks

- Local implementation-head `test`: SUCCESS — run `34049801779`, required check
  at `ce8f333267effd514a3e9ce8b59262be2e766c08`.
- Exact Gateway required checks: SUCCESS — all ten named checks at the exact
  Gateway implementation head.
- All required checks green at drafting: YES.
- Report-head checks may be pending after publication; strategy verifies them.

## Local setup/dependencies

- Used a task-owned detached clean Gateway checkout at the exact ordered head and
  a temporary Python 3.12 environment; both were removed after the run.
- Used the existing repository environment for focused no-model checks.
- Used one bounded loopback-only temporary PostgreSQL resource; task resources
  and temporary logs were cleaned up. No persistent service or model was started.

## Documentation

Not updated. The order permits integration, testing, runbook, configuration,
installation, and Objective-005 ledger updates only after complete protected B
and candidate C/D acceptance; those gates failed before completion.

## Lifecycle state at publication

| Label | State |
|---|---|
| `IMPLEMENTED` | yes, existing Local candidate and activated order transcript |
| `TESTED` | yes, focused no-model/preflight checks and remote CI |
| `REAL-E2E ACCEPTED` | no |
| `CUTOVER ACCEPTED` | no |
| `MERGED` | no |
| `RELEASE-READY` | no |

## Safety/scope confirmations

- Unrelated files: none committed.
- Secrets/raw content: none committed, logged, cached, or reported.
- Gateway source/PR #291/merged Gateway main: NO changes.
- Protected `18020`/Qwen/Codex fixture: NO changes.
- Active/order edited by coding: NO; activated bytes were committed unchanged.
- Required later protected, governance, vision, replay, accounting, and cutover
  cases: NOT RUN after the first protected stream failure.
- Extra objective PR: NO.
- Coding merge/auto-merge: NO.
- Active/order bytes changed: NO.
- Report commit report-only: YES.

## Known limitations/blockers

- The exact clean Gateway emitted a stream error event before terminal completion
  for the first protected streaming request. Safe evidence shows Local/Qwen
  transport success and Gateway-owned stream/accounting non-terminal state, but
  not the raw error payload.
- No protected product verdict exists for governance, vision, replay/tamper,
  complete accounting, no-bypass acceptance, or cutover/rollback.
- The failure is not evidence of generic vision/model quality or production
  readiness. No Local accommodation or Gateway patch was attempted.

## Recommended strategic follow-up

Review the exact clean Gateway stream/accounting failure and issue a new same-PR
continuation only if strategy authorizes a corrected bounded acceptance attempt.
Preserve the unchanged Qwen fixture; do not infer real-E2E or cutover acceptance
from this report.

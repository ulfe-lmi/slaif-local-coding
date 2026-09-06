# OAP Coding-Agent Report — 005-q

## Status

BLOCKED

Implementation head SHA: 64e50172ee02563e2b021554f6b0d345cc7dfdec
Report publication commit: SELF

The repository-only fake acceptance orchestrator is implemented and the
machine-gated run reached the exact clean Gateway, Local candidate, fake-Qwen,
Codex, identity, governance, accounting, and cutover-matrix stages. The exact
vision resume remains blocked by the clean Gateway input contract described
below. No protected credential or authenticated protected-Qwen request was
used.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #7, existing branch `oap/005-gateway-ingress-integration`
- PR state: OPEN, non-draft, MERGEABLE
- Base/head: `main` / `oap/005-gateway-ingress-integration`
- Remote implementation head: `64e50172ee02563e2b021554f6b0d345cc7dfdec`
- Required `test` check: SUCCESS — run `34062874264`, job `101566432750`
- New PR: NO
- Merge or auto-merge: NO

## Implementation

- Replaced the recursive fake `_write_events` path with bounded, deterministic
  SSE framing and flushes.
- Added the strict eight-event function lifecycle and nine-event terminal
  assistant-message lifecycle, with event, byte, call, usage, ordering, and
  fail-closed validation.
- Added an actual loopback HTTP regression for identified and id-less function
  continuations, matching call IDs, lifecycle validity, terminality, and
  malformed continuation rejection.
- Added provider-boundary observations independent of Gateway accounting:
  request class, tool class, function/result adjacency, item-ID class, call-ID
  relation, image count/hash class, compiler/inference class, normal close,
  lifecycle, and terminality.
- Added explicit ordered projections for every fake-selected C1–C5/D
  obligation. The result schema includes source observation keys, producer,
  proving test node IDs, observed relationship, status, count class, and
  dependency-aware execution status.
- Corrected the fake runner to use the task-controlled Codex 0.149.0 binary,
  exact clean Gateway pin, scoped synthetic credentials, fresh C2 identity
  evidence, and independent compiler/rehydration observations.
- Updated `TESTING.md` and `docs/SLAIF-GATEWAY-INTEGRATION.md` with the
  executable command, bounded schema, fake/protected boundary, and current
  limitation.

## Exact fake acceptance

Preflight PASSED with clean Gateway SHA
`9d247e7f3d8fd6a588976840c4657181b7486b81`, Codex version `0.149.0`, and the
reviewed binary SHA-256
`bbc3341e44c9ead340ed9570c17be936e37870f570751a941699ffd04d672827`.

The final bounded machine result was:

- `passed=false`
- `missing=[]`
- `first_failure=C3.1`
- `retry_count=0`
- 29 selected results `PASSED`
- C3.1 and dependent D6 `FAILED`
- C3.2, C3.3, C3.4, D7, D8, and D9 `NOT RUN` by dependency

Concrete passing runtime evidence included C1.1–C2.6, C4.1–C4.9, C5.1–C5.3,
and D1–D5. This included actual Codex exit 0 for C1, two independent fake
provider inference calls, function continuation/HMAC scope facts, id-less
loopback regression success, governance acquisition/compile/cache/
rehydration, signed identity and replay/tamper/quota/failure matrices,
terminal accounting, privacy, cleanup, and fake cutover refusal/rollback
facts.

C3.1 is blocked after the first full-image vision turn succeeded in the same
session, while the resumed crop/history turn exited nonzero before reaching
the fake provider. Independent bounded diagnosis identified clean Gateway's
`responses_input_content_part_not_supported` rejection for
`input[5].content[0].type`: Codex 0.149 resume history contains the prior
assistant `output_text` content part, which the exact Gateway pin rejects
before Local admission. No raw request, prompt, image, response body, tool
output, or arbitrary error text was retained. No relay or Gateway source
change was introduced.

## Verification

- `uv run --frozen pytest -q`: PASSED — 670 passed, 8 skipped.
- Focused acceptance/Gateway/Codex/vision suites: PASSED — 283 passed, 1
  skipped.
- Focused acceptance/Gateway suites after final harness fixes: PASSED — 115
  passed.
- `uv run --frozen ruff format --check .`: PASSED — 241 files formatted.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen mypy src tests`: PASSED — 55 files, no issues.
- `uv run --frozen python -m compileall -q scripts tests/helpers src`: PASSED.
- `bash -n oap/bin/*.sh`: PASSED.
- `uv build --wheel --sdist`: PASSED.
- Wheel/sdist package boundary: PASSED — 26 wheel members and 267 sdist
  members, with no `tests/` or `scripts/` members.
- `git diff --check`: PASSED.
- Active-code stale Gateway-pin scan: PASSED — no stale active-code pin;
  historical fixture evidence remains unchanged.
- Historical Objective-155 hook scan: PASSED — no such active support hook.
- Credential-shaped literal/raw-content scan: PASSED — no real credential
  pattern or raw payload artifact found.

Skipped tests are existing host/live-gated skips and are not passes. Local
verification does not impersonate the required remote check; the current
remote `test` check is independently SUCCESS.

## Protected-host and cleanup evidence

- Protected vision service: read-only snapshot remained active/running, PID
  `23961`, start `Sun 2026-09-06 18:57:26 CEST`, zero restarts, listener on
  port `18020`.
- Protected text service: inactive.
- Protected ports `18021`, `18030`, and `18031`: free at the final snapshot.
- Protected Qwen worktree: seven pre-existing status entries preserved; their
  contents were not inspected.
- Protected credential, authenticated health/models/inference/vision calls:
  NOT RUN by explicit order.
- Fake run cleanup: task PostgreSQL, Gateway, Local, fake provider, Codex
  home, caches, processes, and listeners were removed; cleanup predicates
  passed.

## Lifecycle state

| State | Result |
| --- | --- |
| `IMPLEMENTED` | yes — bounded fake stream, runtime projections, and tests implemented |
| `TESTED` | no — exact full fake gate is BLOCKED at C3.1 |
| `REAL-E2E ACCEPTED` | no |
| `CUTOVER ACCEPTED` | no |
| `MERGED` | no |
| `RELEASE-READY` | no |

## Scope and limitations

005-q changed only the repository-owned fake acceptance harness, supporting
tests, documentation, activated order, selector, and this report. It did not
change Gateway, Local production behavior, dependencies, Qwen, model state,
network state, protected profiles, or the unresolved 005-o ownership result.
The fake provider is not protected-Qwen acceptance, and fake cutover planning
is not a real cutover. An authorized Gateway compatibility change is required
before a later continuation can establish the missing vision obligations.

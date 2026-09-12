# OAP Coding-Agent Report — 006-a

## Work order
- Identifier: `006-a`
- Order path: `oap/orders/006-a-signed-request-replay-hardening.md`
- Numeric objective: Objective006 signed-request replay hardening
- PR mode: `CREATED_NEW_PR`

## Status
COMPLETE

## Executive summary

Implemented and remotely published the Local adapter replay-hardening objective.
Signed nonce digests now use typed atomic reservation outcomes, retain entries
through the inclusive request-derived validity horizon and configured minimum
TTL, reject live-store capacity pressure without evicting protected entries,
and fail closed after wall-clock rollback. Focused regressions, the full local
suite, package checks, and implementation-head CI are green. No protected model
or live service state was accessed or changed.

The coding agent considers the security invariant accepted by coding based on
the evidence below; this is not strategic acceptance, merge, deployment, or
release readiness.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #8 — https://github.com/ulfe-lmi/slaif-local-coding/pull/8
- PR state: OPEN, non-draft; base `main`; head `oap/006-signed-request-replay-hardening`
- Starting remote SHA: `e3f10e93c1ea84bf4021fd15d566bf577d5a9dcf`
- Implementation head SHA: `4e1f07adc5d71c3f17e71b73cb57aec76aa28d9a`
- Report publication commit: SELF
- Implementation commits pushed before report: `4e1f07adc5d71c3f17e71b73cb57aec76aa28d9a`
- New PR this round: yes; amended existing PR: no; merge performed: NO

## Changes and files
- `ReplayProtector` now has closed `ReplayReservation` outcomes for reserved,
  replay, capacity unavailable, clock rollback, and clock unavailable states.
- Effective retention is
  `max(admission_now + replay_ttl_seconds, signed_timestamp + clock_skew_seconds)`;
  entries are purged only when `expiry < current_time`, so the inclusive
  request boundary remains protected.
- The protector keeps a locked non-decreasing wall-clock high-water mark and
  never evicts a live digest. Full capacity returns a distinct safe outcome.
- Verification samples an unprovided wall clock once, validates finite values,
  performs HMAC verification before reservation, and maps typed outcomes to
  fixed public errors.
- Replay-related integer configuration fields are strict and reject booleans
  and coercible non-integer values.
- Updated `README.md`, `SECURITY.md`, `docs/ADAPTER-CONFIGURATION.md`,
  `docs/SLAIF-GATEWAY-INTEGRATION.md`, and `config/adapter.example.toml`.
- Preserved the activated `oap/active` and exact order bytes in the commit.

## Acceptance evidence

### Criterion A — replay invariant and API behavior
- Result: PASSED. The implementation derives the inclusive signed timestamp
  horizon and combines it with configured minimum retention using the required
  maximum formula.
- Result: PASSED. Equality at the effective expiry remains live; only strictly
  later wall time purges an entry.
- Result: PASSED. Live entries are never LRU-evicted. Capacity returns
  `signed_identity_replay_capacity_unavailable` with HTTP 503.
- Result: PASSED. Rollback and non-finite clock conditions map to the fixed
  `signed_identity_clock_unavailable` HTTP 503 without exposing internal facts.
- Result: PASSED. HMAC/signature validation precedes nonce reservation and
  capacity consumption.

### Criterion B — deterministic regressions
- Result: PASSED. Tests cover immediate replay, maximum-future timestamps across
  the remaining validity interval and exact boundary, past-dated minimum
  retention, strict expiry, live-capacity no-eviction, known replay while full,
  invalid-signature non-consumption, same-digest concurrency, one clock sample,
  non-finite time, and forward-then-rollback re-protection.
- Result: PASSED. App-boundary tests prove fixed 503/409 codes and no additional
  constitution or upstream work after capacity is full.
- Result: PASSED. Existing canonicalization, header, route, secret, readiness,
  identity propagation, and service-auth tests remain green.

### Criterion C — configuration, documentation, compatibility
- Result: PASSED. Defaults remain skew 60 / TTL 60 / max entries 4096; bounds,
  strict types, and `replay_ttl_seconds >= clock_skew_seconds` are tested.
- Result: PASSED. Current-facing docs describe request-derived inclusive
  retention, expired-first reclamation, fail-closed capacity, rollback safety,
  digest-only process-local single-worker state, and restart loss.
- Result: PASSED. The exact Gateway main
  `5ea38325ef3a3ebc69524b4679b795fab0c52935` was inspected read-only. Its
  `app/slaif_gateway/modules/servers/local_coding/contract.py` advertises
  `process_local_ttl_lru`, defaults skew 60 / TTL 120, bounded nonce fields,
  single-worker deployment, and TTL >= skew. Its Local Coding adapter emits
  the unchanged v1 signed wire headers with fresh nonce and integer timestamp.
- Compatibility decision: Local remains wire/runtime compatible, but the
  Gateway mode label is no longer truthful. The proposed follow-up mode is
  `process_local_inclusive_horizon_fail_closed`; the Gateway numeric bounds and
  TTL/skew validation need not change. No Gateway repository file was modified.

### Criterion D — verification and security review
- Result: PASSED. CPU-only implementation and deterministic fake-upstream
  tests were used; no Qwen or compiler call was made.
- Result: PASSED. Production diff review covered lock atomicity, inclusive
  boundary comparison, rollback high-water behavior, capacity availability,
  error ordering, digest-only memory bound, restart/single-worker limitation,
  wire compatibility, and documentation claims.

## Verification
- `uv run --frozen pytest -q tests/test_gateway_identity.py tests/test_config.py`: PASSED — 76 passed.
- `uv run --frozen pytest -q tests/test_gateway_identity.py -k 'capacity or rollback or invalid_signature or nonfinite or future_horizon or past_dated or replay_is_atomic'`: PASSED — 6 passed, 17 deselected.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen ruff format --check .`: PASSED — 301 files formatted.
- `uv run --frozen mypy src tests`: PASSED — 58 source files.
- `uv run --frozen pytest -q`: PASSED — 866 passed, 17 skipped; skipped tests are not counted as pass.
- `uv build`: PASSED.
- Wheel inspection: PASSED — 26 files, runtime replay code present, LICENSE and NOTICE present, no OAP or test files.
- `python -m compileall -q src tests oap/bin`: PASSED.
- `bash -n oap/bin/*.sh`: PASSED.
- Fixed-message AST privacy scan: PASSED — source log emissions use constant messages with no raw payload interpolation.
- `git diff --check`: PASSED.

## Live model/service evidence
- `NOT RUN` by explicit order: no live `/health`, `/v1/models`, text, tool,
  streaming, vision, compiler, Codex, protected matrix, credential, port
  18020, port 18031 listener, Qwen installation, systemd, firewall, VPN,
  network, model, or profile operation was performed.
- Protected fixture unchanged: YES, based on scope and execution record.

## GitHub CI / required checks
- Implementation-head check: `test` SUCCESS, CI run `34723238097`, job
  `103632766249`, observed on implementation SHA
  `4e1f07adc5d71c3f17e71b73cb57aec76aa28d9a`.
- All required checks at implementation-head drafting: yes.
- Report-head checks may be newly pending; strategy verifies them after this
  report-only publication.

## Local setup/dependencies
- Used the existing Python 3.12 / `uv` frozen environment and repository-local
  tools only. No dependency, service, sudo, or protected-host setup was added.

## Documentation
- Updated: `README.md`, `SECURITY.md`, `docs/ADAPTER-CONFIGURATION.md`,
  `docs/SLAIF-GATEWAY-INTEGRATION.md`, and `config/adapter.example.toml`.
- The Gateway compatibility handoff is source-grounded to the exact pinned
  Gateway main and explicitly leaves Gateway implementation to a later owner.

## Safety/scope confirmations
- Preserved unrelated/pre-existing empty untracked files `Local`, `clean`, and
  `unchanged`; none was staged, edited, or deleted.
- No secrets, keys, credentials, raw request/response bodies, prompts, images,
  source contents, tool output, or customer data entered the report.
- Protected 18020/Qwen fixture changed: NO.
- Required live/model/Codex tests: NOT RUN or SKIPPED as explicitly identified;
  no skipped result is claimed as pass.
- Extra objective PR: NO. Coding merge: NO.
- Activated `oap/active` and order content edited: NO; unchanged bytes committed.
- Report commit report-only: yes.

## Known limitations/blockers
- Replay state remains bounded, digest-only, process-local, single-worker state;
  restart clears history and no cross-process or durable protection is claimed.
- Gateway main still advertises the old replay mode until a separate Gateway
  metadata/parser follow-up; this does not block the Local security fix.
- The 17 skipped local tests and all live/model/protected evidence remain
  distinct from the passed CPU-only evidence.
- The PR is OPEN and UNMERGED; deployment and release readiness are not claimed.

## Recommended strategic follow-up
- Independently review PR #8, the exact implementation/report parent chain,
  report-head CI, security diff, and the Gateway compatibility handoff.
- If accepted under strategic authority, merge PR #8 and verify remote `main`
  plus merged-main CI. Any Gateway metadata/parser change remains a separate
  cross-repository decision.

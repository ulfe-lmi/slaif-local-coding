# OAP Coding-Agent Report — 005-r

## Work order

- Identifier: `005-r`
- Order: `oap/orders/005-r-gateway161-full-acceptance-and-protected-closure.md`
- Numeric objective: Objective-005
- PR mode: `AMENDED_EXISTING_PR`

## Status

PARTIAL

## Executive summary

Re-pinned the repository-only acceptance harness to the accepted Gateway
Objective-161 implementation and repaired the directly evidenced same-session
vision/resume fake-provider behavior. The fresh fake machine gate passed all 37
selected C1–C5/D obligations through actual Codex 0.149.0, Gateway, Local,
and the strict fake provider, including full-image followed by resumed crop
history.

The one authorized protected attempt reached the existing vision-Qwen path
after the fake gate. It did not establish protected acceptance: an independent
protected provider-call and terminal-lifecycle observer is unavailable without
a provider relay or protected-service mutation. The observed protected gate
failed at C1.1 on that boundary. The harness was then repaired to stop before
later protected inference whenever this boundary is unobserved. No protected
retry, cutover, merge, or release was performed.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #7 — `https://github.com/ulfe-lmi/slaif-local-coding/pull/7`
- PR state: OPEN, non-draft, MERGEABLE/CLEAN
- Base/head: `main` / `oap/005-gateway-ingress-integration`
- Starting remote SHA: `5aec2beccc07432d45e936b82952abf52dfb10d8`
- Implementation head SHA: `dae975c2fe761f1fa74679536b161fb40f1b9b1e`
- Report publication commit: SELF
- Implementation commits pushed before report: `dae975c2`
- New PR this round: NO
- Amended existing PR: YES, PR #7
- Merge or auto-merge: NO

## Changes and files

- Updated all active repository-only Gateway pins to
  `50dcc3b85d614eb1d0c6196595bf22ef5779f846`.
- Recorded Gateway provenance separately: production implementation
  `899bd57e6eef49149d54c65838cf25d043e34a55`, immutable Gateway report
  `ad1c556a539130c08dc1063b3e9a25a0af2e5a85`, merged main
  `d142fd7f04c46fac3469b9b9bba1bd2068aabad8`, and app tree
  `c0204deaff3cfd055a25f29a7f5d8d3c5e161d57`.
- Extended the strict fake provider to model a resumed image history with a
  new function turn while preserving ordinary function-result continuation.
- Corrected vision acceptance facts for a resumed terminal assistant message,
  bounded metric-derived phase counts when the candidate is a separate
  process, and optional process-separated outbound recording.
- Added a same-pin complete-fake-gate requirement before protected mode and a
  fail-closed protected stop when independent provider observation is absent.
- Updated current testing/integration documentation and focused tests.
- Committed the activated `005-r` order and `oap/active=005-r` bytes unchanged.
- No Gateway source, Qwen source, model, service, network, profile, or Local
  production policy was changed.

## Acceptance evidence

### Gateway handback and pin

- PASSED — Clean detached task checkout attested at Gateway implementation
  SHA `50dcc3b85d614eb1d0c6196595bf22ef5779f846`; checkout was clean.
- PASSED — Actual imports resolved from that detached checkout for the Gateway
  settings, Codex 0.149 policy, registry, request policy, and route-capability
  modules.
- PASSED — Gateway report commit `ad1c556a539130c08dc1063b3e9a25a0af2e5a85`
  has only the required report path and first parent exactly the implementation
  SHA. Gateway PR #298 is merged at `d142fd7f04c46fac3469b9b9bba1bd2068aabad8`.
- PASSED — The ten handback checks were independently observed SUCCESS on the
  accepted Gateway report head.

### Fresh fake C1–C5/D gate

- PASSED — Machine result status `COMPLETE` for provider target `fake` and the
  exact Gateway pin.
- PASSED — `acceptance_gate.passed=true`, `missing=[]`,
  `first_failure=null`, `retry_count=0`, and 37/37 selected results
  `PASSED`.
- PASSED — Actual Codex 0.149.0 same-session full-image then resumed crop
  history reached Local and fake Qwen. Safe facts were: same session true,
  history turn true, governance on both turns true, two terminal turns true,
  newest-image-only provider facts true, and fixture-hash facts true.
- PASSED — Independent fake provider boundary observations covered function
  and message lifecycles, image multiplicity/hash classes, tool/call-ID
  classes, terminality, and zero direct Gateway ledger rows.
- PASSED — Signed identity, replay/concurrent replay, tamper, authorization,
  quota, failure accounting, compiler exclusion, isolation, privacy, and
  fake cutover/rollback projections were all observed by the selected gate.
- PASSED — Temporary Gateway, Local, fake provider, Codex home/cache,
  PostgreSQL, listeners, processes, and secret-free-log cleanup predicates.

### Protected attempt

- PASSED — Fake gate was complete before protected credential use; the protected
  invocation was supplied only the exact sanitized fake result and same Gateway
  pin.
- PASSED — Read-only precondition: `qwen-serving-vision.service` was active /
  running with MainPID `23961`, start `Sun 2026-09-06 18:57:26 CEST`, zero
  restarts, and one port-18020 listener. Text service was inactive and ports
  18021 and 18031 were free.
- PASSED — The unique nonempty `VLLM_API_KEY` entry was read from the unchanged
  vision MainPID environment into memory only, passed to the bounded harness,
  and not printed, hashed, stored, placed in argv, or reported.
- BLOCKED — Protected C1.1: the runner has no independent protected provider
  call/lifecycle observer. Local request counts and Gateway ledger rows cannot
  substitute for provider-call or terminal-lifecycle proof. Protected status
  was therefore not accepted.
- BLOCKED — The initial protected attempt used the pre-stop implementation and
  consequently executed later diagnostic calls after the first unproven
  boundary. Those facts are not acceptance evidence. The implementation head
  now stops before later protected inference for this condition; no retry was
  made after the repair.
- PASSED — Post-attempt protected snapshot: same PID, start time, restart
  count, port-18020 listener, inactive text service, free port 18031, and
  seven pre-existing Qwen worktree entries.
- NOT RUN — Protected C1–C5/D acceptance, because the first required
  independent provider boundary was unavailable and protected retry is
  prohibited.
- NOT RUN — Ephemeral installation/cutover, active-profile change, persistent
  deployment, public bind, rollback execution, and release.

## Verification

- `uv run --frozen pytest -q`: PASSED — 671 passed, 8 skipped. Skips remain
  host/live-gated and are not passes.
- Focused Gateway/acceptance/vision/provider suites: PASSED — 238 passed, 1
  skipped.
- `uv run --frozen ruff format --check .`: PASSED — 243 files already
  formatted.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen mypy src tests`: PASSED — 55 source files, no issues.
- `uv run --frozen python -m compileall -q scripts tests/helpers src`: PASSED.
- `bash -n oap/bin/*.sh`: PASSED.
- `uv build --wheel --sdist`: PASSED — wheel 26 members; wheel contains no
  `tests/` or `scripts/` members. The source distribution is a repository
  source archive and includes development `tests/`/`scripts/` paths; this is
  recorded separately from the installed wheel boundary.
- `git diff --check`: PASSED.
- Active-code stale Gateway-pin scan: PASSED — zero stale-pin matches in
  `scripts/` and `tests/`.
- Historical Objective-155 active-hook scan: PASSED — zero matches in active
  support code.
- Raw payload artifact scan: PASSED — zero raw image/prompt sentinel artifacts.
- Credential-pattern review: PASSED — matches were synthetic test tokens only;
  no real credential was found or exposed.

## Live model/service evidence

- Protected route used only the existing private vision service on port 18020
  through the disposable Gateway and candidate on 127.0.0.1:18031.
- One bounded authenticated protected attempt was made after fake PASS.
- No service restart, model/configuration change, port rebind, firewall/VPN
  change, profile change, provider relay, or protected checkout mutation.
- No raw prompt, source, image, tool output, response body, key, signature,
  nonce, private endpoint, or arbitrary upstream error was retained.

## GitHub CI / required checks

- Implementation-head `test`: SUCCESS — run `34375116317`, job
  `102545844827`, on `dae975c2fe761f1fa74679536b161fb40f1b9b1e`.
- All required checks green at drafting: YES.
- Report-head checks may be pending after publication; strategy verifies the
  new current PR head.

## Local setup/dependencies

- Used the existing frozen Local environment for repository tests.
- Used a temporary clean detached Gateway checkout at the exact implementation
  SHA and a temporary rehearsal environment outside the repository checkout.
- Used task-controlled Codex 0.149.0 with verified SHA-256
  `bbc3341e44c9ead340ed9570c17be936e37870f570751a941699ffd04d672827`.
- Used disposable synthetic PostgreSQL 16, Gateway, candidate, fake provider,
  Codex state, and caches; exact cleanup passed.

## Documentation

Updated `TESTING.md` and `docs/SLAIF-GATEWAY-INTEGRATION.md` with the accepted
Gateway pin, fresh fake result, protected boundary limitation, and no-retry
stop rule. Historical `005-q` and earlier orders/reports were not edited.

## Lifecycle state at publication

| State | Result |
| --- | --- |
| `IMPLEMENTED` | yes — bounded 005-r harness/pin/vision/protected-stop support |
| `TESTED` | yes for repository checks and complete fake gate; protected matrix no |
| `REAL-E2E ACCEPTED` | no — protected provider boundary unobserved |
| `CUTOVER ACCEPTED` | no |
| `MERGED` | no |
| `RELEASE-READY` | no |

## Safety/scope confirmations

- Unrelated work: preserved; the seven pre-existing Qwen worktree entries were
  not inspected or changed.
- Secrets/raw content: no real key, raw payload, image, prompt, tool output,
  response body, or private customer data entered Git, logs, metrics, or this
  report.
- Protected 18020/Qwen/Codex fixture changed: NO.
- Protected credential read: YES, one bounded in-memory read as explicitly
  authorized; not retained or exposed.
- Extra objective PR: NO.
- Coding merge/auto-merge: NO.
- Active/order edited by coding: NO; activated bytes were committed unchanged.
- Final report commit report-only: YES.

## Known limitations/blockers

- Protected acceptance remains blocked by the absence of an independent
  provider-call/terminal-lifecycle observation at the protected Qwen boundary.
  Adding a relay or mutating the protected service would violate this order.
- The protected attempt occurred before the fail-closed stop repair; its later
  diagnostic calls are explicitly not acceptance evidence, and no protected
  rerun is permitted.
- Source distribution development-source inclusion is distinct from the
  installed wheel boundary and remains reported rather than silently changed.

## Recommended strategic follow-up

Review the complete fake acceptance and the protected C1.1 boundary blocker.
If protected acceptance is required, strategy/human authority must provide an
allowed independent observation mechanism and a new explicit continuation;
this round does not authorize topology or protected-service mutation.

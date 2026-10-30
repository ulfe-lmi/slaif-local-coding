# OAP Coding-Agent Report — 017-j

## Work order
- Identifier: 017-j; order path: `oap/orders/017-j-capture-selection-and-resource-bounds.md`; numeric objective: 017
- PR mode: AMENDED_EXISTING_PR (PR #25, branch `oap/017-cache-read-observation`, base `main`)

## Status
COMPLETE

## Executive summary
The offline capture utility's selection, privacy, ownership, and resource
boundaries were repaired exactly as ordered. The eight bounded repairs landed:
(1) frame selection bound to the controller's issued call records (exact
issued ID, tool family/name, declared step/command and expected argument
values, controller-issued process ID) with advancement requiring completed
outputs that carry issued metadata; (2) lossless retention of proven selected
synthetic result text after ownership/shape/byte verification (selection
schema v2, `fixture_authority: none`); (3) the selected cap enforced on the
exact serialized UTF-8 record bytes (serialize once, publish the same bytes);
(4) all fixture requests counted against the per-run budget before
route/auth/body outcome branches; (5) preflight binary output bounded while
receiving; (6) pre-existing directories never chmoded, group-/world-writable
pre-existing directories rejected in place; (7) closed readiness/
authorization metadata schemas plus the accurate input-gate wording (the
017-i "unreachable by construction" claim is superseded); (8) the absolute
active-run deadline across owned descendants (group terminated and reaped
before pipe-drain joins; unrelated processes survive). Two additional
defects found while verifying the ordered repairs were fixed in-scope: the
published selection path was lost because the atomic writer returns `None`
(`RunOutcome.selection_path` is now the real published path), and the
pre-existing-directory unsafe-mode check missed the group-write bit.
Regressions were added for every repaired boundary. The utility remains inert
(not wired into the adapter runtime); no actual client, provider session, or
model call was made; no format or process acquisition was earned; D09/D10
remain NOT RUN. All twelve frozen strategic probes pass at the implementation
head; the full local gate and all eight implementation CI checks are green.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`; PR #25
  https://github.com/ulfe-lmi/slaif-local-coding/pull/25 — state OPEN
- Base `main` (`96c790423f6f0097a56a0b12bacda8a9b6da6aba` unchanged); head
  branch `oap/017-cache-read-observation`
- Starting remote SHA (round start): `bcb2d195a28dc1943ec6cc0a6589c06cf254384c`
- Implementation head SHA: ac0fc6e27c86a1889dcb6567b7157eb29d06cf90
- Report publication commit: SELF
- Implementation commits pushed before report:
  - `9a7bc3e07b7991856d3df5996f6ffde00c127768` — 017-j implementation/tests/docs
    + exact unchanged activated order and `oap/active` (source A)
  - `ac0fc6e27c86a1889dcb6567b7157eb29d06cf90` — development provenance
    manifest bound to source A (manifest B)
- New PR this round: NO; amended existing PR #25: YES; merge performed: NO

## Changes and files
- `scripts/real_client_capture.py`:
  - Issued-binding extraction: a call/result is proven only by the exact
    issued ID for its step position plus declared tool family/name,
    declared step/command (matched against ALL declared steps) and expected
    argument values; results must carry (or omit) the controller-issued
    process ID; `session_id`/`chunk_id` presence is rejected; a later step's
    call counts as issued only after a structurally valid completed output
    for every earlier step that carries issued metadata ("running" or
    forged-metadata outputs never unlock progression). Unissued/orphaned/
    conflicting/mismatched items are rejected item-by-item with typed
    reasons; raw values are stored nowhere.
  - Lossless selected synthetic text (selection schema
    `slaif-real-client-capture-selection-v2`): the exact received result
    text of a proven selected frame is retained, then byte-verified against
    the bytes this run seeded into the owned workspace for the declared read
    path (or the exact empty payload of a sleep step); unverified text is
    stripped to metadata + exact-byte digest and counted
    `content_unverified`. Frames carry `content_verified` provenance.
  - Serialized-byte cap: the selection record embeds its own canonical
    serialized size (fixed point), `serialize_selection` publishes exactly
    those bytes, and the per-run `max_selected_bytes` cap is enforced on
    that length (`selected_over_bound`, no oversized/partial artifact); the
    run record reports `selected_bytes_total` as the exact published UTF-8
    byte count.
  - Centralized request budget: the per-request count happens before
    header/auth/route/body outcome branches (unsupported and malformed
    requests consume budget; auth failures stay value-free).
  - Bounded preflight: select-based bounded collection with a finite
    deadline; typed `binary_version_over_bound` /
    `binary_help_over_bound` / `binary_probe_timeout` failures, non-echoing;
    no buffer-then-truncate.
  - No-mutation directory guards: pre-existing directories are accepted
    only when owned and not group- or world-writable (mode check now
    `0o022`, which the previous `0o007` check missed for 0770), are never
    chmoded, and symlink/file/foreign-parent cases are rejected in place.
  - Closed readiness/authorization metadata schemas: exact key sets, closed
    verdict/reason/flag enums, detected-flag count binding, closed
    control-candidate table, ownership/mode-0600/size bounds; unknown
    source text never reaches exceptions, reprs, or diagnostics.
  - Descendant deadline: the absolute active-run deadline spans owned
    descendants; at/after the deadline the owned group is terminated and
    reaped before pipe-drain joins, with a bounded, reported
    `teardown_seconds`; normal leader exit does not disable the deadline.
  - Publishing fix: `RunOutcome.selection_path` now carries the actual
    published `selection.json` path (the atomic 0600 writer returns
    `None`).
- `scripts/real_client_capture_fake_child.py`: unchanged.
- `tests/test_real_client_capture.py`: new regression classes for every
  repair (`TestIssuedCallBinding`, `TestSelectionTextRetention`,
  `TestProviderBudgetCentralization`, `TestPreflightBoundedOutput`,
  `TestProtectedDirNoMutation`, `TestDescendantDeadline`,
  `TestReadinessRecordClosure`, `TestCleanupOwnershipGuardSimulated`) plus
  corrected assertions where the 017-i-era expectations were superseded by
  the ordered semantics (item-level rejection keeps a proven issued call
  frame when its output is rejected; running outputs remain proven frames
  of their own issued call; output frames are frames in progression
  cases). The real-`chown` foreign-root test remains an explicit
  environment skip; the deterministic non-root simulated-UID proofs are
  passing tests.
- Docs (same PR, behavior/config/security/tests changed):
  `docs/CACHE-OBSERVATION-CONTRACT.md` (section 11 deferred history +
  section 12.1–12.4, including the accurate input-gate statement),
  `docs/CACHE-REWORK-LEDGER.md` (intro 017-j stage paragraph, D09/D10
  state notes, planned-succession 017 row), `TESTING.md` (017-j facts,
  umask-022 test context, 27 prior + 1 new environment skip accounting),
  `ARCHITECTURE.md` and `ARCHITECTURE-for-agents.md` (017-j stage
  boundaries) with the byte-identical compact mirror
  `oap/strategic-instructions/ARCHITECTURE-for-agents.md`.
- `packaging/dev_provenance_manifest.json`: development manifest bound to
  source A (objective 017-j); the A..B diff touches only this manifest.
- `oap/orders/017-j-capture-selection-and-resource-bounds.md` and
  `oap/active`: committed exactly as activated, byte-unchanged.

## Acceptance evidence
### Criterion 1 — issued-only selection
- Result: PASSED (offline).
- `tests/test_real_client_capture.py::TestIssuedCallBinding` (12 tests,
  PASSED): orphan/unissued IDs (incl. non-selected marker variants),
  progression (no advancement without earlier completed issued-metadata
  outputs; running and forged-completed outputs never count), cross-step
  command/name conflicts, custom issued input values, unissued process ID,
  session/chunk ID rejection, repeated history snapshots, malformed
  Unicode, input immutability. Raw unissued values asserted absent from
  frames and rejection counts.
### Criterion 2 — lossless selected synthetic text, byte-verified
- Result: PASSED (offline).
- `TestSelectionTextRetention` (4 tests, PASSED) and the updated
  `TestExtraction::test_declared_call_and_output_selected` /
  `TestSyntheticRuns::test_happy_path_full` (PASSED): exact received text
  retained with `content_verified: true`, exact `content_bytes`, exact
  output digest of the raw payload; tampered text stripped
  (`content_unverified`, marker absent from all persisted files); unissued
  result values never persisted; synthetic label and
  `fixture_authority: none` present in the published selection.
### Criterion 3 — cap on exact serialized published bytes
- Result: PASSED (offline).
- `test_serialized_cap_on_published_bytes` (PASSED): the run record's
  `selected_bytes_total` equals the published file size exactly; a smaller
  cap yields `selected_over_bound` with no `selection.json` artifact and
  `written: false`; the equal-size boundary publishes without exceeding.
- Probe `check-real-client-capture-v2.py::selected_cap_applies_to_
  persisted_serialized_bytes`: PASSED at the implementation head.
### Criterion 4 — centralized request budget
- Result: PASSED (offline).
- `TestProviderBudgetCentralization` (4 tests, PASSED): authenticated
  unsupported GET/POST routes consume budget (limit 2 → 404, 404, 429),
  oversized-body requests consume budget, auth failures are value-free and
  counted. Probe `check-capture-resource-boundaries.py`
  (`known_route_request_budget_control`,
  `authenticated_unsupported_routes_consume_budget`): PASSED.
### Criterion 5 — bounded preflight while receiving
- Result: PASSED (offline, fake executables only).
- `TestPreflightBoundedOutput` (3 tests, PASSED): version/help overflow is
  a typed non-echoing failure; hang → `binary_probe_timeout`; legacy
  `binary_help_over_bound` class preserved.
- Probe `check-capture-resource-boundaries.py`:
  `preflight_output_is_bounded_before_buffering` PASSED with measured
  tracemalloc peak 1,054,410 bytes (< 4 MiB gate; the 017-i defect was
  33,624,374 bytes).
### Criterion 6 — no mutation of pre-existing permissions/files
- Result: PASSED (offline).
- `TestProtectedDirNoMutation` (6 tests, PASSED): 0755 pre-existing
  directory preserved on rejection; group-writable (0770) pre-existing
  directory rejected `protected_dir_unsafe_preexisting` without mutation;
  symlink/file rejected; simulated-UID foreign owner rejected without
  mutation; fresh directory created 0700.
- Probe `check-capture-file-boundaries.py` (3/3, PASSED — was already
  passing at 017-i; not regressed) and
  `check-real-client-capture-v2.py::rejected_run_preserves_existing_shared_
  directory_mode` / `actual_disabled_control_no_launch_or_write`: PASSED.
### Criterion 7 — closed metadata schemas + accurate gate wording
- Result: PASSED (offline + docs).
- `TestReadinessRecordClosure` (8 tests, PASSED): generated-record
  round-trip, closed reason/field enums, detected-flag count binding,
  closed control candidates, 0644/symlink/foreign-owner rejection with the
  unknown value stored nowhere.
- Docs: the "unreachable by construction" wording is replaced by the
  accurate statement that the gate is input-driven (caller-supplied
  `ready`/authorization records can launch the bound stand-in through the
  public API; `TestActualFailClosed` covers the block/consume-once
  behavior) and that this version's generated readiness verdict is
  `not_ready`; a literal `ready` value is not proof that unverified startup
  controls were verified or applied. No ready state was added, no policy
  bypassed, no actual execution enabled.
### Criterion 8 — deadline across owned descendants
- Result: PASSED (offline, owned synthetic processes only).
- `TestDescendantDeadline` (3 tests, PASSED): normal-exit control;
  exited-leader late descendant is killed before it can write its marker
  at 2 s under a 0.25 s deadline; in-deadline descendants complete
  normally. Teardown grace is bounded and reported (`teardown_seconds`).
- Probe `check-capture-process-boundaries.py` (2/2, PASSED) including
  `exited_leader_does_not_bypass_descendant_deadline`.

## Verification
Test context: process-local `umask 022` (permission fixtures are
intentional), non-root, repo venv via `uv run --frozen`; protected fixture
roots/files created 0700/0600 by the tests; no root used; no shared
host/home permissions changed.

- `umask 022 && uv run --frozen pytest -q tests/test_real_client_capture.py`:
  PASSED — 156 passed, 1 skipped (the explicit real-`chown` environment
  skip `test_cleanup_refuses_foreign_root`, "cannot chown to another uid
  here"; its deterministic non-root simulated-UID companion
  `test_cleanup_refuses_foreign_root_simulated_uid` is PASSED, not a skip).
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen ruff format --check .`: PASSED.
- `uv run --frozen mypy src tests`: PASSED (no issues in 107 source files).
- `uv lock --check`: PASSED.
- `uv sync --frozen --extra dev`: PASSED.
- `uv run --frozen python scripts/docs_consistency_check.py`: PASSED
  (19 claim docs checked).
- `umask 022 && uv run --frozen pytest -q` (full suite): PASSED —
  2198 passed, 28 skipped. The 28 skips are exactly the 27 prior stage
  skips plus the one 017-i foreign-ownership `chown` environment skip;
  no 017-j test is skipped, pending, or missing.
- `uv build` (at source A): PASSED — `slaif_local_coding-0.1.0.tar.gz`,
  `slaif_local_coding-0.1.0-py3-none-any.whl`.
- `uv run --frozen python scripts/artifact_policy_check.py --dist dist --inspect`:
  PASSED (`ok: true`, no violations).
- `uv run --frozen python scripts/artifact_policy_check.py --dist dist --install-smoke`:
  PASSED (`ok: true`, no violations).
- `.venv/bin/python scripts/dev_provenance_manifest.py --verify --dist dist`:
  PASSED — `development provenance OK: state=development
  head=ac0fc6e27c86`; source bound to A, objective 017-j; frozen RC10
  publication baseline intact.
- `python -m compileall -q src tests oap/bin scripts`: PASSED.
- `bash -n` over `oap/bin/*.sh` and `packaging/*.sh`: PASSED (all parse).
- `git diff --check`: PASSED.
- Targeted credential/raw-log/privacy scan over the changed code/docs:
  PASSED — no real key/token/bearer patterns (only the synthetic in-test
  tokens `tok`/`wrong`/`WRONG-TOKEN-VALUE`), no private URLs/hosts in new
  code, prompt text only the synthetic fixture asserted absent from all
  persisted records.
- Invariance: PASSED — `docs/RC-HANDOFF.md`,
  `docs/CACHE-IMPLEMENTATION-PLAN.md`, `docs/CACHE-REWORK.md` (SHA256
  `410df5c0b8f90b05220adc32c8e673b143c0cf1fa3da02270d91ac453c886abd`
  preserved), all `oap/reports/*` and all prior `oap/orders/*` untouched by
  the round diff; the frozen 29 publication paths re-verified by the
  full-suite `test_real_frozen_publication_baseline_holds` (within the
  2198 passed); compact mirror `cmp` byte-identical.
- Clean `git archive` source-A artifact reproduction: PASSED — `git
  archive` of A extracted to a protected 0700 temp root; `uv build` from
  that clean tree reproduced the exact manifest artifacts: wheel
  `99e5ad582232c5a2e9e717c7707162b8c57261983aa0cf472e0c4e0d9263ac71` and
  sdist `8e7cb21bda8fc41b306923c78e48e14eb536ea5d33536e6d44add3601ac5de8b`
  (byte-identical to the manifest-bound artifacts built in-repo).
- Fresh wheel-install observer controls: PASSED — fresh 3.12 venv in the
  protected temp root; wheel installed with `uv pip install --no-cache-
  dir`; package imports (`slaif_local_coding`, version 0.1.0, 10
  submodules); sdist (clean-tree build) contains the test file
  `tests/test_real_client_capture.py` and no `scripts/` entries (source-
  input policy: the runtime wheel ships no test fixtures — verified wheel
  contains no capture utility/fixtures); utility, fake child, and test
  verified present in the clean source tree.
- Twelve frozen strategic scripts (canonical `REPO/.venv/bin/python`, each
  `--head ac0fc6e27c86a1889dcb6567b7157eb29d06cf90`; script SHA256s
  verified against `reviews/017-j-probe-hashes.json` before running;
  scripts unmodified; result JSON written to an owned 0700 temp root, not
  the strategic workspace): all PASSED with `positive_control_valid: true`
  and `all_checks_passed: true`:
  - `check-bundle-observation.py`: 23/23 checks.
  - `check-read-option-semantics.py`: 16/16 checks.
  - `check-endpoint-selection.py`: 5/5 checks.
  - `check-root-endpoint-context.py`: 6/6 checks.
  - `check-finite-read-plans.py`: 40/40 checks.
  - `check-literal-loops.py`: 63/63 checks.
  - `check-loop-word-boundaries.py`: 10/10 checks (162 word variants).
  - `check-real-client-capture-v2.py`: 12/12 checks (017-i final state:
    7 of these failing; now all passing, incl. the generated-readiness
    record control and the serialized-cap check).
  - `check-capture-file-boundaries.py`: 3/3 checks (already passing at
    017-i; not regressed).
  - `check-capture-selection-boundaries.py`: 2/2 checks.
  - `check-capture-resource-boundaries.py`: 4/4 checks + 1 measurement
    (preflight tracemalloc peak 1,054,410 bytes, under the 4 MiB gate).
  - `check-capture-process-boundaries.py`: 2/2 checks.
- Real-Codex E2E: NOT RUN (not ordered; the order authorizes no genuine
  launch or discovery session).
- Live vLLM/model/service calls: NOT RUN (not authorized by the order).

## Live model/service evidence
- NOT RUN. The order authorizes no genuine client session/capture, real
  model/GPU/product API/Gateway call, or service mutation. All evidence
  above is offline (fake children, owned ephemeral loopback provider,
  synthetic binaries/files). No protected fixture was touched.

## GitHub CI / required checks
- Implementation head `ac0fc6e27c86a1889dcb6567b7157eb29d06cf90` —
  all eight required checks present and SUCCESS at drafting:
  - `test`: pass (5m12s)
  - `docker`: pass
  - `docker-published`: pass
  - `gateway-contract`: pass
  - `operator-session`: pass
  - `CodeQL`: pass
  - `Analyze (python)`: pass
  - `Analyze (actions)`: pass
- All required green at drafting: YES. No in-scope CI failure required
  repair this round.
- Report-head checks may be pending; strategy verifies.

## Local setup/dependencies
- Repo venv via `uv` (frozen lock; `uv sync --frozen --extra dev` clean);
  Python 3.12.15; no new dependencies, no new services, no sudo. All
  protected temp roots (probe results, archive reproduction, fresh venv)
  were created 0700 under `/tmp` and are disposable. Durable docs/config
  changes are limited to the files listed in "Changes and files".

## Documentation
- Updated (behavior, configuration, security, tests, and limitations
  changed): `docs/CACHE-OBSERVATION-CONTRACT.md`,
  `docs/CACHE-REWORK-LEDGER.md`, `TESTING.md`, `ARCHITECTURE.md`,
  `ARCHITECTURE-for-agents.md` + byte-identical mirror
  `oap/strategic-instructions/ARCHITECTURE-for-agents.md`. The
  inaccurate broad "unreachable by construction" claim is removed from
  current-state text and superseded by the accurate input-gate statement;
  "hard-capped" and "privacy-law enforced in code" claims are retained
  because the final behavior and evidence (limits enforced on exact
  serialized bytes; issued binding with raw values stored nowhere) support
  them. PR title/body unchanged (objective-level title still accurate; no
  scope change to the numeric objective).

## Safety/scope confirmations
- Unrelated files: none touched beyond the ordered scope (round diff is
  exactly the 10 implementation/docs/order/active files + the development
  manifest).
- Secrets/raw content: none committed, printed, or persisted; synthetic
  markers/tokens only; targeted scan PASSED.
- Production/protected resources: none touched.
- Protected 18020/Qwen/Codex fixture changed: NO.
- No live inference performed (not authorized).
- Required tests skipped/not run: one explicit environment skip (real
  `chown`, 017-i, unchanged; deterministic simulated-UID proof passing);
  live/E2E layers NOT RUN because not authorized — stated, not passed.
- Scope deviation: none. Two additional in-scope defects fixed while
  verifying ordered repairs (selection_path loss; group-write bit in the
  pre-existing-directory check); both are within the ordered repair
  boundaries (correct published-byte accounting; no-mutation directory
  guards) and are covered by new regressions.
- Extra objective PR: NO. Coding merge: NO. Auto-merge: none enabled.
- Active/order edited: NO (committed byte-unchanged; verified by the
  round diff). Report commit report-only: YES (parent = implementation
  head; the commit touches only this report file).

## Known limitations/blockers
- No actual format, process-collector, D09/D10, or v1 runtime
  qualification was earned; the utility remains inert and offline-only.
- The actual-client path is input-gated: a future exact order would need
  to supply (or earn) trusted ready/authorization evidence before any
  genuine launch; a literal `ready` record alone is not such proof.
- The real-`chown` foreign-root guard test remains an environment skip
  where `chown` to another uid is unavailable (non-root host); the
  simulated-UID proof covers the guard deterministically.

## Recommended strategic follow-up
Factual only; strategy decides: independent review of the 017-j head
(including the probe result JSONs and the corrected gate wording);
decision on the next suffix (D09 multi-chunk process completion and the
remaining D10 branch matrix remain NOT RUN and are planned for a later
same-PR suffix; any actual capture requires another exact order after
independent review).

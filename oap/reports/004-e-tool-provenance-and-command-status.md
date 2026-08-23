# OAP Coding-Agent Report — 004-e

## Work order
- Identifier: `004-e`; order path: `oap/orders/004-e-tool-provenance-and-command-status.md`; numeric objective: `004`
- PR mode: AMENDED_EXISTING_PR

## Status
COMPLETE

The bounded implementation and diagnostic objective completed. The two permitted fresh live attempts ended `command_incomplete` and `command_failed`; neither was classified as governance-derived `sentinel_missing`, and no sentinel success or readiness increase was claimed.

## Executive summary
Amended objective-004 PR #6 with repository-file versus crossing-boundary provenance facts, terminal-whitespace classification, cache reconciliation against observed bytes, and a strict ordinary-read lifecycle gate. Focused fake-event/diagnostic tests prove successful, failed, duplicate, wrapper, whitespace, non-whitespace, and privacy behavior.

Two fresh real-Codex invocations were run, the exact round budget. The first exposed the previously hidden lifecycle failure: generic command events showed started +1/failed +1/completed +0, but the then-current intended-read recognizer saw zero intended reads, so the run was `command_incomplete`. After a focused recognizer amendment, the second fresh invocation recognized exactly one intended read with started +1/failed +1/completed +0 and returned `command_failed`. No successful completed read existed, so no governance-derived sentinel result could be attributed and objective-004 completion remained 35%.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #6, https://github.com/ulfe-lmi/slaif-local-coding/pull/6, OPEN, non-draft
- Base: `main` at `7a2c36a0a40958a6059a765c2f9d5e5bf4ddc161`
- Head branch: `oap/004-real-codex-governed-e2e`
- Starting remote SHA: `7d76caca14179d3350ccf703cee7f504096ec530`
- Implementation head SHA: 1553a1e922dd1adca26cb7c6e5ae615c5977e3d6
- Report publication commit: SELF
- Implementation commits pushed before report: `1553a1e922dd1adca26cb7c6e5ae615c5977e3d6` (`OAP 004-e: gate provenance and command lifecycle`)
- New PR this round: NO; amended existing PR: YES; merge performed: NO

## Changes and files
- `src/slaif_local_coding/e2e.py`: added bounded dependency command-observation facts, shell-wrapper-safe recognition of exactly one intended read, output hash/length and terminal-whitespace hashes without retention, lifecycle classification, sentinel gating, observed-byte cache reconciliation, and provenance fields.
- `tests/test_e2e.py`: added focused coverage for one successful read, string zero exit, failed/duplicate/wrapper reads, lifecycle-gated sentinel classification, observed-byte cache reconciliation, terminal-whitespace normalization, non-whitespace observation mismatch, and sentinel privacy.
- `README.md`: documented provenance, byte-length, terminal-whitespace, observed-byte cache validation, and lifecycle-gating semantics and privacy limits.
- `oap/COMPLETENESS.md`: recorded the two fixed live outcomes without increasing objective-004 completion from 35% or branch readiness from approximately 78%.
- `oap/active` and `oap/orders/004-e-tool-provenance-and-command-status.md`: committed unchanged activated strategic bytes.

## Acceptance evidence
### Criterion 1 — provenance distinction
PASSED. Diagnostic facts separately expose repository hash/length, observed crossing-boundary hash/length, equality booleans, terminal-whitespace-only equality, and fixed provenance. Focused tests classify exact equality, terminal-whitespace normalization, non-whitespace mismatch, and unavailable observation.

### Criterion 2 — observed-byte cache validation
PASSED. Cache reconciliation now compares persisted dependency source hashes to full observed crossing-boundary bytes, not repository disk bytes. The fake one-invocation miss test proves a stored source equal to observed bytes has no consistency error; focused tests prove terminal-whitespace and non-whitespace classifications independently.

### Criterion 3 — command lifecycle gate
PASSED. `sentinel_missing` is returned only after process/tool success plus exactly one intended read with one successful completed lifecycle, zero failures, and observable output hash/length. Otherwise the fixed run result is `command_failed` or `command_incomplete`. The second live invocation demonstrated the failed gate.

### Criterion 4 — two fresh live invocations
PASSED with the explicitly supported failure outcome. Attempt one: exit status 0, duration 83.941 seconds, 1695 event bytes, two `command_execution` calls, generic lifecycle started +1/failed +1/completed +0, recognized intended reads 0, command state `command_incomplete`, fixed failure `command_incomplete`. Attempt two: exit status 0, duration 78.988 seconds, 1670 event bytes, two `command_execution` calls, recognized intended reads exactly 1, started +1/failed +1/completed +0, successful reads 0, command state `command_failed`, fixed failure `command_failed`. Both had `sentinel_passed=false`; no third invocation was made.

### Criterion 5 — focused hash/length/lifecycle/privacy tests
PASSED. The focused pytest selection ran 10 tests and all passed. Full pytest ran 274 tests: 274 passed and 7 established opt-in live-service tests skipped. Public diagnostic assertions confirmed the ephemeral sentinel token was absent from serialized sanitized facts.

### Criterion 6 — factual documentation/completeness
PASSED. Documentation describes the new boundary without claiming successful live lifecycle or sentinel compliance. Objective 004 remains 35% complete and the branch remains approximately 78% ready.

### Criterion 7 — local gates and implementation CI
PASSED at implementation-head scope. Every named local gate passed, and GitHub `test` was SUCCESS at implementation head `1553a1e922dd1adca26cb7c6e5ae615c5977e3d6`.

## Verification
- `uv lock --check`: PASSED — exit 0.
- `uv sync --frozen --extra dev`: PASSED — locked/frozen environment checked.
- `uv run --frozen ruff check .`: PASSED — all checks passed.
- `uv run --frozen ruff format --check .`: PASSED — 107 files already formatted.
- `uv run --frozen mypy src tests`: PASSED — no issues in 35 source files.
- `uv run --frozen pytest -q`: PASSED — 274 passed, 7 skipped; the seven are established opt-in live-service skips and are not counted as live passes.
- `uv build`: PASSED — wheel and sdist built.
- `python3 -m compileall -q src tests oap/bin`: PASSED — exit 0.
- `bash -n oap/bin/*.sh`: PASSED — shell syntax valid.
- `git diff --check`: PASSED — no whitespace errors.
- `uv run --frozen pytest tests/test_e2e.py -q -k 'command_event_lifecycle or dependency_observation or sentinel_failure_is_gated or dependency_cache_reconciliation or one_invocation_diagnostic or terminal_whitespace_boundary or non_whitespace_observation'`: PASSED — 10 passed, 15 deselected.
- Secret/raw-content scan of scoped added lines: PASSED — no credential, private-key, bearer, or raw-secret pattern matched.
- Private absolute path scan of scoped added lines: PASSED — no match.
- Scoped diff audit: PASSED — only the six implementation/transcript paths listed above changed before the report.
- Protected-host snapshot comparison: PASSED — service state/PID, listener set, start-script hash, and systemd unit hashes matched the `004-d` pre-diagnostic baseline with timestamp ignored.

## Live model/service evidence
- Host/user: `hinton1` / `janezp`; Codex CLI reported 0.149.0.
- Protected upstream: loopback port 18020. Read-only authenticated `/health` returned HTTP 200 with zero body bytes and `/v1/models` returned HTTP 200 with one model. The model entry exposed no context field, no modalities field, and no lowercase `image` occurrence; it was treated as text-only/zero-image, not as a vision service.
- Qwen remained active/running with main PID 26028, listener `0.0.0.0:18020`, start-script SHA-256 `b2d836246bfe7bc824f8a68345831960d23561b7027f3d9f48de344d5a2bc109`, and both discovered unit-file copies at SHA-256 `64b3ccd5bdb64da4e3dcabca660fada8155583c96b6bc11de47536e595df5910`.
- Active Codex configuration SHA-256 remained `6592a3e2a70ffa00d2d1a2a6c7bb49263d24be7864b0561a69cec3153ebfbc8d`. OAP runtime env remained mode 0600.
- Each live attempt used a fresh disposable fixture/Codex home and a repo-owned candidate adapter on development port 18031 only. Adapter `/healthz` and `/readyz` returned HTTP 200 before use. The adapter was stopped afterward and port 18031 was absent. No protected model/vLLM/network/profile/systemd/key state was changed.
- First live sanitized facts: repository dependency SHA-256 `5cfcf2506a209c0f241e3ff8dd463c50a9933d9200f79f3dc8a477316f323145`, length 127; observed hash/length unavailable; provenance `unavailable`; cache miss +1/hit +0; compiler attempts +2/compiler calls +3; dependency observation metric +1; injected requests +2; persistent inventory before 0 entries and after 0 entries; consistency error `observed_dependency_unavailable`; cache classification `observation_mismatch`; run result `command_incomplete`.
- Second live sanitized facts: repository dependency SHA-256 `b7b898d7754cefaa939b8e36acaa08ceaaf3a753dca15b25c19e8c9ee49f9bf0`, length 127; observed hash/length unavailable; provenance `unavailable`; cache miss +1/hit +0; compiler attempts +2/compiler calls +3; dependency observation metric +1; injected requests +2; persistent inventory after one dependency entry of 1335 bytes with source prefix `d636d893e8a9` and one pinned root entry of 3079 bytes with source prefix `af1c35cda27f`; consistency error `observed_dependency_unavailable`; cache classification `observation_mismatch`; run result `command_failed`.

## GitHub CI / required checks
- Implementation-head check `test`: SUCCESS at `1553a1e922dd1adca26cb7c6e5ae615c5977e3d6`.
- All required implementation-head checks green at drafting: YES.
- Final report-head check: PENDING at drafting, as expected for a report-only child push; response signaling was withheld until its final state was independently checked. Strategy also verifies the final head.

## Local setup/dependencies
- Used repository `.venv` and locked `uv --frozen` commands; no dependency or lock change.
- No sudo action was performed.
- Adapter config/cache and Codex fixture/home were caller-owned disposable temporary boundaries; raw material was discarded after extracting sanitized facts. No production data was used.

## Documentation
Updated `README.md` with provenance fields, terminal-whitespace classification, observed-byte cache reconciliation, lifecycle gating, and raw-content prohibitions. Updated `oap/COMPLETENESS.md` with the actual two outcomes while leaving completion values unchanged as required by the failed-command result.

## Safety/scope confirmations
- Unrelated files changed: NO.
- Secrets, raw prompts/source/tool output/images/request/response bodies, credentials, full private paths, or customer data committed/logged/reported: NO.
- Production systems/data used: NO.
- Protected 18020/Qwen/Codex fixture changed: NO.
- Required tests skipped/not run: ordinary opt-in live suite SKIPPED by default; the explicitly required two real diagnostics ran. Final report-head CI was PENDING at drafting and was checked before signaling. No other named gate was skipped.
- Scope deviation: NO.
- Third/retry invocation beyond the two fresh attempts: NO.
- Sentinel success/completeness increase claimed: NO.
- Extra objective PR: NO; coding merge/auto-merge: NO.
- Strategic-authored active/order bytes edited by coding: NO; their exact activated contents were committed.
- Final report commit is report-only: YES.

## Known limitations/blockers
- Neither live ordinary read completed successfully. Therefore this round provides no live evidence that a successful read crossed the boundary, cannot classify the stored dependency hash as terminal-whitespace normalization versus another observation mismatch, and cannot attribute sentinel absence to model governance.
- The second run's persisted dependency source prefix remained `d636d893e8a9` while that fresh synthetic repository dependency prefix was `b7b898d7754cef`; because observed bytes were unavailable, the helper correctly emitted `observed_dependency_unavailable` rather than guessing cache contamination or normalization.
- This round does not prove forced/equivalent compaction success, vision E2E, signed multi-user identity, gateway integration, systemd operation, production readiness, or cutover readiness.

## Recommended strategic follow-up
Factual option for strategy: authorize a narrowly scoped follow-up to diagnose why the Codex CLI's wrapped `cat GOVERNANCE-DEPENDENCY.md` invocation reports failed, then use a fresh authorized round to validate successful observed-byte provenance and governance classification. Strategy decides whether and when to continue objective 004.

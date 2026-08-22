# OAP Coding-Agent Report — 004-d

## Work order
- Identifier: `004-d`; order path: `oap/orders/004-d-dependency-cache-diagnostics.md`; numeric objective: `004`
- PR mode: AMENDED_EXISTING_PR

## Status
COMPLETE

The diagnostic objective completed with the explicitly permitted `sentinel_missing` result. No sentinel success or completeness increase is claimed.

## Executive summary
Amended PR #6 with privacy-preserving dependency-cache diagnostics, focused tests, and factual documentation. One fresh actual Codex invocation ran against one fresh disposable fixture/Codex home and one fresh adapter/cache boundary. It exited 0, used the command tool twice, and ended `sentinel_missing`. The cache counters showed one miss, zero hits, two persisted valid entries, and a stored dependency source-hash prefix different from the observed fixture dependency. The helper therefore classified the outcome as `observation_mismatch`. This rules out expected same-fixture retry reuse for this run; it does not distinguish cross-content/stale index creation from a source-hash/provenance or observation-mapping defect.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #6, https://github.com/ulfe-lmi/slaif-local-coding/pull/6, OPEN, non-draft
- Base: `main` at `7a2c36a0a40958a6059a765c2f9d5e5bf4ddc161`
- Head branch: `oap/004-real-codex-governed-e2e`
- Starting remote SHA: `bfc291a2a9f782fa051b137e68fee1c47c35e941`
- Implementation head SHA: 9368614090aad1df7f5e05e1aa3f2df11730c662
- Report publication commit: SELF
- Implementation commits pushed before report: `e9719b7` (`OAP 004-d: dependency cache diagnostics`) and `9368614090aad1df7f5e05e1aa3f2df11730c662` (`OAP 004-d: expose dependency observation diagnostics`)
- New PR this round: NO; amended existing PR: YES; merge performed: NO

## Changes and files
- `src/slaif_local_coding/e2e.py`: added sanitized metric deltas, persistent-cache inventory extraction, hit/miss reconciliation, fixed classifications, command lifecycle counts, and exactly-one-invocation diagnostic facts.
- `src/slaif_local_coding/constitution/pipeline.py`: added bounded per-status dependency working-set observations for included/missing/omitted states.
- `tests/test_e2e.py`: covered inventory fields/order/bounds, metric deltas, reconciliation, mismatch detection, classification, command-event counting, diagnostic execution, and absence of raw sentinel content.
- `tests/test_dependency_acquisition.py`: covered included/missing/omitted working-set metrics.
- `README.md`: documented diagnostic fields and the no-raw-content boundary.
- `oap/COMPLETENESS.md`: kept objective 004 at 35% and branch total at approximately 78%; added only that diagnostics are being gathered.
- `oap/active` and `oap/orders/004-d-dependency-cache-diagnostics.md`: committed unchanged activated strategic bytes.

## Acceptance evidence
### Criterion 1 — sanitized helper facts
PASSED. The result contract exposes fixture root/dependency SHA-256 values, stability, before/after inventories, cumulative-to-attempt deltas, dependency included/missing/omitted counts, compiler attempts/calls, injected-request count, command started/completed/failed counts, tool-call count, sentinel boolean/fixed reason, invalid-entry count, and bounded inventory metadata.

### Criterion 2 — focused tests
PASSED. Focused tests proved extraction, reconciliation, known/unknown hits, miss/hash mismatch detection, fixed classifications, approved inventory fields/order/recency, root-versus-dependency filtering, and privacy boundaries using canned fixtures.

### Criterion 3 — one actual invocation
PASSED as explicitly permitted. Exactly one fresh Codex CLI invocation completed in 117.977 seconds with exit status 0, event-byte bound 1581, two command tool calls, command events started=1/completed=0/failed=1, `sentinel_passed=false`, and fixed reason `sentinel_missing`. There was no retry loop or second Codex invocation.

### Criterion 4 — anomaly classification
PASSED: classified `observation_mismatch`.
- Persistent inventory before invocation: zero entries, zero invalid entries.
- Metric deltas: root observations +2; dependency observations +1; misses +1; hits +0; invalid +0; budget +0; injected requests +2; compiler attempts +2; compiler calls +3; working-set included/missing/omitted +1/+1/+0.
- Observed fixture hashes: root `af1c35cda27f6aac380eab5c2ef899189d33242624792b46c35960efb49144ef`; dependency `4eae19d4cd7205b5bd788cf18aaafd60dac58231eff110010b8ec5da7d29cb87`.
- Persisted root entry: logical-key prefix `ab15b6cd1eba`, source prefix `af1c35cda27f`, 3314 bytes, pinned=true.
- Persisted dependency entry: logical-key prefix `abec6b3ee1c9`, source prefix `d636d893e8a9`, 1475 bytes, pinned=false.
- The dependency source prefix did not match the fixture dependency; consistency error was `cache_miss_stored_source_hash_mismatch`. A different-source dependency entry was present after the call.
This is not an expected retry hit because the boundary began empty and the attempt recorded miss +1/hit +0. The evidence establishes a mechanical observation/index mismatch but cannot identify whether its ultimate cause is cross-content index creation, stale provenance, or hash/path mapping without further authorized diagnosis.

### Criterion 5 — gates and CI
PASSED at implementation-head scope. Every named local gate passed, and GitHub `test` was SUCCESS at implementation head `9368614090aad1df7f5e05e1aa3f2df11730c662`. Final report-head CI was PENDING when this immutable report was drafted, as expected for a report-only child commit; strategy independently verifies it.

## Verification
- `uv lock --check`: PASSED — exit 0.
- `uv sync --frozen --extra dev`: PASSED — locked/frozen environment checked.
- `uv run --frozen ruff check .`: PASSED — all checks passed.
- `uv run --frozen ruff format --check .`: PASSED — 105 files already formatted.
- `uv run --frozen mypy src tests`: PASSED — no issues in 35 source files.
- `uv run --frozen pytest -q`: PASSED — 267 passed, 7 skipped; the seven are the established opt-in live-service skips and are not counted as live passes.
- `uv build`: PASSED — wheel and sdist built.
- `python3 -m compileall -q src tests oap/bin`: PASSED — exit 0.
- `bash -n oap/bin/*.sh`: PASSED — shell syntax valid.
- `git diff --check`: PASSED — no whitespace errors.
- Secret/raw-content scan of scoped added lines: PASSED — no credential/private-key/bearer/API-key pattern matched.
- Scoped diff audit: PASSED — only the eight implementation/transcript paths listed above changed before the report.
- Protected-host snapshot comparison: PASSED — Qwen active state/PID/unit hash, active Codex config hash, protected listener state, and authenticated upstream health/model results were stable before and after.
- Final report-head CI: PENDING at drafting — report-only push may create a new run; strategy verifies current head.

## Live model/service evidence
- Host/user: `hinton1` / `janezp`; Codex CLI reported 0.149.0.
- Protected upstream: loopback port 18020; authenticated `/health` HTTP 200 and `/v1/models` HTTP 200 before and after. The catalog advertised one model with context 150000 and no image/modality capability field; it was treated as text-only/zero-image, not as a vision service.
- Qwen service remained active/running with main PID 26028 and unchanged unit aggregate SHA `8b6b31f527fe4a6bfc9001b1e26cf2d8a3989b529e4fe37e44cce633dde7917b`.
- Active Codex configuration SHA remained `6592a3e2a70ffa00d2d1a2a6c7bb49263d24be7864b0561a69cec3153ebfbc8d`.
- Candidate adapter used repo-owned code on development port 18031 only, passed health/readiness, and was stopped after the single diagnostic. Port 18031 was absent afterward. No protected model/vLLM/network/profile/systemd/key state was changed.

## Local setup/dependencies
- Used repository `.venv` and locked `uv` commands; no dependency or lock change.
- No sudo action was performed.
- Adapter config/cache and Codex fixture/home were caller-owned disposable temporary boundaries; raw material was discarded after extracting sanitized facts. No production data was used.

## Documentation
Updated `README.md` with one-invocation diagnostic fields, persistent-cache inventory limits, reconciliation outputs, and explicit raw-content prohibitions. Updated `oap/COMPLETENESS.md` factually without increasing 35% objective readiness or approximately 78% branch total.

## Safety/scope confirmations
- Unrelated files changed: NO.
- Secrets, raw prompts/source/tool output/images/request/response bodies, credentials, full private paths, or customer data committed/logged/reported: NO.
- Production systems/data used: NO.
- Protected 18020/Qwen/Codex fixture changed: NO.
- Required tests skipped/not run: ordinary opt-in live suite SKIPPED by default; the explicitly required real diagnostic ran. Final report-head CI was PENDING at drafting. No other named gate was skipped.
- Scope deviation: NO.
- Second/retry model invocation: NO.
- Sentinel success/completeness increase claimed: NO.
- Extra objective PR: NO; coding merge/auto-merge: NO.
- Strategic-authored active/order bytes edited by coding: NO; their exact activated contents were committed.
- Final report commit is report-only: YES.

## Known limitations/blockers
- The fixed sanitized evidence proves that the newly stored dependency index does not carry the observed dependency hash, but does not identify the internal stage responsible.
- The invocation remained `sentinel_missing`; no governance-derived acknowledgment was obtained.
- This round does not prove forced/equivalent compaction success, vision E2E, signed multi-user identity, gateway integration, systemd operation, production readiness, or cutover readiness.

## Recommended strategic follow-up
Factual options for strategy: authorize a narrowly scoped provenance audit connecting acquired dependency bytes to compiled-index source hashing/storage, then rerun one fresh invocation after any fix; separately retain governance-sentinel and vision/compaction work as unresolved objective-004 gaps.

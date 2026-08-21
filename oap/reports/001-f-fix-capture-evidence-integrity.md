# OAP Coding-Agent Report — 001-f

## Work order
- Identifier: `001-f`
- Order path: `oap/orders/001-f-fix-capture-evidence-integrity.md`
- Numeric objective: `001`
- PR mode: AMENDED_EXISTING_PR

## Status
COMPLETE

## Executive summary
Capture facts now distinguish the actual captured marker location from the normalized canonical fixture location. The canonical detector fixture contains only `model` and `input`, with synthetic provenance in a separate file. Any malformed or duplicate marker in a supported user position now invalidates the entire captured project root. Three fresh Codex 0.149.0 captures, the cumulative local gate, the full live matrix, variant evidence, and implementation-head CI passed.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #2, `https://github.com/ulfe-lmi/slaif-local-coding/pull/2`, OPEN and non-draft
- Base/head: `main` / `oap/001-agents-observation-manifest`
- Starting remote SHA: `f77e9c8307b4556c971caf4c44b5d2c0e04ee5b1`
- Implementation head SHA: 0cbe121524cd3d6806b49cada5ffc704c04b1f17
- Report publication commit: SELF
- Implementation commits pushed before report: `0cbe121524cd3d6806b49cada5ffc704c04b1f17`
- New PR this round: NO
- Amended existing PR this round: YES
- Merge performed: NO

## Changes and files
- `src/slaif_local_coding/constitution/detector.py`: rejects the entire supported project marker set when any supported marker is malformed or when valid markers are duplicated.
- `tests/helpers/capture_codex_project_envelope.py`: reports `actual_user_marker_location` and `canonical_user_marker_location` separately, returns safe facts separately, and hashes the canonical request-only fixture.
- `tests/fixtures/codex/0.149.0/`: request fixture now has exactly `model` and `input`; synthetic provenance is separate and never detector/upstream input.
- `tests/test_capture_helper.py`, `tests/test_observation.py`: cover several actual indexes, canonical byte identity, exact fixture allowlist, provenance separation, valid+malformed/unsafe/duplicate, malformed-only, one-valid-only, and unsupported positions.
- `README.md`, `docs/ADAPTER-CONFIGURATION.md`: document actual versus canonical locations, request-only fixture scope, and mixed-marker strictness.
- Exact strategic order and active selector were committed unchanged.

## Acceptance evidence
### Criterion A — truthful actual and canonical facts
- PASSED. Three fresh disposable Codex CLI 0.149.0 runs each reported actual path `$.input[1].content[0].text`, canonical path `$.input[0].content[0].text`, user/`input_text`, `instructions_corroborated=false`, content byte length 65, equal safe content hash, and canonical request digest `7b0066b1af228c06f30f91ed4c87d823847e7363c3307c79eec4ba5d680f469a`.
- The three request fixtures were byte-identical to each other and the committed canonical fixture. Temporary raw capture state and outputs were deleted.

### Criterion B — provider fixture/provenance separation
- PASSED. `project_instructions_responses.json` has exact top-level keys `{model,input}` and no auth, IDs, tools, metadata, provenance, top-level instructions, or internal prompt fields.
- `project_instructions_provenance.json` is separately documented as synthetic-only and is not passed to the detector or upstream. Helper facts cannot alter canonical fixture bytes.

### Criterion C — unique-valid-marker strictness
- PASSED. Unit tests prove valid+malformed, valid+unsafe, valid+duplicate, and malformed-only supported markers produce zero project roots and incomplete parsing status. One valid marker detects; assistant/metadata markers neither poison nor establish the supported root.
- PASSED. A ten-variant foreground run (canonical, matching corroboration, valid+malformed/unsafe/duplicate, malformed-only, instructions-only, mismatch, plain mention, wrong-role metadata) returned ten HTTP 200 responses and ten upstream round trips. Root/candidate deltas were exactly 2/2, from canonical and matching corroboration only; request observation did not add an upstream call or rewrite bytes.

### Criterion D — cumulative evidence
- PASSED. Local static/unit/build gates, three captures, foreground live matrix, ten-variant proof, and implementation-head GitHub CI all completed successfully.
- No long-session, compaction, compiler, cache, acquisition, injection, or semantic-governance claim is made.

## Verification
- `uv lock --check`: PASSED — lock resolved without change.
- `uv sync --frozen --extra dev`: PASSED — frozen environment checked.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen ruff format --check .`: PASSED — 64 files formatted.
- `uv run --frozen mypy src tests`: PASSED — 19 source files, no issues.
- `uv run --frozen pytest -q`: PASSED — 158 passed; 5 live-only tests skipped in this ordinary invocation and then ran separately.
- `SLAIF_LIVE_TEST=1 uv run --frozen pytest -q tests/test_live.py`: PASSED — 5 passed.
- `uv build`: PASSED — source distribution and wheel built.
- `python3 -m compileall -q src tests oap/bin`: PASSED.
- `bash -n oap/bin/*.sh`: PASSED.
- `git diff --check 91463ae3199dd06e0448a9422a5e713da8ee92df...HEAD`: PASSED.
- Focused credential/raw-content scan and scoped diff audit: PASSED — only synthetic test credentials/placeholders were matched; no real secret or raw capture was found.

## Live model/service evidence
- Before/after `qwen-serving-vision.service`: active/running, PID 4174, start time Thu 2026-08-20 23:27:10 CEST; inactive `qwen-serving.service` remained inactive.
- Before/after listeners: protected `10.8.132.76:18020` only. Candidate loopback 18031 was stopped; 18021/18031 were free at report drafting.
- Full foreground matrix passed health/readiness/models/text, forced and automatic tools, multi-turn, SSE, one-image vision, and two-image newest retention. Bounded calls used the existing protected credential reference without printing or persisting it.
- Protected hashes remained exact: vision env `affabb5701b67b5fcb7cab2e3ae1835e84e19dc98a7f1eb245cf3e49b76b3b5b`; vision unit `fc88870b4f4afee214c25dc9ec544c4178c300bf4d78092a4d12787a955e2e94`; vision start script `8c87e0104b25c9600235a97555c4b0a1d0ea55d34ccb4094af428c8b4501f89f`; Qwen profile `18ead58ac440d29ce2e86addf855c24f471021c6050d4da685320a2cf6eb62eb`; coding overlay `cc243c7057f00cb15a06a5be63c6d811f8f473e367d521b1b6ea6207c794509a`; OAP runtime env `22fdefd324d631353f1b9fedad3bad1fc75577073794a882ce2dd57bc5794bf1`. Vision env mode remained 0777 byte-for-byte.

## GitHub CI / required checks
- Implementation head `0cbe121524cd3d6806b49cada5ffc704c04b1f17`: `CI / test` SUCCESS in 19 seconds.
- All required checks green at drafting: YES.
- Report-head checks may be pending after publication; strategy verifies them independently.

## Local setup/dependencies
- Host `PATH` lacked `uv`; uv 0.12.5 was used from a temporary tooling virtual environment. No dependency or lockfile changed.
- Temporary captures/candidate state were stopped and removed. Build artifacts are ignored. No sudo or persistent repo-local service was used.

## Documentation
- UPDATED. Primary and configuration documentation plus fixture README now state the actual/canonical path distinction, request/provenance separation, and strict mixed-marker behavior.

## Safety/scope confirmations
- Unrelated/pre-existing work overwritten: NO.
- Secrets/raw capture/request/source/tool/image content committed or reported: NO.
- Protected 18020/Qwen/Codex fixture changed: NO.
- Required tests skipped/not run: NO; the ordinary suite's five opt-in skips ran and passed in the required live command.
- Scope deviation: NO.
- Extra objective PR: NO.
- Coding merge: NO.
- Auto-merge: NO.
- Active/order edited by coding: NO.
- Report commit report-only: YES, subject to remote post-push verification.

## Known limitations/blockers
- Support remains conservative for the observed Codex CLI 0.149.0 envelope. All three fresh runs used the same actual index, but this is evidence for these runs only; the helper and tests do not hardcode it as empirical fact.
- The upstream rejected empty-input instructions-only and assistant-message exploratory shapes with HTTP 400. Required accepted negative variants were rerun using ordinary input plus top-level instructions and metadata placement; all ten accepted variants passed with the expected zero-root deltas outside the two positive cases.
- Objective 001 remains request-only observation and deterministic candidate extraction; no compiler/cache/injection or compaction compliance is provided.

## Recommended strategic follow-up
Independently review the actual/canonical fact split, fixture/provenance boundary, mixed-marker rejection, current-head CI, and protected-state evidence; strategy alone decides acceptance or continuation.

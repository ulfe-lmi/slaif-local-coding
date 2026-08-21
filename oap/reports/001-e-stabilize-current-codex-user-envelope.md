# OAP Coding-Agent Report — 001-e

## Work order
- Identifier: `001-e`
- Order path: `oap/orders/001-e-stabilize-current-codex-user-envelope.md`
- Numeric objective: `001`
- PR mode: AMENDED_EXISTING_PR

## Status
COMPLETE

## Executive summary
Codex CLI 0.149.0 project governance is now detected at the stable captured top-level Responses user/`input_text` position. Three fresh disposable captures completed and normalized to byte-identical canonical fixture bytes; all three omitted optional top-level `instructions` corroboration. Matching corroboration adds evidence, while conflicting or duplicate corroboration produces no root. The request-only observer remains bounded and semantics-preserving.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #2, `https://github.com/ulfe-lmi/slaif-local-coding/pull/2`, OPEN and non-draft
- Base/head: `main` / `oap/001-agents-observation-manifest`
- Starting remote SHA: `2233fedc914eda7de5490c3f3dc2b4b604a5d04c`
- Implementation head SHA: dc7feb66d5f65c8d002eb5515ec31eec4d2fc410
- Report publication commit: SELF
- Implementation commits pushed before report: `dc7feb66d5f65c8d002eb5515ec31eec4d2fc410`
- New PR this round: NO
- Amended existing PR this round: YES
- Merge performed: NO

## Changes and files
- `tests/helpers/capture_codex_project_envelope.py`: accepts exactly one supported user occurrence, zero/one matching instructions occurrence, safe label/tail grammar, canonical user-only output, and separate sanitized corroboration facts.
- `src/slaif_local_coding/constitution/detector.py`: detects the exact user envelope, excludes the environment tail from source bytes, optionally records matching instructions evidence, and rejects conflicting/duplicate/malformed supported blocks.
- `tests/fixtures/codex/0.149.0/`: replaces the old developer primary fixture with the canonical fresh user fixture and corrects provenance without modifying historical reports.
- `tests/test_capture_helper.py`, `tests/test_observation.py`: cover normalization, exact hashes/locations, optional corroboration, false positives, unsafe labels, tail exclusion, and duplicate/conflict failure.
- `README.md`, `docs/ADAPTER-CONFIGURATION.md`: document the current capture, delimiter/tail/hash contract, client-supplied trust boundary, conservative version scope, and observation-only limitations.
- Exact strategic order and `oap/active` selector were committed unchanged.

## Acceptance evidence
### Criterion A — three fresh normalized captures
- PASSED. Three separate Codex CLI 0.149.0 runs each completed the fake Responses endpoint with one user/`input_text` marker at `$.input[0].content[0].text`.
- All three reported `instructions_corroborated=false`, content length 65, equal safe content digest, and byte-identical canonical fixture digest `1e9c7be2fece595e159e7af6b69d5932154241ca88764ac81ce8f739bc0c113b`.
- Temporary homes, repositories, endpoints, and fixture outputs were removed after comparison; no raw capture persisted.

### Criterion B — exact user-envelope detector
- PASSED. The parser requires the captured boundary, user role, `input_text` type, exact delimiters, safe logical label, and supported terminal tail.
- Exact inner UTF-8 bytes alone determine source length/hash/candidates. A matching instructions block adds corroborating evidence; absence is accepted; mismatch/duplicate is incomplete with no root. Non-exact instructions mentions are ignored.

### Criterion C — exact tests
- PASSED. Focused helper/observation/app suite: 130 passed. Full local suite: 149 passed and 5 opt-in live tests skipped in that invocation; the same five live tests subsequently ran and passed separately.
- Existing input-file, paired-tool, reference/path/span/budget/identity/fallback and objective-000 proxy/image/SSE/tool/error/body/depth coverage remained green.

### Criterion D — live and cumulative evidence
- PASSED. Foreground candidate on loopback 18031 passed health/readiness/models/text, forced/automatic/streaming tools, multi-turn, SSE, one-image, and two-image retention matrix: 5 passed.
- Final seven-variant bounded run returned HTTP 200 for user-only, matching instructions, instructions-only, mismatch, duplicate, plain mention, and wrong-role metadata. Root delta was 2 and candidate delta was 2, limited to user-only and matching corroboration; seven requests made seven upstream round trips.
- No compaction, long-session compliance, compiler, cache, or semantic-governance claim is made.

## Verification
- `uv lock --check`: PASSED — lock resolved without change.
- `uv sync --frozen --extra dev`: PASSED — frozen environment checked.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen ruff format --check .`: PASSED — 62 files formatted.
- `uv run --frozen mypy src tests`: PASSED — 19 source files, no issues.
- `uv run --frozen pytest -q`: PASSED — 149 passed, 5 live-only skipped in this non-live invocation.
- `SLAIF_LIVE_TEST=1 uv run --frozen pytest -q tests/test_live.py`: PASSED — 5 passed.
- `uv build`: PASSED — sdist and wheel built after removing the temporary in-tree tooling environment from package input.
- `python3 -m compileall -q src tests oap/bin`: PASSED.
- `bash -n oap/bin/*.sh`: PASSED.
- `git diff --check 91463ae3199dd06e0448a9422a5e713da8ee92df...HEAD`: PASSED.
- Focused sensitive-diff scan: PASSED — no credential/header/session/cookie pattern found.

## Live model/service evidence
- Before and after: `qwen-serving-vision.service` active/running with PID 4174 and unchanged start time; inactive `qwen-serving.service` remained inactive.
- Before and after: only protected `10.8.132.76:18020` listened. Candidate loopback 18031 was stopped; 18021/18031 were free at report drafting.
- Bounded authenticated calls used the existing protected key reference without printing or persisting it. The upstream fixture was not restarted or reconfigured.
- Required before/after protected hashes matched exactly: vision env `affabb5701b67b5fcb7cab2e3ae1835e84e19dc98a7f1eb245cf3e49b76b3b5b`; vision unit `fc88870b4f4afee214c25dc9ec544c4178c300bf4d78092a4d12787a955e2e94`; vision start script `8c87e0104b25c9600235a97555c4b0a1d0ea55d34ccb4094af428c8b4501f89f`; Qwen profile `18ead58ac440d29ce2e86addf855c24f471021c6050d4da685320a2cf6eb62eb`; coding overlay `cc243c7057f00cb15a06a5be63c6d811f8f473e367d521b1b6ea6207c794509a`; OAP runtime env `22fdefd324d631353f1b9fedad3bad1fc75577073794a882ce2dd57bc5794bf1`.

## GitHub CI / required checks
- Implementation head `dc7feb66d5f65c8d002eb5515ec31eec4d2fc410`: `CI / test` SUCCESS (20 seconds).
- All required checks green at drafting: YES.
- Report-head checks may be pending after publication; strategy verifies them independently.

## Local setup/dependencies
- The host lacked `uv`; version 0.12.5 was installed into a temporary tooling environment, used for verification, then removed. No dependency or lockfile changed.
- Built artifacts and temporary capture/candidate state were removed. No sudo action or persistent repo-local service was used.

## Documentation
- UPDATED. README, adapter configuration documentation, and fixture provenance now describe the stable captured user shape, optional instructions variability, exact grammar/hash boundary, trust boundary, historical correction, synthetic supplements, and observation-only limitations.

## Safety/scope confirmations
- Unrelated/pre-existing work overwritten: NO.
- Secrets or raw capture/request/source/tool/image content committed or reported: NO.
- Protected 18020/Qwen/Codex fixture changed: NO.
- Required tests skipped/not run: NO; the five opt-in tests skipped by the ordinary suite were run and passed under the required live command.
- Scope deviation: NO.
- Extra objective PR: NO.
- Coding merge: NO.
- Auto-merge: NO.
- Active/order edited by coding: NO.
- Report commit report-only: YES (subject to remote post-push verification).

## Known limitations/blockers
- Support is conservative for the observed Codex CLI 0.149.0 envelope only. Future or changed shapes fail without establishing this root.
- This objective provides request-only observation and deterministic candidate enumeration only. It does not implement compiler/ranking/cache/acquisition/injection/rehydration, production multi-user identity, or semantic/compaction compliance.
- Explicit developer/assistant Responses message variants were rejected by the live upstream API itself; the successful wrong-role live negative used accepted metadata placement and still produced zero root/candidate delta.

## Recommended strategic follow-up
Review the exact detector boundary, three-run provenance, live negative evidence, CI, and immutable report commit against objective-001 acceptance; strategy alone decides acceptance or continuation.

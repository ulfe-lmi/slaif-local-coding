# OAP Coding-Agent Report — 004-ak

## Work order

- Identifier: `004-ak`
- Order path: `oap/orders/004-ak-classify-two-byte-sentinel-prefix.md`
- Numeric objective: `004`
- PR mode: `AMENDED_EXISTING_PR`

## Status

FAILED

## Executive summary

Added a closed, privacy-safe two-byte prefix classification to the repository-only `FinalMessageEvidence` support. Event and output-file evidence share the same transient fixed-pair comparison and serialize only an allowlisted label. Exact-sentinel, terminal-CR/LF, sentinel, response, and aggregate acceptance predicates were not changed.

The one authorized live vision acceptance attempt ran once and failed only the unchanged exact-sentinel predicates for turns 1 and 2. The event and output-file channels for both turns were classified as `leading_lf_lf`. All other reported acceptance gates passed. No retry, fixture/prompt/model/service change, acceptance relaxation, or protected-host mutation was performed.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #6 — `https://github.com/ulfe-lmi/slaif-local-coding/pull/6` — `OPEN`, non-draft, mergeable; coding merge: `NO`.
- Base/head: `main` / `oap/004-real-codex-governed-e2e`.
- Starting remote SHA: `1fd59fd4d08f77dc68309d04e11612fbd4ea2059`.
- Implementation head SHA: `d35ec3ce4925ab3ea3592434b768f3618c433f65`.
- Report publication commit: `SELF`.
- Implementation commits pushed before report: `d35ec3ce4925ab3ea3592434b768f3618c433f65`.
- New PR this round: `NO`; amended existing PR: `YES`; merge performed: `NO`.

## Changes and files

- Extended `tests/helpers/vision_e2e_support.py` with the fixed prefix label vocabulary, transient comparison of the twelve exact byte pairs, fixed-shape safe serialization, and `FinalMessageEvidence.prefix_classification`.
- Added exhaustive fixed-class, `other_two_byte_prefix`, `not_applicable`, event/file parity, acceptance-preservation, and serialization-privacy tests in `tests/test_vision_e2e.py`.
- Committed the activated `oap/active` and `oap/orders/004-ak-classify-two-byte-sentinel-prefix.md` bytes unchanged.
- No product, service, fixture, prompt, model, image, metric, bound, or acceptance predicate changed.

## Acceptance evidence

### Criterion A — closed prefix classification

- PASSED — all twelve fixed prefix classes were compared only in memory; an unlisted two-byte prefix maps to `other_two_byte_prefix`; missing, repeated, suffixed, or otherwise non-applicable relationships map to `not_applicable`; exact content maps to `none`.
- PASSED — event and output-file evidence produced identical labels for every exhaustive test case.
- PASSED — serialized evidence contains only the fixed label and existing bounded facts; no sentinel, prefix bytes, prompt, source, image, tool output, path, session, or arbitrary dynamic string is retained by the new field.

### Criterion B — unchanged live acceptance

- FAILED — the exact command ran once and returned `1 failed, 109 deselected in 78.32s`.
- Fixed failure reasons: `turn1_exact_sentinel`, `turn2_exact_sentinel`.
- For both turns and both event/file channels: actual byte length `39`; expected byte length `37`; expected occurred exactly once at offset `2`; common prefix `0`; common suffix `37`; leading extra bytes `2`; trailing extra bytes `0`; prefix class `leading_lf_lf`.
- Both turns exited with status `0`, were not timed out, emitted bounded events, and recorded two tool calls. The unchanged response and sentinel predicates remained false because the final binding was not exact.
- Same session, image-capable catalog, disabled original image detail, context `100000`, and disabled parallel tools all passed.
- Both invocation phases contained two bounded main requests. Image metric deltas were turn 1 `seen=2, removed=0` and turn 2 `seen=4, removed=2`. All four outbound requests passed fixed image identity/count, ordering, governance, non-image, and tool-content predicates.

## Verification

- `git fetch origin --prune`: PASSED — remote reconciled before mutation.
- `uv run --frozen pytest -q tests/test_vision_e2e.py -k 'prefix_classification or final_binding or fixed_final_message or relationship or diagnostic_summary'`: PASSED — `50 passed, 60 deselected`.
- `uv run --frozen ruff check tests/helpers/vision_e2e_support.py tests/test_vision_e2e.py`: PASSED.
- `uv run --frozen ruff format --check tests/helpers/vision_e2e_support.py tests/test_vision_e2e.py`: PASSED — both files already formatted.
- `uv run --frozen mypy src tests`: PASSED — 42 source files checked.
- `SLAIF_VISION_ACCEPTANCE=1 uv run --frozen pytest -q tests/test_vision_e2e.py -k live_vision_exec_resume_acceptance`: FAILED — one authorized attempt; fixed reasons and classifications are recorded above.
- `git diff --check`: PASSED before implementation publication.
- Full pytest after the live failure: `NOT RUN` — the order required stopping after the result.
- Build/wheel validation, compileall, shell syntax, and post-failure broad sensitive scans: `NOT RUN` — the order required stopping after the result.

## Live model/service evidence

- Read-only preflight and post-attempt state: vision unit active/running at PID `364444`, `NRestarts=0`; text unit inactive; authenticated upstream `/health` status `200`; `/v1/models` status `200` with one `qwen3.8-27b` model; process facts showed context `100000` and the one-image limit; development port `18031` had zero listeners afterward.
- The candidate adapter, disposable fixture, cache, session, output files, and logs were temporary and cleaned up by the test context.
- Protected Qwen/vLLM unit, model, port `18020`, network, credentials, and Codex profiles were not changed.

## GitHub CI / required checks

- Implementation-head `test`: `SUCCESS` at `d35ec3ce4925ab3ea3592434b768f3618c433f65`.
- All required implementation-head checks green at report drafting: `YES`.
- Report-head checks may be pending after publication; strategy verifies them.

## Local setup/dependencies

- Used the existing frozen repository `uv` environment and installed no new dependency.
- No persistent runtime configuration, production service, or protected-host setup changed.

## Documentation

- Not updated — this order was limited to bounded repository-only evidence support and tests; acceptance and operational behavior remain unchanged.

## Safety/scope confirmations

- Unrelated files: `NONE`.
- Secrets/raw content: no raw request, response, prompt, source, image, tool data, credential, key, or private payload was retained or published.
- Production/protected resources: no mutation; protected `18020`/Qwen/Codex fixture changed: `NO`.
- Required tests skipped/not run: full pytest, build/wheel validation, compileall, shell syntax, and post-failure broad sensitive scans are `NOT RUN` as stated above.
- Extra objective PR: `NO`; coding merge: `NO`.
- Active/order edited: `NO`; activated bytes were committed unchanged.
- Report commit report-only: `YES`.

## Known limitations/blockers

- The live Codex final-message channels remain non-exact because of the fixed two-byte leading LF/LF relationship; classification is diagnostic only and does not advance completeness or alter acceptance.
- No Local Coding product defect was established by the failed unchanged acceptance.
- Broad post-failure gates were not run by order.

## Recommended strategic follow-up

- Review the fixed `leading_lf_lf` evidence and decide the next objective or human judgment. Coding does not choose that decision.

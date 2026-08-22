# OAP Coding-Agent Report — 003-d

## Work order
- Identifier: `003-d`
- Work-order file: `oap/orders/003-d-dependency-acquisition.md`
- Numeric objective: `003`
- PR mode: `AMENDED_EXISTING_PR`

## Status
`COMPLETE`

## Executive summary
Amended PR #5 with request-only, exact-path dependency observation for `input_file` and one-to-one Responses/Chat tool-result evidence. After successful one-root compilation, the pipeline incrementally compiles at most four observed dependencies by default, validates each index against the declared path/hash/length/candidate set, includes validated dependencies in working-set selection, and preserves missing or invalid dependencies as safe acquisition instructions. Documentation and completeness evidence were updated. All required local gates passed, the implementation-head CI check passed, and bounded live text/compiler/cache testing passed through temporary loopback port 18031.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`
- PR number/URL/state: [#5](https://github.com/ulfe-lmi/slaif-local-coding/pull/5), `OPEN`, non-draft
- Base/head: `main` / `oap/003-working-set-injection-foundation`
- Starting remote SHA: `9c35edc35ed8a911de64eea561066d2cb7a26a25`
- Implementation head SHA: `ea561cd31663fafcf5c8ca5454fab8513d0bf876`
- Report publication commit: `SELF`
- Implementation commits pushed: `ea561cd31663fafcf5c8ca5454fab8513d0bf876` — `feat: acquire evidenced constitutional dependencies`
- New PR this round: `NO`
- Amended existing PR: `YES`
- Merge performed: `NO`

## Changes and files
- Added deterministic request-content dependency observation with a shared exact repository-path validator, exact candidate equality, bounded UTF-8 handling, one-to-one call-ID pairing, duplicate/mismatch/extra/unsafe rejection, and in-memory-only source handoff.
- Added bounded incremental dependency compilation after root compilation, strict index validation, cache reuse, fixed safe outcome metrics, and working-set selection of validated acquired indexes.
- Added `constitution.max_dependency_acquisitions` with default `4` and hard maximum `16`.
- Updated adapter/configuration documentation and the factual completeness table; committed the activated order and advanced `oap/active` to `003-d`.
- Added focused fake-upstream dependency tests and changed the bounded live dependency fixture to use a supported top-level Responses tool-history pairing.
- Files changed in implementation commit: `README.md`; `config/adapter.example.toml`; `docs/ADAPTER-CONFIGURATION.md`; `oap/COMPLETENESS.md`; `oap/active`; `oap/orders/003-d-dependency-acquisition.md`; `src/slaif_local_coding/app.py`; `src/slaif_local_coding/config.py`; `src/slaif_local_coding/constitution/__init__.py`; `src/slaif_local_coding/constitution/detector.py`; `src/slaif_local_coding/constitution/models.py`; `src/slaif_local_coding/constitution/pipeline.py`; `src/slaif_local_coding/constitution/references.py`; `tests/test_app.py`; `tests/test_dependency_acquisition.py`; `tests/test_live.py`.

## Acceptance-criteria evidence

### Criterion 1 — root plus observed P1 compiles once, injects, then reuses
- Result: `PASSED`
- Evidence: `tests/test_dependency_acquisition.py::test_root_plus_dependency_compiles_then_reuses_both_indexes` observed exactly two compiler operations on the first request, included the dependency summary in injected context, produced identical injected context on repeat, and recorded dependency outcomes `cache_miss=1` and `cache_hit=1`.

### Criterion 2 — both acquisition paths with exact ordering/path matching
- Result: `PASSED`
- Evidence: `test_input_file_dependency_is_exact_bounded_and_private`, `test_responses_input_file_and_tool_dependencies_are_deterministic`, and `test_chat_message_tool_result_pairs_with_exact_call_id` cover `input_file`, Responses paired tool results, and Chat paired tool results. Exact normalized path equality and deterministic observation were asserted without retaining source in public observation JSON.

### Criterion 3 — unsafe/invalid evidence fails safely
- Result: `PASSED`
- Evidence: `test_invalid_or_duplicate_evidence_is_never_acquired` covers duplicate, mismatched, and extra evidence; `test_unsafe_mismatched_and_oversized_dependencies_fail_closed` covers unsafe path, missing content, and oversized content; `test_dependency_compiler_failure_still_injects_root_missing_instruction` proves compiler failure still injects root governance with a missing-dependency instruction. Fixed observation reasons and metrics were asserted.

### Criterion 4 — budgets, scores, isolation, and cancellation
- Result: `PASSED`
- Evidence: `test_budget_preserves_missing_dependency_instruction` proves the configured budget leaves a missing instruction and emits `budget_exceeded`; `test_identity_isolation_and_cancellation_slot_release` proves separate configured identities do not share cache results and releases the compiler semaphore after cancellation. Existing compiler/cache tests cover independent confidence/priority validation and all identity/source/schema/compiler/policy/bounds cache-key dimensions.

### Criterion 5 — zero-dependency and proxy behavior preserved
- Result: `PASSED`
- Evidence: The complete fake-upstream suite remained green: `240 passed, 7 skipped`. Existing pipeline, image-policy, tool, SSE, error, disconnect, and envelope-preservation tests passed. Final live suite result was `6 passed, 1 skipped`; the skip was the expected zero-image vision case.

### Criterion 6 — documentation and completeness
- Result: `PASSED`
- Evidence: README and adapter configuration describe exact evidence requirements, bounded incremental compilation, safe metrics, and explicit non-goals. `oap/COMPLETENESS.md` records objective 003 at 75%, branch readiness at approximately 68%, and compaction rehydration as missing without production/vision/Codex E2E claims.

### Criterion 7 — local gates and GitHub CI
- Result: `PASSED`
- Evidence: Every required local command below passed. Implementation head `ea561cd31663fafcf5c8ca5454fab8513d0bf876` had required GitHub check `CI / test` with conclusion `SUCCESS` in run `32583319244`. The report-head check had not completed at drafting and is not represented as green; strategy must independently verify the final report-head check.

## Local verification
- `uv lock --check`: `PASSED` — resolved 32 packages; lockfile unchanged.
- `uv sync --frozen --extra dev`: `PASSED` — checked 31 locked packages into the repository-local environment.
- `uv run --frozen ruff check .`: `PASSED` — all checks passed.
- `uv run --frozen ruff format --check .`: `PASSED` — 92 files already formatted.
- `uv run --frozen mypy src tests`: `PASSED` — no issues in 32 source files.
- `uv run --frozen pytest -q`: `PASSED` — 240 passed, 7 skipped; skips were opt-in live tests.
- `SLAIF_LIVE_TEST=1 uv run --frozen pytest -q tests/test_live.py`: `PASSED` — final run: 6 passed, 1 skipped; image case skipped because the verified fixture is zero-image.
- `uv build`: `PASSED` — source distribution and wheel built successfully.
- `python3 -m compileall -q src tests oap/bin`: `PASSED` — exit 0.
- `bash -n oap/bin/*.sh`: `PASSED` — exit 0.
- `git diff --check 68f212b5ad316b95fa12ef632e1538b56479081b...HEAD`: `PASSED` — no whitespace errors.
- Secret/raw-content scan: `PASSED` — no high-risk credential/auth/private-key pattern in non-test added lines; synthetic test fixtures were excluded as intentional test data.
- Scoped diff audit: `PASSED` — implementation commit changed exactly the 16 in-scope files listed above.

## Live model/service evidence
- Sanitized endpoint/route: private upstream `/health` and `/v1/*`; temporary adapter bound only to `127.0.0.1:18031`; no secrets or private URLs recorded.
- Exact bounded call/result: upstream `/health` returned HTTP `200` with zero-byte body. The temporary adapter ran the final live suite once: HTTP result `6 passed, 1 skipped`. Its enabled synthetic-root test made two bounded Responses calls and proved root/dependency cache reuse, at least two injected pipeline outcomes, and at least one dependency cache hit. The temporary process was stopped and port 18031 was free afterward.
- Intermediate live evidence: two exploratory runs were `FAILED` because the synthetic dependency evidence was embedded in a user content list in an upstream-unsupported shape. The fixture was corrected to a supported top-level Responses `function_call` / `function_call_output` history; only the test fixture changed, and the final required suite then passed.
- Protected fixture mutation: `NO`. Before and after snapshots found `qwen-serving` active with PID `26028` listening on `0.0.0.0:18020`; the user-unit hash remained `64b3ccd5bdb64da4e3dcabca660fada8155583c96b6bc11de47536e595df5910`. No protected model, vLLM, systemd, key, firewall, VPN, profile, or network state was changed. Pre-existing modified/untracked files in the protected serving workspace were observed only and preserved.

## GitHub CI / required checks
- Implementation-head state: `ea561cd31663fafcf5c8ca5454fab8513d0bf876`
- Check `CI / test`: `SUCCESS` — run `32583319244`, job `97055811594`.
- All required green at drafting: `YES` for implementation head; report-head check was `PENDING`/newly triggered and is not claimed green.
- Report-head checks may still be running; strategy independently verifies the final report commit.

## Local setup / dependencies
- Used the repository-local Python 3.12 environment through `uv sync --frozen --extra dev`; no dependency lock change.
- Created temporary `/tmp` TOML/cache/log state for the loopback adapter with synthetic static identity labels. Upstream authentication was read from the running protected process environment without printing or persisting it.
- Started and stopped only the repo-owned temporary adapter on port 18031; no sudo or protected service action was required.

## Documentation
- Updated `README.md` and `docs/ADAPTER-CONFIGURATION.md` for dependency evidence, acquisition limits, validation, metrics, and explicit exclusions.
- Updated `oap/COMPLETENESS.md` factual completion/readiness fields only as ordered.
- Committed the exact activated `oap/orders/003-d-dependency-acquisition.md` and changed only `oap/active` from `003-c` to `003-d`.

## Safety and scope confirmations
- Unrelated files changed: `NO`.
- Secret/raw customer content exposed: `NO`.
- Production/protected resources accessed or changed: bounded authenticated live calls and read-only process/state snapshots only; no protected resource was changed.
- Port 18020 or Qwen/Codex fixture changed: `NO`.
- Required tests skipped/not run: none. The normal suite skipped opt-in live tests, which were then run explicitly; the live image test was `SKIPPED` for the verified zero-image fixture.
- Scope deviation: `NO`.
- Extra objective PR: `NO`.
- Coding-agent merge/auto-merge: `NO`.
- Activated order/active edited: `NO`; their exact intended round transcript bytes were committed.
- Report commit changes only this report: `YES`.

## Known limitations / blockers
- Compaction/new-context rehydration remains explicitly unimplemented.
- Acquisition is request-only and non-recursive; the adapter still never reads a client filesystem or network source.
- The bounded live dependency exercise used supported top-level tool-history evidence. `input_file` acquisition is covered by fake-upstream tests, while the explored nested user-content file shape was rejected by the current upstream and was not made a live success claim.
- Static local appliance identity remains MVP-only; signed multi-user production identity is not implemented.
- No production, vision, real-Codex E2E, gateway, or cutover readiness is claimed.

## Recommended strategic follow-up
- Independently verify the report-head GitHub check and review PR #5.
- If accepted, strategy may schedule the explicitly missing compaction/new-context rehydration objective.
- A later bounded live exercise could assess supported upstream `input_file` compatibility separately from this order without expanding its scope.

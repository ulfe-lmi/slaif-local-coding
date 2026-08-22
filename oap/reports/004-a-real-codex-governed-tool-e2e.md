# OAP Coding-Agent Report — 004-a

## Work order
- Identifier: `004-a`; order path: `oap/orders/004-a-real-codex-governed-tool-e2e.md`; numeric objective: `004`
- PR mode: `CREATED_NEW_PR`

## Status
COMPLETE

## Executive summary
Added a repository-owned, disposable real-Codex CLI 0.149.0 E2E harness and Codex 0.149.0 `shell_command` observation support. A bounded two-invocation live run through the loopback candidate adapter completed both runs successfully with ordinary command-tool use and sentinel-positive final messages. Metrics showed root/dependency compilation on the first governed exchange and persistent reuse on the second invocation without additional compiler model attempts. Documentation records the safety boundary, sanitized evidence, prompt-target limitation, and remaining objective-004 gaps.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`; PR number/URL/state: #6, https://github.com/ulfe-lmi/slaif-local-coding/pull/6, OPEN, non-draft
- Base/head: `main` / `oap/004-real-codex-governed-e2e`
- Starting remote base SHA: `7a2c36a0a40958a6059a765c2f9d5e5bf4ddc161`
- Implementation head SHA: `3363a50c4ffa830e2aa48e942d76b5297e3d7ba9`
- Report publication commit: SELF
- Implementation commits pushed before report: `fcd23b50533ef00e8651f1e177b042445de01cf8`, `3363a50c4ffa830e2aa48e942d76b5297e3d7ba9`
- New PR this round yes; amended existing no; merge performed NO

## Changes and files
- Added `src/slaif_local_coding/e2e.py`: isolated temporary repository/CODEX_HOME/config/catalog generation, serialized process/time/output budgets, sanitized event parsing, bounded retry budget, persistent-cache metric extraction, and raw-state cleanup.
- Added `tests/test_e2e.py`: focused private fixture/config isolation, event parser, final-message sentinel check, attempt-budget, and metric-reader tests.
- Updated `src/slaif_local_coding/constitution/detector.py` to recognize Codex 0.149.0 `shell_command` string/argv read calls while retaining the prior bounded pairing rules.
- Added a focused dependency-acquisition regression in `tests/test_dependency_acquisition.py`.
- Updated `README.md` and `oap/COMPLETENESS.md` with launcher safety, sanitized behavior, limitations, objective-004 completion at 35%, and branch readiness at approximately 78%.
- Committed the activated transcript exactly: `oap/active` and the immutable order file.

## Acceptance evidence
### Criterion 1 — isolated Codex home/config
PASSED. Focused tests verify private temporary repository/CODEX_HOME modes, config mode 0600, custom loopback Responses provider, environment-name credential reference, and clean disposable Git fixture. Active Codex config SHA-256 was identical before and after: `6592a3e2a70ffa00d2d1a2a6c7bb49263d24be7864b0561a69cec3153ebfbc8d`.

### Criterion 2 — real Codex tool use and sentinel compliance
PASSED. Two actual Codex CLI 0.149.0 invocations used max one attempt each. Both returned exit 0, emitted two command-execution item events (started plus completed), and had sentinel-positive final messages. Durations were 60.175s and 66.141s; event byte bounds were 837 and 839.

### Criterion 3 — one-root observation, acquisition, compile, cache reuse
PASSED. Across the two-invocation run: four request-level root observations of the fixture's single root, one dependency cache-miss acquisition, one dependency cache-hit acquisition, four injected requests, compiler model attempts 0 -> 2 after the first invocation -> 2 after the second. The unchanged attempts value proves no additional compiler model calls; cache hits supplied the second invocation.

### Criterion 4 — raw-content containment
PASSED. Scoped diff audit found only approved source/test/transcript paths. Scans found no concrete generated sentinel token, API-key literal, private-key block, authorization header, or temporary-run path. Raw events/output were confined to temporary boundaries and cleaned; this report contains only fixed labels, counters, durations, and hashes.

### Criterion 5 — existing fake-upstream behavior preserved
PASSED. Full non-live suite: 254 passed, 7 skipped.

### Criterion 6 — honest documentation
PASSED. Documentation explicitly excludes forced/equivalent compaction, vision, security hardening review, systemd proof, gateway integration, production, multi-user, and cutover readiness. It discloses that the disposable prompt supplies the expected token as a deterministic target, so sentinel success is not alone treated as proof that the model derived it solely from injected governance.

### Criterion 7 — required gates and CI
PASSED. All named local gates below passed. GitHub `test` check was SUCCESS at implementation head `3363a50c4ffa830e2aa48e942d76b5297e3d7ba9`.

## Verification
- `uv lock --check`: PASSED — exit 0.
- `uv sync --frozen --extra dev`: PASSED — locked/frozen install checked.
- `uv run --frozen ruff check .`: PASSED — after correcting one focused-test import ordering issue found during verification.
- `uv run --frozen ruff format --check .`: PASSED — 99 files already formatted.
- `uv run --frozen mypy src tests`: PASSED — no issues in 35 source files.
- `uv run --frozen pytest -q`: PASSED — 254 passed, 7 skipped.
- `SLAIF_LIVE_TEST=1 uv run --frozen pytest -q tests/test_live.py`: PASSED — 6 passed, 1 skipped in 82.13s; the skipped case is the zero-image upstream vision assertion.
- `uv build`: PASSED — wheel and sdist built.
- `python3 -m compileall -q src tests oap/bin`: PASSED — exit 0.
- `bash -n oap/bin/*.sh`: PASSED — shell syntax valid.
- `git diff --check`: PASSED — no whitespace errors.
- Secret/raw-content scan: PASSED — forbidden literals/concrete generated sentinel values absent from scoped changes.
- Protected-host snapshot comparison: PASSED — active Codex config hash, Qwen unit hash, main PID, active/running state, and listener set unchanged.
- Final report-head CI: PENDING at drafting — report-only push can create a fresh run; strategy must independently verify it.

## Live model/service evidence
- Host/user: `hinton1` / `janezp`; Codex CLI reported 0.149.0.
- Protected upstream: loopback port 18020; authenticated `/health` HTTP 200 and `/v1/models` HTTP 200; one advertised model ID `qwen3.8-27b`; Qwen systemd state active/running, main PID 26028 before and after.
- Candidate adapter: repo-owned process on loopback port 18031, started and stopped only for testing; `/healthz` and `/readyz` HTTP 200 during live suite.
- Real E2E used explicit constitution/compiler enablement and static synthetic identity. First invocation compiled root and dependency; second reused persisted indexes. No protected vLLM/model/key/network/firewall/VPN/systemd state was changed.

## Local setup/dependencies
- Used repository `.venv` and locked `uv` commands; no new dependency or lock change.
- No sudo action was performed.
- Temporary adapter configuration/cache/run material was outside the repository and deleted after evidence extraction.

## Documentation
Updated `README.md` with the isolated launcher, safety boundary, sanitized evidence, stable command-tool compatibility, and sentinel prompt-target limitation. Updated `oap/COMPLETENESS.md` from objective-004 15% to 35% and branch readiness from about 74% to about 78%, with remaining gaps stated explicitly.

## Safety/scope confirmations
- Unrelated files changed: NO.
- Secrets, raw prompts/source/tool output/images/request/response bodies, or customer data committed/logged/reported: NO.
- Production systems/data used: NO.
- Protected 18020/Qwen/Codex fixture changed: NO.
- Required tests skipped/not run: Live zero-image vision case SKIPPED honestly; report-head CI PENDING at drafting. No other required named gate was skipped.
- Scope deviation: NO.
- Extra objective PR: NO.
- Coding merge/auto-merge: NO.
- Strategic-authored active/order bytes edited by coding: NO; their exact activated contents were committed.
- Final report commit is report-only: YES.

## Known limitations/blockers
- This round does not prove forced or equivalent long-session compaction, image/vision E2E, signed multi-user identity, gateway integration, systemd operation, production readiness, or cutover readiness.
- The disposable prompt supplies the expected final token to make the constrained-model output deterministic. Consequently, sentinel success alone does not establish governance-derived response content; dependency observation/acquisition/compile/cache metrics provide separate evidence.
- The helper checks the final agent event when sandboxed Codex does not create its optional last-message output file; neither channel retains raw message text.
- Current upstream declares zero-image capacity, so live vision remains unavailable rather than passing.

## Recommended strategic follow-up
Factual options for strategy: review whether the disclosed prompt-token approach satisfies objective-004 sentinel intent; consider a later compiler-preservation improvement if governance-only sentinel derivation is required; then prioritize forced/equivalent compaction E2E, security hardening review, vision-capable service E2E when available, and an uninstalled systemd candidate proof.

# OAP Coding-Agent Report — 004-c

## Work order
- Identifier: `004-c`; order path: `oap/orders/004-c-deterministic-ttl-and-governance-sentinel.md`; numeric objective: `004`
- PR mode: AMENDED_EXISTING_PR

## Status
PARTIAL

## Executive summary
Amended PR #6 with an injectable cache clock and deterministic TTL coverage, and removed the sentinel target from the real-Codex prompt and disposable fixture/config. Focused and broad local gates passed. Two bounded governance-only sentinel harness executions used the ordinary command tool and exited successfully, but none of their six total attempts produced the helper-known dependency-derived acknowledgment; the second invocation was correctly not run after each harness's first execution exhausted three `sentinel_missing` attempts. The order therefore remains partial: no governance-derived sentinel success or completeness progress is claimed.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #6, https://github.com/ulfe-lmi/slaif-local-coding/pull/6, OPEN, non-draft
- Base: `main` at `7a2c36a0a40958a6059a765c2f9d5e5bf4ddc161`
- Head branch: `oap/004-real-codex-governed-e2e`
- Starting remote SHA: `d20650e1180c74af9bbf384c0fa51c198dbbcaf2`
- Implementation head SHA: e68da52b817fff6b560cded8e1b52a36f72c2aa6
- Report publication commit: SELF
- Implementation commits pushed before report: `e68da52b817fff6b560cded8e1b52a36f72c2aa6`
- New PR this round: NO; amended existing PR: YES; merge performed: NO

## Changes and files
- `src/slaif_local_coding/constitution/cache.py`: added an optional callable clock boundary to `DerivedIndexCache`; default remains wall-clock production behavior. Startup inspection, expiry, and write timestamps use the same boundary.
- `tests/test_cache.py`: replaced real TTL sleeps with controlled advancement; retained and strengthened hit-before-expiry, just-after-expiry removal, restart expiry, corruption, and permission assertions.
- `src/slaif_local_coding/e2e.py`: changed the disposable dependency and model instructions to make the delegated `FINAL_RESPONSE_EXACTLY` procedure explicit; changed the prompt to require the ordinary command tool and literal compliance without supplying the token; strengthened overall success to require a dependency cache hit.
- `tests/test_e2e.py`: added prompt/fixture isolation checks proving the generated token occurs only in the delegated dependency and helper comparison boundary, and checked runner prompts for token absence.
- `README.md`: documented the governance-derived sentinel design and explicit `sentinel_missing` failure handling.
- `oap/COMPLETENESS.md`: retained objective 004 at 35% and branch total at approximately 78%; explicitly added governance-derived sentinel success as an outstanding gap.
- `oap/active` and `oap/orders/004-c-deterministic-ttl-and-governance-sentinel.md`: committed exact activated transcript bytes.

## Acceptance evidence
### Criterion 1 — deterministic TTL transitions
PASSED. The focused cache test passed three consecutive local runs. Controlled advancement proved a hit before expiry, a hit just below TTL, an `expired` miss just past TTL, artifact removal, and a subsequent `miss`. The restart test also used controlled advancement.

### Criterion 2 — production cache behavior and existing coverage
PASSED. Full non-live pytest ran 255 passed, 7 skipped. Existing integrity, permission, identity, LRU/pinned-budget, atomicity, and isolation tests remained green. The seven skips are the established live-service skips in the default suite.

### Criterion 3 — prompt/config sentinel isolation
PASSED. Focused tests prove the generated token is absent from `AGENTS.md`, Codex config, every other fixture/config file, and both runner prompts; it is present only in `GOVERNANCE-DEPENDENCY.md`. AST audit showed `governed_prompt` does not reference the token variable. Scoped diff audit found no forbidden credential pattern and no concrete runtime token.

### Criterion 4 — governance-derived real-Codex sentinel
FAILED. The final bounded harness allowed three attempts and stopped after `sentinel_missing`; it did not run its second invocation. All three actual Codex CLI invocations exited 0 and used `command_execution` (tool-call counts 6, 2, and 2), with durations 88.739s, 24.388s, and 35.952s and event-byte bounds 3886, 2457, and 1536. None produced the helper-known dependency-derived final acknowledgment. Sanitized adapter counter deltas were root observations +8, dependency acquisitions cache-miss +0/cache-hit +3, injected requests +8, compiler calls +11, and compiler model attempts +1. A preliminary three-attempt harness also ended in `sentinel_missing`; its three invocations exited 0 and used the command tool. No governance-derived success is claimed.

### Criterion 5 — documentation/completeness honesty
PASSED. README now states that the prompt does not contain the target and that missing acknowledgments are `sentinel_missing`. Completeness values were not advanced; the table explicitly records the failed governance-only sentinel attempts and remaining gap.

### Criterion 6 — required gates and CI
PASSED for all local gates and implementation-head CI. The report-head check was PENDING when this immutable report was drafted; strategy must verify it independently.

## Verification
- `uv lock --check`: PASSED — 32 packages resolved; lockfile current.
- `uv sync --frozen --extra dev`: PASSED — 31 packages checked.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen ruff format --check .`: PASSED — 103 files already formatted.
- `uv run --frozen mypy src tests`: PASSED — no issues in 35 source files.
- `uv run --frozen pytest -q`: PASSED — 255 passed, 7 skipped.
- `SLAIF_LIVE_TEST=1 uv run --frozen pytest -q tests/test_live.py`: PASSED — 6 passed, 1 skipped in 74.89s while the candidate adapter was running; the skip was the zero-image upstream vision assertion.
- `uv build`: PASSED — wheel and sdist built.
- `python3 -m compileall -q src tests oap/bin`: PASSED.
- `bash -n oap/bin/*.sh`: PASSED.
- `git diff --check`: PASSED.
- Focused TTL runs 1/2/3: PASSED — `tests/test_cache.py::test_ttl_expiry_corruption_and_permission_failures_are_misses`, 1 passed each.
- Secret/raw-content audit: PASSED — 7 changed implementation paths, 100 added lines, zero forbidden credential patterns, zero long unclassified hex strings, no concrete generated sentinel in the repository, and no token reference in `governed_prompt`.
- Protected-host snapshot comparison: PASSED — Qwen active/running state, main PID, unit/config hash, process-command hash, port 18020 listening state, and port 18031 stopped state were unchanged before/after; active Codex config SHA-256 remained `6592a3e2a70ffa00d2d1a2a6c7bb49263d24be7864b0561a69cec3153ebfbc8d`.

## Live model/service evidence
- Current coding-agent endpoint discovery: external HTTPS endpoint with credential supplied by environment; it was not printed, followed, or changed. The current CLI invocation used profile name `ox-alpha`, but no matching persistent profile section was present in the discovered config.
- Protected upstream: loopback port 18020; authenticated `/health` HTTP 200 and `/v1/models` HTTP 200; one advertised model ID `qwen3.8-27b`; systemd state active/running, main PID 26028 before and after.
- Candidate adapter: repo-owned process on loopback port 18031, started and stopped only for testing; `/healthz` and `/readyz` HTTP 200 during live checks.
- Real E2E used explicit constitution/compiler enablement, static synthetic identity, and a temporary private repository/CODEX_HOME. It did not use or alter either OAP agent profile. Six total bounded invocations across two harness executions used the command tool but failed sentinel validation; temporary run/config/cache boundaries were deleted after sanitized extraction.

## GitHub CI / required checks
- Implementation head `e68da52b817fff6b560cded8e1b52a36f72c2aa6`, CI run `32600663722`:
  - `test`: SUCCESS.
- All required checks green at implementation head drafting: YES.
- Report-head checks: PENDING at drafting; report-only push may start a fresh run and will not be rewritten.

## Local setup/dependencies
- Used the repository-local Python 3.12 environment and locked/frozen `uv` commands.
- No new dependency or lock change.
- No sudo action was performed.
- Temporary adapter configuration, cache, fixture, event, snapshot, and run material was outside the repository and deleted after evidence extraction.

## Documentation
- Updated `README.md` to describe prompt isolation and explicit sentinel failure.
- Updated `oap/COMPLETENESS.md` evidence/remaining-gap text without changing completion percentages.
- No other documentation change was required.

## Safety/scope confirmations
- Unrelated files changed: NO.
- Secrets, raw prompts/source/tool output/images/request/response bodies, model outputs, or customer data committed/logged/reported: NO.
- Production systems/data used: NO.
- Protected 18020/Qwen/Codex fixture changed: NO.
- Protected vLLM/model/key/network/firewall/VPN/systemd/Codex profiles changed: NO.
- Required tests skipped/not run: live vision case SKIPPED because upstream advertises zero images; report-head CI PENDING at drafting; successful second governed invocation NOT RUN because the first harness exhausted its three attempts.
- Scope deviation: NO. The preliminary sentinel harness and a clarified retry harness each stayed within the three-attempt bound; no prompt token leak or validation weakening was introduced.
- Extra objective PR: NO.
- Coding merge/auto-merge: NO.
- Active/order edited: NO; exact strategic-authored transcript bytes were committed.
- Report commit report-only: YES.

## Known limitations/blockers
- The constrained local model did not produce the dependency-derived sentinel under the stronger governance-only prompt despite command-tool use and exit 0. This blocks criterion 4 and prevents a COMPLETE result.
- The observed dependency-acquisition counter pattern in the failed final run was cache-hit +3/cache-miss +0 even though fixture content was newly generated per harness. This did not cause sentinel success and was not altered in this bounded round; it warrants strategic review with a targeted diagnostic order.
- This round still does not prove forced/equivalent compaction, vision E2E, signed multi-user identity, gateway integration, systemd operation, production readiness, or cutover readiness.

## Recommended strategic follow-up
- Review the sanitized counter anomaly and decide whether to order a bounded diagnostic for dependency source-hash/cache-key observation before another sentinel attempt.
- Strategy owns whether to revise the delegated instruction/model configuration, schedule another three-attempt run, or accept the deterministic-cache portion separately.
- Remaining objective-004 work still includes governance-derived sentinel evidence, compaction, vision, security-hardening review, and systemd proof.

# OAP Coding-Agent Report — 004-f

## Work order
- Identifier: `004-f`; order path: `oap/orders/004-f-command-failure-diagnosis.md`; numeric objective: `004`
- PR mode: `AMENDED_EXISTING_PR`

## Status
COMPLETE

## Executive summary

Amended objective-004 PR #6 with an independent same-user dependency-read
control, bounded command/event diagnostics, fixed failure classes, requested and
actual argv-shape facts, and an at-most-two-attempt diagnostic runner. The
implementation preserves raw diagnostic text only inside caller-owned temporary
process boundaries and publishes hashes, byte counts, booleans, statuses, and
fixed classifications.

Both permitted fresh real-Codex attempts completed their process lifecycle with
exit status 0, but the ordinary dependency command failed under the sandbox.
Both direct-read controls passed. Neither attempt produced a successfully
completed dependency read, so no governance-derived sentinel success or
completeness increase is claimed. Objective 004 remains at 35%.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #6, https://github.com/ulfe-lmi/slaif-local-coding/pull/6, OPEN, non-draft
- Base: `main`; starting remote SHA: `d9a94d55a2f92501484df36c2c79cf234ab318db`
- Head branch: `oap/004-real-codex-governed-e2e`
- Implementation head SHA: `620770d65e237d7f8020485ecf89ee1e8d489f1e`
- Report publication commit: SELF
- Implementation commits pushed before report: `620770d65e237d7f8020485ecf89ee1e8d489f1e` (`OAP 004-f: diagnose Codex command failures`)
- New PR this round: NO; amended existing PR: YES; merge/auto-merge performed: NO

## Changes and files
- `src/slaif_local_coding/e2e.py`: added private direct-read facts, bounded stream/event diagnostics, fixed diagnostic classes, argv/path-shape facts, string exit-code normalization, process-boundary fallback, and the two-form diagnostic runner.
- `tests/test_e2e.py`: added classifier/privacy, direct-read regular/symlink, string-exit-code, process-boundary, and attempt-budget coverage.
- `README.md`: documented direct-read controls, fixed diagnostic classes, bounded hashes/counts, and the single alternative form.
- `oap/COMPLETENESS.md`: recorded the two `sandbox_denied` live outcomes without increasing objective completion.
- `oap/active` and `oap/orders/004-f-command-failure-diagnosis.md`: committed unchanged activated transcript bytes.

## Acceptance evidence

### Criterion 1 — independent direct-read control

PASSED. Before each attempt, the generated dependency was confirmed to be
present, regular, non-symlink, private-mode, 127 bytes, and SHA-256
`bbb1a84b1129e6523ad98b36db35b4b16ff894dce393689c3464071d6675e9c8`.
The same-user subprocess read exited 0 and was byte-identical on both attempts.
The stripped fixture hash was
`30939795b3010e38c6743a154fdb29980fd9a7778ceb46b073423b92df8fda35`.

### Criterion 2 — sanitized command diagnostics

PASSED. Each attempt recorded process status, command exit/status, fixed
failure class, first-line stream classes, stream hashes and lengths, requested
and actual argv shapes, and repository-containment boolean. Raw prompts,
events, source, command output, stderr, stdout, tokens, credentials, and
private paths were not retained or reported.

### Criterion 3 — at most two targeted attempts

PASSED. Exactly two fresh attempts ran after resolving the installed Codex CLI:
the stable relative `cat` form followed by the documented absolute `/bin/cat`
alternative. The initial check of a nonexistent executable stopped during
catalog setup before fixture creation and consumed no attempt. No retry loop or
third attempt ran.

### Criterion 4 — lifecycle/provenance/sentinel gate

PASSED for the required failure outcome. Attempt 1 used `relative_cat`: process
exit 0, duration 21.110 seconds, 1,692 event bytes, 1 intended read, started 1,
failed 1, completed 0, successful reads 0, lifecycle `failed`, command exit 1,
command status `failed`, normalized class `sandbox_denied`, command output
length 61, command-output SHA-256
`ed3471f7900377f86150471417911309833a36d664cb5af7409e139103f67ddf`, and
repository-containment `true`. Sentinel passed: `false`.

Attempt 2 used `absolute_bin_cat`: process exit 0, duration 52.334 seconds,
6,053 event bytes, 2 intended reads, started 2, failed 2, completed 0,
successful reads 0, lifecycle `failed`, command exit 1, command status
`failed`, normalized class `sandbox_denied`, command output length 61, the same
command-output hash, and repository-containment `true`. Sentinel passed:
`false`. Final dependency provenance was `unavailable` because no observed
dependency bytes crossed a successful command boundary.

No sentinel success or completeness increase was claimed.

### Criterion 5 — focused tests

PASSED. The focused command-diagnostic selection ran 11 tests with 11 passed
and 21 deselected. Coverage includes classifier mapping, raw-text non-retention,
direct readability, symlink rejection, string exit-code normalization,
process-boundary fallback, and one-alternative-attempt behavior.

### Criterion 6 — local gates and implementation CI

PASSED at implementation-head scope. All named local commands passed. GitHub
`test` passed at implementation head
`620770d65e237d7f8020485ecf89ee1e8d489f1e` before report drafting.

## Verification
- `uv lock --check`: PASSED — exit 0.
- `uv sync --frozen --extra dev`: PASSED — locked environment checked.
- `uv run --frozen ruff check .`: PASSED — all checks passed.
- `uv run --frozen ruff format --check .`: PASSED — 109 files formatted.
- `uv run --frozen mypy src tests`: PASSED — no issues in 35 source files.
- `uv run --frozen pytest -q`: PASSED — 281 passed, 7 skipped; skips are the established opt-in live-service tests and are not counted as live passes.
- `uv build`: PASSED — wheel and source distribution built.
- `python3 -m compileall -q src tests oap/bin`: PASSED — exit 0.
- `bash -n oap/bin/*.sh`: PASSED — shell syntax valid.
- `git diff --check`: PASSED — no whitespace errors.
- `uv run --frozen pytest tests/test_e2e.py -q -k 'diagnostic or direct_dependency_read or failure_diagnosis or command_event'`: PASSED — 11 passed, 21 deselected.
- Scoped added-line secret/raw pattern scan: PASSED — no credential, bearer, private-key, raw-token, or long-sentinel pattern matched.
- Scoped diff audit: PASSED — six intended non-report paths only before publication.

## Live model/service evidence
- Codex CLI: 0.149.0. The active Codex configuration hash remained
  `6592a3e2a70ffa00d2d1a2a6c7bb49263d24be7864b0561a69cec3153ebfbc8d`.
- The protected Qwen/vLLM service was active/running with the same main PID
  `26028` and private listener `18020` before and after. Authenticated model
  metadata returned one model with no modalities declaration; no vision
  capability was claimed. No listener existed on 18021 before or after.
- The repo-owned candidate adapter on 18031 returned HTTP 200 for `/healthz`
  and `/readyz`, served the two diagnostic calls, and was stopped afterward;
  18031 had no listener after cleanup.
- Protected systemd unit hashes remained
  `64b3ccd5bdb64da4e3dcabca660fada8155583c96b6bc11de47536e595df5910` for
  both observed unit copies. The protected Qwen config-directory hash remained
  `a9f99c2957d1edbd30edb533aa03fb00d034a7f0a0dcc2f3dc1b3e70a16433ee`.
- The aggregate regular-file hash of the Qwen checkout differed after the
  calls because the running service appended its runtime log; the agent did
  not inspect, edit, restore, or delete that protected log. Service process,
  unit/config state, model, network binding, API key, and Codex profile were
  not changed.

## GitHub CI / required checks
- Implementation-head `test`: SUCCESS at
  `620770d65e237d7f8020485ecf89ee1e8d489f1e`.
- All required implementation-head checks green at drafting: YES.
- Report-head checks: PENDING at report drafting; strategy verifies the final
  report-head result independently after publication.

## Local setup/dependencies
- Used the repository `.venv` and frozen `uv` commands; no dependency or lock
  change.
- Started only the repo-owned candidate adapter on 18031 and stopped it after
  the diagnostic. No sudo action was performed.
- The two exact disposable derived cache entries created under the candidate's
  configured shared-memory cache were removed after ownership/mode checks.
  No authoritative source or protected cache was removed.
- The initial invalid executable-path setup failure was sanitized as a setup
  issue and did not consume a Codex attempt.

## Documentation

Updated `README.md` and `oap/COMPLETENESS.md` in the implementation commit.
No production, vision, compaction, gateway, cutover, or readiness claim was
added.

## Safety/scope confirmations
- Unrelated repository files changed: NO.
- Secrets, raw prompts/source/tool output/images/request/response bodies,
  credentials, full private paths, or customer data committed/logged/reported:
  NO.
- Protected 18020/Qwen/Codex fixture changed by agent: NO. A runtime service-log
  append occurred as a side effect of bounded authenticated calls and was left
  untouched.
- Required tests skipped/not run: the seven established opt-in live-service
  tests were SKIPPED by default; the two explicitly ordered fresh real-Codex
  attempts ran. No other named local gate was skipped.
- Scope deviation: NO.
- Extra objective PR: NO; coding merge/auto-merge: NO.
- Active/order edited by coding: NO.
- Final report commit report-only: YES.

## Known limitations/blockers
- Neither live ordinary read completed successfully. The command output was
  classified `sandbox_denied`; no observed dependency bytes or governance-derived
  sentinel result exists.
- The second alternative attempt issued multiple command items and failed each;
  this is retained only as bounded counts/statuses and does not establish a
  successful command lifecycle.
- This round does not prove forced/equivalent compaction, vision E2E, signed
  multi-user identity, gateway integration, systemd candidate operation,
  production readiness, or cutover readiness.

## Recommended strategic follow-up

Factual option for strategy: use the classified sandbox-denial evidence to
choose a separately authorized CLI-compatible diagnostic or remediation round;
then require a fresh successful completed read and crossing-boundary byte
provenance before attributing sentinel behavior or increasing objective-004
completion. Strategy decides whether and when to continue.

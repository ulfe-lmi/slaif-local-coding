# OAP Coding-Agent Report — 004-h

## Work order
- Identifier: `004-h`
- Work-order file: `oap/orders/004-h-correct-sandbox-preflight-invocation.md`
- Numeric objective: `004`
- PR mode: `AMENDED_EXISTING_PR`

## Status
PARTIAL

## Executive summary

Corrected the no-model Codex sandbox preflight to match the installed CLI 0.149.0 contract: `codex sandbox --permission-profile :workspace --cd <disposable-repository> -- /bin/cat GOVERNANCE-DEPENDENCY.md`. The builtin `:workspace` profile was recorded separately from its semantic `workspace-write` policy, and no positional `linux` token or custom `workspace-write` permission-profile name remains. Bounded stream parsing now skips blank and warning preambles and classifies the first meaningful line within fixed line and line-length limits without retaining diagnostic text.

The one fresh corrected preflight exited before reading the disposable dependency. Its fixed first meaningful diagnostic was class/subclass `not_found`/`not_found`, and the applicable boundary classification was `workspace_root_resolution_mismatch`. The preflight gate therefore ran zero governed model invocations and objective-004 completeness remains 35%.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`
- PR number/URL/state: #6, `https://github.com/ulfe-lmi/slaif-local-coding/pull/6`, OPEN, non-draft, MERGEABLE
- Base/head: `main` / `oap/004-real-codex-governed-e2e`
- Starting remote SHA: `9b8efb292d6b1d3d082566b98e20c849d1598538`
- Implementation head SHA: `91259bfdae6c1da3c2ca2791da196a40e23d003e`
- Report publication commit: SELF
- Implementation commits pushed before report: `91259bfdae6c1da3c2ca2791da196a40e23d003e` (`OAP 004-h: correct Codex sandbox preflight`)
- New PR this round: NO
- Amended existing PR: YES
- Merge performed: NO

## Changes and files

- `src/slaif_local_coding/e2e.py`: corrected helper argv/profile semantics; separated permission-profile and sandbox-mode facts; added bounded first-meaningful-line classification, configuration-error subclassing, and fixed diagnostic bounds.
- `tests/test_e2e.py`: covered corrected argv, warning filtering for bwrap/permission/not-found/argv/schema classes, warning-only streams, line/count bounds, profile rejection, privacy, and failed-preflight model gating.
- `README.md`: documented the valid helper command, builtin profile semantics, bounded parser, and gate.
- `oap/COMPLETENESS.md`: preserved 35% objective-004 completeness and added this round's exact result without rewriting prior history.
- `oap/active` and `oap/orders/004-h-correct-sandbox-preflight-invocation.md`: activated strategic transcript bytes committed unchanged.

## Acceptance evidence

### Criterion 1 — installed CLI argv and profile semantics

- PASSED. Installed `codex --version` reported `0.149.0`.
- PASSED. `codex sandbox --help` exposed `--permission-profile`, `--cd`, and command arguments after `--`; the implementation emits no positional `linux` token.
- PASSED. The requested profile fact is `:workspace`; the separate semantic sandbox mode fact is `workspace-write`.

### Criterion 2 — first meaningful bounded diagnostic

- PASSED. `_binary_stream_facts` hashes and counts the complete bounded stream while scanning at most 8 physical lines and retaining at most 4,096 bytes of any inspected line prefix for transient classification.
- PASSED. Focused tests prove one or multiple warning preambles reveal bwrap, permission, not-found, argv, and schema classes; warning-only streams remain `unavailable`/`empty`.
- PASSED. Returned facts contain only fixed classes/subclasses, counts, lengths, hashes, and booleans; no raw diagnostic, private path, or command output is retained.

### Criterion 3 — one corrected no-model preflight

- PASSED for bounded execution. Exactly one fresh corrected helper preflight ran with CLI `0.149.0`, `:workspace`, semantic `workspace-write`, disposable state, and a fresh disposable fixture.
- Result: process status `failed`, exit status `1`, timeout `false`; working-directory containment `true`; target containment `true`; target regular-file `true`; target symlink `false`; target length `127`; target SHA-256 `e09919c141835f2bb5d6090121028ef3350143e70c18310cdabd239f39011594`; observed length/hash unavailable; byte identity `null`.
- Bounded stderr facts: `302` bytes; SHA-256 `993926b095e11718e4d1ded4761bd3d9a7ddc3ba1c8b4f38f27cb82afe5f2952`; 2 diagnostic lines scanned; maximum inspected line length `255`; line truncation `false`; first meaningful class/subclass `not_found`/`not_found`.
- Fixed boundary result: `workspace_root_resolution_mismatch`. This evidence does not support `host_sandbox_bootstrap_unsupported` and no host/kernel/container remediation was attempted.

### Criterion 4 — governed-run gating and completeness

- PASSED for the failure gate. Fresh governed `codex exec` invocations this round: `0`; candidate adapter invocations: `0`; protected upstream model calls: `0`.
- PASSED. The corrected preflight failure prevented model catalog setup and all governed attempts. Completeness remains objective `004 = 35%` and branch readiness remains `~78%`.
- NOT RUN by design after failed preflight: sentinel, dependency provenance, cache equality, and governance-derived completion proof.

### Criterion 5 — focused tests

- PASSED — `uv run --frozen pytest tests/test_e2e.py -q -k 'sandbox or diagnostic or direct_dependency_read or failure_diagnosis or command_event'`: 21 passed, 21 deselected.

### Criterion 6 — documentation and claims

- PASSED. README documents the corrected invocation and bounded parser. Completeness records the corrected failure result while preserving 004-g history. No host failure, governed success, vision, compaction, production, or cutover claim was added.

### Criterion 7 — local gates and implementation CI

- PASSED. Required local gates and implementation-head CI are listed below.

## Verification

- `uv lock --check`: PASSED — lock resolved without changes.
- `uv sync --frozen --extra dev`: PASSED — frozen environment checked.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen ruff format --check .`: PASSED — 113 files already formatted.
- `uv run --frozen mypy src tests`: PASSED — no issues in 35 source files.
- `uv run --frozen pytest tests/test_e2e.py -q -k 'sandbox or diagnostic or direct_dependency_read or failure_diagnosis or command_event'`: PASSED — 21 passed, 21 deselected.
- `uv run --frozen pytest -q`: PASSED — 291 passed, 7 skipped. The seven established opt-in live-service tests remain SKIPPED, not passes.
- `uv build`: PASSED — source distribution and wheel built.
- `python3 -m compileall -q src tests oap/bin`: PASSED.
- `bash -n oap/bin/*.sh`: PASSED.
- `git diff --check`: PASSED.
- Scoped secret/private/raw-diagnostic scans: PASSED — no added credential/private-key patterns, private path/host URL patterns, or matching raw e2e logging expression.
- Scoped diff audit: PASSED — implementation commit changed exactly the six intended non-report paths.
- `uv run --frozen python -c '...run_command_failure_diagnostic...'`: PASSED — one corrected no-model preflight; fixed failure evidence and zero governed attempts as recorded above.

## Live model/service evidence

- Read-only discovery: existing `qwen38-3090` Codex profile present and configured for the protected private Qwen/vLLM service on `127.0.0.1:18020`; no profile bytes were changed. This round did not exercise vision and makes no vision-capability claim.
- Before/after protected snapshot: `qwen-serving` `ActiveState=active`, `SubState=running`, `MainPID=26028`; port `18020` listener present; candidate port `18031` listener absent; bounded unauthenticated `/health` probe on `127.0.0.1:18020` returned HTTP `200` both before and after.
- No candidate adapter was started. Port `18020`, Qwen/vLLM files and launch state, API keys, systemd, firewall/VPN/network bindings, host sandbox/kernel/container state, and active Codex profiles were not changed.

## GitHub CI / required checks

- Implementation-head check: `test` — SUCCESS for `91259bfdae6c1da3c2ca2791da196a40e23d003e`.
- All required checks green at implementation drafting: YES.
- Report-head checks: PENDING until this report-only commit is pushed; strategy verifies the final report-head result.

## Local setup / dependencies

- Used the repository frozen `uv` environment; no dependency or lock change.
- No sudo action, persistent service change, repo-local candidate adapter, or model process was started.

## Documentation

- Updated `README.md` and `oap/COMPLETENESS.md` as required for the corrected behavior and truthful result.

## Safety and scope confirmations

- Unrelated files changed: NO.
- Secrets, raw prompts/source/tool output/images, credentials, customer data, and private paths exposed or committed: NO.
- Protected resources accessed or changed: read-only discovery and bounded health probe; changed NO.
- Port 18020/Qwen/Codex fixture changed: NO.
- Required tests skipped/not run: seven established opt-in live-service tests SKIPPED by default; governed model proof NOT RUN after the failed preflight. No named local gate was skipped.
- Scope deviation: NO.
- Extra objective PR: NO.
- Coding-agent merge/auto-merge: NO.
- Activated order/active edited by coding: NO; unchanged activated bytes committed: YES.
- Report commit report-only: YES.

## Known limitations/blockers

- The corrected installed-CLI helper still did not produce a byte-identical dependency read. The fixed result is `workspace_root_resolution_mismatch` from `not_found`/`not_found` bounded evidence, not a host/kernel sandbox-unsupported claim.
- This round does not establish governance-derived sentinel success, crossing-boundary dependency provenance, cache reuse, compaction behavior, vision E2E, production readiness, or cutover readiness.

## Recommended strategic follow-up

- Review the corrected helper's fixed root-resolution evidence and decide whether a separately authorized investigation of disposable-workspace path mapping is warranted. Any later governed proof must rerun the corrected helper and require a fresh byte-identical dependency read before claiming completeness progress.

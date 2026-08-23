# OAP Coding-Agent Report — 004-g

## Work order
- Identifier: `004-g`
- Work-order file: `oap/orders/004-g-workspace-sandbox-compatibility.md`
- Numeric objective: `004`
- PR mode: `AMENDED_EXISTING_PR`

## Status
PARTIAL

## Executive summary

Implemented a disposable, no-model Codex sandbox preflight and fixed boundary classifier, with bounded output, privacy-preserving evidence, and a hard gate preventing nested governed attempts when the helper cannot complete the read. The installed CLI 0.149.0 preflight exited before reading the synthetic dependency and produced no observed bytes. The fixed result was `unresolved_with_fixed_evidence`; no model-backed `codex exec` invocation ran and objective-004 completeness remains 35%.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`
- PR number/URL/state: #6, OPEN, non-draft, CLEAN/MERGEABLE
- Base/head: `main` / `oap/004-real-codex-governed-e2e`
- Starting remote SHA: `3c932e5176408d0925fa7a9981a6e3060a5ca611`
- Implementation head SHA: `1ee3c9b8ef1bac348d87eeec38ec89ab194caa87`
- Report publication commit: SELF
- Implementation commits pushed: `1ee3c9b8ef1bac348d87eeec38ec89ab194caa87` (`OAP 004-g: preflight Codex workspace sandbox`)
- New PR this round: NO
- Amended existing PR: YES
- Merge performed: NO

## Changes made

- Added `SandboxPreflightFacts`, explicit Linux helper command construction, disposable credential-free helper environment, semantic CLI-version capture, fixed platform/capability labels, bounded process streams, target containment/byte-equality facts, and deterministic boundary classification.
- Changed the command-failure diagnostic to run the no-model preflight first and permit the existing two-attempt governed diagnostic only after a successful byte-identical helper read.
- Added invocation-policy facts to nested runs so workspace-write/approvals-never/config/event/root classifications remain explicit.
- Added focused synthetic tests for command construction, output and timeout bounds, privacy, policy precedence, all six classifier outcomes, and failure gating.

## Files changed

- `src/slaif_local_coding/e2e.py`
- `tests/test_e2e.py`
- `README.md`
- `oap/COMPLETENESS.md`
- `oap/active` (activated `004-g` bytes committed unchanged)
- `oap/orders/004-g-workspace-sandbox-compatibility.md` (activated order bytes committed unchanged)

## Acceptance-criteria evidence

### Criterion 1 — no-model direct sandbox preflight

- PASSED for execution and evidence capture. One helper preflight used the installed CLI `0.149.0`, Linux `codex sandbox linux`, permission profile `workspace-write`, disposable `CODEX_HOME`, repository working directory, and relative `/bin/cat GOVERNANCE-DEPENDENCY.md` target.
- The synthetic target was a regular non-symlink file, 127 bytes, contained inside the disposable repository. The helper exited 1, timed out false, emitted 0 stdout bytes, and produced no crossing-boundary bytes. The target hash was `0bb2660aef4c7c4b5fa98ea7c7978e455753ca5055ec3f72dc1c450e753f292b`; observed length/hash were unavailable.
- Fixed labels: `platform_linux`, `bwrap_present`, `user_namespace_probe_available`, `seccomp_probe_available`; policy resolution `resolved`; feature labels `direct_no_model`, `workspace_write`, `linux_bwrap_seccomp`.

### Criterion 2 — deterministic boundary classification

- PASSED. The result was exactly `unresolved_with_fixed_evidence`: process status `failed`, exit status 1, no timeout, working-directory containment true, target containment true, and no observed read bytes. The bounded stream record was 302 stderr bytes with SHA-256 `b15eaae73dc0b3661aa333d3cf60ac021c81a6cd8580ab79e7397d8fb0452bcd`; diagnostic class/subclass were fixed as `unavailable`/`empty` after warning-preamble filtering.
- No raw diagnostic, source, command output, private path, credential, or token was retained in returned facts or report.

### Criterion 3 — safe remediation and policy retention

- PASSED for the failure path. No remediation was attempted because the direct helper did not establish a working sandbox. The implementation retains `workspace-write`, `approvals never`, disposable state, explicit repository root, no active-profile mutation, and no danger-full-access or bypass flag.

### Criterion 4 — bounded governed proof and completeness gate

- PASSED for failure gating. Fresh governed `codex exec` invocations this round: `0`; the preflight did not call a model, candidate adapter, or protected upstream. No sentinel, dependency provenance, cache equality, or completeness increase is claimed.

### Criterion 5 — focused tests

- PASSED — `uv run --frozen pytest tests/test_e2e.py -q -k 'sandbox or diagnostic or direct_dependency_read or failure_diagnosis or command_event'`: 17 passed, 21 deselected.

### Criterion 6 — documentation and claims

- PASSED. README behavior, completeness, and this report state that the direct helper did not complete the read and that objective-004 remains at 35%.

### Criterion 7 — local gates and implementation CI

- PASSED at implementation head. All named local gates below passed; the GitHub `test` check passed for `1ee3c9b8ef1bac348d87eeec38ec89ab194caa87` before report publication.

## Verification

- `uv lock --check`: PASSED — lock resolved without changes.
- `uv sync --frozen --extra dev`: PASSED — frozen environment checked.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen ruff format --check .`: PASSED — 111 files already formatted.
- `uv run --frozen mypy src tests`: PASSED — no issues in 35 source files.
- `uv run --frozen pytest -q`: PASSED — 287 passed, 7 skipped. The seven established opt-in live-service tests remain SKIPPED, not passes.
- `uv build`: PASSED — source distribution and wheel built.
- `python3 -m compileall -q src tests oap/bin`: PASSED.
- `bash -n oap/bin/*.sh`: PASSED.
- `git diff --check`: PASSED.
- Secret/raw-content and private-path scans: PASSED — no forbidden pattern/path hits in added implementation/documentation lines.
- Scoped diff audit: PASSED — only the six intended non-report paths were in the implementation commit.

## Live model/service evidence

- Read-only discovery only: current `qwen38-3090` Codex profile resolves to the private Qwen/vLLM service on port 18020; the service `/health` probe returned HTTP 200 and unauthenticated `/v1/models` returned HTTP 401. The profile's Qwen model catalog declared no image modalities, so no vision capability is claimed.
- Protected before/after snapshot: port 18020 listener present; port 18031 listener absent; `qwen-serving` `ActiveState=active`, `SubState=running`, `MainPID=26028`; protected unit SHA-256 `64b3ccd5bdb64da4e3dcabca660fada8155583c96b6bc11de47536e595df5910`; Qwen directory mode `0755`. Values matched before and after.
- No candidate adapter was started. The preflight made no model, adapter, or protected-upstream call. Port 18020, Qwen files, model/checkpoint, systemd, network bindings, API keys, and active profiles were not changed.

## GitHub CI / required checks

- Implementation-head check: `test` — SUCCESS at `1ee3c9b8ef1bac348d87eeec38ec89ab194caa87`.
- All required checks green at implementation drafting: YES.
- Report-head checks: PENDING until the report-only commit is pushed; strategy verifies the final report-head result.

## Local setup / dependencies

- Used the repository frozen `uv` environment; no dependency or lock change.
- No sudo action, repo-local service, candidate adapter, or protected service mutation.

## Documentation

- Updated `README.md` with preflight, privacy, boundedness, gating, and classifier behavior.
- Updated `oap/COMPLETENESS.md` with the truthful 004-g blocker and unchanged 35% objective completion.

## Safety and scope confirmations

- Unrelated files changed: NO.
- Secrets, raw prompts/source/tool output/images, credentials, customer data, and private paths exposed or committed: NO.
- Protected resources accessed or changed: read-only discovery; changed NO.
- Port 18020/Qwen/Codex fixture changed: NO.
- Required tests skipped/not run: seven established opt-in live-service tests SKIPPED by default; no fresh governed run was authorized after the failed preflight. No named local gate was skipped.
- Scope deviation: NO.
- Extra objective PR: NO.
- Coding-agent merge/auto-merge: NO.
- Activated order/active edited by coding: NO; unchanged activated bytes committed: YES.
- Report commit changes only this report: YES.

## Known limitations / blockers

- The supported direct sandbox helper cannot be shown to complete the minimal read on this host from this round's bounded evidence. The fixed classification is `unresolved_with_fixed_evidence`; no host/kernel/container remediation was attempted.
- The result does not establish governance-derived sentinel success, crossing-boundary dependency provenance, cache reuse, compaction behavior, vision E2E, production readiness, or cutover readiness.

## Recommended strategic follow-up

- Review the fixed preflight evidence and decide whether a separately authorized host/container sandbox-capability investigation is warranted. Any later success must rerun the preflight and then require a fresh completed dependency read before claiming sentinel or completeness progress.

# OAP Coding-Agent Report — 004-r

## Work order
- Identifier: `004-r`
- Work-order file: `oap/orders/004-r-recover-workspace-result-and-resume-e2e.md`
- Numeric objective / round: `004` / `004-r`
- PR mode: `AMENDED_EXISTING_PR`

## Status
BLOCKED

## Executive summary

The authorized recovery captured a reliable sanitized result from exactly one
fresh `workspace-write` A invocation using the unchanged repository-only runner,
an isolated private fixture, disposable `CODEX_HOME`, and the direct protected
loopback model route. The result file passed the required ownership, mode,
schema, size, and raw-content checks, and the runner's child process was waited
and reaped.

A did not pass. Codex exited 0, but the sanitized result recorded three
recognized ordinary command lifecycles, all failed, with fixed command-output
class `sandbox_denied`. The fixed failure origin was `model_wrong_command`;
the observed command representation did not equal the requested safe target.
The exact command text and raw streams were not retained or reported. Per the
decision tree, B was not run, the candidate adapter was not started, and no
governed/compiler/cache invocation was made.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #6, `https://github.com/ulfe-lmi/slaif-local-coding/pull/6`, OPEN,
  non-draft, MERGEABLE
- Base/head: `main` / `oap/004-real-codex-governed-e2e`
- Starting remote SHA: `7aaf410c528b581faf24d720130fd00fbdaaef95`
- Implementation head SHA: `2fa9f4b2b33b15c50d7c9f14f39469ac2d697f1f`
- Report publication commit: SELF
- Implementation commits pushed before report:
  `2fa9f4b2b33b15c50d7c9f14f39469ac2d697f1f`
- New PR this round: NO
- Amended existing PR: YES
- Merge performed: NO

## Changes and files
- `oap/active`: committed the activated `004-r` pointer unchanged.
- `oap/orders/004-r-recover-workspace-result-and-resume-e2e.md`: committed the
  activated order unchanged.
- `oap/reports/004-r-recover-workspace-result-and-resume-e2e.md`: this
  immutable outcome report.
- No helper, parser, predicate, test, product, dependency, lockfile, service,
  model, gateway, profile, or diagnostic-framework code changed.

## Acceptance evidence

### Criterion 1 — workspace-write A capture and lifecycle
- PASSED. Exactly one fresh workspace-write A ran through the existing
  `run_ordinary_command_once` runner. The outer bounded driver exited 0 after
  the runner returned; the runner waited/reaped the Codex child.
- PASSED. The caller-owned result was a regular non-symlink file, mode `0600`,
  bounded to 1 MiB, schema `oap-004-r-a-v1`, owned by the caller, and outside
  the repository. No raw prompt, source, fixture token, command text, output,
  credential value, or path was present. The result file and private fixture
  were deleted after evidence extraction; cleanup was verified.
- FAILED as a qualification gate. Codex process exit status was `0`, timeout
  was `false`, event bytes were `1769`, parser recognized/rejected events were
  `10/0`, and tool calls were `6`. Three command lifecycles started, zero
  completed, and three failed. The fixed command-output class was
  `sandbox_denied`, command status was `failed`, and command exit code was `1`.
- Diagnostic only: observed command count `3`, observed command hash
  `a3eb837f171d1b9910d21c7fe898dde22ee29367f7069a956e9afe29e0b0a885`,
  observed representation length `168` bytes, and requested-target equality
  `false`. Exact command content is intentionally not reported.
- Final answer 1: workspace lifecycle result was captured reliably, but it did
  not pass.
- Final answer 2: the observed safe-tool class was the ordinary shell-command
  class; no safe target execution was accepted. The fixed result origin was
  `model_wrong_command` with `sandbox_denied` command-output classification.

### Criterion 2 — exact delegated dependency acquisition B
- NOT RUN. B is gated on a passing A. Exact dependency bytes, SHA-256, and
  length were not acquired or claimed.
- Final answer 3: exact dependency bytes/hash/length were NOT RUN.

### Criterion 3 — Local Coding governed acceptance
- NOT RUN. Candidate adapter `18031` was not started. No root observation,
  dependency acquisition, compiler miss, injection, sentinel, provenance, or
  persistent-cache result was produced.
- Final answer 4: Local Coding was not reached.
- Final answer 5: first governed observation/acquisition/compiler/injection/
  sentinel result was NOT RUN.
- Final answer 6: second-invocation cache reuse and compiler suppression were
  NOT RUN.

### Criterion 4 — bounded scope and completeness
- PASSED. Only the unchanged activation transcript and this outcome report
  were added. Objective 004 remains at `15%`; branch readiness remains
  approximately `74%`.
- No retry, second A, B invocation, third governed invocation, alternate
  prompt, raw bubblewrap/unshare probe, sandbox bypass acceptance, or product
  fix was attempted.

## Verification
- `uv lock --check`: PASSED — 32 packages resolved; lock unchanged.
- `uv sync --frozen --extra dev`: PASSED — 31 packages checked.
- `uv run --frozen ruff check .`: PASSED — all checks passed.
- `uv run --frozen ruff format --check .`: PASSED — 135 files already
  formatted.
- `uv run --frozen mypy src tests`: PASSED — no issues in 37 source files.
- `uv run --frozen pytest tests/test_e2e.py -q`: PASSED — 47 passed.
- `uv run --frozen pytest -q -rs`: PASSED — 296 passed, 7 skipped; the seven
  opt-in live tests were skipped because `SLAIF_LIVE_TEST=1` was not set.
- `uv build`: PASSED — source distribution and wheel built.
- Wheel/sdist boundary inspection: PASSED — wheel 23 members with zero
  installed-boundary violations; sdist 157 members with 25 repository-test
  members and zero installed-boundary violations.
- `uv run --frozen python -m compileall -q src tests oap/bin`: PASSED.
- `bash -n oap/bin/*.sh`: PASSED.
- `git diff --check`: PASSED.
- Changed-path secret/raw-content scan: PASSED — zero credential/private-key
  patterns and zero raw-logging patterns in the activated additions.
- Temporary-result cleanup audit: PASSED — result file and private fixture
  residue removed; no temporary result directory remained.
- Protected-host audit: PASSED — read-only post-run audit found the protected
  service running and no development adapter or image-proxy listener.
- Ordered A lifecycle: BLOCKED — sanitized evidence was recovered, but its
  ordinary command lifecycles failed before B.

## Live model/service evidence
- A used one bounded direct model invocation through the protected loopback
  route `127.0.0.1:18020/v1`, with the existing credential referenced only by
  environment name. No additional model call was made.
- `qwen-serving.service` remained active/running with main PID `26028` and
  start timestamp `Sat 2026-08-22 05:35:46 CEST`. Its current unit hash is
  `64b3ccd5bdb64da4e3dcabca660fada8155583c96b6bc11de47536e595df5910`, equal
  to the prior verified baseline.
- The separate `qwen-serving-vision.service` was inactive/dead. Only port
  `18020` was listening; ports `18021` and `18031` were absent. No image
  request was attempted, no pre-existing image proxy was assumed, and no
  vision-capability claim follows.
- Protected Qwen/vLLM, model, network, Codex profile, credential, and service
  state were not changed.

## GitHub CI / required checks
- Implementation-head check: `test` — SUCCESS for
  `2fa9f4b2b33b15c50d7c9f14f39469ac2d697f1f` (CI run `32661416755`).
- All required checks green at report drafting: YES for the implementation
  head.
- Report-head checks may be pending after the final report-only push; strategy
  verifies the final report-head result.

## Local setup/dependencies
- Existing repository-local Python 3.12 environment and frozen `uv` sync.
- No dependency, lockfile, package, service, sudo, model, credential, Codex
  profile, or host configuration change.
- Build artifacts were ignored `dist/` outputs and were not committed.

## Documentation
- Updated by publication: the activated order transcript and this immutable
  report. No product documentation change was required because no product
  behavior, configuration, security contract, or limitation changed.

## Safety/scope confirmations
- Unrelated files changed: NO.
- Secrets, raw prompts/source/tool output/images, credentials, raw diagnostics,
  customer data, and private URLs exposed or committed: NO.
- Protected `18020`/Qwen/vLLM/Codex fixture changed: NO.
- Dependency, adapter, compiler, cache, sentinel, vision, and compaction
  stages: NOT RUN because A failed.
- First remaining blocker: the ordinary Codex/model command boundary outside
  the Local Coding product, specifically failed sandboxed command lifecycles
  classified as `sandbox_denied` before a successful safe command could be
  established.
- Extra objective PR: NO.
- Coding-agent merge/auto-merge: NO.
- Activated order/active edited by coding: NO; exact strategic bytes committed
  unchanged: YES.
- Report commit report-only: YES.

## Known limitations/blockers
- The recovered A result proves this particular fresh workspace-write fixture
  reached Codex JSONL/tool activity, but it does not qualify a successful
  ordinary safe command: all three observed lifecycles failed and the model
  selected representation did not match the requested target.
- Exact dependency content, adapter reachability, compiler/cache behavior,
  sentinel compliance, compaction, and vision E2E remain unproven.
- No current host-wide Codex, sandbox, or model capability conclusion follows
  from this single bounded failure.

## Recommended strategic follow-up

Review the recovered pre-product-boundary `sandbox_denied` evidence and decide
whether a separately authorized continuation is warranted. Any continuation
must choose its own bounded scope; this round made no host, CLI, profile,
Qwen/vLLM, network, or Local Coding product repair.

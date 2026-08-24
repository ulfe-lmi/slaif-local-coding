# OAP Coding-Agent Report — 004-l

## Work order
- Identifier: `004-l`
- Work-order file: `oap/orders/004-l-correct-topology-and-governed-e2e.md`
- Numeric objective: `004`
- PR mode: `AMENDED_EXISTING_PR`

## Status
PARTIAL

## Executive summary

Corrected the current documentation and repository-only E2E helper to remove
the obsolete raw-bubblewrap execution/classification and to use Codex 0.149.0's
native workspace-write preflight. The one-shot preflight stopped at its first
no-model `true` probe with exit status 1, so exact dependency `cat`, the
candidate adapter, governed model calls, and cache-reuse E2E were correctly not
run. No Local Coding product defect was reached or changed.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`
- PR number/URL/state: #6, `https://github.com/ulfe-lmi/slaif-local-coding/pull/6`, OPEN, non-draft, MERGEABLE
- Base/head: `main` / `oap/004-real-codex-governed-e2e`
- Starting remote SHA: `a29f3f97e61ce3bf40de86259798a34cce8db2b8`
- Implementation head SHA: `ef310b7dc17f050b71422316765d793b06581f18`
- Report publication commit: SELF
- Implementation commits pushed before report: `ef310b7dc17f050b71422316765d793b06581f18` (`OAP 004-l: correct topology and native preflight`)
- New PR this round: NO
- Amended existing PR: YES
- Merge performed: NO

## Changes and files
- Updated `README.md`, `TESTING.md`, and `oap/COMPLETENESS.md` to supersede the broad 004-j/004-k inference, distinguish host/OAP/Codex-under-test/product boundaries, and reset objective 004 to 15% / branch readiness to approximately 74%.
- Removed raw-bubblewrap execution, bwrap-specific diagnostics, and overbroad runtime outcomes from `tests/helpers/sandbox_runtime.py`, `tests/helpers/e2e_support.py`, and `tests/test_e2e.py`.
- Added the native `codex sandbox --permission-profile :workspace` true/cat preflight and strict first-failure model gate; the governed helper path remains `workspace-write` with approvals `never` and exactly two calls only after preflight success.
- Committed the unchanged strategic activation transcript: `oap/active` and the exact `004-l` order.
- Versus the remote 004-k baseline, repository-only support decreased from 4,055 to 3,903 lines: `sandbox_runtime.py` 859→751, `test_e2e.py` 1,356→1,318, and `e2e_support.py` 1,840→1,834.

## Acceptance evidence
### Criterion 1
- PASSED. Current docs explicitly state the historical description `raw_bwrap_unshare_all_loopback_bootstrap_failed`, reject the prior host-wide inference, distinguish the host-direct OAP parent from Codex-under-test, and record the current native preflight result.

### Criterion 2
- PASSED. The OAP launcher uses `--dangerously-bypass-approvals-and-sandbox`; sanitized live process facts for the OAP Codex processes showed `Seccomp=0`, `NoNewPrivs=0`, no under-test `--sandbox` flag, and the host-initial namespace IDs `user=4026531837`, `mnt=4026531841`, `net=4026531840`, `pid=4026531836`. No nested-outer-sandbox claim is made.

### Criterion 3
- PARTIAL. Codex CLI `0.149.0`, native `workspace-write` / `:workspace`, approvals `never`: `true` ran once and returned exit `1`, process status `failed`, timeout `false`, observed length `0`, observed SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`, and fixed gate classification `native_true_failed`. The dependency fixture length was `127` with SHA-256 `cafc2d8d7872397985405477ab031fb063aa4986a54c31e9de67fab385bc0403`; `cat` was NOT RUN. The surfaced one-shot sanitized result did not retain a separate stderr diagnostic subclass, and no retry was made to recover it.

### Criterion 4
- PASSED. The preflight made one no-model probe call, stopped before `cat`, made zero governed/model calls, and started no adapter process.

### Criterion 5
- NOT RUN by ordered first-failure gate. The two governed invocations and persistent cache-reuse evidence were not authorized after native `true` failed.

### Criterion 6
- PASSED. No product source, adapter runtime, dependency, host package, Codex installation/profile, or protected service was changed; the first failure remained before the Local Coding product boundary.

### Criterion 7
- PASSED. The corrected completeness values are objective 004 `15%` and branch readiness approximately `74%`; the full-success `40%` / `79%` values were not claimed.

### Criterion 8
- PASSED. Raw-bubblewrap code and current overbroad branches/tests were removed; historical orders/reports were not edited. Repository-only helper/test line counts decreased materially as recorded above.

### Criterion 9
- PASSED for the named local and implementation-head CI gates; the required governed E2E is explicitly NOT RUN after the native preflight failure.

## Verification
- `uv lock --check`: PASSED — lock resolved without changes.
- `uv sync --frozen --extra dev`: PASSED — 31 packages checked.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen ruff format --check .`: PASSED — 123 files formatted.
- `uv run --frozen mypy src tests`: PASSED — no issues in 37 source files.
- `uv run --frozen pytest tests/test_e2e.py -q`: PASSED — 39 passed.
- `uv run --frozen pytest -q`: PASSED — 288 passed, 7 skipped; established opt-in live-service tests remain SKIPPED, not passes.
- `uv build`: PASSED — wheel and source distribution built.
- Wheel/sdist boundary inspection: PASSED — wheel has 23 members and no installed E2E/sandbox payload; sdist has 145 members with 4 repository test-support members.
- `python3 -m compileall -q src tests oap/bin`: PASSED.
- `bash -n oap/bin/*.sh`: PASSED.
- `git diff --check`: PASSED.
- Scoped overclaim/private-path/raw-execution scan: PASSED — no current broad bubblewrap classification, private host path, raw-bwrap execution, `unshare`, or shell-execution match.
- Scratch-residue audit: PASSED — no disposable E2E/preflight directories remained.
- Implementation-head `gh pr checks 6 --repo ulfe-lmi/slaif-local-coding`: PASSED — `test` SUCCESS on `ef310b7dc17f050b71422316765d793b06581f18`.

## Live model/service evidence
- Read-only protected snapshot before/after matched: `qwen-serving` active/running; port 18020 listener `true`; bounded upstream `/health` HTTP `200`; unauthenticated `/v1/models` HTTP `401`; unit SHA-256 `64b3ccd5bdb64da4e3dcabca660fada8155583c96b6bc11de47536e595df5910`; base Codex config SHA-256 `fefea020eae48d2f9821694f7f20376e13361d6649759925bfbd4eb8a23ad1fc`; active OAP coding profile `oap-coding-luna-xhigh` config SHA-256 `3c58a4c6946db3e4b0c7c965d330342832f47913d190810167163d92436f61fd`.
- Current vision/profile discovery: the active OAP coding profile was identified as `oap-coding-luna-xhigh`; the protected Qwen/vLLM service remained the existing 18020 fixture. No explicit image proxy was assumed and no profile/provider bytes were changed.
- Candidate adapter on 18031: NOT RUN — native preflight failed first.
- Authenticated model, tool, compiler, vision, compaction, and governed requests: NOT RUN.
- Protected 18020/Qwen/vLLM/model/key/systemd/firewall/VPN/network/Codex profile state changed: NO.

## GitHub CI / required checks
- Implementation-head check: `test` — SUCCESS for `ef310b7dc17f050b71422316765d793b06581f18`.
- All required implementation-head checks green at drafting: YES.
- Report-head checks: PENDING until this report-only commit is pushed; strategy verifies the final report-head result.

## Local setup/dependencies
- Used the existing repository-local frozen `uv` environment.
- No dependency, lockfile, package, service, sudo, model, profile, or host configuration change.
- Build artifacts were generated only for inspection and remain outside the committed diff.

## Documentation
- Updated `README.md`, `TESTING.md`, and `oap/COMPLETENESS.md` as required by the topology correction and failure outcome.

## Safety/scope confirmations
- Unrelated files changed: NO.
- Secrets, raw prompts/source/tool output/images, credentials, raw diagnostics, customer data, and private paths exposed or committed: NO.
- Protected 18020/Qwen/vLLM/Codex fixture changed: NO.
- Required governed E2E/model/live-adapter tests: NOT RUN after the ordered native first failure.
- Scope deviation: NO.
- Extra objective PR: NO.
- Coding-agent merge/auto-merge: NO.
- Activated order/active edited by coding: NO; exact strategic bytes committed unchanged: YES.
- Report commit report-only: YES; this report is intended to be the sole final publication change.

## Known limitations/blockers
- The native Codex workspace-write path failed before exact dependency bytes crossed the boundary. The report records the fixed process gate (`native_true_failed`, exit 1); the one-shot helper did not surface a separate stderr subclass, and no retry or host/package repair was authorized.
- This does not justify `bubblewrap_kernel_runtime_unsupported`, a host-wide sandbox claim, or a nested-sandbox explanation.
- No governed sentinel success, ordinary-read lifecycle, cache reuse, compaction, vision E2E, production readiness, or cutover readiness is claimed.
- The activated order's prior-implementation text contains `349a0fda7777870adc79952f9a77201470565b3`, while GitHub verifies the actual 004-k implementation parent as `349a0afda7777870adc79952f9a77201470565b3`; the order and prior report bytes were preserved unchanged, and the current GitHub branch/head state is authoritative.

## Required report answers
1. 004-j's host-wide `bubblewrap_kernel_runtime_unsupported` conclusion was **not justified**; its raw probe supports only the narrower historical probe failure.
2. The raw 004-j probe was **host-direct**, not nested inside an outer Codex sandbox, based on the wrapper flag and sanitized `/proc` facts.
3. The observed raw-probe failure was **not a nested-sandbox artifact**, but neither does it establish a host/kernel-wide capability limit.
4. Host-direct Codex 0.149.0 **did not demonstrate** native workspace-write use here: `true` exited 1 and stopped the sequence before `cat`. This is a bounded result, not a host-wide unsupported claim.
5. Governed Local Coding E2E and cache reuse: **NOT RUN**, because the first native preflight gate failed.
6. First remaining failure: **before the Local Coding/product boundary**; no product defect was isolated.

## Recommended strategic follow-up
- Review the truthful pre-product-boundary native failure and its missing separate stderr subclass evidence. Any continuation should decide the next bounded diagnostic or rerun policy; this round made no host, Codex, bubblewrap, or product repair.

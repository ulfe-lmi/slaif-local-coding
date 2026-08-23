# OAP Coding-Agent Report — 004-k

## Work order
- Identifier: `004-k`
- Work-order file: `oap/orders/004-k-unship-and-consolidate-e2e-diagnostics.md`
- Numeric objective: `004`
- PR mode: `AMENDED_EXISTING_PR`

## Status
COMPLETE

## Executive summary

Removed the real-Codex E2E and sandbox diagnostic machinery from the installed
production package, moved the retained support into two repository-only helper
modules, and removed the superseded intermediate preflight/differential/
localization wrappers and tests. The retained fixture, bounded launcher,
sanitized event/lifecycle/provenance facts, cache/sentinel gates, final
read-only sandbox-runtime decision table, privacy controls, and cleanup checks
remain covered. The focused security review corrected inherited-environment
credential exposure and added bounded catalog subprocess output handling.

The verified external `bubblewrap_kernel_runtime_unsupported` result remains
unchanged from 004-j. This cleanup round made no governed model or live service
call and did not attempt the externally blocked sandbox repair.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`
- PR number/URL/state: #6, `https://github.com/ulfe-lmi/slaif-local-coding/pull/6`, OPEN, non-draft, MERGEABLE-CLEAN
- Base/head: `main` / `oap/004-real-codex-governed-e2e`
- Starting remote SHA: `d8a53ae0faf6b4ff43847cfb481c9a87461cf435`
- Implementation head SHA: `349a0fda7777870adc79952f9a77201470565b3`
- Report publication commit: SELF
- Implementation commits pushed before report: `349a0fda7777870adc79952f9a77201470565b3` (`OAP 004-k: unship and consolidate E2E diagnostics`)
- New PR this round: NO
- Amended existing PR: YES
- Merge performed: NO

## Changes and files
- Deleted the installed `src/slaif_local_coding/e2e.py` payload by moving its retained core into `tests/helpers/e2e_support.py`.
- Added `tests/helpers/sandbox_runtime.py` for the final bounded runtime/layout probe and fixed classification.
- Added `tests/helpers/__init__.py` to mark support explicitly repository-only.
- Removed superseded intermediate sandbox-preflight, differential-matrix, localization, direct-read-control, and command-failure wrapper machinery and their tests.
- Added explicit subprocess environment allowlisting, credential-name validation, stdin closure, timeouts, bounded catalog output, and focused negative coverage.
- Updated `README.md` and `TESTING.md` to label the support non-runtime and preserve the unchanged external blocker/completeness statement.
- Committed unchanged activated `oap/active` and the exact strategic order transcript.

Line counts:
- Shipped Python production source: `8,405` lines before (`4,999` plus the 3,406-line E2E module) to `4,999` after; production decrease `3,406` lines.
- E2E helper/test baseline: `5,406` lines (`src/.../e2e.py` 3,406 + `tests/test_e2e.py` 2,000) to `4,056` repository-only lines after (`e2e_support.py` 1,840, `sandbox_runtime.py` 859, helper init 1, test 1,356); decrease `1,350` lines.

## Acceptance evidence
### Criterion 1
- PASSED. `src/slaif_local_coding/e2e.py` no longer exists; production import/payload scan found no E2E/sandbox diagnostic names. The wheel contained 23 members and no `e2e.py`, `tests/`, sandbox, bubblewrap, or Codex diagnostic payload.

### Criterion 2
- PASSED. Repository-only helpers retain the private synthetic fixture, disposable Codex home, bounded launcher, sanitized event and command lifecycle facts, sentinel/cache gates, and final runtime boundary probe. Sdist inspection found the support only under `tests/`; no installed `src` diagnostic payload was present.

### Criterion 3
- PASSED. Focused review covered every retained subprocess, temporary-file, credential-environment, raw-stream, cache-inventory, and cleanup boundary. Added negative tests cover named-credential allowlisting and bounded model-catalog output.

### Criterion 4
- PASSED. No `shell=True`, `os.system`, shell execution, unbounded catalog capture, inherited credential environment, raw logging, or unsafe scratch cleanup path remains in retained support. Fixed argv, closed stdin, explicit timeouts, private temporary state, process waits/kill-on-timeout, and sanitized return dataclasses are enforced.

### Criterion 5
- PASSED. Baseline/current line counts, wheel/sdist member scans, production import scan, secret/private-path scan, subprocess/shell audit, raw-logging audit, and scratch-residue audit were completed truthfully. Helper/test total decreased by 1,350 lines.

### Criterion 6
- PASSED. README and TESTING identify repository-only support, the unchanged `bubblewrap_kernel_runtime_unsupported` external limitation, objective-004 completeness at 35%, and branch readiness at approximately 78%. No production, vision, compaction, cutover, or host-repair claim was added.

### Criterion 7
- PASSED. All required local gates passed; implementation-head GitHub CI `test` is SUCCESS for the implementation SHA. Report-head checks are pending until this report-only commit is pushed.

## Verification
- `uv lock --check`: PASSED — lock is resolved without changes.
- `uv sync --frozen --extra dev`: PASSED — frozen environment checked.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen ruff format --check .`: PASSED — 121 files formatted.
- `uv run --frozen mypy src tests`: PASSED — no issues in 37 source files.
- `uv run --frozen pytest tests/test_e2e.py -q`: PASSED — 38 passed.
- `uv run --frozen pytest -q`: PASSED — 287 passed, 7 skipped; established opt-in live-service tests remain SKIPPED, not passes.
- `uv build`: PASSED — wheel and source distribution built.
- Wheel/sdist member inspection: PASSED — wheel 23 members with no installed diagnostic payload; sdist 143 members with support labeled under repository `tests/` and no installed `src` diagnostic module.
- `python3 -m compileall -q src tests oap/bin`: PASSED.
- `bash -n oap/bin/*.sh`: PASSED.
- `git diff --check`: PASSED.
- Production E2E/import scan: PASSED — no diagnostic imports or payload names in `src/slaif_local_coding`.
- Secret/private-path scan: PASSED — no added secret, bearer, credential-value, or private-host-path matches.
- Subprocess/shell audit: PASSED — no shell execution patterns in retained helpers.
- Raw logging audit: PASSED — no direct print/logger/metric emission in retained helpers.
- Scratch-residue audit: PASSED — no E2E/sandbox temporary directories remained.
- `gh pr checks 6 --repo ulfe-lmi/slaif-local-coding`: PASSED — `test` SUCCESS for implementation head `349a0fda7777870adc79952f9a77201470565b3`.

## Live model/service evidence
- Cleanup-only live model/service checks: NOT RUN — no live call was required or authorized for this cleanup round.
- Candidate adapter 18031: NOT RUN — not started.
- Protected Qwen/vLLM 18020, model files, keys, systemd, firewall/VPN/network bindings, Codex profiles, and host sandbox/kernel state changed: NO.
- The prior verified 004-j external result is preserved as historical evidence; it was not rerun or broadened here.

## GitHub CI / required checks
- Implementation-head check: `test` — SUCCESS for `349a0fda7777870adc79952f9a77201470565b3`.
- All required checks green at drafting: YES.
- Report-head checks: PENDING until this report-only commit is pushed; strategy verifies the final report-head result.

## Local setup/dependencies
- Used the existing repository-local frozen `uv` environment.
- No dependency, lockfile, package metadata, service, sudo, model, profile, or host configuration change.
- Build artifacts were generated only for inspection and are ignored local outputs.

## Documentation
- Updated `README.md` and `TESTING.md` to describe the repository-only helper modules, installed-wheel boundary, retained gates, security controls, and unchanged external limitation.

## Safety/scope confirmations
- Unrelated files changed: NO.
- Secrets, raw prompts/source/tool output/images, credentials, raw diagnostics, customer data, and private paths exposed or committed: NO.
- Protected 18020/Qwen/vLLM/Codex fixture changed: NO.
- Required live model/service tests: NOT RUN by explicit cleanup-round scope; no local static/unit gate was skipped.
- Scope deviation: NO.
- Extra objective PR: NO.
- Coding-agent merge/auto-merge: NO.
- Activated order/active edited by coding: NO; exact strategic bytes committed unchanged: YES.
- Report commit report-only: YES; this report is intended to be the sole final publication change.

## Known limitations/blockers
- The existing Codex/bubblewrap boundary remains externally blocked at the verified `bubblewrap_kernel_runtime_unsupported` classification. No installation, host, kernel, or package remediation was attempted.
- No new governed sentinel success, vision proof, compaction proof, production readiness, or cutover readiness is claimed.

## Recommended strategic follow-up
- Review the reduced installed attack surface, focused security remediation, truthful package evidence, and preserved external boundary. Strategy decides any future host/CLI investigation or objective continuation.

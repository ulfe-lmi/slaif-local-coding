# OAP Coding-Agent Report — 004-q

## Work order
- Identifier: `004-q`
- Work-order file: `oap/orders/004-q-lifecycle-and-content-based-gates.md`
- Numeric objective / round: `004` / `004-q`
- PR mode: `AMENDED_EXISTING_PR`

## Status
BLOCKED

## Executive summary

The ordinary-lifecycle predicate and focused fake-run test were changed so a
harmless model-selected command is accepted when the Codex process exits 0,
the command lifecycle completes with exit 0, no command lifecycle fails, and
there is no parser/startup/tool-boundary failure. Exact command equality remains
available as a diagnostic. No Local Coding production code changed.

The one authorized fresh workspace-write A invocation was started against the
protected 18020 provider using Codex `0.149.0`, approvals-never, a disposable
CODEX_HOME, and the synthetic fixture. Its enclosing terminal session did not
return the sanitized result payload to this execution. Therefore A success is
not proven, and the order correctly stopped before dependency acquisition,
candidate adapter 18031, compiler/cache, and governed E2E. No retry was made.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #6, `https://github.com/ulfe-lmi/slaif-local-coding/pull/6`, OPEN,
  non-draft, MERGEABLE
- Base/head: `main` / `oap/004-real-codex-governed-e2e`
- Starting remote SHA: `01029d0b82839109e56a26bf097e7eb255b02f3c`
- Implementation head SHA: `19ce6a3843fc1655ef1f01530a9c402b5cacdfa6`
- Report publication commit: SELF
- Implementation commits pushed before report:
  `19ce6a3843fc1655ef1f01530a9c402b5cacdfa6`
- New PR this round: NO
- Amended existing PR: YES
- Merge performed: NO

## Changes and files
- `tests/helpers/e2e_support.py`: ordinary lifecycle success no longer requires
  exact `/usr/bin/true` equality; it requires recognized/completed successful
  lifecycle facts and excludes fixed parser/startup/tool-boundary failures.
- `tests/test_e2e.py`: focused fake-run coverage now uses a different harmless
  command and proves lifecycle acceptance while retaining equality diagnostics.
- `README.md`, `TESTING.md`, `oap/COMPLETENESS.md`: recorded the corrected gate
  and truthful 004-q evidence state.
- `oap/orders/004-q-lifecycle-and-content-based-gates.md` and `oap/active`:
  committed unchanged activated strategic bytes.
- No Local Coding production adapter, dependency, lockfile, model, gateway,
  service, or profile code changed.

## Acceptance evidence

### Criterion 1 — 004-p control and corrected lifecycle predicate
- PASSED as prior immutable evidence. 004-p's danger-control invocation
  reached Codex `0.149.0`, exited 0, and completed one successful ordinary
  command; the model-selected command differed from the former literal gate.
- PASSED. The 004-q predicate no longer uses `actual_command_equal` as a
  success requirement. Equality remains a reported diagnostic fact.

### Criterion 2 — workspace-write ordinary lifecycle A
- BLOCKED / NOT PROVEN. Exactly one fresh A invocation was launched with
  `workspace-write`; its sanitized result payload was not returned by the
  execution session. Process exit, timeout, recognized-event count, chosen
  command class, command hash/shape, lifecycle counts, and failure origin are
  therefore unavailable. No retry was made.

### Criterion 3 — exact delegated dependency acquisition B
- NOT RUN. The order gates B on a qualified A result. No dependency output,
  byte length, SHA-256, or provenance claim is made.

### Criterion 4 — governed Local Coding E2E
- NOT RUN. Candidate adapter 18031 was not started. No governed invocation,
  root/dependency observation, compiler miss/hit, injection, sentinel, or
  persistent-cache reuse claim is made.

### Criterion 5 — bounded scope
- PASSED. The implementation is limited to the existing ordinary lifecycle
  predicate, focused test fixture/assertions, outcome documentation, and the
  unchanged activated transcript. No new field, dataclass, module, parser,
  retry, fallback, diagnostic subsystem, or product behavior was added.

### Criterion 6 — required final answers

1. Workspace-write successful ordinary shell lifecycle? **NOT PROVEN**; exactly
   one A was launched, but its sanitized result was not retrievable.
2. Safe command class and acceptance? **NOT AVAILABLE**; no raw command or
   unsanitized event was retained or reported.
3. Exact delegated dependency by contents/hash/length? **NOT RUN**.
4. Local Coding reached? **NO**; candidate 18031 was not started.
5. First governed invocation passed? **NOT RUN**.
6. Second invocation proved persistent cache reuse? **NOT RUN**.
7. First remaining blocker? Bounded A evidence capture in the ordinary Codex
   qualification execution, outside the Local Coding product boundary.

## Verification
- `uv lock --check`: PASSED — 32 packages resolved; lock unchanged.
- `uv sync --frozen --extra dev`: PASSED — 31 packages checked.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen ruff format --check .`: PASSED — 133 files formatted.
- `uv run --frozen mypy src tests`: PASSED — no issues in 37 source files.
- `uv run --frozen pytest tests/test_e2e.py -q`: PASSED — 47 passed.
- `uv run --frozen pytest -q -rs`: PASSED — 296 passed, 7 skipped because
  `SLAIF_LIVE_TEST=1` was not set.
- `uv build`: PASSED — wheel and source distribution built.
- Wheel/source boundary inspection: PASSED — wheel 23 members with zero
  installed-payload violations; sdist 155 members with 17 source payload
  members and zero installed-payload violations.
- `uv run --frozen python -m compileall -q src tests oap/bin`: PASSED.
- `bash -n oap/bin/*.sh`: PASSED.
- `git diff --check`: PASSED.
- Changed-addition secret scan: PASSED — no credential, bearer, or private-key
  material detected.
- Changed-addition raw-logging scan: PASSED — no raw prompt/source/image/tool
  output/body logging pattern detected.
- Ordered A lifecycle: BLOCKED — one invocation launched; sanitized result
  unavailable; dependency and governed stages were not run.

## Live model/service evidence
- Live discovery found Codex profile `default`, provider class
  `qwen38_3090_vllm`, model `qwen3.8-27b`, Responses wire mode, and protected
  provider port 18020. The separate `qwen-serving-vision.service` was
  inactive; no separate active vision route was altered or claimed. The live
  catalog identified text input for this profile, so no vision request was
  attempted.
- Before/after protected snapshots matched: `qwen-serving.service` remained
  active with main PID `26028` and start timestamp
  `Sat 2026-08-22 05:35:46 CEST`; the vision unit remained inactive; only port
  18020 listened; ports 18021 and 18031 were absent; protected `/health` and
  `/v1/models` each returned HTTP 200.
- Protected hashes were unchanged before/after: Qwen unit
  `64b3ccd5bdb64da4e3dcabca660fada8155583c96b6bc11de47536e595df5910`, Codex
  profile `18ead58ac440d29ce2e86addf855c24f471021c6050d4da685320a2cf6eb62eb`,
  and model catalog
  `0d4e3235dd2730b8d353a62c63c970e733de1d2b6b6bfe00216f8fb3ce5e1eeb`.
- A used only disposable fixture/config state and the existing environment-
  referenced credential name. No credential, prompt, source, image, event, or
  response body was printed or persisted.

## GitHub CI / required checks
- Implementation-head check: `test` — SUCCESS for
  `19ce6a3843fc1655ef1f01530a9c402b5cacdfa6` (CI run
  `32660913561`, job `97246841819`).
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
- Updated `README.md`, `TESTING.md`, and `oap/COMPLETENESS.md` with the
  corrected lifecycle gate and truthful partial qualification state.

## Safety/scope confirmations
- Unrelated files changed: NO.
- Secrets, raw prompts/source/tool output/images, credentials, raw diagnostics,
  customer data, and private URLs exposed or committed: NO.
- Protected `18020`/Qwen/vLLM/Codex fixture changed: NO.
- Dependency, adapter, compiler, cache, sentinel, vision, and compaction
  stages: NOT RUN because A evidence was unavailable.
- Scope deviation: NO; no retry or alternate prompt was used.
- Extra objective PR: NO.
- Coding-agent merge/auto-merge: NO.
- Activated order/active edited by coding: NO; exact strategic bytes committed
  unchanged: YES.
- Report commit report-only: YES.

## Known limitations/blockers
- The one permitted A invocation did not return its sanitized evidence payload
  to this execution, so ordinary workspace-write capability is not qualified.
- Exact A command class/hash/shape, dependency content/hash/length, adapter
  reachability, compiler/cache behavior, sentinel compliance, compaction, and
  vision E2E remain unproven.
- Objective 004 remains at 15%; branch readiness remains approximately 74%.

## Recommended strategic follow-up

Review the bounded A evidence-capture blocker and decide whether a future
continuation should repeat qualification under a reliable sanitized-output
capture path. No host, Codex profile, Qwen/vLLM service, network, or product
repair was made in this round.

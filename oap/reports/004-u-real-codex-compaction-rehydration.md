# OAP Coding-Agent Report — 004-u

## Work order
- Identifier: `004-u`
- Order path: `oap/orders/004-u-real-codex-compaction-rehydration.md`
- Numeric objective / round: `004` / `004-u`
- PR mode: `AMENDED_EXISTING_PR`

## Status
BLOCKED

## Executive summary

The bounded persistent-session attempt reached the disposable candidate adapter
boundary but Codex `0.149.0` failed during startup before the seed request. The
candidate health/readiness checks passed, then the seed process exited `1` with
zero JSONL event bytes and no upstream model request. Four bounded resume
attempts were subsequently made by the harness; each exited without a session,
producing no event bytes or adapter request. No Codex-native compaction event,
reduced-history continuation, Local Coding rehydration, governance injection,
compiler attempt, or sentinel result was produced.

This is an external Codex acceptance-fixture limitation at the pre-request
startup boundary, not a Local Coding product failure. No product code was
changed. The round remains blocked and does not raise objective completeness or
branch-readiness percentages.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #6, `https://github.com/ulfe-lmi/slaif-local-coding/pull/6`, OPEN,
  non-draft, MERGEABLE-CLEAN
- Base/head: `main` / `oap/004-real-codex-governed-e2e`
- Required base SHA: `7a2c36a0a40958a6059a765c2f9d5e5bf4ddc161`
- Starting remote SHA: `057fb4b4f5f3a43cedb6204ee39b616b6dfbcbbc`
- Implementation head SHA: `940c2345e2f20d08a25059ced24d5ec04a1ae1b3`
- Report publication commit: SELF
- Implementation commits pushed before report: `940c2345e2f20d08a25059ced24d5ec04a1ae1b3`
- New PR this round: NO
- Amended existing PR: YES
- Merge performed: NO

## Changes and files

- `oap/orders/004-u-real-codex-compaction-rehydration.md`: committed the
  activated strategic order byte-for-byte unchanged.
- `oap/active`: committed the activated `004-u` pointer byte-for-byte unchanged.
- No runtime adapter, compiler, cache, helper, test, dependency, configuration,
  service, model, profile, or gateway code changed.

## Acceptance evidence

### Criterion 1 — persistent Codex-native compaction setup

- BLOCKED. Codex version was `0.149.0`. Current help exposed no explicit compact
  command. Disposable catalog/config facts selected a `24,000` context window,
  `16,000` auto-compaction threshold, and persistent `CODEX_HOME`; the seed
  invocation was non-ephemeral and included the global-approval-bypass intent.
- Sanitized argv facts: seed shape was `<codex> exec --dangerously-bypass-approvals-and-sandbox --json --strict-config --disable unified_exec --cd <fixture> --output-last-message <last-message> <prompt>`; resume shape was `<codex> exec resume --last --dangerously-bypass-approvals-and-sandbox --json --strict-config --disable unified_exec --cd <fixture> --output-last-message <last-message> <prompt>`. `--ephemeral` was absent; no session identity was emitted.
- BLOCKED at startup. The seed exited `1`, timed out `false`, emitted `0` event
  bytes, and made no upstream model request. The exact startup diagnostic was
  not retained or reported.

### Criterion 2 — governed seed state

- NOT RUN. Seed metrics remained zero for roots, dependency observations,
  dependency cache misses, compiler attempts/calls, injections, and
  rehydration outcomes. No dependency bytes/hash or hidden sentinel was
  acquired.

### Criterion 3 — Codex-native compaction proof

- NOT RUN. No compaction event type was observed. No reduced-history request,
  pre/post request hash pair, root-absence observation, or same-session
  continuation was available.
- The four bounded resume attempts exited `2`, emitted `0` event bytes, and
  had no recorded model request; they did not establish a session or compaction.

### Criterion 4 — post-compaction rehydration/injection

- NOT RUN. No root-absent post-compaction request reached Local Coding, so
  rehydration hit/injected metrics, stable injection, compiler-attempt
  suppression, and sentinel compliance cannot be claimed.

### Criterion 5 — isolation, privacy, bounds, cleanup, and host invariants

- PASSED for the bounded fixture lifecycle. Candidate health/readiness were
  HTTP `200`; the temporary fixture, disposable Codex home, cache, event
  files, diagnostics, and candidate were cleaned up.
- PASSED. The protected Qwen service remained active with PID `26028`; port
  `18020` remained the only listener among `18020`, `18021`, and `18031`; the
  separate vision service remained inactive.
- PASSED. No raw prompt, source, tool output, model response, credential value,
  or opaque compaction text was retained or reported.

### Criterion 6 — no premature product change and truthful limitation

- PASSED. No Local Coding product change occurred before or after the bounded
  run. The first direct gate is recorded as a Codex startup/session boundary,
  not a product defect.
- SCOPE DEVIATION. The harness continued with four bounded resume attempts after
  the failed seed instead of stopping immediately at the first failed gate.
  They were session-less, produced no model request, stayed within the order's
  four-continuation ceiling, and no further live retry will be made this round.

### Criterion 7 — local and remote gates

- PASSED for the unchanged repository baseline and activation-only amendment;
  implementation-head CI passed. The required compaction acceptance remains
  blocked, and report-head CI is checked after this report-only publication.

## Verification

- `uv lock --check`: PASSED — lock resolved and remained unchanged.
- `uv sync --frozen --extra dev`: PASSED — 31 packages checked.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen ruff format --check .`: PASSED — 141 files already formatted.
- `uv run --frozen mypy src tests`: PASSED — no issues in 37 source files.
- `uv run --frozen pytest tests/test_e2e.py -q -rs`: PASSED — 48 passed.
- `uv run --frozen pytest -q -rs`: PASSED — 297 passed; 7 opt-in live tests
  correctly `SKIPPED` because `SLAIF_LIVE_TEST=1` was not set.
- `uv build`: PASSED — source distribution and wheel built.
- Wheel boundary inspection: PASSED — no `tests`, `oap`, `e2e_support`, or
  `sandbox_runtime` members in the wheel. Source distribution repository/test
  support is source-only and non-runtime.
- `uv run --frozen python -m compileall -q src tests oap/bin`: PASSED.
- `bash -n oap/bin/*.sh`: PASSED.
- `git diff --check` and staged diff check: PASSED.
- Changed-path secret/private-value scan: PASSED — no credential value, bearer
  value, private key, or raw private payload match.
- Bounded persistent-session driver: BLOCKED — candidate checks were `200`, but
  seed startup exited `1` with zero events/requests; four session-less resumes
  exited `2`; no compaction or governance evidence.
- Codex capability reconnaissance: PASSED — `codex-cli 0.149.0`; no explicit
  compact command in help; disposable model catalog exposed the selected
  context/auto-compaction fields.
- Protected-host post-audit: PASSED — Qwen active/PID `26028`, vision service
  inactive, `18020` listening, `18021` and `18031` absent after teardown.
- Scoped-path check: PASSED — implementation commit changed only the exact
  activated order and active pointer.

## Live model/service evidence

- Candidate adapter: loopback `18031`, bounded health/readiness `200/200`,
  stopped after the attempt.
- Protected upstream: loopback `18020`; one bounded readiness request reached
  the protected service through the candidate. No `/v1/responses` model request
  reached upstream.
- Current protected model catalog: one text-only model was advertised by the
  bounded `/v1/models` check; no vision request or vision-capability claim was
  made. No pre-existing image proxy was assumed.
- Protected Qwen/vLLM/model/network/Codex-profile state was not changed.

## GitHub CI / required checks

- Implementation-head check: CI `test` — SUCCESS at
  `940c2345e2f20d08a25059ced24d5ec04a1ae1b3` (run `32664513354`, job
  `97255733328`).
- All required checks green at drafting: YES for the implementation head.
- Report-head checks: newly queued by this report-only publication; strategy
  verifies the final report head independently.

## Local setup/dependencies

- Existing Python 3.12 repository environment with frozen `uv` sync.
- One temporary candidate app was created in-process on `18031` with a fresh
  private cache, static opaque identity, protected upstream reference, and
  disposable synthetic fixture.
- The Codex-under-test used a fresh persistent disposable `CODEX_HOME`, no
  `--ephemeral` flag, bounded output/diagnostic files, and was waited/reaped.
- No package, lockfile, host package, sudo, service, model, credential,
  profile, network, or system configuration change.

## Documentation

- No product documentation changed because no behavior or contract changed.
- This immutable report records the external acceptance-fixture limitation and
  the bounded scope deviation.

## Safety/scope confirmations

- Unrelated files changed: NO.
- Secrets, raw prompts/source/tool output/images/model text/customer data,
  credentials, and opaque compacted content: NOT exposed, logged, or committed.
- Protected `18020`/Qwen/vLLM/Codex fixture changed: NO.
- Compaction, post-compaction rehydration, injection, compiler suppression,
  and sentinel stages: NOT RUN because seed startup failed.
- Extra objective PR: NO.
- Coding-agent merge/auto-merge: NO.
- Activated order/active edited by coding: NO; exact strategic bytes committed
  unchanged: YES.
- Report commit report-only: YES.

## Known limitations/blockers

- The exact Codex startup diagnostic was intentionally not retained, so this
  report does not identify a speculative config/fixture cause.
- A successful persistent Codex session, actual native compaction or reduced
  history, and Local Coding rehydration remain unproven.
- No product defect is inferred from zero adapter traffic. Strategy must decide
  whether a future continuation may repair the disposable Codex fixture and
  attempt a new bounded run.
- This evidence does not claim production, multi-user, gateway, cutover,
  generic compaction-provider, vision, or systemd readiness.

## Recommended strategic follow-up

Review the remote blocked report and decide whether a separately bounded
continuation should diagnose the disposable Codex startup boundary. Any future
attempt must preserve the no-host-mutation boundary and stop immediately at its
first failed seed gate.

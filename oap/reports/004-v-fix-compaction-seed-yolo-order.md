# OAP Coding-Agent Report — 004-v

## Work order
- Identifier: `004-v`
- Order path: `oap/orders/004-v-fix-compaction-seed-yolo-order.md`
- Numeric objective / round: `004` / `004-v`
- PR mode: `AMENDED_EXISTING_PR`

## Status
BLOCKED

## Executive summary

The corrected persistent Codex seed placed the global yolo flag before `exec`,
but Codex `0.149.0` still exited during startup before producing any event or
request. The disposable candidate adapter was healthy on 18031, but received
zero seed/model requests and recorded zero governance/compiler activity. Per
the order, the run stopped immediately: zero resumes and zero post-compaction
turns ran. No Local Coding product or helper code changed.

This is an external Codex acceptance-fixture limitation at the pre-request
startup boundary, not a proven Local Coding product defect. Actual native
compaction, rehydration, injection, and sentinel compliance remain unproven.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #6, `https://github.com/ulfe-lmi/slaif-local-coding/pull/6`, OPEN,
  non-draft, MERGEABLE-CLEAN
- Base/head: `main` / `oap/004-real-codex-governed-e2e`
- Required base SHA: `7a2c36a0a40958a6059a765c2f9d5e5bf4ddc161`
- Starting remote SHA: `e40f86a0a94ebad270abb08604cbf03653ed4355`
- Implementation head SHA: `4a1d5982520eb75bac6c8b6158c64e03a8348b8f`
- Report publication commit: SELF
- Implementation commits pushed before report: `4a1d5982520eb75bac6c8b6158c64e03a8348b8f`
- New PR this round: NO
- Amended existing PR: YES
- Merge performed: NO

## Changes and files

- `oap/active`: activated `004-v` pointer, committed unchanged from the
  strategic workspace.
- `oap/orders/004-v-fix-compaction-seed-yolo-order.md`: committed unchanged
  from the strategic workspace.
- No runtime adapter, compiler, cache, helper, test, dependency, service,
  configuration, model, profile, or gateway code changed.

## Acceptance evidence

### Criterion 1 — corrected persistent global-yolo setup

- BLOCKED at Codex startup. Installed Codex was `0.149.0`; no explicit compact
  command was exposed by the inspected help. The disposable catalog/config
  used a `24,000` context window and `16,000` auto-compaction threshold, with a
  persistent private `CODEX_HOME` and no `--ephemeral` flag.
- Corrected seed template: `<codex> --dangerously-bypass-approvals-and-sandbox
  exec --json --strict-config --disable unified_exec --cd <fixture>
  --output-last-message <last-message> <prompt>`.
- Seed argv template SHA-256: `4b2516f74531f83c5b397f2d7e85ad5b6cdff1b5590dd096428612be5e107508`.
- Supported resume template was recorded as
  `<codex> exec resume --last --dangerously-bypass-approvals-and-sandbox
  --json --strict-config --disable unified_exec --output-last-message
  <last-message> <prompt>`.
- Resume argv template SHA-256:
  `c0628d34c0b25f4e59fbd76590eb54cf0ad700c1c3ad063edf1634582c3b9719`.

### Criterion 2 — governed seed state

- BLOCKED. Candidate health/readiness were HTTP `200/200`, but the seed exited
  `1` after `0.008` seconds with `0` event bytes and no adapter/model request.
- Compiler-attempt delta: `0`; compiler-call delta: `0`; root observation
  delta: `0`; dependency observation delta: `0`; dependency cache-miss delta:
  `0`; injection delta: `0`; rehydration entries: `0`.
- Dependency observation and hidden sentinel were not produced.

### Criterion 3 — Codex-native compaction proof

- NOT RUN. The first seed gate failed, so no resume was run (`0/4`), no
  compaction event was observed, and no reduced-history continuation or
  same-session evidence exists.

### Criterion 4 — post-compaction rehydration/injection

- NOT RUN. No post-compaction request reached the adapter. Rehydration hit,
  rehydrated injection, zero post-compaction compiler attempts, and hidden
  sentinel compliance cannot be claimed.

### Criterion 5 — privacy, bounds, cleanup, and host invariants

- PASSED. The candidate was loopback-only on 18031, stopped after the bounded
  attempt, and its temporary fixture, cache, persistent Codex home, events, and
  diagnostics were removed.
- PASSED. No raw prompt, source, tool output, model response, credential,
  authorization value, or opaque diagnostic text was retained or reported.
- PASSED. Protected 18020/Qwen state was unchanged: the unit remained active
  with the same observed process identity/start time; only 18020 remained
  listening after teardown, and 18021/18031 were absent.

### Criterion 6 — no premature product change and truthful limitation

- PASSED. No product/helper change occurred before or after the run. The first
  acceptance gate is recorded as a Codex startup/session boundary, not as a
  Local Coding defect.
- PASSED. After correcting the disposable candidate configuration, the ordered
  seed itself was run once with the corrected argv. It failed immediately and
  the required stop rule prevented resumes or retries.
- Objective and branch percentages remain unchanged pending strategic review.

### Criterion 7 — local and remote gates

- PASSED for the activation-only implementation amendment and required CI. The
  compaction acceptance remains blocked.

## Verification

- `uv lock --check`: PASSED — lock remained resolved.
- `uv sync --frozen --extra dev`: PASSED — 31 packages checked.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen ruff format --check .`: PASSED — 143 files already formatted.
- `uv run --frozen mypy src tests`: PASSED — no issues in 37 source files.
- `uv run --frozen pytest tests/test_e2e.py -q -rs`: PASSED — 48 passed.
- `uv run --frozen pytest -q -rs`: PASSED — 297 passed; 7 opt-in live tests
  correctly `SKIPPED` because `SLAIF_LIVE_TEST=1` was not set.
- `uv build`: PASSED — source distribution and wheel built.
- Wheel boundary inspection: PASSED — wheel contained no `tests`, `oap`,
  `e2e_support`, or `sandbox_runtime` members.
- `uv run --frozen python -m compileall -q src tests oap/bin`: PASSED.
- `bash -n oap/bin/*.sh`: PASSED.
- `git diff --cached --check`: PASSED for the activation amendment.
- Staged changed-path secret/private-value scan: PASSED.
- Corrected bounded persistent-session runner: BLOCKED — candidate
  health/readiness `200/200`; seed exit `1`, `0` events, `0` requests, `0`
  resumes, `0` post-compaction turns.
- Protected upstream authenticated `/health` and `/v1/models`: PASSED — both
  returned HTTP `200`; no raw response body was retained.
- Protected-host post-audit: PASSED — 18020/Qwen remained active; 18021 and
  candidate 18031 were absent after teardown.
- `gh pr checks 6 --repo ulfe-lmi/slaif-local-coding --watch --interval 5`:
  PASSED — required CI check `test` succeeded at implementation head.

## Live model/service evidence

- Current protected Qwen profile/catalog was discovered read-only before the
  run: model context `150,000`, configured auto-compaction threshold `125,000`,
  input modality `text`, and image support `false`.
- No current live vision service or pre-existing image proxy was found: 18021
  was not listening and the Qwen catalog declared zero image support. No vision
  request or vision-capability claim was made.
- Candidate adapter: loopback 18031, health/readiness `200/200`, stopped after
  the failed seed. No candidate model request reached protected Qwen.
- Protected Qwen/vLLM/model/network/Codex-profile state was not changed.

## GitHub CI / required checks

- Implementation-head check: CI `test` — SUCCESS at
  `4a1d5982520eb75bac6c8b6158c64e03a8348b8f` (run `32665193077`, job
  `97257394819`).
- All required checks green at drafting: YES for the implementation head.
- Report-head checks are newly triggered by this report-only publication;
  strategy verifies the final report head independently.

## Local setup/dependencies

- Existing Python 3.12 environment with frozen `uv` synchronization.
- One temporary candidate used a fresh private cache, static opaque identity,
  protected upstream reference, synthetic governed repository, persistent
  disposable `CODEX_HOME`, and bounded private event/diagnostic files.
- No package, lockfile, host package, sudo, service, model, credential,
  profile, network, or system configuration change.

## Documentation

- No product documentation changed because no behavior or contract changed.
- This immutable report records the corrected argv evidence, external startup
  limitation, exact stop point, and required verification.

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

- The bounded corrected seed still fails before the first Codex event/request.
  The exact startup diagnostic was not retained, so this report does not infer
  a speculative config or fixture cause.
- A successful persistent Codex session, native compaction/reduced history,
  Local Coding rehydration, and post-compaction sentinel compliance remain
  unproven.
- This evidence does not claim production, multi-user, gateway, cutover,
  generic compaction-provider, vision, or systemd readiness.

## Recommended strategic follow-up

Review the remote blocked report and decide whether a separately bounded
continuation may diagnose the disposable Codex startup boundary. Any future
attempt should preserve the no-host-mutation boundary and the first-failed-seed
stop rule.

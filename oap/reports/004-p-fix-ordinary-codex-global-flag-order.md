# OAP Coding-Agent Report — 004-p

## Work order
- Identifier: `004-p`
- Work-order file: `oap/orders/004-p-fix-ordinary-codex-global-flag-order.md`
- Numeric objective / round: `004` / `004-p`
- PR mode: `AMENDED_EXISTING_PR`

## Status
PARTIAL

## Executive summary

The ordinary Codex harness now places the global approval option before `exec`:
`codex --ask-for-approval never exec --sandbox <mode> ...`. The focused test
rejects the former ordering, and the corrected live B invocation passed Codex
startup and reached a command lifecycle. B exited 0, but the model issued one
successful shell command that was not the required exact `/usr/bin/true`.
Per the order, A and every later dependency/adapter/compiler/governed step were
not run. No Local Coding production code or protected live service changed.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #6, `https://github.com/ulfe-lmi/slaif-local-coding/pull/6`, OPEN, non-draft, MERGEABLE
- Base/head: `main` / `oap/004-real-codex-governed-e2e`
- Starting remote SHA: `0a95c963375f0a3b9bb372dd10b0c5cf99917172`
- Implementation head SHA: `d22f81e28fa05129c1d8cbd4d84aa894ba17179c`
- Report publication commit: SELF
- Implementation commits pushed before report: `d22f81e28fa05129c1d8cbd4d84aa894ba17179c`
- New PR this round: NO
- Amended existing PR: YES
- Merge performed: NO

## Changes and files
- `tests/helpers/e2e_support.py`: moved `--ask-for-approval never` before
  `exec` in both the normalized ordinary fingerprint and subprocess argv.
- `tests/test_e2e.py`: added one focused assertion that the global option
  precedes `exec`.
- `README.md`, `TESTING.md`, `oap/COMPLETENESS.md`: recorded the corrected
  004-p qualification and its partial result.
- `oap/orders/004-p-fix-ordinary-codex-global-flag-order.md` and `oap/active`:
  committed unchanged activated strategic bytes.
- No production adapter, dependency, lockfile, model, gateway, service, or
  profile code was changed.

## Acceptance evidence

### Criterion 1 — supported ordinary argv and focused regression
- PASSED. The two ordinary-run argv construction sites now emit the global
  approval option before `exec`.
- PASSED. The focused fake-run test asserts
  `index(--ask-for-approval) < index(exec)` and verifies the A/B fingerprint
  equality contract.
- PASSED. The installed Codex `0.149.0` accepted the corrected B argv and
  reached JSONL/model/tool activity; the former startup `argv_unsupported`
  failure did not recur.

### Criterion 2 — danger-full-access B
- PARTIAL. B ran once using the fresh private fixture and disposable
  `CODEX_HOME`. It exited `0`, was not timed out, emitted 861 bounded event
  bytes, and had 7 recognized/0 rejected events.
- One command event was observed with successful command status and exit code
  0, but `actual_command_equal=false` for the required `/usr/bin/true`.
  The sanitized run facts were `failure_reason=command_incomplete` and
  `failure_origin=model_wrong_command`; this is not accepted as exact-command
  success.
- B tool-call count: 2. B normalized argv SHA-256:
  `c85a7d14e4732ac5e6129375ff57738f1a5d69c106377461b5b87b542f76b755`.
  B fixture fingerprint SHA-256:
  `d4f5de501290ba4290657447ab4308572b4a54e06fb2e3c38ea513ef21f9ab54`.

### Criterion 3 — workspace-write A and equivalence
- NOT RUN. A was correctly gated because B did not prove one exact
  `/usr/bin/true` command with exit 0.
- A normalized argv hash and A/B live equivalence: NOT PROVEN; no A
  fingerprint exists. The synthetic focused test still proves the helper's
  mode-independent fingerprint contract.

### Criterion 4 — dependency, Local Coding, and governed/cache sequence
- NOT RUN. Exact dependency `cat` was gated after A.
- NOT RUN. Candidate adapter `18031` was not started; no adapter, compiler,
  cache, sentinel, or governed E2E call occurred.
- The exact two governed invocations and persistent cache-reuse proof were not
  reached.

### Criterion 5 — bounded scope
- PASSED. The change is limited to the ordinary test harness, one focused
  regression assertion, supporting documentation, and the activated OAP
  transcript.
- PASSED. No new result field, dataclass, module, classification, fallback,
  retry mechanism, production behavior, or diagnostic subsystem was added.

### Criterion 6 — required final answers

1. Danger-full-access ordinary `/usr/bin/true` success? **NO.** B exited 0,
   but the one successful command was not the exact required command.
2. Workspace-write ordinary `/usr/bin/true` success? **NOT RUN**; A was gated.
3. A/B equivalent except sandbox mode? **NOT PROVEN**; A was not run.
4. Exact failure origin? **`model_wrong_command`** after successful Codex
   startup: one command event completed successfully but did not match the
   required command.
5. Same ordinary command path as normal Codex? **PARTIAL/UNPROVEN.** The
   installed ordinary `codex ... exec` surface was reached, but exact command
   qualification did not pass.
6. Difference from known-working outer Codex? **NOT DETERMINED.** The outer
   OAP host-direct/unsandboxed execution surface is not an equivalent proof of
   this disposable local-Qwen ordinary command path.
7. Dependency read? **NOT RUN.**
8. Local Coding reached? **NO.**
9. Governed E2E/cache reuse run/pass? **NOT RUN.**
10. First blocker and product-boundary location? The first remaining blocker is
    the ordinary Codex/model command-selection boundary (`model_wrong_command`),
    before the workspace gate and outside the Local Coding adapter product.

## Verification
- `uv lock --check`: PASSED — 32 packages resolved without lock changes.
- `uv sync --frozen --extra dev`: PASSED — 31 packages checked.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen ruff format --check .`: PASSED — 131 files already formatted.
- `uv run --frozen mypy src tests`: PASSED — no issues in 37 source files.
- `uv run --frozen pytest tests/test_e2e.py -q`: PASSED — 47 passed.
- `uv run --frozen pytest -q`: PASSED — 296 passed, 7 skipped; opt-in live
  adapter tests were skipped because the ordered B gate prevented starting
  the candidate adapter.
- `uv build`: PASSED — wheel and source distribution built.
- Wheel boundary inspection: PASSED — 23 members, zero installed
  test/OAP/diagnostic payload violations.
- Source-distribution boundary inspection: PASSED — 153 members, zero
  installed-payload violations.
- `uv run --frozen python -m compileall -q src tests oap/bin`: PASSED.
- `bash -n oap/bin/*.sh`: PASSED.
- `git diff --check`: PASSED.
- Changed-addition secret scan: PASSED — no credential, bearer, or private-key
  material detected.
- Changed-addition raw-logging scan: PASSED — no raw prompt/source/image/tool
  output/body logging pattern detected.
- Bounded live ordinary decision tree: PARTIAL — one B process ran; A,
  dependency, adapter, compiler, and governed/cache stages were gated by the
  exact-command failure. No retry, alternate prompt, or third control was
  used.

## Live model/service evidence
- Pre/post protected checks: `qwen-serving.service` remained active with main
  PID 26028 and the same start timestamp; `qwen-serving-vision.service`
  remained inactive.
- Only `0.0.0.0:18020` listened in both snapshots; 18021 and 18031 were
  absent. Protected `/health` and `/v1/models` each returned HTTP 200 before
  and after the bounded B run.
- Current protected unit SHA-256 was
  `64b3ccd5bdb64da4e3dcabca660fada8155583c96b6bc11de47536e595df5910`, equal
  to the previously verified baseline. The current Codex profile config hash
  was unchanged before/after at
  `fefea020eae48d2f9821694f7f20376e13361d6649759925bfbd4eb8a23ad1fc`.
- Live discovery found no active separate vision service/profile route to
  alter. The current Qwen service and Codex profile were preserved; no image
  request was attempted or claimed.
- The single B process used the protected loopback model route with the
  existing environment-referenced credential. No credential or raw response
  was printed or persisted.

## GitHub CI / required checks
- Implementation-head check: `test` — SUCCESS for
  `d22f81e28fa05129c1d8cbd4d84aa894ba17179c` (CI run
  `32656284727`).
- All required checks green at report drafting: YES for the implementation
  head.
- Report-head checks may be pending after the final report-only push; strategy
  verifies the final report-head result.

## Local setup/dependencies
- Existing repository-local Python 3.12 environment and frozen `uv` sync.
- No dependency, lockfile, package, service, sudo, model, credential, Codex
  profile, or host configuration change.
- Build artifacts were inspection outputs under ignored `dist/` and were not
  committed.

## Documentation
- Updated `README.md`, `TESTING.md`, and `oap/COMPLETENESS.md` with the
  corrected argv and truthful partial qualification.

## Safety/scope confirmations
- Unrelated files changed: NO.
- Secrets, raw prompts/source/tool output/images, credentials, raw diagnostics,
  customer data, and private URLs exposed or committed: NO.
- Protected `18020`/Qwen/vLLM/Codex fixture changed: NO.
- A, dependency, adapter, compiler, governed/cache, vision, and compaction
  stages: NOT RUN because the ordered B gate failed.
- Scope deviation: NO. The corrected B exposed the first remaining
  model-command qualification blocker; no repair or retry was attempted.
- Extra objective PR: NO.
- Coding-agent merge/auto-merge: NO.
- Activated order/active edited by coding: NO; exact strategic bytes committed
  unchanged: YES.
- Report commit report-only: YES.

## Known limitations/blockers
- The corrected global-option placement fixes the proven startup defect, but
  the ordinary B model selected a command other than the required exact
  `/usr/bin/true`. The order therefore does not authorize A or any later
  stage.
- Exact workspace capability, dependency bytes, adapter path, compiler/cache,
  sentinel, compaction, and vision E2E remain unproven.
- Objective 004 remains at 15%; branch readiness remains approximately 74%.

## Recommended strategic follow-up

Review the sanitized `model_wrong_command` B evidence and decide whether a
separately authorized continuation should address that ordinary command-path
qualification. No host, Codex profile, Qwen/vLLM service, network, or product
repair was made in this round.

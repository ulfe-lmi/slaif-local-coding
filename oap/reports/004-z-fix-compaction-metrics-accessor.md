# OAP Coding-Agent Report — 004-z

## Work order

- Identifier: `004-z`; order path: `oap/orders/004-z-fix-compaction-metrics-accessor.md`; numeric objective: `004`.
- PR mode: `AMENDED_EXISTING_PR`.

## Status

PARTIAL

## Executive summary

The proven external compaction-runner metrics accessor was corrected in the
private bounded runner to use the existing `root_observations` field. The
corrected bounded run used Codex `0.149.0`, global yolo before `exec`, a
persistent disposable session, a 24,000 context-window-only catalog with no
explicit auto-compaction field, a fresh private candidate on port `18031`, and
the protected upstream on port `18020`.

The governed seed passed with exact dependency acquisition and the hidden
sentinel. Four same-session resume turns also exited successfully, but every
resume still carried observed roots and no explicit compaction event was
emitted. The bounded run therefore did not prove Codex-native compaction or
run a post-compaction verification turn. No Local Coding product defect was
observed and no durable product/helper change was made.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`; PR: [#6](https://github.com/ulfe-lmi/slaif-local-coding/pull/6); state: OPEN, non-draft, merge state CLEAN after the implementation check.
- Base/head: `main` / `oap/004-real-codex-governed-e2e`.
- Starting remote SHA: `eb2f2c7954feb2d0422557c6884fc98f20143b71`.
- Implementation head SHA: `118f607acaa43f70d2b9fd9a413bd75a150e03cf`.
- Report publication commit: SELF.
- Implementation commits pushed before report: `118f607acaa43f70d2b9fd9a413bd75a150e03cf` (`OAP 004-z: record compaction metrics accessor rerun`).
- New PR this round: NO; amended existing: YES; merge performed: NO.

## Changes and files

- `oap/active`: committed unchanged strategic activation `004-z`.
- `oap/orders/004-z-fix-compaction-metrics-accessor.md`: committed unchanged activated order.
- No adapter, compiler, cache, durable E2E helper, fixture, dependency, service, model, profile, gateway, or host implementation changed.
- The repository helper already used `ConstitutionMetricsSnapshot.root_observations` and its focused accessor assertion passed; no repository helper/test edit was needed.
- The private runner used `root_observations` and was deleted after the run.

## Acceptance evidence

### Criterion 1 — sole metrics accessor correction

- PASSED — the corrected private bounded runner read the existing typed
  `root_observations` field; no `ConstitutionMetricsSnapshot.roots` accessor
  remains in the durable repository helper or the temporary runner used for
  the accepted rerun.

### Criterion 2 — governed seed

- PASSED — candidate health/readiness were `200/200`; the disposable catalog
  was `context_window=24000`, `max_context_window=24000`, and
  `auto_compact_token_limit=absent`.
- PASSED — the seed used Codex `0.149.0`, global
  `--dangerously-bypass-approvals-and-sandbox` before `exec`, omitted
  `--ephemeral`, exited `0`, emitted 908 bounded JSONL bytes, completed one
  successful intended dependency read, and passed the hidden sentinel.
- PASSED — seed metric deltas were root observations `2`, dependency
  observations `1`, dependency cache misses `1`, compiler attempts `2`,
  compiler calls `3`, injection updates `2`, injected requests `2`, and
  rehydration population `2`; no raw content was retained or reported.

### Criterion 3 — native compaction within bounds

- PARTIAL — four successful same-session resume turns were run with bounded
  synthetic filler. Their root-observation deltas were respectively `1`, `1`,
  `2`, and `2`; request deltas were `1`, `1`, `2`, and `2`. No resume emitted
  an explicit compaction event, and no root-absent request was proven.
- NOT RUN — no post-compaction verification turn was authorized because the
  bounded native compaction/reduced-history gate was not reached.

### Criterion 4 — root-absent rehydration and sentinel

- NOT RUN — no root-absent post-compaction request occurred, so no valid
  post-compaction rehydration hit, injected sentinel, or zero-additional-
  compiler-attempt claim is made.

### Criterion 5 — privacy, cleanup, protected state, and gates

- PASSED — the candidate process was terminated, port `18031` was absent, and
  all temporary fixture/session/cache/config/runner state was removed.
- PASSED — protected Qwen/vLLM remained active/running with MainPID `26028`
  and the same start timestamp; the service, drop-in, and launch-script
  hashes were unchanged. Only protected port `18020` remained in the relevant
  listener set.
- PASSED — bounded authenticated protected `/health` and `/v1/models` calls
  returned `200`; the current model catalog contained one model and zero
  image-capable models. No vision service or image proxy was assumed or
  changed.
- PASSED — the four OAP Codex profiles and two Qwen Codex config/catalog files
  had identical pre/post hashes. The unrelated `zapit-strategic-sol` profile
  was not read, mutated, restored, or attributed to coding.
- PARTIAL — implementation-head GitHub CI was successful; report-head checks
  are necessarily pending until this final report-only commit is pushed.

### Criterion 6 — no product change

- PASSED — no direct Local Coding product defect was observed; no product,
  environment, sandbox, catalog driver, systemd, protected service, or
  diagnostic expansion was made.

## Verification

- `uv lock --check && uv sync --frozen --extra dev`: PASSED — lock consistent; 31 packages checked.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen ruff format --check .`: PASSED — 152 files already formatted.
- `uv run --frozen mypy src tests`: PASSED — no issues in 38 source files.
- `uv run --frozen pytest -q tests/test_e2e.py tests/test_packaging.py tests/test_config.py tests/test_app.py tests/test_cache.py tests/test_compiler.py tests/test_pipeline.py tests/test_rehydration.py`: PASSED — 149 passed.
- `uv run --frozen pytest -q -rs`: PASSED — 307 passed; 7 opt-in live tests SKIPPED because `SLAIF_LIVE_TEST=1` was not set. Skips are not claimed as pass.
- `uv build`: PASSED — wheel and source distribution built.
- Wheel/source boundary inspection: PASSED — wheel had 23 members and no test/OAP/helper boundary matches; source distribution had 174 members including repository-support paths.
- `uv run --frozen python -m compileall -q src tests oap/bin`: PASSED.
- `bash -n oap/bin/*.sh`: PASSED.
- `git diff --check`: PASSED.
- Temporary corrected bounded runner: PARTIAL — one initial private harness attempt reached the seed but stopped during sanitized stderr extraction; after that harness-only correction, the bounded rerun passed the seed and four resumes, then stopped truthfully at the no-compaction boundary. No seed failure, product failure, or raw diagnostic was retained.
- `gh pr view 6 --repo ulfe-lmi/slaif-local-coding`: PASSED — implementation head `118f607acaa43f70d2b9fd9a413bd75a150e03cf`, required `test` check SUCCESS, PR OPEN/non-draft/CLEAN at drafting.

## Live model/service evidence

- Candidate route: disposable adapter on loopback port `18031`; health/readiness `200/200`, then stopped and cleaned up.
- Protected upstream: private Qwen/vLLM service on port `18020`; bounded authenticated health/models `200/200` before and after, same PID/start state, and unchanged protected files.
- Codex-under-test: `0.149.0`; persistent disposable `CODEX_HOME`; seed/resume global yolo flag placed before `exec`; no raw prompt, response, source, image, tool output, or credential is reported.
- Vision discovery: current protected catalog reported zero image-capable models and no relevant listener on port `18021`; no vision capability or pre-existing image proxy is claimed.

## GitHub CI / required checks

- Implementation-head check: CI `test` — SUCCESS at `118f607acaa43f70d2b9fd9a413bd75a150e03cf`.
- All required checks at report drafting: YES for the implementation head.
- Report-head checks may be pending immediately after publication; strategy verifies them independently.

## Local setup/dependencies

- Existing Python 3.12 repository environment with frozen `uv` synchronization.
- One private temporary adapter candidate, disposable persistent Codex home,
  synthetic repository, 24,000-context catalog, and private cache were used;
  all were removed after the bounded run.
- No package, lockfile, sudo, persistent unit, daemon reload, model, key,
  network, gateway, or profile write was performed.

## Documentation

- No product documentation update was required because no adapter behavior or
  contract changed. The immutable order and report record the bounded result.

## Safety/scope confirmations

- Unrelated repository files: NO.
- Secrets, raw prompts, source, images, tool output, model text, credentials,
  and customer data: NOT exposed, logged, or committed.
- Protected `18020`/Qwen/vLLM state changed by coding: NO.
- Protected OAP/Qwen profiles changed by coding: NO.
- Extra objective PR: NO; coding merge/auto-merge: NO.
- Active/order edited by coding: NO; exact strategic bytes committed unchanged.
- Report commit report-only: YES.

## Known limitations/blockers

- Actual Codex-native compaction, reduced history, root-absent rehydration,
  post-compaction sentinel preservation, and compiler-attempt suppression
  remain unproven because the four successful resume budget ended with roots
  still observed on every request.
- The initial disposable harness attempt failed after the seed while reading
  a sanitized stream helper; the corrected harness rerun is the evidence used
  for the bounded acceptance result. This did not fail the seed and did not
  mutate durable code or protected state.
- This report makes no production, gateway, cutover, generic compaction-
  provider, or vision-readiness claim.

## Recommended strategic follow-up

Review the truthful bounded external compaction limitation and decide whether
strategy should issue a later continuation with a separately justified trigger
or leave objective 004 open. Coding does not choose the next objective or
claim compaction completeness.

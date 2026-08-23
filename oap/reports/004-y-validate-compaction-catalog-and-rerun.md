# OAP Coding-Agent Report — 004-y

## Work order

- Identifier: `004-y`; order path: `oap/orders/004-y-validate-compaction-catalog-and-rerun.md`; numeric objective: `004`.
- PR mode: `AMENDED_EXISTING_PR`.

## Status

PARTIAL

## Executive summary

Updated the completeness record for the strategically accepted 004-x temporary
systemd candidate proof from objective 004 `60%` / branch `~83%` to `80%` /
`~87%`. Offline Codex 0.149.0 catalog checks isolated the only compaction-
specific fixture delta to `context_window`, `max_context_window`, and the added
`auto_compact_token_limit` field. A disposable context-window-only correction
removed that field, and one persistent non-ephemeral global-yolo seed then
completed through the candidate with exact delegated-dependency acquisition and
the hidden sentinel.

The disposable runner failed at its first post-seed metrics read because it
used the wrong sanitized dataclass attribute name (`roots` instead of
`root_observations`). The candidate was stopped and its temporary session was
deleted. Consequently zero resumes and no Codex-native compaction or
post-compaction rehydration turn ran. No Local Coding production code changed.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`; PR: [#6](https://github.com/ulfe-lmi/slaif-local-coding/pull/6); state: OPEN, non-draft, MERGEABLE.
- Base/head: `main` / `oap/004-real-codex-governed-e2e`.
- Starting remote SHA: `6fb3a35e8e2f2cb8b6c2e56030033cc33da71efd`.
- Implementation head SHA: `d122422a334dd2a1d6785452412e22c29913696c`.
- Report publication commit: SELF.
- Implementation commits pushed before report: `d122422a334dd2a1d6785452412e22c29913696c` (`OAP 004-y: record compaction fixture rerun`).
- New PR this round: NO; amended existing: YES; merge performed: NO.

## Changes and files

- `oap/COMPLETENESS.md`: credits accepted 004-x systemd evidence at objective
  004 `80%` and branch `~87%`; compaction and vision remain explicit gaps.
- `oap/active`: activated strategic pointer `004-y`, committed unchanged.
- `oap/orders/004-y-validate-compaction-catalog-and-rerun.md`: committed
  unchanged from the strategic workspace.
- No adapter, compiler, cache, fixture-driver, dependency, service, model,
  profile, gateway, or host implementation changed.

## Acceptance evidence

### Criterion 1 — completeness record

- PASSED — `oap/COMPLETENESS.md` records objective 004 at `80%` and branch
  readiness at approximately `87%`, credits the accepted systemd candidate,
  and retains actual compaction and vision as remaining gaps.

### Criterion 2 — bounded working/failed fixture delta

- PARTIAL — disposable catalogs were generated from the Codex 0.149.0 bundled
  catalog. The working variant used context `150000` with no auto-compaction
  field; the failed 004-v delta used context/max-context `24000` plus integer
  `auto_compact_token_limit=16000`; the corrected variant used context/max-
  context `24000` with that field absent. The Codex debug resolver returned
  exit `0` for all three, reported the changed field as an integer when
  present, and strict `exec --help` startup validation returned exit `0` for
  all three without a model request. The resolver does not expose a stricter
  relationship diagnostic, so no raw startup text is claimed.
- The corrected context-only seed subsequently passed, while the prior 004-v
  field-bearing seed had failed before any JSONL event or adapter request. This
  bounds the cause to the disposable fixture delta; it does not establish a
  generic Codex compaction-provider claim.

### Criterion 3 — minimal fixture correction

- PARTIAL — the one ordered live attempt used the preferred context-window-only
  disposable correction and did not add a custom compaction implementation or
  weaken `--strict-config`. The existing repository catalog driver already
  emits no `auto_compact_token_limit`; no durable fixture-driver change was
  needed. A dedicated new regression for this compaction-only variant was not
  added because the runner stopped before its resume phase; the existing
  focused E2E/config/packaging suite passed.

### Criterion 4 — corrected persistent seed

- PASSED — temporary candidate health/readiness were HTTP `200/200` on loopback
  18031; the seed used global yolo before `exec`, omitted `--ephemeral`, exited
  `0`, emitted 6 bounded JSONL events, performed exactly 1 intended and 1
  successful delegated dependency read, and passed the hidden sentinel.
- PASSED — the seed stderr was bounded to 39 bytes and represented only by
  fixed class/hash evidence; no raw diagnostic was retained or reported.
- NOT RUN — sanitized per-seed metric deltas were not emitted after the runner
  attribute error, so root/compiler/injection counts are not claimed here.

### Criterion 5 — native compaction and post-compaction rehydration

- NOT RUN — zero same-session resumes ran after the successful seed because the
  runner failed before the first resume. No compaction event, reduced-history
  proof, root-absent request, rehydration hit/injection, post-compaction
  sentinel, or compiler-attempt suppression is claimed.
- NOT RUN — no opaque compacted content or raw history was inspected or
  reported.

### Criterion 6 — privacy, cleanup, and protected-host boundary

- PASSED — the temporary candidate stopped, loopback 18031 was absent after
  teardown, temporary fixture/session/cache/config state was deleted, and the
  candidate log had no upstream credential match.
- PASSED — protected `qwen-serving` remained active/running with the same main
  PID `26028`, start time, unit hash
  `64b3ccd5bdb64da4e3dcabca660fada8155583c96b6bc11de47536e595df5910`, and
  authenticated health/models HTTP `200` results. Only port 18020 remained
  listening; 18021 and 18031 were absent.
- PASSED — the protected model catalog still reported one model and zero
  image-capable models. No current vision endpoint or pre-existing image proxy
  was assumed or changed.
- NOT VERIFIED — a read-only Codex profile inventory differed for
  `zapit-strategic-sol.config.toml` between preflight hash
  `f316932feca55796d39887aee11261503849feb723741d1cabdf6d32b6864e99d8` and
  post-run hash
  `1a292c56ea4178354a7aee668d7582be11f5d88944dddd90fa15e02b451a7fc1`.
  The post-run hash was stable across three probes. Coding did not write,
  restore, or otherwise mutate that profile and does not infer ownership or
  cause; the discrepancy prevents claiming the full Codex-profile invariant.

### Criterion 7 — local and remote gates

- PASSED — required local static, unit, package, privacy, and CI gates listed
  below passed, with live opt-in skips kept distinct from pass.
- PASSED — PR #6 remained the sole open objective PR, with implementation head
  `d122422a334dd2a1d6785452412e22c29913696c` and GitHub CI `test` SUCCESS.

## Verification

- `uv lock --check`: PASSED — lock consistent.
- `uv sync --frozen --extra dev`: PASSED — 31 packages checked.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen ruff format --check .`: PASSED — 150 files formatted.
- `uv run --frozen mypy src tests`: PASSED — no issues in 38 source files.
- `uv run --frozen pytest -q tests/test_e2e.py tests/test_packaging.py tests/test_config.py tests/test_app.py tests/test_cache.py tests/test_compiler.py tests/test_pipeline.py tests/test_rehydration.py`: PASSED — 149 passed.
- `uv run --frozen pytest -q -rs`: PASSED — 307 passed; 7 opt-in live tests
  SKIPPED because `SLAIF_LIVE_TEST=1` was not set. Skips are not claimed as
  pass.
- `uv build`: PASSED — wheel and source distribution built.
- Wheel/sdist boundary inspection: PASSED — wheel had 23 members and zero
  test/OAP/helper boundary violations; source distribution had 172 members,
  including 130 repository-support path matches.
- `uv run --frozen python -m compileall -q src tests oap/bin`: PASSED.
- `bash -n oap/bin/*.sh`: PASSED.
- `git diff --check`: PASSED.
- Offline Codex fixture resolver harness: PASSED for bounded no-model catalog
  resolution and typed-field/hash evidence; strict `exec --help` returned 0 for
  working, failed-delta, and corrected variants.
- Bounded corrected persistent seed/candidate harness: PARTIAL — candidate and
  one seed passed; runner attribute error occurred before resume 1, so the
  ordered compaction phase was not run.
- Changed-path secret/raw-log scan: PASSED — zero matches; no raw payload,
  credential, source, image, tool output, or private diagnostic was retained
  in the report.
- `gh pr checks 6 --repo ulfe-lmi/slaif-local-coding`: PASSED — required CI
  check `test` SUCCESS at the implementation head.

## Live model/service evidence

- Candidate: disposable adapter on loopback 18031; health/readiness `200/200`,
  then stopped and cleaned up.
- Protected upstream: private Qwen/vLLM service on 18020; bounded authenticated
  health/models `200/200` before and after. No protected model request was
  claimed beyond the bounded governed seed path through the candidate.
- Codex-under-test: `0.149.0`; seed normalized argv used
  `<codex> --dangerously-bypass-approvals-and-sandbox exec --json
  --strict-config --disable unified_exec --cd <fixture> --output-last-message
  <last-message> <prompt>`; no raw prompt or output is reported.
- Vision: current protected model catalog had zero image-capable models and no
  listener on 18021; no vision capability or image-proxy behavior is claimed.

## GitHub CI / required checks

- Implementation-head check: CI `test` — SUCCESS at
  `d122422a334dd2a1d6785452412e22c29913696c`.
- All required checks at implementation-head drafting: YES.
- Report-head checks may be pending immediately after publication; strategy
  verifies them independently.

## Local setup/dependencies

- Existing Python 3.12 repository environment with frozen `uv` synchronization.
- One private temporary candidate configuration/cache and one disposable
  persistent Codex home were used; all were removed after the bounded attempt.
- No package, lockfile, sudo, persistent unit, daemon reload, model, key,
  network, gateway, or profile write was performed by coding.

## Documentation

- Updated `oap/COMPLETENESS.md` as explicitly ordered for accepted 004-x proof.
- No product documentation changed because no adapter behavior or contract
  changed.

## Safety/scope confirmations

- Unrelated repository files: NO; implementation diff is transcript plus
  completeness only.
- Secrets/raw prompts/source/tool output/images/model text/customer data:
  NOT exposed, logged, or committed.
- Protected 18020/Qwen/vLLM state changed by coding: NO.
- Protected Codex profile state: full pre/post equality NOT VERIFIED because of
  the unrelated stable `zapit-strategic-sol` hash discrepancy recorded above;
  coding made no profile mutation or repair.
- Required compaction/resume/post-compaction tests: NOT RUN after the seed
  runner failure; no live vision test was run.
- Extra objective PR: NO; coding merge/auto-merge: NO.
- Active/order edited by coding: NO; exact strategic bytes committed unchanged.
- Report commit report-only: YES.

## Known limitations/blockers

- The disposable runner’s sanitized metrics accessor bug prevented the first
  resume after a successful seed and destroyed the only same-session state when
  the bounded lifecycle cleaned up. No second seed or fresh-session substitute
  was run.
- Actual Codex-native compaction, reduced history, root-absent rehydration,
  sentinel-after-compaction, and compiler suppression remain unproven.
- The stable unrelated Codex profile hash discrepancy prevents a complete
  protected-profile unchanged claim; no corrective mutation is authorized.
- This evidence makes no production, gateway, cutover, multi-user, generic
  compaction-provider, or vision-readiness claim.

## Recommended strategic follow-up

Review the partial seed evidence, runner defect, and protected-profile hash
discrepancy. Strategy may decide whether a future continuation may repair the
repository-only runner and perform a new bounded same-session attempt; coding
does not choose that continuation or next objective.

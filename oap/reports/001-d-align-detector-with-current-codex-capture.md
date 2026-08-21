# OAP Coding-Agent Report — 001-d

## Work order

- Identifier: `001-d`
- Order: `oap/orders/001-d-align-detector-with-current-codex-capture.md`
- Numeric objective: `001`
- PR mode: `AMENDED_EXISTING_PR`

## Status

PARTIAL

## Executive summary

Amended objective-001 PR #2 with a stricter, unit-tested safe minimizer and an
honest provenance correction, but did not add the ordered two-position detector.
A fresh disposable Codex CLI 0.149.0 run varied again: exactly one synthetic
project marker occurred, in a top-level user/`input_text` item; top-level
`instructions` contained no AGENTS label, project phrase, project delimiter, or
synthetic instruction rule. The minimizer failed closed and wrote no fixture.
Per the order, coding did not fabricate pair equivalence or broaden detection.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #2, `https://github.com/ulfe-lmi/slaif-local-coding/pull/2`, OPEN and non-draft
- Base/head: `main` / `oap/001-agents-observation-manifest`
- Starting remote SHA: `434c97a3b5475606ed2d4fb3d85a6038afbd1fcf`
- Implementation head SHA: 64339aec47a4e91986d8827c3c7da39d8fe06855
- Report publication commit: SELF
- Implementation commits pushed before report: `64339aec47a4e91986d8827c3c7da39d8fe06855`
- New PR this round: NO; amended existing PR: YES; merge performed: NO
- Auto-merge enabled: NO

## Changes and files

- `tests/helpers/capture_codex_project_envelope.py` now searches the captured
  request in memory, requires exactly one top-level-instructions envelope and one
  top-level user/`input_text` envelope, requires equal labels and exact inner
  bytes, recognizes only the bounded environment-context tail, maps the random
  disposable directory to `repo`, and emits only a deterministic synthetic
  minimized structure plus safe count/hash/length/equality facts. Unsupported,
  missing, relocated, duplicate, or mismatched pairs fail with structural facts.
- `tests/test_capture_helper.py` exercises successful synthetic minimization and
  fail-closed missing, duplicate, relocated, and mismatched cases, and proves
  unrelated tools, metadata, request text, model slug, and host label are absent.
- Fixture, README, and adapter documentation relabel the developer-item fixture
  synthetic-only, correct the immutable `001-a` provenance claim, record both
  failed reproductions, and state that unsupported wire shapes fail conservatively.
- The detector and observation contracts remain byte-for-byte unchanged from
  `001-c`; no unsupported current-Codex rule was introduced.
- The exact strategic `001-d` order and active selector were committed unchanged.

## Acceptance evidence

### Criterion A — fresh capture and minimization

- PARTIAL: a new disposable Codex CLI 0.149.0 custom-provider request reached the
  loopback fake Responses endpoint and completed, but did not reproduce the ordered
  pair. Sanitized result: one marker occurrence at `$.input[1].content[0].text`,
  parent role `user`, item type `input_text`; zero marker occurrences in top-level
  instructions. The instructions field was a string but contained no AGENTS label,
  project phrase, open delimiter, or exact synthetic instruction rule. No raw
  request was written or printed, and no fixture was emitted.
- PASSED: synthetic raw-like helper tests prove exact paired label/content handling,
  deterministic privacy mapping, safe output allowlisting, and rejection of
  missing, relocated, duplicate, and mismatched evidence.
- PASSED: provenance docs now state the old developer shape is synthetic-only and
  explicitly correct the historical immutable report claim without rewriting it.

### Criterion B — corroborated detector rule

- BLOCKED: the required fresh empirical prerequisite was not reproduced. The
  detector was therefore not broadened. Instructions-only, user-only, mismatched,
  duplicate, and synthetic paired-current-shape requests all remain no-detect.
- PASSED: exact hashing, deterministic candidate extraction, bounds, privacy,
  request identity, forwarding, and the previously accepted developer/input-file/
  paired-tool supplemental behavior are unchanged and regression-tested.

### Criterion C — tests and live evidence

- PASSED: 137 ordinary tests passed, including all objective-000/001 image, proxy,
  SSE, tool, error, body/depth, evidence, path, span, budget, identity, fallback,
  and new helper/minimizer tests. Five opt-in tests skipped in the ordinary run and
  passed in a separate foreground-candidate invocation.
- PASSED: foreground candidate full accepted live matrix completed five tests for
  health/readiness/models/text, forced/automatic/streaming tools, multi-turn output,
  SSE, one image, and two-image newest retention.
- BLOCKED: the ordered actual-shape paired probe returned HTTP 200 with root delta
  0 and candidate delta 0 because the empirical pair was not established and the
  detector was intentionally unchanged. Instructions-only, user-only, mismatch,
  and duplicate probes each returned HTTP 200 with zero deltas and one forwarding
  request; no retry occurred.

## Verification

- `/tmp/slaif-uv-tool/bin/uv lock --check`: PASSED — 32 packages resolved.
- `/tmp/slaif-uv-tool/bin/uv sync --frozen --extra dev`: PASSED — 31 packages checked.
- `/tmp/slaif-uv-tool/bin/uv run --frozen ruff check .`: PASSED.
- `/tmp/slaif-uv-tool/bin/uv run --frozen ruff format --check .`: PASSED — 60 files.
- `/tmp/slaif-uv-tool/bin/uv run --frozen mypy src tests`: PASSED — 19 source files.
- `/tmp/slaif-uv-tool/bin/uv run --frozen pytest -q`: PASSED — 137 passed; five
  opt-in live tests SKIPPED here and passed separately below.
- `SLAIF_LIVE_TEST=1 /tmp/slaif-uv-tool/bin/uv run --frozen pytest -q tests/test_live.py`:
  PASSED — five passed in 6.49 seconds with the foreground candidate.
- Fresh disposable Codex CLI 0.149.0 helper run: FAILED fixture-equivalence guard
  after safely completing the provider request — sanitized structural divergence
  above; no minimized file emitted.
- Paired/instructions-only/user-only/mismatch/duplicate candidate probes: PARTIAL —
  each HTTP 200; each root/candidate delta 0; the paired +1 criterion was BLOCKED.
- `/tmp/slaif-uv-tool/bin/uv build`: PASSED — sdist and wheel built.
- `python3 -m compileall -q src tests oap/bin`: PASSED.
- `bash -n oap/bin/*.sh`: PASSED.
- `git diff --check 91463ae3199dd06e0448a9422a5e713da8ee92df...HEAD`:
  PASSED at implementation head.
- Changed-content credential/private-key scan: PASSED.

## Live model/service evidence

- Foreground candidate `127.0.0.1:18031` passed the five-test bounded live matrix
  and was stopped afterward (PID 43863). Ports 18021 and 18031 were then free.
- Protected vision vLLM remained active/running at PID 4174 with start timestamp
  `Thu 2026-08-20 23:27:10 CEST`; only `10.8.132.76:18020` listened at report time.
- Before/after hashes matched: vision env
  `affabb5701b67b5fcb7cab2e3ae1835e84e19dc98a7f1eb245cf3e49b76b3b5b`, vision unit
  `fc88870b4f4afee214c25dc9ec544c4178c300bf4d78092a4d12787a955e2e94`, start script
  `8c87e0104b25c9600235a97555c4b0a1d0ea55d34ccb4094af428c8b4501f89f`, Qwen profile
  `18ead58ac440d29ce2e86addf855c24f471021c6050d4da685320a2cf6eb62eb`, coding overlay
  `cc243c7057f00cb15a06a5be63c6d811f8f473e367d521b1b6ea6207c794509a`, and OAP runtime
  env `22fdefd324d631353f1b9fedad3bad1fc75577073794a882ce2dd57bc5794bf1`.

## GitHub CI / required checks

- Implementation head `64339aec47a4e91986d8827c3c7da39d8fe06855`: workflow `CI`, check `test`,
  SUCCESS in 21 seconds (Actions run 32439073113, job 96645982736).
- All required checks green at drafting: YES.
- Report-head checks may be pending after publication; strategy verifies them.

## Local setup/dependencies

- Used `uv 0.12.5` from temporary tooling and the ignored repository `.venv`; no
  dependency or lockfile change. Temporary Codex homes/repositories, loopback
  capture endpoint, and foreground candidate were disposable. No service was
  installed/enabled, no sudo action was taken, and no human setup was requested.

## Documentation

- Updated README, adapter operations, and fixture provenance to distinguish
  synthetic supplemental support from captured evidence, correct the immutable
  historical claim, state both observed divergences, and document conservative
  failure and the observation-only/request-only boundary.
- No universal Codex compatibility, long-session, compiler/ranking/cache,
  acquisition/injection/rehydration, or multi-user production claim was made.

## Safety/scope confirmations

- Unrelated files and every prior order/report were preserved; no production or
  customer data was used.
- Secrets/raw prompts/internal instructions/private source/tool output/images/
  request bodies/credentials/IDs/private URLs/session/account data committed,
  logged, metric-labeled, reported, or persisted: NO.
- Protected 18020/Qwen/vLLM/Codex fixture changed: NO.
- Mode-0777 vision environment file preserved byte-for-byte: YES; not remediated.
- Firewall, VPN, key files, systemd units/services, model/checkpoint/patches/Qwen
  venv, launch flags, bindings, active Codex profiles/login/catalog/sessions/
  compaction, and OAP wrapper changed: NO.
- Required tests skipped/not run: NONE after the separate live invocation. The
  paired +1 empirical acceptance criterion is BLOCKED, not reported as skipped.
- Scope deviation: NONE; fail-closed partial path was explicitly ordered.
- Extra objective PR: NO; coding merge: NO; auto-merge: NO.
- Active/order edited by coding: NO; report commit report-only: YES by publication
  procedure and remote verification.

## Known limitations/blockers

- Fresh Codex CLI 0.149.0 custom-provider captures have now produced two different
  sanitized structures across consecutive rounds. This run did not reproduce the
  ordered instructions+user pair, so no fresh actual-shape fixture or supported
  detector rule exists. The retained developer envelope is synthetic-only.
- Detection remains observation-only and request-local, with no compiler, semantic
  ranking, cache, persistence, acquisition, injection, replacement, rehydration,
  cross-request state, gateway, deployment, profile switch, or cutover behavior.

## Recommended strategic follow-up

Review the second sanitized capture divergence and independently verify the SELF
parent/report-only commit, report-head CI, and protected fixture state. Strategy
decides whether another controlled capture configuration or a revised objective is
warranted; coding does not infer a new wire contract.

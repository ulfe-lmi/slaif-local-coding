# OAP Coding-Agent Report — 001-b

## Work order

- Identifier: `001-b`
- Order: `oap/orders/001-b-tighten-observation-evidence-boundaries.md`
- Numeric objective: `001`
- PR mode: `AMENDED_EXISTING_PR`

## Status

COMPLETE

## Executive summary

Amended objective-001 PR #2 with explicit Responses/Chat envelope walkers instead
of arbitrary recursive detection; strict role/item/tool/call-ID boundaries; one
shared bounded logical `AGENTS.md` path validator; fixed unsafe-root incomplete
status; sentence-final bare-path punctuation handling with exact UTF-8 spans; and
non-empty candidate evidence enforcement at both evidence budgets. Expanded the
adversarial, boundary, integration-fallback, provenance, and documentation coverage.
No compiler, ranking, cache, persistence, acquisition, injection, filesystem access,
gateway behavior, or protected-host state was added or changed.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #2, `https://github.com/ulfe-lmi/slaif-local-coding/pull/2`, OPEN and non-draft
- Base/head: `main` / `oap/001-agents-observation-manifest`
- Starting remote SHA: `8cb38711981f885af2efe6dd5aa8342a41b6113c`
- Implementation head SHA: 71b59c72c9ee39d952bda8a0a8181f5bb2f68861
- Report publication commit: SELF
- Implementation commits pushed before report: `71b59c72c9ee39d952bda8a0a8181f5bb2f68861`
- New PR this round: NO; amended existing PR: YES; merge performed: NO
- Auto-merge enabled: NO

## Changes and files

- `constitution/detector.py`: replaced recursive scanning with explicit top-level
  Responses input and Chat message walkers. Captured project evidence requires a
  developer/`input_text` Responses item. Input-file evidence requires an explicit
  `input_file` and paired inline text in an allowed content role. Tool evidence
  requires the exact `exec_command` name, conservative single-command read grammar,
  non-empty stable call ID, one call, and one paired output.
- `constitution/detector.py`, `models.py`: added one shared POSIX repository-relative
  `AGENTS.md` normalizer/validator and fixed `invalid_root_path` incomplete status.
  Absolute captured project directories map only to privacy-safe `AGENTS.md`; unsafe
  input/tool paths do not detect. Candidate evidence is schema-validated non-empty.
- `constitution/references.py`: sentence-final bare `SECURITY.md.` and `Makefile.`
  retain only the accepted token span. Evidence budget exhaustion cannot reserve a
  zero-evidence candidate.
- `test_observation.py`, `test_app.py`: added exact strategic reproductions, supported
  envelope acceptance, wrong role/type/parent/name rejection, malformed/duplicate/
  mismatched/unpaired tool cases, unsafe root and candidate classes, byte spans,
  per-candidate/global evidence boundaries, schema invariant, and injected-failure
  unchanged-body/exactly-one-upstream coverage.
- Fixture provenance now includes a safe command/configuration skeleton and minimal
  fake Responses class, while distinguishing the captured Codex 0.149.0 project
  envelope from synthetic input-file/tool supplements.
- README/configuration documentation now states the implemented structural and path
  boundaries. The exact strategic-authored `001-b` order and selector were committed
  unchanged; all prior OAP artifacts remained byte-identical.

## Acceptance evidence

### Criterion A — context-aware envelope traversal

- PASSED: captured developer/`input_text` project envelope detects; identical
  assistant/tool/user, metadata, Chat/arbitrary-nested, and wrong item-type shapes do
  not. Explicit supported `input_file` detects; missing/wrong type, assistant output,
  arbitrary filename dictionaries, and remote-only forms do not.
- PASSED: exact Responses and Chat `exec_command` read pairs detect. Wrong/delete/
  write/custom tool names, compound/write/ambiguous commands, malformed arguments,
  mismatched/duplicate/absent IDs, duplicate outputs, proposed tools, and unpaired
  outputs do not detect.

### Criterion B — safe logical root labels

- PASSED: safe `./services//api/AGENTS.md` normalizes to
  `services/api/AGENTS.md`; captured absolute project directory maps only to
  `AGENTS.md`.
- PASSED: traversal, POSIX/Windows/UNC absolute, URL/scheme, percent/query/fragment,
  control, wrong basename/case, directory-only, and overlength input labels reject.
  Project-directory and read-command unsafe cases use the same validator; rejected
  evidenced root paths expose only fixed `invalid_root_path` state.

### Criterion C — candidate and evidence correctness

- PASSED: sentence-final `SECURITY.md.` and `Makefile.` enumerate without punctuation;
  half-open byte spans map exactly to `SECURITY.md` and `Makefile`, including a prior
  multibyte Unicode prefix.
- PASSED: structured Markdown/reference/backtick/quote invalid URL, absolute,
  Windows/UNC, traversal, NUL/control, percent, query, directory, unsupported, and
  overlength tokens each assert one exact fixed rejection reason/count. Existing
  duplicate ordering, Unicode/newline hashes, fragments, and stable serialization
  remain covered.
- PASSED: exact `max_evidence_per_candidate` and `max_total_evidence` boundaries mark
  incomplete, retain only permitted evidence, and never create empty evidence. The
  Pydantic contract independently rejects an empty evidence tuple.

### Criterion D — total/fallback integration

- PASSED: expected malformed arguments and unsupported structures no-detect without
  exception. The narrow parsers precede a documented last-resort observation fallback.
- PASSED: deliberate injected observation failure emits only fixed `parsing_error`,
  forwards the byte-identical body exactly once, makes no extra call, and does not
  bypass earlier route/image processing.

### Criterion E — provenance/documentation/scope

- PASSED: provenance documents disposable synthetic topology, fake endpoint response
  class, placeholder-only CLI/provider skeleton, minimization, and captured-versus-
  synthetic boundaries. README/config docs match explicit implemented positions.
- PASSED: implementation remains route-scoped, request-only, CPU-only, bounded, and
  observation-only with no later-objective behavior.

## Verification

- `uv lock --check`: PASSED — resolved 32 locked packages.
- `uv sync --frozen --extra dev`: PASSED — checked 31 installed packages.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen ruff format --check .`: PASSED — 54 files formatted.
- `uv run --frozen mypy src tests`: PASSED — 17 source files, no issues.
- `uv run --frozen pytest -q`: PASSED — 115 passed; five opt-in live tests SKIPPED in
  the ordinary invocation and all five passed separately below.
- `SLAIF_LIVE_TEST=1 uv run --frozen pytest -q tests/test_live.py`: PASSED — five
  passed in the final post-change run in 6.10 seconds.
- Synthetic project-observation live metric delta: PASSED — HTTP 200, root +1,
  candidate +1. An initial helper invocation was FAILED because it queried an
  incorrect local metric name; the adapter request itself returned HTTP 200. The
  corrected fixed-name probe passed exactly.
- `uv build`: PASSED — sdist and wheel built.
- `python3 -m compileall -q src tests oap/bin`: PASSED.
- `bash -n oap/bin/*.sh`: PASSED.
- `git diff --check 91463ae3199dd06e0448a9422a5e713da8ee92df...HEAD`:
  PASSED at implementation head.
- Changed-content credential/private-path scan and prior OAP transcript diff check:
  PASSED.

## Live model/service evidence

- Foreground candidate `127.0.0.1:18031`: final health/readiness, proxied health/models,
  ordinary text, forced/automatic/streaming tool calls, multi-turn function output,
  SSE, one-image, two-image newest retention, and metrics matrix passed; candidate was
  stopped afterward.
- The synthetic project envelope returned HTTP 200 and exact +1 root/+1 candidate
  safe metric deltas. Supplemental input-file provider compatibility was not newly
  claimed; its adapter semantics are covered by fake-upstream tests.
- Protected vision vLLM stayed active/running at PID 4174 with start timestamp
  `Thu 2026-08-20 23:27:10 CEST`; only `10.8.132.76:18020` listened after testing and
  ports 18021/18031 were free.
- Required before/after hashes matched: vision env
  `affabb5701b67b5fcb7cab2e3ae1835e84e19dc98a7f1eb245cf3e49b76b3b5b`, vision unit
  `fc88870b4f4afee214c25dc9ec544c4178c300bf4d78092a4d12787a955e2e94`, start script
  `8c87e0104b25c9600235a97555c4b0a1d0ea55d34ccb4094af428c8b4501f89f`, Qwen profile
  `18ead58ac440d29ce2e86addf855c24f471021c6050d4da685320a2cf6eb62eb`, coding overlay
  `cc243c7057f00cb15a06a5be63c6d811f8f473e367d521b1b6ea6207c794509a`, and OAP runtime
  env `22fdefd324d631353f1b9fedad3bad1fc75577073794a882ce2dd57bc5794bf1`.

## GitHub CI / required checks

- Implementation head `71b59c72c9ee39d952bda8a0a8181f5bb2f68861`: workflow `CI`, check `test`,
  SUCCESS in 18 seconds (Actions run 32437014407).
- All required checks green at drafting: YES.
- Report-head checks may be pending after publication; strategy verifies them.

## Local setup/dependencies

- Used `uv 0.12.5` from temporary tooling and the ignored repository `.venv`; no
  dependency or lockfile change. Temporary foreground adapter was stopped. No service
  was installed/enabled, no sudo action was taken, and no protected fixture changed.

## Documentation

- Updated README, adapter configuration documentation, and fixture provenance with
  exact parent/role/type/tool/path/budget/fallback boundaries and limitations.
- Normative architecture was not changed; no conflict required strategic resolution.

## Safety/scope confirmations

- Unrelated files and all prior orders/reports preserved; no production/customer data.
- Secrets/raw prompts/private source/tool output/images/bodies/credentials committed,
  logged, metric-labeled, or persisted: NO.
- Protected 18020/Qwen/vLLM/Codex fixture changed: NO.
- Mode-0777 vision environment file preserved byte-for-byte: YES; not remediated.
- Firewall, VPN, key files, systemd units/services, model/checkpoint/patches/Qwen venv,
  launch flags, bindings, and active Codex profiles changed: NO.
- Required tests skipped/not run: NONE after separate final live invocation.
- Scope deviation: NONE; no compiler/ranking/cache/acquisition/injection/gateway/cutover.
- Extra objective PR: NO; coding merge: NO; auto-merge: NO.
- Active/order edited by coding: NO; report commit report-only: YES by publication
  procedure and remote verification.

## Known limitations/blockers

- Detection intentionally supports only documented current/synthetic structures;
  unsupported future provider shapes no-detect rather than guessing.
- Only the project envelope derives from the disposable Codex 0.149.0 capture;
  input-file and tool fixtures remain synthetic supplements.
- Observation remains ephemeral and provides no compilation, semantic ranking, cache,
  acquisition, injection, or rehydration. No blocker remains within order `001-b`.

## Recommended strategic follow-up

Independently verify the SELF parent/report-only commit, report-head CI, protected
fixture state, and exact detector/path/extractor boundaries before acceptance.

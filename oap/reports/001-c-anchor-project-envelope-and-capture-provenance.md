# OAP Coding-Agent Report — 001-c

## Work order

- Identifier: `001-c`
- Order: `oap/orders/001-c-anchor-project-envelope-and-capture-provenance.md`
- Numeric objective: `001`
- PR mode: `AMENDED_EXISTING_PR`

## Status

PARTIAL

## Executive summary

Amended objective-001 PR #2 with complete project-envelope matching, explicit
terminal-newline and exact-content semantics, adversarial suffix/delimiter/hash
tests, and a disposable executable Codex capture helper with a fully specified
custom Responses provider, synthetic model catalog, fake SSE completion, and
fail-closed minimization. Parser, cumulative local tests, bounded live adapter
tests, suffix live evidence, and CI passed. A fresh sanitized Codex 0.149.0 capture
did not reproduce the fixture's developer-item parent/role: the marker occurred in
top-level instructions and a user input item. The helper correctly refused to
rewrite the role or publish a fixture, so the requested developer-item provenance
remains unresolved.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #2, `https://github.com/ulfe-lmi/slaif-local-coding/pull/2`, OPEN and non-draft
- Base/head: `main` / `oap/001-agents-observation-manifest`
- Starting remote SHA: `d12d51dabaa17192a62c99994daa4ea8f2724688`
- Implementation head SHA: ddbc096c212ada5e58df2d71ad34ddc2a5a37c3c
- Report publication commit: SELF
- Implementation commits pushed before report: `ddbc096c212ada5e58df2d71ad34ddc2a5a37c3c`
- New PR this round: NO; amended existing PR: YES; merge performed: NO
- Auto-merge enabled: NO

## Changes and files

- `constitution/detector.py` now requires a full project-envelope match. It accepts
  no terminal newline, one LF, or one CRLF after the closing delimiter and rejects
  all other prefix/suffix/concatenated/ambiguous closing-tag forms.
- The newline immediately before `</INSTRUCTIONS>` is envelope syntax, not observed
  content. Additional content newlines, LF versus CRLF, trailing whitespace,
  Unicode, UTF-8 byte length, and SHA-256 remain exact and unnormalized.
- `test_observation.py` adds accepted fixture, terminal-newline, prefix/suffix,
  concatenation, malformed delimiter, closing-tag-text, and exact hash/length tests.
  All prior parent/role/type/path/tool/reference/budget regressions remain intact.
- `capture_codex_project_envelope.py` creates a temporary Codex home and committed
  synthetic Git repository; obtains a one-model catalog from bundled model metadata;
  invokes Codex with a custom loopback Responses provider; returns one terminal
  `response.completed` SSE event; retains only the exact developer project item;
  and refuses missing, relocated, or duplicate markers.
- Fixture and adapter documentation specify the exact grammar, configuration,
  throwaway credential mapping, streaming response, minimization allowlist, and
  sanitized reproduction limitation. The exact `001-c` order and selector were
  committed unchanged; all prior OAP artifacts remain immutable.

## Acceptance evidence

### Criterion A — complete-envelope contract

- PASSED: the captured fixture exact envelope and documented no-newline/LF/CRLF
  terminal policy detect.
- PASSED: non-whitespace prefix, same-line suffix, next-line suffix, blank-line plus
  suffix, concatenated envelopes, missing/mismatched/open close, and embedded closing
  delimiter no-detect.
- PASSED: LF, CRLF, content trailing newline/space, and Unicode retain exact UTF-8
  byte length and SHA-256. Developer role, `input_text`, top-level Responses parent,
  and path requirements remain unchanged.
- PASSED: live accepted envelope returned HTTP 200 with root delta +1 and candidate
  delta +2. The exact strategic suffix reproducer returned HTTP 200 with root delta
  0 and candidate delta 0, preserving normal forwarding.

### Criterion B — reproducible safe capture provenance

- PASSED: executable helper and documentation specify `codex-cli 0.149.0`, synthetic
  model `synthetic-capture-model`, provider `synthetic_capture`, ephemeral loopback
  base URL, `wire_api="responses"`, `env_key="SLAIF_CAPTURE_KEY"`, throwaway value,
  temporary model catalog/home/repository, `--ephemeral`, `--ignore-user-config`,
  `-C`, streaming requirement, terminal SSE event, and minimization/discard rules.
- PARTIAL: a new disposable run safely reached the fake endpoint and completed the
  CLI, but sanitized structure placed the project marker in top-level instructions
  and a user/`input_text` item rather than the fixture's developer item. No raw body
  was printed or written. The helper refused output instead of relabeling evidence.
  Therefore the existing developer-item fixture's capture provenance was not
  independently reproduced.

### Criterion C — cumulative compatibility and scope

- PASSED: 132 ordinary tests passed, including all objective-000 and objective-001
  adversarial/boundary/fixture regressions; all five opt-in live tests passed in the
  separate foreground-candidate run.
- PASSED: no compiler, ranking, cache, persistence, acquisition, injection,
  cross-request state, gateway, deployment, cutover, or protected-host mutation.

## Verification

- `/tmp/slaif-uv-tool/bin/uv lock --check`: PASSED — 32 packages resolved.
- `/tmp/slaif-uv-tool/bin/uv sync --frozen --extra dev`: PASSED — 31 packages checked.
- `/tmp/slaif-uv-tool/bin/uv run --frozen ruff check .`: PASSED.
- `/tmp/slaif-uv-tool/bin/uv run --frozen ruff format --check .`: PASSED — 57 files.
- `/tmp/slaif-uv-tool/bin/uv run --frozen mypy src tests`: PASSED — 18 source files.
- `/tmp/slaif-uv-tool/bin/uv run --frozen pytest -q`: PASSED — 132 passed; five
  opt-in live tests SKIPPED here and passed separately below.
- `SLAIF_LIVE_TEST=1 ... pytest -q tests/test_live.py` before candidate start:
  FAILED — five connection-refused failures because port 18031 was correctly free.
- `SLAIF_LIVE_TEST=1 ... pytest -q tests/test_live.py` with foreground candidate:
  PASSED — five passed in 6.09 seconds.
- Disposable `codex-cli 0.149.0` capture helper: FAILED its fixture-equivalence
  guard after the fake request completed — sanitized parent/role divergence above;
  no output fixture written.
- Accepted/suffix project-envelope HTTP metric probe: PASSED — accepted 200,
  +1 root/+2 candidates; suffix 200, +0 root/+0 candidates.
- `/tmp/slaif-uv-tool/bin/uv build`: PASSED — sdist and wheel built.
- `python3 -m compileall -q src tests oap/bin`: PASSED.
- `bash -n oap/bin/*.sh`: PASSED.
- `git diff --check 91463ae3199dd06e0448a9422a5e713da8ee92df...HEAD`:
  PASSED at implementation head.
- Changed-content credential/private-key scan: PASSED.

## Live model/service evidence

- Foreground candidate `127.0.0.1:18031`: health/readiness, proxied health/models,
  text, forced/automatic/streaming tools, multi-turn function output, SSE, one-image,
  and two-image newest-retention tests passed. Candidate PID 39633 was stopped.
- Protected vision vLLM remained active/running at PID 4174 with start timestamp
  `Thu 2026-08-20 23:27:10 CEST`; final listener state contains only
  `10.8.132.76:18020`, with 18021/18031 free.
- Before/after hashes matched: vision env
  `affabb5701b67b5fcb7cab2e3ae1835e84e19dc98a7f1eb245cf3e49b76b3b5b`, vision unit
  `fc88870b4f4afee214c25dc9ec544c4178c300bf4d78092a4d12787a955e2e94`, start script
  `8c87e0104b25c9600235a97555c4b0a1d0ea55d34ccb4094af428c8b4501f89f`, Qwen profile
  `18ead58ac440d29ce2e86addf855c24f471021c6050d4da685320a2cf6eb62eb`, coding overlay
  `cc243c7057f00cb15a06a5be63c6d811f8f473e367d521b1b6ea6207c794509a`, and OAP runtime
  env `22fdefd324d631353f1b9fedad3bad1fc75577073794a882ce2dd57bc5794bf1`.

## GitHub CI / required checks

- Implementation head `ddbc096c212ada5e58df2d71ad34ddc2a5a37c3c`: workflow `CI`, check `test`,
  SUCCESS in 19 seconds (Actions run 32438075789).
- All required checks green at drafting: YES.
- Report-head checks may be pending after publication; strategy verifies them.

## Local setup/dependencies

- Used `uv 0.12.5` from temporary tooling and the ignored repository `.venv`; no
  dependency or lockfile change. Temporary capture homes/repositories and foreground
  candidate were disposable. No service was installed/enabled and no sudo action was
  taken.

## Documentation

- Updated adapter configuration and fixture provenance with exact envelope/newline/
  hash behavior, complete temporary custom-provider/model/fake-response skeleton,
  minimization allowlist, synthetic-supplement labels, and the sanitized rerun gap.
- Normative architecture was unchanged; the detector contract remains the accepted
  developer-item contract required by the order.

## Safety/scope confirmations

- Unrelated files and every prior order/report preserved; no production/customer data.
- Secrets/raw prompts/private source/tool output/images/bodies/credentials committed,
  logged, metric-labeled, or persisted: NO.
- Protected 18020/Qwen/vLLM/Codex fixture changed: NO.
- Mode-0777 vision environment file preserved byte-for-byte: YES; not remediated.
- Firewall, VPN, key files, systemd units/services, model/checkpoint/patches/Qwen venv,
  launch flags, bindings, and active Codex profiles changed: NO.
- Required tests skipped/not run: NONE after separate final live invocation.
- Scope deviation: NONE; capture provenance criterion remains partial.
- Extra objective PR: NO; coding merge: NO; auto-merge: NO.
- Active/order edited by coding: NO; report commit report-only: YES by publication
  procedure and remote verification.

## Known limitations/blockers

- The existing fixture remains accepted test evidence, but the fresh 0.149.0 custom-
  provider run did not reproduce its developer parent/role. Resolving whether the
  earlier capture used an additional safe configuration input or whether the fixture
  provenance claim must be revised requires strategic review; coding did not weaken
  role detection or fabricate equivalence.
- Detection intentionally supports only the ordered developer project envelope and
  synthetic input-file/tool supplements. It provides no compiler, semantic ranking,
  cache, acquisition, injection, or rehydration.

## Recommended strategic follow-up

Review the sanitized capture-shape divergence and decide whether a further bounded
capture configuration order or a correction to the accepted evidence contract is
required. Independently verify the SELF parent/report-only commit, report-head CI,
and protected fixture state.

# OAP Coding-Agent Report — 001-a

## Work order

- Identifier: `001-a`
- Order: `oap/orders/001-a-agents-observation-and-reference-manifest.md`
- Numeric objective: `001`
- PR mode: `CREATED_NEW_PR`

## Status

COMPLETE

## Executive summary

Implemented route-scoped, request-only observation of evidenced effective
`AGENTS.md` content after image policy and before forwarding. Added versioned typed
context/source/candidate/evidence/completeness contracts; exact UTF-8 hashing;
captured/synthetic Codex 0.149.0 envelope fixtures; conservative project-instruction,
input-file, and paired-tool detectors; deterministic bounded repository-reference
enumeration with stable UTF-8 byte spans; fixed safe overflow/rejection states and
metrics; fake/live compatibility tests; and documentation. Observation does not alter
otherwise untransformed request bytes and introduces no compiler, model call, semantic
ranking, cache, acquisition, persistence, governance injection, or cross-request state.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #2, `https://github.com/ulfe-lmi/slaif-local-coding/pull/2`, OPEN and non-draft
- Base/head: `main` / `oap/001-agents-observation-manifest`
- Starting remote SHA: `91463ae3199dd06e0448a9422a5e713da8ee92df`
- Implementation head SHA: 7ce8fc2a2ae83ba2e51b634e1851b84460782630
- Report publication commit: SELF
- Implementation commits pushed before report: `7ce8fc2a2ae83ba2e51b634e1851b84460782630`
- New PR this round: YES; amended existing PR: NO; merge performed: NO

## Changes and files

- `src/slaif_local_coding/constitution/`: typed immutable observation contracts,
  evidence-based root detection, normalization/rejection policy, deterministic
  reference manifest, and fixed bounded failure states.
- `src/slaif_local_coding/app.py`, `config.py`, and example TOML: explicit route opt-in,
  finite observation limits, post-image/pre-forward integration, and safe fixed-label
  counters/timing without raw content, path, hash, identity, query, or tool labels.
- `tests/fixtures/codex/0.149.0/`: minimized disposable provider-bound project-envelope
  fixture, supplemental input-file/tool fixtures, provenance, limitations, and safe
  refresh procedure.
- `tests/test_observation.py`, `test_app.py`, `test_config.py`: detector false positives,
  exact hashes, evidence ordering/spans, path classes/rejections, every configured
  overflow class, route enablement, identity non-trust, byte fidelity, safe metrics,
  and exactly one upstream request.
- `README.md`, `docs/ADAPTER-CONFIGURATION.md`: implemented scope, exact hashing/path/
  overflow semantics, identity/privacy boundaries, fixture limitations, and explicit
  absence of later compiler/cache/injection behavior.
- Committed strategic-authored `oap/active` and the `001-a` order bytes unchanged.

## Acceptance evidence

### Criterion A — typed observation contracts and identity

- PASSED: versioned immutable models cover request context, root source kind/path/hash/
  byte length/evidence, candidate first-seen order/all retained evidence, completeness,
  fixed incomplete reasons, and fixed rejection counts.
- PASSED: client identity/session headers remain stripped and are not copied into the
  observation context. Tests use explicitly untrusted request-only hints; no cache or
  cross-request state exists and no combined semantic score is defined.

### Criterion B — evidence-based effective AGENTS detection

- PASSED: captured project-instruction, input-file, Responses paired-tool, and Chat
  paired-tool shapes detect exact/nested `AGENTS.md` labels and stable call-ID pairs.
- PASSED: prose mentions, quoted examples, tool descriptions, unpaired output,
  substring filenames, URL filenames, and assistant claims do not detect roots.
- PASSED: LF, CRLF, trailing whitespace, and Unicode exact UTF-8 bytes yield asserted
  byte lengths and SHA-256 values without normalization; duplicate evidence is retained.

### Criterion C — sanitized Codex fixture

- PASSED: `codex-cli 0.149.0` was run with `--ephemeral --ignore-user-config` in a
  disposable synthetic repository against a temporary loopback fake Responses endpoint.
  The capture yielded one synthetic project-instruction envelope. Only minimized
  synthetic structure is committed; authentication, IDs, host paths, internal prompts,
  unrelated tools, and response content were discarded. No active profile was edited.

### Criterion D — deterministic candidate extraction

- PASSED: tests cover inline/reference Markdown, backticks, quotes, normative neighbors,
  nested and `.github` paths, scripts/configs, duplicates, stable first-seen order, all
  evidence, fragment handling, deterministic serialization, and half-open UTF-8 byte
  offsets mapping back to synthetic source.
- PASSED: URL/scheme, absolute POSIX/Windows/UNC, traversal, control/empty, percent/query
  ambiguity, directory/unsupported, and overlength inputs receive fixed safe rejection
  classes/counts. The extractor performs no file, symlink, network, Git, or existence IO.

### Criterion E — bounds and failure behavior

- PASSED: validated limits cover roots, exact source bytes, candidates, evidence per
  candidate, total evidence, and path bytes. Boundary tests assert `complete=false` and
  fixed source/root/candidate/evidence/path reason states on overflow.
- PASSED: observation errors/overflow do not reject or alter the governance-bearing
  request. Existing body/depth parsing and image enforcement remain earlier stages.

### Criterion F — pipeline and compatibility

- PASSED: observation is disabled by default and enabled only by explicit route policy.
  Fake upstream receives exact original bytes for enabled zero/one-image input and
  exactly one request; disabled routes produce no observation work. No compiler/internal
  request or injected/removed governance exists.
- PASSED: cumulative fake and live suites preserve image, errors, tools, usage, headers,
  query, compression, SSE order/incrementality, disconnect, timeout, bounds, health,
  readiness, Responses, and Chat behavior.

### Criterion G/H — observability, documentation, and non-goals

- PASSED: metrics expose only fixed endpoint/route/evidence/status/reason labels, counts,
  and duration. Tests and scans prove synthetic private paths, spoofed identities, raw
  source, hashes, and credential values are absent from runtime metrics/tracked output.
- PASSED: documentation states exact supported evidence/path policies, bounds, privacy,
  request-only identity, fixture limits/update procedure, original-request preservation,
  experimental scope, and absence of objectives 002–006 behavior.

## Verification

- `uv lock --check`: PASSED — resolved 32 locked packages.
- `uv sync --frozen --extra dev`: PASSED — checked 31 installed packages.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen ruff format --check .`: PASSED — 52 files formatted.
- `uv run --frozen mypy src tests`: PASSED — 17 source files, no issues.
- `uv run --frozen pytest -q`: PASSED — 61 passed; five opt-in live tests SKIPPED in
  the ordinary invocation and then all five passed separately below.
- `SLAIF_LIVE_TEST=1 uv run --frozen pytest -q tests/test_live.py`: PASSED — five
  passed in 6.55 seconds.
- Synthetic observation-enabled live request/metric delta: PASSED — HTTP 200, root
  counter +1, candidate counter +1.
- `uv build`: PASSED — sdist and wheel built.
- `python3 -m compileall -q src tests oap/bin`: PASSED.
- `bash -n oap/bin/*.sh`: PASSED.
- `git diff --check 91463ae3199dd06e0448a9422a5e713da8ee92df`: PASSED.
- Changed-content private-capture-path and tracked live-credential-value scans: PASSED.

## Live model/service evidence

- Candidate: foreground `127.0.0.1:18031`; the accepted health/readiness, proxied
  health/models, text, forced/automatic/streaming tools, multi-turn function output,
  SSE completion, one-image, two-image newest retention, metrics, and Chat matrix passed.
  The candidate was stopped and no 18031 listener remained.
- One synthetic project-instruction request returned HTTP 200 and safe +1 root/+1
  candidate deltas. A supplemental input-file request produced the expected observation
  deltas but upstream rejected that unsupported provider input shape with HTTP 400; it
  is not claimed as provider-compatible. Fake-upstream tests are authoritative for exact
  byte/count/no-extra-call behavior.
- Protected vision vLLM remained active/running at PID 4174, start timestamp
  `Thu 2026-08-20 23:27:10 CEST`, with model `qwen3.8-27b` and one-image cap. Only
  `10.8.132.76:18020` listened; ports 18021/18031 were free after testing.
- Required hashes matched before and after: vision env
  `affabb5701b67b5fcb7cab2e3ae1835e84e19dc98a7f1eb245cf3e49b76b3b5b`, vision unit
  `fc88870b4f4afee214c25dc9ec544c4178c300bf4d78092a4d12787a955e2e94`, start script
  `8c87e0104b25c9600235a97555c4b0a1d0ea55d34ccb4094af428c8b4501f89f`, Qwen profile
  `18ead58ac440d29ce2e86addf855c24f471021c6050d4da685320a2cf6eb62eb`, coding overlay
  `cc243c7057f00cb15a06a5be63c6d811f8f473e367d521b1b6ea6207c794509a`, and OAP runtime
  env `22fdefd324d631353f1b9fedad3bad1fc75577073794a882ce2dd57bc5794bf1`.

## GitHub CI / required checks

- Implementation head `7ce8fc2a2ae83ba2e51b634e1851b84460782630`: workflow `CI`, check `test`,
  SUCCESS in 20 seconds (Actions run 32435747519).
- All required checks green at drafting: YES.
- Report-head checks may be pending after publication; strategy verifies them.

## Local setup/dependencies

- Reused temporary `uv 0.12.5`; application/test dependencies remain in ignored
  repo-local `.venv` and committed `uv.lock`. No dependency or lockfile change.
- Used only foreground repo candidate and temporary loopback fixture capture server;
  both stopped. No service installed/enabled and no sudo action taken.

## Documentation

- Updated README, example configuration, adapter operations documentation, and fixture
  provenance with exact implemented observation/extraction/privacy/limit contracts.
- Normative architecture was not changed; no conflict required strategic resolution.

## Safety/scope confirmations

- Unrelated files preserved; no production/customer data used.
- Secrets/raw prompts/private source/tool output/customer images committed, logged,
  metric-labeled, or persisted: NO.
- Protected 18020/Qwen/vLLM/Codex fixture changed: NO.
- Mode-0777 vision environment file preserved byte-for-byte: YES; not remediated.
- Firewall, VPN, key files, systemd units/services, model/checkpoint/patches/Qwen venv,
  launch flags, network bindings, and active Codex profiles changed: NO.
- Required tests skipped/not run: NONE after separate live invocation.
- Scope deviation: NONE; no compiler/model ranking/cache/acquisition/injection/gateway/
  cutover work and no long-session/compaction compliance claim.
- Extra objective PR: NO; coding merge: NO; auto-merge: NO.
- Active/order edited by coding: NO; report commit report-only: YES by publication
  procedure and remote verification.

## Known limitations/blockers

- Detection is conservative and version/shape-specific; unsupported or ambiguous future
  envelopes remain undetected rather than guessed.
- Input-file and paired-tool committed fixtures are synthetic supplements; only the
  project-instruction fixture derives from the disposable Codex 0.149.0 capture.
- Observation is ephemeral and intentionally provides no compilation, semantic ranking,
  cache reuse, dependency acquisition, injection, or compaction rehydration.
- No blocker remains within order `001-a`.

## Recommended strategic follow-up

Independently verify the SELF parent/report-only commit, report-head CI, protected
fixture state, conservative detector/extractor boundaries, and objective acceptance.

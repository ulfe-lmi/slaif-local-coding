# OAP 015-a Report — Repair upstream diagnostics and compiler truncation; qualify private RC8

## Scope and identity

- Repository: `ulfe-lmi/slaif-local-coding`
- Order: `oap/orders/015-a-upstream-diagnostics-compiler-truncation-rc8.md`
  (byte-exact; sha256
  `43003708ea28f80e939d3c51bbbb03b58eb21fe378f1701c38df9c2695b7ff49`)
- PR: **#22** — https://github.com/ulfe-lmi/slaif-local-coding/pull/22
  (non-draft; base `main` @
  `87ed2cea43a0a8706efe485b9b625dfda7cf75aa`; branch
  `oap/015-upstream-diagnostics-compiler-truncation-rc8`; coding did not and
  does not merge; auto-merge not enabled)
- Implementation commits (oldest → newest):
  1. `1294d2493d232825e50cfb83c280c8a0697e1851` — Objective 015-a activation
     transcript (byte-exact order + `oap/active=015-a`)
  2. `c05663021cb570d5180330d85be1d09859206eeb` — P01/P02 implementation,
     tests, config, docs, release machinery, RC7 archive
  3. `718fff301bed0a5ba93b29196cde4d0bcc5d711a` — image source commit `S`
     (freeze; pre-freeze provenance manifest; manifest-only diff)
  4. `78822ca8f8c58fbc959495d37bdff32e525eb945` — post-freeze derived
     metadata only (RC8 record + handoff, `rc_published` manifest, testing
     ledger 006). **Exact final implementation SHA (this commit).**

## External-review adjudication (CODE-DEFECTS.md)

`CODE-DEFECTS.md` was **external human review input**. It is not a
repository file and is not part of benchmark-harness archive 001 or 002
(both immutable and untouched by this round). No copy was preserved in the
repository. Strategy independently verified both findings against exact
`origin/main` (`87ed2cea…`) source before activation; coding reproduced the
pre-fix behaviors mechanically against the base before repairing:

- **P01 (confirmed):** the upstream HTTP-error path preserved only the
  status + allowlisted headers, never read the response body, and left no
  private bounded cause classification — only the generic public error and
  transport-level failure counters existed. This is an observability
  defect; it does **not** prove Local Coding caused any RC7 rejection.
- **P02 (confirmed):** the compiler parsed `choices[0].message.content`
  with exactly one choice but never read `choices[0].finish_reason`; a
  length-finished incomplete body therefore became `INVALID_JSON` and the
  retry repeated the identical (known-insufficient) `max_tokens`. This is a
  truncation-classification and retry-policy defect; it does **not**
  establish that P02 caused Minesweeper coding errors or a later
  image-limit failure.

This order repaired and qualified these two product defects. It makes no
claim that Local Coding caused the rejected requests or any task mistakes,
and no causation claim to archive 002 (failed/incomplete qualification
context) is made or implied.

## Workstream A — P01 bounded private classification (implemented)

- New module `src/slaif_local_coding/upstream_diagnostics.py`: closed enum
  `authentication | rate_limit | image_count_limit | context_length_limit |
  malformed_input | upstream_5xx | unknown`; pure
  `classify_upstream_error(status, body|None)`; bounded structured
  allowlist (top-level error object; fixed `code`/`type`/`param`/`message`
  locations); raw strings examined only by a fixed matcher table and never
  returned, logged, persisted, or used as labels; numeric/null/collection/
  unexpected types cannot crash classification.
- `config.py`: validated `upstream_error_diagnostic_max_bytes`
  (default 16384; 1..65536) and `upstream_error_diagnostic_timeout_seconds`
  (default 1.0; >0..5.0), consistently named in schema/templates/docs.
- `app.py`: `_read_bounded_error_diagnostic` — streaming iteration
  retaining only the remaining permitted slice (one oversized chunk cannot
  exceed the allowance), hard time bound via `wait_for`, `CancelledError`
  re-raised, response closed on every path (timeout, cancellation,
  malformed content, read error, bound reached); classification happens
  only for `status >= 400` before close; 401/403/429/5xx are status-derived
  without a body read; all other statuses require allowlisted structured
  or fixed-pattern evidence, else `unknown`.
- New private low-cardinality counter
  `slaif_upstream_http_errors_total{endpoint,route,status_class,reason}` —
  labels are bounded closed values only (no provider text/codes, no
  request-derived identity/path, no exact private URL, no credentials).
- Client contract unchanged: identical generic public `upstream_error`
  body, original status, allowlisted safe headers (`cache-control`,
  `openai-processing-ms`, `retry-after`, `x-request-id`); no upstream body
  or provider text forwarded; success/streaming/transport semantics
  preserved.
- Regressions: `tests/test_upstream_diagnostics.py` (40 tests) — distinct
  expected classes for evidenced image-count/context-length/malformed/
  authentication/rate-limit/5xx; `unknown` for non-JSON, malformed JSON,
  unexpected shapes, unknown/numeric codes, empty and incomplete bodies
  where status does not independently classify; single >16 KiB chunk,
  many-chunk crossings, stalled body, and binary/invalid-UTF-8 data all
  within byte/time bounds with guaranteed close; public body/headers/
  status fidelity; sentinel strings from every fake provider body absent
  from public responses, logs, and metrics/labels; request/status counters
  and transport-failure distinctness unchanged.

## Workstream B — P02 typed truncation and bounded adaptive retry (implemented)

- `constitution/compiler_models.py`: `COMPILER_VERSION = "compiler-v3"`;
  new `FailureReason.OUTPUT_TRUNCATED` (serialized `output_truncated`).
- `constitution/compiler.py`: strict chat-completion envelope (exactly one
  choice, string `finish_reason`, dict `message`, `str|None` content). A
  response with exactly one choice and `finish_reason == "length"` yields
  `OUTPUT_TRUNCATED` **before** content JSON/schema validation; a normally
  completed malformed body remains `INVALID_JSON` (or the precise existing
  schema failure); missing/unsupported structure fails closed under the
  existing invalid-output category, never masquerading as truncation.
- Adaptive retry: on explicit truncation the next attempt uses
  `min(previous_allowance * 2, max_output_tokens_ceiling)`; a known-
  insufficient allowance is never repeated; the loop stops explicitly with
  `OUTPUT_TRUNCATED` once the allowance reaches the ceiling or
  `max_attempts` (per-compilation hard bound) is exhausted.
- `config.py`: validated `max_output_tokens_ceiling` (default 8000;
  128..16000; must be ≥ initial `max_output_tokens`, default 3000 kept).
- Identity binding: compiler version + initial allowance + ceiling bound
  into request deduplication fingerprints, persistent cache keys
  (`constitution/cache.py`), rehydration keys (`constitution/pipeline.py`),
  source-input maps, strict records, config hashes, and tests — old and new
  compilation policies cannot be confused.
- Content-free truncation counter
  `slaif_constitution_compiler_truncations_total` (no labels); metrics
  distinguish attempt, validated success, explicit truncation, completed
  invalid JSON/schema, timeout/transport/status failure, degraded pipeline
  result, cache write/hit, and successful injection.
- No partial/truncated governance index is validated or persisted; the
  direct, tool-free, non-recursive compiler boundary, one global compiler
  slot, prompt/source/privacy bounds, and preserve-original degradation are
  preserved.
- Regressions: `tests/test_compiler_truncation.py` (20 tests) — incomplete
  content + `finish_reason="length"` is `OUTPUT_TRUNCATED` never
  `INVALID_JSON`; malformed JSON + normal completion stays distinct;
  first-attempt truncation at 3000 → second request at 6000 (< 8000
  ceiling) → valid second response compiles and caches; repeated
  truncation never repeats an allowance and never exceeds the configured
  attempts/ceiling, terminating explicitly truncated; initial-allowance-
  equals-ceiling cannot blind-retry; large synthetic governance corpus
  produces every required index field; exactly one cache write after a
  validated compile, subsequent hit unchanged, truncation/invalid/overflow
  produce no cache or rehydration entry; attempt/token/byte/depth/timeout/
  cancellation/concurrency bounds enforced; metrics and pipeline result
  expose truncation, eventual success/cache, degradation, and injection
  with no source/path/identity/content in labels.

## Workstream C — documentation

- `docs/ADAPTER-CONFIGURATION.md`: private error-classification contract
  (bounded byte/time reads, closed reason set, privacy) in "Forwarding,
  errors and metrics"; typed truncation + exact adaptive policy (ceiling,
  attempt scope, metrics, cache identity, degradation) in "Optional
  governance pipeline".
- `ARCHITECTURE-for-agents.md`: two compact normative clauses (P01
  classification boundary; P02 truncation/adaptive-retry contract).
- `docs/HISTORY.md`: RC8 entry — external review motivated the
  independently verified P01/P02 repairs; archive 002 is failed/incomplete
  qualification context (no causation claim); RC7 archived per convention
  and remains immutable.
- `docs/RC-HANDOFF.md`, `docs/RELEASE-ARTIFACT-POLICY.md`, `TESTING.md`:
  RC7→RC8 succession, archived/rejected RC history, ledger 006,
  Gateway-not-required for standalone qualification, benchmark-not-run,
  final-public-release false, cutover false.
- README remains product documentation, not an OAP ledger.
- No scope creep: no CACHE image pruning, image histogram, Codex history
  validation/rewriting, benchmark-driver/task/judge changes, model or vLLM
  changes, or speculative fixes.

## Workstream D — freeze, publication, full qualification

### Freeze identities

- Image source commit `S` = `718fff301bed0a5ba93b29196cde4d0bcc5d711a`
  (manifest-only diff over `c056630…`; no artifact input changes after `S`
  — verified by `scripts/source_input_map.py --ab` and `--ref`).
- Wheel `W` = `eb241dda2e079b29190868108c488edaf98261c84119bfd405070dea98b546b9`
  (byte-identical across CPython 3.12.3 and 3.12.14 clean `git archive`
  builds, the local `uv build` at `S`, and the in-workflow CI rebuild).
- Sdist = `2fce6516d8d4c07fd31e565b975c1bb91e810fb9029c0acc606aa5e2e26b8f21`.
- Dependency lock (uv.lock) sha256 =
  `1237cbd179f71b99984c80f927529549f5e61eb705585ef9cf2ab0fa9e26764a`
  (unchanged; `uv lock --check` green).
- Build environment pins: hatchling 1.32.0, packaging 26.3, pathspec 1.1.1,
  pluggy 1.6.0, tomlkit 0.15.1, trove-classifiers 2026.6.1.19; uv 0.12.5.
- Gateway compatibility authority commit:
  `08ca421bee1ddca62078302b910e8be88cf705be` (unchanged peer).
- RC7 archive: `packaging/releases/0.1.0-rc7/` (record, handoff, manifest
  all byte-identical to the base-commit versions; verified mechanically by
  `test_rc7_archive_is_immutable_and_excluded_from_artifact_inputs`).
  All prior archives (`0.1.0-rc1` … `0.1.0-rc5`, `0.1.0-rc7`) present.
  The RC7 registry identity (`0.1.0-rc7` /
  `sha-ae6271318627703785f42de57d893c9be3b980c9` →
  `sha256:a3782915da58a403fd0f7991c57f9954b07bfb9377e4730715c0fb7398f901db`)
  was last verified resolvable by the order 014-g final-head baseline; this
  round's publisher wrote only the RC8 pair, and this round's CI baseline
  did NOT re-assert the RC7 pair — see the exact blocker under the verdict.

### Pre-publication gates at `S` (local)

- `uv run --frozen pytest -q`: **1500 passed, 27 skipped, 0 failed**
  (3.00 min).
- `uv lock --check`, `ruff check`, `ruff format --check`, `mypy src`,
  `docs_consistency_check.py`: all green.
- `uv build`: wheel = `W`, sdist as above (byte-identical).
- `artifact_policy_check.py --inspect`: ok, 0 violations;
  `--install-smoke`: ok (fresh venv, noneditable, version 0.1.0).
- `rc_record_present_rehearsal.py` (PRE mode at `S`): PASSED (disposable
  clean `git archive` rebuild → wheel == `W`; synthetic record gate set).

### Fresh CI/CodeQL at source head `S` (GitHub, before any registry write)

- CI run `36953785370`
  (https://github.com/ulfe-lmi/slaif-local-coding/actions/runs/36953785370,
  pull_request, head `718fff30…`): **SUCCESS** — `test` SUCCESS (1499
  passed, 28 skipped on the runner; the single delta vs local is the
  host-pinned
  `test_target_semantic_preflight_failure_precedes_protected_selection`,
  honestly SKIPPED on the runner because its pinned target qualification
  dependencies are unavailable there), `gateway-contract` SUCCESS, `docker`
  SUCCESS (15/15 phases, build mode), `docker-published` SUCCESS in
  **prepublication mode** (explicit `NOT RUN (pre-publication: no RC or
  final publication record)`), `operator-session` SUCCESS (19/19 phases).
- CodeQL run `36953783492`
  (https://github.com/ulfe-lmi/slaif-local-coding/actions/runs/36953783492,
  head `718fff30…`): `Analyze (python)` SUCCESS, `Analyze (actions)`
  SUCCESS, aggregate SUCCESS.
- Open code-scanning alerts: **0** (7 historical alerts, all `fixed`/
  `dismissed`).

### Private publication (workflow_dispatch only)

- Publication run `36954165586`
  (https://github.com/ulfe-lmi/slaif-local-coding/actions/runs/36954165586,
  `release-image.yml`, head verified = `718fff30…`,
  2026-10-02T02:07:34Z → 2026-10-02T02:08:11Z, SUCCESS):
  - in-workflow fresh wheel rebuilt and asserted equal to the committed
    manifest wheel `W` (both
    `eb241dda2e079b29190868108c488edaf98261c84119bfd405070dea98b546b9`);
  - authenticated strict registry pre-check: `registry before:
    sha-718fff301bed0a5ba93b29196cde4d0bcc5d711a = verified absent;
    0.1.0-rc8 = verified absent`;
  - both aliases pushed; `registry after:` both present at ONE digest.
- **Digest `D` =
  `sha256:50450f4aa26a4da158dc457e0b80b441c69386c201491c6c0150c25d5916e126`**;
  tags `0.1.0-rc8` and `sha-718fff301bed0a5ba93b29196cde4d0bcc5d711a` both
  resolve to `D`; `published_at` = 2026-10-02T02:08:11Z.
- Local `gh` credential cannot read the private package (fail-closed
  `unauthorized` class, 013-n precedent); registry truth comes from the
  authenticated workflow/CI credentials, as in prior rounds; no new
  credential introduced. Package remains private.

### Pulled-image qualification of the actual `D` (final-head `B`)

- Final-head `docker-published` job (CI run `36955048233`, job
  `110676064121`, published mode) pulled
  `ghcr.io/ulfe-lmi/slaif-local-coding@sha256:50450f4a…` (`D`) **without
  rebuilding** (`pull_preexistence_no_build`: `pulled_before_up: true`) and
  passed ALL 13 phases: `verify_wheel_binding` (in-image wheel = `W`),
  `pull_preexistence_no_build`, `fake_upstream_start`, `adapter_stack_up`
  (image_id matches pull), `in_image_provenance` (noneditable install,
  dependency-lock closure 18/18 pinned, wheel `W`), `bridge_positive_signed`
  (chat 200, SSE 4 frames + terminal, models, tool-roundtrip continuation),
  `bridge_negative_contract` (bad signature 403, missing token 401, replay
  200→409, cross-namespace refused), `config_time_rejection`,
  `fail_closed_readiness` (readyz 503), `image_content_scan` (6485 files,
  0 forbidden), `hardening_and_labels` (full OCI label set incl.
  revision/source/wheel, `linux/amd64`, non-root, read-only rootfs,
  no-new-privileges, cap-drop-all), `teardown_absence_proof`
  (containers/listeners absent on 18031/18033/18034),
  `compose_rendered_validation` — summary PASSED.
- Authenticated read-only registry baseline in the same job (ephemeral
  `packages:read` token): `0.1.0` / `sha-fe334e87…` →
  `sha256:a5debcb2…`; `sha-be3c78b2…` → `sha256:15778b30…`;
  `0.1.0-rc1` / `sha-4d096e40…` → `sha256:2dd889c2…`; `0.1.0-rc2` →
  `sha256:2349400a…`; `0.1.0-rc3` / `sha-307a929f…` → `sha256:41db6fcc…`;
  `0.1.0-rc4` / `sha-601a7f9f…` → `sha256:a4f2014c…`; `0.1.0-rc5` /
  `sha-e04b4a99…` → `sha256:70b450f5…` (ALL historical identities
  unchanged); current pair `0.1.0-rc8` / `sha-718fff30…` → `D`; `package
  visibility -> private`. **The archived RC7 pair is NOT in this
  baseline's historical tuple** — the exact blocker below.

### Focused P01 qualification (controlled, no fabricated history)

- Mandatory fake-upstream proof (controlled providers, distinct sentinels):
  the 40-test `tests/test_upstream_diagnostics.py` suite — all cases map to
  the closed expected classes; unknown/malformed/oversized/stalled/binary
  inputs are bounded and classify `unknown` where status does not
  independently classify; sentinels proven absent from public responses,
  logs, metrics/labels, and persisted artifacts. All pass locally at `S`
  and `B` and in both CI runs.
- No synthetic rejection was injected into the protected live backend and
  no lost RC7 context-BOTH body was fabricated or labeled historical; the
  live backend was exercised only on ordinary authenticated success paths
  (`/health`, `/v1/models`, and the Workstream E arms: 0 upstream
  failures).

### Focused P02 qualification

- Mandatory fake-upstream proof: the 20-test
  `tests/test_compiler_truncation.py` suite — typed truncation before
  content validation, adaptive 3000→6000 below the 8000 ceiling with
  successful second-attempt compile+cache, exhaustion without repeated
  allowances, no partial cache/rehydration entries, corpus coverage, and
  content-free metrics. All pass locally at `S` and `B` and in both CI
  runs.
- Live treatment-delivery proof: Workstream E CACHE and BOTH arms each
  completed a genuine tool-bearing loop against the protected backend with
  1 real compiler call, 1 derived-cache entry, and successful treatment
  delivery (ledger 006).

## Workstream E — standalone genuine-Codex RC8 smoke (no Gateway)

- Testing ledger **006** (`oap/evidence/testing-ledger/006/`: README +
  `real-codex-rc8-qualification.json` + `MANIFEST.sha256`,
  `sha256sum -c` verified; ledgers 001–005 untouched).
- Gate: `scripts/real_codex_rc_qualification.py` (facts schema
  `slaif-real-codex-rc-qualification-v2`), run 2026-10-02 UTC (facts
  created 2026-10-02T02:10:02Z), overall verdict **PASS**.
- Client: Codex CLI **0.149.0**
  (`bbc3341e44c9ead340ed9570c17be936e37870f570751a941699ffd04d672827`) —
  exact pinned binary established on this host; no fallback used.
- Wheel binding `equal` (`W`); topology
  `disposable-codex-home;loopback-adapter;port-18031;existing-backend;
  gateway-ingress-disabled`; model `qwen3.8-27b`; serial arms; all ceilings
  enforced and below limit (arms 4≤4, attempts 1≤2, tool interactions
  1/arm≤8, adapter requests ≤64, compiler calls ≤4, per-attempt 1 MiB /
  600 s, total 5400 s).
- Arms:
  - **VISION** PASS — 1 attempt, exit 0, sentinel 3 bytes, 1 genuine tool
    interaction, adapter 200/500/422 = 2/0/0, upstream failures 0,
    compiler calls 0, cache entries 0, 5 s, failure class `none`.
  - **CACHE** PASS — 1 attempt, exit 0, sentinel 3 bytes, 1 tool
    interaction, adapter 2/0/0, upstream failures 0, compiler calls 1,
    cache entries 1, 34 s, `none` (compiler/cache success + treatment
    delivery evidenced).
  - **BOTH** PASS — 1 attempt, exit 0, sentinel 3 bytes, 1 tool
    interaction, adapter 2/0/0, upstream failures 0, compiler calls 1,
    cache entries 1, 39 s, `none` (treatment delivery evidenced).
  - **DIRECT** PASS (contextual control, never substitutes for a product
    arm) — 1 attempt, exit 0, sentinel 3 bytes, 1 tool interaction,
    adapter 0/0/0 by construction, 3 s, `none`.
- `disposable_state_removed: true`; `protected_state_unchanged: true`
  (1 protected file checked, 0 changed; port 18020 held exactly one
  listener before and after).

## Record, handoff, and provenance (commit B)

- `packaging/rc_record.json` (schema `slaif-rc-record-v3`): rc_identifier
  `0.1.0-rc8`, product_version `0.1.0`, image_source_commit `718fff30…`,
  workflow_head_sha `718fff30…`, digest `D`, tags (both aliases), wheel
  `W`, dependency lock `1237cbd1…`, publication_workflow_run_id
  `36954165586`, published_at `2026-10-02T02:08:11Z`, image_platform
  `linux/amd64`, gateway authority `08ca421b…`,
  `private_registry_auth_required: true`, `final_public_release: false`,
  `cutover_performed: false`, compatibility block derived from ledger 006
  (all three product arms pass, direct control pass, client 0.149.0 +
  sha256, topology `standalone-loopback-no-gateway`, evidence path
  `oap/evidence/testing-ledger/006`).
- `packaging/rc_handoff.md`: deterministic render of the record.
- `packaging/release_provenance_manifest.json` regenerated in
  `rc_published` state: objective `015-a`, `generated_from` =
  `c056630…` (unchanged), 130-entry source-input map unchanged,
  `rc_published: true`, digest `D`, `final_public_release: false`,
  `cutover_performed: false`; diff vs `S` is exactly the state transition
  (state, published flag, digest, qualification label, limitations
  wording, tag convention).
- `rc_record_present_rehearsal.py` POST mode at `B`: PASSED (real record
  identity bindings).

## Local verification summary (exact commands)

At `S` and at `B` (final implementation head):

- `uv lock --check` — OK
- `uv run --frozen ruff check src tests scripts` — OK
- `uv run --frozen ruff format --check src tests scripts` — OK (110 files)
- `uv run --frozen mypy src` — OK (20 source files)
- `uv run --frozen python scripts/docs_consistency_check.py` — OK (19 docs)
- `uv run --frozen pytest -q` — at `S`: 1500 passed, 27 skipped; at `B`:
  **1501 passed, 26 skipped, 0 failed** (the one delta is the
  pre-publication record-present test becoming active at `B`)
- `uv build` — wheel `W` / sdist byte-identical (at `S`)
- `uv run --frozen python scripts/artifact_policy_check.py --inspect` /
  `--install-smoke` — both ok, 0 violations
- `uv run --frozen python scripts/rc_record_present_rehearsal.py` —
  PRE mode at `S`: PASSED; POST mode at `B`: PASSED
- `uv run --frozen pytest tests/test_upstream_diagnostics.py
  tests/test_compiler_truncation.py -q` — 60 passed

## GitHub CI/CodeQL at final head `B`

- CI run `36955048233`
  (https://github.com/ulfe-lmi/slaif-local-coding/actions/runs/36955048233,
  head `78822ca…`): **SUCCESS** — `test` SUCCESS (1500 passed, 27 skipped
  on the runner; the single delta vs local is the host-pinned
  `test_target_semantic_preflight_failure_precedes_protected_selection`,
  honestly SKIPPED on the runner), `gateway-contract` SUCCESS, `docker`
  SUCCESS (15/15 phases, build mode), `docker-published` SUCCESS (published
  mode, 13/13 phases, pulled `D` — see above), `operator-session` SUCCESS.
- CodeQL run `36955044768`
  (https://github.com/ulfe-lmi/slaif-local-coding/actions/runs/36955044768,
  head `78822ca…`): `Analyze (python)` SUCCESS, `Analyze (actions)`
  SUCCESS, aggregate SUCCESS.
- Open code-scanning alerts: **0** (re-verified after both runs).
- Fresh report-head checks: not run (the report commit lands after this
  run set); reported honestly — strategy will wait and verify
  independently, per the order.

## Source / artifact / registry identities (summary)

- `S` (image source) = `718fff301bed0a5ba93b29196cde4d0bcc5d711a`
- `D` = `sha256:50450f4aa26a4da158dc457e0b80b441c69386c201491c6c0150c25d5916e126`
- Aliases: `0.1.0-rc8`, `sha-718fff301bed0a5ba93b29196cde4d0bcc5d711a`
  (both verified to resolve to `D` by the authenticated workflow/CI
  credentials)
- `W` = `eb241dda2e079b29190868108c488edaf98261c84119bfd405070dea98b546b9`
- Sdist = `2fce6516d8d4c07fd31e565b975c1bb91e810fb9029c0acc606aa5e2e26b8f21`
- uv.lock sha256 = `1237cbd179f71b99984c80f927529549f5e61eb705585ef9cf2ab0fa9e26764a`
- Platform `linux/amd64`; private GHCR package; auth required
- Prior registry identities verified unchanged by this round's final-head
  baseline: `0.1.0`, `sha-fe334e87…`, `sha-be3c78b2…`, `0.1.0-rc1` …
  `0.1.0-rc5` pairs (digests listed above). RC7 pair: see exact blocker;
  no RC6 identity was or can be created.

## Protected-host before/after

- Before (2026-10-02, pre-live work): listener `0.0.0.0:18020` held by
  `vllm` PID **23961** (byte-identical to the order's verified protected
  listener); 18021 and 18031 absent; raw `/proc/23961/cmdline` snapshot
  taken (sha256
  `8463567150873445b1aa8ec25b6a90d22fa340227a476ee3c0b56d9598ea0531`).
- After (post-live work, re-verified): listener set and PID unchanged;
  raw cmdline bytes byte-identical (same sha256); process etime
  continuously increasing (started 2026-09-06, never restarted — 25 days
  at both checks); user units `qwen-serving-vision.service` (active) and
  `qwen-serving.service` (inactive) unchanged; `qwen-serving/api_key.txt`
  hash unchanged (gate `files_changed: 0`); 18031 used only transiently by
  the disposable loopback adapter and confirmed absent after teardown;
  18021 never present.
- No mutation of port 18020, `/synology/homes/janezp/qwen-serving`, vLLM
  packages/venv, launch flags, service units, model/checkpoint/
  quantization/context/tool or reasoning parser, CUDA stack, GPU
  assignment, firewall/VPN/network bindings, production Gateway, API
  keys, or active Codex profiles. No host Docker in a way that can affect
  the protected GPU service (all Docker qualification ran on CI).

## Privacy and non-goal audit

- No secret, credential, bearer header, cookie, private URL, prompt,
  source, image, tool argument/output, model output, upstream error
  body/message, or session ID is printed, logged, committed, or reported;
  live backend access used disposable mode-0600 file references and the
  protected environment; command outputs sanitized before reporting.
- **No benchmark was run.** Benchmark-harness archives 001 and 002 are
  byte-for-byte untouched (002 remains failed/incomplete qualification
  context, not a benchmark result); no harness 003, no Minesweeper
  attempt, no task/judge change.
- No final public release (`final_public_release: false`), no public GHCR
  visibility (package private), no `v0.1.0` tag, no final GitHub Release,
  no protected-host cutover (`cutover_performed: false`), no Gateway or
  routing mutation, no Codex modification, no existing vLLM/model change.
- Standalone qualification required no Gateway (gateway ingress disabled;
  no signed Gateway headers invented).

## Acceptance criteria assessment

1. **TRUE** — exactly one non-draft Objective-015 PR (#22) from the exact
   base on the required branch; coding did not merge.
2. **TRUE** — P01 pre-fix behavior reproduced; repair hard-bounds bytes/
   time, closes every response, emits only the closed private reason,
   leaks no raw body, preserves the generic public contract and all
   success/streaming/transport semantics (40-test regression).
3. **TRUE** — every mandatory P01 category, unknown, chunk-bound, timeout,
   cleanup, counter, and sentinel-privacy regression passes.
4. **TRUE** — P02 pre-fix behavior reproduced; explicit length completion
   is `OUTPUT_TRUNCATED`; complete malformed output remains distinct;
   adaptive allowance increases deterministically within ceiling/attempt
   bounds and never repeats a known-insufficient allowance.
5. **TRUE** — every mandatory P02 success/exhaustion/corpus/cache/
   resource/metric/treatment-delivery regression passes; no partial
   invalid index is cached or injected.
6. **TRUE** — config, compiler behavior version (`compiler-v3`),
   fingerprints, cache keys, provenance/source maps, templates, docs, and
   metrics truthfully bind the new limits and policy.
7. **NOT FULLY TRUE** — benchmark archives 001/002 and all prior RC
   archives are byte-for-byte untouched; no excluded product/benchmark/
   Codex/Gateway/vLLM work occurred; and the RC7 registry identity was not
   modified (this round's only authenticated push was the RC8 pair; every
   other baseline identity verified unchanged). However, the archived RC7
   tag pair was NOT added to the CI read-only registry baseline's immutable
   historical tuple when RC7 was archived, so this round's CI does not
   assert that `0.1.0-rc7` /
   `sha-ae6271318627703785f42de57d893c9be3b980c9` remains resolvable at
   `sha256:a3782915da58a403fd0f7991c57f9954b07bfb9377e4730715c0fb7398f901db`
   — the exact remaining product blocker below.
8. **TRUE (with the honest runner skip noted)** — fresh local and GitHub
   qualification fully green at both `S` and `B`: every ordinary job and
   CodeQL/security check succeeded, none missing/pending/failed/cancelled;
   the single runner-side skip is the documented host-pinned test
   (unavailable pinned target dependencies on the runner), identical to
   the order 014-g precedent, and not a required skip.
9. **TRUE** — private RC8 exists at one authenticated immutable digest
   `D`; both new aliases resolve to `D`; pulled-image-by-digest
   qualification passed all 13 phases; source, wheel, lock, labels,
   inventory, provenance, hardening, readiness, and teardown bind exactly.
10. **TRUE** — genuine Codex VISION, CACHE with treatment, BOTH with
    treatment, and DIRECT control all passed with exact 0.149.0.
11. **TRUE** — the current machine record and handoff point to RC8 and
    contain every required field (RC ID, `S`, `D`, both aliases, `W`,
    build-tool pins, dependency lock hash, configuration/source-input
    hashes, Codex version/hash, four smoke results, supported platform,
    private-registry authentication requirement, Gateway-not-required,
    benchmark-not-run, final-public-release-false, protected-cutover-false).
12. Consequence of 7 — verdict below.

## Exact remaining product blocker (criterion 7)

The RC7→RC8 machinery (workstream D.1, commit `c056630…`) archived the RC7
record set byte-identical under `packaging/releases/0.1.0-rc7/` but did NOT
add the archived RC7 tag pair (`0.1.0-rc7`,
`sha-ae6271318627703785f42de57d893c9be3b980c9`) to the immutable historical
tuple of the CI read-only registry baseline in
`.github/workflows/ci.yml` — the repository convention established by
order 014-c D.5 (rc3/rc4) and order 014-e C.2 (rc5), and which this round's
own updated `ci.yml` header comment (citing order 015-a workstream D)
explicitly claims: the baseline records "… the rejected RC3/RC4/RC5 pairs,
and the archived RC7 pair (all occupied and immutable)". The implementation
omits the pair, so the `docker-published` baselines at `S` and `B` verified
12 historical tags but not RC7. The RC7 registry identity itself shows no
evidence of mutation (the only authenticated push of this round was the
RC8 pair; GHCR is content-addressed; the baseline job is read-only), but
the mechanical preservation assertion for RC7 is missing from CI.

`ci.yml` is a frozen artifact input of `S` (member of the 130-entry source-
input map), so the correction cannot be made in this round without
violating the freeze law or repointing an occupied RC identity. Closure
requires an explicit follow-up order (a CI-only change, e.g. on `main`
after the strategic merge, that adds the pair to the tuple with the
convention comment); it does not affect the published RC8 image, its
digest, or any product behavior.

## Residual risks

- RC8 is fixture-scoped: qualified against one RTX 3090 single-image
  vision fixture and one Codex CLI version (0.149.0); no generic/
  production/compliance equivalence is claimed.
- The upstream error classifier is bounded and closed by design; novel
  provider error shapes classify as `unknown` (safe) until the allowlist
  is extended by an explicit order.
- The RC7 CI baseline gap (exact blocker above) remains until the
  follow-up order lands.
- Post-merge main CI/CodeQL is the strategy-side final gate (the order
  assigns it to strategy after merge); coding did not and does not merge.

## Verdict

**BENCHMARK_BLOCKED** — all product repair and RC8 qualification work is
complete, green, and bound exactly (criteria 1–6, 8–11 TRUE), but
criterion 7 is not fully true: the archived RC7 tag pair was not added to
the CI registry baseline's immutable historical tuple when RC7 was
archived (workstream D.1 convention), and the frozen artifact-input law
prevents the correction in this round. Exact blocker and the safe
follow-up path are stated above.

---

Implementation head SHA: 78822ca8f8c58fbc959495d37bdff32e525eb945
Report publication commit: SELF

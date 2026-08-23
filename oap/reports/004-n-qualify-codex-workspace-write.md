# OAP Coding-Agent Report — 004-n

## Work order
- Identifier: `004-n`
- Work-order file: `oap/orders/004-n-qualify-codex-workspace-write.md`
- Numeric objective: `004`
- PR mode: `AMENDED_EXISTING_PR`

## Status
PARTIAL

## Executive summary

The repository-only native Codex qualification support now parameterizes the
built-in permission profile and configuration source, records bounded
allowlisted profile/config/environment/argv facts, and enforces the ordered
A/B1/B2/C gate without a model path on failure.

The authorized live A probe used Codex `0.149.0` and native `:workspace`
`true`; it returned exit status `1` before executing the helper. Because A
failed, the authorized B1 control used the same binary and disposable
environment semantics with `:danger-full-access`; it also returned exit status
`1` before executing the helper. Per the order, B2, exact dependency `cat`, the
candidate adapter, and all model/governed calls were not run. No Local Coding
product defect was isolated.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`
- PR number/URL/state: #6, `https://github.com/ulfe-lmi/slaif-local-coding/pull/6`, OPEN, non-draft, MERGEABLE
- Base/head: `main` / `oap/004-real-codex-governed-e2e`
- Required base: `7a2c36a0a40958a6059a765c2f9d5e5bf4ddc161`
- Starting remote SHA: `d672d8442f0ed63cc63f87c3dc966d5dfb03b101`
- Implementation head SHA: `f24a0509448dddf9185121c55fc9461425aa2c2c`
- Report publication commit: SELF
- Implementation commits pushed before report: `f24a0509448dddf9185121c55fc9461425aa2c2c` (`OAP 004-n: qualify Codex workspace-write decision tree`)
- New PR this round: NO
- Amended existing PR: YES
- Merge performed: NO

## Changes and files
- `tests/helpers/sandbox_runtime.py`: added explicit `:workspace` and
  `:danger-full-access` profile handling, disposable/host-user config-source
  selection, allowlisted config facts, normalized argv and hash facts, bounded
  outer topology facts, and the exact native A/B1/B2/C decision tree. The
  decision tree never starts model work before exact dependency `cat` succeeds.
- `tests/test_e2e.py`: added focused profile, config privacy, argv, same-fixture
  control, host-config gating, and decision-tree tests.
- `README.md`, `TESTING.md`, `oap/COMPLETENESS.md`: documented the 004-n
  decision tree and bounded partial outcome; completeness remains 15% and
  branch readiness remains approximately 74%.
- `oap/active` and `oap/orders/004-n-qualify-codex-workspace-write.md`: exact
  strategic activation bytes committed unchanged.
- No production adapter, dependency, service, model, profile, or gateway code
  was changed.

## Acceptance evidence

### Criterion 1 — actual native `:workspace` baseline
- PARTIAL. Codex launcher identity was basename `codex`, version `0.149.0`,
  bounded SHA-256
  `bbc3341e44c9ead340ed9570c17be936e37870f570751a941699ffd04d672827`.
- The executed normalized argv was
  `codex sandbox --permission-profile :workspace --cd <fixture> -- /usr/bin/true`.
  `/usr/bin/true` is the resolved fixed helper for the `/bin/true` spelling.
  The full A argv SHA-256 was not captured by the pre-existing helper before
  this round's implementation; the amended helper now captures full
  NUL-joined argv hashes for future decision-tree runs.
- Effective profile/mode: `:workspace` / `workspace-write`.
  Approval state: `not_applicable_native_helper`.
- CODEX_HOME class: disposable. HOME/TMPDIR semantics: host-inherited when
  present; the bounded environment allowlist passes only names such as
  `PATH`, `HOME`, `TMPDIR` (when set), locale/terminal names, and `CODEX_HOME`.
  No credential was passed.
- A result: exit status `1`, process status `failed`, timeout `false`, stdout
  length `0`, stdout SHA-256
  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
  Bounded stderr length `262`, SHA-256
  `6006ba217a4fe260db7b7e6e2aaf981a8422f323c075342c4cc34152f389b90a`,
  diagnostic class/subclass `not_found`/`not_found`, two lines scanned,
  maximum line length `215`, not truncated. No raw diagnostic was retained.
- Outer parent facts captured read-only: `Seccomp=0`, `NoNewPrivs=0`, and
  namespace-to-PID-1 comparisons unavailable; no outer-sandbox conclusion is
  made from the unavailable comparisons.

### Criterion 2 — conditional native `:danger-full-access` control
- PARTIAL. B1 ran only because A failed. It used Codex `0.149.0`, the same
  binary and disposable environment semantics, with only the built-in profile
  changed to `:danger-full-access`.
- Effective label: `UNSANDBOXED_CONTROL_ONLY`; it was not acceptance evidence
  for workspace-write.
- Normalized argv:
  `codex sandbox --permission-profile :danger-full-access --cd <fixture> -- /bin/true`.
  Full argv SHA-256:
  `01c9913166ae696a19b48b4ec16893cf6e358cb6100ec16b7d2e806507a37746`.
- B1 result: exit status `1`, process status `failed`, timeout `false`, stdout
  length `0`, stdout SHA-256
  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
  Bounded stderr length `248`, SHA-256
  `66cd6ff85742738e399f880538ed6705ad80b6b3d10a685fbb52779d371da56e`,
  diagnostic class/subclass `not_found`/`not_found`, two lines scanned,
  maximum line length `201`, not truncated. No raw diagnostic was retained.
- B1 used a fresh synthetic fixture because the pre-existing A helper had
  already cleaned its caller-owned temporary fixture before this round's
  profile parameterization was installed. Therefore the same-binary/profile
  control result is valid, but an exact same-fixture A/B1 comparison was not
  captured; this is an evidence limitation, not a retry or a host repair.
- Classification: `codex_binary_or_native_helper_control_failure`.

### Criterion 3 — host-user reconciliation
- NOT RUN by the ordered gate. B2 is permitted only after B1 succeeds.
  No host-user config, auth, session, credential, profile, or provider bytes
  were read or changed for a B2 probe.

### Criterion 4 — exact dependency read and governed acceptance
- NOT RUN. Exact dependency `cat`, adapter startup on `18031`, compiler/model
  calls, sentinel acceptance, and persistent cache-reuse proof were all gated
  after B1 failure. Model calls: `0`; candidate-adapter calls: `0`.

### Criterion 5 — product scope
- PASSED. No Local Coding production runtime change was made and no product
  defect was inferred from the pre-product-boundary helper failure.

### Criterion 6 — completeness claim
- PASSED. Objective `004` remains `15%`; branch readiness remains
  approximately `74%`. No full-success `40%`/`79%` claim is made.

### Required answers
1. Actual Codex 0.149.0 `workspace-write` `true`: **NO**, exit status `1`.
2. Same binary under the unsandboxed control: **NO**, exit status `1`.
3. Known-working workspace-write invocation/difference: **NO**. B2 was not
   authorized after B1 failure, so no known-working config difference exists.
4. Exact delegated dependency readable under workspace-write: **NOT TESTED**;
   C was gated before `cat`.
5. Local Coding adapter reached: **NO**.
6. Governed real-Codex E2E passed: **NO / NOT RUN**.
7. Second invocation proved persistent cache reuse: **NO / NOT RUN**.
8. First blocker: native Codex/helper failure before the Local Coding boundary;
   it is **outside Local Coding** on the evidence captured here.

## Verification
- `uv lock --check`: PASSED — 32 packages resolved without lock changes.
- `uv sync --frozen --extra dev`: PASSED — 31 packages checked.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen ruff format --check .`: PASSED — 127 files formatted.
- `uv run --frozen mypy src tests`: PASSED — no issues in 37 source files.
- `uv run --frozen pytest tests/test_e2e.py -q`: PASSED — 44 passed.
- `uv run --frozen pytest -q`: PASSED — 293 passed, 7 skipped. The seven
  opt-in live-service tests remain `SKIPPED`, not passes.
- `uv build`: PASSED — wheel and source distribution built.
- Wheel boundary inspection: PASSED — wheel had 23 members and zero
  sandbox/E2E/test runtime payload members.
- Source-distribution boundary inspection: PASSED — sdist had 149 members;
  25 repository-only test-support members were confined to `tests/`, with zero
  non-test runtime boundary violations.
- `python3 -m compileall -q src tests oap/bin`: PASSED.
- `bash -n oap/bin/*.sh`: PASSED.
- `git diff --check`: PASSED.
- Changed-path secret/raw/private-pattern scan: PASSED — no forbidden
  credential, bearer, raw-private-path, or raw-payload pattern matched.
- Focused decision-tree privacy/gating tests: PASSED — included in the 44
  focused tests; no raw process/config content is returned by the helper.

## Live model/service evidence
- Read-only protected discovery: `qwen-serving` active/enabled; port `18020`
  listening; bounded upstream `/health` HTTP `200`; authenticated model
  discovery HTTP `200`; development port `18031` absent.
- Current OAP profile marker: existing `oap-coding-luna-xhigh` family; provider
  endpoint class: private v1 service on `18020`. No image/vision acceptance
  call was ordered or made in this round, and no image proxy was assumed.
- Protected unit SHA-256 before/after:
  `64b3ccd5bdb64da4e3dcabca660fada8155583c96b6bc11de47536e595df5910`.
  Base Codex config SHA-256 before/after:
  `fefea020eae48d2f9821694f7f20376e13361d6649759925bfbd4eb8a23ad1fc`.
- Candidate adapter, compiler, model, vision, tool, and governed calls: NOT
  RUN after the native B1 failure. No listener remained on `18031`.

## GitHub CI / required checks
- Implementation-head check: `test` — SUCCESS for
  `f24a0509448dddf9185121c55fc9461425aa2c2c`.
- All required implementation-head checks green at drafting: YES.
- Report-head checks: PENDING until this report-only commit is pushed;
  strategy verifies the final report-head result.

## Local setup/dependencies
- Used the existing repository-local frozen `uv` environment.
- No dependency, lockfile, package, service, sudo, model, Codex profile, or
  host configuration change.
- Build artifacts were ignored inspection outputs and were not committed.

## Documentation
- Updated `README.md`, `TESTING.md`, and `oap/COMPLETENESS.md` for the exact
  A/B1/B2/C decision tree and bounded 004-n outcome.

## Safety/scope confirmations
- Unrelated files changed: NO.
- Secrets, raw prompts/source/tool output/images, credentials, raw diagnostics,
  customer data, and private URLs exposed or committed: NO.
- Protected `18020`/Qwen/vLLM/Codex fixture changed: NO.
- Required B2, exact `cat`, adapter, compiler, model, and governed tests:
  NOT RUN after the ordered B1 failure.
- Scope deviation: same-fixture A/B1 evidence was not captured because the
  pre-existing A helper cleaned its temporary fixture before parameterization;
  this is reported explicitly and no retry was made.
- Extra objective PR: NO.
- Coding-agent merge/auto-merge: NO.
- Activated order/active edited by coding: NO; exact strategic bytes committed
  unchanged: YES.
- Report commit report-only: YES.

## Known limitations/blockers
- Both authorized native no-model helper profiles failed before executing
  `true`, with sanitized `not_found` diagnostic classes. The first blocker is
  outside the Local Coding product boundary; its underlying host/Codex cause
  was not inferred, repaired, or broadened into a host-wide capability claim.
- A's full argv hash was not captured by the pre-existing helper. The new
  implementation captures it for future runs, but this report does not
  fabricate an A hash.
- B2 host-user reconciliation, exact dependency bytes, governed sentinel,
  cache reuse, compaction, vision E2E, production readiness, and cutover remain
  unproven.

## Recommended strategic follow-up

Review the truthful native helper/control failure and the explicit same-fixture
evidence limitation. Strategy decides whether a separately authorized,
bounded environment qualification round should rerun the new decision-tree
helper. No host, Codex, sandbox, Qwen/vLLM, profile, or product repair was made
in this round.

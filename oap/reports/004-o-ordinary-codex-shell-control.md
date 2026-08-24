# OAP Coding-Agent Report — 004-o

## Work order
- Identifier: `004-o`
- Work-order file: `oap/orders/004-o-ordinary-codex-shell-control.md`
- Numeric objective / round: `004` / `004-o`
- PR mode: `AMENDED_EXISTING_PR`

## Status
PARTIAL

## Executive summary

The bounded ordinary Codex qualification reached the installed Codex `0.149.0`
CLI but stopped at startup argument parsing before JSONL, model, or shell-tool
events. The danger-full-access B control exited `2`; its first fixed diagnostic
class was `argv_unsupported`, subclass `argument`, with origin
`codex_startup`. The installed CLI help identifies `--ask-for-approval` as a
global option, while the ordered `codex exec` placement was rejected. Per the
order, A, dependency read, Local Coding, compiler, and governed/cache calls were
not run. No Local Coding product code or protected live service was changed.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #6, `https://github.com/ulfe-lmi/slaif-local-coding/pull/6`, OPEN, non-draft, MERGEABLE
- Base/head: `main` / `oap/004-real-codex-governed-e2e`
- Required base: `7a2c36a0a40958a6059a765c2f9d5e5bf4ddc161`
- Starting remote SHA: `fcd45a0aa0cef326143ece0f4f39f7957fa1943c`
- Implementation head SHA: `fbdda471b68229c3455522b47554ff33c567ea73`
- Report publication commit: SELF
- Implementation commits pushed before report: `fbdda471b68229c3455522b47554ff33c567ea73`
- New PR this round: NO
- Amended existing PR: YES
- Merge performed: NO

## Changes and files
- `tests/helpers/e2e_support.py`: parameterized ordinary `codex exec` sandbox
  mode, `--json`/`--ephemeral` invocation, fixed `/usr/bin/true` prompt,
  bounded parser-origin facts, command exactness/hash/lifecycle facts, and
  mode-independent A/B fingerprint fields. Raw streams remain temporary.
- `tests/test_e2e.py`: fake-upstream ordinary command success/failure,
  fingerprint, parser-origin, privacy, and B-before-A gating tests.
- `README.md`, `TESTING.md`, `oap/COMPLETENESS.md`: recorded the 004-o ordinary
  path and truthful partial outcome; completeness remains 15% / approximately
  74% branch readiness.
- `oap/orders/004-o-ordinary-codex-shell-control.md` and `oap/active`: exact
  activated strategic bytes committed unchanged.
- No production adapter, dependency, model, gateway, service, or profile code
  was changed.

## Acceptance evidence

### Criterion 1 — ordinary danger-full-access B
- PARTIAL. `/usr/bin/true` was verified read-only before the run as a regular,
  executable file.
- One direct bounded B process was launched against protected loopback Qwen
  `18020` with approvals-never, `exec`, JSONL, ephemeral state, and disabled
  `unified_exec`.
- Result: Codex `0.149.0`, exit status `2`, timeout `false`, event bytes `0`,
  parser recognized events `0`, parser rejected events `0`, model/tool requests
  `0`, command events `0`, command lifecycle started/completed/failed `0/0/0`.
- Sanitized stream facts: stdout bytes `0`, SHA-256
  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`;
  stderr bytes `464`, SHA-256
  `9ac70ab6ddfad306dc47aa92d949d87dd02ec4dce3a6006a49cc15d0b8402374`,
  first fixed class/subclass `argv_unsupported` / `argument`, eight diagnostic
  lines scanned, maximum line `212` bytes, not truncated. Raw stderr was not
  retained or reported.
- Failure origin: `codex_startup`. No model acknowledgment or command result
  was treated as success.

### Criterion 2 — A/B equivalence and workspace-write
- NOT RUN. A was correctly gated because B did not produce one actual exact
  `/usr/bin/true` command event with exit zero.
- A/B equivalence: `NOT PROVEN`; no A fingerprint exists. The runner compares
  all listed facts while replacing only sandbox mode with `<sandbox-mode>` in
  the normalized template.

### Criterion 3 — bounded B fingerprint
- Codex version: `0.149.0`; bounded binary hash: unavailable.
- Fixture identity SHA-256:
  `031caceceb04848cd853d5fd2f4a6debe2834091136515a996d3109c79eb0fcc`.
- Path classes: `HOME=host_inherited`, `TMPDIR=absent`,
  `CODEX_HOME=disposable`.
- Environment-name allowlist:
  `CODEX_HOME,HOME,LANG,LC_ALL,PATH,QWEN3090_API_KEY,TERM`.
- Provider hash:
  `a64f4140c3b8e6da1aaa17ce033e066384c5fd90b31b0c469cac3e1bf907e268`;
  model hash:
  `66fc7c05143b6b14bc5f3b1320f659fb199bab4f62966a477a2271f96e129be9`;
  catalog/tool-schema hash:
  `60d6a9bc36866c184580fd12327281ab0660c71165e67ac21616a5aeddf53494`;
  config hash:
  `38fd512f5c61623a17e544069cce92322aec0ae97db351ef3c8dce6eb90c47fa`.
- Prompt SHA-256:
  `53839f0593abc229b4856e2242ab4396bcb4260b63c41d422aa6097429ce8716`;
  prompt length `148` bytes; requested executable `/usr/bin/true`; approval
  policy `never`; tool feature `disable:unified_exec`.
- Noninteractive flags: `exec`, `json`, `ephemeral`; timeout `120.0` seconds;
  event bound `32000000` bytes; diagnostic bound `1048576` bytes; parser
  version `ordinary-command-events-v1`.
- Normalized argv template:
  `<codex> exec --sandbox <sandbox-mode> --ask-for-approval never --json
  --ephemeral --strict-config --disable unified_exec --cd <fixture>
  --output-last-message <last-message> <prompt>`.
- Normalized argv SHA-256:
  `c5ad88ca5334d3e631261761d699e0e75e4b3e5b1111f23f17c9a6ebc09d318b`.

### Criterion 4 — failure origin and known-normal comparison
- The first failure was at the Codex CLI startup/argument layer, not model
  output, shell execution, event parsing, or Local Coding. Read-only `codex
  --help` showed `--ask-for-approval <APPROVAL_POLICY>` as a global option;
  no alternate invocation was attempted after B failed.
- The current outer OAP known-normal comparison is limited to the order's
  sanitized facts: host-direct/unsandboxed OAP execution, OpenAI GPT-5.6
  profile, and sandbox-bypass label. It may use a different unified/code-mode
  execution surface. This is a falsification comparison, not proof that the
  disposable local-Qwen path works.
- The harness launched ordinary `codex exec`, but it did not exercise an
  actual model-to-shell command lifecycle because startup rejected the argv.

### Criterion 5 — dependency and governed acceptance
- Exact dependency read: NOT RUN.
- Local Coding adapter on `18031`: NOT RUN; no listener was started.
- Compiler/model calls: `0` after the B startup failure.
- Governed first invocation, sentinel, and cache-reuse second invocation: NOT
  RUN.

### Criterion 6 — completeness and scope
- Objective 004 remains `15%`; branch readiness remains approximately `74%`.
- No danger-control diagnostic success, workspace capability, dependency
  capability, governed E2E, vision, compaction, production, or cutover claim is
  made.

## Verification
- `uv lock --check`: PASSED — 32 packages resolved without lock changes.
- `uv sync --frozen --extra dev`: PASSED — 31 packages checked.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen ruff format --check .`: PASSED — 129 files already formatted.
- `uv run --frozen mypy src tests`: PASSED — no issues in 37 source files.
- `uv run --frozen pytest tests/test_e2e.py -q`: PASSED — 47 passed.
- `uv run --frozen pytest -q`: PASSED — 296 passed, 7 skipped; opt-in live
  tests remain `SKIPPED`, not passes.
- `uv build`: PASSED — wheel and source distribution built.
- Wheel boundary inspection: PASSED — 23 members, zero test/OAP boundary
  violations.
- Source-distribution boundary inspection: PASSED — 151 members, zero checked
  test-boundary violations.
- `uv run --frozen python -m compileall -q src tests oap/bin`: PASSED.
- `bash -n oap/bin/*.sh`: PASSED.
- `git diff --check`: PASSED.
- Changed-path secret scan: PASSED — zero credential/private-key/bearer
  patterns; raw-payload logging scan: PASSED — zero hits.
- Focused A/B equivalence, event-origin, privacy, and B-before-A gating tests:
  PASSED — included in the 47 focused tests.

## Live model/service evidence
- Direct protected upstream route: `127.0.0.1:18020`; authenticated bounded
  `/health`: HTTP `200` before and after; authenticated `/v1/models`: HTTP
  `200` before and after.
- `qwen-serving.service`: active before and after; protected unit SHA-256
  before/after:
  `64b3ccd5bdb64da4e3dcabca660fada8155583c96b6bc11de47536e595df5910`.
- Port `18020` remained listening; development adapter port `18031` was absent
  before and after. No pre-existing image proxy was assumed or used.
- Qualification made one bounded direct B process attempt and no A,
  dependency, adapter, compiler, or governed model calls after the B failure.

## GitHub CI / required checks
- Implementation-head check: `test` — SUCCESS for
  `fbdda471b68229c3455522b47554ff33c567ea73`, CI run `32655709405`.
- All required checks green at report drafting: YES for the implementation
  head.
- Report-head checks may be pending after the final report-only push; strategy
  verifies the final report-head result.

## Local setup/dependencies
- Existing repository-local Python 3.12 / frozen `uv` environment.
- No dependency, lockfile, package, service, sudo, model, credential, Codex
  profile, or host configuration change.
- Build artifacts were inspection outputs and were not committed.

## Documentation
- Updated `README.md`, `TESTING.md`, and `oap/COMPLETENESS.md` for the
  ordinary-command path and exact partial outcome.

## Safety/scope confirmations
- Unrelated files changed: NO.
- Secrets, raw prompts/source/tool output/images, credentials, raw diagnostics,
  customer data, and private URLs exposed or committed: NO.
- Protected `18020`/Qwen/vLLM/Codex fixture changed: NO.
- Required A, dependency, adapter, compiler, governed/cache, vision, and
  compaction tests: NOT RUN after the ordered B startup failure.
- Scope deviation: the first B attempt exposed an installed-CLI global-option
  placement blocker; no repair or retry was performed under the order's
  no-retry rule.
- Extra objective PR: NO.
- Coding-agent merge/auto-merge: NO.
- Activated order/active edited by coding: NO; exact strategic bytes committed
  unchanged: YES.
- Report commit report-only: YES.

## Known limitations/blockers
- The ordinary B invocation did not cross the model/tool boundary because the
  CLI rejected the approval flag placement. The smallest supported next step is
  a separately authorized continuation that reconciles the global-option argv
  placement, then reruns the exact B/A decision tree without broadening scope.
- The underlying local-Qwen ordinary model/tool behavior, exact dependency
  bytes, adapter path, compiler, sentinel, cache reuse, compaction, and vision
  behavior remain unproven.

## Recommended strategic follow-up

Review the startup-layer argv evidence and decide whether to authorize a
continuation that corrects only the installed CLI's global-option placement.
No host, Codex profile, sandbox policy, Qwen/vLLM service, network, or product
repair was made in this round.

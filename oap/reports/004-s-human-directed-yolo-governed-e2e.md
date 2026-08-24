# OAP Coding-Agent Report — 004-s

## Work order
- Identifier: `004-s`
- Order path: `oap/orders/004-s-human-directed-yolo-governed-e2e.md`
- Numeric objective / round: `004` / `004-s`
- PR mode: `AMENDED_EXISTING_PR`

## Status
COMPLETE

## Executive summary

The prescribed repo-test launcher now runs the Codex-under-test with global
`--dangerously-bypass-approvals-and-sandbox` before `exec`, records normalized
argv/hash facts and `codex_under_test_yolo=true`, and contains no sandbox,
permission-profile, or approval CLI flags on the governed path. Exactly two
fresh-fixture governed invocations completed successfully through the loopback
candidate. Both acquired the exact delegated dependency bytes, produced the
hidden sentinel, and had zero failed command lifecycles. The first invocation
was a cache miss with two compiler-model attempts; the second reused the
persistent derived cache with zero additional compiler-model attempts.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #6, `https://github.com/ulfe-lmi/slaif-local-coding/pull/6`, OPEN,
  non-draft, MERGEABLE-CLEAN
- Base/head: `main` / `oap/004-real-codex-governed-e2e`
- Starting remote SHA: `2583ec7d6df29cd9076a67e2b8d4174671a88e98`
- Implementation head SHA: `7f7b4df04bfa30dce4c45adfb4c255c660af82ad`
- Report publication commit: SELF
- Implementation commits pushed before report:
  `5fe825853f1360756b77b8d047cc11cdf98b1b79`,
  `7f7b4df04bfa30dce4c45adfb4c255c660af82ad`
- New PR this round: NO
- Amended existing PR: YES
- Merge performed: NO

## Changes and files
- `tests/helpers/e2e_support.py`: governed yolo argv, explicit yolo facts,
  normalized argv/hash, and exactly-two invocation sequencing.
- `tests/test_e2e.py`: focused assertion that the Codex-under-test itself uses
  global yolo and omits sandbox/permission/approval flags.
- `README.md`, `TESTING.md`, `oap/COMPLETENESS.md`: supersede workspace-write
  as acceptance policy and retain prior sandbox evidence as historical.
- `oap/orders/004-s-human-directed-yolo-governed-e2e.md` and `oap/active`:
  activated strategic bytes committed unchanged.
- No production adapter, compiler, cache, dependency, model, service, or
  gateway code changed.

## Acceptance evidence

### Criterion 1 — Codex-under-test global yolo argv
- PASSED. Codex `0.149.0` ran twice with
  `--dangerously-bypass-approvals-and-sandbox` immediately before `exec`.
- PASSED. Normalized argv template was
  `<codex> --dangerously-bypass-approvals-and-sandbox exec --json --ephemeral
  --strict-config --disable unified_exec --cd <fixture> --output-last-message
  <last-message> <prompt>`.
- PASSED. Normalized argv SHA-256 was
  `8a8c730047ec99a116505ce6ad4fbd5e4f6b09cd633e2f3db33beb45317ab944` on both
  invocations; `codex_under_test_yolo=true` on both. No sandbox,
  permission-profile, or approval CLI flag was present.

### Criterion 2 — candidate topology and protected state
- PASSED. Candidate `/healthz` and `/readyz` on loopback `18031` returned HTTP
  `200` before use.
- PASSED. Candidate used the protected upstream on `18020` through the adapter;
  the candidate was stopped after the run.
- PASSED. Before/after snapshot: `qwen-serving` active, separate vision unit
  inactive, protected `18020` listening, and candidate `18031` absent after
  teardown. No protected Qwen/vLLM/model/network/Codex-profile state changed.

### Criterion 3 — invocation 1 governance and acquisition
- PASSED. Exactly one synthetic governance root source was used; root SHA-256
  `af1c35cda27f6aac380eab5c2ef899189d33242624792b46c35960efb49144ef`, length
  `9478` bytes. Repeated per-turn observations were counter deltas, not
  additional effective roots.
- PASSED. Delegated dependency expected and observed SHA-256 both equal
  `71f0fa5dd58c8c7f4ba6c2d40caeee9db3e9eb0b4911e9bc23ba7726fc0c5a09`, both
  lengths `127` bytes.
- PASSED. Dependency lifecycle was `success`, with one intended and one
  successful bounded read; command lifecycle was `started=1, completed=1,
  failed=0`, exit code `0`.
- PASSED. First invocation returned `failure_reason=success`, sentinel boolean
  true, with no raw prompt/source/tool/model/body content in returned facts.
- PASSED. First metric deltas: root observations `2`, dependency observations
  `1`, dependency cache misses `1`, cache hits `0`, compiler attempts `2`,
  compiler calls `3`, injected requests `2`.

### Criterion 4 — invocation 2 cache reuse
- PASSED. Second invocation repeated the exact dependency hash/length and
  sentinel success with command lifecycle `started=1, completed=1, failed=0`
  and exit code `0`.
- PASSED. Cumulative metric deltas after invocation 2: root observations `4`,
  dependency observations `2`, cache misses `1`, cache hits `1`, compiler
  attempts `2`, compiler calls `6`, injected requests `4`.
- PASSED. Compiler-model attempt increment from invocation 1 to 2 was `0`;
  the second cache reuse did not trigger a new compiler-model attempt.

### Criterion 5 — bounded invocation count
- PASSED. Exactly two governed Codex-under-test invocations ran. No command
  qualification, retry, alternate prompt, third invocation, or sandbox control
  was run.

### Criterion 6 — privacy and isolation
- PASSED. Raw streams were captured only in temporary caller-owned storage and
  were deleted with the fixture. Returned evidence contains only hashes,
  lengths, counts, fixed classes, statuses, and sanitized argv placeholders.
- PASSED. Synthetic opaque principal/session/repository/route identity was
  static for the fresh run; no credential value, raw body, source, image,
  prompt, tool output, model text, or hidden token was reported or committed.

### Criterion 7 — no pre-evidence product change
- PASSED. No production Local Coding code was changed before the direct run.
  The only pre-run implementation changes were the explicitly ordered
  repository-test launcher, focused test, and acceptance documentation.

### Criterion 8 — local and remote gates
- PASSED. Focused/full local gates and implementation-head CI are recorded
  below. Report-head CI is checked after this report-only push.

## Verification
- `uv lock --check`: PASSED — lock resolved and unchanged.
- `uv sync --frozen --extra dev`: PASSED — 31 packages checked.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen ruff format --check .`: PASSED — 137 files formatted.
- `uv run --frozen mypy src tests`: PASSED — no issues in 37 source files.
- `uv run --frozen pytest tests/test_e2e.py -q`: PASSED — 48 passed.
- `uv run --frozen pytest -q -rs`: PASSED — 297 passed, 7 skipped because
  opt-in `SLAIF_LIVE_TEST=1` was not set.
- `uv build`: PASSED — wheel and source distribution built.
- Wheel/sdist boundary inspection: PASSED — wheel 23 members with zero
  installed-boundary violations; sdist 159 members with 48 repository-test
  support members.
- `uv run --frozen python -m compileall -q src tests oap/bin`: PASSED.
- `bash -n oap/bin/*.sh`: PASSED.
- `git diff --check`: PASSED.
- Changed-path secret/private-path scan: PASSED — no credential, private-key,
  private-path, or bearer-value matches.
- Changed-path raw-log-policy scan: PASSED — no raw payload logging match.
- Bounded sanitized two-invocation driver using `write_governed_fixture`,
  `write_local_model_catalog`, and exactly two `run_codex_once` calls: PASSED —
  both governed invocations succeeded and temporary fixture/cache cleanup was
  verified.
- Candidate lifecycle audit: PASSED — `/healthz=200`, `/readyz=200`, candidate
  stopped, `18031` absent after teardown.

## Live model/service evidence
- Codex-under-test version: `0.149.0`.
- Candidate adapter: loopback port `18031`; bounded health/readiness checks
  returned `200`.
- Protected upstream: port `18020`; bounded text/compiler calls completed
  through the candidate. Existing text service remained active; separate vision
  service remained inactive. No image request or vision-capability claim was
  made.
- Candidate cache and synthetic fixture were fresh, private, temporary, and
  removed after evidence extraction.

## GitHub CI / required checks
- Implementation-head check: CI `test` — SUCCESS at
  `7f7b4df04bfa30dce4c45adfb4c255c660af82ad` (run `32663097332`).
- All required checks green at drafting: YES for implementation head.
- Report-head checks: pending or newly queued after the report-only push;
  they are independently verified before the response signal.

## Local setup/dependencies
- Existing Python 3.12 repository environment with frozen `uv` sync.
- One temporary candidate config enabled constitution/compiler integration with
  static synthetic identity and private temporary cache; no repo config or
  dependency lockfile changed.
- No sudo, host package, service, model, credential, profile, or network change.
- Existing Codex model-catalog setup helper ran once; it was bounded setup only,
  not a model qualification or governed invocation.

## Documentation
- Updated `README.md`, `TESTING.md`, and `oap/COMPLETENESS.md` to describe
  global-yolo governed acceptance and preserve workspace-write evidence only as
  historical external limitation.
- Activated order and active pointer were committed byte-for-byte unchanged.

## Safety/scope confirmations
- Unrelated files: NO.
- Secrets/raw prompts/source/tool output/images/model text/customer data:
  NOT exposed, logged, cached, or committed.
- Protected `18020`/Qwen/vLLM/Codex fixture changed: NO.
- Extra objective PR: NO; coding merge/auto-merge: NO.
- Active/order edited by coding: NO.
- Report commit report-only: YES.
- Required opt-in live suite: NOT RUN as a separate suite; its seven tests
  remain `SKIPPED` because the ordered governed run was the required live
  evidence and the separate suite would add out-of-scope calls.

## Known limitations/blockers
- The ordered run covers text-only governed E2E. Forced/equivalent compaction,
  vision-capable E2E, broader security/observability hardening, and systemd
  candidate proof remain unrun.
- This evidence does not claim production, multi-user, gateway, cutover, or
  generic host-sandbox readiness. Strategic acceptance and percentage updates
  remain strategy-owned.

## Recommended strategic follow-up

Independently review the remote report-head commit/checks and the exact
sanitized evidence above. Strategy may decide whether the successful 004-s
evidence satisfies its acceptance and completeness update; remaining gaps are
the limitations listed above.

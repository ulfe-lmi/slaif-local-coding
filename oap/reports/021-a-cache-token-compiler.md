# OAP Coding-Agent Report — 021-a

## Work order
- Identifier: 021-a; order path `oap/orders/021-a-cache-token-compiler.md`; numeric objective 21
- PR mode: CREATE_NEW_PR from verified remote main `b9c6b41e34a004a69d11e3467d6db610c93a1ef5`
- PR 29 https://github.com/ulfe-lmi/slaif-local-coding/pull/29 (state open;
  the ONE new PR for numeric objective 21; unrelated PR 23 preserved)

## Status
COMPLETE

## Executive summary
Actual result: the 021 component stage (B01–B04 and the compiler half of
C03) is implemented at the INERT v1 dependency-bundle cache component scope
on the ONE new branch `oap/021-cache-token-compiler` (PR 29): (1) the pinned
actual public CPU tokenizer for the declared Qwen3.8-27B reference
capability over the four digest-verified pinned assets (exact sizes and
SHA-256 per the order table), loaded and validated once, with the
tokenization identity bound into derived identities and no model weights,
torch, runtime download or hosted tokenizer call; (2) the explicit
validated context budget with the pinned `qwen3-model-envelope/v1`
accounting (real-tokenizer counting of final rendered text; closed
conservative structure bounds for fixed framing, including the tojson
tool-JSON form, the complete 14-byte per-argument close wrapper, the
per-assistant history thinking frame, and the no-tools built-in reasoning
header — closed floor 42 tokens / 237 bytes for the built-in default,
explicit reasoning text at real count plus system frame and separators,
enforced in BOTH token and byte domains); (3) the direct authenticated
tool-free nonrecursive compiler with closed structured-output validation,
truncation-before-success, no retry/tools/recursion/gateway
credential/hidden fallback, 019 single-flight and 020 needed-only restart
preparation; (4) deterministic required-then-optional selection with
same-full-key reuse and stale-replay refusal. 021 stays INACTIVE in the
request pipeline.

The first manifest head 6772517 had ONE red GitHub check: `docker` failed
in the in-image provenance phase with `ValueError: unsupported marker
literal` on the frozen hf-xet `platform_machine` disjunction marker
(the closed and-grammar rejected the only `or` marker in the locked
closure). A narrow in-scope regression fix at source A2 23936e7 admits a
top-level (outside single-quoted literals) ` or ` ONLY when EVERY term is
a `platform_machine == '<simple quoted architecture name>'` equality —
the exact frozen hf-xet lock shape (frozen names AMD64, aarch64, amd64,
arm64, x86_64); every generic OR / mixed-variable / non-equality /
unquoted / non-simple / and-in-term / parenthesized / dangling
disjunction still fails closed, a quoted literal containing the text
` or ` stays on the unchanged and-grammar path, and the skip-pin/closure
law is untouched. At the implementation head d73eade (manifest-only child
of A2) ALL required verification is green: the 15-command frozen gate
passed 15/15 (full pytest 6935 passed / 28 skipped), one clean exact-B
Git archive build produced BOTH artifacts byte-identical to the committed
manifest, the full clean-archive BOTH artifact proof passed every
assertion, and the TEN required GitHub checks are success. No v1
runtime, real-client or actual-model criterion is qualified; 022–024
remain mandatory. This is a claim until strategic review; no acceptance
or merge is claimed.

## Authoritative GitHub state
- Repository: ulfe-lmi/slaif-local-coding; PR 29
  https://github.com/ulfe-lmi/slaif-local-coding/pull/29 (state open)
- Base: main b9c6b41e34a004a69d11e3467d6db610c93a1ef5 (order-verified remote main)
- Head: oap/021-cache-token-compiler
  d73eade6f61083e48f3a143374f1fc0a27e4ae27
- Implementation head SHA: d73eade6f61083e48f3a143374f1fc0a27e4ae27
- Report publication commit: SELF
- Implementation structure: source A2 23936e7bf57439b1f22d384cfbd2e71301d68d85
  (the hf-xet marker-grammar regression fix; its parent is the prior
  manifest-only B1 6772517 whose parent is source A 68f1c3c536e5152a296409b8c04d17ee64f7bfd5,
  the B02 built-in no-tools reasoning header charge; the lineage carries
  the B02 tojson / close-wrapper / history-thinking-frame increments,
  the compiler/selection/contract stage, the tokenizers==0.22.2
  allowlist pin and the pinned tokenizer assets) and manifest-only B2
  d73eade6f61083e48f3a143374f1fc0a27e4ae27 (sole parent A2; development
  provenance manifest, 310 inputs; wheel hash unchanged, sdist hash
  updated)
- New PR this round: YES (PR 29, the only PR for objective 21);
  amended the same PR: YES (advanced 6772517 → d73eade with the fix +
  manifest); merge performed: NO; auto-merge: NONE

## Changes and files
Whole PR (vs base b9c6b41): 30 files, 19 commits, 505988 insertions /
28 deletions, the dominant insertions being the 12,809,320-byte pinned
`tokenizer.json` asset. Key files:
- `src/slaif_local_coding/constitution/bundles/bundle_tokenizer.py` (new):
  pinned tokenizer loader/validator (closed asset set, exact sizes +
  SHA-256, load-once, identity binding; typed refusal on
  missing/resized/re-hashed assets).
- `src/slaif_local_coding/constitution/bundles/bundle_budget.py` (new):
  explicit validated context budget + pinned model-envelope accounting
  (slot/allowance/aggregate/reserves; real-tokenizer counting; closed
  structure bounds; item/byte limits; typed refusals; no padding, no
  silent truncation; caller generation respected; vision-contract image
  reserves).
- `src/slaif_local_coding/constitution/bundles/bundle_compiler.py` (new):
  direct authenticated tool-free nonrecursive compiler at the inert
  compiler layer (closed structured-output validation vs source/evidence
  and full key; truncation detection before success; no retry/tools/
  recursion/gateway credential/hidden fallback; accounting separated).
- `src/slaif_local_coding/constitution/bundles/bundle_compile_work.py`
  (new): compile-through-RAM composition over the 019-b work plane (019
  single-flight, 020 needed-only restart preparation).
- `src/slaif_local_coding/constitution/bundles/bundle_selection.py`
  (new): deterministic required-then-optional selection (stable ordering,
  scoped root/authority, missing-binding guidance, overlap coverage,
  whole-entry optional omission, typed essential overflow, same-full-key
  reuse, stale-replay refusal).
- `src/slaif_local_coding/constitution/bundles/tokenizer_assets/` (new):
  the four pinned assets (tokenizer.json 12809320
  0997f410…; chat_template.jinja 9004 af16f654…;
  tokenizer_config.json 9984 207c03c4…; LICENSE 11544 bbedc3fd…) + NOTICE.
- `tests/` (new): `test_bundle_tokenizer.py`, `test_bundle_budget.py`,
  `test_bundle_compiler.py`, `test_bundle_compile_work.py`,
  `test_bundle_selection.py` (focused 021 matrix: 113 tests).
- `pyproject.toml` / `uv.lock`: the authorized minimal locked CPU
  dependency `tokenizers==0.22.2` (packaging allowlist updated).
- `packaging/dev_provenance_manifest.json`: refreshed at source A2
  (manifest-only B2; 310 inputs; wheel/sdist hashes bound).
- `docs/CACHE-TOKEN-COMPILER-CONTRACT.md` (new owning contract);
  `docs/CACHE-IMPLEMENTATION-PLAN.md` / `docs/CACHE-REWORK-LEDGER.md`
  (current criterion ledger updated); `ARCHITECTURE-for-agents.md` and
  compact mirrors updated as needed.
- FIX COMMIT 23936e7 (this round's in-scope CI repair; 2 files,
  +199/−1):
  - `scripts/docker_qualification_ci.py`: `_slaif_marker_applies` now
    recognizes a top-level (outside single-quoted literals) ` or ` ONLY
    when every term fullmatches `platform_machine == '<arch>'` with a
    simple quoted architecture name (`[A-Za-z0-9_]+`); the disjunction
    applies iff the platform machine equals one listed name; a missing
    `platform_machine` fact and every other disjunction shape raise
    ValueError (fail-closed); the and-grammar path is byte-for-byte
    unchanged for markers without a top-level outside-quotes ` or `
    (including quoted literals that legally contain the text ` or `).
    The in-image audit embedding (inspect.getsource of the same
    function) carries the new logic; the in-image driver already imports
    `re`.
  - `tests/test_runtime_lock_ci.py`: +21 tests — exact lock-shaped
    positive (all five frozen names, supported x86_64 env), nonmatch
    (riscv64/ppc64le/armv7l/i686/x86 → False, never error), missing
    machine fact fails closed, the exact `uv export --frozen` hf-xet
    line parses to the exact marker, the quoted-literal-containing-` or
    ` compatibility case stays on the and-grammar (False/True as
    expected), 14 malformed disjunctions fail closed (generic or, mixed
    variables, non-machine term, non-equality op, unquoted literal, and
    inside a term, space/dot/empty names, parentheses, dangling or,
    leading or, double-space operator, quoted-or literal mixed into a
    disjunction), and two skip-pin closure tests over the real frozen
    marker (applicable → required at the locked version; nonmatching
    machines → pin must be absent).

## Verification
- Focused closure/marker suite at B2:
  `uv run --frozen pytest tests/test_runtime_lock_ci.py -q` — PASSED
  (61 passed; the 21 new tests above; ruff check, ruff format --check
  and mypy on both changed files — PASSED).
- 15-command frozen gate at exact B2 d73eade
  (`gate-driver-021a-r9.sh`, managed foreground absolute-path
  invocation, private capture parent umask 077, full-pytest child umask
  022, run dir gate-run9, driver pid 1371874, startup
  source_sha256 70a1887c0e9b85c624b688ae019eb5f5894a0ad697ea65aa8036bbf5ec1fdaf8,
  head d73eade): ALL 15 commands rc=0 — cmd01 `uv lock --check`; cmd02
  `uv sync --frozen --extra dev`; cmd03 ruff check; cmd04 ruff format
  --check; cmd05 `mypy src tests`; cmd06 docs consistency; cmd07 full
  `uv run --frozen pytest -q` — 6935 passed, 28 skipped, 16 warnings,
  1363.53 s; cmd08 `uv build`; cmd09/10 artifact policy (inspect +
  install smoke); cmd11 Python 3.12.15; cmd12 compileall; cmd13
  dev-provenance verify vs dist; cmd14 shell syntax; cmd15
  `git diff --check b9c6b41… HEAD`. PASSED
  (gate-run8, a detached attempt at the same head, died after cmd06
  with no cmd07 result and is preserved intact as an incomplete
  diagnostic; it earns no gate result.)
- One clean exact-B2 Git archive build (clean-build-021a-r5, fresh
  protected paths, literal exact-B + exact-parent guards, umask 077):
  archive exit 0 (38041600 bytes), extract exit 0 (942 files),
  `uv build` exit 0; BOTH artifacts byte-identical to the committed
  manifest — wheel sha256
  4a0015fd3068a44f16c1686c3094f5ff20f84bf52f65770153c9f9b70a16ef6f
  (4387258 bytes, 85 entries) and sdist sha256
  ffdcc5cb0f0fa0af293b9c30e10f84cdda152f9d025add46510f2f60287b402c
  (6032018 bytes, 308 entries). PASSED
- Full clean-archive BOTH artifact proof on the same clean artifacts
  (`artifact-proof-021a-r4.py`): ALL PROOF ASSERTIONS PASSED — 942 clean
  archive files byte-identical to Git B2; 310 manifest source inputs
  byte-identical to original Git A2, Git B2 and the clean tree; B2
  manifest-only (sole parent A2; exactly
  packaging/dev_provenance_manifest.json changed); sdist 308 entries
  (307 source-verified + 1 generated PKG-INFO whose bytes equal wheel
  METADATA); wheel 85 entries (79 runtime entries byte-identical to
  Git src/; RECORD full entry-set coverage incl. self row; per-entry
  sha256 digest + size verified; unique raw rows); entry_points.txt
  equals pyproject [project.scripts]; LICENSE/NOTICE byte-identical;
  repo dist/ artifacts byte-identical (sha256+size) to the clean
  artifacts. PASSED
- GitHub checks at implementation head d73eade (TEN exact-B checks):
  CodeQL success; cache-native-containment success; cache-native-fixture
  success; docker success; docker-published success; gateway-contract
  success; operator-session success; test success; Analyze (actions)
  success; Analyze (python) success. All required green at drafting: YES.
  (At the prior head 6772517: 9/10 success and `docker` FAILED in the
  in_image_provenance phase — ValueError on the frozen hf-xet marker —
  repaired by A2 and re-verified green at d73eade. Report-head checks
  may be pending after the report push; strategy verifies.)
- Unearned layers NOT RUN: 022 opt-in config and transactional source
  replacement/forwarding; 023 full stack; 024 genuine Codex/actual-model
  qualification; real inference in the compiler order. Skipped/pending/
  missing is never reported as pass.

## Live model/service evidence
- No live model call from this host in this round; no protected
  18020/Qwen/Codex fixture touched. The `docker` check ran on a
  disposable GitHub runner (canonical port 18031, fake upstream, no
  protected fixture on this host); the runner is not this protected
  host and no host service state was changed.

## GitHub CI / required checks
- Implementation-head (d73eade) check state: the TEN success states
  listed above, observed before the report commit.
- All required green at drafting: YES.
- Report-head checks may be pending; strategy verifies.

## Local setup/dependencies
- uv frozen repo venv, Python 3.12.15; no new dependencies (the
  tokenizers==0.22.2 pin was already part of the 021 source stage).
- All manual artifacts under
  /home/janezp/codex-supervision/slaif-local-coding/work-artifacts/oap-021a-work/
  (0700 dirs, 0600 files): gate-driver-021a-r9.sh + gate-run9 captures,
  build-021a-r5.sh + clean-build-021a-r5 captures,
  artifact-proof-021a-r4.py + proof JSON, preserved incomplete
  gate-run8, and prior-round evidence.

## Documentation
- The closed marker-grammar contract is owned by the
  `scripts/docker_qualification_ci.py` docstring (updated with the
  exact disjunction shape rule) and the focused tests (extended); no
  standalone docs section owns this grammar (verified by inspection),
  so no doc/ file change is required for the fix. The development
  provenance manifest was refreshed at B2 (order-mandated: every later
  source change requires a refreshed development manifest). Order and
  active bytes are unchanged.

## Safety/scope confirmations
- Unrelated files: NO (fix commit = exactly 2 files; manifest commit =
  exactly 1 file).
- Secrets/raw content: none in this report or the pushed diff (hashes,
  counts, command names, exit codes, SHAs only).
- Production/protected resources: unchanged.
- Protected 18020/Qwen/Codex fixture changed: NO.
- Required tests skipped/not run: the 28 full-pytest skips are the
  pre-existing honest live-credential/fixture skips; the unearned 022–024
  layers are NOT RUN as stated.
- Scope deviation: none (the fix is the exact in-scope CI repair the
  round's verification phase requires).
- Extra objective PR: NO (PR 29 only); coding merge: NO; auto-merge:
  NONE.
- Active/order edited: NO; report commit report-only: YES (single new
  path oap/reports/021-a-cache-token-compiler.md; verified against the
  remote after push).

## Known limitations/blockers
- None at this scope. gate-run8 remains an incomplete diagnostic only
  (no gate result claimed from it). The 021 component is INERT: no
  runtime success claim is made from it.

## Recommended strategic follow-up
Factual only: strategic review/acceptance of PR 29 at head d73eade; per
the current criterion ledger the next mandatory stages are 022 (opt-in
config and transactional source replacement/forwarding), then 023 (full
stack) and 024 (genuine Codex/actual-model qualification).

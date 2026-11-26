# OAP Coding-Agent Report — 022-a

## Work order
- Identifier: 022-a; order path `oap/orders/022-a-cache-source-replacement.md`; numeric objective 22
- PR mode: CREATE_NEW_PR from verified remote main `144af0bd5e34387afcb8e3f9ddf761eabd56e817`
- PR 30 https://github.com/ulfe-lmi/slaif-local-coding/pull/30 (state open;
  the ONE new PR for numeric objective 22; unrelated PR 23 preserved)

## Status
COMPLETE

## Executive summary
Actual result: the first same-objective slice (validated opt-in cache
configuration and pure context contract) is implemented at source A
`e4e3ad1afd2aa9ba2100dfe73bb164b4ee8d1ee9` on the ONE new branch
`oap/022-cache-source-replacement` (PR 30): (1) the explicit
`[context_cache]` profile selector in `Settings` and the TOML loader —
omission keeps legacy behavior, `legacy` selects it explicitly,
`dependency-bundles-v1` is a closed typed configuration (admission default
`lean`, `greedy` explicit, unknown/incompatible/ambiguous fail closed) —
plus the migration conflict law: an explicitly supplied legacy cache/TTL/
LRU, derived rehydration, byte-injection, compiler or selector policy
conflicts with v1 even at its default value, while materialized defaults or
an empty policy block alone do not, and common flags (`constitution.
enabled`, route observation/constitution, validated identity source/labels)
are reused with legacy compiler/selector rules applied to legacy only;
(2) the explicit effective context and 021 budget bounds validated against
each enabled v1 route's declared model/vision contract, reusing
`BundleBudgetConfig`, the pinned tokenizer/render capability and
`BundleCompilerConfig` or their validators, with compiler revision/
compatibility bound to the actual configured effective C, reserves and
capability (never a model alias, executor setting or upstream maximum
alone) and changed effective C / compiler compatibility proven a distinct
budget/compile policy through the 021 identity recipe; no tokenizer load at
legacy startup; (3) the explicit v1 protected-recovery opt-in and
configured root, the existing one-worker policy and explicit bounded
process/session RAM ownership using the accepted 019/020 types, with
configuration validation never opening/creating/enumerating/probing a
recovery store, resolving a request workspace, reading credentials or
calling an upstream, fixed error messages without private-path/credential
echo, and the compiler protected-environment credential law (never a
Gateway credential); (4) the fixed `create_app` startup refusal of a valid
selected v1 profile for unavailable v1 runtime, before constructing an HTTP
client, legacy cache or recovery owner, with legacy entry points unchanged.
The later 022 slices (exact-span replacement, trusted upstream issuance,
protected checkpoint and forwarding integration, full actual-upstream
R01–R05/S01–S02 evidence) are NOT implemented in this round, per the order.
Live model inference remains NOT RUN.

Known limitation found by strategy and recorded without a code change this
round: a synthetic malformed legacy TOML value can be echoed in a
configuration error before the v1 migration refusal is reached. The frozen
code and the activated order are left untouched in this round; the
correction is reserved for the next same-PR order.

## Authoritative GitHub state
- Repository: ulfe-lmi/slaif-local-coding; PR 30
  https://github.com/ulfe-lmi/slaif-local-coding/pull/30 (state open)
- Base: main `144af0bd5e34387afcb8e3f9ddf761eabd56e817` (order-verified
  remote main, the accepted 021 merge)
- Head: oap/022-cache-source-replacement
  `d34c989e0e8381ef1f09833e5da764aed496eb11`
- Implementation head SHA: d34c989e0e8381ef1f09833e5da764aed496eb11
- Report publication commit: SELF
- Implementation structure: source A `e4e3ad1afd2aa9ba2100dfe73bb164b4ee8d1ee9`
  (the 022-a configuration/app/docs slice; sole parent `144af0b`, the
  order-verified remote main) and manifest-only B `d34c989` (sole parent A;
  exactly `packaging/dev_provenance_manifest.json` changed; 310 source
  inputs; wheel/sdist dev hashes `98351a42…` / `01dfa9bc…`). The exact
  activated order bytes and `oap/active` are committed in the branch and
  published on the PR (blob sha256-verified against the working tree at B).

## Verification
- Focused suites at source A (before the candidate freeze): config/app
  `187 passed in 1.97s`; route/selection policy `74 passed in 13.94s`;
  ruff check, ruff format --check, mypy and docs consistency green before
  the freeze (and re-proven at exact B by gate cmd03–cmd06 rc=0). The exact
  focused logs are preserved under the work directory as
  `focused022a-exact.log` and `policy022a-exact.log` (moved from /tmp);
  earlier-timing duplicates `focused022a.log` / `policy022a2.log` are
  preserved intact as superseded.
- 15-command frozen gate at exact B (`gate-driver-022a.sh`, managed
  foreground absolute-path invocation, run dir `gate-run1`, driver pid
  1475776 birth 370873326, ppid 598258, uid 1001, capture umask 077, driver
  source_sha256 `54c92e017bc6b98f025108faaaebe8166e17b81458390a6d176c8fbac8b7e1f1`,
  started 2026-11-19T13:41:55Z, head `d34c989`): ALL 15 commands rc=0 —
  cmd01 `uv lock --check`; cmd02 `uv sync --frozen --extra dev`; cmd03
  ruff check; cmd04 ruff format --check; cmd05 `mypy src tests`; cmd06 docs
  consistency; cmd07 full `uv run --frozen pytest -q` — 6985 passed, 28
  skipped, 16 warnings, 1368.12 s; cmd08 `uv build`; cmd09 artifact policy
  inspect (no violations); cmd10 artifact policy install-smoke (fresh
  disposable venv, `ok: true` — the required supported Python 3.12 fresh
  noneditable install smoke, module imported from the disposable venv only);
  cmd11 Python 3.12.15; cmd12 compileall; cmd13 dev-provenance verify vs
  dist; cmd14 shell syntax; cmd15 `git diff --check 144af0b… HEAD`. PASSED.
- TEN required exact-B GitHub checks at `d34c989`: ALL pass — test (retry,
  see below), Analyze (actions), Analyze (python), CodeQL,
  cache-native-containment, cache-native-fixture, docker, docker-published,
  gateway-contract, operator-session. The initial `test` job
  (135600198777, run 44535644455) FAILED once: 6984 passed / 28 skipped /
  1 failed — `tests/test_cache_native_fixture_local.py::test_run_id_
  mismatch_and_malformed_refused` with local-control-protocol non-convergence
  at prepare while the owner thread did not converge. That file is
  byte-identical to the base (the base→B diff contains only the 13 expected
  022-a paths) — a flake, not an in-scope regression. Exactly ONE retry of
  only the failed job at the same B (`gh run rerun 44535644455 --failed`,
  job 135611955608) PASSED (12m37s); the initial failure is preserved here
  and no product/test change was made.
- Clean exact-B archive, one clean build per run (fresh protected paths,
  fail-closed no-overwrite guards, startup metadata after run-dir creation):
  - Run 1 (`clean-build-022a`, `build-022a.sh`): git archive of B (38,144,000
    bytes, 944 files), extract and `uv build` exit=0 with BOTH artifacts
    byte-identical to the manifest; the fresh-install step then died on a
    `noclobber` redirect bug in its own driver (truncating `2>` on the
    append step; `install.exit=1` recorded) and the run is preserved intact
    as an incomplete diagnostic; it earns no install result.
  - Run 2 (`clean-build-022a-r2`, `build-022a-r2.sh`): the clean build
    earning the result — archive/extract/build exit=0; BOTH artifacts
    byte-identical to the manifest (wheel `98351a423884…`, 4,391,508 bytes,
    85 entries; sdist `01dfa9bc5ab9…`, 6,040,006 bytes, 308 entries); fresh
    NONEDITABLE install of the clean-built wheel exit=0 with import probe
    (version 0.1.0, module resolved inside the disposable venv only,
    console entry point present). The run-2 supplemental fresh install used
    Python 3.14 (the local `python3`); the required supported Python 3.12
    fresh noneditable install smoke is established by gate cmd10.
  - Full clean-archive BOTH artifact proof (`artifact-proof-022a.py`,
    `clean-build-artifact-proof-022a.json`): ALL PROOF ASSERTIONS PASSED —
    944 clean-archive files byte-identical to Git B (full path set); 310
    manifest source inputs byte-identical to the ORIGINAL Git A, to Git B
    and to the clean tree; B manifest-only (sole parent A, exactly the
    manifest path changed); every sdist entry allowlisted-generated (one,
    PKG-INFO) or byte-identical to Git B; every wheel runtime entry
    byte-identical to Git B `src/`; wheel RECORD exactly covers the entry
    set with per-entry sha256 digest and size (unique raw rows, no
    collapsing); PKG-INFO bytes equal wheel METADATA bytes; entry_points
    equal pyproject `[project.scripts]`; LICENSE/NOTICE byte-identical; repo
    gate `dist/` artifacts byte-identical to the clean artifacts.
- Live model inference: NOT RUN. The protected Qwen/18020 service,
  profiles, launch/systemd, keys and network state were not touched; no dev
  service was started; no registry publication, deployment, benchmark or
  cutover. No merge, no auto-merge.

## Known limitations (unchanged this round)
- Strategy-found: a synthetic malformed legacy TOML value can be echoed in
  a configuration error before the v1 migration refusal is reached; the
  order's fixed-message / no-echo requirement is not fully met on that
  narrow path by this round's frozen code. Frozen code and order bytes are
  untouched here; the correction is reserved for the next same-PR order.
- v1 remains unwired: `create_app` refuses a selected v1 profile by
  design. No v1 readiness, source-replacement, native-format, streaming or
  recovery qualification is earned; full 022 and later runtime/client
  criteria remain unearned. This report is a claim until strategic review;
  no acceptance or merge is claimed.

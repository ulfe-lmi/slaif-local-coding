# OAP Coding-Agent Report — 004-m

## Work order
- Identifier: `004-m`
- Work-order file: `oap/orders/004-m-reconcile-native-codex-environment.md`
- Numeric objective: `004`
- PR mode: `AMENDED_EXISTING_PR`

## Status
PARTIAL

## Executive summary

The repository-only Codex helper now keeps `CODEX_HOME` in fresh disposable
state while retaining inherited host `HOME` and `TMPDIR` semantics when
present, and it continues to pass only the existing non-secret allowlist plus
the explicitly named credential. Focused and full local verification passed.

The one authorized native Codex 0.149.0 preflight still stopped at its first
no-model `true` probe with exit status 1. The exact dependency `cat`, candidate
adapter, model calls, and governed/cache-reuse E2E were not run. The prior
`HOME`/`TMPDIR` rewrite is therefore not established as the cause, and no
Local Coding defect has yet been tested.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`
- PR number/URL/state: #6, `https://github.com/ulfe-lmi/slaif-local-coding/pull/6`, OPEN, non-draft, MERGEABLE
- Base/head: `main` / `oap/004-real-codex-governed-e2e`
- Required base: `7a2c36a0a40958a6059a765c2f9d5e5bf4ddc161`
- Starting remote SHA: `a724875f8196582b63415e68b7d6f05df1f0de75`
- Implementation head SHA: `97237cc8190eef08278f026673192aeab7466270`
- Report publication commit: SELF
- Implementation commits pushed before report: `97237cc8190eef08278f026673192aeab7466270` (`OAP 004-m: reconcile native Codex environment`)
- New PR this round: NO
- Amended existing PR: YES
- Merge performed: NO

## Changes and files
- `tests/helpers/e2e_support.py`: retained host `HOME`/`TMPDIR` semantics in
  the bounded subprocess allowlist and kept explicit disposable `CODEX_HOME`.
- `tests/test_e2e.py`: added environment-name, disposable-home, host-variable,
  unset-`TMPDIR`, and named-credential boundary assertions.
- `README.md`, `TESTING.md`, and `oap/COMPLETENESS.md`: documented the 004-m
  experiment and its bounded pre-product failure without a host-wide or
  product conclusion.
- Committed unchanged strategic activation bytes in `oap/active` and the
  exact `004-m` order file.
- No production adapter, dependency, service, or protected-host change.

## Acceptance evidence

### Criterion 1
- PASSED. `CODEX_HOME` is explicitly set to each fresh private fixture home;
  host `HOME` and `TMPDIR` are inherited only when present, and unset
  `TMPDIR` is omitted. The environment test proves the unrelated synthetic
  secret is excluded and the named credential is the only credential passed.
  Base Codex config hash remained
  `fefea020eae48d2f9821694f7f20376e13361d6649759925bfbd4eb8a23ad1fc` and the
  discovered active OAP profile config hash remained
  `3c58a4c6946db3e4b0c7c965d330342832f47913d190810167163d92436f61fd`.

### Criterion 2
- PARTIAL by the ordered first-failure gate. Codex `0.149.0` ran exactly one
  native `workspace-write`/`:workspace` `true` probe. It returned process exit
  status `1`, process status `failed`, timeout `false`; stdout was length `0`
  with SHA-256
  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
  Bounded stderr facts were length `262`, SHA-256
  `c86940e043081d5f52fad5bfa189aefdd6935f5cb59428c0620abc7f9b306b68`, class
  `not_found`, subclass `not_found`, two lines scanned, maximum line length
  `215`, and not truncated. The dependency fixture was length `127` with
  SHA-256 `2c936f6e0d380e91b5688d252e4c87f8b9ab2e2c3c75c081cdb23267a6110660`;
  exact `cat` was `NOT RUN`.

### Criterion 3
- PASSED for the no-model gate. One native helper call occurred before any
  dependency verification; zero model calls and zero candidate-adapter calls
  occurred. The failure stopped the sequence before dependency `cat`.

### Criterion 4
- NOT RUN. The two governed invocations and persistent cache-reuse proof were
  not authorized after native `true` failed.

### Criterion 5
- PASSED. No product fix or product-runtime change was made. A Local Coding
  defect was not reached.

### Criterion 6
- PASSED. Objective 004 remains `15%` and branch readiness remains
  approximately `74%`. The full-success `40%`/`79%` values are not claimed.

### Criterion 7
- PASSED for the named local gates and implementation-head CI. Environment
  allowlist, privacy, native first-failure, cache, and cleanup checks are
  covered by the focused/full suite; the ordered governed E2E remains `NOT RUN`.

## Verification
- `uv lock --check`: PASSED — 32 packages resolved without lock changes.
- `uv sync --frozen --extra dev`: PASSED — 31 packages checked.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen ruff format --check .`: PASSED — 125 files formatted.
- `uv run --frozen mypy src tests`: PASSED — no issues in 37 source files.
- `uv run --frozen pytest tests/test_e2e.py -q`: PASSED — 40 passed.
- `uv run --frozen pytest -q`: PASSED — 289 passed, 7 skipped; the skipped
  opt-in live-service tests remain `SKIPPED`, not passes.
- `uv build`: PASSED — wheel and source distribution built.
- Wheel/sdist boundary inspection: PASSED — wheel had 23 members and no
  E2E/sandbox payload; sdist had 147 members and retained repository-only test
  support, including the two E2E helper modules.
- `python3 -m compileall -q src tests oap/bin`: PASSED.
- `bash -n oap/bin/*.sh`: PASSED.
- `git diff --check`: PASSED.
- Changed-file secret/raw/private-path scan: PASSED — no real credential,
  bearer value, private path, raw diagnostic, or raw payload entered the diff.
- Caller-owned cleanup audit: PASSED — zero leftover directories for all four
  diagnostic temporary prefixes; no pre-existing host temporary state was
  deleted.
- Native preflight helper: PASSED as a bounded diagnostic; outcome
  `native_true_failed`, exactly one helper call, no retry.
- Protected before/after snapshot: PASSED — qwen-serving remained active and
  running, port 18020 remained listening, bounded health remained HTTP 200,
  authenticated model discovery remained HTTP 200, unit hash remained
  `64b3ccd5bdb64da4e3dcabca660fada8155583c96b6bc11de47536e595df5910`, and
  candidate port 18031 remained unused.

## Live model/service evidence
- Current protected Qwen/vLLM service discovery was read-only: existing 18020
  service active/running, bounded `/health` HTTP 200, authenticated `/v1/models`
  HTTP 200. The current OAP coding profile was identified without changing its
  bytes. No image proxy was assumed.
- Candidate adapter on 18031: NOT RUN; no listener remained.
- Authenticated model, tool, compiler, vision, compaction, and governed calls:
  NOT RUN after the native first failure.
- Protected 18020/Qwen/vLLM/model/key/systemd/firewall/VPN/network/Codex profile
  state changed: NO.

## GitHub CI / required checks
- Implementation-head check: `test` — SUCCESS for
  `97237cc8190eef08278f026673192aeab7466270`.
- All required implementation-head checks green at drafting: YES.
- Report-head checks: PENDING until this report-only commit is pushed;
  strategy verifies the final report-head result.

## Local setup/dependencies
- Used the existing repository-local frozen `uv` environment.
- No dependency, lockfile, package, service, sudo, model, profile, or host
  configuration change.
- Build/cache/bytecode outputs were ignored inspection artifacts and were not
  committed.

## Documentation
- Updated `README.md`, `TESTING.md`, and `oap/COMPLETENESS.md` for the
  corrected environment semantics and bounded 004-m outcome.

## Safety/scope confirmations
- Unrelated files changed: NO.
- Secrets, raw prompts/source/tool output/images, credentials, raw diagnostics,
  customer data, and private paths exposed or committed: NO.
- Protected 18020/Qwen/vLLM/Codex fixture changed: NO.
- Required governed E2E/model/live-adapter tests: NOT RUN after the ordered
  native first failure.
- Scope deviation: NO.
- Extra objective PR: NO.
- Coding-agent merge/auto-merge: NO.
- Activated order/active edited by coding: NO; exact strategic bytes committed
  unchanged: YES.
- Report commit report-only: YES.

## Known limitations/blockers
- Normal host `HOME`/`TMPDIR` plus disposable `CODEX_HOME` still fails before
  exact dependency bytes cross the native Codex boundary. The bounded stderr
  facts are recorded without raw text; no retry, raw probe, host repair,
  package repair, or further hypothesis was authorized.
- The 004-j raw probe remains only the narrower historical
  `raw_bwrap_unshare_all_loopback_bootstrap_failed` description. It was
  host-direct, not nested inside an outer Codex sandbox, but it does not justify
  a host/kernel-wide capability conclusion.
- No governed sentinel success, ordinary-read lifecycle, cache reuse,
  compaction, vision E2E, production readiness, or cutover readiness is
  claimed.

## Required report answers
1. The 004-j host-wide `bubblewrap_kernel_runtime_unsupported` conclusion was
   **not justified**; its raw probe supports only the narrower historical probe
   failure.
2. The raw 004-j probe was **host-direct**, not nested inside an outer Codex
   sandbox, based on the wrapper and sanitized process facts already recorded.
3. The raw-probe failure was **not established as a nested-sandbox artifact**,
   but neither does it establish a host/kernel-wide capability limit.
4. Host-direct Codex 0.149.0 still **did not demonstrate** native
   workspace-write use here: with host `HOME`/`TMPDIR` semantics and explicit
   disposable `CODEX_HOME`, `true` exited 1 and stopped before `cat`. This is a
   bounded result, not a host-wide unsupported claim.
5. Governed Local Coding E2E and cache reuse: **NOT RUN**, because the first
   native preflight gate failed.
6. First remaining failure: **before the Local Coding/product boundary**; no
   product defect was isolated. The rewritten `HOME`/`TMPDIR` was a concrete
   harness difference, but this experiment did not establish it as the cause
   or as a harness fault.

## Recommended strategic follow-up

Review the truthful repeated native pre-product-boundary failure and decide the
next bounded diagnostic or rerun policy. No host, Codex, bubblewrap, or product
repair was made in this round.

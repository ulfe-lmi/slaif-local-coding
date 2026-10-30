# OAP Round Report — 017-r: prepare the serial right-pane native fixture

Status: COMPLETE for the round scope (all ordered work executed and verified;
independent strategic review/acceptance pending; genuine native and v1 items
remain NOT RUN by scope, as listed below). Acceptance is never automatic from
green CI.

Implementation head SHA: 2ce9dcd904126be8458ae9e8391cc2bc4cae9ada
Report publication commit: SELF

## Objective, PR, and reconciled state

- Order: `oap/orders/017-r-right-pane-native-fixture-preparation.md`;
  `oap/active` = `017-r` (6 bytes). Both committed at activation commit
  `88f368f` and byte-unchanged through the implementation head (verified by
  path-scoped history and tree inspection at `2ce9dcd`).
- PR #25 `https://github.com/ulfe-lmi/slaif-local-coding/pull/25`, branch
  `oap/017-cache-read-observation`, base `main` @
  `96c790423f6f0097a56a0b12bacda8a9b6da6aba`. AMEND_EXISTING_PR. No second
  PR, no merge, no auto-merge.
- Q SELF `d688cc40dc0cd33d2904cd3a09e3a5408752f19a` and sole implementation
  parent `0f3d2bab48ad015a51140370d66f63a69d33a613` at start; R control OK
  consumed exactly once at round start; never re-read or replayed.
- Source A7 `a66b3eaa9f5973c7ff1eeb18af7855f8f45e1252`; manifest B7 /
  implementation head `2ce9dcd904126be8458ae9e8391cc2bc4cae9ada` (B7 changes
  ONLY the development provenance manifest; sole parent A7).
- `src/` unchanged across R; no frozen-publication-path change; wheel identity
  unchanged from P (`1f2ebaff444be1ae90a7f1d863f462abcc82ff28caca448e28c206699fa4b50c`,
  142,753 B). Human handoff doc `docs/CACHE-REWORK.md` unchanged
  (`410df5c0b8f90b05220adc32c8e673b143c0cf1fa3da02270d91ac453c886abd`).

## Scope delivered (21 paths, +15854/-17 vs Q implementation parent)

- `.github/workflows/ci.yml` (+28): new Python-only `cache-native-fixture`
  job; all 9 pre-existing required checks preserved unchanged.
- `scripts/cache_native_fixture_model.py` (1558): typed phase/budget/closed-
  schema model (prepared -> measured -> synthetic scenario -> quiesced ->
  frozen selected snapshot -> teardown verified -> publication), closed
  validation-field diagnostic vocabulary, bounded mount-inventory
  classification (scanner cap 512, masked /dev/null alias admission,
  coherent alias/scanned/cap relation), subject group-membership contract
  (`[]` or `[SUBJECT_UID]`, exact non-bool integers only).
- `scripts/cache_native_fixture_controller.py` (1147): PID1 Python
  controller for UID 21001; issued registry, non-resettable ledger, bounded
  metadata diagnostic (fixed assistant text, no tools), SSE envelope paths
  matching public 0.164.0 wire vocabulary, quiesce/export ordering.
- `scripts/cache_native_fixture_standin.py` (1555): Python-only stand-in
  subject for UID 21002; actual exec measurements (uid/gid/groups,
  capability sets, NoNewPrivs, seccomp, namespace comparison, loopback-only
  network, keyring denial via the reviewed harmless NULL/unknown-command
  ABI, memory/swap/PID/storage bounds), measured mount inventory, bounded
  output capture, pidfd-based exact-identity termination (no numeric-PID
  fallback).
- `scripts/cache_native_fixture_ci.py` (3528): host runner for the
  disposable hosted CI; closed Docker command allowlist through a mandatory
  guarded executor/ledger, pinned base and fixture image build, public
  artifact acquisition with pre-extraction size/digest bounds and NOTICE
  retention, 10 fresh-container scenarios, ordered teardown-before-
  publication, protected atomic publication (0700 dir / 0600 file,
  refuse-overwrite, commit-boundary safe), closed fail-token diagnostic
  channel (fixed stage + known validation-field categories only; unknown/
  canary/oversized text never reflected).
- `scripts/cache_native_fixture_export_client.py` (255): trusted 21001
  exporter client over the peer-verified Unix socket; deadline-bounded
  reads; snapshot digest revalidation.
- `scripts/cache_native_fixture.Dockerfile` (59): fixture image (python
  3.12-slim-bookworm pinned by digest; users 21001/21002; bounded tmpfs
  roots; no host materials).
- Tests (all Python-only; fake executors/sockets/registries; tiny exact-
  owned Python children where a real process is needed):
  `tests/test_cache_native_fixture.py` (207 model),
  `tests/test_cache_native_fixture_controller.py` (33),
  `tests/test_cache_native_fixture_standin.py` (76),
  `tests/test_cache_native_fixture_ci.py` (218) — 534 total.
- Docs: `docs/CACHE-OBSERVATION-CONTRACT.md` (+406: fixture contract,
  confinement surface, syntax matrix for handoff 6.2 literals and D01-D10,
  section 11c serial foreground handoff runbook — preparation only),
  `docs/CACHE-REWORK-LEDGER.md` (R stage entries), `TESTING.md` (+95:
  fixture suites, Python-only CI job, umask-022 gate context, frozen-probe
  interpreter requirement), `ARCHITECTURE.md` and
  `ARCHITECTURE-for-agents.md` (+ byte-identical compact mirror): concise R
  entries — Python-only disposable-CI capability fixture, PENDING
  qualification, D09 NOT RUN.
- `packaging/dev_provenance_manifest.json`: B7 refresh, 192 source inputs.
- `oap/orders/017-r-right-pane-native-fixture-preparation.md` + `oap/active`:
  exact activated order and active committed.

## Fixed confinement bounds (documented; measured on CI, not inferred from argv)

Memory 1073741824 B (1 GiB); swap 0 via v2 `swap.max` (measured source
`v2-swap-max`); CPU 1; PIDs 96; writable data mounts 4 x 64 MiB =
268435456 B (256 MiB effective total: `/run/slaif-ctl` 21001:21001 0700,
`/run/slaif-subj` 21002:21002 0700, `/tmp` 21002:21002 0777, `/dev/shm`
64 MiB 1777); network none (loopback-only); read-only rootfs; cap-drop ALL;
no-new-privileges; seccomp builtin; private pid/mount/ipc/uts/net
namespaces; no host bind mounts/devices/socket/home/repository/auth/history/
profile materials; `--log-driver none` verified by actual inspect; no secrets
are forwarded to the fixture. Missing/unlimited/mismatched facts fail closed.

## Measured hosted CI success (closed record)

Run 40202693032 at `2ce9dcd`: all 10 expected checks SUCCESS — CodeQL
(run 40202690319), docker, gateway-contract, test (job 121197015145, 6m28s),
cache-native-fixture (job 121197015135, 79s), cache-native-containment,
operator-session, docker-published, Analyze (actions), Analyze (python).
Closed final record (schema `slaif-cache-native-fixture-ci-v1`, status
`pass`) retained at
`/home/janezp/codex-supervision/slaif-local-coding/reviews/017-r-fixture-2ce9dcd90412.json`
(0600):

- Subject (exec as 21002, measured): uid 21002, gid 21002, groups `[21002]`
  (own-primary-GID variant; the groups contract accepts only `[]` or
  `[21002]`), 27 mount table records scanned, 5 verified masked /dev/null
  aliases, memory limit 1073741824, PIDs 96, CPU 1, swap source
  `v2-swap-max`, keyring probe errnos all 1 (denied).
- All 10 scenarios in their exact declared states: controller-measurement
  completed; exec-21002-measurement completed; pty-attach completed
  (`pty_attached: true`, separate profile file, no `[profiles.early-beta]`
  table); synthetic-success completed (quiesce closed-pass, export
  revalidated, export sha `c55f13c582fa7cdd995dc7ad7d6ed89bd85a916c04b974913700f5d4ab7a1d8b`);
  synthetic-fail failed-as-designed (exit 3, unissued provider state);
  synthetic-hang timed-out-as-designed (host_timeout, descendant_terminated,
  sentinel_survived); synthetic-output-cap cap-hit-as-designed (524288 B);
  export-fail failed-as-designed (`export-invalid`); quiesce-fail
  failed-as-designed (`quiesce-state`); controller-crash crashed-as-designed
  (exit 137).
- Teardown: container present before -> `absent-verified` after; image
  present before -> `absent-verified` after (verified absence, not a failed
  query); descendants 1 before -> 0 after; sentinel survived; export
  completed before teardown; `cleanup_exact_only: true`.
- Ledger (non-resettable): api attempts/requests 10/10; admitted 7, refused
  3; healthz attempts 9; docker admissions 108, refusals 0; bytes drained
  814917 / retained 552951; deadline_expired false.
- Publication: dir mode 0700 (448), file mode 0600 (384), snapshot digest
  match true.
- Artifact (static acquisition only): tag `rust-v0.164.0` -> commit
  `6aaac694803004a63c6f393d153c96d22521a6b9`; archive 114,979,035 B sha256
  `90dd0b03b28afcb7fa733a4f73b413db2916a47347efd43fb669cc1c774ee8e4`;
  extracted `codex-x86_64-unknown-linux-musl` 308,139,304 B sha256
  `b93f6811d3f653f0fb83be4050d857fb9abbb111dfa2ce160563327daff7f306`;
  LICENSE Apache-2.0 sha256 `d17f227e4df5da1600391338865ce0f3055211760a36688f816941d58232d8dc`;
  NOTICE (Ratatui-derived, MIT) sha256
  `9d71575ecfd9a843fc1677b0efb08053c6ba9fd686a0de1a6f5382fd3c220915`;
  signature verification NOT RUN.
- Runner: x86_64, kernel 6.17.0-1022-azure, runner Python 3.12.3, engine
  28.0.4, runc 1.5.2, base `python:3.12-slim-bookworm@sha256:782412e8...`,
  `codex_invoked: false` — the native binary was never executed, not even
  `--help`/`--version`.
- Base image pinned: `sha256:782412e85d0f0984994c290652577d4018aff08145c85b262bb63dc0c7522254`;
  fixture image `sha256:331e1a70ec585f6fb1494c8486faf77fb1e624cf5f0f5765f7c5bab83a92de94`.

This is NOT native Codex, model, or v1 qualification.

## Preserved failed CI runs (closed reasons only; no raw payloads retained)

1. Run 40190405368 @ `33458a9`, fixture job 121159999646: closed failure
   `confinement-value:Devices` — daemon-side `[]` serialization mismatch.
   Repaired in `8e56b54`.
2. Run 40193753511 @ `558a852`, fixture job 121170067027:
   `exec-measurement-failed` — child cause not yet surfaceable through the
   job log at that revision.
3. Run 40196182798 @ `dbde930`, fixture job 121177390762:
   `exec-measurement-failed`, detail `unlisted-writable-mount` — runc
   1.5.2 maskPaths bind-masked files misclassified as writable data.
   Repaired in `709296b` (strictly-evidenced masked /dev/null alias
   admission).
4. Run 40198493538 @ `863e10d`: test job 121184416104 — 1 failed /
   2870 passed / 28 skipped; `test_masked_null_thermal_alias_admitted`
   depended on host paths (eager real lstat in the fake node helper);
   fixture job 121184416162 — `internal` with no stage/field attribution
   channel yet. Repaired in `b0d21d9` (host-path-independent lazy lookup;
   closed stage + known validation-field diagnostics).
5. Run 40201519961 @ `eaee7a7`, fixture job 121193510985: `closed record
   field state invalid: groups`, stage `exec-21002-measurement` — the
   invented empty-list-only groups law rejected the actual measured
   `[21002]`. Repaired in `a66b3ea` (finite two-variant contract).
   Measured array at success: `[21002]`.

## Verification record (all at literal implementation head 2ce9dcd unless stated)

- Full local TESTING gate, fresh run this round 2026-10-25 14:51:06Z-
  14:59:14Z at HEAD 2ce9dcd (log `/home/janezp/oap-017r-work/gate-b6-full.log`,
  0600): `uv lock --check` 0; `uv sync --frozen --extra dev` 0; ruff check
  "All checks passed!"; ruff format --check 0; `mypy src tests` 0;
  `scripts/docs_consistency_check.py` 0; `pytest -q` with process-local
  `umask 022` in the same shell invocation: **2919 passed, 28 skipped,
  0 failed** (481.13s); `uv build` 0; `artifact_policy_check --inspect` ok,
  0 violations; `--install-smoke` ok, 0 violations.
- Four fixture suites: 534 collected/passed (207 model + 33 controller +
  76 standin + 218 runner). P containment helper suite unchanged in meaning:
  61 tests, all pass.
- Frozen 21 strategic probes at literal `2ce9dcd`, repo Python 3.12
  (`/home/janezp/codex-work/slaif-local-coding/.venv/bin/python`): 21/21
  pass, all result heads 2ce9dcd, hash baseline unchanged (local
  `probes-final-2ce9dcd.json`); independently re-executed by strategic root
  with pre/post-run hash verification: 21/21
  (`reviews/017-r-independent-frozen21-2ce9dcd90412.json`).
- Installed-wheel observer controls at literal `2ce9dcd`, executed by
  strategic root from outside the checkout in fresh venv (Python 3.12,
  site-packages only, no repo on sys.path): 27/27 functional case checks
  pass (`reviews/017-r-installed-functional-2ce9dcd90412.json`); all 30
  installed package modules byte-match the wheel
  (`reviews/017-r-installed-wheel-identity-2ce9dcd90412.json`). Wheel bytes
  identical to P's (src/ unchanged); P's attribution evidence
  (`reviews/017-p-installed-functional-3db.json`, 27/27 at 3db699c) preserved.
- Supplemental pure strategic probes (selected AST / all-fake interfaces; no
  system interfaces; NOT part of frozen 21), all PASS at final source:
  model-wip 10/10; model-review2 9/9 (model `89df7e74...`);
  diagnostic-bounds 5/5; standin-mocked 20/20; controller-wire 7/7;
  controller-causality 6/6; runner-command-guard 8/8;
  runner-negative-evidence 6/6; mount-inventory 14/14
  (standin `554d1f9d...`); mount-counter-consistency 8/8 (model
  `b5173790...`); docker-schema-extended 12/12 (runner
  `58b25964...`); exporter-mocked 16/16 (exporter `cb6e1a64...`);
  evidence-ancestor-policy 14/14; model-diagnostic 8/8 (runner
  `93b73885...`); subject-groups 14/14 (model `e3caab1e...`).
- Focused privacy scan of the full round diff `0f3d2bab..2ce9dcd`
  (15,854 added lines), re-run this round with a closed pattern set:
  key-literal patterns 0 hits; private-upstream host/port patterns 0 hits;
  long-base64 payloads 0 hits; secret-assignment pattern 1 hit, classified
  benign: synthetic fake credential construction in
  `scripts/cache_native_fixture_standin.py` (fixed synthetic prefix plus
  truncated SHA256 of a per-run token; fake credential for the private
  loopback fake provider per order section 3; not a real credential). No
  real API keys, gateway keys, bearer headers, cookies, private URLs, or
  raw bodies appear in the diff.
- Development provenance: manifest B7 (source A7 `a66b3ea`, objective
  017-r) 192 source inputs match the current checkout; current dist matches
  the manifest. Clean git-archive reproduction performed this round at
  `/home/janezp/oap-017r-work/archive-final-2ce9dcd-v1` (0700): archive of
  `2ce9dcd`; 192/192 source-input SHA256s verified against the manifest;
  fresh Python 3.12 venv; `uv build` reproduced byte-identical artifacts —
  sdist `slaif_local_coding-0.1.0.tar.gz` 813,410 B sha256
  `f123635db71f4910b228d30700b690c8fad2a7673d26a42057a69fdc68b40044` and
  wheel `slaif_local_coding-0.1.0-py3-none-any.whl` 142,753 B sha256
  `1f2ebaff444be1ae90a7f1d863f462abcc82ff28caca448e28c206699fa4b50c`
  (evidence `archive-final-2ce9dcd-v1-evidence.json`, 0600). The earlier
  `archive-ctl` directory is an OLD control: an archive of B1 `33458a9`
  (fixture CI script and model test match B1, not B6; its sdist does not
  match the current identity); it is NOT the final archive proof and is not
  presented as current.
- GitHub: all 10 expected checks SUCCESS at `2ce9dcd` (see above); PR #25
  head = `2ce9dcd`, open, mergeable_state clean (read-only verified).
- PR metadata: title and body updated and remotely verified byte-identical
  to the intended 229-line body (12,971 B; remote adds one trailing
  newline) before this report was created. No metadata mutation after this
  report's parent.
- Owned evidence modes (verified immediately before this report): private R
  root `/home/janezp/oap-017r-work` 0700; all 40 owned root-level
  evidence/driver/output files 0600; subdirectories (archive-ctl,
  archive-final-2ce9dcd-v1, fresh-venv, fresh-venv-312) 0700 with internal
  content at tool modes (public repo content / tool byproducts, unchanged).
  Temporary /tmp metadata copies made during remote verification
  (`/tmp/pr25-remote-body.md`, 0664 when created, plus two verification
  copies) were removed before this report; they are not claimed to have
  ever been 0600.

## Deviations and disclosures

- Prohibited staging command: a `git add -A` invocation was used before
  commit `529a38d` ("017-r: closed stand-in fail-token diagnostic channel
  for the CI job log"), which the coding protocol prohibits. The resulting
  commit was independently verified to contain exactly the four intended
  paths (`TESTING.md`, `docs/CACHE-REWORK-LEDGER.md`,
  `scripts/cache_native_fixture_ci.py`,
  `tests/test_cache_native_fixture_ci.py`) and no unrelated paths. Exact-
  path staging was used for every commit since. No history was rewritten;
  the deviation is disclosed, not recast as compliant.
- Strategic root adapted UNFROZEN private probe fixtures only (no
  production changes, no frozen 21 changes): model-review2 baseline
  (alias-count 0; 9/9), mount-inventory harness (current 3-tuple + 9
  identity/classification controls; 14/14), exporter positive baseline
  (the earlier 15/16 run used an obsolete positive missing
  `snapshot.controller_ledger`, so its payload negatives were vacuous under
  that invalid baseline — that history is preserved, never described as
  waived or all-green; after the baseline fix, 16/16 with all 16 original
  assertions unchanged), model-diagnostic (8/8), subject-groups (14/14).
  Production validation was never loosened to satisfy probe fixtures.
- Invalid frozen-21 run preserved: the `probes-final-33458a9.json` run used
  ambient `python3` (missing `prometheus_client`; exit 1, no JSON,
  all_passed false) and is INVALID; valid runs at 558a852, dbde930 and
  2ce9dcd used the repo Python 3.12. The invalid record is retained for
  history.
- umask discipline (carried from P): host umask is 0002; `umask 022` was
  scoped in the same shell invocation as every required pytest run this
  round. No global/home/fixture/validator permission changes were made.
- P-round deviations (premature full-suite run against known-stale
  provenance; overbroad `pkill -INT -f "pytest -q"` and its unknown
  collateral impact) are recorded in the immutable P report
  `017-p-observation-native-fixture-prerequisites.md` and are not recast
  here.
- Q's wording limitations are recorded in the immutable Q report; the
  required clarifications appear in Appendix A below.

## NOT RUN / remaining (distinct from passes)

- D09 genuine native formats / native process+chunk collector: NOT RUN.
- Actual-trace process/chunk collection and versioned textual-vs-structured
  native output capture: NOT RUN (seams prepared only).
- Serial foreground handoff execution: NOT RUN — section 11c runbook
  preparation only; a later active order must authorize and record it.
- Native codex binary execution of any kind: NOT RUN (CI static
  fetch/hash only; `codex_invoked: false`).
- Public archive signature verification: NOT RUN (archive SHA256 only).
- Required-syntax scope audits for ls+cat and unguarded/labeled loop
  literals (and remaining matrix gaps): PENDING.
- Handoff-preparation qualification: PENDING strategic review of the actual
  job outcome. 017-p capability qualification: PENDING strategic review
  (its CI job is green at `2ce9dcd`).
- Objectives 018-024 v1 runtime work: NOT RUN. No v1 runtime is active or
  qualified. No real Codex E2E, model/GPU/gateway call, benchmark, RC/tag/
  registry/release/deployment/cutover occurred in R.

## Appendix A — Q wording clarification (Q bytes immutable)

1. Q's report phrase "measured public native client" refers to researched
   public release METADATA for codex rust-v0.164.0 (tag -> commit
   `6aaac694...`, archive SHA/size, LICENSE/NOTICE identities). Metadata
   does not measure a client. R fetches the public archive in CI and
   statically hashes it; it never executes the binary. All client-behavior
   claims remain NOT RUN until genuine execution is separately authorized.
2. Q's blanket "D01-D08 + D10 earned" claim is narrowed to what is actually
   proven: D01-D05 plus the named D06/D07/D08 slices and the D10 matrix;
   the ls+cat and unguarded/labeled loop literal scope audits remain
   PENDING. Per order section 6 this clarification is appended here rather
   than by rewriting Q.

## Closing

No secrets are forwarded to the fixture. This report-only commit changes
only `oap/reports/017-r-right-pane-native-fixture-preparation.md`; its sole
parent is the implementation head. After publication: no further mutation
of any kind; read-only verification only; then the single response FIFO
OK, then same-instance blocking wait for the next control.

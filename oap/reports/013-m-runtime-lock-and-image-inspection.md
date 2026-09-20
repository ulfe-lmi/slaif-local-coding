# OAP Coding-Agent Report — 013-m

## Work order
- Identifier: 013-m; order path: `oap/orders/013-m-runtime-lock-and-image-inspection.md`; numeric objective 013
- PR mode: AMENDED_EXISTING_PR (PR #15, no new PR)

## Status
COMPLETE

## Executive summary
M1: the demonstrated Docker runtime dependency-lock bypass is fixed and
mechanically re-proven. The build stage now exports the FROZEN runtime
closure from the committed `uv.lock` (`uv export`, no re-resolution) into
`/build/wheel/requirements-runtime-frozen.txt`; the runtime stage syncs the
frozen lock into the EXPLICIT `/opt/slaif/venv` (`VIRTUAL_ENV` +
`uv sync --frozen --no-dev --no-install-project --active` — a plain
`uv sync` targets the project `.venv`, which is the demonstrated defect) and
installs the built wheel with `--no-deps` (no second dependency resolution).
The in-image provenance gate was extended to inspect the ACTUALLY installed
distributions (in-image `importlib.metadata`) against the frozen closure plus
the product wheel, in BOTH build and published modes; missing, wrong-version,
or unexpected distributions fail closed. Fresh disposable Docker CI proves
the corrected image: the installed inventory is exactly the locked set
(anyio 4.14.2, pydantic 2.13.4, uvicorn 0.52.4, … — NOT the previously
drifted 4.15.1/2.13.5/0.53.0; win32-only `colorama` correctly absent: 18
pins, 17 applicable, 18 installed including the product wheel). M2: the
hardening/label phase now reads the ACTUAL image `Os`/`Architecture` via
`docker image inspect` (built tag in build qualification, pulled digest in
published mode) and asserts it in both modes; the OS-only container
`Platform` comparison is retired; all existing wheel/label/hardening/
signed-ingress/lifecycle assertions preserved (15/15 phases PASSED,
`image_platform: linux/amd64` observed). M3: the docker-published baseline
now queries GHCR package visibility via the DIRECT container-package
endpoint (`/orgs/ulfe-lmi/packages/container/slaif-local-coding`) with the
same ephemeral `packages: read` token and explicit API version 2022-11-28;
this round the endpoint RETURNED the package and the actual visibility
`private` was recorded (the legacy list endpoint's empty-list ambiguity is
gone; a denied query would record the exact nonsecret status as a
limitation). Two clean isolated builds of final source A agree (wheel
`ad6be6d2…` unchanged as required; sdist `4fc43041…` for the corrected
inputs); the provenance manifest (metadata B) was regenerated bound to A
with the 121-entry input map and the A/B binding is mechanically proven;
fresh normal CI is 5/5 SUCCESS. Source round only: no registry writes, no
workflow dispatch; the published-digest proof (same dependency check and
platform assertion applied to the subsequently pulled digest) remains
honest NOT RUN pre-publication, as does image-pull qualification.

## Authoritative GitHub state
- Repository: ulfe-lmi/slaif-local-coding; PR #15 OPEN
  https://github.com/ulfe-lmi/slaif-local-coding/pull/15
- Base: main `a04693e6792df6a8ad4262acfb46336a0f662202`; head branch
  `oap/013-mvp-release-publication`
- Starting remote SHA: `2d2a6a5b32ced6a5f6c3512c84504b1965721213`
  (verified report-only SELF child of implementation
  `1689817984fa4b653d2208ee908f0673002fd250`, per the order)
- Implementation head SHA: 39f453eb931ddbcfba7a12627b32a77939686688
- Report publication commit: SELF
- Implementation commits pushed before report: `1368e12cf67314ff03e24dc9198254e08c33e30b`
  (source M1-M3 + activated order/active byte-exact), `39f453eb931ddbcfba7a12627b32a77939686688`
  (provenance manifest rebind, derived metadata only)
- New PR this round: NO; amended existing PR #15: YES; merge performed: NO

## Changes and files
- `Dockerfile` (M1): build stage adds `uv export --frozen --no-dev
  --no-emit-project --no-hashes` of the committed `uv.lock` to
  `/build/wheel/requirements-runtime-frozen.txt`; runtime stage syncs the
  frozen lock into the EXPLICIT venv (`VIRTUAL_ENV=/opt/slaif/venv`
  `uv sync --frozen --no-dev --no-install-project --active`); the closure
  export is copied to `/opt/slaif/artifacts/`; the wheel installs with
  `--no-deps`. Base digests, build pins, stage set, `src` and `config`
  bytes, `uv.lock` all unchanged.
- `scripts/docker_qualification_ci.py` (M1+M2): new pure, fail-closed
  closure functions (`_slaif_canonical_name`, `_slaif_parse_frozen_pins`,
  `_slaif_marker_applies` closed-grammar PEP 508 evaluator,
  `_slaif_evaluate_runtime_closure`) embedded into the in-image audit via
  their own source (`_runtime_venv_audit_code`), so the image executes
  exactly the tested code; `in_image_provenance` now requires
  `closure.ok` (applies in build AND published modes — published mode
  covers the subsequently pulled digest); `hardening_and_labels` asserts
  the ACTUAL image `Os/Architecture` from `docker image inspect` in BOTH
  modes (record-declared platform in published mode with
  supported-platform fallback; supported platform `linux/amd64` in build
  mode); OS-only container `Platform` comparison retired; observed
  platform and image ref added to the failure diagnostic and phase output.
- `.github/workflows/ci.yml` (M3): the docker-published read-only registry
  baseline reads package visibility via the DIRECT container-package
  endpoint with the same ephemeral `packages: read` token and explicit
  `X-GitHub-Api-Version: 2022-11-28`; the legacy org package-list call (and
  its `packages_listed` fact) is removed; exact nonsecret status recorded
  as a limitation when the package is not returned. No new permissions,
  services, retries, or discovery framework.
- `scripts/release_provenance_manifest.py` +
  `tests/test_release_provenance_manifest.py`: generator/E3 objective
  bumped to `013-m` (established per-round pattern).
- `tests/test_runtime_lock_ci.py` (new, M1): 41 focused tests — canonical
  names; frozen-pin parsing with every malformed-line negative case
  (no/empty version, URL, extras, option lines, empty marker, duplicate,
  empty file); closed-grammar marker evaluation (win32/linux/version
  comparisons, zero-padded version tuples, `and` clauses, fail-closed on
  `in`/`not`/`or`/unknown-variable/quote-in-string); closure evaluation
  positive + every required negative (missing, wrong-version — the exact
  observed drift `anyio 4.15.1` vs locked `4.14.2` — unexpected
  distribution, inapplicable-marker dependency installed, product
  missing/wrong-version, unsupported marker); in-image audit code compiles
  and embeds the exact tested function sources; Dockerfile wiring proven
  from the committed bytes (`--active` explicit venv sync, `--no-deps`
  install, export-file copy, base pins unchanged).
- `docs/RELEASE-ARTIFACT-POLICY.md`: OCI bullet documents the explicit
  venv frozen sync + `--no-deps` wheel install, the in-image frozen-closure
  gate (both qualification modes), and the real image `Os/Architecture`
  assertion; Qualification bullet documents the corrected direct
  container-package visibility query.
- `oap/active` + `oap/orders/013-m-runtime-lock-and-image-inspection.md`:
  activated order/active committed byte-exact (order sha256
  `f81e6e475603f677f6687bc19f965609a8e617117a287df21d06c2cff8205d05`).
- `packaging/release_provenance_manifest.json`: regenerated (derived only),
  schema v5, objective `013-m`, bound to source A
  `1368e12cf67314ff03e24dc9198254e08c33e30b`, 121-entry input map.

## Acceptance evidence
### M1 — frozen runtime dependencies installed and proven
- Result: PASSED (fresh disposable Docker CI, build mode; negative cases
  locally).
- Evidence: CI run `35532178837` docker job 15/15 phases PASSED.
  `in_image_provenance` phase line: `runtime_lock_closure.ok=true`,
  `pinned_count=18`, `applicable_count=17`, `installed_count=18`, actual
  installed inventory exactly
  `annotated-doc 0.0.5, annotated-types 0.8.0, anyio 4.14.2,
  certifi 2026.7.22, click 8.4.2, fastapi 0.141.1, h11 0.16.0,
  httpcore 1.0.9, httpx 0.28.1, idna 3.19, prometheus-client 0.26.0,
  pydantic 2.13.4, pydantic-core 2.46.4, slaif-local-coding 0.1.0,
  starlette 1.6.0, typing-extensions 4.16.0, typing-inspection 0.4.4,
  uvicorn 0.52.4` — the previously drifted trio (anyio 4.15.1 / pydantic
  2.13.5 / uvicorn 0.53.0) is ABSENT; `colorama` (win32-only pin) correctly
  absent; retained wheel hash `ad6be6d2…` equals the manifest. Negative
  cases (missing dependency, wrong version, unexpected distribution,
  inapplicable-marker installed, product missing/wrong version,
  unsupported marker grammar) all fail closed: `tests/test_runtime_lock_ci.py`
  41/41 PASSED locally. Published mode applies the SAME check to the
  subsequently pulled digest: NOT RUN pre-publication (no RC exists yet —
  the `docker-published` job reports the explicit pre-publication NOT RUN).
### M2 — actual image Os/Architecture asserted
- Result: PASSED (build mode in fresh CI; published mode NOT RUN
  pre-publication).
- Evidence: `hardening_and_labels` phase line carries
  `image_platform: "linux/amd64"` (PASSED) read via `docker image inspect
  --format '{{.Os}}/{{.Architecture}}'` on the built image reference; the
  assertion runs in BOTH modes in code (published mode compares the
  record-declared platform, fallback supported platform). All existing
  wheel/label/hardening/signed-ingress/lifecycle assertions preserved
  (15/15 phases PASSED, incl. `bridge_positive_signed`,
  `bridge_negative_contract`, `fail_closed_readiness`,
  `operations_stop_start_recreate_upgrade_rollback`,
  `teardown_absence_proof`).
### M3 — corrected visibility query
- Result: PASSED (endpoint returned the package; actual visibility
  recorded).
- Evidence: docker-published job "Read-only registry baseline" logged
  `package visibility -> private` via
  `GET /orgs/ulfe-lmi/packages/container/slaif-local-coding` with the same
  ephemeral `packages: read` token and `X-GitHub-Api-Version: 2022-11-28`.
  Registry baseline unchanged: `0.1.0 -> digest:sha256:a5debcb24bb6bbf7cf00dbf80cd17367d57186f6b0d7fadac020b94df53a0011`,
  `sha-fe334e87c9f0fc65d1826cf9af7dad7e9f70a94a -> digest:sha256:a5debcb24bb6bbf7cf00dbf80cd17367d57186f6b0d7fadac020b94df53a0011`,
  `sha-be3c78b2016d5d40ce9155df8f94d14525c43d39 -> digest:sha256:15778b30d6a929d01fa42dffccc363f89967d22d92610466bb531cca5027e113`
  (orphan, actual current truth), `0.1.0-rc1 -> absent` (authenticated
  verified-absent). The L report's enum/platform assertions are corrected
  prospectively by this round's code/docs, never by editing its immutable
  bytes.

## Verification
- `uv run --frozen pytest -q tests/test_runtime_lock_ci.py` (new focused
  M1 negative cases + wiring): PASSED (41/41)
- `uv run --frozen pytest -q tests/test_release_provenance_manifest.py
  tests/test_source_input_binding.py`: PASSED (31/31 at manifest head)
- `uv run --frozen python scripts/source_input_map.py --ab
  1368e12cf67314ff03e24dc9198254e08c33e30b
  39f453eb931ddbcfba7a12627b32a77939686688 --manifest
  packaging/release_provenance_manifest.json`: PASSED (121 input files
  identical at A and B; A..B diff confined to derived metadata)
- two clean isolated `git archive` builds of A (`uv build`, isolated
  dirs): PASSED — both agree: wheel
  `ad6be6d2e8ad0f99eafb4be7b1c78efbcffe6de16e39106182d85db03933ce1e`
  (UNCHANGED, as required), sdist
  `4fc43041cc6c5f1fd92590cb24fa260d8ce2dbd8d599393fdad10eaff8a58659`
- `uv run --frozen ruff check .`: PASSED; `uv run --frozen ruff format
  --check .`: PASSED (392 files); `uv run --frozen mypy src tests`: PASSED
  (78 files); `python3 -m compileall -q src tests oap/bin scripts` +
  `bash -n oap/bin/*.sh packaging/*.sh`: PASSED
- `uv run --frozen pytest -q` (full local suite at manifest head): PASSED
  (1278 passed, 26 skipped — pre-existing conditional skips only: live
  tests require `SLAIF_LIVE_TEST=1`, Gateway162 focused tests require
  `SLAIF_GATEWAY_ROOT`, protected vision fixture requires human
  activation; one of these conditionals differs between this host and the
  CI runner, as in the previous round: local 1237/26 vs CI 1236/27)
- `uv run --frozen python scripts/docs_consistency_check.py`: PASSED
  (13 claim docs checked)
- CI run `35532178837` at implementation head `39f453e…`: 5/5 jobs SUCCESS
  (test 1277 passed/27 skipped; gateway-contract 18/18 frozen peer
  `08ca421b…` network guard enabled; docker 15/15 phases;
  docker-published incl. registry baseline + explicit prepublication NOT
  RUN; operator-session 19 phases)

## Live model/service evidence
- No live model inference was performed this round (none ordered; source
  round). Protected baseline verified before and after, row-identical:
  user unit `qwen-serving-vision.service` active/running, MainPID 23961,
  start `Sun 2026-09-06 18:57:26 CEST`; only 18020 listening among
  18020/18021/18031/18033/18034; `qwen-neumann` profile sha256
  `3aef2d8b819e9a5649c1fb739cd97b885cc69dbdf04eb15db7dcdbf4fac488bb`
  unchanged; frozen Gateway authority fixture
  `08ca421bee1ddca62078302b910e8be88cf705be` unchanged (not in diff).
  No host Docker daemon use, no Qwen inference, no protected resource
  touched.

## GitHub CI / required checks
- CI run `35532178837` (head `39f453eb931ddbcfba7a12627b32a77939686688`):
  `test` SUCCESS (1277 passed, 27 skipped); `gateway-contract` SUCCESS
  (18/18); `docker` SUCCESS (15/15 phases); `docker-published` SUCCESS
  (registry baseline recorded; explicit prepublication NOT RUN for the
  pull qualification); `operator-session` SUCCESS (19 phases).
- All required green at drafting: YES
- Report-head checks may be pending; strategy verifies.

## Local setup/dependencies
- Repository venv (`uv 0.12.5`, Python 3.12) only; no new dependencies, no
  new services. Clean isolated builds in `/tmp` (disposable). No sudo used.
  No durable setup changes beyond the committed source/metadata.

## Documentation
- Updated: `docs/RELEASE-ARTIFACT-POLICY.md` (OCI bullet: explicit-venv
  frozen sync + `--no-deps` install + in-image frozen-closure gate in both
  qualification modes + real image `Os/Architecture` assertion; Qualification
  bullet: corrected direct container-package visibility query). No README
  rewrite; no other doc drift (docs consistency gate PASSED).

## Safety/scope confirmations
- Unrelated files: none (diff vs starting head is exactly the 10 paths
  listed; no `src/`, no `uv.lock`, no `config/`, no gateway fixture, no
  base digests/build pins touched).
- Secrets/raw content: none in logs/artifacts/report (evidence uses
  hashes, version pins, status codes, fixed classes only).
- Production/protected resources: protected 18020/Qwen/Codex fixture
  changed: NO (before/after row-identical, above).
- Required tests skipped/not run: published-mode (pulled-digest) closure +
  platform proof and image-pull qualification are NOT RUN pre-publication
  by construction (no RC/final record exists); live-test matrix remains
  SKIPPED by its documented conditionals (unchanged). No scope deviation.
- Extra objective PR: NO; coding merge: NO; force-push: NO.
- Active/order edited: NO (strategic bytes committed verbatim; order
  sha256 above). Report commit report-only: YES (this commit stages only
  `oap/reports/013-m-runtime-lock-and-image-inspection.md`).
- Registry writes: NO; workflow dispatch: NO; Git tags/Releases: none
  created; visibility unchanged (M3 is read-only).
- Benchmark boundary: no benchmark design/code/tasks/judges/controller/
  ledger/A100 setup/pilot/experiment/statistics/telemetry/instrumentation.

## Known limitations/blockers
- The published-digest proofs (same frozen-closure check and real
  `Os/Architecture` assertion applied to the subsequently pulled digest)
  execute only when a publication record exists; honest NOT RUN this round.
- The optional visibility query returned `private` (recorded); no further
  visibility work is possible or ordered (a denied query would record the
  exact nonsecret status and stop).
- One pre-existing conditional test skip differs between this host and the
  CI runner (local 1278/26 vs CI 1277/27; same one-test class as the
  previous round's 1237/26 vs 1236/27).

## Recommended strategic follow-up
Factual only; strategy decides. This source state (A `1368e12…`, metadata B
`39f453e…`) passes the complete fresh normal CI with the corrected runtime
frozen-lock closure gate and the real image-platform assertion; the
`docker` CI job's existing release-build-command proof also passes. A later
RC publication from an exact reviewed source would exercise the published
mode (pulled digest) for the closure gate, the platform assertion, and the
signed-ingress/fail-closed/no-build/teardown assertions on the digest.

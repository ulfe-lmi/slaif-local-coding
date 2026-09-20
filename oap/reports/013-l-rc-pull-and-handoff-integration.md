# OAP Coding-Agent Report — 013-l

## Work order
- Identifier: 013-l; order path: `oap/orders/013-l-rc-pull-and-handoff-integration.md`; numeric objective 013
- PR mode: AMENDED_EXISTING_PR (PR #15, no new PR)

## Status
COMPLETE

## Executive summary
L1: the real pulled-image gate (`scripts/docker_qualification_ci.py`) now
consumes the generator's `slaif-rc-record-v2` through the existing strict v2
loader (reused, not reimplemented); the published qualification-label
comparison is bound to the committed manifest's state-bound label instead of
the hardcoded `mvp-release-0.1.0`; the published image inspection verifies
the record-declared platform (`linux/amd64`); malformed records — including
the superseded v1 key set — fail closed; all existing signed-ingress,
fail-closed, wheel, no-build, hardening, lifecycle and teardown assertions
preserved; focused consumer-integration coverage added (generated v2 temp
fixture accepted by the real published-mode loader/constructor; malformed
data rejected; no fake record in `packaging/`). L2: `render_handoff` emits
the correct two-brace Docker Go-template commands, renders the
`build_toolchain`/`base_images` facts, and links `INSTALL.md` at the literal
image source commit; `docs/DEPLOYMENT.md` current table aligned to v2/v5;
`docs/RELEASE-ARTIFACT-POLICY.md` publication introduction made durable
procedural language. L3: the `docker-published` CI job now records a READ-ONLY
authenticated registry baseline with its ephemeral `packages: read` token,
BEFORE the prepublication gate, using the existing strict resolver: this
round's fresh CI recorded the before baseline (see registry evidence). Source
round only: no RC digest claimed; image-pull qualification remains NOT RUN
pre-publication. Two in-scope CI repairs were required for the visibility
read (REST `package_type` value; owner-qualified name matching + list count),
each followed by the truthful A→B manifest rebind trail
(10ce438/75d9ac8 → 9cb6e64/ab90b79 → d0804e9/1689817).

## Authoritative GitHub state
- Repository: ulfe-lmi/slaif-local-coding; PR #15 OPEN
  https://github.com/ulfe-lmi/slaif-local-coding/pull/15
- Base: main `a04693e6792df6a8ad4262acfb46336a0f662202`; head branch
  `oap/013-mvp-release-publication`
- Starting remote SHA: `db5bf49612de39d40c4d1c459dc323dab9d92c97`
- Implementation head SHA: 1689817984fa4b653d2208ee908f0673002fd250
- Report publication commit: SELF
- Implementation commits pushed before report: 10ce438 (source L1-L3 +
  activated order/active), 75d9ac8 (manifest bound to 10ce438), 9cb6e64 (CI
  repair 1: REST package_type docker), ab90b79 (manifest rebind to 9cb6e64),
  d0804e9 (CI repair 2: visibility name match + list count), 1689817
  (manifest rebind to d0804e9)
- New PR this round: NO; amended existing PR #15: YES; merge performed: NO

## Changes and files
- `scripts/docker_qualification_ci.py` (L1): `_load_publication_record` now
  dispatches RC records to `_load_strict_rc_record`, which reuses
  `release_provenance_manifest.load_rc_record` (the existing strict v2
  loader); final-record path (`slaif-release-record-v1`) kept verbatim;
  hardcoded `PUBLISHED_QUALIFICATION_LABEL` and the superseded v1 RC key set
  removed; published label check binds
  `manifest["oci"]["labels"]["slaif-local-coding.qualification"]`; published
  image inspection adds `image_platform == record["image_platform"]`
  (linux/amd64 for the v2 RC record).
- `scripts/rc_artifact_record.py` (L2): RepoDigests inspect command now
  renders the valid two-brace Go template (was quadruple-brace, invalid);
  json-labels template kept valid (f-string brace escaping documented);
  `build_toolchain` and per-stage `base_images` facts rendered; INSTALL.md
  linked at the literal image source commit for exact-source
  Compose/config retrieval. Frozen-record/no-overwrite behavior unchanged.
- `scripts/release_provenance_manifest.py`: docstring schema reference
  corrected v1→v2 (the loader it describes is the v2 strict loader).
- `tests/test_docker_qualification_record_gate.py` (new, L1): 17 focused
  consumer-integration tests — generated v2 temp fixture accepted by the
  real published-mode loader and constructor; record_missing; 10 malformed
  v2 variants rejected; superseded v1 record rejected; RC-authoritative-when
  both exist; final record accepted alone; malformed final record rejected.
- `tests/test_rc_record.py` (L2): renderer assertions extended with the
  literal rendered Docker commands (exact `--format` lines), toolchain/base
  image facts, the INSTALL.md-at-literal-commit link, and a no-quadruple-
  brace invariant.
- `.github/workflows/ci.yml` (L3): new step "Read-only registry baseline
  (ephemeral packages:read token)" in the `docker-published` job BEFORE the
  prepublication gate — strict-resolver states for 0.1.0,
  sha-fe334e87c9f0fc65d1826cf9af7dad7e9f70a94a,
  sha-be3c78b2016d5d40ce9155df8f94d14525c43d39, 0.1.0-rc1 plus org docker-
  package list count and visibility read with the same credential (exact
  limitation recorded when unavailable); job header comment updated.
- `docs/DEPLOYMENT.md` (L2): current asset table rows aligned to
  `slaif-rc-record-v2` (full v2 fact list) and
  `slaif-release-provenance-v5`.
- `docs/RELEASE-ARTIFACT-POLICY.md` (L2): publication introduction is now
  durable procedural language (no round-specific zero-write claim); the
  Qualification bullet documents the L3 read-only baseline behavior.
- `oap/active` + `oap/orders/013-l-rc-pull-and-handoff-integration.md`:
  activated order/active committed byte-exact.
- `packaging/release_provenance_manifest.json`: regenerated (derived only),
  schema v5, bound to final source A `d0804e9...`, 120-entry input map.

## Acceptance evidence
### L1 — v2 record connected to the real pulled-image gate
- Result: PASSED (local consumer-integration + code-level binding).
- Evidence: `tests/test_docker_qualification_record_gate.py` 17/17 PASSED;
  generated v2 fixture accepted by `Qualification` (published mode) with
  `image_ref = <record oci_image_reference>@<record oci_image_digest>` and
  `source_commit` from the record; 10 malformed variants + legacy v1 record
  each raise `QualificationError(release_record, record_invalid)`; final v1
  record still accepted alone (RC/final distinction). No fake RC record in
  `packaging/` (only temp-dir fixtures).

### L2 — handoff renderer + two current doc references
- Result: PASSED.
- Evidence: rendered handoff contains the literal valid commands
  `docker image inspect "ghcr.io/ulfe-lmi/slaif-local-coding:0.1.0-rc1"
  --format '{{range .RepoDigests}}{{.}}{{end}}'` and
  `docker image inspect "<ref>@<digest>" --format '{{json .Config.Labels}}'`;
  `Build toolchain: backend hatchling==1.32.0, python 3.12, uv 0.12.5` and
  the three digest-pinned base-image lines render;
  `https://github.com/ulfe-lmi/slaif-local-coding/blob/<S>/INSTALL.md` with
  the literal source commit S; no `{{{{` anywhere. `tests/test_rc_record.py`
  PASSED (27/27). DEPLOYMENT.md table now v2/v5; RELEASE-ARTIFACT-POLICY.md
  introduction no longer claims "this round performs zero writes"
  (docs_consistency_check OK).

### L3 — actual private registry truth with the existing CI credential
- Result: PASSED (before baseline recorded by this round's fresh CI; after
  evidence will come from the published round's CI).
- Evidence: run 35528765082 (head ab90b79) docker-published job step
  "Read-only registry baseline": `0.1.0 -> digest:sha256:a5debcb2...a0011`;
  `sha-fe334e87... -> digest:sha256:a5debcb2...a0011`;
  `sha-be3c78b2... -> digest:sha256:15778b30...e113`;
  `0.1.0-rc1 -> absent` (verified absent); package visibility read: HTTP 200
  org docker-package list, no exact-name match (recorded
  `package-not-listed`). Run 35529144342 (head 1689817) re-records the same
  baseline with the list count and both name forms matched:
  `packages_listed=0`, `visibility=package-not-listed` (HTTP 200 empty list
  under the job token). Zero registry writes/dispatches; no tag
  mutation; no credential printing (token only via env); no new token,
  workflow, or service.

## Verification
- `.venv/bin/python -m pytest tests/test_docker_qualification_record_gate.py tests/test_rc_record.py -q`: PASSED (44/44)
- `.venv/bin/python -m pytest -q` (full suite at manifest head 75d9ac8): PASSED (1237 passed, 26 skipped — pre-existing conditional skips only)
- `.venv/bin/python -m pytest tests/test_release_provenance_manifest.py tests/test_source_input_binding.py tests/test_docker_qualification_record_gate.py tests/test_rc_record.py -q` (after final rebind 1689817): PASSED (75/75, includes E3 clean-A rebuild + working-tree binding gate)
- `.venv/bin/python -m ruff check .` / `.venv/bin/python -m ruff format --check .`: PASSED (clean)
- `.venv/bin/python -m mypy src tests`: PASSED (Success: no issues found in 77 source files)
- `.venv/bin/python scripts/docs_consistency_check.py`: PASSED (13 claim docs checked)
- `uv build --wheel --sdist` ×2 per rebind (clean `git archive` tree; isolated out/cache dirs; CPython 3.12.14 and 3.12.3): PASSED — wheel+sdist byte-identical across both builds in every rebind
- `sha256sum` of both wheels (final rebind d0804e9): PASSED — both `ad6be6d2e8ad0f99eafb4be7b1c78efbcffe6de16e39106182d85db03933ce1e` (order-required wheel unchanged; no drift)
- `.venv/bin/python scripts/artifact_policy_check.py --dist <clean dist> --inspect`: PASSED (ok:true, no violations)
- `.venv/bin/python scripts/artifact_policy_check.py --dist <clean dist> --install-smoke`: PASSED (ok:true, no violations)
- `.venv/bin/python scripts/source_input_map.py --ab <A> <B> --manifest packaging/release_provenance_manifest.json`: PASSED for each rebind — final: `input-map A/B binding OK: d0804e9194a8 == 1689817984fa (120 input files)`
- Local Docker/live-vLLM image pull qualification: NOT RUN (pre-publication; no RC record exists — explicit, not a skip of a required gate)
- Real Codex E2E: NOT RUN (not ordered this round)

## Live model/service evidence
- Private GHCR registry (READ-ONLY, authenticated with the job's ephemeral
  packages:read token via the existing strict resolver):
  - `0.1.0` → `sha256:a5debcb24bb6bbf7cf00dbf80cd17367d57186f6b0d7fadac020b94df53a0011` — EQUAL to prior evidence (no discrepancy)
  - `sha-fe334e87c9f0fc65d1826cf9af7dad7e9f70a94a` → same digest `sha256:a5debcb2...a0011` — EQUAL to prior evidence (no discrepancy)
  - `sha-be3c78b2016d5d40ce9155df8f94d14525c43d39` (orphan) → `sha256:15778b30d6a929d01fa42dffccc363f89967d22d92610466bb531cca5027e113` — actual current registry truth recorded; prior evidence did not state a digest for this tag and none was invented
  - `0.1.0-rc1` → `absent` (verified absent: the credential resolves the package and the manifest 404s)
  - Package visibility (final, run 35529144342): `packages_listed=0` and `visibility=package-not-listed` — the HTTP 200 org docker-package list is empty under the job token, so neither the bare nor the owner-qualified name form is listed and the visibility field itself is not observable through this endpoint; registry-level privacy remains established by the strict resolver's tri-state behavior (anonymous probes are denied; the job token resolves)
- Image-pull qualification: NOT RUN (no RC record exists yet — explicit pre-publication state)
- Protected host: NO mutation. No Qwen/vLLM/port/systemd/API-key/firewall/VPN/profile action performed (read-only status checks only).

## GitHub CI / required checks
- Implementation head `1689817984fa4b653d2208ee908f0673002fd250`, run
  35529144342: 5/5 SUCCESS — test SUCCESS (ruff/mypy/docs-gate clean;
  pytest 1236 passed, 27 skipped; uv build + artifact policy + install
  smoke), gateway-contract SUCCESS (frozen peer
  08ca421bee1ddca62078302b910e8be88cf705be), docker SUCCESS,
  docker-published SUCCESS (read-only baseline recorded; publication gate
  explicit NOT RUN pre-publication), operator-session SUCCESS
- Prior heads this round (superseded, evidence trail):
  - run 35528506711 @ 75d9ac8: 5/5 SUCCESS (docker-published recorded the
    first baseline; visibility read recorded `inaccessible (HTTP 400)` due
    to the invalid REST enum — repaired)
  - run 35528693324 @ 9cb6e64: FAILURE (test job only — the working-tree
    source-input binding check failed because the CI input changed ahead of
    its manifest rebind, the expected transient of the A->B rebind
    discipline; resolved by rebind ab90b79)
  - run 35528765082 @ ab90b79: 5/5 SUCCESS (baseline with corrected
    package_type; visibility recorded package-not-listed)
  - no workflow run is recorded at d0804e9; the following push 1689817 ran
    the full suite green (both repairs covered)
- All required green at drafting: yes
- Report-head checks may be pending; strategy verifies

## Local setup/dependencies
- Repo venv (Python 3.12.3) + uv 0.12.5; CPython 3.12.14/3.12.3 for the two
  clean isolated builds; no new dependencies; no sudo used.

## Documentation
- Updated in-PR: docs/DEPLOYMENT.md (current table v2/v5),
  docs/RELEASE-ARTIFACT-POLICY.md (durable publication introduction + L3
  Qualification bullet), scripts docstring (v2 reference). README untouched
  (settled). No other docs changed (scope law).

## Safety/scope confirmations
- Unrelated files: none touched beyond the named scope; pre-existing
  untracked `Local`/`clean`/`unchanged` preserved, not committed.
- Secrets/raw content: none in logs, diffs, or this report (token via env
  only; GH masks it in CI logs).
- Protected 18020/Qwen/Codex fixture changed: NO (read-only recheck
  before/after; see below).
- Required tests skipped/not run: image-pull qualification NOT RUN
  pre-publication (explicit, not a pass claim); real Codex E2E not ordered.
- Scope deviation: two in-scope CI repairs (visibility read) with truthful
  rebind trail; no other deviation.
- Extra objective PR: NO. Coding merge: NO. Force-push: NO.
- Active/order edited: NO (committed byte-exact as activated).
- Report commit report-only: YES (single path oap/reports/013-l-...).
- No benchmark code/design/tasks/judges/controller/ledger/A100 setup/pilot/
  experiment/telemetry/statistics/instrumentation; no src/, config/, or
  uv.lock changes; no registry writes/dispatch; no final v0.1.0 Git tag or
  GitHub Release; no visibility change; no final release claim; no
  protected-host cutover or Gateway routing mutation.

## Known limitations/blockers
- Package visibility via the REST package list with the job token (final,
  run 35529144342): HTTP 200 with `packages_listed=0` — the org docker-
  package list is empty, so the package's visibility field is not
  observable through this endpoint (recorded `package-not-listed`). No
  privileges were added and the package was not made public. Registry-level
  privacy remains established by the strict resolver's tri-state behavior
  (anonymous probes are denied; the job token resolves).
- The orphan tag `sha-be3c78b2...` resolves to a digest that prior evidence
  did not document; strategy may wish to adjudicate that orphan's provenance
  (no action taken by this round).

## Recommended strategic follow-up
Factual only: strategy selects the literal reviewed source S for the
human-authorized private publication round; the published round's
docker-published CI will then produce the after evidence (digest pull,
label set, platform check on the pulled image, signed-ingress run) against
the before baseline recorded here.

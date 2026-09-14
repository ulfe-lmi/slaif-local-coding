# OAP Coding-Agent Report — 009-a

## Work order
- Identifier: `009-a`; order path: `oap/orders/009-a-release-candidate-and-operational-closure.md`; numeric objective: `009`
- PR mode: CREATED_NEW_PR

## Status
COMPLETE

## Executive summary
Objective 000–008 merged truth was reconciled across all current-facing
documents (A); the release-artifact policy was closed and proven
mechanically with the wheel as the single supported distributable (B); the
single supported deployment path (systemd user service, repository venv,
loopback 18031) was documented with a complete operator contract (C); all
deployment mechanics were exercised end-to-end in a disposable environment
against fake loopback upstreams only and passed, including upgrade,
mechanical rollback, an injected failed start with recovery, a uniquely
named transient systemd unit, and cleanup with absence proof (D); a
content-free, schema-versioned, drift-gated release provenance manifest was
published (E); and the regression/CI gates were added with both required CI
jobs green at the implementation head (F). No cutover was performed;
nothing was released; the protected live Qwen/vLLM service was not mutated
(verified identical before and after). One deliberate runtime change was
required by an acceptance criterion (F4 call-out, see Changes).

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #11 — https://github.com/ulfe-lmi/slaif-local-coding/pull/11 — state OPEN, non-draft
- Base: `main` at `1a913bf3520e7570042774ef7c8ca5153da7a671` (starting remote SHA, unchanged during the round)
- Head: `oap/009-release-candidate-and-operational-closure`
- Implementation head SHA: 0216c8e3ad5db628a03b4d807eb92ec10e2639ae
- Report publication commit: SELF
- Implementation commits pushed before report (3):
  - `dd1714328d21a2186d94e7de9891fa9c83bf8f50` — workstreams B/C/D/E/F code (packaging policy, deployment assets, qualification script, provenance tooling, new docs/tests, CI, activated order + `oap/active`)
  - `a21ecc77aeff46b35486e3cf931579e5ca615710` — first generated `packaging/release_provenance_manifest.json`
  - `0216c8e3ad5db628a03b4d807eb92ec10e2639ae` — docs reconciliation (A), artifact-policy corrections, qualification/install fixes, CLI `--version` behavior, final manifest regeneration
- New PR this round: yes (#11); amended existing PR: no; merge performed: NO

## Changes and files
Workstream A (docs reconciliation): `README.md`, `oap/COMPLETENESS.md`,
`ARCHITECTURE.md`, `ARCHITECTURE-for-agents.md`, `SECURITY.md`,
`TESTING.md`, `docs/IMPLEMENTATION-ROADMAP.md`,
`docs/SLAIF-GATEWAY-INTEGRATION.md`, `docs/ADAPTER-CONFIGURATION.md` —
merged PR/SHA tables, historical-vs-live identifier demotion,
cutover-NOT-performed / NOT-released statements.

Workstream B (packaging closure): `docs/RELEASE-ARTIFACT-POLICY.md`
(policy: wheel = single supported distributable; sdist = developer-only
whitelist; manifest + schema git-only because they hash the artifacts —
no self-hash cycle); `pyproject.toml` (explicit `[tool.hatch.build]`
include/exclude for both targets, incl. manifest/schema and
`tests/test_artifact_policy.py` sdist exclusion);
`scripts/artifact_policy_check.py` (mechanical `--inspect` +
`--install-smoke`; install uses `python -m venv --without-pip` + `uv pip`
because uv-managed/minimal system interpreters do not ship ensurepip);
`tests/test_artifact_policy.py` (src/-path sdist assertions).

Workstream C (operator closure, from commit 1):
`packaging/slaif-local-coding.service` (evolved unit: loopback-only,
hardening, `ProtectProc=invisible`, external 0600 `EnvironmentFile`),
`config/adapter.deployment.template.toml` (exactly two documented
placeholders), `packaging/readyz-wait.sh`, `docs/DEPLOYMENT.md`.

Workstream D (disposable qualification):
`scripts/disposable_deployment_qualification.py` — fake loopback upstream,
build + policy check + fresh-venv wheel install, template config,
readiness, JSON/SSE/tool contracts, stop/restart, upgrade, mechanical
rollback, injected failed start with recovery, optional transient systemd
unit, cleanup with absence proof. Fixes found and repaired during this
round's first end-to-end runs (harness-only, no adapter change):
(1) venvs created `--without-pip` with `uv pip` installs (ensurepip absent);
(2) fake upstream normalizes the adapter's pre-existing empty-query
trailing `?` (adapter forwarding behavior is unchanged and was already
accepted against real vLLM); (3) upgrade/rollback backups keep the exact
`.whl` filename (`uv pip` refuses non-wheel names); (4) readiness probe
uses `http.client` so a documented 503 is observed as 503 (urllib raises
on error statuses).

Workstream E (provenance): `packaging/release_provenance_manifest.json`
(regenerated from the final build; `generated_from.git_commit` =
`a21ecc77aeff46b35486e3cf931579e5ca615710`, an ancestor of the
implementation head), schema, generator, E3 drift test;
`docs/RELEASE-CUTOVER-RUNBOOK.md` (prepare-only, authority-classed).

Workstream F (CI): `.github/workflows/ci.yml` — `test` job now runs
checkout `fetch-depth: 0`, ruff check, ruff format --check, mypy, full
pytest, `uv build`, `--inspect`, `--install-smoke`, `compileall`,
`bash -n`; `gateway-contract` job unchanged.

F4 runtime change call-out: `src/slaif_local_coding/cli.py` — `--version`
now uses the argparse `version` action so it works without `--config`
(required by B4 "version behavior"; the previous `store_true` +
`required=True --config` combination made `--version` exit 2). No other
runtime behavior changed.

## Acceptance evidence
### A1–A5 documentation reconciliation
- Result: PASSED (committed; CI ruff/format clean on the docs).
- Evidence: README/COMPLETENESS/ROADMAP now carry a merged PR/SHA table
  (PR #1 `91463ae3…92df` … PR #10 `1a913bf3…a671`, verified against
  GitHub at preflight); the original planned meanings of numeric 006–008
  are marked historical planning prose in every current-facing document;
  every current capability statement distinguishes implemented-and-merged,
  real-E2E accepted (fixture-scoped, 004), continuously
  Gateway-contract tested (007), packaged (009-B), deployment-qualified
  (disposable only, 009-D), cutover NOT performed, NOT released.
  `oap/orders/` and `oap/reports/` were not edited (A5).
### B1–B6 artifact policy and mechanical proof
- Result: PASSED.
- Policy: `docs/RELEASE-ARTIFACT-POLICY.md` (linked from README and
  DEPLOYMENT.md): wheel = single supported distributable; sdist =
  developer-only source archive, never a supported release artifact;
  explicit, not a backend default.
- Final artifact hashes (from a cleared `uv build --clear`, reproducible):
  wheel `slaif_local_coding-0.1.0-py3-none-any.whl` SHA-256
  `e4759c00e37332998ed92dc5c01fe10be4b11b3a4b1df8c33edc64e176752ee1`
  (81462 bytes, 26 entries; top-level `slaif_local_coding` +
  `slaif_local_coding-0.1.0.dist-info` with LICENSE/NOTICE — verified-clean
  property); sdist `slaif_local_coding-0.1.0.tar.gz` SHA-256
  `80233f0ae25af0f54e969297212d7e0b700b2b60afa9a7b58d8c8653d77572fb`
  (389053 bytes, 96-entry developer whitelist). A second cleared rebuild
  produced byte-identical artifacts (same SHA-256s), proving
  determinism.
- `--inspect`: `ok: true, violations: []` (forbidden entries, forbidden
  byte patterns `/synology/`, `hinton1`, `10.8.132.x`, key patterns,
  required entries, package drift).
- `--install-smoke`: `ok: true` — fresh empty venv, wheel-only install,
  import OK, console entry point `--help` exit 0 and `--version` exit 0
  printing `slaif-local-coding 0.1.0`, installed module inside the
  disposable venv and not the repository checkout (in-venv provenance
  recorded with entry point SHA-256).
- B5: sdist asserted against the same forbidden set; docs state wheel-only
  support. B6: no new dependencies added; no weights/vendor/hosted
  components.
### C1–C4 deployment assets and operator contract
- Result: PASSED.
- Single supported path justified from source review (one CPU-only console
  entry point → `Type=exec` user unit; repository venv; loopback 18031;
  no OCI/Compose). Asset set: evolved unit (loopback-only
  `IPAddressAllow`, full hardening, external 0600 `EnvironmentFile`,
  start-limit), template with exactly two placeholders, bounded
  fail-closed `readyz-wait.sh`, `docs/DEPLOYMENT.md` covering
  start/stop/restart/status, readiness ordering, cache/state permissions
  and purge/rebuild, logging/privacy, upgrade (exact backup path
  `~/.local/state/slaif-local-coding/backups/<UTCZ>/`, mode, contents),
  mechanical rollback with post-rollback verification, and
  uninstall/disable.
- C3: `tests/test_packaging.py` asserts across all packaging assets that
  no secret appears in any unit, argv, example, template, or document.
  C4: no persistent unit of this host was installed/enabled/changed.
### D1–D6 disposable operational qualification
- Result: PASSED — `scripts/disposable_deployment_qualification.py`
  completed `result: PASS` (twice; final clean run below).
- Commands: `uv run --frozen python scripts/disposable_deployment_qualification.py`
  (final clean run; an earlier `--keep` run preserved evidence for
  debugging intermediate in-scope harness failures, all fixed and
  re-run).
- Facts (final clean run, sanitized): fake loopback upstream only (never
  18020, never any Gateway/provider); candidate bound loopback 127.0.0.1:18031
  (listener line verified loopback-only, count 1); readiness in 1.031 s
  (`/readyz` 200); `/healthz` 200, `/readyz` 200, private `/metrics` 200
  with `slaif_requests_total` present and no prompt marker; `/v1/models`
  200 exposing the fake model; Responses JSON 200 with usage
  {input 11, output 7, total 18}; Responses SSE event order
  created → in_progress → output_item.added → content_part.added →
  output_text.delta → output_text.done → content_part.done →
  output_item.done → completed with first byte before terminal (tail ≥
  0.25 s) and terminal usage preserved; Responses tool SSE events with
  call id `call_fake_009`; Chat tool JSON 200 returning `fake_lookup`;
  Chat SSE data + done with usage. Fake request counts: GET /health 7,
  GET /v1/models 1, POST /v1/responses 8, POST /v1/chat/completions 2.
- Stop/restart: clean (exit -15/SIGTERM, no orphan process, port free);
  restart ready 0.516 s, smoke 200.
- Upgrade: previous artifact backed up (config + exact `.whl` filename +
  inventory, 0600) → wheel force-reinstalled (exit 0) → config SHA
  preserved, config mode 0600, cache root `/dev/shm/slaif-local-coding`
  state unchanged (disposable, no migration) → ready, smoke 200.
- Rollback: mechanical restore of exact previous artifact and config
  (install exit 0, restored config SHA-256 equals backup) → ready, smoke
  200.
- Failed-start injection: new config pointed at a closed loopback port →
  `/readyz` 503 with `upstream: "unavailable"` (readiness false) →
  recovery from backup (install exit 0, config matches backup) → ready,
  smoke 200.
- systemd (available on this host, D4 exercised): `systemd-analyze
  --user verify` on the unit exit 0 with no errors; uniquely named
  transient unit `slaif-009-qual-<pid>.service` via
  `systemd-run --user --collect` started (exit 0), reached readiness
  (healthz 200), stopped (exit 0), and was fully removed (unit absent,
  port 18031 free). The candidate process used a synthetic
  loopback-only credential value defined in the qualification script
  (never a real key).
- Final stop: no orphan, port free; candidate stdout scanned — no prompt
  marker, no synthetic key value.
- Cleanup/absence proof: workdir removed, protected unit unchanged, no
  orphan candidate process, 18031 free after.
### E1–E4 provenance manifest and cutover plan
- Result: PASSED.
- Manifest (`packaging/release_provenance_manifest.json`, schema-versioned
  `.schema.json`) contains exactly the ordered fact class: git SHA,
  Gateway peer `65666f5886832034c52211fdd7604046557e6ada` with module
  contract versions (`local-coding-v1` v2
  `process_local_inclusive_horizon_fail_closed`,
  `codex-0.149-responses-v1` v4), Python runtime (3.12) and package
  version (0.1.0), lockfile/build-input hashes, artifact SHA-256/size,
  config/template hashes, reference compatibility facts (model name
  `qwen3.8-27b`, vLLM OpenAI-compatible `/v1`, Codex 0.149.0 wire
  fixtures), and explicit limitations (deployment-qualified disposable
  only; cutover not performed; not released).
- E2: generator and E3 test exclude host paths, credentials, private
  identifiers, prompts, model output, and raw payloads by construction
  and by scan; `oap/evidence/` stays separate.
- E3: `tests/test_release_provenance_manifest.py` regenerates from the
  actual build inputs and fails on any drift or forbidden content
  (only `generated_from.git_commit` may advance; committed value must be
  an ancestor of HEAD) — PASSED in the full suite and CI.
- E4: `docs/RELEASE-CUTOVER-RUNBOOK.md` — exact final cutover/rollback
  sequence with per-step authority classes (CODING-SAFE vs
  HUMAN-AUTHORIZED), preconditions (009 accepted and merged), and
  rollback triggers. No step executed.
### F1–F4 CI gates
- Result: PASSED.
- F1: `gateway-contract` job unchanged; still pinned to
  `ulfe-lmi/slaif-api-gateway @ 65666f5886832034c52211fdd7604046557e6ada`
  (re-verified live at preflight: the gateway repository's default-branch
  `main` HEAD was still exactly this commit, so no re-pin was needed);
  fixture `tests/fixtures/gateway/current_peer_authority.json`
  unchanged.
- F2: `test` job runs all existing gates plus `uv build`, artifact
  policy `--inspect`, and `--install-smoke` (all verified in the CI run
  below).
- F3: see GitHub CI section — all required checks green at the
  implementation head before the report.
- F4: no protocol refactor; one runtime change called out above
  (CLI `--version`, required by B4).

## Verification
Local (final, post all fixes, 2026-09-14, repo venv `uv sync --frozen
--extra dev`):
- `uv run --frozen ruff check .`: PASSED (All checks passed)
- `uv run --frozen ruff format --check .`: PASSED (326 files already formatted)
- `uv run --frozen mypy src tests`: PASSED (no issues in 66 source files)
- `uv run --frozen pytest -q`: PASSED — 982 passed, 26 skipped (skips are
  the normal opt-in live/gateway/historical-evidence gates)
- `uv build --clear`: PASSED (byte-identical artifacts across rebuilds)
- `uv run --frozen python scripts/artifact_policy_check.py --dist dist --inspect`: PASSED (`ok: true`, `violations: []`)
- `uv run --frozen python scripts/artifact_policy_check.py --dist dist --install-smoke`: PASSED (`ok: true`)
- `python3 -m compileall -q src tests oap/bin scripts`: PASSED
- `bash -n oap/bin/*.sh packaging/*.sh`: PASSED
- `uv run --frozen python scripts/disposable_deployment_qualification.py`: PASSED (`result: PASS`, final clean run with absence proof; earlier `--keep` run also `PASS`)
- Protected-host read-only probes (before/after): PASSED (see Live section)
No live-vLLM test matrix was re-run (explicit non-goal: no broad
protected-acceptance rerun; Objectives 005–008 remain accepted as-is).
Real Codex E2E: NOT RUN (not ordered for this objective).

## Live model/service evidence
- Protected service (read-only): `qwen-serving-vision.service` — at round
  start and after the round: `Active: active (running) since Sun
  2026-09-06 18:57:26 CEST`, Main PID 23961 (vllm), listener
  0.0.0.0:18020, GET `/health` = 200 (bounded read-only, both before and
  after qualification); port 18021 absent (before and after); port 18031
  absent before and after the round; `~/.codex/qwen-neumann.config.toml`
  mode 0600, mtime 2026-09-13 11:59 CEST, unchanged. No unit/PID/listener
  discrepancy: protected before/after facts recorded by the qualification
  are identical.
- Disposable candidate: bound only 127.0.0.1:18031 (verified via socket
  inspection); all its traffic went to the in-process fake loopback
  upstream (synthetic fixtures only); zero protected/Gateway/provider
  traffic; fully removed afterwards (no listener, no orphan process).
- Fixture unchanged: YES.

## GitHub CI / required checks
- Implementation head `0216c8e3ad5db628a03b4d807eb92ec10e2639ae`, run
  34793824162:
  - `test`: SUCCESS (all 14 named steps completed successfully, incl.
    ruff check, ruff format --check, mypy, pytest, uv build,
    artifact-policy inspect, fresh-venv install smoke, compileall,
    bash -n)
  - `gateway-contract`: SUCCESS
- All required green at drafting: yes. Report-head checks may be pending
  after the report push; strategy verifies.

## Local setup/dependencies
- Repo-owned `.venv` (Python 3.12, `uv` 0.12.5, `uv sync --frozen --extra
  dev`); no new dependencies added; no new services; no sudo used; the
  only user-systemd activity was the uniquely named transient
  `systemd-run --user --collect` unit, fully removed with proof.
  Disposable workdirs under `/tmp/slaif-009-qual-*` and the smoke venvs
  under `/tmp/slaif-artifact-smoke-*` were removed; network was used only
  for GitHub and the routine package index during wheel installs.

## Documentation
- Updated: `README.md`, `oap/COMPLETENESS.md`, `ARCHITECTURE.md`,
  `ARCHITECTURE-for-agents.md`, `SECURITY.md`, `TESTING.md`,
  `docs/IMPLEMENTATION-ROADMAP.md`, `docs/SLAIF-GATEWAY-INTEGRATION.md`,
  `docs/ADAPTER-CONFIGURATION.md`, `docs/RELEASE-ARTIFACT-POLICY.md`.
- New (committed in the first implementation commit): `docs/DEPLOYMENT.md`,
  `docs/RELEASE-CUTOVER-RUNBOOK.md`.
- Same-PR documentation for every behavior/config/security/test/ops
  change: yes.

## Safety/scope confirmations
- Unrelated/pre-existing files preserved: yes — the strategic local edit
  in `oap/runtime.env.example` and the untracked placeholder files
  `Local`, `clean`, `unchanged` were left in the working tree, not
  committed, not deleted; the build policy excludes the placeholders from
  all artifacts (verified by `--inspect`).
- Secrets/raw content: none committed, logged, or published — synthetic
  fixtures only; the qualification's credential is a synthetic
  loopback-only value defined in the committed script; reports/evidence
  contain statuses, counts, hashes, and timings only.
- Protected resources: protected 18020/Qwen/Codex fixture changed: NO
  (read-only probes only; before/after identical). No firewall/VPN/network
  mutation. No Gateway change.
- Required tests skipped/not run: the 26 pytest skips are the normal
  opt-in/live/historical gates; real-Codex E2E NOT RUN (not ordered); no
  protected-acceptance rerun (explicit non-goal). No scope deviation.
- Extra objective PR: NO (exactly PR #11). Coding merge: NO.
- Active/order edited: NO (order and `oap/active` committed as exact
  strategic-authored bytes in the first implementation commit).
- Report commit report-only: yes (this commit changes only
  `oap/reports/009-a-release-candidate-and-operational-closure.md`).

## Known limitations/blockers
- No blockers.
- Deployment qualification is disposable-environment evidence only; it
  does not prove protected-service behavior, production readiness, or
  multi-user/production certification.
- The live cutover/rollback runbook is prepare-only; its
  HUMAN-AUTHORIZED steps remain to be performed under a separate
  human-authorized order after this objective is accepted and merged.
- The final live-cutover smoke (real Codex text/tool/vision against the
  protected upstream) remains NOT RUN by design.

## Recommended strategic follow-up
Factual only: the only remaining work toward production is the real
protected cutover/release act itself (`docs/RELEASE-CUTOVER-RUNBOOK.md`),
which requires a separate human-authorized order. Review of PR #11
(incl. the F4 CLI `--version` call-out) is at strategy's discretion.

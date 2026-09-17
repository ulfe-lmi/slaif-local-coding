# OAP Coding-Agent Report — 011-a

## Work order
- Identifier: `011-a`; order path: `oap/orders/011-a-docker-mvp-release-readiness.md`; numeric objective: `011`
- PR mode: `CREATED_NEW_PR` (round `a`; exactly one PR for objective 011)

## Status
COMPLETE

## Executive summary
Objective 011 is implemented and fully qualified in this PR: the D1
LAN-visible binding law, the Docker product surface (Dockerfile /
.dockerignore / compose.yaml / hardened runtime / healthcheck / wheel-based
install), the mandatory Docker CI job (14-phase qualification), the
host-networking security delta review, the release-provenance schema v2 with
regenerated manifest, full documentation reconciliation plus the operator
Docker install and documented (not executed) publication path, and the
runbook/topology/state-machine updates. All three required CI checks
(`test`, `gateway-contract`, `docker`) are `success` at the implementation
head. The Docker qualification was additionally exercised as a D6-confined
disposable run on the protected host (docker0 link-local bind only, fake
upstream only, fully torn down). Five in-scope CI-repair commits fixed
quoting, runner portability, manifest drift, a pre-existing fake-provider
bookkeeping race, and engine-version-dependent inspect representations. No
release, tag, registry publication, Gateway mutation, protected mutation, or
cutover was performed.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #13 — https://github.com/ulfe-lmi/slaif-local-coding/pull/13 — state `OPEN`, non-draft
- Base: `main` @ `4aa805fdd197938f1f25c9ca034c2e3c3cf2fc87`
- Branch: `oap/011-docker-mvp-release-readiness`
- Starting remote SHA (base at order time): `4aa805fdd197938f1f25c9ca034c2e3c3cf2fc87`
- Implementation head SHA: 204848b44b8db90d41fd91b520ca4452345ebf75
- Report publication commit: SELF
- Implementation commits pushed before report (9, all on the single PR branch):
  - `5500e805a93008993103e457229b1e2605d73080` — Docker MVP packaging, LAN-visible binding law, release-readiness closure (workstreams A–G)
  - `92b5c596871715e59a6cf812cda4c4381bd7835a` — initial manifest regeneration (superseded)
  - `442d957a87375f00e439a7e4fa57628add105d6d` — C repair: wheel-binding shell quoting in the docker CI job
  - `37bfdc255954f1743984df364d75e4074376838f` — C repair: container-file ownership portable to GitHub runners (no CAP_CHOWN; 0644 fallback for disposable fake-value CI site files)
  - `ba01d941e02f0e29c6ec7ecfb9750bcea6d0f44e` — E2: final manifest regeneration from the final implementation state
  - `52dcb5d472f844f100aa0d44fe9310b314b9320a` — C repair: in-image provenance as a real multiline `python -c` script
  - `a52fa90b37baae7fb5aa014e7bfa72b521112d3e` — C repair: disabled-mode config-rejection rendering + fake-provider dispatch bookkeeping race (pre-byte bookkeeping)
  - `2892c31e1cd8cd6518d6b6f87e6d79a1185f26ce` — C repair: engine-version-neutral hardening/label check representations + observed-state diagnostics
  - `204848b44b8db90d41fd91b520ca4452345ebf75` — C repair: CI fake upstream torn down before the absence-proof port scan
- New PR this round: yes (exactly one). Amended existing: n/a. Extra objective PR: NO. Merge performed: NO. Auto-merge: not enabled.
- Strategic transcript bytes: `oap/orders/011-a-docker-mvp-release-readiness.md` and `oap/active` committed byte-identical to the activated working-tree bytes (verified by `git diff HEAD` = empty); not edited in any commit.

## Changes and files
36 files changed (+5121/−251 vs base). By workstream:

- **A — LAN-visible binding law**: `src/slaif_local_coding/config.py` (D1 `listen_host` syntax law in `ServerConfig` + `Settings.binding_law` cross-mode rule; hostnames/schemes/ports/malformed rejected; loopback default unchanged), `tests/test_config.py` (A2 full configuration matrix incl. all rejects + 010 distinct-secret-role and signed/no-static invariants), `config/adapter.gateway-integrated.template.toml` (A3: exactly one added placeholder `__LISTEN_HOST__`, existing two placeholders and truthful label kept), `tests/test_gateway_integrated_deployment.py` (A4: exactly three documented placeholders; loopback and non-loopback substituted variants parse; non-loopback rejected by validators under disabled/static — fail closed), `docs/ADAPTER-CONFIGURATION.md` (A5: exact binding law + `metrics_host` policy).
- **B — Docker product surface**: `Dockerfile` (multi-stage; pinned-by-digest runtime; wheel built from repo source with committed `uv.lock`; non-editable install; no repo source/`oap`/`tests`/`references`/caches in runtime), `.dockerignore` (explicit exclusions), `compose.yaml` (D2 `network_mode: host`; B3 hardening: non-root 10001, RO rootfs, no-new-privileges, cap_drop ALL, no privileged, no socket, no source bind, bounded tmpfs `/tmp` 64m + `/dev/shm` 256m, `unless-stopped`; in-image `/readyz` healthcheck; single RO config bind + mode-0600 env file reference only; B6 OCI labels), `scripts/docker_qualification_ci.py` (C job driver), `scripts/fake_upstream_server.py`, `scripts/sim_gateway_client.py` (stdlib-only, D7).
- **C — Docker CI job**: `.github/workflows/ci.yml` (mandatory `docker` job; wheel rebuilt and bound to the committed manifest before qualification; `test`/`gateway-contract` contracts unchanged).
- **D — Security delta review (release gate)**: `docs/DOCKER-SECURITY-DELTA.md` (D1'–D6' complete, strategic decisions D1–D8 recorded as authority).
- **E — Release provenance extension**: `packaging/release_provenance_manifest.schema.json` (schema v2 `slaif-release-provenance-v2` with `oci` section), `scripts/release_provenance_manifest.py` (v2 generator), `packaging/release_provenance_manifest.json` (regenerated: `objective: "011-a"`, wheel `7cede0b8…` (changed bytes per D5), sdist `4ba17680…`, base-image digests, Dockerfile/compose/.dockerignore hashes, `image_digest: null`, `published: false`, `cutover_performed: false`, `released: false`), `tests/test_release_provenance_manifest.py` (v2 validation + hash cross-checks + status fields).
- **F — Documentation reconciliation + operator docs**: `README.md` (F1: status table 009→PR #11 `4fd4502…`, 010→PR #12 `4aa805f…`, 011 = this PR truthful pre-merge; binding-law prose; Docker named canonical MVP install path), `oap/COMPLETENESS.md` (F2, historical sections verbatim), `docs/IMPLEMENTATION-ROADMAP.md` (F3), `docs/DEPLOYMENT.md` (F4: two supported paths, asset table, qualification boundary, unit header comment corrected to all three secret roles), `docs/DOCKER-INSTALL.md` (F5, new), `docs/DOCKER-SECURITY-DELTA.md` (F6, new), `docs/TOPOLOGY.md` + `docs/topology.manifest.json` (F7: signed LAN-visible variant, per-hop table, §5 invariant re-adjudicated per D4, schema bumped and mechanically checked), `docs/RELEASE-ARTIFACT-POLICY.md` (F8), `docs/RELEASE-CUTOVER-RUNBOOK.md` (F9: `local.binding_class`, cutover authority → 011-a manifest, bridge-container Gateway note).
- **G — Runbook/topology/state-machine mechanics**: `scripts/cutover_state_machine.py` (G1: `local.binding_class` tracked through all mutating transitions + rollback table; self-test extended), `scripts/topology_qualification.py` (G2: signed-contract dimension + trusted-LAN endpoint class; unsigned combinations fail closed; cross-namespace loopback still rejected; unknown inputs fail closed; 010 negative behavior retained), `tests/test_cutover_state_machine.py`, `tests/test_topology_qualification.py` (G3, deterministic/synthetic only), `scripts/gateway_accounting_rehearsal.py` (C repair only: pre-existing fake-provider dispatch bookkeeping race — see Verification), `packaging/slaif-local-coding.service` (comment-only: all three secret roles listed in unit header), `.github/workflows/release-image.yml` (E5: inert, `workflow_dispatch`-only, `packages: write` declared, no secrets configured, cannot run on PRs/pushes; nothing pushed by this objective).

## Acceptance evidence

### Criterion 1 — A2 configuration matrix + 010 invariants
- PASSED. Pure-unit matrix (loopback × {disabled, static, signed} valid; non-loopback literal × {disabled, static} rejected; non-loopback literal × signed valid; `0.0.0.0`/`::` × signed valid; hostname rejected in every mode; three distinct secret-role names enforced) in `tests/test_config.py` + template tests in `tests/test_gateway_integrated_deployment.py` — all green in the full local pytest (1087 passed / 26 skipped) and in CI `test` job (run 35176646965, success).

### Criterion 2 — Rebuilt wheel + manifest v2
- PASSED. Rebuilt wheel `slaif_local_coding-0.1.0-py3-none-any.whl` SHA-256 `7cede0b8e930463400a40662248a97aae22f75b0512dcd8151d6122a99157166` (83070 B, 26 entries) — reproducible across local builds and the CI wheel-build step. sdist `slaif_local_coding-0.1.0.tar.gz` SHA-256 `4ba17680c55c557494593087f4d632abb6a79f0c595ecab08bb2414abc86f5d6` (424608 B, 105 entries). Manifest v2 `slaif-release-provenance-v2` regenerated with `objective: "011-a"`; template/asset/lockfile hashes cross-checked against committed files by `tests/test_release_provenance_manifest.py` (10 passed); status fields `cutover_performed=false`, `released=false`, `oci.published=false`, `oci.image_digest=null`. The 010-a wheel hash `8678e16b…` is referenced only as the historical record.

### Criterion 3 — Image builds + B8 in-image provenance
- PASSED (CI + local D6). CI `image_build` PASSED (`slaif-local-coding:0.1.0-af13643affd28f8b336f5cd2260429fe5b99b3d5`); `in_image_provenance` PASSED: version 0.1.0, module at `/opt/slaif/venv/lib/python3.12/site-packages/slaif_local_coding/__init__.py` (non-editable), in-image wheel hash == manifest. Local D6: image `slaif-local-coding:0.1.0-e36896e`, final image digest `sha256:fb4af5b5af2a8cbc09ae243dec0cba89907d2bd8dd306e49bbbcf5e96b34cb1e`; same B8 proof passed in-image.

### Criterion 4 — Compose validation + start + readiness
- PASSED. CI `compose_rendered_validation` PASSED (rendered compose valid; zero secret values in rendered output); `adapter_stack_up` PASSED (container `slaif-local-coding-adapter-1` healthy within bound, `network_mode: host`, bind `0.0.0.0:18031`). Local D6: validated/started healthy on the confined bind.

### Criterion 5 — C5 signed requests via non-loopback endpoint
- PASSED. CI `bridge_positive_signed` from a simulated bridge-namespace Gateway runtime against `http://172.17.0.1:18031` (endpoint address class: `host_bridge_ip`): models 200, non-stream chat 200, SSE stream 200 with 4 frames and terminal `response.completed`, function-tool round-trip 200 — every response sentinel-correlated to the fake upstream. Local D6: same positive set via `172.17.0.1:18032`, sentinel-correlated.

### Criterion 6 — C6 negatives
- PASSED. CI `bridge_negative_contract`: missing token → 401; invalid signature → 403; replay → 409 (first 200); cross-namespace `127.0.0.1` → unreachable (`gaierror`). `config_time_rejection`: disabled + non-loopback rejected at config time with the binding-law error naming `service_bearer_signed_identity_v1`; static + non-loopback rejected; signed + non-loopback accepted (`listen_host` retained). Local D6: same negative set.

### Criterion 7 — C7 fail-closed
- PASSED. CI `fail_closed_readiness`: second adapter instance without the signing-secret role starts, `/readyz` = 503 with `gateway_ingress: "unavailable"`, compose healthcheck reports `unhealthy` — mechanically asserted. Local D6: same.

### Criterion 8 — C8 content/hardening/labels
- PASSED. CI `image_content_scan`: 6487 files scanned, 0 forbidden entries, 0 secret-pattern matches, in-image wheel hash matches manifest. `hardening_and_labels`: non-root user (10001), read-only rootfs, no-new-privileges, cap_drop ALL, not privileged, host network, no Docker socket, single read-only config bind, no repo-source bind, bounded tmpfs (`/tmp` 64m, `/dev/shm` 256m), `unless-stopped`, all 8 OCI/provenance labels correct. Local D6: same assertions (6486 files in that build).

### Criterion 9 — C9 operations + teardown absence proof
- PASSED. CI `operations_stop_start_recreate_upgrade_rollback`: stop → start → recreate → upgrade (second tag, `--force-recreate`) → rollback, every step healthy with the mounted configuration hash unchanged (`f1a40f59ce99a1421e013d8001d339d9716339c86fdaf5b4782509f6d7826840`); `teardown_absence_proof`: no leftover containers, no leftover images, no listeners on 18031/18033/18034. Local D6: full teardown with absence proof (ports 18021/18031–18034 free, no slaif containers/images).

### Criterion 10 — CI green at report head + local gates
- PASSED. At implementation head `204848b…`: `test` success, `gateway-contract` success (peer pin still `65666f58…`), `docker` success (run 35176646965). Local: full pytest 1087 passed / 26 skipped (repeated on each repair commit), ruff check + format clean, `mypy src tests` clean (70 files), artifact-policy inspect + fresh-venv install smoke green (re-proven after wheel bytes changed per D5).

### Criterion 11 — Protected host before/after identical
- PASSED (verified). Before (order-time, strategic, 2026-09-17): `qwen-serving-vision.service` active (running) since Sun 2026-09-06 18:57:26 CEST, MainPID 23961, `0.0.0.0:18020` `/health` = 200, 18021/18031–18034 absent, profile `~/.codex/qwen-neumann.config.toml` mtime 2026-09-13 11:59 mode 0600, `Linger=no`, only three stale exited (years-old) containers, no slaif unit. After (re-probed by coding this round, read-only): identical on every item — service active since 2026-09-06 18:57:26 CEST with MainPID 23961 (no restart), `/health` 200, no listeners on 18021/18031–18034, profile mtime/mode unchanged, `Linger=no`, no new containers, no slaif unit. No LAN-exposed listener existed at any point during qualification (D6 bind was docker0 link-local `172.17.0.1:18032` only; CI runs on the disposable runner). Observation (not our unit, untouched): `zap-it-lan.service` (different project) was previously observed in a `Restart=on-failure` flap; it was `active (running)` at re-probe time.

### Criterion 12 — Documentation consistency
- PASSED (by diff review in the PR). No "this PR (open)" language remains in current-facing docs; 009/010 rows carry exact merge commits (`4fd4502…` PR #11, `4aa805f…` PR #12); Docker canonical / systemd secondary stated; `docs/DOCKER-INSTALL.md` matches repository behavior command-for-command; `docs/DOCKER-SECURITY-DELTA.md` complete per D1'–D6'; TOPOLOGY + manifest + runbook + state machine consistent with D1/D2; historical OAP artifacts byte-unchanged (only the new 011-a order/report/active touch `oap/`).

### Criterion 13 — Dependency + scope invariance
- PASSED. `uv.lock` SHA-256 `1237cbd179f71b99984c80f927529549f5e61eb705585ef9cf2ab0fa9e26764a` and `pyproject.toml` SHA-256 `af91f82283882f1e51ee763d635f94f1ae2534c51585c837aa61cff8a2f7dda2` — byte-identical to base (D7, zero new dependencies; all Docker/qualification tooling stdlib-only). Diff bounded to the 36 in-scope files listed above; no dependency, service, model, network, profile, or release-state change.

### Criterion 14 — No publication/mutation (GitHub-verified at report time)
- PASSED (verified against GitHub at report time). No tags (`git ls-remote --tags` empty), no GitHub releases, no image pushed anywhere, `slaif-api-gateway` repository unmodified by this PR (cross-repo pin check only), version stays `0.1.0`.

## Verification
Local commands (all on the protected host, repo venv via `uv`):
- `uv run --frozen pytest -q`: PASSED — 1087 passed, 26 skipped (repeated on each repair commit; also repeated 3× full-suite + rehearsal file 5× + targeted stress of the 4 race-prone tests 20× after the fake-provider fix)
- `uv run --frozen ruff check .`: PASSED — all checks passed
- `uv run --frozen ruff format --check .`: PASSED — 343 files already formatted
- `uv run --frozen mypy src tests`: PASSED — no issues in 70 source files (CI-equivalent invocation)
- `uv build --out-dir dist`: PASSED — wheel + sdist byte-identical to committed manifest hashes (reproducible)
- `uv run --frozen pytest tests/test_release_provenance_manifest.py -q`: PASSED — 10 passed
- `uv run --frozen python scripts/artifact_policy_check.py --dist dist --inspect`: PASSED — ok, 0 violations
- `uv run --frozen python scripts/artifact_policy_check.py --dist dist --install-smoke`: PASSED — ok, 0 violations
- `python -m compileall -q src tests oap/bin scripts`: PASSED
- Docker qualification phase harness (real `_do_config_time_rejection` method against the real config validators): PASSED — `{"disabled": true, "service_bearer_static_identity": true, "signed_non_loopback": true}`
- Hardening check expressions against a live compose container on Docker 29.1.3/Compose v5.0.1: PASSED (observed `SecurityOpt=["no-new-privileges:true"]`, `Tmpfs={"/tmp":"size=64m","/dev/shm":"size=256m"}`)
- no-new-privileges kernel-effect probe (disposable, `--network none` containers): setuid-root escalation succeeds in the control container and is rejected (EPERM, uid stays 10001) with `no-new-privileges:true` — the SecurityOpt form is kernel-effective
- C-repair root-cause fixes: (a) disabled-mode template rendering now produces a well-formed disabled config so the Settings-level binding-law error (naming `service_bearer_signed_identity_v1`) surfaces instead of the earlier ingress-level token-env error; (b) fake provider now performs returned-call registration + call record before the first response byte (Content-Length framing lets clients complete before post-send bookkeeping — the source of the intermittent `inference_calls`/`take_returned_call` flakes; no test assertions changed or weakened); (c) hardening/label checks accept both engine representations (`NoNewPrivileges` boolean or `no-new-privileges:true` SecurityOpt; `HostConfig.Tmpfs` map or `Mounts` entries) with observed-state diagnostics on failure; (d) the CI fake upstream is torn down inside the absence-proof phase so the port scan covers every listener the job created.

## Live model/service evidence
- No live Qwen/vLLM inference was performed (order non-goal). The protected upstream was probed status-only: `GET 127.0.0.1:18020/health` → 200 (before and after; no other endpoint touched).
- All adapter/gateway/vision evidence is from bounded disposable fake upstreams: CI (GitHub runner, `127.0.0.1:18033` fake upstream, `172.17.0.1:18031` simulated-bridge endpoint) and the local D6 run (protected host, fake upstream `127.0.0.1:18033` only, adapter confined to `172.17.0.1:18032` — docker0 link-local, no LAN exposure).
- Protected fixture unchanged (Criterion 11 evidence above).

## GitHub CI / required checks
- Implementation-head run 35176646965 (head `204848b44b8db90d41fd91b520ca4452345ebf75`):
  - `test` (job 105059715359): SUCCESS — `1086 passed, 27 skipped in 64.70s` (the one extra skip vs local is the standing environment-conditional skip on hosted runners; identical to prior runs)
  - `gateway-contract` (job 105059715433): SUCCESS (pinned peer `65666f5886832034c52211fdd7604046557e6ada`, fixture unchanged vs base)
  - `docker` (job 105059715201): SUCCESS — all 14 phases PASSED (verify_wheel_binding, compose_rendered_validation, image_build, fake_upstream_start, adapter_stack_up, in_image_provenance, bridge_positive_signed, bridge_negative_contract, config_time_rejection, fail_closed_readiness, image_content_scan, hardening_and_labels, operations_stop_start_recreate_upgrade_rollback, teardown_absence_proof); runner Docker 28.0.4 / Compose 2.38.2
- Prior runs on the branch (all repaired in-scope): 35170462845@92b5c59 FAILURE, 35170588792@442d957 FAILURE, 35171656209@ba01d94 FAILURE, 35172194279@52dcb5d FAILURE, 35174677241@a52fa90 FAILURE, 35176161551@2892c31 FAILURE — each failure root-caused and fixed by a follow-up C-repair commit (details in "Changes and files" + Verification).
- All required green at drafting: YES. Report-head checks may re-run; strategy verifies.

## Local setup/dependencies
- Repo venv via `uv` (locked/frozen installs; no new dependencies).
- Docker Engine 29.1.3 + Compose v5.0.1 (protected host, via passwordless sudo) used for the D6 disposable run and read-only daemon-behavior probes only (disposable `--network none` / bridge-no-ports containers, all removed; probe-pulled public base images removed; no persistent units/services).
- No repo-local services left running; CI workdir state is ephemeral.

## Documentation
- Updated (required and done): per F1–F9 and G1–G4 — `README.md`, `oap/COMPLETENESS.md`, `docs/IMPLEMENTATION-ROADMAP.md`, `docs/DEPLOYMENT.md`, `docs/ADAPTER-CONFIGURATION.md`, `docs/DOCKER-INSTALL.md` (new), `docs/DOCKER-SECURITY-DELTA.md` (new), `docs/TOPOLOGY.md` + `docs/topology.manifest.json`, `docs/RELEASE-ARTIFACT-POLICY.md`, `docs/RELEASE-CUTOVER-RUNBOOK.md`, unit header comment (comment-only). Release-honesty ladder current: Docker qualification placed at "deployment-qualified (disposable/CI environments only)" — NOT "release-qualified", NOT "released"; cutover NOT performed.

## Safety/scope confirmations
- Unrelated files: preserved. Pre-existing working-tree modifications (`oap/runtime.env.example`) and untracked junk files (`Local`, `clean`, `unchanged`) were never staged or committed; `dist/` remains gitignored.
- Secrets/raw content: secret scan of the PR diff (excluding the strategic-authored order file) found zero credential values, zero private host paths, zero sentinels; the only pattern-name hits are placeholder/env-name references in docs and CI scripts (no values). No raw prompts/source/images/tool outputs in any artifact.
- Protected 18020/Qwen/Codex fixture changed: NO. No new persistent units; `Linger` untouched.
- Required tests skipped/not run: none required were skipped; standing environment-conditional skips only (26 locally, 27 on hosted runners), unchanged vs base behavior.
- Scope deviation: none beyond in-scope C repairs to `scripts/docker_qualification_ci.py` and one pre-existing fake-provider race in `scripts/gateway_accounting_rehearsal.py` (repository-only support code, outside the wheel/sdist; no product behavior or test assertion changed).
- Extra objective PR: NO. Coding merge: NO. Active/order edited: NO. Report commit report-only: will be verified below at publication.

## Known limitations/blockers
- Docker qualification is disposable/CI-environment-only (hosted runner + D6 confined run); it is NOT release-qualification and nothing is released.
- Accepted MVP limitation (strategic D4): no TLS on the LAN-visible adapter hop; the trusted-private-LAN boundary + signed ingress contract are the compensating controls.
- Evidence boundary (C11): the protected-host fixture invariance and the docker0-link-local confined bind class cannot be exercised in hosted CI; compensated by the D6 disposable run (facts above). GitHub runners lack CAP_CHOWN, so disposable fake-value CI site files fall back to 0644 (documented in the script; values are random fakes never recorded).
- Engine representation variance: Docker 28.0.4/Compose 2.38.2 (runner) vs 29.1.3/v5.0.1 (protected host) represent no-new-privileges and tmpfs differently in `docker inspect`; checks now accept both forms (kernel effect of the SecurityOpt form verified by a setuid-escalation negative).
- Observation (no action taken; different project): `zap-it-lan.service` flap previously noted.

## Recommended strategic follow-up
Factual only — strategy decides:
- Pinned Gateway peer remains `65666f5886832034c52211fdd7604046557e6ada` while Gateway main moved to `1fccaa746df6cd44f1ddf8c2ec5cf6ea9f18b1cb` (gateway PR #302, merged 2026-09-17). Per the fixture pin law, any re-pin requires a separate reviewed PR; it was not performed in this objective.
- The container publication path (`docs/DOCKER-INSTALL.md` / `docs/DEPLOYMENT.md` + inert `release-image.yml`) awaits a later human-authorized release order to execute (image push, digest capture, manifest `image_digest` fill, `published` flip).
- Objective 011 acceptance and merge are strategic/human decisions; coding has not and will not merge.

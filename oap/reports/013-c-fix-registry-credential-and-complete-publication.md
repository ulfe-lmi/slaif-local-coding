# OAP Coding-Agent Report — 013-c

## Work order
- Identifier: `013-c`; order path `oap/orders/013-c-fix-registry-credential-and-complete-publication.md` (strategic-authored bytes committed verbatim in W1 with `oap/active` → `013-c`); numeric objective `013`
- PR mode: `AMENDED_EXISTING_PR` — PR #15 (the single objective-013 PR), branch `oap/013-mvp-release-publication`; NO new PR

## Status
BLOCKED (at C6 — genuine human-authority boundary per strategic re-adjudication 3; the round's authorized C1–C5 work is complete, pushed, and CI-green at W; the C6 publication dispatch at W was EXECUTED and FAILED at the registry push step with a permission/credential error; per the order, no re-dispatch; no `P`, no `D`, no executed `docker-published`)

## Executive summary
W1 (C1 push-reference fix + C2 secret-based workflow + transcript) and W2 (C4 documentation reconciliation + generator/E3 objective bump + manifest `M_W2`) were implemented exactly per order, pushed to PR #15, and CI at both is fully green (4/4 each). The repository secret `SLAIF_GHCR_TOKEN` (C3) was provisioned after W2's CI was fully green and before the C6 dispatch, via the wrapper's own `gh auth token` piped into `gh secret set` (value never on a visible command line). The pre-dispatch anonymous registry probe found both tags `absent`. The `workflow_dispatch` release run at W (run `35215843816`) passed every pre-push step — including the new fail-fast secret check and `docker login ghcr.io` with the secret — and FAILED at the push step with `denied: permission_denied: The token provided does not match expected scopes.` This is a permission/credential error at the push step distinct from a fixable in-repo defect (the C1 reference fix is proven active: the push targeted the qualified `ghcr.io/ulfe-lmi/slaif-local-coding:sha-<W>` reference). Per the order's C6 stop law and re-adjudication 3 (org SSO / org policy / token scope boundary), this round STOPs: no re-dispatch, no ceiling change, no workaround. Post-failure anonymous probes show the registry is clean (both tags `absent`; no package object; no orphan state). The protected host was never touched (before/after probes identical). The Git tag `v0.1.0` and the GitHub Release do not exist (strategy post-merge acts, as always).

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`; PR #15 https://github.com/ulfe-lmi/slaif-local-coding/pull/15 — `OPEN`, `MERGEABLE` (`CLEAN`), `autoMergeRequest: null`, `mergedAt: null` (merge performed NO)
- Base: `main` @ `a04693e6792df6a8ad4262acfb46336a0f662202` (unchanged, verified at preflight and at report time)
- Starting remote SHA (at order time): `b9b90393a4781f80824081f4fd2625c0123b490f` (013-b report commit)
- W1 = `3deb1fbaa87e45b939e839a4762fd2ca99eb50ae` (C1 + C2 + activated order + `oap/active` → `013-c`)
- W2 = `W` = `9c04669a4fcbb65267fc6cd19f0b8176ec33a5e2` (C4 + generator/E3 objective bump + `M_W2`) — the final implementation head and the IMAGE-SOURCE HEAD
- `P`: does NOT exist (C7 NOT RUN — no `D`)
- R: SELF (this report; first parent = `W`)
- Implementation head SHA: 9c04669a4fcbb65267fc6cd19f0b8176ec33a5e2
- Report publication commit: SELF
- Implementation commits pushed before report: W1, W2 (both pushed; remote branch head = W2 at report time)
- New PR this round: NO; amended existing PR #15: YES; merge performed: NO
- `D`: NOT captured (publication run failed at push before any manifest was written)

## Changes and files
**W1** (`3deb1fb…`, 4 files, none an sdist/build-context input):
- `scripts/release_registry_publish.py` (C1): both docker tag/push references now built by the pure function `build_push_references()` as fully qualified `ghcr.io/<repo>:sha-<S>` and `ghcr.io/<repo>:0.1.0` (the 013-b latent Docker-Hub-resolution bug); new `--self-check-refs` deterministic local proof (asserts the exact qualified reference strings for a fixture git-sha; no docker, no push); module docstring credential line reconciled to the 013-c secret mechanism (the same file C1 owns; disclosed here — C4's doc-file scope is untouched by this). All other behavior byte-for-byte as designed: no-silent-repoint guard, digest capture from push log, registry-API cross-verification, `SLAIF_PUBLISHED_DIGEST`/`GITHUB_OUTPUT`/JSON-line output contract.
- `.github/workflows/release-image.yml` (C2, exactly the five authorized edits): header comment now describes the 013-c secret-based mechanism (dispatch-only loading; never printed; credential identity class; ceiling rejection); `permissions:` → `contents: read` ONLY (`packages: write` dropped); NEW fail-fast step immediately after checkout (`test -n "$SLAIF_GHCR_TOKEN"` with the secret env); login step `printf '%s' "$SLAIF_GHCR_TOKEN" | docker login ghcr.io -u "${{ github.repository_owner }}" --password-stdin` (org-name username unchanged); push step keeps `SLAIF_GHCR_TOKEN` env (now sourced from the secret) with the unchanged publish-script invocation. No trigger/job/runner change; still `workflow_dispatch`-only.
- `oap/orders/013-c-fix-registry-credential-and-complete-publication.md` (activated order, strategic-authored bytes verbatim; SHA-256 `a88f2c1378cadc9a3feb345ff426b4474e5f091fa0a1c268c6ed763afa0c16e4`)
- `oap/active` → `013-c` (one-line change)

**W2** (`9c04669…` = `W`, 5 files):
- `docs/RELEASE-ARTIFACT-POLICY.md` (C4, the two GITHUB_TOKEN-only statements, ~L35 and ~L213): replaced with the secret-based mechanism (dispatch-only loading; never printed; credential identity class at the canonical Publication section, plus the explicit rejection of the repo-ceiling alternative and the post-release hardening advisory — dedicated fine-grained `packages: write` + `contents: read` PAT + rotation procedure). All other B5 released-truth wording intact.
- `docs/DOCKER-INSTALL.md` (C4, the ~L331 statement): same secret-based mechanism wording; all other B5 wording intact.
- `scripts/release_provenance_manifest.py`: `OBJECTIVE` → `"013-c"` + docstring reference (013-c).
- `tests/test_release_provenance_manifest.py`: E3 objective assertion → `"013-c"` (the historical 013-b wheel-ruling comment intentionally untouched).
- `packaging/release_provenance_manifest.json` → `M_W2`: `objective "013-c"`; not-yet-published state (`oci.published: false`, `oci.image_digest: null`, no `release` key, `status.released: false`); `gateway_peer.commit = 08ca421bee1ddca62078302b910e8be88cf705be`; `artifacts.wheel.sha256 = oci.wheel_sha256 = 879baa3ad19e0f513090add965d267957d27f7bcd904d1e225586d76126f8b19` (= `H_new`, 83,352 B, unchanged); `artifacts.sdist.sha256 = 8e0298f0ba10b2f633bace7d9369cdb866960d65921493ffc0db613944efbd6e` (NEW — 437,124 B, 107 entries; equals a fresh `uv build` at W2, verified); `generated_from.git_commit = 3deb1fbaa87e45b939e839a4762fd2ca99eb50ae` (= W1).

**No other file changed** in this round (verified: `git diff --name-only b9b9039…..W2` = the 9 files above; the pre-existing unrelated worktree items — `oap/runtime.env.example` modification and the empty root files `Local`/`clean`/`unchanged` — are untouched and uncommitted, exactly as found at round start).

## Acceptance evidence
### C1 — PASSED (implementation + local proof)
- Both push references qualified: run-log proof at W — the failing push targeted `ghcr.io/ulfe-lmi/slaif-local-coding:sha-9c04669a4fcbb65267fc6cd19f0b8176ec33a5e2` (qualified; the 013-b unqualified form is gone).
- `python3 scripts/release_registry_publish.py --self-check-refs` → `reference self-check OK: sha-tag ghcr.io/ulfe-lmi/slaif-local-coding:sha-0000000000000000000000000000000000000000; release-tag ghcr.io/ulfe-lmi/slaif-local-coding:0.1.0` (fixture git-sha, no host push).
- Note on the "e.g. unit test" form: the order's C5 requires NO test/manifest/doc changes in W1 and W1's tree to leave the sdist inputs (which include `tests/`) mutually consistent with the committed `013-b` manifest so CI at W1 is 4/4 green; a new `tests/` file in W1 would break that gate, and `pyproject.toml` is frozen. The proof is therefore implemented inside the C1-owned script (`scripts/` is not an sdist input) as an assertion of the exact reference strings for a fixture sha, run as part of the local gate set below.

### C2 — PASSED
- The five exact edits landed in W1 (see Changes); workflow remains `workflow_dispatch`-only; `permissions: contents: read` only; no echo/unmasked environment dump of the token anywhere in the workflow.

### C3 — PASSED (provisioned; value never exposed)
- Credential identity (identity only, NEVER the value): account `jpers1`, classic PAT, scopes `read:org, repo, workflow`, org `ulfe-lmi` member with admin on this repository — the same credential identity the coding wrapper already uses for `gh` operations.
- Redacted command: `gh auth token | gh secret set SLAIF_GHCR_TOKEN --repo ulfe-lmi/slaif-local-coding` (value transferred through the pipe; never on a visible command line, never printed; `gh secret list` shows only the name).
- Secret `SLAIF_GHCR_TOKEN` created `2026-09-17T11:27:42Z` — AFTER W2's CI was fully green (run `35215420037` SUCCESS 4/4) and BEFORE the C6 dispatch (run `35215843816` started `2026-09-17T11:28:13Z`), exactly per the order's timing.
- No new token/credential created; wrapper auth unaltered; no other repository secret touched; NO repository Actions/security setting modified (the ceiling remains `read` — verified unchanged by the order's own verification and by this round never touching it).

### C4 — PASSED
- Exactly the three GITHUB_TOKEN-only publication statements updated (two in `docs/RELEASE-ARTIFACT-POLICY.md`, one in `docs/DOCKER-INSTALL.md`); zero remaining `GITHUB_TOKEN` occurrences in those docs or in `release-image.yml` (grep-verified).
- Content present: dispatch-only loading of the secret; never printed; credential identity class (org-member classic PAT, `repo` scope); explicit rejection of the repo-ceiling alternative; post-release hardening advisory (dedicated fine-grained `packages: write` + `contents: read` PAT + rotation procedure).
- B5 released-truth wording intact: path-only digest references (no literal digest in any document); no document cites the current sdist hash or the manifest `objective` field; the Git tag `v0.1.0` and the GitHub Release are described as strategy post-merge acts that do not exist (verified: zero Git tags and zero GitHub releases on the repository at report time).

### C5 — PASSED
- W1 = child of `b9b9039…` (4 files; NO generator/test/manifest/doc changes; `oap/` excluded from every artifact; `scripts/` and `release-image.yml` not sdist inputs). Fresh `uv build` at W1's tree reproduced the committed manifest hashes byte-for-byte (wheel `879baa…`, sdist `73cc354…`) — sdist inputs and committed `013-b` manifest mutually consistent.
- CI at W1 FULLY GREEN 4/4 — run `35215178452`: `test` SUCCESS (1097 passed, 27 skipped), `gateway-contract` SUCCESS, `docker` SUCCESS (two-file compose build, all 15 phases), `docker-published` SUCCESS (explicit not-yet-published skip, record absent).
- W2 = child of W1 (5 files). CI at W2 FULLY GREEN 4/4 — run `35215420037`: `test` SUCCESS (1097 passed, 27 skipped), `gateway-contract` SUCCESS, `docker` SUCCESS, `docker-published` SUCCESS with the explicit line `not yet published (packaging/release_record.json absent) — docker-published skipped`.
- **No-image-change proof (required):** `git diff --name-only dfa77fb442a82754bb6af21a2e0fb0af29ddfbab..9c04669a4fcbb65267fc6cd19f0b8176ec33a5e2` = exactly:
  ```text
  .github/workflows/release-image.yml
  docs/DOCKER-INSTALL.md
  docs/RELEASE-ARTIFACT-POLICY.md
  oap/active
  oap/orders/013-c-fix-registry-credential-and-complete-publication.md
  oap/reports/013-b-repin-peer-and-complete-publication.md
  packaging/release_provenance_manifest.json
  scripts/release_provenance_manifest.py
  scripts/release_registry_publish.py
  tests/test_release_provenance_manifest.py
  ```
  Build-context intersection (`Dockerfile`, `.dockerignore`, `pyproject.toml`, `uv.lock`, `LICENSE`, `NOTICE`, `README.md`, `src/`): **NONE** — grep over the list returned no match. Therefore the image built at W2 (locally tagged `slaif-local-coding:0.1.0-<W2>`; runner-built local image `sha256:3a35da7b6d865de213ba144da67c741fd932025c1ed403584d1fad25e2a14c34` in the failed run) is layer-identical to the S''-built image modulo the per-build `org.opencontainers.image.revision` label (design intent; the revision label at W would be W, at S'' it was S'').

### C6 — BLOCKED (the round's blocker; genuine human-authority boundary)
- Pre-dispatch anonymous registry probe (token NOT in the environment; `scripts/ghcr_tag_check.py`): `0.1.0` → `absent`; `sha-9c04669a4fcbb65267fc6cd19f0b8176ec33a5e2` → `absent` (2026-09-17T11:28Z, immediately before dispatch).
- Dispatch: `gh workflow run release-image.yml --ref oap/013-mvp-release-publication` (branch tip verified = W before dispatch; a `--ref <sha>` dispatch attempt returned GitHub's 422 "No ref found" for a raw SHA — the dispatch API takes a ref name; the by-branch dispatch is the equivalent at the same head). Run **`35215843816`**, headSha `9c04669a4fcbb65267fc6cd19f0b8176ec33a5e2`, started `2026-09-17T11:28:13Z`, completed `2026-09-17T11:28:40Z`, `completed/failure`.
- Per-step result (run log): `checkout` success → **`Fail fast when the registry credential secret is missing` SUCCESS** (`SLAIF_GHCR_TOKEN present (value never printed)`) → `setup-uv`/`setup-python` success → **wheel-binding step SUCCESS** (`fresh wheel sha256: 879baa3ad19e0f513090add965d267957d27f7bcd904d1e225586d76126f8b19` = `manifest wheel sha256: 879baa…` = `H_new`) → **two-file compose image build SUCCESS** (built image `sha256:3a35da7b6d…` local) → **`Authenticate to GHCR (SLAIF_GHCR_TOKEN repository secret)` SUCCESS** (`docker login ghcr.io -u "ulfe-lmi" --password-stdin`; the log shows the env as masked `SLAIF_GHCR_TOKEN: ***`) → **`Push tags and registry-verify a single digest` FAILURE** with the exact error line:
  ```text
  PublishError: docker push ghcr.io/ulfe-lmi/slaif-local-coding:sha-9c04669a4fcbb65267fc6cd19f0b8176ec33a5e2 failed: denied: permission_denied: The token provided does not match expected scopes.
  ```
- Classification per re-adjudication 3: a **permission/credential error at the push step, distinct from a fixable in-repo defect** — the token authenticated (login succeeded) but the registry denied the push scope. The candidate causes are all human-authority items: org SSO enforcement on the PAT, org-level package policy, or token-scope interaction; none is distinguishable from, or fixable by, in-repo evidence, and none is a repository security setting this round may touch (the ceiling stays `read`).
- Per the order's C6 stop law: **NO re-dispatch** (the failure is not transient-infrastructure; a second dispatch is not permitted for this class), no workaround, no ceiling change. `D` not captured; independent `ghcr_tag_check.py` post-publication verification NOT RUN (nothing published to verify).
- **Registry state stated exactly:** post-failure anonymous probes (2026-09-17T11:30:34Z): `0.1.0` → `absent`; `sha-9c04669a4fcbb65267fc6cd19f0b8176ec33a5e2` → `absent`. No partial state: the push failed before any manifest was accepted, so no tag was written, no package object was created, and no orphan-tag cleanup is needed (orphan cleanup is a strategic act regardless).
- **013-b B8 failure evidence re-cited (the blocker this round resolves the mechanism of):** runs `35208313536` and `35209542430` (both at `S''` = `dfa77fb…`), both failing at the push step with the exact line `PublishError: docker push ulfe-lmi/slaif-local-coding:sha-dfa77fb442a82754bb6af21a2e0fb0af29ddfbab failed: unauthorized: access token has insufficient scopes` (GITHUB_TOKEN clamped by `default_workflow_permissions = "read"`). The 013-c run shows the C1/C2 mechanism fully engaged (qualified reference; secret present and used for login) — the remaining denial is at the token-scope/permission boundary.

### C7 — NOT RUN
- No `D` → `packaging/release_record.json` was NOT written and `P` was NOT created. `P` remains defined for the round that actually publishes: child of W, EXACTLY two files (`packaging/release_record.json` per the 013-a R1 field set with `image_source_commit = W`, `oci_image_digest = sha256:<D>`, `oci_tags = ["0.1.0", "sha-<W>"]`, `published_at` RFC 3339 UTC of the successful run, `publication_workflow_run_id` = the successful run id; and `M_P` regenerated from W's tree in the published state).

### C8 — NOT RUN
- CI at `P` (including the EXECUTED `docker-published` job) and the `P`-parented report are NOT RUN: no `P`, no published image. The `docker-published` job's correct at-W behavior (explicit not-yet-published skip) is verified in the CI section.

## Verification
All local gates at W2 (working tree = W2 exactly):
- `uv run --frozen ruff check .` / repo venv equivalent: **PASSED** — `All checks passed!`
- `uv run --frozen ruff format --check .`: **PASSED** — `358 files already formatted`
- mypy in the CI-equivalent environment (fresh `UV_PROJECT_ENVIRONMENT` venv, `uv sync --frozen --extra dev` ONLY, mirroring the CI `test` job): `mypy src tests` → **PASSED** — `Success: no issues found in 71 source files`. Note: the long-lived repo venv additionally carries the `gateway-contract` group (SQLAlchemy), which makes two pre-existing `type: ignore[import-not-found]` comments in `scripts/gateway_accounting_rehearsal.py` report as unused locally; with the CI-identical dev-only environment they are used and mypy is clean (consistent with the green CI history of this tree). No file in this round touches that script.
- `uv run --frozen pytest -q` (repo venv): **PASSED** — `1098 passed, 26 skipped in 79.40s` (the standing 26 routine skips remain as designed; the one extra local pass vs CI is a Gateway-dependent test enabled by the local venv's `gateway-contract` group — CI reports `1097 passed, 27 skipped` in its dev-only environment)
- `python -m compileall -q src tests oap/bin scripts`: **PASSED**
- `bash -n` on changed shell scripts: **NOT NEEDED** — this round changed no shell scripts (the CI `bash -n oap/bin/*.sh packaging/*.sh` gate ran green within both W1/W2 `test` jobs)
- `uv build` (fresh, at W2): **PASSED** — wheel `879baa3ad19e0f513090add965d267957d27f7bcd904d1e225586d76126f8b19` (= `H_new`) and sdist `8e0298f0ba10b2f633bace7d9369cdb866960d65921493ffc0db613944efbd6e` (= `M_W2` sdist hash); byte-for-byte reproducible
- `python scripts/artifact_policy_check.py --dist <fresh> --inspect`: **PASSED** — `ok: true, violations: []`
- `python scripts/artifact_policy_check.py --dist <fresh> --install-smoke`: **PASSED** — `ok: true, violations: []`
- manifest module suite `pytest -q tests/test_release_provenance_manifest.py` (at W2, `M_W2` committed): **PASSED** — `18 passed`
- gateway-contract local re-run: fresh checkout of `ulfe-lmi/slaif-api-gateway` at `08ca421bee1ddca62078302b910e8be88cf705be` (origin/HEAD verified), `SLAIF_GATEWAY_ROOT=… python scripts/gateway_contract.py --gateway-root … --run-tests`: **PASSED** — `tests_collected: 18, tests_passed: 18, tests_failed: 0, tests_skipped: 0, tests_errors: 0, network_guard: "enabled"`
- `docker compose -f compose.yaml -f compose.build.yaml config --quiet` and `docker compose -f compose.yaml config --quiet` (temporary 0-byte env/config files, established 013-b pattern): **PASSED** — render only; **NO host docker build/run/up**
- `python3 scripts/release_registry_publish.py --self-check-refs`: **PASSED** (see C1)
- Pre-dispatch and post-failure anonymous registry probes (`ghcr_tag_check.py`): **PASSED** — exact outputs in C6 (both tags `absent` at both moments)
- Protected-model live matrix (text/tool/SSE/vision/…): **NOT RUN** — explicit non-goal of this order (no protected-model/Qwen inference anywhere; fake/synthetic upstreams only)
- Real Codex E2E: **NOT RUN** — not ordered this round

## Live model/service evidence
- No live model calls were made this round (order non-goal: NO protected-model/Qwen inference anywhere).
- Registry (anonymous, read-only) via `scripts/ghcr_tag_check.py`:
  - pre-dispatch (2026-09-17T11:28Z): `0.1.0` → `absent`; `sha-9c04669a4fcbb65267fc6cd19f0b8176ec33a5e2` → `absent`
  - post-failure (2026-09-17T11:30:34Z): `0.1.0` → `absent`; `sha-9c04669a4fcbb65267fc6cd19f0b8176ec33a5e2` → `absent`
- Protected-host invariance (read-only probes only; no protected resource was touched; NO docker build/run/up on the host; sudo used only for read-only `docker ps`):

| Item | Before (2026-09-17T11:12:20Z) | After (2026-09-17T11:31:15Z) |
|---|---|---|
| `qwen-serving-vision.service` | active, MainPID=23961 | active, MainPID=23961 |
| `qwen-serving.service` | inactive | inactive |
| Port 18020 | `LISTEN 0.0.0.0:18020`, owner `vllm pid=23961` only | identical |
| Ports 18031/18033/18034 | closed | closed |
| `docker ps -a` | three pre-existing exited non-slaif containers (`0e3109680183`/`cc5e7d551c0a` — `chrockey/fpt-votenet:v0.1.0`, Exited 2 years ago; `379dcff9d7f2` — `hello-world`, Exited 2 years ago) | identical (same IDs/images/statuses) |
| `~/.codex/qwen-neumann.config.toml` | size=858, mode=600, mtime=2026-09-13 11:59:21.852183775 +0200 | identical |

## GitHub CI / required checks
- CI at W1 (`3deb1fb…`): run **35215178452** — `test`, `gateway-contract`, `docker`, `docker-published`: **4/4 SUCCESS** (`test` log: `1097 passed, 27 skipped`; `docker-published` explicit not-yet-published skip, record absent)
- CI at W2 (`9c04669…` = W): run **35215420037** — `test`, `gateway-contract`, `docker`, `docker-published`: **4/4 SUCCESS** (`test` log: `1097 passed, 27 skipped`; `docker-published` explicit line `not yet published (packaging/release_record.json absent) — docker-published skipped`)
- CI at P: N/A — `P` does not exist this round
- Release-workflow run at W: **35215843816** — `completed/failure` at the push step (exact error in C6); every pre-push step SUCCESS
- All required green at drafting: YES for all CI that could run at this round's final non-report commit (W); the release publication run itself is the blocker (see C6)
- Report-head checks may be pending at publication; strategy verifies

## Local setup/dependencies
- Repository-owned venv via `uv` (locked/frozen installs); no new dependencies; no changes to `pyproject.toml`/`uv.lock` (frozen by this order).
- The repository venv additionally holds the `gateway-contract` dev group (used for the local gateway-contract gate and manifest-suite runs; see the mypy note in Verification).
- Passwordless sudo used only for read-only `docker ps` probes (established pattern). No terminal operator recruited.
- Disposable `/tmp` scratch only (outside the repository): fresh `uv build` output directories, the fresh dev-only CI-mirror mypy venv, the fresh gateway checkout at `08ca421…`, and the 0-byte compose render temp files.
- One repository-state mutation authorized and performed this round: the `SLAIF_GHCR_TOKEN` repository secret (C3; name/timestamp only above; value never exposed). It REMAINS provisioned after this round's block; its retention/rotation/removal is a strategy/human decision (post-release hardening advisory documented in the docs per C4).

## Documentation
- Updated exactly per C4 (the three GITHUB_TOKEN-only statements → secret-based mechanism with dispatch-only loading, never-printed, credential identity class, rejected-ceiling statement, and post-release hardening advisory). All other B5 released-truth wording intact and still true at this round's completion (no literal digest in any document; tag/Release objects do not exist and no document claims they do; publication described as registry-only with cutover NOT performed).
- No other documentation changes. `src/`, `pyproject.toml`, `uv.lock`, `config/`, `Dockerfile`, `.dockerignore`, `compose.yaml`, `compose.build.yaml`, the docker-qualification harness, and `ci.yml` are byte-identical across this round (verified by diff; the C8 narrow gate-defect exception was NOT needed because `docker-published` was never executed this round).

## Safety/scope confirmations
- Unrelated files preserved: pre-existing worktree items (`oap/runtime.env.example` modification; empty root files `Local`, `clean`, `unchanged`) untouched and uncommitted; no reset/clean/overwrite performed.
- Secrets/raw content: the PAT value never entered any report, commit, log, or command line (secret set via pipe; workflow masks the reference; CI log shows `SLAIF_GHCR_TOKEN: ***`); no prompts/source/images/tool outputs/bodies in any artifact; protected-host paths cited only as established conventions.
- Production/protected resources: **Protected 18020/Qwen/Codex fixture changed: NO** (before/after probes identical; no systemd/network/service/firewall/VPN mutation; no host docker build/run/up).
- NO Gateway-repository mutation (read-only fresh checkout for the local contract gate; peer remains `08ca421…`). NO Git tag and NO GitHub Release by coding (both remain strategy post-merge acts; verified zero of each at report time). NO modification of the repository Actions workflow-permission ceiling or any other repository security setting, in any direction (ceiling remains `read`).
- NO creation of new credentials (the secret holds the wrapper's existing PAT, transferred without minting anything new). NO version change (stays `0.1.0`).
- NO registry publication other than the attempted two tags of the single image built at W — the attempt wrote NOTHING (both tags `absent` after the failure; no package object; no repoints).
- Required tests skipped/not run: the protected-model live matrix and real Codex E2E are NOT RUN by explicit order non-goal; the `docker-published` EXECUTED gate is NOT RUN (no `P`/no published image) — all stated as such, none claimed passed.
- Scope deviation: none; the single disclosed judgment call is the C1 proof's form (in-script deterministic self-check rather than a new `tests/` file), forced by C5's W1 sdist-consistency + "no test changes in W1" constraints (see C1 note).
- Extra objective PR: NO. Coding merge: NO. Auto-merge: none requested or present.
- Active/order edited: NO (strategic-authored order bytes committed verbatim; SHA-256 recorded above). Report commit report-only: will be verified at publication (only `oap/reports/013-c-…md` staged).
- Worktree residue: untouched (as above).

## Known limitations/blockers
- **The blocker:** `denied: permission_denied: The token provided does not match expected scopes.` on `docker push` to `ghcr.io/ulfe-lmi/slaif-local-coding` with the provisioned classic PAT (login to `ghcr.io` with the same credential SUCCEEDED). From in-repo evidence the exact human-side cause cannot be distinguished among: (a) org SSO enforcement on the PAT (the PAT's `repo` scope not authorized for org-owned resources until the user authorizes org SSO), (b) org-level package permission policy, or (c) another token-scope interaction. All three are outside coding authority per re-adjudication 3.
- `D` is unknown; the image built at W exists only as the runner's local image (ID `sha256:3a35da7b6d…`), discarded with the runner; the registry holds no object for this repository's package.
- The `SLAIF_GHCR_TOKEN` secret remains in the repository (provisioned per C3 before the block); strategy/human decides retention, use in the next round, or removal.
- The `docker-published` CI job has still never executed; its first execution (at a future `P`) may surface the C8 narrow gate-defect class and would then be handled per C8.

## Recommended strategic follow-up
Factual only; strategy decides:
1. The push denial is at the PAT/org boundary: candidate human-side remedies to adjudicate are (a) authorizing the existing PAT for org `ulfe-lmi` SSO, (b) an org package-permission/policy check for `jpers1`, or (c) a different human-authorized credential class for the dispatch-only workflow. Any of these is a human/strategic act; none is a repository security setting.
2. Once publication succeeds at W (or a successor head), the remainder of the round sequence is mechanical per C7/C8: record `P` (exactly two files) → CI at `P` including the executed `docker-published` → report.
3. The `SLAIF_GHCR_TOKEN` secret's retention/rotation/removal and the documented post-release hardening advisory (dedicated fine-grained `packages: write` + `contents: read` PAT) are open human/strategic items.
4. PR #15 remains the single objective-013 PR, `OPEN`/`MERGEABLE`, head = W2, base = `main` @ `a04693e…`; the 013-b BLOCKED precedent at B8 is superseded by this round's C6 boundary evidence (mechanism now proven engaged; denial now at the token-scope/permission class).

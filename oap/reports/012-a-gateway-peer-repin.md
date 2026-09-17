# OAP Coding-Agent Report — 012-a

## Work order
- Identifier: `012-a`; order path: `oap/orders/012-a-gateway-peer-repin.md`; numeric objective `012`
- PR mode: `CREATED_NEW_PR`

## Status
PARTIAL

Rationale (single blocking fact): order item 6 / C3 / non-goals require the release
artifact bytes to remain exactly wheel `7cede0b8e930463400a40662248a97aae22f75b0512dcd8151d6122a99157166`
and sdist `4ba17680c55c557494593087f4d632abb6a79f0c595ecab08bb2414abc86f5d6`, while S5
mandates the README Objective-011 status-table fix (and C6 independently bans the
`this PR`/`pre-merge` language that row carried). The build configuration embeds
`README.md` into the wheel `dist-info/METADATA` (long description) and whitelists
`README.md`, `docs/`, and `tests/` into the sdist, so any mandated S5 edit necessarily
changes both artifact hashes. A clean rebuild from the final implementation state
proves the divergence at byte level (see C3): all 20 wheel runtime files are
byte-identical to the Objective-011 record; only the embedded documentation metadata
differs. Every other criterion (C1, C2, C4, C5, C6, C7, C8, C9, C10) is met. This is
a genuine strategic re-adjudication (scope conflict inside the order), not an
in-scope defect; authority is returned with exact evidence.

## Executive summary
Re-pinned the continuous-test Gateway peer from `65666f5886832034c52211fdd7604046557e6ada`
to `1fccaa746df6cd44f1ddf8c2ec5cf6ea9f18b1cb` (verified current gateway default-branch
main, advanced by merged gateway PR #302 / Objective 165 on 2026-09-17), proved the
contract-surface byte identity at blob level, regenerated the release provenance
manifest, updated the Dockerfile label input and the cutover state-machine default
authority, and reconciled the post-011 current-facing documentation drift (README 011
row, TOPOLOGY, SLAIF-GATEWAY-INTEGRATION, RELEASE-CUTOVER-RUNBOOK,
RELEASE-ARTIFACT-POLICY, IMPLEMENTATION-ROADMAP, COMPLETENESS). The strict
18-test gate passes at the new pin with the network guard active. All required CI
checks pass at both pushed heads. The sole exception to the order's acceptance set is
the literal artifact-byte-identity requirement (C3 item 3 / item 6), which is
mechanically incompatible with the mandated S5 README fix; the manifest was
regenerated from the actual final state and the divergence is documented with
byte-level proof. No merge, no release, no cutover, no protected-host mutation.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #14 — https://github.com/ulfe-lmi/slaif-local-coding/pull/14 — `OPEN`, non-draft,
  exactly one PR for objective 012 (verified: zero other open PRs at order time and
  at push time)
- Base: `main` @ `e860e0bff687afded7782fb2687b5b435792459a` (Objective-011 merge commit)
- Head branch: `oap/012-gateway-peer-repin`
- Starting remote SHA: `e860e0bff687afded7782fb2687b5b435792459a`
- Implementation head SHA: `ef790602e64c097ae5ed2fe4b341eff608c1cfe7`
- Report publication commit: SELF
- Implementation commits pushed before report (oldest first):
  1. `db88612c1919b0c1ff6942e5609c165b6d3e92ac` — S1/S4/S5 doc+fixture+state-machine+generator-constant changes and the activated-order transcript
  2. `9a6edc69f9df131851dd2779670ce2ba519ae53d` — regenerated release provenance manifest (S3)
  3. `ef790602e64c097ae5ed2fe4b341eff608c1cfe7` — C6 fix: remaining `this PR (pre-merge)` 011 status row in `oap/COMPLETENESS.md`
- New PR this round: yes (#14); amended existing: no; merge performed: NO

## Changes and files
16 files changed, 444 insertions(+), 48 deletions(-) vs base `e860e0b`.

| File | Workstream | +/- |
| --- | --- | --- |
| `tests/fixtures/gateway/current_peer_authority.json` | S1 | 1/1 |
| `packaging/release_provenance_manifest.json` | S3 | 11/11 |
| `scripts/release_provenance_manifest.py` | S3 (generator objective constant `011-a` -> `012-a`) | 1/1 |
| `tests/test_release_provenance_manifest.py` | S3 (objective expectation only) | 1/1 |
| `Dockerfile` | S4 (`SLAIF_GATEWAY_PEER_SHA` ARG -> new pin) | 1/1 |
| `scripts/cutover_state_machine.py` | S4 (`self_test` default `authority_sha` -> new pin; constant update only) | 1/1 |
| `tests/test_cutover_state_machine.py` | S4 (fixture snapshot -> new pin) | 1/1 |
| `README.md` | S5 (011 row -> `PR #13` + `e860e0bff687afded7782fb2687b5b435792459a`) | 1/1 |
| `docs/TOPOLOGY.md` | S5 (a) current peer statement + 012 provenance, (b) 010-era inspection record annotated, (c) multi-host bullet -> current D1 binding law, plus section-6 stale `this PR` phrasing | 24/9 |
| `docs/SLAIF-GATEWAY-INTEGRATION.md` | S5 (current continuous-test peer bullet -> new pin + 012 provenance; 006-handoff current-peer parenthetical pointed at the current statement) | 13/7 |
| `docs/RELEASE-CUTOVER-RUNBOOK.md` | S5 (`gateway.authority_sha` -> new pin + provenance; preconditions 012/012-a manifest authority) | 9/7 |
| `docs/RELEASE-ARTIFACT-POLICY.md` | S5 (cutover-authority chain scoped to 011 state + 012 regeneration sentence) | 11/3 |
| `docs/IMPLEMENTATION-ROADMAP.md` | S5 (two stale `this PR` occurrences fixed) | 3/2 |
| `oap/COMPLETENESS.md` | S5 audit target (011 merged-state row `this PR (pre-merge)` -> `PR #13` + merge commit) | 1/1 |
| `oap/active` | transcript (strategic bytes unchanged: `011-a` -> `012-a` as found) | 1/1 |
| `oap/orders/012-a-gateway-peer-repin.md` | transcript (activated order, new file, committed byte-unchanged) | 364/0 |

## Acceptance evidence

### Criterion 1 — Pin updated, gate green at new pin — MET
- Fixture diff is exactly one line: `"commit": "65666f58..."` -> `"commit": "1fccaa746df6cd44f1ddf8c2ec5cf6ea9f18b1cb"`; schema (`slaif-local-gateway-peer-authority-v1`, v1), repository, server (`local-coding-v1` v2, `process_local_inclusive_horizon_fail_closed`), client (`codex-0.149-responses-v1` v4), and purpose unchanged.
- `uv run --frozen python scripts/gateway_contract.py --emit-github-output /tmp/oap-012-emit.out` emitted `gateway_repository=ulfe-lmi/slaif-api-gateway` and `gateway_commit=1fccaa746df6cd44f1ddf8c2ec5cf6ea9f18b1cb` (plus the four module fields, fixture `valid`, 7 fields).
- Clean throwaway checkout (blobless `git clone` of the public gateway repo, checked out at the new pin, `HEAD` = `1fccaa746df6cd44f1ddf8c2ec5cf6ea9f18b1cb`, origin proven, clean tree; removed afterwards):
  `SLAIF_GATEWAY_ROOT=/tmp/slaif-012-gw-checkout uv run --frozen python scripts/gateway_contract.py --gateway-root /tmp/slaif-012-gw-checkout --run-tests`
  -> `{"checkout_clean": true, "client_module": "codex-0.149-responses-v1", "commit": "1fccaa746df6cd44f1ddf8c2ec5cf6ea9f18b1cb", "network_guard": "enabled", "repository": "ulfe-lmi/slaif-api-gateway", "server_module": "local-coding-v1", "tests_collected": 18, "tests_errors": 0, "tests_failed": 0, "tests_passed": 18, "tests_skipped": 0}` — 18/18, zero skipped/failed/errors, network guard active, no external egress during the test phase.

### Criterion 2 — Contract-surface identity proven — MET
Independently re-verified via GitHub read-only (`gh api repos/ulfe-lmi/slaif-api-gateway/contents/<path>?ref=<sha>` `.sha`, i.e. git blob SHA) at round time:

| Contract source file | Blob SHA @ old pin `65666f58...` | Blob SHA @ new pin `1fccaa74...` |
| --- | --- | --- |
| `app/slaif_gateway/modules/servers/local_coding/contract.py` | `9e8ae5ef8e1f9d8d48bf3627b9a767d86593a6ac` | `9e8ae5ef8e1f9d8d48bf3627b9a767d86593a6ac` |
| `app/slaif_gateway/modules/clients/codex_0149.py` | `8976c984c4430d65b3d36bad8565062a8c6f955a` | `8976c984c4430d65b3d36bad8565062a8c6f955a` |
| `app/slaif_gateway/providers/streaming.py` | `73cc9f99e8c3cb2f3eb95173344bfbdc211c71ff` | `73cc9f99e8c3cb2f3eb95173344bfbdc211c71ff` |

All six values equal the strategic-verified values in order item 4 (old-pin triple and
new-pin triple match respectively). No divergence; the pin change proceeded.

### Criterion 3 — Release provenance regenerated, artifacts invariant — PARTIAL (see Status)
- `packaging/release_provenance_manifest.json` regenerated from the final implementation state with `uv run --frozen python scripts/release_provenance_manifest.py --dist <clean dist> --emit packaging/release_provenance_manifest.json` at generating commit `db88612c1919b0c1ff6942e5609c165b6d3e92ac`:
  - `objective: "012-a"` — done
  - `gateway_peer.commit` = `1fccaa746df6cd44f1ddf8c2ec5cf6ea9f18b1cb` — done
  - `slaif-local-coding.gateway.peer.sha` OCI label = new pin — done
  - `generated_from.git_commit` = `db88612c1919b0c1ff6942e5609c165b6d3e92ac` (the generating commit; ancestor of the implementation head, satisfying the E3 gate) — done
  - `status` fields: `cutover_performed: false`, `released: false`, `oci.published: false`, `oci.image_digest: null` — unchanged
  - `oci.dockerfile_sha256` advanced to `119f72537195448414ebf77f2ef1c81217849656a2b4d9c7897c340bc3ad5516` (the S4 Dockerfile change); all other OCI inputs (base images, compose, dockerignore), `runtime`, `templates`, `reference_compatibility`, `limitations`, and schema unchanged.
- `tests/test_release_provenance_manifest.py`: only the objective-bound expectation updated (`"011-a"` -> `"012-a"`); all other assertions, including every artifact-hash cross-check, kept; green in CI and locally.
- **Artifact invariance (NOT MET, mechanically)**: clean rebuild (`uv build` into a fresh empty dist directory, then `sha256sum`):
  - wheel: `fceadc378130dd4ffcc3f75d17b5e098577652914f541245d31247911be23aeb` (83097 B) vs required `7cede0b8...` (83070 B)
  - sdist: `910b65db8abe331fb1ad0507697c1e089fd9ea4ede2ec1792b7fac5c8f5c1240` (425234 B) vs required `4ba17680...` (424608 B)
  - Byte-level diff of old (011 record, `dist/` from the base-state build) vs rebuilt:
    - wheel (26 entries): all 20 runtime files under `slaif_local_coding/` byte-identical; only `slaif_local_coding-0.1.0.dist-info/METADATA` and `dist-info/RECORD` differ. The METADATA delta is exactly the S5-mandated README status-table row (embedded as the long description).
    - sdist (105 entries): exactly 9 differing files, all text mandated by S1/S5: `PKG-INFO` (embedded README), `README.md`, `docs/IMPLEMENTATION-ROADMAP.md`, `docs/RELEASE-ARTIFACT-POLICY.md`, `docs/RELEASE-CUTOVER-RUNBOOK.md`, `docs/TOPOLOGY.md`, `tests/fixtures/gateway/current_peer_authority.json`, `tests/test_cutover_state_machine.py`, `tests/test_release_provenance_manifest.py`.
  - Root cause: `pyproject.toml` sets `readme = "README.md"` (embedded in wheel METADATA) and the sdist target whitelist includes `README.md`, `docs/`, `tests/`. Order item 6's premise (doc changes do not touch artifact bytes) is therefore false for this build configuration; S5 and C3-as-written cannot both be satisfied.
- The manifest records the honest rebuilt hashes (self-consistency is enforced by the E3 regeneration gate and the docker CI wheel-binding step, both green); the artifact-policy verified-clean property still passes (`--inspect` -> `ok: true`, `violations: []`).

### Criterion 4 — Dockerfile + state machine — MET
- `Dockerfile` `ARG SLAIF_GATEWAY_PEER_SHA=1fccaa746df6cd44f1ddf8c2ec5cf6ea9f18b1cb` (label input only; one-line diff).
- `scripts/cutover_state_machine.py`: only the `self_test` default `authority_sha` constant updated to the new pin (one-line diff; `canonical_snapshot` semantics, transition table, rollback table, and `binding_class` handling untouched — diff review shows constant updates only).
- `tests/test_cutover_state_machine.py` fixture updated to the new pin (one line); suite green (CI + local).
- `uv run --frozen python scripts/cutover_state_machine.py --self-test` -> `{"lan_rollback_points_checked": 8, "ok": true, "pre_final_mutators": 4, "rollback_points_checked": 8, "transitions": 9}`.

### Criterion 5 — Topology manifest untouched — MET
- `docs/topology.manifest.json` byte-identical to base: `git diff e860e0b..HEAD -- docs/topology.manifest.json` is empty (0 lines). Schema stays `slaif-topology-manifest-v2`; the dated `live_facts_as_of_2026_09_14` section (including its `gateway_peer_commit` value) is preserved as an as-of snapshot; the mechanically checked sections are unchanged; no new fields, no schema bump.
- `tests/test_topology_qualification.py` green in the full suite (CI + local); `uv run --frozen python scripts/topology_qualification.py --self-test` -> `ok: true` (full decision table, both namespace probes with cleanup proof, manifest conformance — recorded in Verification below).

### Criterion 6 — Documentation truthfulness — MET
- README 011 row now reads `PR #13 | e860e0bff687afded7782fb2687b5b435792459a` with the existing status prose kept truthful; no other README changes.
- `docs/TOPOLOGY.md` (a)/(b)/(c) done as specified: (a) "Gateway peer authority" names the new pin as current, records the Objective-012 re-pin (2026-09-17), gateway PR #302 / Objective 165 provenance, documentation/OAP/doc-check-only character, and the contract-surface byte-identity fact; (b) the pinned-source inspection record keeps `65666f58...` as the Objective-010-era inspection commit and gains the truthful note that Objective 012 re-verified the identical contract surface at the new pin; (c) the multi-host bullet now states the current D1 binding law (loopback default; non-loopback legal only under the full `service_bearer_signed_identity_v1` contract; further changes only by human architecture decision) — the stale "loopback-only binding law is preserved by this objective" phrasing does not survive.
- `docs/SLAIF-GATEWAY-INTEGRATION.md`: "Current continuous-test peer" states the new pin with Objective-012 re-pin provenance (date, PR #302/obj165, blob-identity no-op fact); the Objective-007 pin history is preserved; the Objective-006 handoff section keeps its historical pins (`5ea38325ef3a3ebc69524b4679b795fab0c52935` and its 007-era context) and its current-peer claim is made truthful by pointing at the "Current continuous-test peer" statement above.
- Additional current-facing reconciliations found by the audit (S5 audit list + C6 language rule): `docs/RELEASE-CUTOVER-RUNBOOK.md` (`gateway.authority_sha` row -> new pin with provenance; preconditions updated: pre-cutover objectives 010/011/012 and the Objective-012-a regenerated manifest as cutover authority, with the 011/010/009 wheel records retained as accepted history), `docs/RELEASE-ARTIFACT-POLICY.md` (authority chain scoped: 011 set was authority for the 011 state; 012 regeneration with byte-identical runtime content is the only future cutover authority), `docs/IMPLEMENTATION-ROADMAP.md` (two stale `this PR` occurrences fixed, incl. the Objective-009 heading now `PR #11`), `oap/COMPLETENESS.md` (011 merged-state row `this PR (pre-merge)` -> `PR #13` + merge commit).
- Literal-pin audit — every non-`oap/` occurrence of `65666f58` at the final head `ef79060` (via `git grep -n 65666f58 ef79060 -- . | grep -v oap/`):

  | File:line | Context | Disposition |
  | --- | --- | --- |
  | `docs/SLAIF-GATEWAY-INTEGRATION.md:83` | current-peer bullet, provenance clause "replaced the previous pin ..." | UPDATED (current statement names the new pin; old pin retained as re-pin provenance only) |
  | `docs/TOPOLOGY.md:61` | Gateway peer authority bullet, "re-pinned by Objective 012 ... from ..." | UPDATED (same provenance pattern) |
  | `docs/TOPOLOGY.md:102` | "Pinned-Gateway source inspection (Objective-010-era commit ..., read-only)" | HISTORICAL (dated 010-era inspection record, left intact per S5(b)) |
  | `docs/topology.manifest.json:135` | `gateway_peer_commit` inside `live_facts_as_of_2026_09_14` | HISTORICAL (as-of snapshot, byte-identical per S6/C5) |

- `oap/orders` + `oap/reports` vs base: every pre-existing file byte-identical (`git diff e860e0b..HEAD -- oap/orders oap/reports` shows only the addition of the activated order file `oap/orders/012-a-gateway-peer-repin.md`, committed with unchanged strategic bytes; `oap/reports` diff empty). The `oap/active` transcript change (`011-a` -> `012-a`) is the normal-loop transcript commit.
- No `this PR` / `open` / `pre-merge` PR-state language remains in any current-facing doc: exact-phrase scan `git grep -nE "this PR|pre-merge|open PR"` over `README.md`, `docs/`, `oap/COMPLETENESS.md` at the final head returns zero matches.
- Historical pins preserved: `5ea38325ef3a3ebc69524b4679b795fab0c52935` (Objective-005 acceptance pin) and `65666f58...` in dated 006/007/010 historical context remain intact.

### Criterion 7 — CI green at implementation head AND report head — MET (at both pushed heads; report-head run triggered by the report commit will be verified by strategy)
- Implementation head `9a6edc69f9df131851dd2779670ce2ba519ae53d` (first push): run `35180569497` — `test` PASS (job 105071601660), `gateway-contract` PASS (job 105071601860, checking out the NEW pin), `docker` PASS (job 105071601862: wheel-binding to the regenerated manifest, label check against the new pin, content scan, hardening, operations, teardown).
- Final implementation head `ef790602e64c097ae5ed2fe4b341eff608c1cfe7`: run `35180803133` — `test` PASS (job 105072316059), `gateway-contract` PASS (job 105072316086), `docker` PASS (job 105072315915).
- No failed, cancelled, pending, or missing required checks at either head. No in-scope repair was required (no red checks occurred).

### Criterion 8 — Protected host before/after identical — MET
Read-only probes only (systemctl status/`show`, one `GET /health` on 127.0.0.1:18020, TCP presence checks, `stat`, `loginctl`, `docker ps -a`/`docker images` via passwordless sudo, read-only). No service was started, stopped, restarted, reconfigured, or touched.

| Item | Before | After | Identical |
| --- | --- | --- | --- |
| `qwen-serving-vision.service` ActiveState/SubState | active/running | active/running | yes |
| MainPID | 23961 | 23961 | yes |
| Since | 2026-09-06 18:57:26 CEST | 2026-09-06 18:57:26 CEST | yes |
| `127.0.0.1:18020/health` | 200 | 200 | yes |
| port 18021 | absent | absent | yes |
| port 18031 | absent | absent | yes |
| port 18032 | absent | absent | yes |
| port 18033 | absent | absent | yes |
| port 18034 | absent | absent | yes |
| `~/.codex/qwen-neumann.config.toml` mode/mtime | 600 / 2026-09-13 11:59:21.852183775 +0200 | 600 / 2026-09-13 11:59:21.852183775 +0200 | yes |
| `Linger` (user janezp) | no | no | yes |
| `zap-it-lan.service` (context, out of C8 list) | activating/auto-restart, MainPID=0 | activating/auto-restart, MainPID=0 | yes |
| `docker ps -a` | 3 exited containers (2 years old, no published ports): `beautiful_cartwright`, `beautiful_haibt`, `kind_brown` | same 3, same states | yes |
| `docker images` | `postgres:16`, `hello-world:latest`, `chrockey/fpt-votenet:v0.1.0` | same 3 | yes |
| slaif-named containers/images | 0 | 0 | yes |

### Criterion 9 — No publication/mutation — MET
- Zero new tags (`git ls-remote --tags origin` -> 0) and zero GitHub releases (`releases` -> 0) at report time.
- No image pushed anywhere: no push-capable workflow ran on the branch (`release-image.yml` is `workflow_dispatch`-only; zero runs for `oap/012-gateway-peer-repin`); no docker push was performed locally.
- `ulfe-lmi/slaif-api-gateway` unmodified (read-only queries only): default-branch main = `1fccaa746df6cd44f1ddf8c2ec5cf6ea9f18b1cb` at report time — i.e. exactly the new pin, unchanged since the order's verification.
- No live profile/route/service change: see C8 (all probes identical before/after).

### Criterion 10 — Freeze held — MET
- `uv.lock` SHA-256: `1237cbd179f71b99984c80f927529549f5e61eb705585ef9cf2ab0fa9e26764a` (equals the base value required by the order).
- `pyproject.toml` SHA-256: `af91f82283882f1e51ee763d635f94f1ae2534c51585c837aa61cff8a2f7dda2` (equals the base value required by the order).
- Zero `src/` files in the diff (`git diff e860e0b..HEAD --name-only -- src/` -> empty).
- All changed files are within the S1-S6 scope list plus the activated-order/active transcript and the C6-mandated `oap/COMPLETENESS.md` status-row fix (an S5-audit-list document).
- No version bump (still `0.1.0`); no dependency change; `scripts/gateway_contract.py` untouched.

## Verification
Local (protected host, repo venv via `uv`, locked/frozen):
- `git status` clean start from base `e860e0bff687afded7782fb2687b5b435792459a` on fresh branch `oap/012-gateway-peer-repin`: PASSED (pre-existing local work preserved and left uncommitted: `oap/runtime.env.example` local modification and untracked zero-byte scratch files `Local`/`clean`/`unchanged`)
- GitHub read-only blob-SHA re-verification (C2 command: `gh api repos/ulfe-lmi/slaif-api-gateway/contents/<path>?ref=<sha> --jq .sha` for 3 files x 2 refs): PASSED (table in C2)
- Clean checkout of the gateway at the new pin (throwaway path `/tmp/slaif-012-gw-checkout`, blobless clone, removed afterwards) + `SLAIF_GATEWAY_ROOT=<checkout> uv run --frozen python scripts/gateway_contract.py --gateway-root <checkout> --run-tests`: PASSED (18/18, 0 skipped/failed/errors, network guard enabled — C1)
- `uv build` into a fresh empty dist directory + `sha256sum` of wheel/sdist vs C3 hashes: FAILED against the required 011 hashes (byte-level divergence proven; see C3 — the blocking fact); rebuilt hashes `fceadc378130dd4ffcc3f75d17b5e098577652914f541245d31247911be23aeb` / `910b65db8abe331fb1ad0507697c1e089fd9ea4ede2ec1792b7fac5c8f5c1240` are what the regenerated manifest records
- `uv run --frozen pytest -q`: PASSED — 1087 passed, 26 skipped, in both environments (repo venv with the `gateway-contract` group, and a fresh CI-equivalent venv with `--extra dev` only); all 26 skips are the standing environment-conditional skips: 18 x `SLAIF_GATEWAY_ROOT is required` (current Gateway contract tests, run instead by the dedicated gate/CI job), 7 x `set SLAIF_LIVE_TEST=1` (live matrix), 1 x human-activated mutually-exclusive protected vision fixture
- `uv run --frozen ruff check .`: PASSED (All checks passed!); `uv run --frozen ruff format --check .`: PASSED (345 files already formatted)
- `uv run --frozen mypy src tests`: PASSED in the CI-equivalent venv (Success: no issues found in 70 source files). Note: in the repo venv with the locally-installed `gateway-contract` group (sqlalchemy), two pre-existing `# type: ignore[import-not-found]` comments in `scripts/gateway_accounting_rehearsal.py` (a file byte-identical to base, untouched by this round) report as unused; the CI `test` job installs only `--extra dev` (no sqlalchemy) and is green, so this is a local-environment artifact, not a code defect
- `uv run --frozen python -m compileall -q src tests oap/bin scripts`: PASSED
- `uv run --frozen python scripts/cutover_state_machine.py --self-test`: PASSED (`ok: true`, 9 transitions, 8 rollback points, 8 LAN rollback points)
- `uv run --frozen python scripts/topology_qualification.py --self-test`: PASSED (`ok: true`; full decision table, fresh-namespace probe with listener-absent cleanup proof, host-namespace probe, manifest conformance)
- `uv run --frozen python scripts/artifact_policy_check.py --dist <clean dist> --inspect`: PASSED (`ok: true`, `violations: []`, wheel top level = runtime package + dist-info only) — unchanged policy outcome
- Literal-pin audit at the final head (`git grep -n 65666f58 ef79060 -- .` excluding `oap/`, plus `git diff e860e0b..HEAD -- oap/orders oap/reports` proving `oap/` untouched): PASSED (table in C6)
- `uv run --frozen python scripts/gateway_contract.py --emit-github-output <out>`: PASSED (C1 facts)

GitHub (after push, before report):
- Exactly one PR for objective 012 (#14), branch `oap/012-gateway-peer-repin`, base `main` @ `e860e0bff687afded7782fb2687b5b435792459a`, non-draft, 15 changed files at first push (16 after the C6 fix commit)
- Required checks inspected at both pushed heads: all `success`; no in-scope repair needed (no red checks)
- C9 facts verified against GitHub at report time (tags/releases/runs/gateway main)

## Live model/service evidence
None. Explicit: no Qwen/vLLM inference call of any kind was made; the protected host received read-only status probes only (C8). No live Gateway route change. The live-test suite (`tests/test_live.py`, `tests/test_vision_e2e.py` protected path) was not run (standing skips; not required by this order).

## GitHub CI / required checks
- Implementation head `9a6edc69...`: run 35180569497 — test PASS, gateway-contract PASS (new pin), docker PASS.
- Implementation head `ef790602...` (final): run 35180803133 — test PASS, gateway-contract PASS (new pin), docker PASS.
- All required green at drafting: yes (at the final implementation head).
- Report-head checks may be pending at signal time; strategy verifies (report-only push re-triggers the three jobs).
- Prior branch runs: the two above (both final-state pushes); no failed runs, no repairs.

## Local setup/dependencies
- Existing repo venv (Python 3.12.3) synced frozen: `uv sync --frozen --extra dev --group gateway-contract` (4 packages installed for the local strict gate: greenlet, pydantic-settings, python-dotenv, sqlalchemy).
- A second throwaway CI-equivalent venv (`UV_PROJECT_ENVIRONMENT=/tmp/slaif-012-ci-venv`, `uv sync --frozen --extra dev`) was used to mirror the CI `test` job environment exactly (mypy parity); removed afterwards.
- Throwaway clean dist directory and throwaway blobless gateway checkout: created for verification, removed afterwards. No leftover checkouts/containers/processes.
- Passwordless sudo used only for read-only `docker ps -a` / `docker images` listings (C8 probe). No durable docs/config changed beyond the in-scope files.

## Documentation
Updated (all in S5 scope): `README.md`, `docs/TOPOLOGY.md`, `docs/SLAIF-GATEWAY-INTEGRATION.md`, `docs/RELEASE-CUTOVER-RUNBOOK.md`, `docs/RELEASE-ARTIFACT-POLICY.md`, `docs/IMPLEMENTATION-ROADMAP.md`, `oap/COMPLETENESS.md`. Not updated (deliberately): `docs/topology.manifest.json` (S6 as-of snapshot law), `docs/GATEWAY-CONTRACT-CI.md` (fixture-referenced, no literal pin), `docs/ADAPTER-CONFIGURATION.md` (fixture-referenced), `docs/DEPLOYMENT.md`, `docs/DOCKER-INSTALL.md`, `docs/DOCKER-SECURITY-DELTA.md` (generic label/peer descriptions without literal pins — truthful as-is).

## Safety/scope confirmations
- Unrelated files: pre-existing local modification `oap/runtime.env.example` (coding/strategic profile names) and untracked zero-byte scratch files `Local`, `clean`, `unchanged` were preserved in the working tree and NOT committed; no other unrelated changes.
- Secrets/raw content: none in the diff, PR body, or report (SHAs, blob IDs, ports, and standard protected-host status values only; no credential values, no raw payloads).
- Production/protected resources: no production systems/data touched.
- Protected 18020/Qwen/Codex fixture changed: NO (read-only probes only; C8 before/after identical).
- Required tests skipped/not run: the 26 standing environment-conditional skips listed in Verification (gateway-checkout tests, live matrix, protected vision E2E) — these are the same standing skips present at the base; no required test was skipped to get green.
- Scope deviation: one — the C6-mandated `oap/COMPLETENESS.md` status-row fix was committed after the first implementation head because the initial audit sweep missed it (exact-phrase scan caught it before publication); it is within the order's C6/S5 scope and was pushed as an in-scope implementation commit before this report.
- Extra objective PR: NO (exactly one PR, #14). Coding merge: NO. Auto-merge: not enabled.
- Active/order edited: NO (`oap/active` and the order file committed as unchanged strategic bytes; all pre-existing `oap/orders`/`oap/reports` files byte-identical to base).
- Report commit report-only: yes (this commit stages only `oap/reports/012-a-gateway-peer-repin.md`).

## Known limitations/blockers
- BLOCKING (strategic re-adjudication required): C3/item-6 artifact byte-identity vs S5 README fix — mechanically incompatible because `README.md` is embedded in the wheel METADATA and the sdist whitelist carries `README.md`/`docs/`/`tests/`. The manifest carries the honest rebuilt hashes; the runtime package content (all 20 wheel files) is byte-identical to the 011 record and the verified-clean property holds.
- Factual note: at report time `ulfe-lmi/slaif-api-gateway` main = `1fccaa746df6cd44f1ddf8c2ec5cf6ea9f18b1cb` (the new pin), unchanged.
- After this objective merges, `docs/IMPLEMENTATION-ROADMAP.md`'s "Current state" paragraph (dated 2026-09-17) will be one objective behind (it stops at 011); it contains no literal pins or stale PR-state language. Updating it further is a forward-facing doc decision for strategy.

## Recommended strategic follow-up
Factual only; strategy decides:
1. Adjudicate the artifact-hash conflict: either accept the regenerated Objective-012 artifact record (wheel `fceadc378130dd4ffcc3f75d17b5e098577652914f541245d31247911be23aeb`, sdist `910b65db8abe331fb1ad0507697c1e089fd9ea4ede2ec1792b7fac5c8f5c1240`) as the new cutover-authority record — runtime content unchanged, verified-clean property intact — or issue a corrective order (for example, decouple the README from the wheel long description, or schedule an artifact rebuild as part of the next in-scope byte change).
2. Optionally direct a roadmap "Current state" paragraph refresh for post-012.

# OAP Work Order — 012-a: Re-pin current Gateway peer and close post-011 documentation drift

## Objective

Re-pin the current continuous-test Gateway peer from
`65666f5886832034c52211fdd7604046557e6ada` to the verified current gateway
default-branch main `1fccaa746df6cd44f1ddf8c2ec5cf6ea9f18b1cb`, with a
mechanical contract-surface identity proof, regenerated release provenance,
and reconciliation of the remaining post-011 current-facing documentation
drift. After this objective merges, the release candidate's provenance,
Docker image labels, cutover state machine, and current-facing docs all bind
to the current Gateway authority, and no non-live release-readiness work
remains before the human-authorized release/cutover acts.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`
- Numeric objective: `012`; round: `012-a`
- PR mode: `CREATE_NEW_PR` (exactly one new PR for objective 012)
- Base: `main` @ `e860e0bff687afded7782fb2687b5b435792459a`
  (Objective-011 merge commit; verified live 2026-09-17; CI run
  35178140841 success on this commit: test + docker + gateway-contract)
- Required branch: `oap/012-gateway-peer-repin`
- Existing PR: N/A (verified: zero open PRs at order time)
- Starting remote SHA: `e860e0bff687afded7782fb2687b5b435792459a`

## Strategic context and independently verified current state

Verified by strategic against live GitHub (2026-09-17), not inherited:

1. `ulfe-lmi/slaif-local-coding` main = `e860e0bff687afded7782fb2687b5b435792459a`
   (merge of PR #13 / Objective 011). Zero open PRs. Zero tags. Zero GitHub
   releases. Post-merge CI green (run 35178140841).
2. `ulfe-lmi/slaif-api-gateway` main moved from the local pin
   `65666f5886832034c52211fdd7604046557e6ada` to
   `1fccaa746df6cd44f1ddf8c2ec5cf6ea9f18b1cb` via merged gateway PR #302
   ("obj165: establish defensible readiness authority model", merged
   2026-09-17T00:44:18Z, head `78a5fc3a0f2eafdf9513d8fddcc42c192d86079c`).
3. The compare `65666f58...1fccaa746` (4 commits) touches exactly 12 files,
   all gateway-side: `README.md`, `docs/README.md`,
   `docs/beta-readiness.md`, `docs/rc-beta.md`, `docs/support-policy.md`,
   `docs/verification/README.md`, `oap/active`,
   `oap/orders/165-a-readiness-authority-model.md`,
   `oap/reports/165-a-readiness-authority-model.md`,
   `scripts/check_documentation.py`,
   `tests/unit/test_documentation_asof.py`.
4. The three gateway source files that the local contract gate
   (`scripts/gateway_contract.py`) validates at the pinned commit are
   **byte-identical** between the old pin and the new pin (GitHub blob
   SHAs, verified read-only by strategic):
   - `app/slaif_gateway/modules/servers/local_coding/contract.py`
     -> `9e8ae5ef8e1f9d8d48bf3627b9a767d86593a6ac`
   - `app/slaif_gateway/modules/clients/codex_0149.py`
     -> `8976c984c4430d65b3d36bad8565062a8c6f955a`
   - `app/slaif_gateway/providers/streaming.py`
     -> `73cc9f99e8c3cb2f3eb95173344bfbdc211c71ff`
   Therefore the re-pin is a contract no-op proven at blob level; the
   18-test strict gate re-proves compatibility mechanically at CI time
   against the new pin.
5. Residual post-011 current-facing drift found by strategic (to be fixed
   here):
   - `README.md` status-table row for Objective 011 still reads
     `this PR | (pre-merge)`; per the table convention it must carry
     `PR #13` and the merge commit `e860e0bff687afded7782fb2687b5b435792459a`
     (matching the 008/009/010 rows that carry their merge commits).
   - `docs/TOPOLOGY.md` line ~164 (future multi-host bullet) still carries
     the stale Objective-010 phrasing "the Local loopback-only binding law
     is preserved by this objective" although Objective 011 (D1) lawfully
     changed the binding law: loopback default; non-loopback legal only
     under the full `service_bearer_signed_identity_v1` contract.
   - Current-facing "pinned peer" statements in `docs/TOPOLOGY.md`
     (~line 56), `docs/SLAIF-GATEWAY-INTEGRATION.md` (~line 78 and the
     ~line-141 historical-section parenthetical that makes a current
     claim) still name `65666f58...` as the current peer.
6. Release-candidate artifacts remain those accepted in Objective 011:
   wheel `7cede0b8e930463400a40662248a97aae22f75b0512dcd8151d6122a99157166`
   (83070 B), sdist
   `4ba17680c55c557494593087f4d632abb6a79f0c595ecab08bb2414abc86f5d6`
   (424608 B, developer-only). This objective must keep those bytes
   identical.

## Bounded scope

Exactly six workstreams:

- **S1 — Pin update (fixture only).**
  `tests/fixtures/gateway/current_peer_authority.json`: change the `commit`
  field to `1fccaa746df6cd44f1ddf8c2ec5cf6ea9f18b1cb`. Schema
  (`slaif-local-gateway-peer-authority-v1`, version 1), `repository`,
  `server` (`local-coding-v1` v2,
  `process_local_inclusive_horizon_fail_closed`), `client`
  (`codex-0.149-responses-v1` v4), and `purpose` are UNCHANGED. No fixture
  schema extension. No change to `scripts/gateway_contract.py` gate logic
  (it is the accepted 007/010/011 gate).
- **S2 — Mechanical contract-identity evidence.** At round time,
  independently re-verify (via GitHub read-only) the blob SHAs of the three
  contract source files listed in item 4 at BOTH the old and the new pin,
  and record the full old/new table in the report. The values must match
  the strategic values in item 4; any mismatch is a stop-and-report
  condition (do NOT pin in that case; report the divergence). Then run the
  strict gate locally against the new pin (see Verification) and prove
  18/18 with the network guard active.
- **S3 — Release provenance regeneration.**
  `packaging/release_provenance_manifest.json` regenerated with
  `scripts/release_provenance_manifest.py` from the final implementation
  state: `objective` -> `012-a`; `gateway_peer.commit` and the
  `slaif-local-coding.gateway.peer.sha` OCI label -> new pin;
  `generated_from.git_commit` -> the generating commit. The `artifacts`
  section MUST remain byte-identical (wheel
  `7cede0b8...`, sdist `4ba17680...` — prove by rebuild + hash), and all
  status fields remain `cutover_performed: false`, `released: false`,
  `oci.published: false`, `oci.image_digest: null`. Update
  `tests/test_release_provenance_manifest.py` expectations only where they
  bind the peer commit/objective (keep every other assertion, including all
  artifact-hash cross-checks).
- **S4 — Dockerfile and cutover state machine.**
  `Dockerfile` `ARG SLAIF_GATEWAY_PEER_SHA` -> new pin (label input only).
  `scripts/cutover_state_machine.py` `canonical_snapshot` default
  `authority_sha` -> new pin; `tests/test_cutover_state_machine.py`
  updated accordingly. State-machine semantics, transition table, rollback
  table, and `binding_class` handling are otherwise UNCHANGED; the
  built-in self-test must pass.
- **S5 — Current-facing documentation reconciliation.**
  - `README.md`: fix the Objective-011 status-table row to
    `PR #13 | e860e0bff687afded7782fb2687b5b435792459a` with the existing
    status prose kept truthful (Docker-qualified, LAN-visible, MVP release
    candidate; deployment-qualified disposable/CI only; cutover NOT
    performed; NOT released). No other README changes.
  - `docs/TOPOLOGY.md`: (a) the "Gateway peer authority" statement -> new
    pin, explicitly recorded as re-pinned by Objective 012 with the
    contract-surface byte-identity fact and the gateway PR #302 / obj165
    provenance (docs/OAP/doc-check work only); (b) the pinned-source
    inspection record (~line 96) keeps `65666f58...` as the historical
    010-era inspection commit and gains a truthful note that Objective 012
    re-verified the identical contract surface at the new pin; (c) the
    future multi-host bullet (~line 164) rephrased to the truthful current
    D1 binding law (loopback default; non-loopback only under the full
    signed contract; further changes only by human architecture decision)
    — the stale "loopback-only binding law is preserved by this
    objective" phrasing must not survive.
  - `docs/SLAIF-GATEWAY-INTEGRATION.md`: the "Current continuous-test
    peer" statement -> new pin with Objective-012 re-pin provenance; the
    Objective-007 pin remains recorded as the 007-era pin (history); the
    Objective-006 handoff section keeps its historical pins
    (`5ea38325...`, and its 007-era parenthetical) but any sentence making
    a CURRENT-PEER claim inside it must be made truthful or pointed at the
    current-statement location. No other content changes.
  - Exhaustive literal-pin audit: grep every occurrence of
    `65666f58` across all non-`oap/` repository files at the final head;
    the report must contain a table dispositioning each occurrence as
    UPDATED (current-facing) or HISTORICAL (dated/historical context, left
    intact). `oap/orders/` and `oap/reports/` are immutable and must be
    byte-identical to base in the diff.
  - Audit all other current-facing docs (`docs/DEPLOYMENT.md`,
    `docs/DOCKER-INSTALL.md`, `docs/DOCKER-SECURITY-DELTA.md`,
    `docs/RELEASE-CUTOVER-RUNBOOK.md`,
    `docs/RELEASE-ARTIFACT-POLICY.md`, `docs/ADAPTER-CONFIGURATION.md`,
    `docs/IMPLEMENTATION-ROADMAP.md`, `oap/COMPLETENESS.md`) for
    current-peer claims; update only genuine current-facing claims (with
    012 provenance); never rewrite dated historical statements.
- **S6 — Topology manifest.** `docs/topology.manifest.json` stays schema
  `slaif-topology-manifest-v2`: the dated `live_facts_as_of_2026_09_14`
  section (including its `gateway_peer_commit` value) is an as-of snapshot
  and remains byte-identical; the mechanically checked sections
  (`transport_decision`, `invalid_assumption`, `lan_visible_variant`,
  `supported_path`) are unchanged; no new fields, no schema bump. The
  current pin is recorded in the fixture, the release manifest,
  `Dockerfile` ARG, state machine, and the TOPOLOGY.md current statement —
  not in the topology manifest.

## Explicit non-goals

- No wheel/sdist content change (bytes must remain exactly
  `7cede0b8...` / `4ba17680...`); NO `src/` change at all.
- No dependency change: `uv.lock` (SHA-256
  `1237cbd179f71b99984c80f927529549f5e61eb705585ef9cf2ab0fa9e26764a`) and
  `pyproject.toml` (SHA-256
  `af91f82283882f1e51ee763d635f94f1ae2534c51585c837aa61cff8a2f7dda2`)
  byte-identical to base.
- No version bump (stays `0.1.0`). No release, tag, registry publication,
  image push, or release-state change. No cutover. No live Gateway route
  change.
- No protected-host mutation: 18020/Qwen/vLLM, `qwen-serving` systemd
  state, model/checkpoint/venv, API keys, firewall/VPN/network bindings,
  active Codex profiles, `Linger` — all untouched. Read-only status probes
  only (see Protected-host constraints).
- No mutation of `ulfe-lmi/slaif-api-gateway` (read-only GitHub queries
  only). No OAP history rewrite: every `oap/orders/*.md` and
  `oap/reports/*.md` file byte-identical to base. No OAP framework
  expansion. No protocol/refactor work. No fixture schema change. No
  changes to `scripts/gateway_contract.py`. No new deployment platform.

## Concrete requirements and observable acceptance criteria

- **C1 — Pin updated, gate green at new pin.**
  `tests/fixtures/gateway/current_peer_authority.json` carries exactly the
  new commit with all other fields unchanged;
  `python scripts/gateway_contract.py --emit-github-output` emits
  `gateway_repository=ulfe-lmi/slaif-api-gateway` and
  `gateway_commit=1fccaa746df6cd44f1ddf8c2ec5cf6ea9f18b1cb`; the local
  strict gate against a clean checkout of the new pin passes 18/18 with
  zero skipped/failed/errors and the network guard active (no external
  egress).
- **C2 — Contract-surface identity proven.** Report contains the full
  blob-SHA table (3 files x old pin + new pin) independently re-verified by
  coding; all six pairs equal the strategic values in item 4 (the three
  old-pin and three new-pin SHAs must match respectively).
- **C3 — Release provenance regenerated, artifacts invariant.**
  `packaging/release_provenance_manifest.json` regenerated at the final
  implementation state: `objective: "012-a"`, `gateway_peer.commit` = new
  pin, `slaif-local-coding.gateway.peer.sha` label = new pin,
  `generated_from.git_commit` = the generating commit; `artifacts` section
  byte-identical to base (wheel `7cede0b8...` / sdist `4ba17680...`)
  proven by a clean rebuild + `sha256sum`; status fields
  `cutover_performed/released/oci.published = false`, `oci.image_digest =
  null`; `tests/test_release_provenance_manifest.py` green.
- **C4 — Dockerfile + state machine.** `Dockerfile` ARG = new pin;
  `canonical_snapshot` default `authority_sha` = new pin;
  `tests/test_cutover_state_machine.py` green; `cutover_state_machine`
  self-test green; no state-machine semantics change (diff review shows
  constant updates only).
- **C5 — Topology manifest untouched.**
  `docs/topology.manifest.json` byte-identical to base (per S6);
  `tests/test_topology_qualification.py` and the qualification self-test
  green.
- **C6 — Documentation truthfulness.** README 011 row fixed per S5;
  TOPOLOGY.md (a)/(b)/(c) done; SLAIF-GATEWAY-INTEGRATION.md done; the
  literal-pin audit table in the report covers every non-`oap/` occurrence
  of `65666f58` at the final head with UPDATED/HISTORICAL disposition;
  `oap/orders` + `oap/reports` byte-identical to base; no
  "this PR"/"open"/"pre-merge" language remains in any current-facing
  doc; historical pins (`5ea38325...`, `65666f58...` in dated 006/007
  context) preserved in historical context only.
- **C7 — CI green at the report head AND at the implementation head.**
  `test` (full suite), `gateway-contract` (checking out the NEW pin and
  passing the 18-test strict gate), `docker` (wheel-binding to the
  regenerated manifest, label check against the new pin, image content
  scan, hardening, operations, teardown) — all `success`, no failed,
  cancelled, pending, or missing required checks.
- **C8 — Protected host before/after identical.** Read-only probes before
  and after (service unit active state + MainPID + since-time;
  `127.0.0.1:18020/health` = 200; ports 18021/18031-18034 absent;
  `~/.codex/qwen-neumann.config.toml` mtime/mode; `Linger`;
  `docker ps -a` for slaif-named containers/images) identical on every
  item; values recorded in the report.
- **C9 — No publication/mutation.** At report time: zero new tags, zero
  GitHub releases, no image pushed anywhere, `slaif-api-gateway` unmodified
  (verified read-only: main still `1fccaa746...` at report time or, if it
  moved, recorded as a factual note without chasing it), no live
  profile/route/service change.
- **C10 — Freeze held.** `uv.lock` + `pyproject.toml` SHA-256 equal to the
  base values above; zero `src/` files in the diff; all changed files are
  within the S1-S6 scope list.

## Verification and evidence (exact)

Local (protected host, repo venv via `uv`, locked/frozen):
1. `git status` clean start from base `e860e0bff687afded7782fb2687b5b435792459a`
   on a fresh branch `oap/012-gateway-peer-repin`.
2. GitHub read-only blob-SHA re-verification for C2 (record command +
   outputs in the report).
3. Clean checkout of the gateway at the new pin (throwaway path, removed
   after) + `SLAIF_GATEWAY_ROOT=<checkout> uv run --frozen python
   scripts/gateway_contract.py --gateway-root <checkout> --run-tests`
   (C1: 18/18, guard active).
4. `uv build --out-dir dist` + `sha256sum` of wheel/sdist vs C3 hashes.
5. `uv run --frozen pytest -q` (full suite; the standing
   environment-conditional skips only).
6. `uv run --frozen ruff check .` + `uv run --frozen ruff format --check .`
   + `uv run --frozen mypy src tests`.
7. `uv run --frozen python -m compileall -q src tests oap/bin scripts`.
8. `python scripts/cutover_state_machine.py` self-test (or its documented
   entry) + `python scripts/topology_qualification.py` self-test.
9. `uv run --frozen python scripts/artifact_policy_check.py --dist dist
   --inspect` (unchanged policy outcome).
10. Literal-pin audit: `git grep -n 65666f58` at the final head excluding
    `oap/` (plus a separate `git grep` proving `oap/` untouched vs base).

GitHub (after push, before report):
- Exactly one PR for objective 012, branch `oap/012-gateway-peer-repin`,
  base `main` @ `e860e0bff687afded7782fb2687b5b435792459a`, non-draft.
- Inspect and, if red for an in-scope defect, repair the required checks
  (`test`, `gateway-contract` against the NEW pin, `docker`) until green;
  never weaken an assertion to get green; never merge.
- Verify C9 facts against GitHub at report time.

## Documentation and compatibility contracts

- The re-pin keeps the accepted `service_bearer_signed_identity_v1`
  contract and the 010/011 topology/binding laws intact; module versions
  are unchanged (`local-coding-v1` v2, `codex-0.149-responses-v1` v4).
- Every current-facing "current peer" statement must state the new pin AND
  the re-pin provenance (objective 012, date 2026-09-17, contract surface
  byte-identical). Historical statements keep historical pins.
- Release honesty ladder unchanged: deployment-qualified
  (disposable/CI only) — not release-qualified — not released; cutover not
  performed.

## Security/privacy/secrets/resource/protected-host constraints

- Protected host is READ-ONLY: status probes only (systemctl status of
  `qwen-serving-vision.service`, `127.0.0.1:18020/health` HTTP status,
  port presence checks for 18021/18031-18034, Codex profile file
  mtime/mode, `docker ps -a`/`docker images` listings). NO service
  mutation, NO port 18020 mutation, NO model/venv/patch change, NO
  firewall/VPN/network change, NO Codex profile mutation, NO `Linger`
  change, NO new persistent units.
- No secrets, host paths, sentinels, prompts, model outputs, or acceptance
  payloads in the diff, the PR body, or the report (the report may carry
  SHAs, blob IDs, ports, and the standard protected-host status values only).
- Network guard: the strict gate runs with its guard active; the
  throwaway gateway checkout is local and removed afterwards. No
  protected-model inference; no Qwen call of any kind.
- Resources: bounded; no long-lived processes left running; no leftover
  checkouts/containers.

## Local authority

Coding may use existing repository tooling and safe routine setup it
already has (uv, Docker for the docker CI repair path if needed locally,
`gh`/git). No human operator action is required. If the C2 blob-SHA
re-verification disagrees with item 4, STOP the pin change and report the
divergence (that would be a genuine strategic re-adjudication, not an
in-scope defect).

## GitHub publication requirements

- Push all implementation commits to `oap/012-gateway-peer-repin` before
  the report.
- Create exactly ONE PR (title: "Re-pin current Gateway peer and close
  post-011 documentation drift (Objective 012)"); base `main`; non-draft;
  description: objective ID, the re-pin provenance, changed-surface
  summary, CI state, non-goals.
- After CI is green and C9 verified: publish the immutable report
  `oap/reports/012-a-gateway-peer-repin.md` as a report-only commit
  (SELF) whose parent is the literal implementation head SHA; push it.
- NEVER merge. NEVER enable auto-merge.

## Exact immutable report contract

`oap/reports/012-a-gateway-peer-repin.md` must contain, at minimum:

- Work order: identifier `012-a`, order path, numeric objective `012`,
  PR mode `CREATED_NEW_PR`.
- Status: COMPLETE (or the honest alternative with the blocking fact).
- Authoritative GitHub state: repository, PR number/URL/state, base,
  branch, starting remote SHA, implementation head SHA (literal 40-hex),
  report publication commit = SELF, full pushed commit list, "Merge
  performed: NO".
- Changes and files: every changed file mapped to S1-S6 with the
  diff-summary counts.
- C1-C10 evidence, each with the exact commands/outputs or CI job
  references; the C2 blob-SHA table (old vs new, 3 files); the C6
  literal-pin audit table; the C8 protected-host before/after table; the
  C9 no-publication verification; the C10 freeze proof (uv.lock/pyproject
  SHA-256, zero `src/` files, `oap/` untouched).
- GitHub CI: implementation-head and report-head run IDs with per-job
  conclusions; every prior branch run and its repair.
- Live model/service evidence: none (explicit: no Qwen/vLLM call).
- Safety/scope confirmations: per the report convention (unrelated files,
  secrets, protected fixture, skipped tests, scope deviations).
- Known limitations/blockers: honest, including the factual note of the
  gateway `main` state at report time.


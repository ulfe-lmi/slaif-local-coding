# OAP Coding-Agent Report — 013-a

## Work order
- Identifier: `013-a`; order path: `oap/orders/013-a-mvp-release-publication.md`; numeric objective `013`
- PR mode: CREATED_NEW_PR (this round created the one and only objective PR)
- Round state: wrapper-consumed control `OK` at start; this is the final report of the round

## Status
**BLOCKED** (publication workstream, per R18 Gateway-peer drift); implementation
workstreams A–F are **COMPLETE** at the implementation head with all four CI
jobs green. No registry publication, release record, or workflow dispatch was
performed, by the order's own R18 rule.

Per workstream:
- **A** (release record + provenance v3): implementation **COMPLETE** at S
  (schema v3, state-aware generator, state-conditional gates, cross-consistency
  tests all green); the record itself is **BLOCKED** — it exists only in `P`,
  which was never created.
- **B** (Dockerfile label parameterization): **COMPLETE** (one documented
  deviation; effective default byte-identical; CI-verified).
- **C** (compose split + qualification update): **COMPLETE** (CI-verified).
- **D** (release workflow activation): implementation **COMPLETE**;
  execution **BLOCKED** (R18; not triggered).
- **E** (CI published-image gate): implementation **COMPLETE** (correct
  explicit skip at S); execution at `P` **NOT RUN** (no `P`).
- **F** (documentation reconciliation): **COMPLETE** at the pending-publication
  truth (publication claims are intentionally absent because publication did
  not occur; see deviations 3–4).

## Executive summary
All six implementation workstreams of order 013-a are complete, committed, and
CI-verified at implementation head
`S = 0096886aad1be25770f817dcdeaab779260f903e`: pull-based canonical
`compose.yaml` (no `build:`), new `compose.build.yaml` qualification override,
two-file qualification harness (all 15 phases PASSED in CI), activated
`workflow_dispatch`-only release workflow (not executed), `docker-published`
CI gate (explicit skip at S), schema-v3 provenance manifest with
state-aware generator and drift gates, and documentation reconciled to the
truthful pending-publication state. The round started with the R18
precondition PASS (gateway `main` == pinned peer). Mid-round the remote
gateway `main` moved twice, off the pinned peer; per R18 ("If it differs: DO
NOT publish; stop, publish a BLOCKED report with the exact delta"), no
release-workflow dispatch was made, no release record was written, and no
digest `D` was captured. The exact delta is recorded below for strategic
inspection and deliberate re-qualification. One in-scope CI failure
(`qualification_label` at a superseded head) was root-caused in the buildkit
parser and fixed (commit C4) with the effective ARG default remaining
byte-identical to the pre-013 hardcoded label.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding` (public)
- PR: **#15** — https://github.com/ulfe-lmi/slaif-local-coding/pull/15 — state `OPEN`, non-draft, `MERGEABLE`
- Base: `main` @ `a04693e6792df6a8ad4262acfb46336a0f662202` (order base, unchanged this round)
- Branch: `oap/013-mvp-release-publication`
- Starting remote SHA (branch created from `origin/main`): `a04693e6792df6a8ad4262acfb46336a0f662202`
- **Implementation head SHA: 0096886aad1be25770f817dcdeaab779260f903e**
- **Report publication commit: SELF** (first parent = the literal implementation SHA above; `P` does not exist, so `S` is the final non-report commit of the round)
- Implementation commits pushed before this report (base → S, single-parent chain):
  1. `8ce9b18d2d42cd388b6fb8faafa3bf80529af082` — workstreams A–F + transcript (C1)
  2. `e02124e0e45a676121381bde5742ee0bbcb199a2` — adds missing `compose.build.yaml` (C1b)
  3. `039c14bbef98929a3b2fcd177f76a531fade0284` — manifest (superseded)
  4. `95ce9b442c917c8b8599770d8e18dfa34d1a0148` — harness `str`/`str` path-join fix (C2)
  5. `f88c31ff3043125f0ff8c48aa2a12862a3ef1662` — manifest (superseded)
  6. `79592ee8d6243e878540c2c26dc5bb61d77c8f54` — R8 merge-equivalence fixture render-location fix (C3)
  7. `8a0aa2cdeba6687d623d7778695efda1fe6b339a` — manifest (superseded)
  8. `817d9b0ce368fbe35582aaf06e11b943307f306b` — qualification-label ARG quoting fix + label detail in failure output (C4)
  9. `0096886aad1be25770f817dcdeaab779260f903e` — manifest `M_S` at final state (S)
- New PR this round: **yes** (exactly one; #15). Amended existing: no. Merge performed: **NO**. Auto-merge: **NO**.

## Changes and files
- `Dockerfile` — exactly one new build ARG
  `SLAIF_QUALIFICATION_LABEL` (quoted default; see deviation 1) and the LABEL
  line parameterized to `slaif-local-coding.qualification="${SLAIF_QUALIFICATION_LABEL}"`;
  all other lines byte-identical.
- `compose.yaml` — pull-based canonical file: no `build:` key; image default
  `${SLAIF_LOCAL_CODING_IMAGE:-ghcr.io/ulfe-lmi/slaif-local-coding:0.1.0}`;
  Objective-011 hardening preserved exactly (verified by R8 merge-equivalence
  against the pre-013 effective spec).
- `compose.build.yaml` — new qualification override (local image
  `slaif-local-coding:0.1.0-${SLAIF_GIT_SHA:-local}` + `build:` with
  `SLAIF_GIT_SHA`/`SLAIF_WHEEL_SHA256` args; does NOT set the qualification ARG).
- `scripts/docker_qualification_ci.py` — two-file compose for all phases;
  `--published` mode (digest/tag pulls, label checks, pull-based contract run,
  no-build proof, teardown absence proof); rendered content-scan covers both
  compose files; C4 adds the full non-secret label set to the
  `hardening_and_labels` failure detail.
- `.github/workflows/release-image.yml` — activated publication path
  (`workflow_dispatch` only; `GITHUB_TOKEN` only; wheel-binding assert;
  two-file build with `SLAIF_QUALIFICATION_LABEL=mvp-release-0.1.0`; GHCR
  login; unconditional `sha-<S>` push; `0.1.0` push only when the tag is
  absent or already at this digest; registry digest verification emitting `D`).
- `.github/workflows/ci.yml` — new `docker-published` job, gated on
  `packaging/release_record.json` existence (explicit skip line otherwise).
- `packaging/release_provenance_manifest.schema.json` — `slaif-release-provenance-v3`
  (optional closed `release` object; state-aware enums; `additionalProperties: false`).
- `scripts/release_provenance_manifest.py` — state-aware generator (objective
  `013-a` in both states; not-yet-published state at S).
- `packaging/release_provenance_manifest.json` — `M_S`: 12 top-level keys,
  `generated_from.git_commit = 817d9b0ce368fbe35582aaf06e11b943307f306b` (= S's
  parent), `status.released=false`, `oci.published=false`,
  `oci.image_digest=null`, no `release` key; wheel
  `fceadc378130dd4ffcc3f75d17b5e098577652914f541245d31247911be23aeb` (83,097 B);
  sdist `28f391e14fc26f47241487a4656bb8366941f7f5a749d8cbe056741f6d5e942f`;
  5,630 bytes.
- `tests/test_release_provenance_manifest.py`, `tests/test_compose_pull_canonical.py`
  — state-conditional E3 gate, new cross-consistency tests (record/commit
  binding, build-input blob equality at S vs HEAD, digest/tag/label/wheel
  bindings, tamper negatives, objective assertion), static pull-canonical
  compose gates.
- Workstream F docs: `docs/DOCKER-INSTALL.md` (pull-based primary operator
  path; build path labeled qualification/development-only; no
  Python/uv/venv requirement stated explicitly), plus current-state
  corrections in `README.md` (frozen — deviation 2), `docs/IMPLEMENTATION-ROADMAP.md`,
  `oap/COMPLETENESS.md`, `docs/DEPLOYMENT.md`, `docs/TOPOLOGY.md`,
  `docs/RELEASE-CUTOVER-RUNBOOK.md`, `docs/RELEASE-ARTIFACT-POLICY.md`,
  `ARCHITECTURE.md`, `docs/DOCKER-SECURITY-DELTA.md`. Historical OAP
  orders/reports and 009–012 records byte-identical.
- Transcript: activated order file + `oap/active` (`013-a\n`, 6 bytes) committed
  unchanged at C1 and untouched since (verified: no commit after C1 touches
  either path).

## Acceptance evidence
### R1 (release record + v3 schema) — PARTIAL
Schema `slaif-release-record-v1` semantics, closed key set, and generator
support implemented and unit-tested; the record file is correctly ABSENT from
S's tree (state-conditional gates assert this in the not-yet-published state).
The record itself (fields `schema`, `version=0.1.0`, `git_tag=v0.1.0`,
`image_source_commit=S`, `oci_image_reference=ghcr.io/ulfe-lmi/slaif-local-coding`,
`oci_image_digest=sha256:<D>`, `oci_tags=["0.1.0","sha-<S>"]`, `published_at`,
`publication_workflow=release-image.yml`,
`publication_workflow_run_id`) exists only in `P` — **BLOCKED** (R18; no
publication, no `D`, no workflow run id).
### R2 (schema v3) — PASSED
`slaif-release-provenance-v3`, `$id` + `schema_version: 3`, closed top-level
key set with optional `release`, `status.released`/`oci.published` state
enums, `oci.image_digest` null-or-digest, closed `release` key set,
`additionalProperties: false` throughout; verified by the green manifest test
module at S (18/18).
### R3 (state-aware generator) — PASSED
Generator emits the not-yet-published state at S (null/false/false, same
qualification label, reserved-reference `oci.tag_convention`, objective
`013-a`) and the published-state branch (record load, `release` object with
`git_tag_target := image_source_commit`, `mvp-release-0.1.0` label, truthful
published-state `limitations`/`tag_convention`) is implemented and
state-conditionally tested; all manifest tests green at S.
### R4 (state-conditional E3 + cross-consistency) — PASSED (at S)
Regeneration/drift gate (strip `generated_from.git_commit`, ancestor rule) is
state-conditional and green at S; new cross-consistency tests (a)–(f)
(commit/record/HEAD binding, build-input blob equality, digest/tag/label/wheel
bindings, three tamper negatives, objective assertion, state-conditional
status const) all pass at S; the published-state variants will execute at `P`
(**NOT RUN** — no `P`).
### R5 (byte-identity law) — PASSED
No branch commit touches `src/`, `pyproject.toml`, or `uv.lock` (verified by
diff inspection of the base→S chain). Fresh `uv build` wheel SHA-256 =
`fceadc378130dd4ffcc3f75d17b5e098577652914f541245d31247911be23aeb` locally and
in CI (`verify_wheel_binding` PASSED at S); in-image wheel provenance proof
PASSED at S (`in_image_provenance`).
### R6 (Dockerfile label parameterization) — PASSED (deviation 1 on the literal line)
Exactly one new build ARG and the parameterized LABEL line; no other Dockerfile
line changed. The unquoted literal default from the order is unparseable to
the intended value (buildkit tokenizes it at whitespace — see deviation 1), so
the default is quoted; the shlex-resolved effective default is byte-identical
to the pre-013 hardcoded label `disposable-qualification-only; not released`.
CI proof at S: `hardening_and_labels` `qualification_label: true` (docker
28.0.4 / compose 2.38.2). `compose.build.yaml` does not set the ARG; the
release workflow sets it to `mvp-release-0.1.0`.
### R7 (pull-based canonical compose.yaml) — PASSED
No `build:` key; image default
`${SLAIF_LOCAL_CODING_IMAGE:-ghcr.io/ulfe-lmi/slaif-local-coding:0.1.0}`;
Objective-011 hardening preserved exactly — proven mechanically by
`compose_merge_equivalence` (merged two-file spec == pre-013 single-file
effective spec over the closed field set) PASSED at S, and by the static gates
in `tests/test_compose_pull_canonical.py`.
### R8 (compose.build.yaml + mechanical merge test) — PASSED
Override created; `compose_merge_equivalence` phase PASSED at S
(`merged_equals_pre013: true`).
### R9 (two-file harness, all phases) — PASSED
All 15 phases PASSED at S in CI `docker` (see CI section); rendered-compose
content-policy scan covers BOTH files (`compose_rendered_validation` PASSED);
fail-closed phase unchanged and PASSED (`fail_closed_readiness`).
### R10 (static pull-canonical gate) — PASSED
`compose.yaml` has no `build:` key; default pull reference equals manifest
`oci.image_reference` + `:0.1.0`; `SLAIF_LOCAL_CODING_IMAGE` override renders
verbatim including digest-pinned `…@sha256:<64-hex>` forms — static stdlib
tests green at S.
### R11 (release workflow activation) — PASSED (implementation); execution NOT RUN
Workflow is `workflow_dispatch`-only with `GITHUB_TOKEN` only (no repository
secrets), wheel-binding assert, two-file build with `SLAIF_GIT_SHA`/
`SLAIF_WHEEL_SHA256`/`SLAIF_QUALIFICATION_LABEL=mvp-release-0.1.0`, GHCR
login, unconditional `sha-<S>` push, `0.1.0` guarded against pre-existing
different digests, registry-verified single digest emission. **Not
executed**: R18 hold (see R12/R18).
### R12 (trigger workflow at S, capture D) — BLOCKED
Not triggered. The coding credential has `repo`+`workflow` scopes (dispatch
would have been possible); the blocker is the R18 peer drift, which the order
makes absolute ("DO NOT publish"). No workflow run id, no `D`.
### R13 (CI `docker-published` gate) — PARTIAL
Job implemented and gated; at S it skipped with the explicit line
`not yet published (packaging/release_record.json absent) — docker-published
skipped` (run 35203279259, job 105142891026). Execution with digest/tag
pulls, label checks, pull-based contract run, no-build proof, and teardown
absence proof is **NOT RUN** (requires `P` + a published image; R18 hold).
### R14 (all existing gates green at final head) — PASSED
At S: `test` PASSED, `gateway-contract` PASSED (pinned peer
`1fccaa746df6cd44f1ddf8c2ec5cf6ea9f18b1cb`), `docker` PASSED (complete 011/012
qualification, all 15 phases; no assertion removed, skipped, or weakened).
### R15 (DOCKER-INSTALL pull-based primary path) — PARTIAL (hold-conformant)
Restructure fully implemented: pull-based primary operator path (compose
file set, three-placeholder signed template with three distinct 0600 secret
roles, `docker compose pull` / `up -d`, readiness/health verification,
stop/restart/status, upgrade/rollback by tag-or-digest pin + recreate, cache
purge, uninstall incl. pulled-image removal, digest-pinning as
exact-reproduction option; explicit no-Python/uv/venv statement);
build-from-source path documented and labeled qualification/development-only,
NOT the released-user path. The "published at `D`" final wording is
intentionally absent (publication did not occur — deviation 4); it belongs to
the round that actually publishes.
### R16 (doc reconciliation) — PARTIAL (hold-conformant)
All identified current-facing documents reconciled to the exact current
truth: publication PENDING (no digest/tag/Release claims), cutover NOT
performed, no real deployment evidenced, deployment-qualified
(disposable/CI only), D1 binding law / loopback default / systemd secondary
path unchanged; stale "NOT released / build locally primary / inert
workflow" current-state statements removed or corrected to the pull-based +
two-file truth. A document must not claim the `v0.1.0` tag or GitHub Release
objects exist — none do (verified: zero Git tags, zero GitHub releases on the
repository at report time).
### R17 (no document above manifest status) — PASSED (hold-conformant)
Manifest `M_S` states not-yet-published; no current-facing document asserts a
status above it (mechanical spot-check by review, per the order).
### R18 (Gateway peer re-verification) — PASSED at round start; drift detected mid-round → publication BLOCKED
At round start, remote gateway `main` == pinned peer
`1fccaa746df6cd44f1ddf8c2ec5cf6ea9f18b1cb` ("Merge pull request #302 from
ulfe-lmi/oap/165-readiness-authority-model", 2026-09-17T00:44:17Z): PASS,
proceeded. Mid-round `main` moved; at report time the exact delta
(compare `1fccaa74……08ca421…`, pin is ancestor, main 8 commits ahead, 0 behind):
- `87c1393d1496590dac8f3e9d861734d5a41b62e4` — "obj166: qualify OpenAI Python SDK 3.9.0 official-client compatibility" (2026-09-17T07:01:05Z)
- `fd0f5f516179726f0e9960dc2d9e62260fcec5e5` — "oap: activate 166-a openai sdk3 compatibility qualification" (2026-09-17T07:01:11Z)
- `61d9c56662dd40b1134d0abeb0298f3dd28a3f6e` — "OAP 166-a: publish final immutable report" (2026-09-17T07:07:49Z)
- `9bb81cb960b6d3ba5373425cbe50cdcc670b93dc` — "Merge pull request #303 from ulfe-lmi/oap/166-openai-sdk3-compatibility-qualification" (2026-09-17T07:15:34Z)
- `026ea7e59f41ceef35bcfa0c40c21605c605398b` — "obj167: fresh integrated qualification of current main for RC posture" (2026-09-17T08:11:38Z)
- `41fcb5d5b9ae02e1dd9654a75d7dac85d56dcf28` — "oap: activate 167-a current main integrated qualification" (2026-09-17T08:11:38Z)
- `4b56deee787732fcfb813de416e2fd2c2a2282c6` — "OAP 167-a: publish final immutable report" (2026-09-17T08:17:04Z)
- `08ca421bee1ddca62078302b910e8be88cf705be` — "Merge pull request #304 from ulfe-lmi/oap/167-current-main-integrated-qualification" (2026-09-17T08:30:55Z)
Diff nature (facts for strategy re-qualification): 18 files changed; **zero**
under `modules/` or `src/` (contract surface unchanged); `pyproject.toml`
dev-dependency `openai==2.41.0` → `openai==3.9.0`; 10 `tests/e2e/` files; 4
`docs/` files; 5 `oap/` files. Per R18, publication stopped; strategy
inspects and deliberately re-qualifies.
### R19 (exact round sequence) — PARTIAL (stopped by R18 at the publish boundary)
Executed: implementation commits → `S` with `M_S` (no release record) → CI at
`S` fully green with `docker-published` explicit skip. Stopped: workflow
trigger at `S` (R18); therefore no `D`, no `P`, no CI at `P`. Report `R`
(this commit, parent `S`) pushed and verified as remote PR head.
### R20 (protected-host invariance) — PASSED
Before (2026-09-17, ~08:0x local, read-only) / after (2026-09-17T09:08:43Z,
read-only) probes — identical states:
- `systemctl --user`: `qwen-serving-vision.service` active/running;
  `qwen-serving.service` inactive/dead; `zap-it-lan.service`
  activating/auto-restart — unchanged before/after.
- Port 18020: `LISTEN 0.0.0.0:18020`, owner `vllm pid=23961` — unchanged.
- Ports 18031/18033/18034: closed before and after.
- `docker ps -a`: only three pre-existing non-slaif exited containers
  (`beautiful_cartwright`, `beautiful_haibt` — `chrockey/fpt-votenet:v0.1.0`,
  Exited 2 years ago; `kind_brown` — `hello-world`, Exited 2 years ago); no
  new/changed slaif containers.
- NO docker build/run/up/recreate occurred on the host this objective (only
  read-only `docker ps`-class inspection and daemonless `docker compose
  config` renders with temporary 0-byte `SLAIF_CONFIG_FILE`/`SLAIF_ENV_FILE`).

## Verification
- `uv run --frozen pytest -q` (at S tree): **PASSED** — 1098 passed, 26 skipped, 0 failed
- `uv run --frozen ruff check .`: **PASSED** — all checks passed
- `uv run --frozen ruff format --check .`: **PASSED** — 354 files already formatted
- `uv run --frozen mypy src tests`: **PASSED** — no issues in 71 source files
- `uv run --frozen python -m compileall -q src tests oap/bin scripts`: **PASSED**
- `uv build --out-dir $D` + `sha256sum`: **PASSED** — wheel
  `fceadc378130dd4ffcc3f75d17b5e098577652914f541245d31247911be23aeb` (83,097 B),
  byte-identical to the accepted 012 authority
- `uv run --frozen pytest -q tests/test_release_provenance_manifest.py`
  (E3 gate + cross-consistency, not-yet-published state): **PASSED** — 18/18
- `docker compose config --quiet` renders (pull file; two-file build
  combination), with temporary 0-byte env/config files: **PASSED** (render only;
  no host docker build/run/up)
- `bash -n` on changed shell: **PASSED**
- `python3 scripts/ghcr_tag_check.py --repo ulfe-lmi/slaif-local-coding --tag 0.1.0`: **PASSED** — `absent` (anonymous probe)
- `python3 scripts/ghcr_tag_check.py --repo ulfe-lmi/slaif-local-coding --tag sha-0096886aad1be25770f817dcdeaab779260f903e`: **PASSED** — `absent` (anonymous probe)
- `gh workflow run release-image.yml --ref <S>`: **BLOCKED** (R18 hold; not attempted)
- Protected-model live matrix (text/tool/SSE/vision/etc.): **NOT RUN** (explicit non-goal of this order: fake/synthetic upstreams only; no protected-model inference anywhere)
- Real Codex E2E: **NOT RUN** (not ordered this round)

## Live model/service evidence
No live model or adapter service was used: this order authorizes
fake/synthetic upstreams only (all CI Docker evidence runs against the
disposable fake upstream on the GitHub runner, canonical port 18031 inside
the runner). Protected-host read-only probes only (R20 above); the existing
vision service state is unchanged; no request was sent to port 18020.

## GitHub CI / required checks
- Superseded head `8a0aa2cdeba6687d623d7778695efda1fe6b339a`, run `35199868081`:
  `test` PASSED (1m19s); `gateway-contract` PASSED (12s); `docker-published`
  PASSED-as-skip (9s); `docker` **FAILED** — 12/15 phases PASSED,
  `hardening_and_labels` failed with `failed_checks: ["qualification_label"]`
  (built label lacked `not released`; root cause: unquoted ARG default
  tokenized at whitespace — deviation 1). Fixed in C4.
- **Implementation head `S = 0096886aad1be25770f817dcdeaab779260f903e`, run
  `35203279259`: all four jobs PASSED**
  - `test` PASSED (1m25s) — job 105142891062
  - `gateway-contract` PASSED (14s, pinned peer `1fccaa74…`) — job 105142890605
  - `docker-published` PASSED-as-skip (9s) with explicit line `not yet published (packaging/release_record.json absent) — docker-published skipped` — job 105142891026
  - `docker` PASSED (1m28s) — job 105142890980; all 15 phases PASSED:
    `verify_wheel_binding`, `compose_rendered_validation`,
    `compose_merge_equivalence`, `image_build`, `fake_upstream_start`,
    `adapter_stack_up`, `in_image_provenance`, `bridge_positive_signed`,
    `bridge_negative_contract`, `config_time_rejection`,
    `fail_closed_readiness`, `image_content_scan`,
    `operations_stop_start_recreate_upgrade_rollback`,
    `hardening_and_labels` (`qualification_label: true`),
    `teardown_absence_proof`; docker 28.0.4 / compose 2.38.2.
- All required green at drafting: **yes** (at S).
- CI at `P`: **NOT RUN** (no `P`). Report-head (this commit) checks may be
  pending; strategy verifies.

## Local setup/dependencies
- Repository-owned venv via `uv` (locked/frozen installs); no new dependencies;
  no changes to `pyproject.toml`/`uv.lock`.
- Passwordless sudo used only for the read-only `docker ps`-class R20 probe
  (established pattern). No terminal operator recruited.
- No durable docs/config changed beyond the order scope; `oap/runtime.env.example`
  local runtime edits remain uncommitted (intentionally, per round convention).

## Documentation
Updated as listed under Changes and files (workstream F, hold-conformant
wording — deviations 3–4). Historical OAP orders/reports and 009–012 records
untouched. PR #15 body updated at round end with the current R18 delta and
final implementation head.

## Safety/scope confirmations
- Unrelated/pre-existing work preserved; working tree contains only the
  intended modified paths plus pre-existing untracked junk left untouched
  (`Local`, `clean`, `unchanged` — not committed).
- No secrets, raw prompts, source, images, tool outputs, request/response
  bodies, or private URLs in the report, commits, CI logs, or artifacts;
  CI fake credentials follow the 011 pattern (generated, 0600, never printed).
- Protected 18020/Qwen/Codex fixture changed: **NO** (R20 invariance above).
- Gateway repository change: **NO** (read-only `gh api` inspection only).
- Dependency change: **NO**. Version: still `0.1.0`.
- Required tests skipped/not run: 26 routine skips in the local suite
  (Gateway-dependent modes without `SLAIF_GATEWAY_ROOT`, as designed);
  protected-model matrix and real-Codex E2E NOT RUN (not ordered).
- Extra objective PR: **NO** (exactly one PR, #15). Coding merge: **NO**.
- Active/order edited: **NO** (transcript bytes unchanged since C1; verified).
- Report commit report-only: **yes** (staged diff is exactly the one report
  path; verified before commit).

## Known limitations/blockers
1. **R18 peer drift (the blocker).** Remote gateway `main` is 8 commits ahead
   of the pinned peer (exact delta above). Per R18, publication (R12) is
   forbidden until strategy inspects and deliberately re-qualifies; no
   re-pin was performed by coding (order: "NO re-pin unless the peer delta
   check (R18) blocks" — it blocks, and the re-qualification decision is
   strategic).
2. **`D` not captured; no `P`.** Consequently the release record, the
   published-state manifest `M_P`, the `v0.1.0` tag (strategic post-merge
   act), the GitHub Release, and the `docker-published` execution at `P` are
   all outstanding. Registry verified clean (both candidate tags `absent`,
   anonymous), so a future publication has no orphan-tag cleanup.
3. Documentation carries the pending-publication truth (deviation 4); the
   final "published at `D`" wording lands in the round that publishes.

## Deviations (exact justification and status)
1. **R6 literal ARG line — quoted default.** The order's literal
   `ARG SLAIF_QUALIFICATION_LABEL=disposable-qualification-only; not released`
   cannot yield the required effective default under buildkit:
   `frontend/dockerfile/parser/line_parsers.go` (`parseNameOrNameVal` →
   `parseWords`) tokenizes the unquoted default at whitespace into three
   words, so `instructions/parse.go` (`parseArg`) assigns
   `SLAIF_QUALIFICATION_LABEL=disposable-qualification-only;` (truncated) and
   two bare ARG names `not` and `released` (legal, non-error). Observed in CI
   run 35199868081: `hardening_and_labels` failed `qualification_label`.
   The fix quotes the default
   (`ARG SLAIF_QUALIFICATION_LABEL="disposable-qualification-only; not released"`);
   `dockerfile2llb/convert.go` (`buildMetaArgs` → `shell.Lex
   .ProcessWordWithMatches`) then resolves the effective default to
   `disposable-qualification-only; not released` — byte-identical to the
   pre-013 hardcoded value (the pre-013 quoted LABEL with the same string
   parsed correctly in the 011/012 green CI). Verified at S: CI `docker`
   `qualification_label: true`. No other Dockerfile line changed. **Status:
   resolved in C4; semantic contract of R6 fully met.**
2. **README.md byte-frozen.** Workstream F lists README.md, but R5's
   byte-identity law prevails: the build backend embeds the README into the
   wheel METADATA; an unmodified-tree build reproduces
   `fceadc378130dd4ffcc3f75d17b5e098577652914f541245d31247911be23aeb` while a
   README-edit build produced a different hash (`ed215ab3…`), empirically
   proven in this round. Any README change would break the accepted wheel
   byte identity. Under the hold, the README's "NOT released" statements are
   in fact accurate. If publication proceeds in a later round, the README (and
   the wheel pin) need an explicit strategic decision there. **Status:
   intentional deviation, documented.**
3. **`D` cannot appear literally in S's docs/manifest.** By the order's R19
   ordering, the digest and release record exist only in `P`; `P` was never
   created (R18). Docs therefore point to `packaging/release_record.json` /
   the manifest as the authoritative publication record locations. **Status:
   consequence of the hold.**
4. **Docs state pending-publication truth, not "PUBLISHED at D".** R15/R16's
   target wording is post-publication truth; publication did not occur in this
   round, so the exact current truth is PENDING, and no document may assert a
   status above the manifest (R17). The pull-based structural requirements of
   R15 are fully implemented; the final published wording (digest, tags, tag
   semantics) belongs to the round that actually publishes, since `P` by
   definition cannot touch docs. **Status: consequence of the hold.**
5. **CI-driven harness fixes C1b/C2/C3/C4.** Each fixed a concrete failing CI
   phase at a superseded head without weakening any gate: C1b added the
   omitted `compose.build.yaml`; C2 fixed `str`/`str` path joins in harness
   constants (import failure); C3 fixed the R8 merge-equivalence fixture
   render location (pre-013 fixture now rendered from a temporary repo-root
   copy, removed in `finally`); C4 is deviation 1. All 011/012 qualification
   assertions unchanged and green at S. **Status: resolved.**
6. **R12 dispatch not attempted.** The credential could trigger
   `workflow_dispatch` (`repo`+`workflow` scopes verified present); the
   blocker is R18, not the credential, so no attempt was made. **Status:
   BLOCKED (R18).**

## Recommended strategic follow-up
Factual only; strategy decides:
- Inspect the R18 delta (above; contract surface unchanged per the file list)
  and deliberately re-qualify the Gateway peer (re-pin
  `tests/fixtures/gateway/current_peer_authority.json` in a new round, or
  confirm the pin still stands).
- Upon re-qualification, the publication closure (workflow dispatch at S or an
  amended S, `D` capture, `P` with record + `M_P`, `docker-published`
  execution, final published-wording docs pass, then tag/Release as the
  strategic post-merge acts) remains executable from the current green
  implementation head `S`; no orphan registry cleanup is needed (registry
  verified absent for both candidate tags).
- Report-head CI for this report commit may still be running at publication
  time; verify per the protocol.

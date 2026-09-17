# OAP Work Order — 013-b: Re-pin the current Gateway peer and complete the MVP 0.1.0 GHCR publication (same PR #15)

## Objective

Complete the publication that the 013-a round correctly held at R18:

1. Re-qualify and RE-PIN the current Gateway peer to the verified
   contract-identical current gateway `main` (strategic re-adjudication
   recorded below; exact 012-a precedent), so the published image, manifest,
   and documentation carry the current peer.
2. Reconcile the remaining release-facing documentation (including
   `README.md`) from "publication pending" to the released truth, under the
   explicit strategic wheel ruling below.
3. Execute the publication exactly per the 013-a normative ordering:
   CI-green final implementation head `S''` → release workflow dispatched at
   `S''` → digest `D` captured (registry-verified) → release-record commit
   `P` (record + regenerated manifest ONLY) → CI at `P` fully green including
   the executed `docker-published` job → report.

The 013-a order remains in force on this PR for every criterion not
superseded here; the 013-a implementation at `S_a` is ACCEPTED AS-IS (no
refactor, no re-implementation of workstreams A–F except where this order
explicitly requires).

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`
- Numeric objective: `013`; round: `013-b`
- PR mode: `AMEND_EXISTING_PR` — **NO NEW PR**
- Existing PR: #15 — https://github.com/ulfe-lmi/slaif-local-coding/pull/15
  (OPEN, non-draft, MERGEABLE; exactly the Objective-013 PR)
- Base: `main` @ `a04693e6792df6a8ad4262acfb46336a0f662202` (unchanged)
- Branch (required, unchanged): `oap/013-mvp-release-publication`
- Current head at order time:
  `29356060322329b9aeed83b289f42ecf5bb66647` (013-a report commit);
  prior implementation head `S_a = 0096886aad1be25770f817dcdeaab779260f903e`
  (CI run 35203279259: all four jobs SUCCESS; report-head run
  35204003091: SUCCESS)
- Verified at order time (strategic, independent, 2026-09-17 ~11:25 CEST):
  - 013-a round independently verified: PR #15 unique/OPEN/non-draft/
    MERGEABLE; report commit `2935606…` changes ONLY the report file with
    first parent `S_a`; 9-commit chain base→S_a as reported; base→S_a diff
    touches NO `src/`, `pyproject.toml`, `uv.lock`, `config/`, or
    `tests/fixtures/gateway/`; registry tags `0.1.0` and
    `sha-0096886…` independently confirmed ABSENT (anonymous); protected
    host post-round probe (2026-09-17T11:19:10+02:00) identical to the
    pre-round baseline: Qwen user unit active/running MainPID 23961,
    vllm pid 23961 on 0.0.0.0:18020 only, 18031/18033/18034 closed,
    three pre-existing exited non-slaif containers, profile file mtime/mode
    unchanged. 013-a report status BLOCKED-at-publication per its own R18
    rule; all other workstreams COMPLETE at S_a.
  - GATEWAY DRIFT (the 013-a blocker): gateway `main` =
    `08ca421bee1ddca62078302b910e8be88cf705be`
    (2026-09-17T08:30:55Z), 8 commits ahead of the pinned peer
    `1fccaa746df6cd44f1ddf8c2ec5cf6ea9f18b1cb` (gateway objectives 166-a
    "openai-sdk3-compatibility-qualification" and 167-a "current-main
    integrated qualification"; PRs #303/#304 merged).
  - STRATEGIC DELTA INSPECTION (read-only GitHub blob comparison, pinned
    peer vs `08ca421…`): the local-coding contract surface is UNCHANGED —
    all three files blob-identical:
    `app/slaif_gateway/modules/servers/local_coding/contract.py`
    (`9e8ae5ef8e1f9d8d48bf3627b9a767d86593a6ac`),
    `app/slaif_gateway/modules/clients/codex_0149.py`
    (`8976c984c4430d65b3d36bad8565062a8c6f955a`),
    `app/slaif_gateway/providers/streaming.py`
    (`73cc9f99e8c3cb2f3eb95173344bfbdc211c71ff`). The 8-commit delta
    contains only `docs/`, `oap/`, client e2e tests under `tests/e2e/`, and
    `pyproject.toml` (dev-dependency `openai` 2.41.0 → 3.9.0). The strict
    contract test files are LOCAL to this repository
    (`tests/test_gateway162_validator_factory.py`,
    `tests/test_current_gateway_contract.py`) and are unchanged in PR #15.
  - No `013-b`/`013-c` orders exist; no release workflow run exists;
    registry remains absent for all candidate tags.

## Strategic re-adjudications (authority recorded)

1. **Peer re-pin (the deliberate re-qualification of human requirement 9).**
   The 8-commit gateway drift is a contract-surface-identical no-op for the
   local coding contract (proven above). Therefore the published image,
   manifest, and current-facing docs must carry the CURRENT peer:
   `08ca421bee1ddca62078302b910e8be88cf705be`. The mechanical
   re-qualification is the `gateway-contract` job re-proven against the new
   pin at `S''` (exact 012-a precedent: blob-identical re-pin + contract
   gate). No human decision is required.
2. **Wheel ruling (README change consequence).** `README.md` is a wheel
   build input (embedded in the wheel METADATA); human requirement 12
   forbids repository documentation that still describes the MVP as
   unreleased. Therefore `README.md` changes in this round and the wheel
   hash legitimately changes with it. The change MUST be METADATA-ONLY and
   is mechanically proven (B6): the new wheel is byte-identical to the 012
   authority wheel `fceadc378130dd4ffcc3f75d17b5e098577652914f541245d31247911be23aeb`
   for every entry except the dist-info METADATA (which differs only in
   README-derived content). The new wheel hash becomes the release wheel
   recorded in the manifest at `S''`/`P`. `src/`, `pyproject.toml`, and
   `uv.lock` remain frozen. The sdist hash also legitimately changes
   (README + docs are sdist inputs); it is recorded in the manifest and, per
   the 012-c citation-stability law, NOT cited in current-facing docs.

## Why 013-a is insufficient (exact)

R12 (trigger workflow, capture `D`) is BLOCKED by R18 peer drift; R1's
record, R13's published execution, and R15/R16's final published wording
were hold-conformantly deferred (013-a deviations 3–4). The peer pin is
stale at `S_a`. All of the above is completed in this round on the SAME PR.

## Bounded scope (files)

- `tests/fixtures/gateway/current_peer_authority.json` — peer re-pin.
- `Dockerfile` — `SLAIF_GATEWAY_PEER_SHA` ARG default → new peer (ONLY
  Dockerfile line changed).
- `scripts/release_provenance_manifest.py` — `OBJECTIVE` constant →
  `013-b`.
- `tests/test_release_provenance_manifest.py` — objective assertion →
  `013-b`.
- `README.md` — released-truth reconciliation (wheel input; see ruling 2).
- `docs/DOCKER-INSTALL.md` — pending-publication wording → published truth.
- `docs/IMPLEMENTATION-ROADMAP.md`, `oap/COMPLETENESS.md` — current-state
  sections: Objective-013 line + released state; peer references updated.
- `docs/SLAIF-GATEWAY-INTEGRATION.md`, `docs/TOPOLOGY.md`,
  `docs/RELEASE-CUTOVER-RUNBOOK.md` — peer references updated (only where
  the stale pin is cited as current).
- `packaging/release_provenance_manifest.json` — `M_S''` in the `S''`
  commit; `M_P` in the `P` commit (regenerated with the record).
- `packaging/release_record.json` — exists ONLY in `P`'s tree.
- Transcript: activated 013-b order + `oap/active` (`013-b`).

## Explicit non-goals

- All 013-a non-goals remain in force verbatim (protected host, no git
  tag/Release by coding, no version bump, no dependency change, no Gateway
  repository change, no protocol change, no systemd change, no other
  registry, no docker build/run/up/recreate on the protected host, no
  protected-model inference).
- NO changes to `compose.yaml`, `compose.build.yaml`,
  `.github/workflows/release-image.yml`, `.github/workflows/ci.yml`,
  `scripts/docker_qualification_ci.py`, `scripts/release_registry_publish.py`,
  `scripts/ghcr_tag_check.py`, `packaging/release_provenance_manifest.schema.json`
  — the 013-a implementation is accepted as-is.
- NO changes to `src/`, `pyproject.toml`, `uv.lock`, or `config/` templates.
- NO edits to the 013-a order, the 013-a report, or any earlier OAP
  artifact (immutable; transcript bytes unchanged).
- NO new dependencies. NO OAP machinery expansion.

## Acceptance criteria (013-b)

- **B1.** At round start, coding re-verifies remote gateway `main` ==
  `08ca421bee1ddca62078302b910e8be88cf705be`. If it differs: DO NOT
  publish; stop; publish a BLOCKED report with the exact delta; strategy
  inspects and re-adjudicates. If it matches: proceed.
- **B2.** Peer re-pin: fixture `commit` = `08ca421…` (all other fixture
  fields unchanged); `Dockerfile` `SLAIF_GATEWAY_PEER_SHA` default =
  `08ca421…` (only line changed in the Dockerfile); every current-facing
  doc citation of the old pin as CURRENT is updated (historical OAP records
  and objective-scoped historical statements stay byte-identical).
- **B3.** Generator `OBJECTIVE` and the E3 objective assertion = `013-b`.
- **B4.** The `gateway-contract` job passes at `S''` against the NEW pin
  (checks out `08ca421…` and runs the strict 18-test gate) — the mechanical
  re-qualification proof.
- **B5.** Documentation reconciled to the released truth, with these exact
  semantics: MVP `0.1.0` is RELEASED on `ghcr.io/ulfe-lmi/slaif-local-coding`
  with tags `0.1.0` and `sha-<S''>` (both resolving to one registry digest
  `D`); image source commit `S''`; Git tag `v0.1.0` TARGETS `S''` as the
  release reference (created by strategy post-merge — documents must NOT
  claim the tag/Release objects already exist at document time); `D` is
  authoritatively recorded in `packaging/release_record.json` and the
  manifest (`oci.image_digest`, `release` section) — documents reference
  these records by path and must NOT carry a literal digest (it cannot
  exist at `S''` time) and must NOT cite the current sdist hash or the
  manifest `objective` field (012-c citation-stability law); publication is
  registry-only: protected-host cutover NOT performed, no real deployment
  yet evidenced, Docker qualification remains deployment-qualified
  (disposable/CI environments only), D1 binding law / loopback default /
  systemd secondary path unchanged; release ladder language only (no
  production-ready/certification claims). `README.md` no longer describes
  the MVP as unreleased. No current-facing doc asserts a status above what
  the manifest states at `P`.
- **B6.** METADATA-ONLY wheel proof: (a) clean rebuild of the 012 authority
  state (`git archive` of `a04693e6792df6a8ad4262acfb46336a0f662202` tree +
  `uv build`) reproduces
  `fceadc378130dd4ffcc3f75d17b5e098577652914f541245d31247911be23aeb`;
  (b) unpack both wheels: every entry byte-identical EXCEPT the dist-info
  METADATA, whose difference is only README-derived content; (c) the new
  wheel hash `H_new` is recorded in the report and is the hash bound by CI
  (wheel-binding step), the manifest, the in-image provenance proof, and
  the release workflow.
- **B7.** `S''` = the final implementation head = a manifest-regeneration
  commit (`M_S''`: objective `013-b`, `generated_from.git_commit` = S'''s
  parent, not-yet-published state, new wheel/sdist hashes, peer
  `08ca421…`) whose tree contains the peer re-pin, the doc reconciliation,
  and the generator/test objective change, and does NOT contain the release
  record. CI at `S''` FULLY GREEN: `test`, `gateway-contract` (new pin),
  `docker` (all 011/012 phases via the two-file compose), `docker-published`
  (explicit not-yet-published skip).
- **B8.** Coding triggers `gh workflow run release-image.yml --ref <S''>`
  within the round; the run SUCCEEDS; `D` and the workflow run id are
  captured from the registry-verified run output; the run log proves both
  tags `0.1.0` and `sha-<S''>` resolve to `D`.
- **B9.** `P` = child of `S''` changing EXACTLY two files: adds
  `packaging/release_record.json` (schema `slaif-release-record-v1`;
  `image_source_commit` = `S''`; `oci_image_digest` = `sha256:D`;
  `oci_tags` = `["0.1.0", "sha-<S''>"]`; `published_at` RFC 3339 UTC;
  `publication_workflow_run_id`) and regenerates
  `packaging/release_provenance_manifest.json` (`M_P`) with the record
  staged at HEAD = `S''` (so `M_P.generated_from.git_commit` = `S''`;
  released state: `status.released` true, `oci.published` true,
  `oci.image_digest` = `D`, `release` section with
  `git_tag_target` = `S''`, qualification label `mvp-release-0.1.0`,
  truthful published-state limitations replacing exactly the two
  not-yet-published bullets, published tag convention). `P` must not change
  any build input, doc, workflow, compose file, or OAP order/active/report.
- **B10.** CI at `P` FULLY GREEN including the EXECUTED `docker-published`
  job: pull by digest `D` and by both tags (each resolving to `D`,
  registry-verified); full label set verified (revision = `S''`, version
  `0.1.0`, peer `08ca421…`, wheel `H_new`, qualification
  `mvp-release-0.1.0`, topology mode unchanged); pull-based compose run
  against the disposable fake upstream on canonical port 18031 reaches
  healthy readiness; representative signed request succeeds from the
  simulated Gateway namespace; negative contract cases and missing-secret
  readiness fail closed; no-build proof; teardown absence proof.
- **B11.** Report `R` = child of `P`, report-only, pushed and verified as
  remote PR head with first parent `P`; CI at `R` green (strategy waits).
- **B12.** Protected-host invariance recorded (before/after read-only
  probes: Qwen user unit state, 18020 owner, 18031/18033/18034 closed,
  container list, profile file mtime/mode); NO docker build/run/up on the
  host (render-only `docker compose config` with temporary 0-byte files
  permitted, as in 013-a).
- **B13.** Every 013-a acceptance criterion remains satisfied at the final
  head (the 013-a order stays in force on this PR): the 013-b report
  re-affirms each R-criterion with its evidence at `S''`/`P` (R12/R13
  transitions from BLOCKED/PARTIAL to satisfied by B8/B10; R15/R16 to
  satisfied by B5; R14/R18 by B4/B7/B10).

## Verification and evidence (exact)

- Local at `S''` tree: full `pytest`, ruff check + format, mypy, compileall,
  `bash -n` on changed shell, `uv build` + wheel/sdist hashes, E3 gate
  (not-yet-published state at `S''`, published-state variants unit-tested),
  the METADATA-ONLY wheel proof (B6), `docker compose config` render checks
  (render only), protected-host before probe.
- CI at `S''`: all four jobs (B7/B4). Release workflow run at `S''`:
  SUCCESS (B8). CI at `P`: all four jobs with `docker-published` EXECUTED
  (B10). CI at `R`: green (strategy verifies).
- Registry (captured by coding, re-verified independently by strategy):
  `0.1.0` → `D`, `sha-<S''>` → `D`, image pulled by digest carries the
  asserted labels, anonymous pull works.
- Protected-host after probe (B12).

## Documentation and compatibility contracts

- The pinned Gateway contract moves to the current peer `08ca421…`
  (contract surface blob-identical; strict gate re-proven at B4).
- The configuration contract is unchanged (same signed template, same three
  placeholders, same three distinct Local-side secret roles).
- Historical OAP orders/reports and all 009–012 records remain
  byte-identical.

## Security / privacy / secrets / resource / protected-host constraints

- Identical to order 013-a: GITHUB_TOKEN only for the registry; no new
  long-lived secret; no secret/host-path/private-identifier/prompt/model-
  output content in image, workflow, compose renders, CI logs, record,
  manifest, or report; CI fake credentials per the 011 pattern; published
  image passes the same forbidden-content scan; protected live-host law in
  full force (read-only probes only); no protected-model inference anywhere.

## Local authority

Identical to order 013-a: coding owns safe repo-local tooling,
uv/pytest execution, static renders, the `gh workflow run` dispatch
(credential verified present with `repo`+`workflow` scopes), and the clean
`git archive` rebuild for B6. Human and strategic are not terminal
operators.

## GitHub publication requirements

- Same branch `oap/013-mvp-release-publication`, same PR #15. Push ALL
  non-report work before the report. The PR contains every activated
  objective order (`013-a` + `013-b`), `oap/active` (`013-b`), and both
  round reports. NEVER merge; never enable auto-merge; publish the
  report-only SELF child `R` and verify it is the remote PR head with first
  parent `P`. Update the PR body with the final S''/D/peer facts at round
  end.

## Exact immutable report contract

`oap/reports/013-b-repin-peer-and-complete-publication.md` (exactly one
report for this ID) containing:

1. `Implementation head SHA: <literal 40-hex P>` and
   `Report publication commit: SELF`.
2. Overall status plus per-workstream status.
3. Literal facts: `S''` (image source commit), `D` (`sha256:<64-hex>`),
   GHCR tag→digest mapping as registry-verified, release-workflow run id,
   `published_at`, new wheel hash `H_new` (with the B6 METADATA-ONLY proof
   result), old authority wheel `fceadc37…` (reproduced in the clean
   rebuild), Gateway peer (must be `08ca421…`), `M_S''.generated_from` and
   `M_P.generated_from`, PR number/URL.
4. Per-acceptance-criterion evidence for B1–B13 AND the re-affirmed 013-a
   R-criteria at the final head (exact command/phase/CI references; honest
   status labels).
5. CI run ids and per-job conclusions at `S''`, `P` (and `R` if observable).
6. Protected-host before/after invariance record (B12).
7. Explicit statements: NO Git tag created, NO GitHub Release created, NO
   protected-host mutation, NO docker build/run/up on the protected host,
   NO gateway repository change, NO dependency change, 013-a order/report
   bytes untouched.
8. Any deviation with exact justification and status.

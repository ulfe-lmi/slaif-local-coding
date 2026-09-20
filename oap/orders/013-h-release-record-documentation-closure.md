# OAP Work Order — 013-h

## Objective

Objective 013, round `013-h` (AMENDS the single Objective-013 PR #15 — NO new
numeric objective, NO new PR): after the human-authorized visibility act makes
the published image anonymously pullable, complete the release closure on the
EXISTING publication — the generator/E3 objective bump `W7`, the
release-record commit `P`, the FIRST EXECUTED `docker-published` gate, the
release-facing documentation reconciliation `D1`, and the report `R`. NO new
dispatch, NO new registry write, NO new image, NO new tag: the ONE controlled
publication was consumed in round 013-g (run `35263999980`) and this round
records that existing state.

## Strategic re-adjudication (primary evidence; strategy-verified at drafting
## time 2026-09-17 and independently re-verified at re-publication 2026-09-18)

- Round 013-g ended BLOCKED at G3 branch B-3 (report commit
  `881f1f360db8c2a22f89fac1e844195f661e8a80`, report-only, parent = W6b
  `fe334e87c9f0fc65d1826cf9af7dad7e9f70a94a`): G1 COMPLETE (W6b, one file,
  two sdist fields, clean-worktree fixed-point proof, CI 4/4 first fully green
  of Objective 013), G2 COMPLETE (the ONE dispatch consumed: run
  `35263999980`, headSha = W6b, `success`, layers 1–6 PASSED, both tags
  `0.1.0` + `sha-fe334e87…` written to ONE digest
  `D = sha256:a5debcb24bb6bbf7cf00dbf80cd17367d57186f6b0d7fadac020b94df53a0011`
  [sic — see the authoritative value below]), G3 = package visibility
  HUMAN UI ACT (the single authorized API attempt returned HTTP 404,
  credential-scope boundary). Strategy has verified the round's remote truth
  (W6b one-file diff, run logs, zero repo secrets, workflow `secrets.`
  hygiene) and INDEPENDENTLY confirmed the round's static pre-G5 finding:
  (a) `tests/test_release_provenance_manifest.py::
  test_publish_state_source_commit_binding` (R4(a), lines 412–428) asserts in
  the published state `generated_from.git_commit == record
  ["image_source_commit"]`; (b) the sdist whitelist
  (`pyproject.toml` `[tool.hatch.build.targets.sdist] include`) contains the
  whole `packaging/` directory with only the manifest + schema
  top-level-excluded, so `packaging/release_record.json` IS an sdist input
  whenever present (the 013-g record-inclusion probe: 109 entries).
- **Normative correction (recorded):** the 013-g order's G5 specification
  (`M_P.generated_from.git_commit = W7`; `M_P.artifacts.sdist = M_W7's
  sdist hash`) is WITHDRAWN as mechanically infeasible against the frozen
  test contract. The conforming value set is mechanically determined and is
  fixed by this order (workstreams G2/G3 below). This is a hash-recorded
  strategic correction; the 013-g order bytes remain immutable in the
  transcript.
- The 013-g BLOCKED report's interim state is exactly the pre-condition of
  this round: the registry holds `0.1.0` + `sha-fe334e87…` at digest `D` in
  package `ghcr.io/ulfe-lmi/slaif-local-coding`; the pre-existing private
  `sha-be3c78b…` version is an untouched orphan; the repository has zero Git
  tags and zero GitHub Releases (strategy post-merge acts); cutover NOT
  performed.

### Authoritative publication facts (strategy-verified; bind every value below)

- Image-source commit `S = W6b =
  fe334e87c9f0fc65d1826cf9af7dad7e9f70a94a` (GITHUB_SHA of the consumed
  dispatch; in-image `org.opencontainers.image.revision`; future Git tag
  `v0.1.0` target).
- Published digest `D =
  sha256:a5debcb24bb6bbf7cf00dbf80cd17367d57186f6b0d7fadac020b94df53a0011`
  (the single digest BOTH tags resolve to; 013-g layer-6 in-script
  verification + strategy's own raw-log read of run `35263999980`; strategy
  verified this 64-hex value character-for-character against the run's raw
  log — all full-digest occurrences in the immutable 013-g report match it
  exactly, and the report's two `a5debcb2…` mentions are deliberate
  abbreviations, not slips).
- Publication run: `35263999980` (`release-image.yml`, `workflow_dispatch`,
  headSha = W6b, `success`).
- `published_at = "2026-09-17T19:18:06Z"` — the publication job's completion
  instant, anchored to the raw log line `Complete job
  2026-09-17T19:18:06.1939601Z` of run `35263999980` (truncated to seconds,
  the loader's RFC 3339 UTC form).
- Package visibility: the human-authorized act (GitHub UI: organization
  `ulfe-lmi` → Packages → `slaif-local-coding` (container) → visibility →
  public) is the ENTRY precondition of this round's productive path.
  Strategy re-probed token-free immediately before this order's publication
  (2026-09-18T12:50Z): anonymous `scripts/ghcr_tag_check.py` reports
  `0.1.0` → `absent` and `sha-fe334e87…` → `absent` (raw anonymous
  `HEAD /v2/ulfe-lmi/slaif-local-coding/manifests/0.1.0` → HTTP 401), i.e.
  the package is STILL NON-PUBLIC at publication time; the human act has
  NOT yet been observed. G0 is therefore the round's entry gate, not a mere
  re-verification: if G0 finds either primary tag not anonymously
  resolving to `D`, the round stops immediately with a zero-work BLOCKED
  report per G0's stop law (the human visibility act remains the sole
  unblocking act; a follow-up letter then completes this identical scope
  from the new head); if G0 passes (the human act completed before G0),
  the round proceeds with G1–G4 exactly as specified. Both outcomes are
  protocol-complete on the same PR #15.
- Gateway release peer: UNCHANGED, FROZEN at
  `08ca421bee1ddca62078302b910e8be88cf705be` for release 0.1.0 (the 013-d
  freeze rule stands; NO re-pin; the fixture stays). Strategy re-verified at
  this order's publication (2026-09-18) that the three Local contract source
  blobs are byte-identical at the frozen pin and at Gateway `main`
  (`845695f03c41233754f276e99c8bf7014d5c21a0`, UNCHANGED at publication
  time): `contract.py` =
  `9e8ae5ef8e1f9d8d48bf3627b9a767d86593a6ac`; `codex_0149.py` =
  `8976c984c4430d65b3d36bad8565062a8c6f955a`; `streaming.py` =
  `73cc9f99e8c3cb2f3eb95173344bfbdc211c71ff`.

## GitHub objective state

- Objective number: 13; round: `013-h`; PR mode: `AMEND_EXISTING_PR`.
- PR: #15 `https://github.com/ulfe-lmi/slaif-local-coding/pull/15` (the
  single Objective-013 PR; OPEN; MERGEABLE).
- Branch: `oap/013-mvp-release-publication`; base `main` @
  `a04693e6792df6a8ad4262acfb46336a0f662202`.
- Starting remote SHA (verified at this order's publication,
  2026-09-18T12:44Z): `881f1f360db8c2a22f89fac1e844195f661e8a80` (the
  013-g report commit; verified report-only with first parent = W6b;
  current PR head; PR #15 OPEN/MERGEABLE, mergeStateStatus CLEAN,
  autoMergeRequest null; CI at this head, run `35264744688`, 4/4 success;
  CI at W6b, run `35263314546`, 4/4 success).
- Commit chain for this round: `W7` (child of the 013-g report) → `P`
  (child of W7, EXACTLY two files) → `D1` (child of P; documentation +
  manifest regeneration) → `R` (report-only, child of D1).
- Implementation head for publication: `S = W6b =
  fe334e87c9f0fc65d1826cf9af7dad7e9f70a94a` (unchanged; NO new image).

## Bounded scope (workstreams)

### G0 — Precondition re-verification (first action of the round)

Token-free anonymous probes (`scripts/ghcr_tag_check.py`, `env -u
SLAIF_GHCR_TOKEN`): `0.1.0` → must resolve to `D`;
`sha-fe334e87c9f0fc65d1826cf9af7dad7e9f70a94a` → must resolve to `D`. Also
record the pre-existing `sha-be3c78b…` probe as the round's BEFORE registry
baseline: once the package is public, every version of the package is
anonymously visible, so the orphan is expected to resolve to the digest
established by the 013-d partial push; if it is `absent` (e.g., removed by
the human as part of the visibility act), record that. The binding
invariant is that the after-round probes are byte-identical to the
before-round probes (ZERO registry delta this round); the orphan must not
be deleted or repointed BY THIS ROUND. If EITHER primary tag does not resolve to
`D` anonymously: STOP immediately with a BLOCKED report (child of the
013-g report, report-only, zero work) stating the exact failing probe
outputs and that the human visibility act is the sole unblocking act. No
other workstream runs in that case.

### G1 — Transcript catch-up commit (with W7)

The 013-g round deliberately left its activated order file and
`oap/active → 013-g` uncommitted (its exact file sets forbade it; recorded in
the 013-g report). This round's `W7` commits the transcript per the standing
protocol: `oap/orders/013-g-manifest-correction-and-complete-publication.md`
(strategic-authored bytes verbatim; SHA-256
`156b82b26dd5bedd1dca5eaa102e1d087a8d06b5ff76b984d4ceae6a1113ebc1`; present
unmodified in the working tree — verify byte-identity before committing),
this 013-h order file (strategic-authored bytes verbatim), and
`oap/active` → `013-h`. No other transcript bytes change; every
pre-existing `oap/orders/*` and `oap/reports/*` file remains byte-identical.

### G2 — Generator/E3 objective bump and manifest `M_W7`

`W7` = child of the 013-g report commit, EXACTLY six files:
1. `scripts/release_provenance_manifest.py`: `OBJECTIVE` → `"013-h"` (plus
   the docstring order reference). No other byte.
2. `tests/test_release_provenance_manifest.py`: the E3 objective assertion →
   `"013-h"`. No other byte.
3. `packaging/release_provenance_manifest.json` → `M_W7`: `objective
   "013-h"`; `generated_from.git_commit = W6b
   (fe334e87c9f0fc65d1826cf9af7dad7e9f70a94a)`; `gateway_peer.commit =
   08ca421bee1ddca62078302b910e8be88cf705be` (FROZEN); `artifacts.wheel` =
   `H_new` `879baa3ad19e0f513090add965d267957d27f7bcd904d1e225586d76126f8b19`
   (unchanged); `artifacts.sdist.sha256` = the fresh clean-build sdist hash
   of the W7 tree (NEW value: the ONLY sdist-input delta vs the W6b/W5/W6
   clean sdist `5a60cd6e…` is the E3 test-file edit; `scripts/` and the
   manifest itself are sdist-excluded; `oap/` is sdist-excluded);
   `oci.published: false`; `oci.image_digest: null`; NO `release` key;
   `status.released: false`; all template/runtime/reference-compatibility
   fields unchanged (their input files are byte-identical).
4. `oap/orders/013-g-manifest-correction-and-complete-publication.md` (new;
   G1).
5. `oap/orders/013-h-release-record-documentation-closure.md` (new; this
   order, strategic-authored bytes verbatim).
6. `oap/active` → `013-h`.
NO other file. Generation mechanics (process norm; dirty-tree
mis-recording is the defect class this objective already suffered once):
fresh detached worktree checked out at `W6b`; apply the W7 file contents
(item 1–3) as working-tree changes; `uv build --sdist` (+ wheel build) from
that worktree; record command + output (sha256, size, entry count 108, entry
list proving `packaging/release_provenance_manifest.json` is NOT an entry and
the only content delta vs the W6b sdist is the test file); run the generator
(its `generated_from` = worktree HEAD = `W6b` by construction); the clean
rebuild of the W7 tree must reproduce `M_W7` byte-for-byte (E3). CI at W7
FULLY GREEN 4/4 (`docker-published` on the explicit not-yet-published skip
path — the record does not exist at W7).

### G3 — Release-record commit `P`

`P` = DIRECT child of W7, EXACTLY two files:
1. `packaging/release_record.json` — schema `slaif-release-record-v1`, the
   loader's CLOSED ten-key set, EXACTLY these values (no other byte):
   - `schema`: `"slaif-release-record-v1"`
   - `version`: `"0.1.0"`
   - `git_tag`: `"v0.1.0"`
   - `image_source_commit`:
     `"fe334e87c9f0fc65d1826cf9af7dad7e9f70a94a"` (= S = W6b)
   - `oci_image_reference`: `"ghcr.io/ulfe-lmi/slaif-local-coding"`
   - `oci_image_digest`:
     `"sha256:a5debcb24bb6bbf7cf00dbf80cd17367d57186f6b0d7fadac020b94df53a0011"`
     (= D)
   - `oci_tags`: `["0.1.0", "sha-fe334e87c9f0fc65d1826cf9af7dad7e9f70a94a"]`
   - `published_at`: `"2026-09-17T19:18:06Z"` (the run-`35263999980` job
     completion instant; raw-log anchor recorded above)
   - `publication_workflow`: `"release-image.yml"`
   - `publication_workflow_run_id`: `35263999980` (integer)
2. `packaging/release_provenance_manifest.json` → `M_P` regenerated with the
   record present (generator's published state): `objective "013-h"`;
   `generated_from.git_commit = W6b
   (fe334e87c9f0fc65d1826cf9af7dad7e9f70a94a)` — REQUIRED by R4(a)
   (`generated_from.git_commit == record.image_source_commit`);
   `release` section exactly `{version "0.1.0", git_tag "v0.1.0",
   git_tag_target W6b, image_source_commit W6b, oci_image_digest D, oci_tags
   ["0.1.0", "sha-fe334e87…"], published_at "2026-09-17T19:18:06Z",
   publication_workflow "release-image.yml",
   publication_workflow_run_id 35263999980}`; `oci.published: true`;
   `oci.image_digest = D`; published tag convention; qualification label
   `mvp-release-0.1.0`; label set (source, version, peer FROZEN, topology
   mode, wheel `H_new`); `artifacts.wheel` = `H_new` (unchanged);
   `artifacts.sdist.sha256` = the fresh clean-build sdist hash of the P tree
   (NEW value: 109 entries — the record IS an sdist input at P; everything
   else per G2); `status.released: true`; `limitations` = the generator's
   published-state bullet substitution (the two not-yet-published bullets
   replaced, all others verbatim).
   Generation mechanics: fresh detached worktree checked out at `W6b`;
   apply the P tree's contents as working-tree changes — ALL of W7's
   changed files (the generator script AND the E3 test file; the script is
   not an sdist input but must be present because it is the program
   emitting `M_P`, its `OBJECTIVE` constant becoming the manifest's
   `objective` field) PLUS the new record file (the test file and the
   record are both sdist inputs); `uv build --sdist` from that worktree
   (record command + output: sha256, size, 109 entries, entry list proving
   the record entry's presence); run the generator (its `generated_from` =
   worktree HEAD = `W6b` by construction); the clean rebuild of the P tree
   must reproduce `M_P` byte-for-byte (E3).
   R4(b) holds by construction: `Dockerfile`, `compose.yaml`,
   `compose.build.yaml`, `.dockerignore` blobs at S = W6b are identical at P
   (neither W7 nor P touches them). R4(c) holds: tags/wheel/qualification
   bindings per the record. NO other file at P.
- CI at P FULLY GREEN 4/4, including the **FIRST EXECUTED `docker-published`
  job** (its pre-record skip path is gone; the record now exists):
  anonymous pull by digest `D` and by both tags, each resolving to `D`;
  registry-API cross-check; OCI label set verified against the record and
  manifest (revision == W6b; version `0.1.0`; peer `08ca421…`; wheel
  `H_new`; qualification `mvp-release-0.1.0`); the PULL-BASED compose
  (primary `compose.yaml` only, `SLAIF_LOCAL_CODING_IMAGE` digest-pinned, NO
  `build` key) against the disposable fake upstream on canonical port 18031:
  readiness healthy; representative signed request succeeds; negative
  contract cases fail closed; missing-secret readiness fail-closed; NO-BUILD
  proof; teardown absence proof.
  - **Narrow gate-defect exception (inherited):** ONLY IF the executed
    `docker-published` job fails due to a defect in the never-executed gate
    itself, a MINIMAL fix to `.github/workflows/ci.yml` and/or
    `scripts/docker_qualification_ci.py` is authorized within this round as a
    documented deviation (it then belongs to D1's file set, and D1's manifest
    regeneration covers the resulting tree), provided it removes, skips, or
    weakens NO 011/012/013 qualification semantics. Any other cause → report
    and stop.
  - Transient CI infrastructure failure → ONE `gh run rerun <id> --failed`
    (strategy precedent); a second failure of any kind → STOP and report.

### G4 — Release-facing documentation reconciliation `D1`

`D1` = child of P: the documentation commits the objective's release-facing
truth (the 013-g report's Documentation finding: the current statements
describe a not-yet-published state and are stale against registry reality).
Files (documentation statements ONLY — no other doc or code change):
1. `docs/RELEASE-ARTIFACT-POLICY.md`: the OCI artifact-policy bullet and the
   `## Publication` section currently read "publication PENDING as of this
   PR's head, order 013-a R18 Gateway-peer hold" / future-tense "will
   resolve … will target … will be" / "executed at the final implementation
   head of this PR (order 013-d)". Correct to the exact post-publication
   truth: publication EXECUTED in round 013-g (the ONE consumed dispatch,
   run `35263999980`) at implementation head S = W6b
   `fe334e87…`; tags `0.1.0` + `sha-fe334e87…` resolve to digest
   `sha256:a5debcb24bb6bbf7cf00dbf80cd17367d57186f6b0d7fadac020b94df53a0011`;
   package `ghcr.io/ulfe-lmi/slaif-local-coding` is PUBLIC (human-authorized
   visibility act; anonymous pull verified); `packaging/release_record.json`
   present from P onward; the Git tag `v0.1.0` targets S (created by
   strategy post-merge; the GitHub Release follows that tag); publication is
   registry-only — protected-host cutover NOT performed, no real deployment
   yet evidenced. Preserve the correction records (013-b diagnosis
   retraction; 013-c secret withdrawal; 013-d mechanism) as historical prose.
2. `docs/DOCKER-INSTALL.md`: the lead paragraph's "publication (Objective
   013, round 013-b) was executed from the final implementation head of PR
   #15" mis-attributes the round — publication was consumed in round 013-g
   at S = W6b (run `35263999980`); the `D`/`S` values are the authoritative
   ones recorded in `packaging/release_record.json` and the manifest. Correct
   the attribution and state the post-publication truth; keep the pull-based
   path, prerequisites, and build-from-source separation statements intact.
3. `docs/IMPLEMENTATION-ROADMAP.md`: the Current-state 013 line (publication
   held / re-pin narrative) → the exact final state: 013-a implementation;
   013-b peer re-qualification to the frozen `08ca421…`; 013-d/e/f
   corrections; 013-g consumed the publication (S, D, run id); 013-h records
   it (release record P, executed `docker-published`, documentation
   reconciliation); Git tag `v0.1.0` + GitHub Release are strategy
   post-merge acts; cutover NOT performed.
4. `oap/COMPLETENESS.md`: the 013 line currently claims "013-b … completed
   the publication: MVP 0.1.0 RELEASED" — wrong round AND an exceeded status
   ceiling. Correct to: publication consumed in 013-g (S, D, run id);
   release record committed in 013-h; MVP 0.1.0 PUBLISHED to
   `ghcr.io/ulfe-lmi/slaif-local-coding` (public package, tags `0.1.0` +
   `sha-<S>`, one digest D); pull-based installation canonical; Git tag
   `v0.1.0` (strategy post-merge) and GitHub Release follow; cutover NOT
   performed; no real deployment yet evidenced. The 011 line and all other
   objective rows remain byte-identical (historical rows are immutable).
   Also correct the file's lead "publication is PENDING the R18
   Gateway-peer hold — no release record exists" to the post-publication
   state (the R18 hold was resolved in 013-b; the record exists from P
   onward).
5. `packaging/release_provenance_manifest.json` → `M_D1` regenerated from the
   D1 tree: BYTE-IDENTICAL to `M_P` except `artifacts.sdist.sha256` (and
   `size_bytes`/`entry_count` if the size moves) — `docs/` IS an sdist
   input, so the D1 sdist hash is NEW (109 entries, record present);
   `generated_from.git_commit` remains `W6b`; all published-state fields
   unchanged. Generation mechanics as G3, with the D1 tree's contents
   (W7's changed files, the record file, and the D1 documentation files)
   applied in a worktree anchored at `W6b`; the clean rebuild of the D1
   tree reproduces `M_D1` byte-for-byte.
   If the narrow gate-defect exception of G3 fired, D1 additionally carries
   the gate-fix files (recorded in the report).
- Documentation truthfulness duty (verification, statement by statement):
  every changed statement must match live remote truth at D1 — zero Git tags
  and zero GitHub Releases (`git ls-remote --tags origin`; `gh release
  list`), package public (G0 probes), record present, cutover NOT performed.
  Record the verification in the report. NO other `docs/` or `oap/` change
  in D1.
- CI at D1 FULLY GREEN 4/4 (the `docker-published` job executes again —
  still green; E3 passes on the regenerated manifest).

### G5 — Report `R`

`R` = report-only commit, child of D1. `Implementation head SHA` =
`fe334e87c9f0fc65d1826cf9af7dad7e9f70a94a` (W6b = S) in all forms. Status:
COMPLETE (all of G0–G4 done; the round leaves the PR ready for strategic
merge: implementation + record + executed published-image gate + reconciled
documentation).

## Identity bindings (normative)

- S (image-source commit) = W6b — the tree the consumed 013-g dispatch built
  from (GITHUB_SHA = W6b; in-image revision label = W6b; future Git tag
  `v0.1.0` target).
- D = `sha256:a5debcb24bb6bbf7cf00dbf80cd17367d57186f6b0d7fadac020b94df53a0011`
  — the single digest BOTH published tags resolve to (013-g layer-6
  in-script verification + strategy raw-log read + this round's G0
  anonymous re-verification).
- W7 (child of the 013-g report) → P (child of W7) → D1 (child of P) → R
  (child of D1). NO registry write anywhere in this chain.
- `M_W7.generated_from.git_commit = W6b`; `M_P.generated_from.git_commit =
  W6b` (R4(a)); `M_D1.generated_from.git_commit = W6b`.
- `record.image_source_commit = W6b`; `record.oci_image_digest = D`;
  `record.oci_tags = ["0.1.0", "sha-<W6b>"]`; `record
  .publication_workflow_run_id = 35263999980`; `record.published_at =
  2026-09-17T19:18:06Z`.
- No circularity: the image was built from S = W6b in the consumed 013-g
  run; P's record describes S + D truthfully; the Git tag (strategy,
  post-merge) points at S; every manifest in this round is generated from a
  worktree anchored at W6b and re-verified by E3 on each clean tree; D1
  changes only documentation (an sdist input) and carries the regenerated
  sdist hash.

## Explicit non-goals (all 013-a … 013-g non-goals inherited, plus)

- NO new dispatch, NO registry publication of any kind (the ONE controlled
  dispatch was consumed in 013-g; this round's registry delta must be ZERO —
  before/after token-free probes prove it). NO repoint of any tag (in
  particular `sha-be3c78b…` and the two published tags remain exactly where
  013-g left them). NO package/version deletion. NO visibility change.
- NO changes to: `src/`, `pyproject.toml`, `uv.lock`, `config/`,
  `Dockerfile`, `.dockerignore`, `compose.yaml`, `compose.build.yaml`,
  `.github/workflows/release-image.yml` (BYTE-IDENTICAL),
  `scripts/ghcr_tag_check.py`, `scripts/release_registry_publish.py`
  (BYTE-IDENTICAL), the gateway-contract gate/fixture, ANY
  `oap/reports/*` (immutable), ANY pre-existing `oap/orders/*` file
  (byte-identical; the 013-g order file is NEW to git at W7 with
  strategy-verified bytes).
- `.github/workflows/ci.yml` and `scripts/docker_qualification_ci.py`
  change ONLY under the narrow G3 gate-defect exception (documented
  deviation; no qualification semantics removed, skipped, or weakened).
- `packaging/release_provenance_manifest.json` changes ONLY at W7, P, D1
  (the three regenerations above); `packaging/release_record.json` appears
  ONLY at P and is byte-identical thereafter.
- `scripts/release_provenance_manifest.py` and
  `tests/test_release_provenance_manifest.py` change ONLY at W7 (the
  objective-constant/docstring bump and the E3 assertion — nothing else).
- NO documentation change beyond D1's four files (statement corrections only;
  the 011 line of `oap/COMPLETENESS.md` and every other objective row
  byte-identical).
- NO protected-host mutation (Qwen/18020, `qwen-serving` units, model/
  checkpoint/patches/venv/systemd/launch flags, API keys, firewall/VPN/
  network bindings, active Codex profiles); NO docker build/run/up on the
  protected host; NO live cutover; NO Qwen/protected-model inference.
- NO Gateway-repository mutation (read-only verification only; peer remains
  `08ca421…`; the fixture is NOT re-pinned).
- NO Git tag / GitHub Release by coding (strategy post-merge acts). NO
  repository Actions/security setting change. NO new credentials; NO
  re-provisioning of any repository secret (zero at drafting time). NO
  version change (stays `0.1.0`).

## Required evidence (report)

- G0: the token-free probe outputs (both tags → D; orphan probe).
- G1: byte-identity verification of the committed 013-g order file (SHA-256
  `156b82b2…`); `oap/active` → `013-h`.
- G2: the exact six-file diff; the clean-worktree generation proof (command +
  output: sdist sha256/size/108 entries + entry-list delta vs the W6b sdist
  = exactly the test file); `M_W7`'s full field values; CI at W7 (4/4;
  `docker-published` explicit skip).
- G3: the exact two-file diff; EVERY `release_record.json` field value;
  `M_P`'s full field values (including the sdist 109-entry build proof);
  R4(a)–(d) green at P (CI); the EXECUTED `docker-published` phase summary
  (each phase, the anonymous pull lines by digest and by tag, the label
  verification, the no-build proof, the teardown absence proof); CI at P
  (4/4).
- G4: the four-file documentation diff (statement by statement: old → new,
  each new statement matched to live remote truth); `M_D1`'s regeneration
  proof (byte-identical to M_P except the sdist block); CI at D1 (4/4,
  `docker-published` executed again).
- Registry state before (G0) and after (post-round) token-free probes:
  identical (ZERO registry delta this round); the published tags still →
  `D`; the `sha-be3c78b…` orphan untouched.
- Protected-host before/after read-only probe table. Round-start baseline
  (strategy-verified at publication, 2026-09-18): `qwen-serving-vision.service`
  (systemd `--user`) `active (running)`, `MainPID=23961` (vllm) — the same
  process continuously since `2026-09-06T18:57:26`; `qwen-serving.service`
  (user) `inactive`/`dead`; port `18020` `LISTEN 0.0.0.0:18020` owned by
  vllm `pid=23961` only; ports `18031`/`18033`/`18034` closed; docker
  (read-only, `sudo -n`): the three pre-existing exited non-slaif
  containers (`0e3109680183`/`cc5e7d551c0a` — `chrockey/fpt-votenet:v0.1.0`;
  `379dcff9d7f2` — `hello-world`) and images `postgres:16`/
  `hello-world:latest`/`chrockey/fpt-votenet:v0.1.0` (zero slaif images);
  `~/.codex/qwen-neumann.config.toml` `size=924`, `mode=600`,
  `mtime=2026-09-18 13:16:48 +0200`; coding OAP wrapper `profile=ox-alpha`
  (OpenRouter). NOTE: the `qwen-neumann` config stat is PRE-EXISTING DRIFT
  versus the 013-g baseline (`858` B, `mtime=2026-09-13 11:59:21 +0200`),
  made outside OAP work between the 013-g report (`2026-09-17T19:24Z`) and
  this order's drafting; strategy records it as the round-start baseline,
  attributes it to the human environment, and the round's after-probes must
  equal THIS round-start baseline (not the 013-g baseline). Any movement of
  ANY row during the round → STOP and report.
- Grep proofs: NO `secrets.SLAIF_GHCR_TOKEN` in active files (only the
  immutable OAP transcripts may match); the release workflow's only
  `secrets.` references are `secrets.GITHUB_TOKEN`; zero repository secrets
  (`gh secret list` empty).
- Gateway freeze re-verification at round time: the three contract blob SHAs
  at `08ca421…` AND at current Gateway `main` (record the current main SHA;
  blob identity required at both); the strict gate 18/18 green at W7/P/D1 CI
  (network guard enabled).
- 013-a R1–R20 re-affirmation at the round's final state (R1 SATISFIED — the
  record exists from P; R12 by the consumed 013-g dispatch; R13 SATISFIED —
  the gate EXECUTED at P and D1; R17 by D1's statement-by-statement
  verification).
- Safety/scope confirmations (standard set), known limitations/blockers, and
  the exact remaining strategic/human acts (Git tag `v0.1.0` → S + GitHub
  Release — strategy post-merge; optional orphan cleanup of the private
  `sha-be3c78b…` version — strategy's choice, NOT authorized here;
  protected-host cutover — separate human act).

## Report contract

- Path: `oap/reports/013-h-release-record-documentation-closure.md`.
- Report-only SELF commit; first parent = D1; `Implementation head SHA:
  fe334e87c9f0fc65d1826cf9af7dad7e9f70a94a` (W6b).
- Status: COMPLETE (or BLOCKED with the exact failing probe at G0, per G0's
  stop law).
- After publishing the report commit and verifying it remotely (PR head = R,
  report-only, parent verified), send exactly two bytes `OK` to
  `response.fifo`.

## Safety/scope (restated)

Routine terminal/setup belongs to coding. The protected live-host boundary
is absolute. No human/strategy recruitment for routine work. No merge by
coding. No auto-merge. One numeric objective = one PR: this round amends PR
#15 only. This round changes no publication input and performs no registry
write: it records, reconciles, and proves the state the consumed 013-g
dispatch left behind.

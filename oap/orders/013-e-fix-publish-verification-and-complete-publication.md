# OAP Work Order — 013-e

## Objective

Objective 013, round `013-e` (AMENDS the single Objective-013 PR #15 — NO new
numeric objective, NO new PR): fix the deterministic publish-verification defect
exposed by the 013-d controlled dispatch, re-establish the ONE controlled GHCR
publication at a new implementation head `W5`, and — if and only if the
package-visibility layer passes with available credentials — complete the
release-record commit `P`, the FIRST EXECUTED `docker-published` gate, and the
report `R`.

## Strategic re-adjudication (primary evidence; supersedes nothing in 013-d's
recorded facts — it completes the classification the 013-d stop law reserved to
strategy)

- The 013-d C6 dispatch (run `35249918197`, head `W4 = be3c78b2016d5d40ce9155df8f94d14525c43d39`)
  proved the corrected GITHUB_TOKEN + qualified-reference mechanism end-to-end
  through layers 1–5: `GITHUB_TOKEN Permissions` granted `Packages: write`;
  wheel binding to `H_new = 879baa3ad19e0f513090add965d267957d27f7bcd904d1e225586d76126f8b19`;
  two-file compose build; `Login Succeeded`; and the qualified
  `ghcr.io/ulfe-lmi/slaif-local-coding:sha-<W4>` push returned exit 0 (the
  script's `_docker(check=True)` raises on any nonzero exit with the registry
  stderr — the same code path that surfaced the explicit 013-c denial; no such
  error occurred). No scope/permission denial occurred.
- The run failed at layer 6, `scripts/release_registry_publish.py::_push_digest()`:
  it scans the captured **stdout only** for `^digest:\s*(sha256:[0-9a-f]{64})\s*$`,
  while the docker CLI (non-TTY) emits push progress — including the final line
  `<ref>: digest:sha256:<64-hex> size:<n>` — on **stderr**. The success path had
  never been exercised (the 013-b and 013-c pushes both failed before a
  completed push). This is a deterministic in-repo verification-tooling defect:
  NEITHER an authorization/permission boundary NOR transient infrastructure.
- Registry state established by 013-d (primary evidence, no repoint occurred):
  package `ghcr.io/ulfe-lmi/slaif-local-coding` (container type) exists in a
  NON-PUBLIC state; tag `sha-be3c78b2016d5d40ce9155df8f94d14525c43d39` was
  written (the W4-built image; its content digest D1 is not recoverable from
  the run); `0.1.0` was NEVER written (pre-dispatch anonymous absence proven;
  the script died before the `0.1.0` step); anonymous manifest HEAD → 401
  UNAUTHORIZED; package metadata API → 403 with the wrapper credentials (no
  `read:packages` scope).
- Strategic determination: the failure class is an in-repo gate defect. 013-e
  authorizes the minimal, precisely scoped fix (D1) and re-establishes the ONE
  controlled publication at `W5` (D3). This is not a retry of the same code
  state: the dispatch is bound to the code state it runs, and the 013-d round's
  single dispatch was consumed by the W4 code state.
- Gateway release peer: UNCHANGED, FROZEN at `08ca421bee1ddca62078302b910e8be88cf705be`
  for release 0.1.0 (the 013-d freeze rule is normative and stands).
  Strategy RE-VERIFIED at this order's drafting time: Gateway `main` has
  advanced again to `1bdbb8bf1534ea0b3217ced136972d1bced9c448` = 21 commits
  beyond the frozen pin; the drift touches `app/slaif_gateway/main.py`,
  `app/slaif_gateway/metrics.py`, both compose files, `pyproject.toml`,
  observability/compatibility/verification docs, Gateway-side OAP transcripts
  (orders/reports 168–173), and `tests/unit/test_metrics_multiprocess.py` —
  NONE of the three Local contract files, which strategy re-verified as
  byte-identical (GitHub blob SHAs) at `08ca421…`, `2b61312…`, AND
  `1bdbb8bf…`:
  `app/slaif_gateway/modules/servers/local_coding/contract.py` =
  `9e8ae5ef8e1f9d8d48bf3627b9a767d86593a6ac`;
  `app/slaif_gateway/modules/clients/codex_0149.py` =
  `8976c984c4430d65b3d36bad8565062a8c6f955a`;
  `app/slaif_gateway/providers/streaming.py` =
  `73cc9f99e8c3cb2f3eb95173344bfbdc211c71ff`.
  The `gateway-contract` CI gate continues to run against the frozen fixture
  (`tests/fixtures/gateway/current_peer_authority.json`, commit `08ca421…`,
  purpose `current_ci_compatibility_authority` = development CI tracking only).
  NO re-pin. This round MUST NOT change the fixture, the gate, or the frozen
  value.

## GitHub objective state

- Objective number: 13; round: `013-e`; PR mode: `AMEND_EXISTING_PR`.
- PR: #15 `https://github.com/ulfe-lmi/slaif-local-coding/pull/15` (the single
  Objective-013 PR; OPEN; MERGEABLE).
- Branch: `oap/013-mvp-release-publication`; base `main` @
  `a04693e6792df6a8ad4262acfb46336a0f662202`.
- Starting remote SHA (at this order's drafting time):
  `59439963a02e8cd6c341708e606f907ef1e6771d` (R, the 013-d report commit;
  report-only, first parent = W4).
- Implementation head: `W5` (created by this round; child of R).
- `P` (release record): DIRECT child of W5, EXACTLY two files — created ONLY
  in the D5-pass branch.
- `R`: report-only SELF commit; first parent = P (D6 branch) or W5 (D5-blocked
  branch).

## Independently verified current state (strategy, at 013-e order time)

- PR #15 OPEN/MERGEABLE (`CLEAN`), head = R `5943996…`, base main unchanged;
  no auto-merge; zero Git tags; zero GitHub Releases.
- CI at R (`5943996…`): run `35251531067` — 4/4 SUCCESS (`docker`,
  `gateway-contract`, `test`, `docker-published` on the explicit not-yet-
  published skip path).
- Repository secrets: ZERO (`gh secret list` empty; `SLAIF_GHCR_TOKEN` removed
  in 013-d C3 at 2026-09-17T16:58:43Z). No re-provisioning of any secret is
  authorized by this order.
- `gh` wrapper credential: classic PAT `jpers1`, scopes `read:org, repo,
  workflow` — NO `*packages` scope (403 on package metadata/visibility APIs;
  recorded as primary evidence in 013-d). Org admin of `ulfe-lmi`.
- Anonymous registry probes at order time (strategy, token-free
  `scripts/ghcr_tag_check.py`): `0.1.0` → `absent`; `sha-be3c78b2016d5d40ce9155df8f94d14525c43d39`
  → anonymous resolution denied (401) — non-public package, consistent with
  the 013-d record.
- Protected host: unchanged per the 013-d report's before/after table (Qwen
  `qwen-serving-vision.service` active, vllm pid 23961 on 0.0.0.0:18020 only;
  18031/18033/18034 closed; three pre-existing exited non-slaif containers;
  zero slaif images; `~/.codex/qwen-neumann.config.toml` 858 B / 600 /
  2026-09-13 11:59:21 +02:00). Re-verify before/after in this round.
- Worktree residue (never commit, never clean): `oap/runtime.env.example`
  (modified), untracked empty root files `Local`, `clean`, `unchanged`.
- Wheel authority: `H_new = 879baa3ad19e0f513090add965d267957d27f7bcd904d1e225586d76126f8b19`
  (83,352 B, 26 entries) — MUST remain the wheel byte-identity of this round
  (D1/D2 touch no wheel input: `src/`, `pyproject.toml`, `uv.lock` are frozen).
- sdist note (strategic fact, verified in `pyproject.toml`): the sdist
  whitelist INCLUDES `tests/` and EXCLUDES `scripts/` (top-level exclusion).
  D1's script fix therefore does not change the sdist; D1's NEW TEST FILE and
  D2's generator/test/manifest changes DO. A fresh `uv build` at W5's tree
  must reproduce `M_W5`'s recorded hashes byte-for-byte.

## Bounded scope (workstreams)

### D1 — Fix the digest capture in `scripts/release_registry_publish.py`
(minimal, behavior-preserving)

UNFREEZE (for this round ONLY, precisely): `scripts/release_registry_publish.py`
and one NEW test file `tests/test_release_registry_publish_digest.py`.
NO other file in `scripts/`. Required changes:

1. Add a pure, deterministic, side-effect-free parser (module level, importable
   and unit-testable without docker or network):
   ```python
   PUSH_DIGEST_LINE_RE = re.compile(
       r"^(?:[^ ]+:\s+)?digest:\s?sha256:([0-9a-f]{64})(?:\s+size:\d+)?\s*$"
   )

   def extract_push_digest(output: str) -> str | None:
       """Return the sha256 digest from docker push output, or None.

       Accepts the final digest line in the two observed docker-CLI forms:
       '<ref>: digest:sha256:<64-hex> size:<n>' (current CLI, non-TTY) and
       the legacy bare 'digest: sha256:<64-hex>' / 'digest:sha256:<64-hex>'.
       Scans all lines (str.splitlines); returns the LAST match's digest.
       """
   ```
   (Exact code at the implementer's discretion provided the observable
   contract is exactly this: last-match wins; both forms; None when no line
   matches.)
2. Rewrite `_push_digest(ref)` ONLY as: run the push via `_docker` (unchanged
   check semantics); combine `proc.stdout.decode()` and `proc.stderr.decode()`
   (stdout first, then stderr, single joined text); call
   `extract_push_digest`; on `None`, raise `PublishError` whose message names
   the ref AND includes the LAST 25 non-empty lines of the joined output with
   the value of environment variable `SLAIF_GHCR_TOKEN` (when set and
   non-empty) replaced by `***` in every line (defense-in-depth redaction;
   docker push output contains no secrets, the redaction is a guard, and the
   redaction itself must be unit-tested).
3. NOTHING else changes in the script: the publish sequence (sha-tag push →
   registry-API cross-check → 0.1.0 no-silent-repoint guard → release-tag
   push → final two-tag verification → `SLAIF_PUBLISHED_DIGEST` /
   `GITHUB_OUTPUT` emission), the reference builders, `--self-check-refs`, and
   all argument handling remain byte-identical (a module-docstring line may
   note the fix if the current text would otherwise be false).
4. `tests/test_release_registry_publish_digest.py` (deterministic; no docker,
   no network, no host state; import the module from `scripts/`):
   - full realistic non-TTY push transcript (banner + ≥3 layer progress lines
     + final `<ref>: digest:sha256:<64-hex> size:<n>`) → returns the digest;
   - legacy bare `digest: sha256:<64-hex>` and `digest:sha256:<64-hex>` forms
     → digest;
   - output with multiple candidate lines → LAST match wins;
   - output with no digest line → None;
   - malformed digest (short/long/non-hex) → None;
   - failure path (monkeypatch `_docker` to return a fake
     `CompletedProcess` with no digest line + set a sentinel
     `SLAIF_GHCR_TOKEN` env value): raised `PublishError` message contains the
     output tail and does NOT contain the sentinel token value;
   - `self_check_references()` still returns 0 (the 013-c self-check contract
     unchanged).
5. Local proof before commit: `ruff check`, `ruff format --check`, mypy
   (CI-equivalent), full `pytest -q` all green at the W5 tree;
   `python3 scripts/release_registry_publish.py --self-check-refs` green.

### D2 — Generator/E3 objective bump and manifest `M_W5`

- `scripts/release_provenance_manifest.py`: `OBJECTIVE` → `"013-e"` (plus the
  docstring order reference, same pattern as 013-d).
- `tests/test_release_provenance_manifest.py`: E3 objective assertion →
  `"013-e"`.
- Regenerate `packaging/release_provenance_manifest.json` → `M_W5` at W5's
  tree, NOT-YET-PUBLISHED state: `objective "013-e"`; `oci.published: false`;
  `oci.image_digest: null`; no `release` key; `status.released: false`;
  `gateway_peer.commit = 08ca421bee1ddca62078302b910e8be88cf705be` (FROZEN,
  unchanged); `artifacts.wheel.sha256 = oci.wheel_sha256 = H_new` (unchanged);
  `artifacts.sdist.sha256` = the fresh `uv build` sdist hash at W5's tree
  (NEW value — the new test file is an sdist input);
  `generated_from.git_commit = 59439963a02e8cd6c341708e606f907ef1e6771d`
  (= R, W5's parent).
- W5 file set (EXACTLY): the D1 script, the D1 new test file, the D2
  generator, the D2 test assertion, `packaging/release_provenance_manifest.json`,
  plus this order file (`oap/orders/013-e-…md`, strategic-authored bytes
  verbatim) and `oap/active` → `013-e`. NO other file. In particular: NO
  `release-image.yml` change (the mechanism is proven; byte-identical), NO
  `ci.yml`, NO `docs/` in W5.

### D3 — The ONE controlled publication at `W5`

- CI at W5 FULLY GREEN 4/4 (`test`, `gateway-contract`, `docker`,
  `docker-published` on the explicit not-yet-published skip path) BEFORE any
  dispatch. The `docker` job must show all 15 qualification phases PASSED.
- Pre-dispatch anonymous registry probe (token NOT in the environment;
  `scripts/ghcr_tag_check.py`): `0.1.0` → record (expect `absent`);
  `sha-<W5>` → record (expect denied/absent — the package is non-public;
  record the exact probe output).
- Verify branch tip = W5 (`git ls-remote`) immediately before dispatching.
- EXACTLY ONE dispatch: `gh workflow run release-image.yml --ref
  oap/013-mvp-release-publication` (branch tip = W5 at dispatch time).
- Classify and report EACH layer separately (do not collapse them), same
  eight layers as 013-d C6: (1) workflow start + checkout; (2) wheel-binding
  assert (fresh wheel == `H_new`); (3) image build (two-file compose,
  `mvp-release-0.1.0` label); (4) GHCR authentication success (GITHUB_TOKEN
  login); (5) GHCR authorization + image upload success (no
  scope/permission denial); (6) in-script registry verification: BOTH tags
  `0.1.0` and `sha-<W5>` resolve to ONE digest `D` (no-silent-repoint guard
  respected) — layer 6 is expected to PASS with the D1 fix; (7) package
  visibility / anonymous pullability per D5; (8) capture `D`
  (`sha256:<64-hex>`) + the workflow run id; then INDEPENDENT anonymous
  re-verification: `0.1.0` → `D` and `sha-<W5>` → `D`.
- Failure law (inherited verbatim from 013-d C6): if the run FAILS, report
  the exact failing layer with the raw log lines (the D1 fix now makes the
  push output tail available in the error); do NOT re-dispatch for an
  authorization/permission-class failure (strategy re-adjudicates with the
  primary evidence — a genuine org-policy boundary would then be a human
  decision with ONE precise choice); ONE deterministic re-dispatch is
  permitted ONLY for a transient-infrastructure failure (e.g., runner error
  before any registry interaction); a second failure of any kind → STOP and
  report. Partial registry state (tag written, verification failed) → STOP
  and report (orphan cleanup is a strategic act; no silent repoint).

### D4 — Registry-state continuity (normative; record, do not mutate)

- The pre-existing `sha-be3c78b…` tag (the W4-built image, digest D1) and its
  registry version are NOT touched by the W5 dispatch: the W5 run writes the
  NEW tag `sha-<W5>` (unconditionally, content-addressed to the W5 build) and
  `0.1.0` (absent → first write). NO existing tag is repointed under any
  branch of this design; record this in the report.
- Build-reproducibility note (factual): W5 changes no build-context path
  (`Dockerfile`, `.dockerignore`, `src/`, `pyproject.toml`, `uv.lock`,
  `LICENSE`, `NOTICE`, `README.md` — prove: `git diff --name-only
  be3c78b2016d5d40ce9155df8f94d14525c43d39..W5` intersects the build-context
  set in NOTHING), so the W5-built image is wheel- and layer-identical to the
  W4-built image modulo the per-build `org.opencontainers.image.revision`
  label (W5 vs W4) and any per-build tar-mtime nondeterminism. If the W5
  content digest `D` differs from D1, that is EXPECTED and acceptable: the
  release identity is `D` under the tags `0.1.0` + `sha-<W5>` as recorded at
  P; D1 remains an unreferenced private version (harmless; deletion is NOT
  authorized and NOT required). If `D == D1`, record the reproducibility
  observation.
- The release record's `image_source_commit` is W5 and the in-image revision
  label is W5 (the dispatch runs at W5; `SLAIF_GIT_SHA` = GITHUB_SHA = W5) —
  the S/P/D binding is exact: the published image is built from W5's tree.

### D5 — Package visibility (layer 7), ONLY after a successful D3 push

- After the script-verified two-tag success, run anonymous probes (token NOT
  in the environment) of BOTH tags: `0.1.0` and `sha-<W5>`.
- Branch A (both anonymously resolvable to `D`): layer 7 PASSED; proceed to
  D6.
- Branch B (either not anonymously resolvable — EXPECTED: the package is
  non-public):
  1. Attempt EXACTLY ONE visibility API call with the wrapper's existing `gh`
     credential: `PATCH /orgs/ulfe-lmi/packages/container/slaif-local-coding`
     with body `{"visibility":"public"}`. Record the HTTP status + body
     verbatim (NO credential value anywhere).
  2. If the call SUCCEEDS (2xx): re-run the anonymous probes of BOTH tags;
     both must resolve to `D`. Record the state change exactly (before:
     non-public/401; after: public/200 + digest). Proceed to D6.
  3. If the call FAILS (expected 403 "need at least read:packages scope" or
     401/404 — a credential-scope boundary, NOT an org-policy decision):
     layer 7 = **HUMAN UI ACT REQUIRED**. STOP the round here with a
     BLOCKED-at-D5 report: capture `D`, the run id, layers 1–6 PASSED
     (raw-log evidence), layer 7 blocked with the verbatim API response, and
     the EXACT human act: GitHub UI — organization `ulfe-lmi` → Packages →
     `slaif-local-coding` (container) → package visibility → public — OR an
     API PATCH performed with a credential holding the packages scope. State
     the post-act verification (anonymous resolution of both tags → `D`) and
     that the follow-up round then completes D6 (P) + D7 (report at P). Do
     NOT create `P` in this branch (the anonymous `docker-published` gate
     cannot pass while the package is non-public). No other work after the
     report; NO second API attempt; NO workaround.

### D6 — Release-record commit `P` (child of `W5`) — ONLY in D5 branch A/B-2

EXACTLY two files changed:
1. `packaging/release_record.json` (schema `slaif-release-record-v1`, per the
   013-a R1 field set): `git_tag = "v0.1.0"`; `image_source_commit = W5`;
   `oci_image_digest = "sha256:" + D`; `oci_tags = ["0.1.0", "sha-<W5>"]`;
   `published_at` = RFC 3339 UTC of the successful D3 publication run;
   `publication_workflow_run_id` = the D3 run id; plus the remaining
   schema-required fields per the 013-a contract (unchanged semantics).
2. `packaging/release_provenance_manifest.json` → `M_P`: regenerated from W5's
   tree with the record present (generator's published state): `objective
   "013-e"`; `oci.published = true`; `oci.image_digest = "sha256:" + D`;
   `status.released = true`; `release.git_tag_target = W5`;
   `generated_from.git_commit = W5`; `gateway_peer.commit =
   08ca421bee1ddca62078302b910e8be88cf705be` (frozen); artifact hashes
   (wheel `H_new`, sdist = `M_W5`'s sdist hash) UNCHANGED from `M_W5`.
`P` changes NO other file.

### D7 — CI at `P` (FIRST EXECUTED `docker-published`) and report `R` — ONLY in D5 branch A/B-2

- CI at P FULLY GREEN, including the **EXECUTED** `docker-published` job
  (its first-ever execution — a green pre-publication CI where
  `docker-published` follows the explicit not-yet-published skip path is NOT
  release evidence; this execution against the real registry image IS the
  release evidence): pull by digest `D` and by both tags (anonymous — this
  also mechanically re-proves the D5 visibility semantics), each resolving to
  `D`; registry-API cross-check; OCI label set verified against the
  record/manifest (revision == W5; version `0.1.0`;
  `slaif-local-coding.gateway.peer.sha == 08ca421…`; wheel == `H_new`;
  qualification `mvp-release-0.1.0`; topology unchanged); the PULL-BASED
  compose (primary file only, `SLAIF_LOCAL_CODING_IMAGE` digest-pinned, NO
  `build` key) against the disposable fake upstream on canonical port 18031:
  readiness healthy; representative signed request succeeds; negative
  contract cases fail closed; missing-secret readiness fail-closed;
  NO-BUILD proof (image exists locally only via pull; running container image
  ID == pulled image ID); teardown absence proof.
  - **Narrow gate-defect exception (inherited from 013-c C8 / 013-d C8):**
    ONLY IF the first execution fails due to a defect in the never-executed
    gate itself, a MINIMAL fix to `.github/workflows/ci.yml` and/or
    `scripts/docker_qualification_ci.py` is authorized within this round as a
    documented deviation, provided it removes, skips, or weakens NO
    011/012/013 qualification semantics. Any other cause → report and stop.
- Post-publication documentation truthfulness (verification duty, ONLY in
  this branch; NO doc changes in this round): the 013-d C4 statements were
  written to remain true at the post-publication state (publication = the
  dispatch-only release workflow executed at this PR's implementation head
  W5; the release record present from the release-record commit P onward;
  digest/tags by path reference only; the Git tag `v0.1.0` and the GitHub
  Release = strategy post-merge acts that do not exist; cutover NOT
  performed). At P, verify each current-facing statement (Publication
  section of `docs/RELEASE-ARTIFACT-POLICY.md`, the corresponding
  current-state statement in `docs/DOCKER-INSTALL.md`, the 013 line of
  `docs/IMPLEMENTATION-ROADMAP.md`, and the roadmap/COMPLETENESS current-
  state lines) against the exact P-state facts (zero Git tags, zero GitHub
  Releases verified live) and record the verification in the report. If ANY
  statement is stale at P, record it precisely as a 013-f item — do NOT
  change documentation in this round.
- `P` is the DIRECT child of W5 (no intermediate implementation commit).
- `R` = report-only commit, child of P (first parent = P; or W5 in the D5
  branch-B-3 case, where R is the BLOCKED-at-D5 report and NO `P` exists).

## Identity bindings (normative; 013-a ordering instantiated at 013-e)

- S (image-source commit) = W5 — the tree the D3 dispatch builds from
  (GITHUB_SHA = W5; in-image revision label = W5).
- D = the single digest BOTH published tags resolve to, captured from the
  successful D3 run and re-verified anonymously (layer 8).
- P = the release-record commit (direct child of W5), the first commit
  in which `packaging/release_record.json` exists with non-null digest.
- Git tag `v0.1.0` target (strategy, post-merge) = S = W5.
- `org.opencontainers.image.revision` label = S = W5.
- No circularity: the image is built from S; P records S and D; P ≠ S; the
  tag points at S; the record at P describes S+D truthfully.

## Explicit non-goals (all 013-a/013-b/013-c/013-d non-goals inherited, plus)

- NO changes to: `src/`, `pyproject.toml`, `uv.lock`, `config/`, `Dockerfile`,
  `.dockerignore`, `compose.yaml`, `compose.build.yaml`,
  `.github/workflows/ci.yml` (except the narrow D7 gate-defect exception),
  `.github/workflows/release-image.yml` (BYTE-IDENTICAL this round — the
  mechanism is proven; any needed change is a later re-adjudication),
  `scripts/ghcr_tag_check.py`, the gateway-contract gate/fixture,
  `oap/orders/*`, `oap/reports/*` (immutable), or any `docs/` site beyond the
  D7 minimal post-publication set (and none at all in the D5-blocked branch).
- NO behavioral change to the publish script beyond D1 items 1–2 (the
  sequence, guards, and output contract are byte-identical).
- NO protected-host mutation (Qwen/18020, `qwen-serving` units, model/
  checkpoint/patches/venv/systemd/launch flags, API keys, firewall/VPN/
  network bindings, active Codex profiles); NO docker build/run/up on the
  protected host (CI runners only); NO live cutover; NO Qwen/protected-model
  inference.
- NO Gateway-repository mutation (read-only verification only; peer remains
  `08ca421…`; the fixture is NOT re-pinned).
- NO Git tag / GitHub Release by coding (strategy post-merge acts).
- NO repository Actions/security setting change (the
  `default_workflow_permissions` setting stays as-is; the 013-d correction
  record explains why no change is needed).
- NO new credentials; NO re-provisioning of any repository secret; NO
  credential-scope change; NO second visibility API attempt.
- NO registry publication other than the single authorized D3 dispatch
  (which writes `sha-<W5>` + `0.1.0`); NO repoint of any pre-existing tag; NO
  package/version deletion (orphan cleanup is a strategic act).
- NO re-dispatch except the single transient-infrastructure exception of D3.
- NO version change (stays `0.1.0`).

## Required evidence (report)

- Per-workstream status with exact evidence (D1 test names + counts + output;
  D2 fresh `uv build` at W5 reproducing `M_W5` hashes byte-for-byte (wheel =
  `H_new`; sdist = new hash) + `artifact_policy_check.py --inspect` +
  `--install-smoke` on the fresh build; D3 layer classification 1–8 with raw
  log lines (including, at layer 6, the parsed digest line); D4
  no-build-context-change proof + tag-non-repoint record + D1-vs-D
  reproducibility observation; D5 branch taken with the verbatim API
  response (or the anonymous probe outputs for branch A); D6 exact two-file
  proof + field values; D7 the EXECUTED `docker-published` phase summary).
- CI runs at W5 and (if created) P: full job/conclusion lists; the `docker`
  job's 15-phase PASSED summary at W5.
- Registry state before (pre-dispatch probes) and after (layer-8 anonymous
  re-verification + post-round probes), token-free.
- Protected-host before/after read-only probe table (identical to the 013-d
  baseline unless a protected resource moved — if it did, STOP and report).
- Grep proofs: NO `secrets.SLAIF_GHCR_TOKEN` anywhere in active files (the
  only repository matches may be the immutable OAP transcripts and this
  order's text); the workflow's only `secrets.` references are
  `secrets.GITHUB_TOKEN`.
- Gateway freeze re-verification at round time: the three contract blob SHAs
  at `08ca421…` and at current Gateway `main` (record the new main SHA if it
  moved beyond `1bdbb8bf…`; blob identity required at BOTH; the strict gate
  18/18 against the frozen peer, network guard enabled).
- 013-a R1–R20 re-affirmation at the round's final state (with R12 now
  SATISFIED if D3 succeeded; R13 SATISFIED by the EXECUTED gate in the D6
  branch; R1 SATISFIED at P in the D6 branch).
- Safety/scope confirmations (standard set), known limitations/blockers, and
  the exact post-merge strategy acts remaining (visibility human act if D5
  branch B-3; else Git tag `v0.1.0` → W5 + GitHub Release).

## Report contract

- Path: `oap/reports/013-e-fix-publish-verification-and-complete-publication.md`.
- Report-only SELF commit; first parent = P (D6 branch) or W5 (D5-blocked
  branch); `Implementation head SHA` = W5 in both branches.
- Status: COMPLETE (D6 branch) or BLOCKED (D5 branch B-3, with the exact
  human act) — a D3 run failure is reported with the failing layer per the
  D3 failure law.
- After publishing the report commit and verifying it remotely (PR head = R,
  report-only, parent verified), send exactly two bytes `OK` to
  `response.fifo`.

## Safety/scope (restated)

Routine terminal/setup belongs to coding. The protected live-host boundary is
absolute. No human/strategy recruitment for routine work. No merge by coding.
No auto-merge. One numeric objective = one PR: this round amends PR #15 only.

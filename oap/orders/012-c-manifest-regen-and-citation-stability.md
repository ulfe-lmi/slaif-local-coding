# OAP Work Order — 012-c: Regenerate the release-provenance manifest at the final state and make artifact-hash documentation citations stable

## Objective

Resolve the 012-b D6 blocking fact (the E3 manifest self-consistency gate
fails deterministically because R1–R3 edited sdist-carrying `docs/` files
while the 012-b order froze the manifest) by regenerating
`packaging/release_provenance_manifest.json` from the final implementation
state, and by making the artifact-hash statements in the current-facing docs
self-reference-stable (no document may cite the CURRENT sdist hash or the
current manifest `objective` field, because the sdist embeds `README.md`,
`docs/`, and `tests/` and therefore its hash changes with any in-scope text
edit, and the `objective` field records the producing round). After this
round, CI must be green at the implementation head and the report head, and
every 012 criterion (012-a as re-adjudicated by strategy, 012-b D1–D3/D5/D7/D8,
and this round's items) is satisfied on one PR (#14).

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`
- Numeric objective: `012`; round: `012-c`
- PR mode: `AMEND_EXISTING_PR`
- Existing PR: #14 — https://github.com/ulfe-lmi/slaif-local-coding/pull/14
  (OPEN, non-draft; exactly the Objective-012 PR)
- Base: `main` @ `e860e0bff687afded7782fb2687b5b435792459a`
- Branch (required, unchanged): `oap/012-gateway-peer-repin`
- Current head at order time:
  `1c6c6b39e0d651d784511f9cd0e15101f99e8483` (012-b report commit);
  prior implementation head: `c384150cbc83c8c5d463b6b855fe20a5fe11a746`
- Verified at order time: at `c384150` CI run 35182393796 — `test`
  FAILURE (single E3-gate assertion `test_committed_manifest_matches_regenerated`:
  committed sdist `910b65db…` vs regenerated `0cf2429079b9a68e9e9920134b55771c2aa2c7bef53a662e953d7c1b6676fcbe`,
  425800 B, 105 entries; wheel `fceadc37…` matched), `gateway-contract`
  SUCCESS, `docker` SUCCESS. Report-head run 35182846809 same pattern.

## Strategic context and independently verified current state

1. The 012-b report is `PARTIAL` with exactly one blocking fact and
  identifies the internal contradiction in the 012-b order (frozen-manifest
  non-goal vs D6 CI-green requirement). Strategic independently verified the
  root cause against the CI log and the build configuration:
   - `pyproject.toml` sdist target carries `README.md`, `docs/`, `tests/`
     (009 artifact policy, deliberate); the wheel embeds `README.md` via
     `readme = "README.md"`.
   - R1–R3 modified three `docs/` files => any rebuild at or after
     `c384150` produces sdist `0cf24290…` (CI-observed), never
     `910b65db…`.
   - The E3 gate
     (`tests/test_release_provenance_manifest.py::test_committed_manifest_matches_regenerated`)
     re-derives the manifest from the repository state and asserts equality;
     it is an accepted 009/011 mechanism and MUST NOT be weakened or
     bypassed.
2. **Strategic re-adjudication (authority recorded):** the 012-b non-goal
   "NO new artifact build or hash change (the manifest keeps
   `fceadc37…` / `910b65db…`)" is WITHDRAWN as over-specified — it
   did not account for the sdist carrying `docs/` while the ordered doc
   edits were sdist build inputs. The withdrawal is bounded:
   - the WHEEL (the single supported distributable and the cutover
     authority wheel) MUST remain exactly
     `fceadc378130dd4ffcc3f75d17b5e098577652914f541245d31247911be23aeb`
     (83097 B) — this round changes no wheel input (no `README.md`, `src/`,
     `pyproject.toml` change);
   - the SDIST is developer-only (not a supported release artifact, per
     docs/RELEASE-ARTIFACT-POLICY.md); its record in the manifest advances
     to the hash derived from the final state (the CI-observed value at
     `c384150` was `0cf24290…`; the final value is whatever the clean
     rebuild at the FINAL state produces after this round's own doc edits);
   - the regenerated manifest remains the only future cutover authority;
     historical records (011-a: `7cede0b8…`/`4ba17680…`; 012-a state:
     `fceadc37…`/`910b65db…`) remain historical only.
3. **Citation-stability defect (why docs must be touched again):** the
   012-b R1/R3 text cites the sdist hash `910b65db…` and the manifest
   `objective: "012-a"` as if current — self-referential statements that
   are false as soon as this round regenerates the manifest. The stable
   design (directed below): documents may cite (a) the wheel hash exactly
   (stable — no wheel inputs change from here on in this objective),
   (b) historical artifact records explicitly labeled as historical,
   (c) the current manifest by path + schema name. Documents MUST NOT
   cite the current sdist hash or the current `objective` field value.

## Bounded scope (exactly six files)

- **T1 — `scripts/release_provenance_manifest.py`:** `OBJECTIVE` constant
  `012-a` -> `012-c` (records the producing round). No other generator
  change.
- **T2 — `tests/test_release_provenance_manifest.py`:** the
  `test_objective_field_records_producing_objective` expectation
  `012-a` -> `012-c`. No other test change; the E3 gate and every
  hash cross-check remain exactly as-is (MUST NOT be weakened).
- **T3 — `docs/RELEASE-ARTIFACT-POLICY.md`:** correct the 012 paragraph
  so it is stable and truthful: keep the exact wheel transition statement
  (`7cede0b8…` -> `fceadc37…`, +27 B, README embedded as METADATA long
  description; all 20 wheel runtime files byte-identical to the 011
  record); replace the CURRENT-sdist-hash citation with the stable policy
  statement: the sdist is developer-only, embeds `README.md`/`docs/`/
  `tests/`, its hash therefore changes with any in-scope text edit, and the
  authoritative current sdist hash is the one recorded in
  `packaging/release_provenance_manifest.json`, mechanically re-derived
  from the final state by
  `test_committed_manifest_matches_regenerated`; cite the two historical
  records explicitly as historical (011-a: wheel `7cede0b8…`/sdist
  `4ba17680…`; 012-a state: wheel `fceadc37…`/sdist `910b65db…`); the
  regenerated Objective-012 manifest (producing round recorded in the
  manifest itself) is the only future cutover authority.
- **T4 — `docs/RELEASE-CUTOVER-RUNBOOK.md`:** Preconditions item 2:
  replace the parenthetical's `the **Objective-012-a regenerated
  manifest** — schema v2, `objective: "012-a"`, …` with the stable form:
  the current `packaging/release_provenance_manifest.json` (schema v2
  `slaif-release-provenance-v2`, produced by Objective 012), with runtime
  source proven byte-identical to the Objective-011-a set (artifact bytes
  differ only via the embedded README METADATA and the sdist-carried
  in-scope text files; see RELEASE-ARTIFACT-POLICY.md). No other runbook
  change.
- **T5 — `docs/IMPLEMENTATION-ROADMAP.md`:** in the "Current state"
  paragraph, replace the parenthetical citing `objective: "012-a"` and the
  sdist hash `910b65db…` with the stable form: regenerated the release
  provenance manifest (the current artifact record is
  `packaging/release_provenance_manifest.json` — wheel
  `fceadc378130dd4ffcc3f75d17b5e098577652914f541245d31247911be23aeb`; the
  sdist is developer-only and its hash is manifest-recorded; per
  `RELEASE-ARTIFACT-POLICY.md`). No other roadmap change.
- **T6 — `packaging/release_provenance_manifest.json`:** regenerated with
  `scripts/release_provenance_manifest.py` from the FINAL implementation
  state (i.e., after T1–T5 are in place). Expected fields: `objective:
  "012-c"`; `artifacts.wheel` unchanged (`fceadc37…`, 83097 B, 26
  entries); `artifacts.sdist` = the clean-rebuild hash at the final state
  (105 entries); `gateway_peer`, labels (incl.
  `slaif-local-coding.wheel.sha256 = fceadc37…`), OCI inputs,
  `reference_compatibility`, `limitations`, status fields
  (`cutover_performed/released/oci.published = false`,
  `oci.image_digest = null`) unchanged except `generated_from.git_commit`
  = the generating commit. The manifest commit MUST be the LAST
  implementation commit of this round (only the report commit may follow),
  so no build input changes after regeneration.

## Explicit non-goals

- NO change to: fixture, Dockerfile, `scripts/cutover_state_machine.py`,
  `tests/test_cutover_state_machine.py`, `src/`, `uv.lock`,
  `pyproject.toml`, CI workflows, `docs/topology.manifest.json`, or any
  other file (the round diff must be exactly T1–T6 + transcripts).
- NO weakening, skipping, or bypassing of
  `test_committed_manifest_matches_regenerated` or any other test.
- NO wheel content change (hash must remain `fceadc37…` — proven by clean
  rebuild).
- NO release/tag/publication, no cutover, no protected-host mutation
  (read-only probes only), no Gateway repo mutation, no OAP history
  rewrite (all `oap/orders/*` and `oap/reports/*` byte-identical; the
  012-a/012-b reports remain immutable history), no OAP expansion, NO
  NEW PR, NO merge.

## Acceptance criteria

- **E1 — Manifest regenerated at final state:** `objective: "012-c"`;
  wheel record exactly `fceadc378130dd4ffcc3f75d17b5e098577652914f541245d31247911be23aeb`
  (83097 B); sdist record equals a clean rebuild from the final state
  (proven by `uv build` + `sha256sum` in the report; 105 entries);
  `test_committed_manifest_matches_regenerated` passes locally AND in CI
  at the final head.
- **E2 — Wheel invariance proven:** clean rebuild at the final head yields
  wheel `fceadc37…` byte-exact; entry-level diff vs the 011 record still
  shows all 20 runtime files identical (METADATA/RECORD only, README-row
  delta).
- **E3 — Citation stability:** at the final head, an exact-phrase audit
  (recorded in the report) shows: no current-facing document cites the
  current sdist hash or the current manifest `objective` field; the
  wheel hash `fceadc37…` may be cited exactly; the values `910b65db…` and
  `objective: "012-a"` appear ONLY as explicitly labeled historical
  records (or not at all in current-facing docs); T4/T5 reference the
  manifest by path + schema.
- **E4 — No other file changed** vs the 012-b implementation head
  `c384150cbc83c8c5d463b6b855fe20a5fe11a746` beyond T1–T6 plus the 012-c
  order/active transcripts and this round's report (verified by diff).
- **E5 — CI green at the implementation head AND the report head:**
  `test` (full suite, E3 gate passing), `gateway-contract` (pinned peer
  `1fccaa746…`), `docker` (wheel-binding to the regenerated manifest,
  label check, content scan, hardening, operations, teardown) — all
  `success`; no failed/cancelled/pending/missing required checks.
- **E6 — 012-b evidence carries:** the report states which 012-b criteria
  (D1–D3, D5, D7, D8) and 012-a criteria (C1, C2, C4, C5, C6, the
  re-adjudicated C3, C8, C9, C10) remain satisfied by the unchanged
  state, and re-runs the cheap verification set at the final head (full
  pytest now fully green, ruff check+format, mypy, compileall, cutover
  self-test, topology self-test, artifact-policy inspect,
  emit-github-output); protected-host before/after re-probe identical.
- **E7 — No publication/mutation** (012-a C9 facts re-verified at report
  time: 0 tags, 0 releases, no image push, gateway main = `1fccaa746…`
  unchanged, no live profile/route/service change).

## Verification and evidence (exact)

- `uv build --out-dir <throwaway>` at the final state + `sha256sum`
  (wheel must equal `fceadc37…`; sdist hash recorded in the regenerated
  manifest and in the report).
- `uv run --frozen pytest -q` fully green at the final head.
- The 012-b D7 command set re-run (record outputs).
- Push, wait for green, publish the 012-c report, signal.

## GitHub publication requirements

- Push implementation commit(s) for T1–T6 to the SAME branch
  `oap/012-gateway-peer-repin` (NO NEW PR); the manifest regeneration
  (T6) is the last implementation commit.
- After CI green: publish
  `oap/reports/012-c-manifest-regen-and-citation-stability.md` as a
  report-only commit (SELF) whose parent is the literal new implementation
  head SHA; push.
- NEVER merge. NEVER enable auto-merge.

## Exact immutable report contract

`oap/reports/012-c-manifest-regen-and-citation-stability.md` must
contain: work order (012-c, AMEND_EXISTING_PR, PR #14); status;
authoritative GitHub state (base, branch, prior implementation head
`c384150…`, new implementation head SHA literal, SELF report commit,
"Merge performed: NO"); T1–T6 diff evidence; E1–E7 evidence (including
the E1/E2 rebuild hashes, the E3 citation-stability audit output, the E5
CI run IDs at both heads, and the E6 re-run outputs); protected-host
before/after table; no-publication verification; safety/scope
confirmations; known limitations. This report supersedes the 012-b
report as the Objective-012 report of record; earlier reports remain
immutable history.


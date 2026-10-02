# OAP 015-b Report — Close immutable registry-history gap and qualify private RC9

## Scope and identity

- Order: `015-b` (`oap/orders/015-b-close-immutable-history-gap-and-qualify-rc9.md`,
  activated byte-exact, sha256
  `1216e976793ab9bd2825e3cd2c4403ead1d1d22d23963cc89bb408968a3d65c5`).
- Repository: `ulfe-lmi/slaif-local-coding`.
- PR mode: `AMEND_EXISTING_PR` — PR #22
  (https://github.com/ulfe-lmi/slaif-local-coding/pull/22), non-draft,
  never merged, auto-merge never enabled.
- Base: `main` at `87ed2cea43a0a8706efe485b9b625dfda7cf75aa`.
- Branch: `oap/015-upstream-diagnostics-compiler-truncation-rc8`.
- Remote head at order start: `40771fd2f3453b90264c44c3f06b745edff58c22`
  (015-a report SELF).
- New commits this round (all on the existing branch):
  1. `09d618f0a6890442b28813daf05c048a208e82e3` — Objective 015-b
     activation transcript (order file + `oap/active`).
  2. `9ee7ae12c8dbf8317c4bac8a97f6a4b1c49553a3` — implementation `A9`
     (CI-history correction, deterministic regression, RC8 archive,
     candidate constants/schemas/workflows/tests/docs reconciled to
     exactly `0.1.0-rc9`).
  3. `7f601bf153ef86a567883c0008edf4ce34e79c95` — image source commit
     `S9` (freeze; pre-freeze provenance manifest; manifest-only diff
     over `A9`).
  4. `231fa6e67a3240dbcc986b27fd7b62cf1c479245` — post-freeze derived
     metadata only (RC9 record + handoff, `rc_published` manifest,
     testing ledger 007). **Exact final implementation SHA (this
     commit).**
- Changed paths (`40771fd…` → `231fa6e…`, 35 files):
  - Correction: `.github/workflows/ci.yml`, `scripts/ghcr_tag_check.py`,
    `tests/test_registry_history_baseline.py` (new).
  - RC8 archive: `packaging/releases/0.1.0-rc8/{rc_record.json,
    rc_handoff.md, release_provenance_manifest.json}` (byte-identical
    move of the top-level files + the S8 manifest copy); top-level
    `packaging/rc_record.json` / `packaging/rc_handoff.md` replaced at
    `B` by the RC9 record/handoff.
  - Candidate constants to `0.1.0-rc9`: `.github/workflows/
    release-image.yml`, `packaging/rc_artifact_record.schema.json`,
    `packaging/release_provenance_manifest.schema.json`, `scripts/
    {docker_qualification_ci,operator_session_ci,rc_artifact_record,
    real_codex_rc_qualification,release_provenance_manifest,
    release_registry_publish}.py`, `tests/test_{compose_pull_canonical,
    docker_qualification_record_gate,rc_record,rc_record_present_
    rehearsal,real_codex_rc_qualification,release_provenance_manifest,
    release_registry_publish_digest,release_registry_publish_gate}.py`.
  - Docs: `TESTING.md`, `docs/HISTORY.md`, `docs/RC-HANDOFF.md`,
    `docs/RELEASE-ARTIFACT-POLICY.md`.
  - Provenance/evidence: `packaging/release_provenance_manifest.json`,
    `oap/evidence/testing-ledger/007/{README.md,MANIFEST.sha256,
    real-codex-rc9-qualification.json}`.
  - Activation: `oap/active`,
    `oap/orders/015-b-close-immutable-history-gap-and-qualify-rc9.md`.
- Pre-existing untracked paths `Local`, `clean`, `unchanged` remained
  untracked, unmodified, and uncommitted throughout.

## The confirmed blocker and the correction

### Blocker (independently confirmed by strategy)

At `40771fd…` the frozen `.github/workflows/ci.yml` registry baseline
claimed (in its comment) to cover the archived RC7 aliases, but its
literal immutable-history tuple stopped at RC5 and omitted the exact
RC7 pair:

```text
0.1.0-rc7
sha-ae6271318627703785f42de57d893c9be3b980c9
```

Because `ci.yml` is a member of the 130-entry frozen source-input map,
the RC8 candidate (`S8`
`718fff301bed0a5ba93b29196cde4d0bcc5d711a`) could not be corrected
post-publication while retaining its source/provenance binding. RC8 is
therefore rejected as the FINAL Objective-015 handoff candidate without
any alteration; its qualification history stands (ledger 006, pulled-
image qualification) and its aliases remain occupied and immutable.

### Correction (workstream C, single source of truth)

1. `scripts/ghcr_tag_check.py` is now the shared single source of truth
   for the read-only registry baseline:
   - `load_archived_rc_records()` strictly loads every
     `packaging/releases/<rc>/rc_record.json` (closed schema set
     `slaif-rc-record-v2`/`slaif-rc-record-v3`, directory/identifier
     agreement, 40-hex source commit, `sha256:<64-hex>` digest, exact
     `[candidate, sha-<source>]` tag pair); any structural violation
     fails closed (`RegistryHistoryError`);
   - `immutable_historical_baseline()` returns the ordered set: the
     pre-RC singletons (`0.1.0`, the two recorded orphan `sha-` tags)
     first, record-only (no archived record exists for them), then
     EVERY archived RC pair — candidate tag and `sha-<source>` tag —
     each bound to its recorded digest. The intentional RC6 absence is
     structural: no `0.1.0-rc6` directory exists and no code path can
     create or reserve one.
2. `.github/workflows/ci.yml` baseline step now consumes
   `immutable_historical_baseline(Path.cwd())` and DIGEST-ASSERTS every
   archived pair at its recorded digest, failing closed (`SystemExit`)
   on absent, unauthorized, ambiguous, or changed registry state. The
   current RC pair is still picked up dynamically from the strict
   `packaging/rc_record.json` in published-state CI (record-only,
   deduped against the historical set). The exact RC7 and RC8 pairs
   are covered with accurate comments. No tag mutation, no credential
   printing, no new permission (ephemeral `packages:read`
   `GITHUB_TOKEN` only).
3. `tests/test_registry_history_baseline.py` (new, 6 tests) is the
   deterministic regression:
   - derives the required historical aliases directly from every
     archived strict record and compares against a pinned 7-record
     inventory (RC1–RC5, RC7, RC8 with exact source/digest values);
   - parses the workflow baseline step (focused parser over the exact
     step) and proves it represents every archived pair, binds each
     pair to its recorded digest, consumes the shared single source of
     truth, and keeps the current pair dynamic (no inline candidate
     tag literal, `rc-candidate-0.1.0-rc9` present);
   - asserts the intentional RC6 absence and its unrepresentability.

### Regression evidence (fails against the 015-a frozen source)

Mechanically replayed in a throwaway clean `git archive` of
`78822ca8f8c58fbc959495d37bdff32e525eb945` (the 015-a final
implementation head; clone cleaned afterwards): **6/6 regression tests
FAIL** against that frozen source, with exactly the expected failure
modes:

- `test_archived_records_match_pinned_inventory` — archive inventory
  drift `['0.1.0-rc8']` (the RC8 archive does not exist pre-015-b);
- `test_workflow_baseline_represents_every_archived_pair` — the
  015-a inline tuple does not represent the RC7 pair (the exact RC7
  omission the order names);
- `test_workflow_baseline_binds_pairs_to_recorded_digests` — the
  015-a shape carries no digest binding to assert;
- `test_rc6_absence_is_intentional_and_unrepresentable` — the
  structural derivation path does not exist in the 015-a source;
- `test_workflow_and_module_share_one_source_of_truth` — "baseline
  step must consume the shared single source of truth
  (scripts/ghcr_tag_check.immutable_historical_baseline)";
- `test_baseline_step_records_current_pair_dynamically` — "inline
  candidate tag literal in the baseline step: 0.1.0-rc1" (the 015-a
  historical set was inlined).

Against the current tree the same suite passes 6/6 at `A9`, `S9`, and
`B` (included in every full local run below).

### Live proof of the corrected baseline

- At `S9` (source round, run 36960052648, docker-published job
  110691536057): the first live execution of the corrected baseline
  digest-asserted every archived pair and succeeded: `0.1.0-rc7` and
  `sha-ae627131…` at `sha256:a3782915da58a403fd0f7991c57f9954b07bfb9377e4730715c0fb7398f901db`
  (D7); `0.1.0-rc8` and
  `sha-718fff301bed0a5ba93b29196cde4d0bcc5d711a` at
  `sha256:50450f4aa26a4da158dc457e0b80b441c69386c201491c6c0150c25d5916e126`
  (D8); RC1–RC5 pairs at their recorded digests; visibility `private`.
- At `B` (published round, run 36961356033, docker-published job
  110695537455): the authenticated baseline explicitly shows RC1–RC5,
  RC7 and RC8 unchanged at their recorded digests AND the current RC9
  pair (`0.1.0-rc9`, `sha-7f601bf153ef86a567883c0008edf4ce34e79c95`)
  at D9 `sha256:54fe19483f00ef6e209b2796786fe27cddd302c6bcf5322821b2192a32884334`;
  visibility `private`.

## RC8 archive (byte-identical, verified against 78822ca)

`packaging/releases/0.1.0-rc8/` (archived under `A9`):

- `rc_record.json` sha256
  `f5f4a64741df9b33fd1bee46e8d1e85e31aa78545fc6b1a56e25c597dd700338`
- `rc_handoff.md` sha256
  `332f4ca84cab62ff7ecacd52c371131d29bf2987ce83795773122f621e6353c5`
- `release_provenance_manifest.json` sha256
  `94bbfedf312230bbcdd101b1d382c99e170cf37c185f12768d1fd12a9ca5ee29`

All three verified byte-identical to the blobs at commit
`78822ca8f8c58fbc959495d37bdff32e525eb945` (mechanical `git cat-file`
comparison). No RC8 alias or digest was rewritten, repointed, or
deleted; no RC6 identity was created; ledger 006 and all earlier
archives/ledgers are byte-for-byte untouched.

## Freeze identities (A9 / S9)

- Implementation commit `A9` =
  `9ee7ae12c8dbf8317c4bac8a97f6a4b1c49553a3`.
- Image source commit `S9` =
  `7f601bf153ef86a567883c0008edf4ce34e79c95` (manifest-only diff over
  `A9`; no artifact input changes after `S9`).
- Wheel `W9 == W8` =
  `eb241dda2e079b29190868108c488edaf98261c84119bfd405070dea98b546b9`
  — PROVEN, not assumed: byte-identical across clean `git archive`
  builds of `A9` under CPython 3.12.3 and 3.12.14 (isolated
  `uv build`, pinned `[build-system].requires`), the local `uv build`
  at `S9`, and the in-workflow CI rebuild (fresh wheel == manifest
  wheel, asserted in run 36960763079). The wheel contains no file that
  changed this round (all changes are workflow/test/docs/scripts
  surfaces), so equality was the expected result; it was
  mechanically verified.
- Sdist (at `S9`) =
  `6353491d3bbe603ba49e19a8af3d7f8664e74f400af07fe53779b26d08d06406`
  (deterministic under both observed interpreters; differs from the
  S8 sdist `2fce6516…` exactly because sdist inputs changed — the
  wheel does not).
- Dependency lock (uv.lock) sha256 =
  `1237cbd179f71b99984c80f927529549f5e61eb705585ef9cf2ab0fa9e26764a`
  (unchanged; `uv lock --check` green).
- Build environment pins: hatchling 1.32.0, packaging 26.3, pathspec
  1.1.1, pluggy 1.6.0, tomlkit 0.15.1, trove-classifiers 2026.6.1.19;
  uv 0.12.5.
- Gateway compatibility authority commit:
  `08ca421bee1ddca62078302b910e8be88cf705be` (unchanged peer).
- Source-input map: 131 entries at `S9` (S8 carried 130). The `S8 → S9`
  delta is exactly as expected: +1 `tests/test_registry_history_
  baseline.py`; 13 rebindings (`.github/workflows/ci.yml`, `docs/
  {HISTORY,RC-HANDOFF,RELEASE-ARTIFACT-POLICY}.md`,
  `packaging/rc_artifact_record.schema.json`, and the 8 corrected
  test files). No wheel/src input changed. Proved with
  `scripts/source_input_map.py`:
  - `--ab A9 S9 --manifest`: OK (131 input files; diff confined to the
    excluded derived manifest);
  - `--ab A9 B --manifest`: OK (post-publication derived metadata only);
  - `--ref S9 --manifest`: ref carries exactly the recorded map.
- Manifest: `packaging/release_provenance_manifest.json` regenerated
  from a clean `git archive` of `A9` (`generated_from.git_commit` =
  `A9`, objective `015-b`, state `pre_freeze` at `S9`); the `B`
  regeneration is the exact `rc_published` state transition (state,
  published flag, digest, qualification label, tag convention,
  limitations wording; map and `generated_from` unchanged).

## Local verification (exact commands and states)

At `A9` (pre-freeze, before the S9 manifest regeneration):

- `uv lock --check`, `uv run --frozen ruff check .`, `uv run --frozen
  ruff format --check .`, `uv run --frozen mypy src tests`,
  `scripts/docs_consistency_check.py`, `python -m compileall -q src
  tests oap/bin scripts`, `bash -n oap/bin/*.sh packaging/*.sh`: all
  green.
- `uv run --frozen pytest -q`: 1500 passed, 27 skipped, 6 failed — the
  6 failures are EXACTLY the committed-manifest binding tests
  (`test_release_provenance_manifest.py` ×5, `test_source_input_
  binding.py::test_real_repo_source_inputs_bound_to_committed_source`)
  failing because the committed manifest still carried the 015-a RC8
  `rc_published` state against the new `A9` inputs. This is the
  expected pre-freeze condition (identical to the 015-a situation at
  its implementation commit, where the manifest was likewise
  regenerated at the freeze commit) and every one of them passed at
  `S9` after the manifest-only freeze commit.
- `uv build`: wheel == `W9 == W8`; `scripts/artifact_policy_check.py
  --dist dist --inspect` and `--install-smoke`: both ok, 0
  violations.
- `tests/test_registry_history_baseline.py`: 6/6 PASSED.

At `S9` (pre-freeze state, post-manifest-regeneration):

- `uv run --frozen pytest -q`: **1506 passed, 27 skipped, 0 failed**
  (3.5 min).
- `uv lock --check`, `ruff check`, `ruff format --check`, `mypy src
  tests`, `docs_consistency_check.py`, compileall, shell syntax: all
  green.
- `rc_record_present_rehearsal.py` (PRE mode at `S9`): PASSED
  (disposable clean `git archive` rebuild → wheel == `W9`; synthetic
  record gate set).
- `uv build` at `S9`: wheel == `W9 == W8` (byte-identical).

At `B` (final implementation head, record present):

- `uv run --frozen pytest -q`: **1507 passed, 26 skipped, 0 failed**
  (2.9 min; the one delta vs `S9` is the pre-publication record-
  present test becoming active in POST mode).
- `uv lock --check`, `uv run --frozen ruff check .`, `uv run --frozen
  ruff format --check .` (451 files), `uv run --frozen mypy src
  tests`, `docs_consistency_check.py` (19 claim docs), compileall,
  shell syntax: all green.
- `rc_record_present_rehearsal.py` (POST mode at `B`): PASSED (real
  record identity bindings at source `231fa6e…`).

## Fresh CI/CodeQL at source head S9 (before any registry write)

- CI run `36960052648`
  (https://github.com/ulfe-lmi/slaif-local-coding/actions/runs/36960052648,
  pull_request, head `7f601bf153ef…`): **SUCCESS** (2026-10-02T
  03:24:45Z → 03:27:25Z) —
  - `test` SUCCESS (job 110691536048): 1505 passed, 28 skipped on the
    runner (the single delta vs local is the host-pinned
    `test_target_semantic_preflight_failure_precedes_protected_
    selection`, honestly SKIPPED on the runner);
  - `docker` SUCCESS (job 110691535963): build mode, all 15 phases
    PASSED (adapter_stack_up, bridge_negative_contract,
    bridge_positive_signed, compose_merge_equivalence,
    compose_rendered_validation, config_time_rejection,
    fail_closed_readiness, fake_upstream_start,
    hardening_and_labels, image_build, image_content_scan,
    in_image_provenance,
    operations_stop_start_recreate_upgrade_rollback,
    teardown_absence_proof, verify_wheel_binding);
  - `docker-published` SUCCESS (job 110691536057): source mode; the
    corrected read-only baseline digest-asserted every archived pair
    (RC7 at D7, RC8 at D8, RC1–RC5 at their recorded digests) and
    recorded visibility `private`;
  - `gateway-contract` SUCCESS (job 110691536064); `operator-session`
    SUCCESS (job 110691535911).
- CodeQL run `36960049598`
  (https://github.com/ulfe-lmi/slaif-local-coding/actions/runs/36960049598,
  head `7f601bf153ef…`): **SUCCESS**.

Only after both were fully green was the publication dispatched.

## Private RC9 publication (workflow_dispatch from exact S9)

- Run `36960763079`
  (https://github.com/ulfe-lmi/slaif-local-coding/actions/runs/36960763079,
  `release-image.yml`, workflow_dispatch, head `S9` =
  `7f601bf153ef86a567883c0008edf4ce34e79c95` — the dispatch ref was
  the branch whose remote head was exactly `S9`; created
  2026-10-02T03:34:23Z, completed 2026-10-02T03:35:29Z, **SUCCESS**):
  - checkout/head verified at `S9`; in-workflow fresh wheel rebuilt
    and asserted equal to the committed manifest wheel (both
    `eb241dda2e079b29190868108c488edaf98261c84119bfd405070dea98b546b9`);
  - authenticated strict pre-mutation check: `registry before:
    sha-7f601bf153ef86a567883c0008edf4ce34e79c95 = verified absent;
    0.1.0-rc9 = verified absent` (the only write precondition —
    collision-safe);
  - single push; `registry after:` BOTH tags present at ONE digest.
- **Digest `D9` =
  `sha256:54fe19483f00ef6e209b2796786fe27cddd302c6bcf5322821b2192a32884334`**;
  tags `0.1.0-rc9` and
  `sha-7f601bf153ef86a567883c0008edf4ce34e79c95` both resolve to
  `D9` (registry API, post-write).
- `published_at` = `2026-10-02T03:35:07Z` (final authenticated
  post-write verification line).
- No historical identity, alias, or visibility was touched by the
  run (private visibility re-asserted by the `B`-head baseline;
  pre-RC singletons and RC1–RC5/RC7/RC8 pairs unchanged at their
  recorded digests).

## Pulled-image qualification of the actual D9 (final head B)

Final-head CI `36961356033`
(https://github.com/ulfe-lmi/slaif-local-coding/actions/runs/36961356033,
head `231fa6e…`): **SUCCESS** — `docker-published` (job 110695537455)
ran in **published** mode and passed ALL 13 phases (adapter_stack_up,
bridge_negative_contract, bridge_positive_signed,
compose_rendered_validation, config_time_rejection,
fail_closed_readiness, fake_upstream_start, hardening_and_labels,
image_content_scan, in_image_provenance, pull_preexistence_no_build,
teardown_absence_proof, verify_wheel_binding):

- actually PULLED `D9` by digest (`docker pull
  ghcr.io/ulfe-lmi/slaif-local-coding@sha256:54fe1948…`) — no rebuild
  (`pull_preexistence_no_build` PASSED;
  `canonical_compose_build_key_absent: true`);
- pulled by both tags and asserted each resolves to the recorded
  digest; in-image wheel binding == `W9 == W8`;
- image id of the pulled image
  `sha256:15c661fcfaaec9f58f3dd56f5a074ad49b8a1f0d3fa018319e44a8eb3051c6f8`
  (identical to the published image built in run 36960763079);
- signed-ingress contract run over the loopback port 18031 with the
  fake upstream (no protected backend involved); fail-closed
  readiness; hardening/labels; content scan; lifecycle
  stop/start/recreate; teardown absence proof.

Its authenticated read-only baseline explicitly showed RC1–RC5, RC7
and RC8 pairs unchanged at D1–D5/D7/D8 and the current RC9 pair at
D9, visibility `private` (see "Live proof of the corrected baseline"
above).

## Record, handoff, and provenance (commit B)

- `packaging/rc_record.json` (schema `slaif-rc-record-v3`, 24 keys)
  generated from authenticated facts:
  - `rc_identifier` `0.1.0-rc9`; `image_source_commit` `S9`;
    `workflow_head_sha` `S9` (dispatch ref == branch head == `S9`);
  - `oci_image_digest` `D9`; `oci_tags` `[0.1.0-rc9,
    sha-7f601bf153ef86a567883c0008edf4ce34e79c95]`;
  - `wheel_sha256` `W9 == W8`; `dependency_lock_sha256`
    `1237cbd1…`; build environment pins; base image digests;
    `image_platform` `linux/amd64`;
  - `publication_workflow` `release-image.yml`;
    `publication_workflow_run_id` `36960763079`; `published_at`
    `2026-10-02T03:35:07Z`;
  - `gateway_authority_sha` `08ca421b…`; `source_input_hashes` (131
    entries) equal to the recorded map;
  - `private_registry_auth_required` true; `final_public_release`
    false; `cutover_performed` false;
  - `compatibility` derived mechanically from the manifest-verified
    ledger 007 facts (VISION/CACHE/BOTH arm verdicts `pass`, client
    `0.149.0`/`bbc3341e…`, standalone no-Gateway topology).
- `packaging/rc_handoff.md`: deterministic render of the record
  (all handoff fields present).
- `packaging/release_provenance_manifest.json` regenerated in
  `rc_published` state: objective `015-b`, `generated_from` = `A9`
  (unchanged from `S9`), 131-entry source-input map unchanged,
  `rc_published: true`, digest `D9`, `final_public_release: false`,
  `cutover_performed: false`; diff vs `S9` is exactly the state
  transition.

## Testing ledger 007 (genuine Codex 0.149.0, no Gateway)

`oap/evidence/testing-ledger/007/` (new; ledger 006 byte-for-byte
untouched):

- Subject client: Codex CLI **0.149.0**
  (`bbc3341e44c9ead340ed9570c17be936e37870f570751a941699ffd04d672827`),
  exact pinned version + hash enforced by the gate.
- Topology: disposable Codex home/repository → `127.0.0.1:18031`
  disposable adapter (exact `W9` wheel, binding asserted `equal`) →
  existing protected backend; **no SLAIF API Gateway** (gateway
  ingress disabled; no signed Gateway headers).
- Overall verdict **PASS** (facts created 2026-10-02T03:24:58Z):
  - **VISION** PASS — attempts 1, exit 0, sentinel present (3 bytes),
    1 genuine tool interaction, adapter 200/500/422 = 2/0/0, upstream
    failures 0, compiler calls 0, cache entries 0, 4 s, failure class
    `none` (one-image `retain_newest` route policy exercised).
  - **CACHE** PASS — attempts 1, exit 0, sentinel present (3 bytes),
    1 genuine tool interaction, adapter 200/500/422 = 2/0/0, upstream
    failures 0, compiler calls 1, cache entries 1, 34 s, failure
    class `none` (full constitutional/compiler/derived-cache path
    with measurable treatment evidence).
  - **BOTH** PASS — attempts 1, exit 0, sentinel present (3 bytes),
    2 genuine tool interactions, adapter 200/500/422 = 3/0/0,
    upstream failures 0, compiler calls 1, cache entries 1, 36 s,
    failure class `none` (both mechanisms enabled, same static
    identity).
  - **DIRECT** PASS (contextual control, never a substitute) —
    attempts 1, exit 0, sentinel present (3 bytes), 1 genuine tool
    interaction, adapter 200/500/422 = 0/0/0, upstream failures 0,
    5 s, failure class `none`.
- Mechanical ceilings enforced and stayed below limit: arms 4 ≤ 4,
  tool interactions 2/arm ≤ 8, adapter requests ≤ 64, compiler calls
  ≤ 4, per-attempt output cap 1048576 bytes, per-attempt 600 s, total
  5400 s, attempts ≤ 2.
- `protected_state_unchanged: true` (1 protected file checked, 0
  changed; units unchanged; 18020 held exactly one listener; 18031
  free before and after), `disposable_state_removed: true`.
- Privacy: fixed synthetic prompt over stdin (no prompt substring in
  any argv); backend URL via a mode-0600 caller-owned file reference
  (the path, never the URL, in argv); sanitized closed-schema facts
  only — no prompt, source, tool output, body, image, credential,
  private URL, or session ID in the record.
- `MANIFEST.sha256` covers exactly the ledger directory (manifest
  itself excepted, per the ledger 001/002 convention).

## GitHub CI/CodeQL at final head B

- CI run `36961356033`
  (https://github.com/ulfe-lmi/slaif-local-coding/actions/runs/36961356033,
  pull_request, head `231fa6e…`): **SUCCESS** —
  - `test` SUCCESS (job 110695537541): 1506 passed, 27 skipped on the
    runner (single delta vs local: the host-pinned
    `test_target_semantic_preflight_failure_precedes_protected_
    selection` honestly SKIPPED on the runner);
  - `docker` SUCCESS (job 110695538005): build mode, 15/15 phases
    PASSED;
  - `docker-published` SUCCESS (job 110695537455): published mode,
    13/13 phases PASSED, pulled `D9` without rebuilding (see above);
  - `gateway-contract` SUCCESS (job 110695537450); `operator-session`
    SUCCESS (job 110695537340).
- CodeQL run `36961353714`
  (https://github.com/ulfe-lmi/slaif-local-coding/actions/runs/36961353714,
  head `231fa6e…`): **SUCCESS**.

## Source / artifact / registry identities (summary)

| Identity | Value |
| --- | --- |
| Implementation commit `A9` | `9ee7ae12c8dbf8317c4bac8a97f6a4b1c49553a3` |
| Image source commit `S9` | `7f601bf153ef86a567883c0008edf4ce34e79c95` |
| Final implementation head `B` | `231fa6e67a3240dbcc986b27fd7b62cf1c479245` |
| Wheel `W9 == W8` | `eb241dda2e079b29190868108c488edaf98261c84119bfd405070dea98b546b9` |
| Digest `D9` | `sha256:54fe19483f00ef6e209b2796786fe27cddd302c6bcf5322821b2192a32884334` |
| RC9 aliases | `0.1.0-rc9`, `sha-7f601bf153ef86a567883c0008edf4ce34e79c95` |
| Published image id | `sha256:15c661fcfaaec9f58f3dd56f5a074ad49b8a1f0d3fa018319e44a8eb3051c6f8` |
| Sdist (at `S9`) | `6353491d3bbe603ba49e19a8af3d7f8664e74f400af07fe53779b26d08d06406` |
| Dependency lock (uv.lock) | `1237cbd179f71b99984c80f927529549f5e61eb705585ef9cf2ab0fa9e26764a` |
| Gateway authority commit | `08ca421bee1ddca62078302b910e8be88cf705be` |
| Publication run | `36960763079` (2026-10-02T03:34:23Z → 03:35:29Z) |
| `published_at` | `2026-10-02T03:35:07Z` |
| Source-input map | 131 entries; `A9 == S9 == B` (proved by `source_input_map.py --ab` / `--ref`) |
| Historical digests re-asserted live | RC1 `2dd889c2…`, RC2 `2349400a…`, RC3 `41db6fcc…`, RC4 `a4f2014c…`, RC5 `70b450f5…`, RC7 `a3782915…` (D7), RC8 `50450f4a…` (D8) |

## Protected-host before/after

Before (order start) and after (after all live work, immediately
before this report) — identical in every observed respect:

- The long-lived vLLM fixture process **PID 23961** (no restart)
  alone owns `0.0.0.0:18020`; `/proc/23961/cmdline` sha256
  `8463567150873445b1aa8ec25b6a90d22fa340227a476ee3c0b56d9598ea0531`
  (command, model, checkpoint, quantization, context, tool/reasoning/
  prefix-cache flags all unchanged).
- Protected credential file
  `/synology/homes/janezp/qwen-serving/api_key.txt`: sha256
  `2b0509fbef278d1d5245d5cb63eeec909cd5e8576157df69a10c730fceffe3ec`,
  mode `0600`, 65 bytes, unchanged (checked before and after the
  ledger 007 run by the gate itself: 1 file checked, 0 changed).
- systemd user units: `qwen-serving-vision.service` **active**,
  `qwen-serving.service` **inactive** — unchanged.
- Ports: `18020` held exactly one listener (PID 23961) before and
  after; `18021` absent; `18031` free before and after the
  disposable adapter run (teardown confirmed in the gate facts).
- No model, vLLM flag, checkpoint, quantization, context, parser,
  CUDA/GPU, network, firewall, VPN, or service state was altered; no
  cutover; the disposable loopback adapter and its Codex home were
  removed.

## Privacy and non-goal audit

- No real API keys, gateway keys, bearer headers, cookies,
  credentials, private URLs, prompts, source, images, tool outputs,
  request/response bodies, model output, or customer data appear in
  any commit, report, log, evidence file, or metric label this round.
  The live backend URL and key were supplied to the gate exclusively
  through mode-0600 caller-owned file references (paths in argv,
  values never); the credential file hash was verified unchanged
  before/after.
- No benchmark or Minesweeper attempt was run; no benchmark harness
  or archive was modified; ledger 006 and all benchmark archives are
  byte-for-byte untouched.
- No final `v0.1.0` or GitHub Release was published; `final_public_
  release` remains false in the record and manifest.
- The package remains **private**; visibility was re-asserted
  `private` by the `S9` and `B` baselines; no visibility change.
- No Gateway, vLLM, Codex-profile, model, or network state mutation;
  no cutover; `cutover_performed` false.
- No second PR was created; PR #22 was amended only; never merged;
  auto-merge never enabled.
- P01/P02 product code, configuration, metrics, privacy, bounds,
  `compiler-v3` identity, and tests were NOT changed this round (no
  `src/` changes at all); the wheel equality `W9 == W8` is the
  mechanical consequence, verified.

## Acceptance criteria assessment

Per the order's acceptance list:

- **TRUE** — the workflow baseline and regression mechanically cover
  every archived RC record (exact RC7 and RC8 pairs digest-asserted;
  RC1–RC5 re-asserted; intentional RC6 absence preserved and
  unrepresentable), proven by 6/6 local regression tests, the 015-a
  frozen-source replay (6/6 FAIL as expected), and two live
  authenticated baseline executions (`S9` source round, `B` published
  round).
- **TRUE** — RC8 and all earlier archive/registry bytes remain
  unchanged (RC8 archive verified byte-identical to `78822ca`; ledger
  006 untouched; live baselines re-assert every historical digest).
- **TRUE** — one new private RC9 digest `D9` exists with both
  collision-safe aliases (verified-absent-for-both precondition,
  single-digest post-write verification) and full source/wheel/
  provenance binding (`S9` → `D9` → `W9 == W8` → 131-entry map →
  record → manifest).
- **TRUE** — all local gates (exact commands above), exact-head CI
  and CodeQL at `S9` and `B` (all jobs), pulled-image qualification
  (13/13 published-mode phases, actual `D9` pull, no rebuild),
  P01/P02 (unchanged product state, full suite green), and genuine-
  Codex VISION/CACHE/BOTH/DIRECT (ledger 007, exact 0.149.0) gates
  are green.
- **TRUE** — the current record/handoff points to RC9 and contains
  every handoff field.
- **TRUE** — no benchmark, final release, public visibility,
  Gateway/vLLM mutation, or cutover occurred (audit above).

The single 015-a blocker (its criterion 7: the frozen CI baseline
omitting the archived RC7 pair) is closed by the correction and
regression above; criteria 1–6 and 8–11 were already TRUE per the
015-a report and remain TRUE (re-verified live where applicable).

## Residual risks

- The read-only baseline asserts the historical pairs on every
  published/source CI round; any future registry mutation of an
  archived pair now fails CI (intended fail-closed behavior).
- The baseline's pre-RC singletons remain record-only (no archived
  record exists to bind them to digests), per the original 013-l
  convention; this is unchanged from all prior rounds.
- Ledger 007 is scoped standalone (disposable loopback, no Gateway);
  it is not benchmark or production-equivalence evidence.
- Strategy will independently review, merge only a fully accepted PR,
  and require fresh post-merge `main` CI and CodeQL before its final
  verdict.

## Verdict

**BENCHMARK_READY** — all cumulative 015-a and 015-b acceptance
criteria are TRUE. The 015-a blocker (frozen CI read-only registry
baseline omitting the archived RC7 pair) is corrected at the source
with a single source of truth and a deterministic regression that
fails against the 015-a frozen source; RC8 is preserved permanently
(archived byte-identical, aliases occupied/immutable); RC9
(`0.1.0-rc9` / `D9` / `W9 == W8` / `S9`) is privately published from
exact `S9` with both collision-safe aliases, fully qualified
(pulled-image 13/13, genuine Codex 0.149.0 VISION/CACHE/BOTH/DIRECT
PASS in ledger 007), bound end to end (record → handoff → manifest →
131-entry source-input map), and green on fresh source-head and
final-head CI plus CodeQL. No benchmark, final release, public
visibility, Gateway/vLLM mutation, or cutover occurred.

---

Implementation head SHA: 231fa6e67a3240dbcc986b27fd7b62cf1c479245
Report publication commit: SELF

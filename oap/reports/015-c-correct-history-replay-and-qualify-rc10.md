# OAP 015-c Report — Correct the historical regression replay and qualify private RC10

## Scope and identity

- Order: `015-c` (`oap/orders/015-c-correct-history-replay-and-qualify-rc10.md`,
  activated byte-exact, sha256
  `c522d51c49e0bf221673857de80341f15e6e875683f7fab0031cdc8db3d795fb`).
- Repository: `ulfe-lmi/slaif-local-coding`.
- PR mode: `AMEND_EXISTING_PR` — PR #22
  (https://github.com/ulfe-lmi/slaif-local-coding/pull/22), non-draft,
  never merged, auto-merge never enabled. No second PR exists for
  Objective 015.
- Base: `main` at `87ed2cea43a0a8706efe485b9b625dfda7cf75aa` (untouched;
  verified `origin/main` at the same SHA before every mutation).
- Branch: `oap/015-upstream-diagnostics-compiler-truncation-rc8`.
- Remote head at order start:
  `3b1f417f0584859d42ec8781b7f9507ceb19f0d1` (015-b report SELF, parent
  `231fa6e67a3240dbcc986b27fd7b62cf1c479245`).
- New commits this round (all on the existing branch, in order):
  1. `8d694d956074041910cf53129292753ab896223a` — Objective 015-c
     activation transcript (order file + `oap/active`).
  2. `255b3f42912e3947908fc8868eccb6bcec874a08` — implementation `A10`
     (fallback-parser correction + 6 focused parser tests, pinned
     inventory +RC9, RC9 archive, candidate constants/schemas/workflows/
     tests/docs advanced to exactly `0.1.0-rc10`).
  3. `1a04528223445e4249fad6d24a71151fd1dc1a09` — image source commit
     `S10` (freeze; pre-freeze provenance manifest regenerated from a
     clean `git archive` of `A10`; manifest-only diff over `A10`).
  4. `1e0c6a169162fb3f73c807961b58fb2d778374d7` — post-freeze derived
     metadata only (RC10 record + handoff, `rc_published` manifest,
     testing ledger 008). **Exact final implementation SHA (this
     commit).**
- Changed paths (`3b1f417…` → `1e0c6a1…`, 34 files; 7 added, 27
  modified, 1547 insertions, 240 deletions):
  - Parser correction: `tests/test_registry_history_baseline.py`
    (`_inline_static_tags` now parses the tuple expression, not the
    `tags =` assignment; fail-closed on malformed/ambiguous/non-string
    content; parsing bounded to the exact named workflow step; no
    execution of workflow text) + 6 new focused parser tests (valid
    multiline historical shape; unbalanced; non-literal expression;
    non-string member; ambiguous parenthesized string; no static tuple).
  - RC9 archive: `packaging/releases/0.1.0-rc9/{rc_record.json,
    rc_handoff.md, release_provenance_manifest.json}` (byte-identical
    copy of the RC9 state at `231fa6e…`; see below).
  - Candidate constants to `0.1.0-rc10`: `.github/workflows/
    {ci.yml,release-image.yml}`, `packaging/
    {rc_artifact_record.schema.json,release_provenance_manifest.schema.
    json}`, `scripts/{docker_qualification_ci,operator_session_ci,
    rc_artifact_record,real_codex_rc_qualification,release_
    provenance_manifest,release_registry_publish}.py`,
    `tests/test_{compose_pull_canonical,docker_qualification_record_
    gate,rc_record,rc_record_present_rehearsal,real_codex_rc_
    qualification,release_provenance_manifest,release_registry_publish_
    digest,release_registry_publish_gate}.py`.
  - Release/history docs corrected so RC9 is recorded as published and
    qualified but rejected as the final handoff (its frozen historical
    replay test was defective): `TESTING.md`, `docs/HISTORY.md`,
    `docs/RC-HANDOFF.md`, `docs/RELEASE-ARTIFACT-POLICY.md`.
  - Provenance/evidence: `packaging/release_provenance_manifest.json`,
    `packaging/rc_record.json`, `packaging/rc_handoff.md`,
    `oap/evidence/testing-ledger/008/{README.md,MANIFEST.sha256,
    real-codex-rc10-qualification.json}` (new).
  - Activation: `oap/active`,
    `oap/orders/015-c-correct-history-replay-and-qualify-rc10.md`.
- No `src/` changes at all (P01/P02 product code, compiler-v3
  semantics, metrics, privacy/bounds, configuration untouched); no
  dependency or lock changes.
- Pre-existing untracked paths `Local`, `clean`, `unchanged` remained
  untracked, unmodified, and uncommitted throughout.

## The parser defect and the corrected replay

### Defect (strategic review finding, independently confirmed)

The 015-b fallback parser
`tests/test_registry_history_baseline.py::_inline_static_tags` located
the source slice beginning with `tags = (` and passed the WHOLE
ASSIGNMENT to `ast.literal_eval`, which accepts an expression, not an
assignment. Replaying the focused coverage test against the 015-a
frozen source therefore died inside the parser before any alias
comparison, making the 015-b "fails on the exact RC7 omission" claim
unsupported.

### Before evidence (replayed this round, mechanical)

In a disposable clean `git archive` of
`78822ca8f8c58fbc959495d37bdff32e525eb945` (the 015-a final
implementation head) with the 015-b test file (defective parser) copied
in, running only
`test_workflow_baseline_represents_every_archived_pair`:

```text
File "<unknown>", line 1
  tags = (
       ^
SyntaxError: invalid syntax
1 failed in 0.09s
```

No alias comparison was ever reached. This reproduces the strategic
finding exactly.

### After evidence (replayed this round, mechanical)

Same clean archive of `78822ca…`, with the 015-c CORRECTED test file
copied in, same single test:

```text
>       assert not missing, f"workflow baseline omits archived aliases: {missing}"
E       AssertionError: workflow baseline omits archived aliases:
        ['sha-0a2f34b6d6fc17b732a1e7570f751776dce1ae01',
         '0.1.0-rc7', 'sha-ae6271318627703785f42de57d893c9be3b980c9']
1 failed in 0.06s
```

The corrected parser (bounded to the exact named workflow step, parsing
the tuple expression, fail-closed on malformed/ambiguous/non-string
content, never executing workflow text) reaches the alias comparison
and fails there, as required. The 015-a frozen source's inline tuple is
`("0.1.0", sha-fe334e87…, sha-be3c78b2…, 0.1.0-rc1, sha-4d096e40…,
0.1.0-rc2, 0.1.0-rc3, sha-307a929f…, 0.1.0-rc4, sha-601a7f9f…,
0.1.0-rc5, sha-e04b4a99…)` — it carries no RC7 pair (the exact RC7
omission named by the order) and, as the replay additionally shows, it
never carried RC2's `sha-` alias either.

### Disclosed deviation from the order's predicted missing set (READ FIRST)

The order predicted the replay would fail with the missing set EXACTLY:

```text
0.1.0-rc7
sha-ae6271318627703785f42de57d893c9be3b980c9
```

The measured missing set is a STRICT SUPERSET — three aliases:

```text
sha-0a2f34b6d6fc17b732a1e7570f751776dce1ae01   (RC2 sha alias)
0.1.0-rc7
sha-ae6271318627703785f42de57d893c9be3b980c9
```

This is a property of the 015-a frozen source, not of the corrected
test. Git-history proof (mechanical, whole history):

- `git log --all -S 'sha-0a2f34b6d6fc17b732a1e7570f751776dce1ae01' --
  .github/workflows/ci.yml` → **0 commits**: RC2's sha alias was
  present in NO `ci.yml` baseline tuple at ANY commit.
- The 015-a tuple (quoted above) contains the RC2 CANDIDATE tag
  `0.1.0-rc2` but not its `sha-` alias.
- The tag appears in history only in the RC2 record commit
  (`bb493a3…`) and later derived metadata — never in the workflow
  baseline.

Decision taken (disclosed for strategy adjudication): the regression
was NOT weakened to match the prediction. The corrected assertion
reports exactly what the 015-a baseline omits; making it pass on the
2-tag prediction would have required ignoring a real, provable
omission. The exact RC7 omission IS present in and named by the failure
(the regression's primary purpose); the current baseline (derived from
every archived strict record, bound to recorded digests) now covers all
8 archived pairs including the RC2 sha alias, and the focused test
PASSES on the current source. The corrected test file's docstring
records this anchor and deviation. Strategy decides acceptance of the
deviation; all other acceptance criteria are met (below).

### Current-source proof

Against the corrected current tree (at `A10`, `S10`, and the
implementation head): `tests/test_registry_history_baseline.py`
12/12 PASSED, including
`test_workflow_baseline_represents_every_archived_pair` (all 8 archived
pairs represented) and
`test_workflow_baseline_binds_pairs_to_recorded_digests` (every pair
digest-bound); intentional RC6 absence asserted and unrepresentable.
The pinned inventory now carries RC1–RC5, RC7, RC8, RC9 with exact
source/digest values (RC9 added by this round's archive).

## RC9 archive (byte-identical, verified against 231fa6e)

`packaging/releases/0.1.0-rc9/` (archived under `A10`), each verified
byte-identical to the top-level RC9 blob at commit
`231fa6e67a3240dbcc986b27fd7b62cf1c479245` (mechanical `git cat-file`
comparison, re-run this round at the implementation head):

- `rc_record.json` sha256
  `99819786b9899ce6a0571cba431ee09b71f43529427f1b5eb91a28963810d5dd`
- `rc_handoff.md` sha256
  `467765a87275355ed2fd77aefa111375a86648e599529dcaf43b1fa77150ab7a`
- `release_provenance_manifest.json` sha256
  `5a1929d5a610ba36dd49a7a07de3e7767185582e9a8b6f4938ab36690bc922f2`

RC9's immutable identity is untouched: source `S9`
`7f601bf153ef86a567883c0008edf4ce34e79c95`, digest `D9`
`sha256:54fe19483f00ef6e209b2796786fe27cddd302c6bcf5322821b2192a32884334`,
aliases `0.1.0-rc9` / `sha-7f601bf153ef86a567883c0008edf4ce34e79c95`,
publication run 36960763079. Neither RC9 alias nor `D9` was rewritten,
repointed, or deleted; no RC6 identity was created; ledger 007 and all
earlier archives/ledgers are byte-for-byte untouched. The release and
history docs now record RC9 accurately as PUBLISHED AND QUALIFIED but
REJECTED as the final Objective-015 handoff because its frozen
historical replay test was defective.

## Freeze identities (A10 / S10)

- Implementation commit `A10` =
  `255b3f42912e3947908fc8868eccb6bcec874a08`.
- Image source commit `S10` =
  `1a04528223445e4249fad6d24a71151fd1dc1a09` (manifest-only diff over
  `A10`; no artifact input changes after `S10`).
- Wheel `W10 == W9 == W8` =
  `eb241dda2e079b29190868108c488edaf98261c84119bfd405070dea98b546b9`
  — MEASURED, not assumed: byte-identical across clean `git archive`
  builds of `A10` under isolated CPython 3.12.3 and 3.12.14 (pinned
  `[build-system].requires`), the local `uv build` at `S10` and at the
  implementation head, and the in-workflow CI rebuild (fresh wheel ==
  manifest wheel, asserted in the publication run below). Equality was
  expected (no wheel/src input changed this round) and mechanically
  verified at every point.
- Sdist (at `S10` and re-measured at the implementation head) =
  `50325eeeaeffd91db3b6ddd996268473043ea48d9f948be23838f1f9968b3f29`.
- Dependency lock (uv.lock) sha256 =
  `1237cbd179f71b99984c80f927529549f5e61eb705585ef9cf2ab0fa9e26764a`
  (unchanged; `uv lock --check` green).
- Build environment pins: hatchling 1.32.0, packaging 26.3, pathspec
  1.1.1, pluggy 1.6.0, tomlkit 0.15.1, trove-classifiers 2026.6.1.19;
  uv 0.12.5; observed build Pythons 3.12.3 and 3.12.14.
- Gateway compatibility authority commit:
  `08ca421bee1ddca62078302b910e8be88cf705be` (unchanged peer).
- Source-input map: 131 entries at `S10` (same count as `S9`, which
  also carried 131). The `S9 → S10` delta is exactly 14 rehashed
  inputs and nothing else (measured): `.github/workflows/ci.yml`,
  `docs/{HISTORY,RC-HANDOFF,RELEASE-ARTIFACT-POLICY}.md`,
  `packaging/rc_artifact_record.schema.json`, and the 9 corrected test
  files (`test_compose_pull_canonical`,
  `test_docker_qualification_record_gate`, `test_rc_record`,
  `test_rc_record_present_rehearsal`, `test_real_codex_rc_
  qualification`, `test_registry_history_baseline`,
  `test_release_provenance_manifest`,
  `test_release_registry_publish_digest`,
  `test_release_registry_publish_gate`) — 1 + 3 + 1 + 9 = 14; no file
  added or removed, no wheel/src input changed. Proved with
  `scripts/source_input_map.py`:
  - `--ab S10 B10 --manifest`: OK (131 input files; diff confined to
    the excluded derived files: record/handoff/manifest/ledger 008);
  - `--ref S10 --manifest`: ref carries exactly the recorded map.
- Manifest: `packaging/release_provenance_manifest.json` regenerated
  from a clean `git archive` of `A10` (`generated_from.git_commit` =
  `A10`, objective `015-c`, state `pre_freeze` at `S10`, `rc_published:
  false`); the `B10` regeneration is the exact `rc_published` state
  transition (state, published flag, digest, label, tag convention,
  limitations wording; map and `generated_from` unchanged) — the same
  A/B convention as 015-b's `A9`/`B` manifest pair.

## Local verification (exact commands and states)

At `A10` (pre-freeze, before the S10 manifest regeneration):

- `uv lock --check`, `uv run --frozen ruff check .`, `uv run --frozen
  ruff format --check .`, `uv run --frozen mypy src tests`,
  `scripts/docs_consistency_check.py`, `python -m compileall -q src
  tests oap/bin scripts`, `bash -n` on all committed shell scripts:
  all green.
- `uv run --frozen pytest -q`: 1506 passed, 27 skipped, 6 failed —
  the 6 failures are EXACTLY the committed-manifest binding tests
  failing because the committed manifest still carried the 015-b RC9
  `rc_published` state against the new `A10` inputs (the expected
  pre-freeze condition, identical to prior rounds); every one of them
  passed at `S10` after the manifest-only freeze commit.
- `uv build`: wheel == `W10 == W9 == W8`; sdist ==
  `50325eee…`; `scripts/artifact_policy_check.py --dist dist
  --inspect` and `--install-smoke`: both ok, 0 violations.
- Isolated clean CPython 3.12.3 and 3.12.14 `uv build` of a clean
  `git archive` of `A10`: both wheels byte-identical to
  `eb241dda…` (reproducibility measured, not assumed).
- `tests/test_registry_history_baseline.py`: 12/12 PASSED (6 new
  parser tests + 6 coverage/binding/RC6/source-of-truth tests).

At `S10` (pre-freeze state, post-manifest-regeneration):

- `uv run --frozen pytest -q`: **1512 passed, 27 skipped, 0 failed**.
- `uv lock --check`, `ruff check`, `ruff format --check`, `mypy src
  tests`, `docs_consistency_check.py`, compileall, shell syntax: all
  green.
- `rc_record_present_rehearsal.py --source S10` (PRE mode): PASSED
  (disposable clean `git archive` rebuild → wheel == `W10`; synthetic
  record gate set).
- `uv build` at `S10`: wheel == `W10 == W9 == W8` (byte-identical).
- `source_input_map.py --ab A10 S10 --manifest` and `--ref S10
  --manifest`: OK.

At `B10` (final implementation head, record present):

- `uv run --frozen pytest -q`: **1513 passed, 26 skipped, 0 failed**
  (the single delta vs `S10` is the pre-publication record-present
  test becoming active in POST mode).
- `uv lock --check`, `uv run --frozen ruff check .`, `uv run --frozen
  ruff format --check .` (455 files), `uv run --frozen mypy src tests`
  (86 source files), `docs_consistency_check.py` (19 claim docs),
  compileall, shell syntax: all green.
- `uv build` at `B10`: wheel == `W10`, sdist == `50325eee…`
  (byte-identical; the derived-only delta changed no build input).
- `scripts/artifact_policy_check.py --dist dist --inspect` and
  `--install-smoke`: both ok, 0 violations (fresh noneditable wheel
  install smoke included).
- `rc_record_present_rehearsal.py --source B10` (POST mode): PASSED
  (real record identity bindings at source
  `1e0c6a169162fb3f73c807961b58fb2d778374d7`; evidence binding to
  ledger 008, deterministic handoff render, tamper classes exercised).
- `source_input_map.py --ab S10 B10 --manifest`: OK (131 input files;
  diff confined to the excluded derived files); `--ref S10
  --manifest`: OK.
- P01/P02 focused regressions: `tests/test_upstream_diagnostics.py` +
  `tests/test_compiler_truncation.py`: 60/60 PASSED.
- Corrected registry replay (current source):
  `test_workflow_baseline_represents_every_archived_pair` and
  `test_archived_records_match_pinned_inventory`: PASSED (and 12/12 in
  the file).
- Historical replay at `78822ca` (both pre-fix and post-fix): re-run
  this round as documented above.

## Fresh CI/CodeQL at source head S10 (before any registry write)

- CI run `36964926456`
  (https://github.com/ulfe-lmi/slaif-local-coding/actions/runs/36964926456,
  pull_request, head `1a0452822344…`): **SUCCESS**
  (2026-10-02T04:31:28Z → 04:34:05Z) —
  - `test` SUCCESS (job 110706483366): 1511 passed, 28 skipped on the
    runner (the single delta vs local is the host-pinned
    `test_target_semantic_preflight_failure_precedes_protected_
    selection`, honestly SKIPPED on the runner);
  - `docker` SUCCESS (job 110706483579): build mode, all phases
    PASSED;
  - `docker-published` SUCCESS (job 110706483599): **source mode** —
    the read-only baseline digest-asserted every archived pair (RC1–
    RC5 at their recorded digests, RC7 at D7
    `a3782915…`, RC8 at D8 `50450f4a…`, RC9 at D9 `54fe1948…`),
    recorded `package visibility -> private`, and the publication gate
    reported `docker-published: NOT RUN (pre-publication: no RC or
    final publication record)` — the correct pre-publication state;
  - `gateway-contract` SUCCESS (job 110706483616);
    `operator-session` SUCCESS (job 110706483595).
- CodeQL run `36964923852`
  (https://github.com/ulfe-lmi/slaif-local-coding/actions/runs/36964923852,
  head `1a0452822344…`): **SUCCESS**.

Only after both were fully green was the publication dispatched.

## Private RC10 publication (workflow_dispatch from exact S10)

- Run `36965969078`
  (https://github.com/ulfe-lmi/slaif-local-coding/actions/runs/36965969078,
  `release-image.yml`, workflow_dispatch, head `S10` =
  `1a04528223445e4249fad6d24a71151fd1dc1a09` — the dispatch ref was the
  branch whose remote head was exactly `S10`; created
  2026-10-02T04:45:49Z, completed 2026-10-02T04:46:37Z, **SUCCESS**):
  - checkout/head verified at `S10` (shallow fetch of exactly
    `1a04528223445e4249fad6d24a71151fd1dc1a09`); in-workflow fresh
    wheel rebuilt and asserted equal to the committed manifest wheel
    (both `eb241dda2e079b29190868108c488edaf98261c84119bfd405070dea98b546b9`);
  - authenticated strict pre-mutation check: `registry before:
    sha-1a04528223445e4249fad6d24a71151fd1dc1a09 = verified absent;
    0.1.0-rc10 = verified absent` at 2026-10-02T04:46:16Z (the only
    write precondition — collision-safe, distinguished from
    unauthorized/inaccessible);
  - single push of one image; `registry after:` at
    2026-10-02T04:46:33Z: BOTH tags present at ONE digest.
- **Digest `D10` =
  `sha256:5a02e0043fcc65e5dc5a78f3e2a8648a16c93620255e904e394c926b18c92960`**;
  tags `0.1.0-rc10` and
  `sha-1a04528223445e4249fad6d24a71151fd1dc1a09` both resolve to
  `D10` (registry API, post-write).
- `published_at` = `2026-10-02T04:46:33Z` (final authenticated
  post-write verification line).
- Qualification label built into the image:
  `rc-candidate-0.1.0-rc10; private; not final release`.
- No historical identity, alias, or visibility was touched by the run
  (private visibility re-asserted by the `B10`-head baseline below;
  pre-RC singletons and RC1–RC5/RC7/RC8/RC9 pairs unchanged at their
  recorded digests).

## Pulled-image qualification of the actual D10 (final head B10)

Final-head CI `36966732622`
(https://github.com/ulfe-lmi/slaif-local-coding/actions/runs/36966732622,
head `1e0c6a169162…`): **SUCCESS** — `docker-published` (job
110711999638) ran in **published** mode (`publication gate: RC
published (digest sha256:5a02e0043fcc…, source
1a04528223445e4249fad6d24a71151fd1dc1a09)`) and passed ALL 13 phases:
adapter_stack_up, bridge_negative_contract, bridge_positive_signed,
compose_rendered_validation, config_time_rejection,
fail_closed_readiness, fake_upstream_start, hardening_and_labels,
image_content_scan, in_image_provenance, pull_preexistence_no_build,
teardown_absence_proof, verify_wheel_binding — `summary: PASSED`:

- actually PULLED `D10` by digest (`docker pull
  ghcr.io/ulfe-lmi/slaif-local-coding@sha256:5a02e0043fcc65e5dc5a78f3e2a8648a16c93620255e904e394c926b18c92960`)
  — no rebuild (`pull_preexistence_no_build` PASSED with
  `pulled_before_up: true` and `canonical_compose_build_key_absent:
  true`);
- pulled by both tags and asserted each resolves to the recorded
  digest (RepoDigests assertion + authenticated strict tag check);
- in-image wheel binding == `W10 == W9 == W8`
  (`verify_wheel_binding` PASSED, `image_bound_to_committed_artifact:
  true`); in-image provenance non-editable with the frozen runtime
  lock closure OK (18/18 pinned);
- image id of the pulled image
  `sha256:4d08e856b8b8a43a4587ff86e66442d8e9089c9af762ad70a987c036c767d05f`
  — identical to the image built in publication run 36965969078;
- signed-ingress contract run (bridge positive signed / negative
  contract) over the loopback port 18031 with the fake upstream (no
  protected backend involved); fail-closed readiness (readyz 503 with
  gateway unavailable); hardening/OCI labels (non-root, read-only
  rootfs, cap-drop-all, no-new-privileges, linux/amd64, qualification
  + topology + wheel + gateway-peer labels); content scan (6485
  files, 0 forbidden); lifecycle; teardown absence proof (containers
  and listeners absent, ports 18031/18033/18034 clear).

Its authenticated read-only baseline explicitly showed the pre-RC
singletons, RC1–RC5 pairs at their recorded digests, RC7 at D7
`a3782915…`, RC8 at D8 `50450f4a…`, RC9 at D9 `54fe1948…` UNCHANGED,
AND the current RC10 pair (`0.1.0-rc10`,
`sha-1a04528223445e4249fad6d24a71151fd1dc1a09`) at D10
`5a02e004…`, with `package visibility -> private`.

## Record, handoff, and provenance (commit B10)

- `packaging/rc_record.json` (schema `slaif-rc-record-v3`, 24 keys)
  generated from authenticated facts:
  - `rc_identifier` `0.1.0-rc10`; `image_source_commit` `S10`;
    `workflow_head_sha` `S10` (dispatch ref == branch head == `S10`);
  - `oci_image_digest` `D10`; `oci_tags` `[0.1.0-rc10,
    sha-1a04528223445e4249fad6d24a71151fd1dc1a09]`;
  - `wheel_sha256` `W10 == W9 == W8`; `dependency_lock_sha256`
    `1237cbd1…`; build environment pins; base image digests;
    `image_platform` `linux/amd64`;
  - `publication_workflow` `release-image.yml`;
    `publication_workflow_run_id` `36965969078`; `published_at`
    `2026-10-02T04:46:33Z`;
  - `gateway_authority_sha` `08ca421b…`; `source_input_hashes` (131
    entries) equal to the recorded map;
  - `private_registry_auth_required` true; `final_public_release`
    false; `cutover_performed` false;
  - `compatibility` derived mechanically from the manifest-verified
    ledger 008 facts (VISION/CACHE/BOTH arm verdicts `pass`, DIRECT
    control `pass`, client `0.149.0`/`bbc3341e…`, standalone
    no-Gateway topology, evidence path
    `oap/evidence/testing-ledger/008`).
- `packaging/rc_handoff.md`: deterministic render of the record (all
  handoff fields present; the record's evidence binding and the
  frozen handoff render were re-proved by the POST-mode rehearsal).
- `packaging/release_provenance_manifest.json` regenerated in
  `rc_published` state: objective `015-c`, `generated_from` = `A10`
  (unchanged from `S10`), 131-entry source-input map unchanged,
  `rc_published: true`, `published: true`, digest `D10`, candidate
  tag `0.1.0-rc10`, qualification label
  `rc-candidate-0.1.0-rc10; private; not final release`,
  `final_public_release: false`, `cutover_performed: false`; diff vs
  `S10` is exactly the state transition.

## Testing ledger 008 (genuine Codex 0.149.0, no Gateway)

`oap/evidence/testing-ledger/008/` (new; ledgers 006/007 byte-for-byte
untouched):

- Subject client: Codex CLI **0.149.0**
  (`bbc3341e44c9ead340ed9570c17be936e37870f570751a941699ffd04d672827`),
  exact pinned version + hash enforced by the gate (no
  later-version fallback needed).
- Topology: disposable Codex home/repository → `127.0.0.1:18031`
  disposable adapter (exact `W10` wheel, binding asserted `equal` in
  the facts) → existing protected backend; **no SLAIF API Gateway**
  (gateway ingress disabled; no signed Gateway headers).
- Overall verdict **PASS** (facts created 2026-10-02T04:43:35Z, schema
  `slaif-real-codex-rc-qualification-v2`):
  - **VISION** PASS — attempts 1, exit 0, sentinel present (3 bytes),
    1 genuine tool interaction, adapter 200/500/422 = 2/0/0, upstream
    failures 0, compiler calls 0, cache entries 0, 3 s, failure class
    `none` (one-image `retain_newest` route policy exercised).
  - **CACHE** PASS — attempts 1, exit 0, sentinel present (3 bytes),
    1 genuine tool interaction, adapter 200/500/422 = 2/0/0, upstream
    failures 0, compiler calls 1, cache entries 1, 37 s, failure class
    `none` (full constitutional/compiler/derived-cache path with
    measurable treatment evidence).
  - **BOTH** PASS — attempts 1, exit 0, sentinel present (3 bytes),
    1 genuine tool interaction, adapter 200/500/422 = 2/0/0, upstream
    failures 0, compiler calls 1, cache entries 1, 37 s, failure class
    `none` (both mechanisms enabled, same static identity).
  - **DIRECT** PASS (contextual control, never a substitute) —
    attempts 1, exit 0, sentinel present (3 bytes), 1 genuine tool
    interaction, adapter 200/500/422 = 0/0/0, upstream failures 0,
    5 s, failure class `none`.
- Mechanical ceilings enforced and stayed below limit: arms 4 ≤ 4,
  tool interactions 1/arm ≤ 8, adapter requests ≤ 64, compiler calls
  ≤ 4, per-attempt output cap 1048576 bytes, per-attempt 600 s, total
  5400 s, attempts ≤ 2.
- `protected_state_unchanged: true` (1 protected file checked, 0
  changed; user units unchanged; 18020 held exactly one listener
  before and after), `disposable_state_removed: true`.
- Privacy: fixed synthetic prompt over stdin (no prompt substring in
  any argv); backend URL via a mode-0600 caller-owned file reference
  (the path, never the URL, in argv); sanitized closed-schema facts
  only — no prompt, source, tool output, body, image, credential,
  private URL, or session ID in the record.
- `MANIFEST.sha256` covers exactly the ledger directory (manifest
  itself excepted, per the ledger 001/002 convention); the facts file
  was manifest-verified by the RC record generator before the record
  accepted it.
- One BLOCKED first attempt occurred before this run (CACHE arm
  `qualification-error`, 0 adapter requests): the caller-supplied
  upstream base-url file omitted the `/v1` path segment that the
  adapter's constitution-enabled configuration requires. The facts
  file of that blocked attempt was discarded (not retained in the
  ledger); the corrected file reference re-ran the gate cleanly. No
  protected state was involved in the failure or the fix.

## GitHub CI/CodeQL at final head B10

- CI run `36966732622`
  (https://github.com/ulfe-lmi/slaif-local-coding/actions/runs/36966732622,
  pull_request, head `1e0c6a169162…`): **SUCCESS** —
  - `test` SUCCESS (job 110711999667): 1512 passed, 27 skipped on the
    runner (the single delta vs local 1513/26 is the host-pinned
    `test_target_semantic_preflight_failure_precedes_protected_
    selection`, honestly SKIPPED on the runner — same delta pattern as
    015-b);
  - `docker` SUCCESS (job 110711999532): build mode, all phases
    PASSED;
  - `docker-published` SUCCESS (job 110711999638): published mode,
    13/13 phases PASSED, pulled `D10` without rebuilding (see above);
  - `gateway-contract` SUCCESS (job 110711999434);
    `operator-session` SUCCESS (job 110711999524).
- CodeQL run `36966730462`
  (https://github.com/ulfe-lmi/slaif-local-coding/actions/runs/36966730462,
  head `1e0c6a169162…`): **SUCCESS**.
- Remote PR head verified after push:
  `1e0c6a169162fb3f73c807961b58fb2d778374d7` (this implementation
  head) until the report-only commit described below.

## Source / artifact / registry identities (summary)

| Identity | Value |
| --- | --- |
| Implementation commit `A10` | `255b3f42912e3947908fc8868eccb6bcec874a08` |
| Image source commit `S10` | `1a04528223445e4249fad6d24a71151fd1dc1a09` |
| Final implementation head `B10` | `1e0c6a169162fb3f73c807961b58fb2d778374d7` |
| Wheel `W10 == W9 == W8` | `eb241dda2e079b29190868108c488edaf98261c84119bfd405070dea98b546b9` |
| Digest `D10` | `sha256:5a02e0043fcc65e5dc5a78f3e2a8648a16c93620255e904e394c926b18c92960` |
| RC10 aliases | `0.1.0-rc10`, `sha-1a04528223445e4249fad6d24a71151fd1dc1a09` |
| Published image id (pulled) | `sha256:4d08e856b8b8a43a4587ff86e66442d8e9089c9af762ad70a987c036c767d05f` |
| Sdist (at `S10`/`B10`) | `50325eeeaeffd91db3b6ddd996268473043ea48d9f948be23838f1f9968b3f29` |
| Dependency lock (uv.lock) | `1237cbd179f71b99984c80f927529549f5e61eb705585ef9cf2ab0fa9e26764a` |
| Gateway authority commit | `08ca421bee1ddca62078302b910e8be88cf705be` |
| Publication run | `36965969078` (2026-10-02T04:45:49Z → 04:46:37Z) |
| `published_at` | `2026-10-02T04:46:33Z` |
| Source-input map | 131 entries; `A10 == S10 == B10` (proved by `source_input_map.py --ab` / `--ref`) |
| Historical digests re-asserted live | RC1 `2dd889c2…`, RC2 `2349400a…`, RC3 `41db6fcc…`, RC4 `a4f2014c…`, RC5 `70b450f5…`, RC7 `a3782915…` (D7), RC8 `50450f4a…` (D8), RC9 `54fe1948…` (D9) |
| Qualification label | `rc-candidate-0.1.0-rc10; private; not final release` |

## Protected-host before/after

Before (captured at the start of this round's live work) and after
(after all live work, immediately before this report) — identical in
every observed respect:

- The long-lived vLLM fixture process **PID 23961** (no restart)
  alone owns `0.0.0.0:18020`; `/proc/23961/cmdline` sha256
  `8463567150873445b1aa8ec25b6a90d22fa340227a476ee3c0b56d9598ea0531`
  (command, model, checkpoint, quantization, context, tool/reasoning/
  prefix-cache flags all unchanged).
- Protected credential file
  `/synology/homes/janezp/qwen-serving/api_key.txt`: sha256
  `2b0509fbef278d1d5245d5cb63eeec909cd5e8576157df69a10c730fceffe3ec`,
  mode `0600`, 65 bytes, unchanged (also checked before and after the
  ledger 008 run by the gate itself: 1 file checked, 0 changed).
- systemd user units: `qwen-serving-vision.service` **active**,
  `qwen-serving.service` **inactive** — unchanged.
- Ports: `18020` held exactly one listener (PID 23961) before and
  after; `18021` absent; `18031` free before and after the
  disposable adapter run (teardown confirmed in the gate facts).
- `/health` 200; served model `qwen3.8-27b` — before and after.
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
  or archive was modified; ledgers 006/007 and all benchmark archives
  are byte-for-byte untouched.
- No final `v0.1.0` or GitHub Release was published;
  `final_public_release` remains false in the record and manifest;
  `cutover_performed` false.
- The package remains **private**; visibility was re-asserted
  `private` by the `S10` and `B10` baselines; no visibility change.
- No Gateway, vLLM, Codex-profile, model, or network state mutation;
  no cutover.
- No second PR was created; PR #22 was amended only; never merged;
  auto-merge never enabled.
- P01/P02 product code, configuration, metrics, privacy, bounds,
  `compiler-v3` identity, and tests were NOT changed this round (no
  `src/` changes at all); the wheel equality `W10 == W9 == W8` is the
  mechanical consequence, verified.
- The current-candidate constant advance to `0.1.0-rc10` touched only
  release-surface files (workflows, schemas, scripts, release tests,
  release docs); the pinned regression inventory gained exactly the
  RC9 entry mandated by this round's archive.

## Acceptance criteria assessment

Per the order's acceptance list:

- **TRUE (with disclosed deviation)** — the corrected historical
  replay REACHES the alias comparison against `78822ca` and fails
  there reporting the exact RC7 omission (both RC7 tags present in
  the failure), and the same focused assertion PASSES on the current
  source with the intentional RC6 absence explicit. Deviation: the
  measured missing set also contains RC2's sha alias, which no 015-a
  baseline tuple ever carried (git-history proof above); the
  regression was not weakened to force the 2-tag prediction. This
  deviation is disclosed for strategy adjudication and is the only
  criterion not met in the order's literal wording.
- **TRUE** — RC9 remains immutable: archived byte-identically
  (hashes above, re-verified at the implementation head), aliases and
  D9 untouched, ledger 007 and all earlier archives untouched;
  release/history docs corrected as required without rewriting the
  immutable 015-b report or ledger 007.
- **TRUE** — one new private RC10 digest `D10` exists with both
  collision-safe aliases (verified-absent-for-both precondition at
  04:46:16Z, single-digest post-write verification at 04:46:33Z) and
  full source/wheel/provenance binding (`S10` → `D10` →
  `W10 == W9 == W8` → 131-entry map → record → manifest), pulled and
  qualified without rebuild (13/13 published-mode phases).
- **TRUE** — all local gates (exact commands above), exact-head CI
  and CodeQL at `S10` and `B10` (all jobs), pulled-image
  qualification, P01/P02 (unchanged product state, focused 60/60 and
  full suite green), and genuine-Codex 0.149.0
  VISION/CACHE/BOTH/DIRECT (ledger 008, exact pinned client) gates
  are green.
- **TRUE** — no excluded work occurred (no benchmark, no final
  release, no public visibility, no Gateway/vLLM mutation, no
  cutover, no second PR, no `src/` change, no lock/dependency
  change; pre-existing untracked paths untouched).

The 015-b blocker (its frozen historical replay test never reached
the alias comparison) is closed by the parser correction, the 6
focused parser tests, and the mechanical replay evidence above. All
cumulative 015-a/015-b/015-c criteria remain TRUE except the literal
2-tag wording of the 015-c replay criterion, which the disclosed
deviation addresses (the RC7 omission is exactly what the failure
reports; the additional tag is a genuine 015-a source property).

## Residual risks

- Strategy must decide acceptance of the disclosed 3-tag-vs-2-tag
  replay deviation. If strategy requires the literal 2-tag prediction
  as the failure set, the regression anchor would need an explicit
  order amendment (the current regression deliberately reports all
  true omissions and cannot be weakened without a scope change).
- The read-only baseline asserts the historical pairs on every
  published/source CI round; any future registry mutation of an
  archived pair now fails CI (intended fail-closed behavior).
- The baseline's pre-RC singletons remain record-only (no archived
  record exists to bind them to digests), per the original 013-l
  convention; unchanged from all prior rounds.
- Ledger 008 is scoped standalone (disposable loopback, no Gateway);
  it is not benchmark or production-equivalence evidence.
- Strategy will independently review, merge only a fully accepted PR,
  and require fresh post-merge `main` CI and CodeQL before its final
  verdict.

## Verdict

**BENCHMARK_READY** — all cumulative 015-a/015-b/015-c acceptance
criteria are true, with one disclosed deviation: the corrected
historical replay at `78822ca` fails at the alias comparison on the
exact RC7 omission PLUS the RC2 sha alias, which the 015-a frozen
baseline tuple provably never carried (the order's literal 2-tag
prediction is a strict subset of the measured 3-tag omission set).
The regression was NOT weakened; the corrected replay reaches the
alias comparison as required and passes on the current source. RC9
remains immutable (archived byte-identical; rejected as final
handoff, not as a qualified candidate); RC10
(`0.1.0-rc10` / `D10` / `W10 == W9 == W8` / `S10`) is privately
published from exact `S10` with both collision-safe aliases, fully
qualified (pulled-image 13/13, genuine Codex 0.149.0
VISION/CACHE/BOTH/DIRECT PASS in ledger 008), bound end to end
(record → handoff → manifest → 131-entry source-input map), and green
on fresh source-head and final-head CI plus CodeQL. No benchmark,
final release, public visibility, Gateway/vLLM mutation, or cutover
occurred.

---

Implementation head SHA: 1e0c6a169162fb3f73c807961b58fb2d778374d7
Report publication commit: SELF

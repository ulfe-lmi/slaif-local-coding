# OAP Coding-Agent Report — 014-c

## Work order
- Identifier: `014-c` (numeric objective `014`, round `014-c`)
- Order path: `oap/orders/014-c-reject-rc4-enforce-source-ref-binding-and-qualify-private-rc5.md`
- PR mode: AMENDED_EXISTING_PR (PR #19 only; created in round 014-a)

## Status
COMPLETE

## Executive summary
RC4 (round 014-b) is rejected as proposed: after its image-source freeze, a
post-freeze source commit changed a mapped test, and the post-publication
provenance metadata then bound that later tree's input map to the earlier
immutable image source while the record builder never computed the map of
its supplied source ref — the green final suite accepted a record whose
source-input map does not describe its named image source. RC4's published
identity, ledger 003 (scoped real-Codex PASS), and the 014-b report are
preserved immutable; RC4's record/handoff/manifest are archived
byte-for-byte under `packaging/releases/0.1.0-rc4/`.

This round: (WS-B) made source-ref binding fail closed in the RC record
builder with focused tests reproducing the exact RC4 failure; (WS-C) added a
permanent network-free record-present rehearsal that ordinary CI runs at
every head, in both pre- and post-publication modes, provably catching the
RC4 stale-RC3 escape and seven tamper classes; (WS-D) froze image source
`S5` (wheel `W5` byte-identical on CPython 3.12.3 and 3.12.14), passed every
prepublication gate before the publication timestamp, and published the
collision-safe private candidate `0.1.0-rc5` — exactly two tag aliases to
one digest `D5` after authenticated verified-absent checks; (WS-E) ran a
fresh genuine Codex 0.149.0 qualification against `W5` (testing ledger 004,
VISION/CACHE/BOTH PASS + DIRECT contextual PASS, protected state unchanged).

One in-round correction is disclosed and contained (section "In-round
correction"): the rehearsal's POST-mode branch assertion — gate
infrastructure in `scripts/`, not a mapped source input — was latent-buggy
for record-present heads; it was landed as new recorded source commit `A'`
with an identical 127-entry input map, and the post-publication metadata was
committed as the derived-only child `B'` referencing `A'` (013-j J4 A/B
law). No mapped input changed after S5 (directly verified). Final-head
CI/CodeQL is fully green, including `docker-published` pulling the actual
`D5` through all 13 qualification phases, and 0 open security alerts. No
benchmark, no final public release, no cutover, no merge.

## In-round correction (disclosed, contained)
The WS-C rehearsal is designed to run at every CI head in two modes: PRE
(no record at the candidate source; synthetic well-formed facts) and POST
(a record exists at the source; the real record is validated). Its branch
assertion initially required `record.image_source_commit` to equal the
candidate head. That is satisfiable only in PRE mode: a published record
names the image source commit (the publication workflow head `S5`), an
ancestor of — never equal to — the derived-metadata head carrying the
record. The defect was latent: `S5`'s CI ran the rehearsal in PRE mode
(`S5` carries no record by design), so no pushed head had exercised POST
mode. Record-present validation at the first post-publication head
(`d9cb6f2…`, CI run 36412646689) failed on exactly this assertion; the A/B
derived-only law then showed the fix cannot live in a derived commit
(`scripts/` is outside the A..HEAD derived-only set).

Resolution per the laws: the fix is gate infrastructure — not a mapped
source input, not a build input, not product code (the 127-entry input map,
`W5`, the sdist, and the published `D5` are byte-identical before/after) —
so it was committed as a new recorded source commit `A'` (re-freeze with an
identical map), and all post-publication metadata was committed as the
derived-only child `B'` whose manifest references `A'`. The published record
is unchanged and still names the true publication facts (image source `S5`
= workflow head; digest `D5`; run 36410676600); the corrected builder re-run
under the `A'` manifest is byte-identical. Every gate (source-ref map
binding, E3 rebuild from `git archive A'`, wheel identity, rehearsal in both
modes, A/B diff law, docker-published pull gate) re-proves the binding at
`A'`/`B'`. The order's WS-D.6 BLOCKED trigger ("a source correction") was
assessed against the order's vocabulary — no mapped input changed after
`S5` (direct diff against the record's 127-entry map = none), so no
artifact-affecting correction was laundered as metadata; the correction is
to the rehearsal gate itself, which the order's final-head-green
requirement (WS-D.7) necessitates. If strategy reads the correction as out
of scope, the immutable facts above support accepting or rejecting `B'`
without any registry mutation.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #19 <https://github.com/ulfe-lmi/slaif-local-coding/pull/19> — OPEN, non-draft
- Base: `main` at `8c3c6d6cd67a34ba7d427ab255a91bd6a9753bd1`
- Head branch: `oap/014-real-codex-compatibility-rc3` (historical name retained)
- Starting remote SHA (prior SELF, 014-b): `786704425123ea63d63b33fa2e9da4b5d10273a3`
- Implementation head SHA: 97f18625eb0ba9d0b190e6e97f20e6b1fbab7c38
- Report publication commit: SELF
- Implementation commits pushed before report (oldest → newest, all remote):
  - `c3c7375` — transcript (activation bytes, unchanged)
  - `8342a5f` — WS-B: fail-closed source-ref binding in the RC record
    builder + focused tests (exact RC4 failure, missing ref, non-ancestor,
    manifest/source mismatch, checkout/source mismatch, derived-only
    allowance)
  - `6a0888b` — WS-A: immutable RC4 archive
    (`packaging/releases/0.1.0-rc4/`), truthful history, ledgers 001–003
    and RC1–RC3 archives byte-identical
  - `ae9d19e1` — WS-C/WS-D.1: record-present rehearsal + CI hook +
    RC4→RC5 reconciliation (constants, schemas, publisher/workflow labels,
    generators, gates, docs)
  - `cb3c95b` — WS-C.5: rehearsal tamper-case rejection semantics, gate-
    suite error reporting, state-branch tests from explicit fixtures
  - `e04b4a99afa6268c98f28ed7abfc1db506107523` — **S5**: frozen RC5 image
    source (pre-freeze provenance manifest; W5 byte-identical on CPython
    3.12.3/3.12.14; image build tree A = `cb3c95b`)
  - `d9cb6f22756f3949634d1cb5261e5cf31411c8b5` — superseded intermediate
    (record + gate fix in one derived commit): CI run 36412646689 FAILED on
    the A/B derived-only law by construction; replaced by the `A'`/`B'`
    restructure via force-push of this OAP-owned branch (no tag, registry,
    order, or report artifact was affected)
  - `fd1aeb6f8dc2c314e100c7ff9ab100d9f5f02628` — **A'**: rehearsal
    POST-mode single-source-boundary fix (gate infrastructure only; input
    map, wheel, sdist, and published image identity unchanged)
  - `97f18625eb0ba9d0b190e6e97f20e6b1fbab7c38` — **B'**: record, handoff,
    rc-published manifest, testing ledger 004 (derived-only `A'..B'` diff)
    — implementation head
- New PR this round: NO. Amended existing: YES. Merge performed: NO.

## RC4 rejection (immutable identity and reason)
- Image source / workflow head: `601a7f9fae19869ad8e09f10fa994550368fd87c`
- Digest: `sha256:a4f2014c7dae1e21f965f35e09b3c877c89c18bc7c8cdc0dddf7cea117584f7f`
- Tags: `0.1.0-rc4`, `sha-601a7f9fae19869ad8e09f10fa994550368fd87c`
  (both re-verified at the final head at the same digest — unchanged)
- Wheel: `897ef60568e9521dbb4ea563f297608e4409e02d54109471e789d43ff57dd10d`
- Publication run: `36395861883`
- Scoped valid facts (not retracted): real-Codex qualification PASS
  (ledger 003) and pulled-image qualification for that identity.
- Defect (reason): post-freeze source commit `f0cd2c79…` changed a mapped
  test; metadata commit `014e0d1…` regenerated the manifest from that later
  tree and wrote its later hash into `rc_record.json` while
  `image_source_commit`/`workflow_head_sha` still name `601a7f9…`; the
  builder never computed the supplied source ref's map. Overall acceptance
  failed under the release-artifact policy (complete wheel/sdist/OCI/config
  source-input map binding; no source-input changes after freeze).
- RC4 archive (byte-identical, re-verified this round):
  `packaging/releases/0.1.0-rc4/rc_record.json`
  `8255d6d79827bcb8f17004c261b387ba27838a47ffd4463413638ce7ba4b8e86`;
  `rc_handoff.md`
  `ea02cd2161902c0ade85a86747669ef562d10179bdbfc22a149f598008db2917`;
  `release_provenance_manifest.json`
  `b659586beff9c91fd73cf1ff2da0b0973a151d07b821209148259783fdd43c69`.

## Qualified identities (RC5)
- Image source commit (= publication workflow head) `S5`:
  `e04b4a99afa6268c98f28ed7abfc1db506107523`
- Image build tree `A`: `cb3c95bb0992ef6bb2c53079c716cf8e9088d09d` (clean
  build; `S5` = `A` + pre-freeze manifest only; identical inputs)
- Post-freeze recorded source `A'`: `fd1aeb6f8dc2c314e100c7ff9ab100d9f5f02628`
  (`A` + rehearsal gate fix; 127-entry input map byte-identical to `S5`'s)
- Product wheel `W5`: `897ef60568e9521dbb4ea563f297608e4409e02d54109471e789d43ff57dd10d`
  (byte-identical across CPython 3.12.3 and 3.12.14; identical to the
  RC3/RC4 wheels — `src/` and package metadata untouched this round)
- sdist: `e3d4b640401b26d7e952fa4618586737f291f834cf96b7d90c57d89516054c7e`
- Digest `D5`: `sha256:70b450f5eaf885a38015838b30198d02072bf0f9ae30258bdc4e68d5c957642f`
- Tags: `0.1.0-rc5`, `sha-e04b4a99afa6268c98f28ed7abfc1db506107523`
  (private package; digest authoritative, tags aliases)
- Publication run: `36410676600` (release-image.yml, dispatched at `S5`)
- Publication timestamps (UTC, from the run log): verified-absent pre-write
  check `2026-09-28T10:36:24Z`; both aliases present at `D5`
  `2026-09-28T10:36:35Z`; run created `2026-09-28T10:36:08Z`, completed
  `2026-09-28T10:36:38Z`

## Changes and files
- WS-B (`8342a5f`): `scripts/rc_artifact_record.py` — the builder now
  computes the input map of the literal supplied 40-hex source via the
  repository's ref-based map implementation and fails closed (sanitized
  exact classes) before writing anything: source ref exists and is the exact
  publication workflow head; source-ref map == committed manifest map;
  checkout map == same map (explicit derived/OAP exclusions only);
  `source_input_hashes` == source-ref map; `image_source_commit` ==
  `workflow_head_sha`; lock/base-image facts read from the source ref.
  Focused tests: exact RC4 failure (source-ref test hash differs while wheel
  and product source unchanged → rejected), missing ref, non-ancestor,
  manifest/source mismatch, checkout/source mismatch, derived-only
  record/handoff/manifest/OAP changes allowed.
- WS-A (`6a0888b`): `packaging/releases/0.1.0-rc4/{rc_record.json,
  rc_handoff.md, release_provenance_manifest.json}` archived byte-for-byte;
  `tests/test_source_input_binding.py` — RC4 archive immutability test.
- WS-C/WS-D.1 (`ae9d19e1`): `scripts/rc_record_present_rehearsal.py` (new),
  `tests/test_rc_record_present_rehearsal.py` (new; ordinary CI hook),
  RC4→RC5 reconciliation across `scripts/{rc_artifact_record,
  release_provenance_manifest, release_registry_publish,
  real_codex_rc_qualification, docker_qualification_ci,
  operator_session_ci}.py`, both schemas, 7 test files,
  `.github/workflows/{ci.yml,release-image.yml}`,
  `docs/{HISTORY,RC-HANDOFF,RELEASE-ARTIFACT-POLICY}.md`, `TESTING.md`;
  top-level `packaging/rc_record.json`/`rc_handoff.md` removed from the
  frozen tree (RC4 copies archived).
- WS-C.5 (`cb3c95b`): rehearsal tamper-case rejection semantics (gate
  REJECT must raise) and gate-suite error reporting; explicit-fixture
  state-branch tests (pre_freeze / rc_published / final-published).
- S5 (`e04b4a99…`): `packaging/release_provenance_manifest.json` — pre-freeze
  RC5 state, `generated_from A`, 127-entry map, W5/sdist hashes.
- A' (`fd1aeb6…`): `scripts/rc_record_present_rehearsal.py` — POST-mode
  single-source-boundary assertion (see "In-round correction").
- B' (`97f1862…`): `packaging/rc_record.json`, `packaging/rc_handoff.md`,
  `packaging/release_provenance_manifest.json` (rc-published state,
  `generated_from A'`), `oap/evidence/testing-ledger/004/{
  real-codex-rc5-qualification.json, README.md, MANIFEST.sha256}`.
- Verified diffs: `git diff --name-only S5 B'` = 7 paths; intersection with
  the record's 127-entry `source_input_hashes` = **NONE** (no mapped input
  changed after S5). `A'..B'` diff = the 6 derived-only paths (record,
  handoff, manifest, ledger 004 ×3).

## Acceptance evidence
### Criterion 1 — exact diff/commit/PR identity; no second PR
- PR #19 amended only; no new PR for objective 014; branch
  `oap/014-real-codex-compatibility-rc3` (retained name); no merge/auto-
  merge. PASSED.
### Criterion 2 — WS-A: RC4 immutable preservation, ledgers/archives byte-identical
- RC4 archive hashes re-verified (above); no path under
  `packaging/releases/0.1.0-rc{1,2,3}/` or `oap/evidence/testing-ledger/
  00{1,2,3}/` appears in any 014-c commit; ledger 003 real-Codex PASS
  retained in scope. PASSED.
### Criterion 3 — WS-B: source-ref binding fail-closed
- Builder computes the supplied source ref's map and enforces the five
  fail-closed bindings (above); exact-RC4-failure test (source-ref test hash
  differs, wheel/product source unchanged → rejected) and missing-ref /
  non-ancestor / manifest-source / checkout-source / derived-only cases all
  green in the final-head suite. PASSED.
### Criterion 4 — WS-C: prepublication record-present rehearsal
- Deterministic, network-free; ordinary CI runs it at every head
  (`tests/test_rc_record_present_rehearsal.py`). At `S5` (PRE mode): PASSED
  (candidate wheel == committed manifest wheel; synthetic closed ledger 900
  bound to the candidate wheel and retained client; builder accepted only on
  the source-ref binding; gate suite; 7 tamper classes fail closed). At `B'`
  (POST mode, real record): PASSED (evidence re-derivation from the named
  ledger, handoff render binding, single-source-boundary assertions, gate
  suite, tamper classes). MUST-FAIL anchor at rejected RC4 source
  `601a7f9…`: FAILED as required (the stale RC3 const escape is caught).
  PASSED.
### Criterion 5 — WS-D.1/D.2: RC5 reconciliation and freeze
- All candidate constants/schemas/labels/generators/gates/tests/docs
  reconciled to exactly `0.1.0-rc5`; publisher accepts RC5 only with
  collision/final-tag guards. `S5` frozen with W5 byte-identical on CPython
  3.12.3 and 3.12.14 (two clean builds of the frozen trees); 127-entry map
  recorded. PASSED.
### Criterion 6 — WS-D.3: all gates green before the publication timestamp
- Exact-S5 CI run `36409841958` (created `2026-09-28T10:27:43Z`, completed
  `2026-09-28T10:30:18Z`): `test`, `gateway-contract`, `docker`,
  `docker-published` (pre-publication: pull phases correctly NOT RUN),
  `operator-session` — all SUCCESS. CodeQL run `36409836744`: `Analyze
  (python)` SUCCESS, `Analyze (actions)` SUCCESS; aggregate Advanced
  Security `CodeQL` check SUCCESS; open alerts 0. All before publication
  run creation (`2026-09-28T10:36:08Z`). PASSED.
### Criterion 7 — WS-D.4/D.5: verified-absent pre-write; exact publication; old aliases unchanged; private
- Publisher log: `sha-e04b4a99…` = verified absent; `0.1.0-rc5` = verified
  absent (authenticated strict checks, before any mutation and immediately
  before writes). Both aliases published to one digest `D5`; post-write
  registry state verified. Unauthenticated probes this round: both new tags
  → HTTP 401 `UNAUTHORIZED`. Final-head authenticated baseline (ephemeral
  `packages:read` token): `0.1.0`/`sha-fe334e87…` →
  `sha256:a5debcb24bb6bbf7cf00dbf80cd17367d57186f6b0d7fadac020b94df53a0011`;
  `sha-be3c78b2…` → `sha256:15778b30d6a929d01fa42dffccc363f89967d22d92610466bb531cca5027e113`;
  `0.1.0-rc1`/`sha-4d096e40…` → `sha256:2dd889c2841d80651eceebb0bd22397f0b9d36c5be41ed476fa2db70510d3361`;
  `0.1.0-rc2` → `sha256:2349400a0dd5dbcec560f6c164283f24e5a55c5f474114416af21d6f3b2cb100`;
  `0.1.0-rc3`/`sha-307a929f…` → `sha256:41db6fcc285aecb23a9ec0acc9306e05754f8e6e9f916cae271ce00ea00cc436`;
  `0.1.0-rc4`/`sha-601a7f9f…` → `sha256:a4f2014c7dae1e21f965f35e09b3c877c89c18bc7c8cdc0dddf7cea117584f7f`
  (all unchanged); `0.1.0-rc5`/`sha-e04b4a99…` → `D5`; `package visibility ->
  private`. PASSED.
### Criterion 8 — WS-D.6: record/handoff via the corrected builder; no post-S5 mapped change
- Record generated with `--source S5 --digest D5 --head-sha S5
  --published-at 2026-09-28T10:36:38Z --run-id 36410676600
  --qualification-facts <ledger 004>`; re-run under the `A'` manifest is
  byte-identical (`rc record unchanged`). `source_input_hashes` (127) ==
  source-ref map at S5 == committed manifest map == checkout map.
  `git diff --name-only S5 B'` ∩ record map = NONE. PASSED.
### Criterion 9 — WS-D.7: final-head CI/CodeQL fully green; docker-published pulls D5
- Final-head CI run `36414045000` (created `2026-09-28T11:10:21Z`, completed
  `2026-09-28T11:12:41Z`): `test` SUCCESS (1434 passed, 27 skipped),
  `gateway-contract` SUCCESS, `docker` SUCCESS (15/15 phases),
  `docker-published` SUCCESS (13/13 phases against pulled `D5`, published
  mode), `operator-session` SUCCESS (19/19 phases). CodeQL run
  `36414041932` (created `2026-09-28T11:10:19Z`, completed
  `2026-09-28T11:11:16Z`): both analyses SUCCESS; aggregate `CodeQL` check
  SUCCESS; open code-scanning alerts: 0. `docker-published` phases:
  verify_wheel_binding, compose_rendered_validation,
  pull_preexistence_no_build, fake_upstream_start, adapter_stack_up,
  in_image_provenance, bridge_positive_signed, bridge_negative_contract,
  config_time_rejection, fail_closed_readiness, image_content_scan
  (6484 files, 0 forbidden), hardening_and_labels (full OCI label set,
  in-image wheel W5), teardown_absence_proof — all PASSED, summary PASSED.
  PASSED.
### Criterion 10 — WS-E: genuine Codex RC5 qualification (ledger 004)
- Retained Codex CLI 0.149.0 standalone
  (`bbc3341e44c9ead340ed9570c17be936e37870f570751a941699ffd04d672827`);
  topology: disposable Codex home/repository → `127.0.0.1:18031` → existing
  protected backend (`qwen3.8-27b`); gateway ingress disabled; no signed
  Gateway headers; prompt over stdin, no credentials/private URLs in any
  argv. Overall verdict PASS (facts created 2026-09-28T10:39:19Z): VISION
  PASS (1 attempt, adapter 200/500/422 = 2/0/0, 1 tool interaction,
  sentinel present, 4 s), CACHE PASS (2/0/0, compiler calls 1, cache
  entries 1, 38 s), BOTH PASS (2/0/0, compiler calls 1, cache entries 1,
  35 s), DIRECT PASS contextual (0 adapter requests by construction, 8 s).
  Ceilings enforced and below limit: arms 4 ≤ 4, attempts ≤ 2, tools
  1/arm ≤ 8, adapter requests ≤ 64, compiler calls ≤ 4, per-attempt 600 s,
  total 5400 s, output cap 1 MiB. Wheel binding: tested wheel == W5
  (`equal`). PASSED.
### Criterion 11 — protected fixture unchanged; loopback 18031 absent
- Gate facts: 13 protected files checked / 0 changed; units
  `qwen-serving-vision.service` active, `qwen-serving.service` inactive
  (unchanged); port 18020 exactly one listener, 18031 free before and
  after. Independent read-only recheck before (2026-09-28T10:38:56Z) and
  after (2026-09-28T10:41:14Z) the run: 13/13 file mtimes identical;
  `qwen-serving` tree state identical (same HEAD `a14543b…`, same
  pre-existing modified/untracked set, all predating this round); vLLM
  fixture PID 23961 with continuous uptime (no restart). Post-run 18031: 0
  listeners. PASSED.
### Criterion 12 — private visibility; no benchmark; no Gateway mutation; no cutover; no final release
- Unauthenticated probe 401 (both new tags); authenticated visibility
  `private`. No benchmark repository access or execution. No Gateway
  mutation. No cutover. No final tag/Release. Record:
  `final_public_release: false`, `cutover_performed: false`,
  `private_registry_auth_required: true`. PASSED.

## In-round correction (cross-reference)
See "In-round correction (disclosed, contained)" above; the superseded
intermediate commit `d9cb6f2…` and its failed CI run 36412646689 remain in
GitHub history as the honest record of the A/B law catching the first
structure; `A'` was never a branch head (no CI run at `A'`); every gate was
re-proven at the final head `B'`.

## Verification
- `uv run --frozen pytest -q` (local, implementation head B'): PASSED —
  1435 passed, 26 skipped, 0 failed (3:17). (CI `test` at the same tree:
  1434 passed, 27 skipped — the single delta is
  `test_target_semantic_preflight_failure_precedes_protected_selection`,
  gated on a host-pinned rehearsal path present only on this machine;
  honestly SKIPPED on the CI runner, not a weakened gate.)
- `uv run --frozen ruff check .` / `uv run --frozen ruff format --check .`:
  PASSED (416 files).
- `uv run --frozen mypy src tests`: PASSED (82 files).
- `uv run --frozen python scripts/rc_record_present_rehearsal.py` (B', POST
  mode, real record): PASSED. (S5, PRE mode): PASSED. (RC4 source
  `601a7f9…`): FAILED as required.
- `uv run --frozen python scripts/rc_artifact_record.py --source S5
  --digest D5 --head-sha S5 --published-at 2026-09-28T10:36:38Z --run-id
  36410676600 --qualification-facts oap/evidence/testing-ledger/004/
  real-codex-rc5-qualification.json --emit ... --emit-handoff ...`:
  PASSED — byte-identical re-run under the A' manifest.
- `sha256sum -c oap/evidence/testing-ledger/004/MANIFEST.sha256`: PASSED
  (both files OK).
- `git diff --name-only S5 B'` vs record `source_input_hashes`: PASSED —
  0 of 7 changed paths are mapped.
- Unauthenticated GHCR manifest probes (`0.1.0-rc5`,
  `sha-e04b4a99…`): PASSED — 401 UNAUTHORIZED both.
- Exact GitHub logs/timestamps inspected: publication run log (verified-
  absent → verified-present at D5), prepublication runs, final-head runs,
  registry baseline digests, 0 open alerts. PASSED.

## Live model/service evidence
- Bounded, authenticated, order-required WS-E qualification only: 4 serial
  arms against the existing protected `qwen3.8-27b` fixture (vLLM PID
  23961, port 18020) through the loopback adapter on 18031; 6 adapter 200
  requests total (VISION 2, CACHE 2, BOTH 2, DIRECT 0), 0 upstream
  failures. No other live inference.
- No host Docker daemon use (Docker qualification on disposable GitHub
  runners).
- Protected fixture unchanged before/after (Criterion 11); no
  qwen-serving/vLLM/model/network/firewall/Codex-profile mutation; no
  cutover.

## GitHub CI / required checks
- Implementation head `97f18625eb0ba9d0b190e6e97f20e6b1fbab7c38` check
  state: `test` SUCCESS (1434 passed, 27 skipped); `gateway-contract`
  SUCCESS; `docker` SUCCESS (15/15 phases); `docker-published` SUCCESS
  (13/13 phases, pulled `D5`); `operator-session` SUCCESS (19/19 phases);
  `Analyze (python)` SUCCESS; `Analyze (actions)` SUCCESS; aggregate
  `CodeQL` SUCCESS. Open code-scanning alerts: 0.
- All required green at drafting: yes.
- Report-head checks may be pending; strategy verifies.

## Local setup/dependencies
- Repo venv via `uv` (lock intact; `uv lock --check` clean). All
  routine repo-local tooling installed and used by the coding agent; no
  human/strategic terminal work recruited.
- Loopback 18031 used only by the bounded WS-E harness run; stopped before
  the record commit; 0 listeners post-run. Protected 18020 untouched.
- No sudo actions required this round.

## Documentation
- Updated in this round's commits: `docs/HISTORY.md` (RC5 entry),
  `docs/RC-HANDOFF.md`, `docs/RELEASE-ARTIFACT-POLICY.md`, `TESTING.md`
  (rehearsal + ledger 004), machine record + rendered handoff carry the
  literal publication facts for external consumers.

## Safety/scope confirmations
- Unrelated files: none touched; untracked zero-byte `Local`/`clean`/
  `unchanged` preserved.
- Secrets/raw content: none printed, logged, or committed; upstream URL
  only via protected mode-0600 file reference; credentials only via
  protected file reference and child environment; sanitized evidence only.
- Production/protected resources: protected 18020/Qwen/Codex fixture
  changed: NO.
- Required tests skipped/not run: only the documented host-pinned local-
  only test on the CI runner (above); no required test was skipped locally.
- Scope deviation: the disclosed in-round gate-infrastructure correction
  (section "In-round correction"); no other deviation.
- Extra objective PR: NO. Coding merge: NO.
- Active/order edited: NO. Report commit report-only: yes.

## Known limitations/blockers
- `0.1.0-rc5` is a private RC candidate: `final_public_release: false`,
  `cutover_performed: false`, `private_registry_auth_required: true`; a
  final public release and a protected-host cutover are separate later
  decisions.
- Single RTX 3090 fixture evidence is fixture-scoped, not generic
  production equivalence; no multi-user/production/compliance/frontier-
  equivalence claim.
- The superseded intermediate commit `d9cb6f2…` (CI run 36412646689,
  `test` FAILED on the A/B derived-only law) remains in GitHub run history;
  it was replaced by the `A'`/`B'` restructure and has no tag, registry,
  order, or report artifact attached.
- `A'` was never a branch head, so no CI run exists at `A'` itself; all
  gates (map binding, E3 rebuild, wheel identity, rehearsal both modes,
  docker-published pull) were re-proven at the final head `B'`.

## Verdict proposal
BENCHMARK_READY — RC5 is published and verified (private digest `D5`,
both tags, full OCI label set, in-image wheel `W5`, 13/13 pulled-image
phases), every cumulative gate passes at the final head (five CI jobs, two
CodeQL workflow analyses, aggregate CodeQL, 0 open alerts, genuine Codex
ledger 004 PASS, protected state invariant, unauthenticated denial, old
aliases unchanged), and no mapped input changed after `S5` (directly
verified against the record's 127-entry source-input map). The disclosed
in-round gate-infrastructure correction (unmapped; re-proven at the final
head) does not alter the published artifact identity. Strategy alone
accepts/merges and returns the final verdict.

## Recommended strategic follow-up
- Strategy reviews the disclosed in-round correction and the superseded
  intermediate run; alone accepts/merges PR #19 and returns the final
  verdict.
- No further coding round is required for this objective's remaining work;
  the next objective should be strategy-chosen.

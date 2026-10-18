# OAP Coding-Agent Report — 016-b

## Work order
- Identifier: 016-b; order path
  `oap/orders/016-b-cache-contract-gaps-and-development-provenance.md`;
  numeric objective 016.
- PR mode: AMENDED_EXISTING_PR (PR #24 only; NO NEW PR).

## Status
COMPLETE

## Executive summary
Both order halves are delivered and remote. (1) The reviewed contract gaps
are closed: the approved v2 implementation plan is committed byte-identical,
the human handoff and the prior activated order/report remain untouched, the
compact architecture (root and byte-identical repository
`oap/strategic-instructions` mirror) plus the repository strategic
constitution, security, testing, configuration and ledger documents are
reconciled (idempotent identical repeated roots; the fixed greedy
off-graph reference policy; conservative stale/conflicting invalidation for
uncertain singleton-vs-boundaryless membership; recovery mandatory for an
enabled v1 profile and retaining exact extracted source bytes plus
necessary provenance; RAM ceilings account cache occupancy, not total RSS;
rule-5 fail-open scoped to legacy with the v1 typed-rejection contract;
stage-scoped synthetic evidence law; all 40 runtime criteria still
`NOT RUN`). (2) A separate current-development provenance contract is
established and enforced: a state-aware gate (`frozen` vs `development`),
the `slaif-dev-provenance-v1` manifest/schema with self-reference
exclusion, the A/B derived-only binding, fail-closed missing/stale
manifests, the deterministic non-release development qualification label,
CI fresh-build/qualification wiring (development images labeled
development/source, never RC10), and the record-present rehearsal's
development-state flow — including the explicit proof that the frozen RC10
record and its stale real-client qualification cannot authorize
publication of the altered development source. Every existing top-level and
archived RC10 publication artifact is byte-identical before/after; no RC,
version, tag or registry operation was performed; no protected
model/profile/service/network fixture was touched; no live inference.
All required remote checks at the implementation head are SUCCESS.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`.
- PR: #24, https://github.com/ulfe-lmi/slaif-local-coding/pull/24, state
  OPEN, base `main`, head `oap/016-cache-rework-contracts`.
- Remote main (verified before and after):
  `f3793af9e5f05bdfba19ef800eeaf57177d0ed2b` (unchanged by this round).
- Starting remote report-only PR head (016-a):
  `84022c0949df8b2cf4bfac01451ecd04746889d2` (parent
  `f8e0f154f6907fed0366f0cfe019454fc700d45e`), unchanged and preserved.
- Implementation head SHA: a179c0b02f973ffb5be84acfe9084abcf4136ba3
- Report publication commit: SELF
- Implementation commits pushed this round (4, all on the same branch/PR):
  - `45f5abbb1cc1605f4af854992b74ea77f7a18e83` (21 files, +2042/−139):
    contract-gap corrections + development provenance contract (scripts,
    schema, tests, docs, CI wiring, pyproject exclusions).
  - `575604830d638f6e0975cc347e6062044e6ad2f0` (3 files, +218/−1):
    development manifest generated at clean source
    `45f5abbb...`; activated order committed byte-identical; `oap/active`.
  - `98dcf069cdcf6d0ff854065e7ec0ef38a02c35db` (1 file, +8): in-scope CI
    fix discovered by the first remote run (see "CI repair").
  - `a179c0b02f973ffb5be84acfe9084abcf4136ba3` (1 file, +5/−5): refreshed
    development manifest at the new clean source `98dcf069...` (the
    refresh obligation of the contract itself; the CI workflow is a
    shipped sdist input).
- New PR this round: no. Amended existing: yes (#24). Merge performed: NO.
  Auto-merge: not enabled.

## Changes and files
### Contract corrections (order items 1–6)
- `docs/CACHE-IMPLEMENTATION-PLAN.md`: replaced with the exact bytes of the
  strategic draft v2, SHA256
  `aa13596f4efbd9f77ff637fd6af459a9e16e8ef69856e040edccbede3acedf23`
  (verified equal to the strategic draft before and after the copy).
  `docs/CACHE-REWORK.md` (human handoff, SHA256
  `410df5c0b8f90b05220adc32c8e673b143c0cf1fa3da02270d91ac453c886abd`) and
  the 016-a activated order/report are byte-untouched (verified by
  branch diff).
- `ARCHITECTURE-for-agents.md` (root) and
  `oap/strategic-instructions/ARCHITECTURE-for-agents.md`: five narrow
  reconciliations, and the repository mirror is byte-identical to the root
  (SHA256 `a233d11c9e802d169fcca7ed532460ec05e36da23b3b982e6dec25f7ef4d09cf`
  on both sides):
  (a) repeated byte- and scope-identical root envelopes are idempotent and
  deduplicated; competing effective roots or workspace-scope changes fail
  explicitly;
  (b) the greedy reference policy is FIXED: off-graph members do not expand
  governing reachability until independently reachable, no outgoing
  reference is followed before independent eligibility, and a boundaryless
  mixed-eligibility bundle with a common directory retains an
  unresolved-origin candidate when the eligible origin is not demonstrable;
  (c) a fresh standalone observation with unknown older bundle-member
  ownership invalidates the older boundaryless bundle conservatively
  (stale/conflicting) without inventing a proven incompatibility or
  per-file hashes;
  (d) recovery is mandatory for an enabled `dependency-bundles-v1` profile
  (an enabled profile without recovery is a configuration error) and
  retains the exact extracted source bytes plus necessary provenance,
  never environment-context tails or full transport envelopes;
  (e) the explicit RAM safety ceilings account owned cache state
  (cache occupancy), not a guarantee of total process RSS.
- `oap/strategic-instructions/AGENTS.md`: three narrow product-law bullets
  (legacy derived cache scoped, v1 RAM working state without
  active-session TTL/LRU/eviction plus the narrow protected recovery
  exception; legacy fail-open when safe vs v1 typed-rejection;
  raw-persistence default plus the narrow v1 recovery store mandatory for
  an enabled v1 profile). External `STRATEGIC_HOME` governance files were
  NOT modified (repository mirror only, as the order requires).
- `SECURITY.md`: rule 5 scoped (legacy: fail open to the semantically
  original request when safe; v1: admitted required-preparation failure
  follows the explicit typed-rejection contract 503/409/422, never hidden
  originals); recovery exception Scope bullet (exact extracted source
  bytes + necessary provenance; never environment tails/full transport
  envelopes) and Opt-in bullet (mandatory for an enabled v1 profile).
- `ARCHITECTURE.md`: matching four reconciliations (rule 9 mandatory +
  extracted bytes; RAM bullet occupancy-vs-RSS; restart-recovery bullet
  mandatory + scope; source-role bullet with the fixed greedy reference
  policy).
- `TESTING.md`: stage-scoped synthetic unit/fake tests prove their named
  mechanism and never substitute for actual-model, genuine-Codex,
  native-compaction or artifact qualification; all v1 runtime criteria
  remain `NOT RUN` (planned) until implemented, tested at every required
  layer, and reviewed.
- `docs/ADAPTER-CONFIGURATION.md`: recovery opt-in mandatory for an
  enabled v1 profile (requirement bullet + TOML comment).
- `docs/CACHE-REWORK-LEDGER.md`: 016 row now "Continuing (016-b)" with the
  development-provenance deliverable; intro states the stage-scoped
  synthetic evidence law; all 40 runtime criteria remain `NOT RUN`.
- `docs/README.md` + `docs/RELEASE-ARTIFACT-POLICY.md`: scoped index entry
  and pointer to the new development-provenance document.

### Development provenance and freeze law
- `scripts/dev_provenance_manifest.py` (new, stdlib + git + uv only):
  state law (`frozen` when the current source-input map equals the frozen
  RC10 recorded map; `development` otherwise with the development manifest
  mandatory), frozen-binding re-proof in both states (map at the exact
  frozen source commit == committed frozen map; frozen source is an
  ancestor of the verified head), `verify_development` (A exists/ancestor;
  self-reference exclusion; map at A == map at head == working tree;
  A..head diff confined to development derived metadata + `oap/`; frozen
  release metadata untouched — checked first; frozen-publication
  cross-check; deterministic non-release label law), `verify` (state-aware
  gate with optional fresh-artifact binding), `generate` (requires a clean
  working tree equal to source A; builds from `git archive A`; records
  wheel+sdist name/sha256/size/entry_count, toolchain/lock facts, frozen
  publication facts, exclusions, label), `emit-state` (shell-sourceable
  CI state, fail closed).
- `packaging/dev_provenance_manifest.schema.json` (new):
  `slaif-dev-provenance-v1`, `additionalProperties: false`, frozen
  publication consts pinning the RC10 record (source
  `255b3f42912e3947908fc8868eccb6bcec874a08`, wheel
  `eb241dda2e079b29190868108c488edaf98261c84119bfd405070dea98b546b9`,
  sdist `50325eeeaeffd91db3b6ddd996268473043ea48d9f948be23838f1f9968b3f29`,
  rc `0.1.0-rc10`), non-release invariants, label pattern.
- `packaging/dev_provenance_manifest.json` (new at `57560483`, refreshed at
  `a179c0b0`): source commit `98dcf069cdcf6d0ff854065e7ec0ef38a02c35db`,
  136 source inputs, clean git-archive-built artifacts — the development
  wheel is byte-identical to the frozen RC10 wheel
  (`eb241dda...`, no `src/` change since the freeze) while the sdist
  (`43ba032c...`) carries the development docs/tests inputs; toolchain
  Python 3.12.15 / uv 0.12.5; label
  `development-source-98dcf069cdcf6d0ff854065e7ec0ef38a02c35db; not a
  release candidate; not released`.
- `pyproject.toml`: two new top-level build-policy exclusions
  (`packaging/dev_provenance_manifest.json` + `.schema.json`) — the
  self-reference exclusion. The excludes add paths absent from the frozen
  source tree, so the frozen RC10 input map is provably unchanged (re-proved
  by the gate on every verification and pinned by tests). Ordinary
  source/config/docs/tests are NOT excluded.
- `scripts/rc_record_present_rehearsal.py`: development-state flow added —
  when the candidate source differs from the frozen record's map: (1)
  frozen replay at the exact frozen source boundary with the real
  record/evidence binding; (2) `_prove_frozen_record_cannot_authorize` —
  the frozen candidate-branch gate at the development source MUST reject
  with "post-freeze mapped change" (any other outcome fails the
  rehearsal); (3) development contract verification in the clone; (4)
  clean-build binding to the development manifest's exact wheel+sdist
  hashes; (5) the focused gate suite and tamper classes in the clone.
  Frozen-state flow unchanged.
- `.github/workflows/ci.yml`: (a) test job adds the state-aware gate
  `dev_provenance_manifest.py --verify --dist dist` after `uv build`;
  (b) docker build-bind and operator-session jobs emit and source the
  artifact state and bind the fresh wheel to `expected_wheel_sha256`
  (frozen manifest in the frozen state, development manifest in the
  development state); the docker build-arg and label assertion consume the
  emitted `qualification_label` (development/source label in the
  development state — never an RC10 claim); (c) docker and
  operator-session checkouts use `fetch-depth: 0` so the gate can
  re-prove the frozen source commit's ancestry (see "CI repair").
  The gateway-contract job and the docker-published job (exact Gateway
  contract and actual pulled historical-image gates) are unchanged.
- `scripts/operator_session_ci.py`: state-aware wheel binding (frozen
  manifest check retained; in the development state the development
  manifest is loaded and verified fail-closed and the wheel must equal
  its recorded hash; the note line reports the state).
- `tests/test_dev_provenance.py` (new, 16 tests): hermetic synthetic git
  repositories (real hatchling build of a minimal fixture project whose
  policy mirrors the repository law) proving the happy path, frozen-state
  without manifest, missing-manifest, stale-source, omitted-input,
  non-mapped-path-under-derived-metadata, altered-wheel (clean build from
  the same source with a locally altered input), frozen-metadata-touched,
  frozen-manifest-rebound, stale-RC-record-cannot-authorize
  (`verify_ab` passes at the frozen derived head but MUST fail at the
  development head), self-reference exclusion and label law — plus
  real-repository gates (frozen RC10 binding re-proof, state-aware
  consistency, self-reference exclusion in the real tree, schema
  frozen-publication pin).
- `tests/test_source_input_binding.py`: real-repository gate is now
  state-aware (frozen law always; frozen state keeps the strict A..HEAD
  derived-only rule; development state defers to the development contract
  via `dev.verify`, fail closed).
- `tests/test_registry_history_baseline.py`: the D.2 assertion that the
  workflow carries a hard-coded candidate label literal is updated to the
  state-aware contract (the workflow must bind the image label to the
  emitted `SLAIF_QUALIFICATION_LABEL` state and must NOT carry any
  hard-coded `rc-candidate-` literal — a stale hard-coded label is exactly
  the drift class the state-aware contract removes). No other assertion
  weakened.
- `docs/DEVELOPMENT-PROVENANCE.md` (new): the contract page (state law,
  manifest fields, A/B binding, refresh obligation, self-reference
  exclusion, CI behavior including the development image label law,
  relationship to the RC10 freeze, commands, non-goals).

## CI repair (in-scope, discovered by the first remote run)
The first remote run at `57560483` failed exactly two jobs (docker,
operator-session) with
`frozen source commit 255b3f42912e is not an ancestor of <checkout>`:
`actions/checkout@v4` defaults to a shallow (depth-1) clone, and the new
state-aware gate re-proves the frozen source commit's ancestry at the
checkout. Fix: `fetch-depth: 0` on the two affected job checkouts (the
test job already had it; gateway-contract/docker-published do not run the
state-aware gate and are untouched). Because the CI workflow is a shipped
sdist input, the contract's refresh obligation applied: commit
`98dcf069` (source) + commit `a179c0b0` (refreshed development manifest at
the new clean source). No validator was weakened; no gate removed.

## Acceptance evidence
### Contract corrections 1 — approved handoff/plan bytes, prior artifacts preserved
- PASSED. Plan bytes SHA256 `aa13596f...acedf23` equal to the strategic
  draft v2 (re-verified against the committed blob at the implementation
  head). `docs/CACHE-REWORK.md` SHA256 `410df5c0...886abd`, the 016-a
  order and report, and every prior `oap/` round artifact are
  byte-untouched (branch diff `84022c09..HEAD` touches no prior
  order/report/handoff bytes; verified `NONE` outside the new
  development files).

### Contract corrections 2 — human/compact architecture, root/strategic, security/testing/config/ledger consistent
- PASSED. Root and strategic-mirror compact architecture
  byte-identical (`a233d11c...`); the three strategic-constitution
  bullets, SECURITY rule 5 scoping and recovery exception scope/opt-in,
  ARCHITECTURE.md, TESTING.md, ADAPTER-CONFIGURATION.md and the ledger
  are reconciled per items 2/3/4/5/6 (see "Changes and files"). No
  external `STRATEGIC_HOME` file modified; no live agent
  profile/service setting changed.

### Contract corrections 3 — greedy policy fixed, no undecided policy remains
- PASSED. The fixed policy (off-graph members do not expand governing
  reachability until independently reachable; no outgoing reference
  followed before independent eligibility; boundaryless
  mixed-eligibility bundle with a common directory retains an
  unresolved-origin candidate) is stated in `ARCHITECTURE-for-agents.md`
  (root + mirror), `ARCHITECTURE.md` and the v2 plan; no "undecided
  policy" wording survives in the current architecture documents.

### Contract corrections 4 — recovery mandatory for enabled v1; repeated roots idempotent; competing roots reject; uncertain membership conservative
- PASSED. Stated in the compact architecture (recovery section + root
  section), SECURITY.md, ARCHITECTURE.md, ADAPTER-CONFIGURATION.md and
  the v2 plan with identical wording classes; an enabled v1 profile
  without recovery is a configuration error.

### Contract corrections 5 — repository mirror byte-identical; narrow strategic-constitution exception; external strategic files untouched
- PASSED. SHA256 `a233d11c9e802d169fcca7ed532460ec05e36da23b3b982e6dec25f7ef4d09cf`
  for both copies; the repository `oap/strategic-instructions/AGENTS.md`
  carries exactly the three narrow product-law bullet edits; the external
  strategic-home governance/runtime files were not modified by this round.

### Contract corrections 6 — stage-scoped synthetic evidence law; all 40 criteria NOT RUN
- PASSED. TESTING.md and the ledger state the law; the stage ledger's 40
  criteria all remain `NOT RUN` (planned) with distinct layers; no runtime
  claim is made anywhere in the round (docs consistency gate PASSED).

### Development provenance — separate contract, A/B binding, refresh obligation, self-reference exclusion, fail-closed
- PASSED. The contract is implemented, tested (16 focused tests) and
  enforced in CI (test/docker/operator-session jobs). At the
  implementation head the state is `development` (source
  `98dcf069...`), the manifest verifies (map at A == map at head ==
  working tree; A..head diff confined to the development manifest +
  `oap/`; frozen release metadata untouched; frozen-publication
  cross-check holds; label law holds), and the freshly built
  wheel+sdist bind to its exact recorded hashes. The development wheel
  equals the frozen RC10 wheel byte-for-byte (no `src/` change since the
  freeze); the development sdist differs only by the shipped
  docs/tests/workflow inputs (input-set delta: 5 new — the 016-a/016-b
  contract documents and this test suite — 7 changed, 0 removed).
- Tamper negatives (synthetic, hermetic): missing manifest in a diverged
  tree, stale source (later source change without refresh), omitted
  mapped input, non-mapped path moved under the derived-metadata commit,
  altered built wheel (same source, locally altered input — caught by the
  artifact binding), frozen release metadata touched by a development
  diff, frozen manifest rebound to a later tree's map, and the frozen RC
  record authorizing the altered development source (MUST fail) — all
  fail closed. PASSED (16/16 in the focused suite).

### Development provenance — CI fresh-build/qualification wiring; development images never claim RC10; frozen/published gates preserved
- PASSED. Remote run `39159284589` (implementation head
  `a179c0b02f973ffb5be84acfe9084abcf4136ba3`): test PASSED (includes
  `--verify --dist dist` and the full suite), docker PASSED (log evidence:
  `fresh wheel sha256: eb241dda...` == `expected wheel sha`
  `state=development, source=98dcf069cdcf`; built image label
  `development-source-98dcf069cdcf6d0ff854065e7ec0ef38a02c35db; not a
  release candidate; not released`), operator-session PASSED (all 17
  phases, `wheel-binding: PASSED ... (state=development)`),
  gateway-contract PASSED, docker-published PASSED (exact Gateway
  contract and actual pulled historical-image gates unchanged), CodeQL
  and both CodeQL Analyze jobs PASSED.
- The rehearsal explicitly proves the frozen RC10 record cannot authorize
  the development source: at the development head the frozen
  candidate-branch gate rejects with "post-freeze mapped change"
  (rehearsal PASSED in development mode; see Verification).

### Freeze law — RC10 bytes immutable; no RC/version/tag/registry operation
- PASSED. All 30 existing top-level + archived RC10/publication artifact
  files (top-level `rc_record.json`, `rc_handoff.md`,
  `release_provenance_manifest.json` + schema, and
  `packaging/releases/0.1.0-rc{1,2,3,4,5,7,8,9}/*`) have identical SHA256
  before (at `84022c09`) and after (at the implementation head) —
  diff of the 30-entry hash sets is empty. No new RC, version, tag or
  registry operation; no record moved/deleted; no source-input
  inclusion, test-collection, security, registry, packaging or
  pulled-image validation weakened.

## Verification
Local gate (Python 3.12.15 via uv 0.12.5, repo venv per
`uv sync --frozen --extra dev`; full suite run at the final
implementation head `a179c0b0`):
- `uv lock --check`: PASSED
- `uv sync --frozen --extra dev`: PASSED
- `uv run --frozen ruff check .`: PASSED
- `uv run --frozen ruff format --check .`: PASSED (465 files)
- `uv run --frozen mypy src tests`: PASSED (87 source files)
- `uv run --frozen python scripts/docs_consistency_check.py`: PASSED
  (19 claim docs)
- `uv run --frozen pytest -q` (full locked local gate at the
  implementation head): 1516 passed, 27 skipped, 12 FAILED.
  Baseline attribution (honest): a baseline full-suite run early in the
  round (before the development manifest existed, at
  `84022c09` with the round's uncommitted work present) recorded
  1511 passed / 27 skipped / 17 failed — the same 12 host cases plus the
  two development-state gates (no manifest yet), the rehearsal (local
  partial-clone condition, see "Local setup") and the pre-fix stale
  CI-label assertion. The 12 remaining local failures are byte-identical
  in identity to the 016-a-recorded host-only
  `test_safe_evidence*`/`test_safe_evidence_export*`
  permission-ordering cases (7 + 5); they fail on this host identically
  on the clean pre-change tree and PASS on the GitHub runner (remote
  `test` job PASSED at the implementation head). They are
  host-environment-dependent, not regressions, and no validator was
  weakened to route around them.
- Focused suites at the implementation head:
  `tests/test_dev_provenance.py` (16), `tests/test_source_input_binding.py`
  (12), `tests/test_registry_history_baseline.py` (14): 42 passed.
- Record-present rehearsal (local, at the implementation head): PASSED —
  `mode=development (frozen record at boundary; development provenance
  verified; frozen record cannot authorize this source)
  digest=real-record+development`; the full development-state flow ran:
  frozen replay at `255b3f42...`, the frozen-record negative proof,
  development contract verification, clean-build wheel+sdist binding to
  the development manifest, the focused gate suite in the disposable
  clone, and all tamper classes.
- RC4 regression anchor: PASSED (required negative) — the rehearsal at
  `601a7f9fae19869ad8e09f10fa994550368fd87c` FAILS with
  "schema candidate.rc_identifier const is not the generator's RC
  identifier (stale prior-RC residue): 0.1.0-rc4" (exit 1), the exact RC4
  escape.
- `uv build`: PASSED
- `uv run --frozen python scripts/artifact_policy_check.py --dist dist --inspect`: PASSED (0 violations)
- `uv run --frozen python scripts/artifact_policy_check.py --dist dist --install-smoke`: PASSED (0 violations)
- `uv run --frozen python scripts/dev_provenance_manifest.py --verify --dist dist`: PASSED (state=development; fresh wheel+sdist bound to the development manifest)
- `python -m compileall -q src tests oap/bin scripts`: PASSED
- `bash -n` over `oap/bin/*.sh` and `packaging/*.sh`: PASSED
- `git diff --check`: PASSED
- `ci.yml` YAML structural validity: PASSED
- Targeted credential/raw-content scan over all round-changed content:
  PASSED — the only pattern hits are pre-existing protected-boundary
  text in constitutional/OAP files (artifact-excluded paths) and
  runtime fake-key templates in `operator_session_ci.py` (values are
  generated at runtime; the scanner's credential-value patterns do not
  match and the built-artifact forbidden-content scan reports 0
  violations). No API keys, gateway keys, bearer headers, cookies,
  private URLs, prompts, source bodies, images or customer data were
  committed, printed or logged.
- Unchanged-hash proof for every existing top-level and archived
  RC10/publication artifact: PASSED (30/30 identical; see Acceptance
  evidence).
- Live model/inference/deployment/registry calls: NOT RUN — none
  authorized by this order (no model, no vLLM, no deployment, no
  registry mutation; the docker-published job is the existing read-only
  pulled-image gate and PASSED remotely).
- Real Codex E2E: NOT RUN — not ordered.
- Optional Gateway peer live tests: covered by the remote
  `gateway-contract` job (PASSED); not run locally.

## Local setup and honest test prerequisites
- This local checkout was a `blob:none` partial clone, which breaks the
  rehearsal's `git clone --no-local` (the 016-a-recorded local rehearsal
  clone failures). Per the order's local-setup clause, permitted Git
  objects were hydrated in this repo-owned checkout only
  (`git config --unset remote.origin.partialclonefilter` +
  `git fetch --refetch origin`); the repository is now complete
  (`git rev-list --objects --missing=print --all` reports zero missing
  objects). No shared-home or protected-host permission was changed and
  no security validator or assertion was weakened. After hydration, both
  rehearsal tests pass locally (development-mode pass at the
  implementation head; required RC4 negative).
- The 12 host-only `test_safe_evidence*` permission-ordering cases
  (byte-identical identity to the 016-a-recorded set) still fail on this
  host on the clean pre-change tree and on the implementation head; they
  pass on the GitHub runner (remote `test` job PASSED). Reported as
  host-environment-dependent, not as pass.

## Live model/service evidence
- NOT RUN. No live model, no vLLM call, no deployment, no registry
  mutation, no protected `qwen-serving`/vLLM port 18020/18021 or Codex
  profile activity. The protected live-host fixture (qwen-serving,
  systemd units, venv, models, API-key files, firewall/VPN/bindings,
  existing Codex profiles) is untouched; no network/service mutation
  occurred. Development port usage was limited to CI-disposable
  infrastructure on the GitHub runner (operator-session job, synthetic
  secrets, complete teardown proof in the job log).

## Secrets/privacy
- No secret, credential, bearer header, cookie, gateway key, private
  URL, prompt, source body, image or tool output appears in the round's
  commits, logs, reports or evidence. All evidence above is redacted by
  construction (SHA256 prefixes, job names, deterministic synthetic
  rehearsal facts). The development manifest and schema contain no
  credentials (schema-pinned frozen publication facts only).

## Known limitations / non-goals (truthful scope boundary)
- The 12 host-only safe-evidence failures (host permission-ordering
  environment) — pass on the GitHub runner; see Verification.
- Development-state CI runs bind artifacts to the development manifest
  and label development images `development-source-<A>; not a release
  candidate; not released`; they do NOT qualify any release candidate.
  Final-stage immutable release identities remain defined by the
  artifact policy and the CACHE rework plan (all 40 runtime criteria
  still `NOT RUN`).
- This round is the approved preparatory contract/development-state
  prerequisite for the CACHE implementation; it is not
  adapter-runtime implementation, not new RC qualification, not
  publication, and not a release.

Implementation head SHA: a179c0b02f973ffb5be84acfe9084abcf4136ba3
Report publication commit: SELF

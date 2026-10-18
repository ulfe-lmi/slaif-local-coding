# OAP Coding-Agent Report — 016-a

## Work order
- Identifier: 016-a; order path `oap/orders/016-a-cache-rework-contracts.md`;
  numeric objective 016.
- PR mode: CREATED_NEW_PR.

## Status
PARTIAL

## Executive summary
The documentation/contract stage of the human-authorized dependency-bundle
CACHE rework is delivered and remote: the exact unchanged human handoff and
the exact unchanged strategic implementation plan are committed, both
architecture documents plus root/strategic law, security, testing and
configuration docs are reconciled so that `dependency-bundles-v1` is the
explicit normative target with the legacy profile explicitly scoped, and a new
stage ledger maps all 40 named acceptance criteria (D/G/C/B/R/M/S/O) as
`NOT RUN` (planned) with the planned 016–024 succession. Objective A–D are
complete with evidence. Objective E is a precise, structurally unavoidable
blocker: the mandated handoff file (and the planned documentation) are sdist
inputs that do not exist in the frozen RC10 source-input map, so the two
frozen development-state packaging gates fail on any tree carrying them,
locally and on the required remote `test` check. Per the order's acceptance
criterion E, this is published as a precise blocker with a request for a
bounded same-PR strategic continuation; no gate was weakened and no immutable
record was touched.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`.
- PR: #24, https://github.com/ulfe-lmi/slaif-local-coding/pull/24, state
  OPEN, not draft, base `main`, head `oap/016-cache-rework-contracts`.
- Starting remote main (verified before branching):
  `f3793af9e5f05bdfba19ef800eeaf57177d0ed2b` (unchanged by this round; no
  other 016 PR existed; unrelated open PR #23 untouched).
- Implementation head SHA: f8e0f154f6907fed0366f0cfe019454fc700d45e
- Report publication commit: SELF
- Implementation commits pushed before report: 1
  (`f8e0f15`, parent `f3793af9`).
- New PR this round: yes (#24). Amended existing: no. Merge performed: NO.

## Changes and files
Single implementation commit `f8e0f15` (12 files, +1932/−112), all
documentation/contract, no runtime:
- `oap/active` → `016-a` and `oap/orders/016-a-cache-rework-contracts.md`:
  committed unchanged (order commit hash
  `34b8d4ad7e0aaa2515c968a7610e9507e6b8d5f338895b574d58f5bedc7d1bdf`,
  byte-identical to the strategic draft).
- `docs/CACHE-REWORK.md`: human handoff committed unchanged, SHA256
  `410df5c0b8f90b05220adc32c8e673b143c0cf1fa3da02270d91ac453c886abd` (as
  required by the order).
- `docs/CACHE-IMPLEMENTATION-PLAN.md`: strategic plan copied byte-identical,
  SHA256 `2c1c429bc48b25ed8ffb57e12bbc997582719ecbebf0d03a33ce2e15dcbe0af5`
  (verified equal to the strategic draft before and after copy).
- `docs/CACHE-REWORK-LEDGER.md` (new): stage ledger — all 40 criteria with
  owning stage, abridged required evidence, `NOT RUN` (planned) states;
  three-claim law (evidence/implementation/acceptance); planned 016–024
  succession and same-PR continuation discipline; RC10 recorded as historical
  baseline (not rework-qualified); private audit corpus provenance
  (name + sealed digest only, no corpus content).
- `ARCHITECTURE.md`: new profile-scope introduction; legacy profile
  explicitly named and scoped; v1 section stating the ten approved rules,
  the resolved choices, and how v1 differs from legacy; profile-scoped
  state-lifetime table, failure table, observability and verification
  sections; implementation map annotated.
- `ARCHITECTURE-for-agents.md`: "Cache profile scope (normative target)"
  section; legacy-scoped constitution and pseudo-context/cache law; new
  "Dependency-bundle cache law (v1 profile, normative target)" covering
  root, recursive graph, read observation, lean/greedy admission,
  identity/replay/overlap, C/32 + aggregate token budgets, compile-once per
  epoch with no automatic retry, RAM ownership without TTL/LRU/capacity
  eviction, per-session exact-original recovery, transactional replacement
  with no hidden fallback, source-role authority, typed failure contract and
  stage-accurate observability; v1 pipeline commit order; updated identity,
  resource, failure and verification laws; objective boundaries updated to
  the verified merged history (000–015 through PR #22) and the open 016 with
  planned 017–024 inert drafts.
- `AGENTS.md` (root): three surgical edits — owned-cache bullet scoped to
  legacy profile with v1 pointer; derived-cache law scoped to legacy profile;
  raw-source-persistence default retained with the narrow explicit v1
  protected per-session recovery/evidence exception. Authority, report
  immutability, credentials/logging prohibitions and protected-service
  boundaries unchanged.
- `SECURITY.md`: rule 9 scoped (legacy) and pointing at the new narrow
  exception; new section "Protected source recovery and evidence retention
  (narrow exception)" (scope, opt-in/ownership 0700/0600, integrity/durability,
  credential handling with no complete-detection claim, access rules,
  retention/encryption prerequisites).
- `TESTING.md`: new "Planned dependency-bundle cache profile (v1)" section —
  planned v1 test layers mapped to the ledger criteria, `NOT RUN` (planned)
  states, RC10 historical-baseline statement, planned configuration examples
  marked non-runnable.
- `docs/ADAPTER-CONFIGURATION.md`: new "Planned: the `dependency-bundles-v1`
  profile (not implemented)" section — planned configuration requirements and
  an explicitly non-runnable illustrative TOML; keys are design placeholders,
  none accepted by the current release; legacy-conflict migration stated.
- `docs/README.md`: one new narrow index section linking the handoff, plan
  and ledger.

No prior activated order/report touched; no `src/`, `tests/`, `config/`,
`packaging/`, `pyproject.toml`, `uv.lock`, workflow or service files changed.

## Acceptance evidence
### Criterion A — approved handoff and finalized strategic plan tracked, unchanged, linked
- PASSED. Commit `f8e0f15` carries `docs/CACHE-REWORK.md` with SHA256
  `410df5c0...886abd` (order-required value; re-verified against the committed
  blob) and `docs/CACHE-IMPLEMENTATION-PLAN.md` with SHA256
  `2c1c429b...e0af5`, byte-equal to the strategic draft
  (`/home/janezp/codex-supervision/slaif-local-coding/drafts/`). Both are
  linked from `ARCHITECTURE.md`, `ARCHITECTURE-for-agents.md`, `TESTING.md`,
  `docs/ADAPTER-CONFIGURATION.md` and `docs/README.md` (relative links
  resolve; docs consistency check PASSED).

### Criterion B — both architecture documents coherent and complete for all ten rules and section-18 choices; legacy not masquerading as v1
- PASSED (delivered; strategic review pending). The ten approved rules are
  stated verbatim in the handoff and restated in `ARCHITECTURE.md`; the
  compact architecture carries the full v1 law section (root, recursive
  graph, read observation/complete outer spans, lean/greedy with default
  lean and session-identity immutability, independent ordered bundle identity
  with replay/overlap invalidation, C/32 slots + `floor(C/4)` aggregate limit
  and generation/tool/uncertainty reserves, compile-once per live epoch with
  single-flight and no automatic retry, one-worker RAM ownership with
  explicit 512/128 MiB recommended ceilings and fixed-503 backpressure,
  per-session exact-original recovery with new-epoch rebuild, transactional
  replacement with no hidden original fallback, source-role authority, typed
  503/409/422 failure contract, stage-accurate observability) — i.e. all ten
  rules plus the strategic section-18 resolved choices. Legacy behavior is
  explicitly named "legacy (implemented)" everywhere it appears, and v1 is
  marked "planned/not implemented"; no legacy law remains unscoped where it
  would contradict v1.

### Criterion C — root/strategic law, security and testing/config no longer categorically prohibit required v1 protected originals or require v1 TTL/LRU/filesystem hot cache/raw fallback
- PASSED (delivered). Root `AGENTS.md` and `SECURITY.md` retain the default
  prohibition and add exactly one narrow, explicitly opted-in protected
  per-session recovery/evidence exception (exact observed originals and
  derived metadata only; no credentials; 0700/0600; integrity; retention and
  encryption prerequisites). The compact architecture scopes TTL/LRU/
  filesystem-derived-cache law to the legacy profile and states v1 RAM
  ownership with no eviction and no filesystem hot read; the old
  "safe raw-request fallback" law is scoped to legacy while v1 carries its
  explicit no-hidden-fallback failure contract. V1 requirements do not
  weaken default log/credential/identity-isolation rules (identity, header,
  metric and protected-host laws untouched).
- Strategic-home copies updated outside the repository as ordered: strategic
  `ARCHITECTURE-for-agents.md` is now byte-identical to the normative repo
  compact architecture (SHA256 `4dda5bb0a0262010a8d1e14c0c07cfee605af6eae051434308ed249a1133243d`
  on both sides), and the strategic `AGENTS.md` product-law cache bullet is
  scoped to the legacy derived cache with the narrow v1 exception. These
  files are outside the repository and are not part of the PR.

### Criterion D — stage ledger maps all 40 named acceptance cases with honest NOT RUN states and planned evidence; no root-only success assertion
- PASSED. `docs/CACHE-REWORK-LEDGER.md` contains all 40 criteria
  (D01–D10, G01–G05, C01–C06, B01–B04, R01–R05, M01–M05, S01–S02, O01–O03),
  each with owning stage, abridged required evidence, state `NOT RUN`
  (planned), and the three-claim law (evidence/implementation/acceptance)
  plus the O01/O02 no-substitution rule; the 016–024 succession table and
  same-PR continuation discipline are recorded; RC10 is documented as
  historical baseline, not a rework-qualified artifact.

### Criterion E — documentation/publication/build validation and current-head required remote checks genuinely successful; frozen RC10 bytes/provenance preserved
- PARTIAL — precise blocker. All documentation and build gates succeeded:
  docs consistency PASSED (20 docs), ruff/mypy PASSED, `uv build` PASSED,
  artifact policy inspect + install-smoke PASSED (the rebuilt sdist/wheel
  contain the new docs and no forbidden content), `git diff --check` PASSED,
  shell-script `bash -n` PASSED, privacy/secret scans PASSED. All frozen
  RC10/historical artifact bytes are preserved (no `packaging/` or
  `oap/` prior-round file touched). However, the required remote `test`
  check FAILED with exactly two failures, both the same structural condition
  described in "Known limitations/blockers": they are caused by committing
  documentation that is sdist input, which the frozen RC10 development-state
  gates cannot accept without either a development-state provenance contract
  change or a new qualified artifact boundary — both outside this round's
  authorized scope ("No runtime Python, dependencies, … artifact publication,
  or service changes in this round"). Per the order, this is published as a
  precise blocker with a request for a bounded same-PR strategic
  continuation; gates were not weakened and immutable records were not
  rewritten.

## Verification
Local gate (Python 3.12.15 via uv 0.12.5, venv per `uv sync --frozen
--extra dev --python 3.12`; baseline first run on the clean tree, then on
the modified tree; both runs identical except as stated):
- `uv lock --check`: PASSED
- `uv sync --frozen --extra dev`: PASSED (environment setup)
- `uv run --frozen ruff check .`: PASSED
- `uv run --frozen ruff format --check .`: PASSED
- `uv run --frozen mypy src tests`: PASSED
- `uv run --frozen python scripts/docs_consistency_check.py`: PASSED
- `uv run --frozen pytest -q`: FAILED locally — 15 failed, 1497 passed,
  27 skipped. Baseline attribution: the exact same 15 tests fail on the
  clean pre-change tree on this host (12 `test_safe_evidence*` host
  permission-ordering cases, 2 `test_rc_record_present_rehearsal` cases —
  the local checkout is a `blob:none` partial clone whose promisor fetch
  breaks the rehearsal's `git clone --no-local`, and 1
  `test_source_input_binding::test_real_repo_source_inputs_bound_to_committed_source`
  — already failing on the clean tree because the untracked human handoff
  file on disk is a sdist input absent from the frozen RC10 map). On the
  GitHub runner, of these 15, 14 pass (host-environment-dependent) and 1
  remains, plus the rehearsal variant (see CI section).
- `uv build`: PASSED
- `uv run --frozen python scripts/artifact_policy_check.py --dist dist --inspect`: PASSED
- `uv run --frozen python scripts/artifact_policy_check.py --dist dist --install-smoke`: PASSED
- `python -m compileall -q src tests oap/bin scripts`: PASSED
- `bash -n` over `oap/bin/*.sh` and `packaging/*.sh` (4 scripts): PASSED
- `git diff --check`: PASSED
- Exact handoff/plan hashes: PASSED (`410df5c0...` / `2c1c429b...`, remote
  blobs re-verified after push)
- Relative link check: PASSED (docs consistency gate + manual enumeration of
  all relative targets in the new/changed docs)
- Targeted privacy/secret scan: PASSED (artifact-policy forbidden-content
  scan over built wheel+sdist; grep for `/synology/`, hostnames, private LAN
  endpoints, key patterns over all new/changed docs — none present)
- No prior immutable-artifact edits: PASSED (diff confined to the 12 listed
  paths; all `packaging/`, prior `oap/` orders/reports and
  `packaging/releases/*` bytes untouched)
- Live model calls: NOT RUN — none authorized or needed by this order.
- Optional Gateway peer/live tests: NOT RUN locally (CI `gateway-contract`
  job covers the pinned peer; PASSED remotely).

## Live model/service evidence
- NOT RUN. No live inference, deployment or service interaction was
  authorized by this order; protected 18020/Qwen/Codex fixtures unchanged.

## GitHub CI / required checks
Checked at implementation head `f8e0f154f6907fed0366f0cfe019454fc700d45e`
(run 39152707733):
- `test`: FAILURE — 2 failed, 1510 passed, 27 skipped.
  1) `tests/test_source_input_binding.py::test_real_repo_source_inputs_bound_to_committed_source`
     — working-tree input map differs from the frozen RC10 recorded map by
     exactly the 5 documentation inputs (2 modified, 3 new; nothing else);
  2) `tests/test_rc_record_present_rehearsal.py::test_record_present_rehearsal_passes_at_head`
     — rehearsal stderr: "candidate source map differs from the qualified
     source boundary map (post-freeze mapped change)". Both are the same
     structural frozen-RC10 development-state condition (see blocker).
- `gateway-contract`: SUCCESS
- `docker`: SUCCESS
- `operator-session`: SUCCESS
- `docker-published`: SUCCESS
- `CodeQL`: SUCCESS; `Analyze (python)`: SUCCESS; `Analyze (actions)`: SUCCESS
- All required green at drafting: NO (`test` failed for the disclosed
  structural reason). Report-head checks may be pending; strategy verifies.

## Local setup/dependencies
- uv 0.12.5 (matches pinned build provenance), CPython 3.12.15 repo venv
  (matches CI's 3.12), locked frozen installs; repo-local git identity set to
  the established repository committer `jpers1 <30219753+jpers1@users.noreply.github.com>`
  to match prior OAP commits. No new dependencies; no protected-host tools;
  no sudo used.

## Documentation
- Updated as listed under "Changes and files"; all plan/architecture links
  work; future configuration examples explicitly marked planned/non-runnable;
  no new runtime keys claimed to exist; README build-input changes deferred
  to integration as the order permits.

## Safety/scope confirmations
- Unrelated files: none touched; unrelated open PR #23 untouched.
- Secrets/raw content: none committed, printed or logged; report uses hashes,
  counts and sanitized statuses only.
- Production/protected resources: no model/profile/API-key, Qwen/vLLM
  unit/port/model/venv/flag, network/firewall/VPN, Gateway repo, registry/RC
  tag/record, or benchmark-history changes.
- Protected 18020/Qwen/Codex fixture changed: NO.
- Required tests skipped/not run: live model calls NOT RUN (not authorized,
  not needed); local optional peer/live tests NOT RUN (covered by CI).
- Scope deviation: none beyond ordered documentation scope; the two
  strategic-home files updated outside the repository are the ordered
  "strategic instruction constitution/compact architecture" sync.
- Extra objective PR: NO. Coding merge: NO. Auto-merge: NO.
- Active/order edited: NO (committed byte-identical; order hash
  `34b8d4ad...` verified against the strategic draft).
- Report commit report-only: yes (single path
  `oap/reports/016-a-cache-rework-contracts.md`).

## Known limitations/blockers
1. **Frozen RC10 development-state gate (structural, precise).** The RC10
   provenance manifest records a 131-entry source-input map for the published
   candidate. Two unconditional gates bind the current tree to that frozen
   map: `test_source_input_binding::test_real_repo_source_inputs_bound_to_committed_source`
   (working-tree input map must equal the recorded map) and the
   record-present rehearsal (qualified source boundary map). The human
   handoff — which the order mandates be committed at `docs/CACHE-REWORK.md`
   — is an sdist input absent from the frozen map, so the binding gate was
   already failing on the clean tree the moment the handoff file existed on
   disk; this round's planned documentation (plan, ledger, changed
   ADAPTER-CONFIGURATION.md and docs index) widens the same delta to 5 input
   paths. Resolving it requires either (a) a development-state provenance
   contract distinguishing current development artifacts from the frozen RC10
   record (no artifact weakening, no rewrite of immutable records) or
   (b) a new qualified artifact boundary/publication — neither authorized in
   this documentation-only round ("No runtime Python, dependencies, …
   artifact publication … in this round").
2. 14 additional local-only pytest failures on this host (12
   safe-evidence permission-ordering, 2 rehearsal clone) are pre-existing
   host-environment conditions, present on the clean baseline tree and
   passing on the GitHub runner; they do not affect the PR.

## Recommended strategic follow-up
Factual only; strategy decides:
- Issue a bounded same-PR continuation (next valid suffix of objective 016)
  that implements the development-state provenance contract anticipated by
  the strategic plan's publication item ("if existing gates make product
  development require a release, fix the development-state contract in a
  bounded same-PR continuation without weakening artifact validation"), so
  that the two frozen-map gates accept post-publication development inputs
  while keeping every RC10 record byte-identical and immutable. After that
  continuation, the PR's required checks can reach green and objective 016
  can be re-reviewed for acceptance; the 017+ implementation stages can then
  proceed under the existing succession.
- No human decision is required for the documentation content itself; the
  only open question is the development-state gate contract.

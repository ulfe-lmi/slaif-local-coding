# OAP Coding-Agent Report — 016-d

## Work order
- Identifier: 016-d; order path: `oap/orders/016-d-selected-state-and-local-test-context.md`; numeric objective 016
- PR mode: AMENDED_EXISTING_PR (PR #24 only; NO NEW PR)

## Status
COMPLETE (claim for strategic review; not acceptance)

## Executive summary
Closed the remaining frozen-state operator validation bypass and completed the
full local gate under a resolved restrictive test-process context, without
touching the frozen RC10 publication, `src/`, dependencies, or any protected
fixture. (1) `operator_session_ci.select_artifact_state` now consumes the full
authoritative state-aware verification in BOTH states before returning an
expected wheel: the frozen branch previously called only the committed-map
classifier and read its wheel hash; it now additionally requires the actual
working-tree map binding and the independent pre-rework
frozen-publication baseline validation (a pure committed-state classifier is
not artifact authorization — dirty or untracked mapped inputs and frozen
publication bytes that differ from the pinned baseline, even a still-valid-
JSON reformat, fail closed before any wheel is returned); the accepted
verifier (`dev_provenance_manifest.verify`) is reused unchanged, the
production invocation keeps the pinned freeze authority, and a clean frozen
tree remains supported without a development manifest. (2) Three focused
standalone frozen-operator-selection regressions added (dirty tracked input,
untracked mapped input, valid-JSON mutated frozen record), each failing the
production selection logic at its intended guard; the 016-c
changed-runtime-source development positive, clean frozen positive and
wrong-selected-wheel negatives are preserved. (3) The complete locked local
gate was executed once at the new implementation under a restrictive
process-local umask 022 test context (the order's "077, or 022 if adequate"):
1543 passed, 27 skipped, 0 failed; a diagnostic umask-077 run is recorded
separately (one test-cache fixture-mode expectation cannot be expressed under
077 and is documented, not relabeled); the 12 pre-existing host-only
safe-evidence failures at the canonical umask 0002 remain recorded as FAILED
on that context and are never labeled pass. (4) PR #24 title/body rewritten
around the final architecture/contracts plus the current-development
provenance scope (obsolete 016-a documentation-only statements removed; no v1
runtime delivery claimed); the compact architecture's contradictory
"duplicate effective roots" phrase narrowed to competing effective root
scopes (byte-identical mirror preserved); TESTING.md's surviving absolute
synthetic-evidence sentence removed, leaving one consistent per-criterion
rule. All eight required exact-head GitHub checks SUCCESS; all 40 v1 runtime
criteria remain NOT RUN. No live inference, no Docker activity on the
protected host, no registry/model/network/service mutation.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`; PR #24 https://github.com/ulfe-lmi/slaif-local-coding/pull/24 — OPEN, MERGEABLE, non-draft, single objective PR
- Base `main` = `f3793af9e5f05bdfba19ef800eeaf57177d0ed2b` (also the pinned pre-rework freeze baseline); head branch `oap/016-cache-rework-contracts`
- Starting remote SHA: `77d5d6281aab6e1fe32e000aca975f5f88745e91` (016-c report-only commit, sole parent implementation `1acc702353489fb7f28833e6581f34a3d3d7128d`)
- Implementation head SHA: 1fd18d9caebd947a3ed5b2eff600a21e30d60321
- Report publication commit: SELF
- Implementation commits pushed before report: `fc6e512c28a783718996e7524864399c33d1c99f` (both-states operator validation + regressions + docs, 6 files) and `1fd18d9caebd947a3ed5b2eff600a21e30d60321` (dev-manifest refresh + activated order + `oap/active`, 3 files)
- New PR this round: NO; amended existing PR #24: YES; merge performed: NO
- PR title/body updated this round (before report publication) to the final architecture/contracts plus development-provenance scope

## Changes and files
### `fc6e512` — 016-d: full authoritative validation in both operator artifact states
- `scripts/operator_session_ci.py`:
  - `select_artifact_state` now calls the accepted verifier
    `dev_provenance_manifest.verify` (state-aware: committed-map AND
    actual-working-tree-map binding, frozen-binding re-proof, independent
    pre-rework frozen-publication baseline validation in the frozen state,
    full closed-contract validation in the development state) BEFORE any
    expected wheel is returned, then reads the wheel hash from exactly the
    verified state's manifest. DevProvenanceError is surfaced as
    SessionError (main's existing handler) with the guard message preserved.
  - The now-superseded private helpers `_development_state_active` and
    `_load_dev_manifest` (committed-map classifier + partial manifest load)
    are removed; no other behavior changed.
  - The production `main()` invocation passes no `baseline_commit`: the
    pinned pre-rework baseline remains the freeze authority (the typed
    argument exists for hermetic fixtures only).
- `tests/test_dev_provenance.py` (suite 28→31): three focused standalone
  frozen-operator-selection regressions, each exercising the production
  selection logic (not a mocked state flag) and failing at its intended
  guard before any wheel is returned:
  - `test_operator_frozen_selection_dirty_tracked_input` — dirty tracked
    mapped input at the frozen head fails at the working-tree binding guard
    ("working tree differs from the committed source");
  - `test_operator_frozen_selection_untracked_mapped_input` — new untracked
    mapped input fails at the working-tree binding guard (extra=
    ['docs/untracked.md']);
  - `test_operator_frozen_selection_valid_json_mutated_frozen_record` —
    frozen `release_provenance_manifest.json` reformatted as still-valid,
    data-identical JSON fails at the independent baseline working-tree
    guard ("frozen publication bytes differ from the pre-rework baseline").
  - Preserved unchanged: `test_operator_binding_changed_runtime_source`
    (genuine changed-runtime-source development positive: freshly built
    wheel differs from the frozen wheel; dev hash passes, frozen hash and
    another wrong hash fail) and `test_operator_binding_frozen_state`
    (clean frozen positive + mismatched-wheel negative).
- `ARCHITECTURE-for-agents.md` + byte-identical
  `oap/strategic-instructions/ARCHITECTURE-for-agents.md` mirror (cmp-
  verified): the identity/security sentence that still said "duplicate
  effective roots ... fail explicitly" is narrowed to "competing effective
  root scopes ... fail explicitly", consistent with the root section's
  repeated byte- and scope-identical idempotence law and the genuine-version
  law (both untouched). No new cache policy.
- `TESTING.md`: the surviving absolute sentence "no v1 runtime criterion is
  `PASSED` on synthetic evidence alone" (with its Markdown formatting) is
  removed; the immediately following per-criterion evidence-layer rule is
  the single consistent rule, with actual-model/genuine-Codex/native-
  compaction/artifact claims retaining their own mandatory layers. All 40
  v1 runtime criteria remain NOT RUN.
- `docs/DEVELOPMENT-PROVENANCE.md`: documents the order 016-d both-states
  operator-session state selection (frozen state: working-tree map binding
  + independent baseline validation before any wheel; development state:
  closed-contract validation; pinned freeze authority; clean frozen tree
  without a development manifest).

### `1fd18d9` — 016-d: refresh development provenance manifest; commit activated order and active
- `packaging/dev_provenance_manifest.json` regenerated at source
  `fc6e512c28a783718996e7524864399c33d1c99f` (136 source inputs; wheel
  `eb241dda2e079b29190868108c488edaf98261c84119bfd405070dea98b546b9`,
  unchanged because no `src/` product change and equal to the frozen RC10
  wheel; sdist `2241651139142271872fbf949975064a53a9d8c4f782dced3dccecad1ce8be21`
  (546726 bytes); toolchain Python 3.12.15 / uv 0.12.5 / `uv.lock` SHA256
  bound; label `development-source-fc6e512c28a783718996e7524864399c33d1c99f;
  not a release candidate; not released`).
- `oap/orders/016-d-selected-state-and-local-test-context.md` committed
  unchanged (SHA256 `56ccc1429900a0334970a04decd754638713d263a27b7b3b840ec47b8c22a922`,
  byte-identical to the strategic-authored order) and `oap/active` = `016-d`.

## Acceptance evidence
### Criterion 1 — full authoritative validation in BOTH operator states
- Independent probe evidence from the order: the pre-round frozen branch of
  `select_artifact_state` called only the committed-map classifier and read
  the wheel hash, so a dirty tracked README and a newly added untracked
  mapped document each failed `verify`/`emit_state` correctly yet were
  ACCEPTED_FROZEN by operator selection (helper SHA256
  `802c7456164076d3e90d5e4248ef4c7426436f660eb6287682d996e38c9b4937`).
- Now `select_artifact_state` consumes `dev_provenance_manifest.verify` in
  both states before any expected wheel is returned: frozen state =
  working-tree map binding + frozen-binding re-proof + independent
  frozen-publication baseline validation; development state = full closed-
  contract validation. The accepted verifier is reused unchanged (no new
  guard logic added to it); the change is confined to the operator script
  (63 lines removed, 29 added across the function + removed helpers).
- New focused regressions (production selection logic, hermetic synthetic
  repository, fixture baseline): dirty tracked input → fails at "working
  tree differs from the committed source" before any wheel; untracked
  mapped input → fails at the same guard with extra=['docs/untracked.md'];
  valid-JSON reformatted frozen record → fails at "frozen publication bytes
  differ from the pre-rework baseline (working tree)" before any wheel.
  PASSED (31/31 in the focused suite; see Verification).
- Production invocation keeps the pinned freeze authority (`main()` passes
  no `baseline_commit`); a clean frozen tree remains supported without a
  development manifest (preserved frozen positive; `--verify`/`--emit-state`
  frozen-state paths unchanged).

### Criterion 2 — preserved positives/negatives plus the three new regressions
- Preserved: changed-runtime-source development positive (freshly built
  wheel `!=` frozen wheel; dev hash passes; frozen hash and another wrong
  hash fail), clean frozen positive, wrong-selected-wheel negatives —
  `test_operator_binding_changed_runtime_source` and
  `test_operator_binding_frozen_state` unchanged and PASSED.
- Added: the three standalone frozen-selection negatives above; each fails
  at its intended guard before returning an expected wheel; no mocked state
  flag (the real `select_artifact_state` runs the real verifier on the real
  synthetic repository).
- Result: PASSED (focused suite 162 passed across the seven named modules;
  full suite 1543 passed at the implementation head).
- No real Docker/model activity needed for these pure tests; the existing
  remote Docker/operator jobs remain required and PASSED (see GitHub CI).

### Criterion 3 — complete local verification under the resolved test context
- 016-c's umask diagnosis is recognized and NOT relabeled as unresolved:
  the same 12 safe-evidence node ids PASSED in the owned private exact-
  source umask-077 checkout, and the 12 FAILED node-id list was byte-
  identical to the pre-change baseline at umask 0002.
- The full corrected-context run WAS performed at the new implementation
  (source `1fd18d9caebd947a3ed5b2eff600a21e30d60321`, canonical checkout,
  clean tree): the complete 10-command locked local gate under a
  process-local umask 022 (the order's "077, or 022 if adequate"):
  `uv lock --check`, `uv sync --frozen --extra dev`, `ruff check .`, `ruff
  format --check .`, `mypy src tests`, `docs_consistency_check.py`, full
  `pytest -q`, `uv build`, `artifact_policy_check.py --inspect`,
  `--install-smoke` — all PASSED; full `pytest -q`: **1543 passed, 27
  skipped, 0 failed** (322.55s). No shared/home permissions changed, no
  validator changed, no test or assertion weakened or skipped, no root
  execution (user `janezp`; the execute-only-ancestor test ran, since the
  process is non-root).
- Diagnostic umask-077 full run (recorded separately, superseded): 1542
  passed, 27 skipped, 1 FAILED — `test_cache.py::test_untrusted_fallback_
  is_never_adopted`, whose fixture is created with `mkdir(mode=0o755)`;
  under umask 077 the mode is masked to 0700, which the (correct,
  unchanged) validator accepts as a trusted fallback, so the test's intent
  (a 0755 fallback must never be adopted) cannot be expressed under 077.
  This is a fixture-mode expectation, not a validator defect; umask 022 is
  therefore the recorded resolved context (default mkdir 0775 → 0755: no
  group-write bit, so the safe-evidence component walk reaches the intended
  later rejection assertions, and 0755 fixture semantics are preserved).
- Canonical default-umask (0002) context: NOT re-run this round; 016-c
  recorded 1528 passed / 27 skipped / 12 FAILED there at `1acc702`
  (host-environment prerequisite; byte-identical node-id list). This round's
  source delta does not touch those suites. The 12 are kept separate and
  are never labeled pass in this report; under the resolved 022 context
  they are included in the 1543 passed.
- Focused suites at the same source/context: 162 passed (dev-provenance/
  operator 31, source-input binding, record-present rehearsal, registry-
  history baseline, safe-evidence ×2, release-provenance manifest).
- Exact tested source and permission context recorded above (source SHA,
  canonical checkout, user, umask 022 final / 077 diagnostic, no root).
- A private exact-source checkout was not needed: the child-process umask
  was set in the canonical checkout session, as the order permits.

### Criterion 4 — documentation consistent with the validated state selection
- PR #24 title rewritten to "Dependency-bundle cache rework contracts and
  development provenance binding"; body rewritten around the final
  architecture/contracts (v1 normative target, legacy profile scope,
  security exception, single consistent testing rule, ledger) plus the
  current-development provenance scope, with resulting behavior and actual
  validation for a reviewer without this conversation; the obsolete 016-a
  "documentation-only / no packaging change / source-binding fix outside
  scope" statements are removed (abandoned approach omitted); no v1 runtime
  delivery is claimed; all 40 v1 runtime criteria remain NOT RUN.
- Compact architecture: "duplicate effective roots" narrowed to "competing
  effective root scopes" in the identity/security section only; the root
  section's idempotence (repeated byte- and scope-identical roots) and
  genuine-version laws are untouched; the repository mirror
  (`oap/strategic-instructions/ARCHITECTURE-for-agents.md`) is byte-
  identical (cmp-verified at the final source).
- TESTING.md: one consistent rule (per-criterion evidence layers;
  actual-model/genuine-Codex/native-compaction/artifact claims retain their
  own mandatory layers); no new cache policy.
- Human handoff (`docs/CACHE-REWORK.md`), approved plan
  (`docs/CACHE-IMPLEMENTATION-PLAN.md`), prior activated orders/reports and
  every frozen top-level/archive publication file are byte-identical
  (not in the round diff; 29/29 frozen paths re-verified against the pinned
  baseline).

## Verification
Recorded test context: canonical checkout `/home/janezp/codex-work/slaif-
local-coding`, clean tree at source `1fd18d9caebd947a3ed5b2eff600a21e30d60321`
(implementation head), user `janezp` (non-root), process-local umask 022
(final gate and focused suites); umask 077 diagnostic full run recorded
separately; no shared/host/home permission changes, no validator changes,
no root execution.

Full locked local gate at the final unchanged source (umask 022):
- `uv lock --check`: PASSED
- `uv sync --frozen --extra dev`: PASSED
- `uv run --frozen ruff check .`: PASSED (All checks passed)
- `uv run --frozen ruff format --check .`: PASSED (469 files already formatted)
- `uv run --frozen mypy src tests`: PASSED (Success: no issues found in 87 source files)
- `uv run --frozen python scripts/docs_consistency_check.py`: PASSED (19 claim docs checked)
- `uv run --frozen pytest -q`: PASSED — 1543 passed, 27 skipped, 0 failed (322.55s); includes the 12 host-only safe-evidence cases (passing at umask 022) and the 3 new regressions
- `uv build`: PASSED (wheel + sdist)
- `uv run --frozen python scripts/artifact_policy_check.py --dist dist --inspect`: PASSED (0 violations; wheel `eb241dda2e07...` == frozen RC10 wheel, sdist `224165113914...` == development manifest)
- `uv run --frozen python scripts/artifact_policy_check.py --dist dist --install-smoke`: PASSED (0 violations)
- Diagnostic full gate at umask 077 (superseded context, recorded for the record): 9/10 commands PASSED; `pytest -q`: 1542 passed, 27 skipped, 1 FAILED (`test_cache.py::test_untrusted_fallback_is_never_adopted`, fixture-mode expectation, see Criterion 3) — NOT labeled pass

016-c Verification-section commands re-run at the final source/context:
- `uv run --frozen pytest -q` (full gate): PASSED (above; not re-run a second time for this report)
- `uv run --frozen python scripts/dev_provenance_manifest.py --verify --dist dist`: PASSED (`state=development head=1fd18d9caebd`; fresh wheel+sdist bound)
- `uv run --frozen python -m compileall -q src tests oap/bin scripts`: PASSED
- `bash -n` over `oap/bin/*.sh` + `packaging/*.sh`: PASSED
- `git diff --check`: PASSED (round diff: 9 files, +149/−77)
- Targeted privacy/credential scan over the round diff: PASSED — no key/token/credential/private-IP hits
- Frozen-publication baseline comparison (29 paths, baseline `f3793af9e5f0` → head `1fd18d9caebd` → working tree, plus absence/no-new-record checks): PASSED (29/29 byte-identical; 5 top-level + 24 archived; `release_record.json` absent; no new top-level/archived records)
- Independent clean artifact reproduction from `git archive HEAD` in a clean 0700-owned temp tree: PASSED — wheel `eb241dda2e079b29190868108c488edaf98261c84119bfd405070dea98b546b9` and sdist `2241651139142271872fbf949975064a53a9d8c4f782dced3dccecad1ce8be21`, both equal to the committed development manifest (and the wheel equal to the frozen RC10 wheel; no `src/` change this round)
- `scripts/rc_record_present_rehearsal.py` at the implementation head: PASSED (`mode=development (frozen record at boundary; development provenance verified; frozen record cannot authorize this source) digest=real-record+development`, source `1fd18d9caebd`)
- RC4 negative anchor: rehearsal at RC4 source `601a7f9fae19869ad8e09f10fa994550368fd87c` FAILED as required (exit 1, "stale prior-RC residue: 0.1.0-rc4")
- Focused suites (umask 022, implementation head): PASSED — 162 passed: `tests/test_dev_provenance.py` (31, incl. 3 new), `tests/test_source_input_binding.py`, `tests/test_rc_record_present_rehearsal.py`, `tests/test_registry_history_baseline.py`, `tests/test_safe_evidence.py`, `tests/test_safe_evidence_export.py`, `tests/test_release_provenance_manifest.py`
- Mirror byte-identity (`cmp ARCHITECTURE-for-agents.md oap/strategic-instructions/ARCHITECTURE-for-agents.md`): PASSED (identical)
- No live inference, live API call, Docker activity on the protected host, or registry mutation: NOT RUN (not authorized by the order)

## Live model/service evidence
- NOT RUN. The order authorizes no live inference, API call, Docker activity on the protected host, deployment/cutover, registry mutation, or protected profile/key/model/service change. No live endpoint was contacted; no protected fixture was touched.

## GitHub CI / required checks
Implementation head `1fd18d9caebd947a3ed5b2eff600a21e30d60321` — all eight required exact-head checks (verified via check-runs API bound to that head SHA):
- `test` SUCCESS (3m37s; run 39167619193) — full suite on the runner: 1543 passed, 27 skipped, 0 failed; dev-provenance gate `development provenance OK: state=development` (CI checks out the PR merge ref with full history, so the gate verified the merge-of-head commit); artifact policy, docs gate, compileall, bash -n
- `docker` SUCCESS (1m47s) — fresh built wheel bound to the committed development manifest
- `operator-session` SUCCESS (1m2s) — all phases PASSED incl. wheel-binding: `wheel sha256 eb241dda2e079b29... == manifest (state=development)`, expected wheel at `state=development, source=fc6e512c28a7`
- `gateway-contract` SUCCESS (17s) — exact pinned Gateway peer, no inference
- `docker-published` SUCCESS (1m21s) — exact Gateway contract + actual pulled historical-image gates unchanged
- `CodeQL` SUCCESS (3s)
- `Analyze (python)` SUCCESS (1m6s)
- `Analyze (actions)` SUCCESS (43s)
- All required green at drafting: YES
- Report-head checks may be pending; strategy verifies.

## Local setup/dependencies
- Repository-owned uv venv (Python 3.12.15, uv 0.12.5, locked/frozen); no new dependencies; no sudo used; no new services. Disposable 0700-owned temp dirs were used for the clean `git archive` rebuild and the smoke venvs (inert, deletable). All test fixtures were process-local (pytest tmp / mkdtemp) under the recorded umask contexts; no shared host/home permissions were changed.

## Documentation
- Updated in this round: `ARCHITECTURE-for-agents.md` (+ byte-identical mirror), `TESTING.md`, `docs/DEVELOPMENT-PROVENANCE.md`, PR #24 title/body. Required because validation behavior and the criterion-evidence wording changed. `docs/CACHE-REWORK.md`, `docs/CACHE-IMPLEMENTATION-PLAN.md`, the human handoff, prior orders/reports and every frozen publication file were not touched.

## Safety/scope confirmations
- No `src/` product change; no dependency update; no image-policy, Gateway-policy, packaging-policy, registry, RC/tag/version, benchmark, or deployment change.
- No secrets, raw payloads, prompts, images, or private URLs in the diff or this report (targeted scan: no hits).
- Protected 18020/Qwen/Codex fixture changed: NO. No firewall/VPN/network, systemd, model, or key mutation.
- Required tests skipped/not run: none skipped by the implementation (27 skipped are the standing fixture/layer-dependent skips, identical in count to the runner); live-inference layers NOT RUN because not authorized; the 12 host-only safe-evidence cases are recorded as FAILED at the canonical umask 0002 context (never labeled pass) and PASSED at the recorded 022 context and on the runner.
- Scope deviation: none.
- Extra objective PR: NO (PR #24 amended only). Coding merge: NO; auto-merge: NO.
- Active/order edited: NO — committed bytes identical to the strategic-authored order (SHA256 above); `oap/active` unchanged (`016-d`).
- Report commit report-only: yes (only `oap/reports/016-d-selected-state-and-local-test-context.md`, parent = implementation head).
- All 40 v1 runtime criteria: NOT RUN (planned stages); RC10 remains the historical baseline, not a rework-qualified artifact.

## Known limitations/blockers
- At the host's canonical shell umask 0002, the 12 safe-evidence permission-ordering tests still fail (host-environment prerequisite; unchanged from 016-b/016-c; they pass at umask 022 and on the GitHub runner). Not a code regression; never labeled pass here.
- Under umask 077, `test_cache.py::test_untrusted_fallback_is_never_adopted` cannot express its intent (its `mkdir(mode=0o755)` fixture is masked to 0700, which the validator correctly accepts). The recorded resolved test context is therefore umask 022, exactly as the order permits ("077, or 022 if adequate").
- No blocking condition otherwise; no unambiguous safe work was left undone.

## Recommended strategic follow-up
Factual only; strategy decides: verify the report-head checks and the remote report bytes; review the both-states operator validation and the resolved local test context; choose acceptance and the next suffix for objective 016 (or the 017 line per the plan).

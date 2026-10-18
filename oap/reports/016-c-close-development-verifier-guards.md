# OAP Coding-Agent Report — 016-c

## Work order
- Identifier: 016-c; order path: `oap/orders/016-c-close-development-verifier-guards.md`; numeric objective 016
- PR mode: AMENDED_EXISTING_PR (PR #24 only; NO NEW PR)

## Status
COMPLETE (claim for strategic review; not acceptance)

## Executive summary
Closed the five independently confirmed current-development provenance verifier
defects named by order 016-c, without touching the frozen RC10 publication,
adapter runtime (`src/`), dependencies, or any protected fixture:
(1) `current_state`/`verify`/`emit_state` now bind the committed source-input
map AND the actual working-tree map in every frozen/development verification
and CI emission path (dirty or untracked mapped inputs fail closed instead of
acquiring frozen authority); (2) the development contract is actually
enforced — exact key/type/value/schema/lock/toolchain/self-exclusion
validation runs on every public consumption path, including callers of
`verify_development` that bypass the loader (rehearsal), and no usable state
is emitted on invalid input; (3) `operator_session_ci.py` selects and fully
validates the artifact state before comparing the wheel, with a genuine
changed-runtime-source synthetic fixture whose freshly built wheel differs
from the frozen RC10 wheel (dev hash passes; frozen hash and another wrong
hash fail); (4) freeze immutability is now anchored to the independently
pinned pre-rework baseline `f3793af9e5f05bdfba19ef800eeaf57177d0ed2b`
(module constant; CLI never accepts a caller baseline) and checks all 29
existing top-level/archived publication files byte-identical against baseline,
head tree, and working tree, including presence/deletion and
`release_record.json` absence; (5) the two narrow contract clarifications
(shared directory never proves member attribution; criterion evidence-layer
law) landed in the compact architecture (+ byte-identical mirror),
`TESTING.md`, and the stage ledger, with all 40 v1 runtime criteria still
NOT RUN. Full local gate re-run at the implementation head; all eight
required exact-head GitHub checks SUCCESS; the 12 known host-only
safe-evidence failures remain FAILED on this host (byte-identical node-id
list to the pre-change baseline; root cause: host umask 0002 group-write
bits on pytest fixture dirs; an owned private exact-source checkout run with
umask 077 passes all 12; the GitHub runner full suite is fully green), and
they are never labeled pass. No live inference, no Docker activity on the
protected host, no registry/model/network/service mutation.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`; PR #24 https://github.com/ulfe-lmi/slaif-local-coding/pull/24 — OPEN, MERGEABLE, non-draft, single objective PR
- Base `main` = `f3793af9e5f05bdfba19ef800eeaf57177d0ed2b` (also the pinned pre-rework freeze baseline); head branch `oap/016-cache-rework-contracts`
- Starting remote SHA: `0411ac4612bebe3b5c3f3dfb2bd734511f869f3c` (016-b report-only commit)
- Implementation head SHA: 1acc702353489fb7f28833e6581f34a3d3d7128d
- Report publication commit: SELF
- Implementation commits pushed before report: `e2e502a59397cd1219c4fe10eb7c096d67af279f` (verifier guards + tests + docs, 8 files) and `1acc702353489fb7f28833e6581f34a3d3d7128d` (dev-manifest refresh + activated order + `oap/active`, 3 files)
- New PR this round: NO; amended existing PR #24: YES; merge performed: NO

## Changes and files
### `e2e502a` — 016-c: close the current-development provenance verifier guards
- `scripts/dev_provenance_manifest.py`:
  - `current_state` now takes and binds the actual working-tree map
    (`tree_map`) in addition to the committed map; `verify`, `verify_development`,
    and `emit_state` always pass the real tree map, so dirty or untracked
    mapped inputs fail in frozen AND development states (deliberately
    excluded OAP/derived-only differences unchanged).
  - New `_validate_dev_manifest()`: exact top-level key set (schema
    `additionalProperties: false`), schema/version consts, repository and
    state consts, non-release facts, safe source-input paths (no `..`/absolute/
    escape), safe artifact basenames, 64-hex SHA256, real nonnegative ints
    (booleans rejected), toolchain patterns, exact declared
    self-exclusion set, and qualification-label regex. Enforced inside
    `verify_development` itself (covering rehearsal's loader-bypass path) and
    inside `load_dev_manifest`; `MIN_SOURCE_INPUTS = 100` mirrors the schema
    `minProperties`; lock binding `toolchain.uv_lock_sha256 == sha256(current
    uv.lock)`; `emit_state` writes nothing on invalid state. No new dependency.
  - Independent freeze baseline: `PRE_REWORK_BASELINE_COMMIT =
    "f3793af9e5f05bdfba19ef800eeaf57177d0ed2b"` (module constant; the CLI never
    accepts a caller baseline; the typed `baseline_commit` argument exists only
    on `verify`/`verify_development`/`emit_state`/`generate`/
    `frozen_publication_paths` for hermetic fixtures). New
    `verify_frozen_publication_baseline()`: the 5 top-level candidates
    (`rc_artifact_record.schema.json`, `rc_handoff.md`, `rc_record.json`,
    `release_provenance_manifest.json` + schema; `release_record.json` must NOT
    appear) plus all 24 archived `packaging/releases/` files must exist in the
    head tree and working tree byte-identical to the baseline, with no
    deletions and no new top-level/archived records. Called from `verify`
    (both states), `verify_development`, `emit_state` (both states), and
    `generate`.
  - Preserved the delivered `shlex.quote` shell-emission fix; emitted
    frozen/development labels round-trip without execution.
- `scripts/operator_session_ci.py`: new `select_artifact_state(repo,
  baseline_commit=None) -> (state, expected_wheel)` and `bind_wheel_sha256()`;
  `main()` selects and fully validates the state FIRST, then compares the
  wheel argument against exactly that state's expected wheel.
- `tests/test_dev_provenance.py` (suite 16→28): new positives/negatives for
  every order item, including a genuine changed-runtime-source synthetic
  repository (altered `src/fixture/__init__.py`, real `uv build`) whose
  development wheel hash differs from the frozen RC10 wheel;
  `test_real_frozen_publication_baseline_holds` asserts the exact 29-path
  baseline binding in the real repository.
- `ARCHITECTURE-for-agents.md` + byte-identical `oap/strategic-instructions/ARCHITECTURE-for-agents.md` mirror:
  a shared directory no longer implies member attribution — boundaryless
  mixed-eligibility origin remains unresolved whenever attribution is unproven,
  even when the members' directories are proven equal; the fixed off-graph
  no-expansion policy is kept.
- `TESTING.md` + `docs/CACHE-REWORK-LEDGER.md`: a criterion passes only after
  its own required evidence layers pass and are reviewed; pure/unit/fake
  criteria may be proven by their named layers, whereas actual-model,
  genuine-Codex, native-compaction and artifact claims require their distinct
  evidence. All 40 v1 runtime criteria remain NOT RUN.
- `docs/DEVELOPMENT-PROVENANCE.md`: documents the 016-c guards (tree-map
  binding, closed-contract validation, state-before-wheel, independent
  baseline).

### `1acc702` — 016-c: refresh development provenance manifest; commit activated order and active
- `packaging/dev_provenance_manifest.json` regenerated at source `e2e502a`
  (136 source inputs; wheel `eb241dda2e079b29190868108c488edaf98261c84119bfd405070dea98b546b9`,
  sdist `088997cceb6eb7d00cbde6f52a389bcd7be6498a5b18ce45a0f536de1d2dca23`;
  toolchain Python 3.12.15 / uv 0.12.5 / `uv.lock` SHA256 bound; label
  `development-source-e2e502a59397cd1219c4fe10eb7c096d67af279f; not a release
  candidate; not released`).
- `oap/orders/016-c-close-development-verifier-guards.md` committed unchanged
  (SHA256 `945e6445092847ba11c6b9418131edd837c933f70645f40ca725882790d5adb1`,
  byte-identical to the strategic-authored bytes) and `oap/active` = `016-c`.

## Acceptance evidence
### Criterion 1 — bind frozen state to actual inputs
- Pre-fix independent probe (`/home/janezp/codex-supervision/slaif-local-coding/probes/check-dev-dirty-tree.py`, read-only; published helper SHA256 `f3381cb06dcf8d03a22e853774c9df52f65bca20f29774027e5234411a40d799`) accepted a dirty mapped `docs/A.md` and a new untracked mapped `docs/B.md` at frozen HEAD.
- Now `verify`/`verify_development`/`emit_state` perform three independent comparisons (recorded source commit, current head commit, actual working tree) plus the committed-map binding; dirty/untracked mapped inputs fail in frozen AND development states; a clean frozen tree remains supported without a development manifest; `emit_state` emits nothing on invalid state.
- New tests `test_dirty_mapped_input_at_frozen_head_fails`, `test_untracked_mapped_input_at_frozen_head_fails`, `test_dirty_frozen_metadata_in_development_fails`: PASSED (focused suite 28/28).

### Criterion 2 — actually enforce the closed development contract
- The three probe-reproduced violations are now rejected at the intended guard: wrong repository (`synthetic/wrong-repository`), zeroed `toolchain.uv_lock_sha256`, unexpected root key — plus boolean-as-int, path escape, omitted input, malformed nested objects, missing manifest, and label-law violations (`test_closed_contract_negatives_fail`, `test_dev_label_law`, `test_dev_missing_manifest_fails`).
- Validation runs on ALL public consumption paths, including `verify_development` callers that bypass `load_dev_manifest` (rehearsal path covered); `emit_state` emits nothing on invalid state; no new dependency; the `shlex.quote` emission fix is preserved and `test_emit_state_round_trip` proves ordinary frozen/development labels round-trip without execution.
- Result: PASSED (focused suite 28/28; full local gate green except the 12 host-only cases below).

### Criterion 3 — choose operator artifact state before expected wheel
- `main()` now selects and fully validates the state first, then compares the wheel to exactly that state's expected wheel.
- New genuine changed-runtime-source regression: synthetic repository with altered `src/fixture/__init__.py` and a real `uv build` whose wheel hash differs from the frozen RC10 wheel; the development hash passes, while the frozen hash and another wrong hash both fail (`test_operator_binding_changed_runtime_source`); frozen-state positive and mismatched-wheel negative preserved (`test_operator_binding_frozen_state`).
- No Docker/model activity in the focused regression; the existing remote `docker` and `operator-session` checks ran and PASSED at the implementation head (log evidence: `operator-session wheel-binding: PASSED (wheel sha256 eb241dda2e079b29... == manifest (state=development))`; docker `fresh wheel sha256 == expected wheel sha (state=development, source=e2e502a59397)`).

### Criterion 4 — independent pre-rework freeze baseline
- `PRE_REWORK_BASELINE_COMMIT` is a module constant; the production CLI never accepts a caller baseline (typed helper argument for hermetic fixtures only); a development manifest can never choose a new freeze authority (`test_dev_baseline_is_never_chosen_by_the_manifest`).
- Negatives fail at the intended guard, not merely as malformed JSON: a valid-JSON frozen metadata mutation committed inside a newly authored source A (`test_dev_frozen_metadata_mutated_in_new_source_fails`), a deleted archived record (`test_dev_deleted_archived_record_in_new_source_fails`), a new publication record (`test_dev_new_publication_record_in_new_source_fails`), and plain frozen-metadata touch (`test_dev_frozen_metadata_touched_fails`).
- Real repository: all 29 frozen-publication paths (5 top-level + 24 archived `packaging/releases/` files) re-verified byte-identical baseline `f3793af` → implementation head → working tree, 0 mismatches; `release_record.json` absent at baseline and head; no new archived records and no deletions; the only new top-level packaging entries are the development-provenance manifest + schema (development artifacts, not frozen publication records); `test_real_frozen_publication_baseline_holds` asserts exactly this 29-path binding.
- Existing exact frozen-source binding and actual pulled historical-image gates preserved (remote `docker`/`docker-published` PASSED).

### Criterion 5 — two narrow contract clarifications
- Compact architecture and its byte-identical repository mirror (`cmp`-verified): a shared directory never identifies which eligible/off-graph member supplied a reference; boundaryless mixed-eligibility origin stays unresolved whenever member attribution is unproven, even with proven-equal directories; the off-graph no-expansion policy is kept verbatim.
- `TESTING.md` + ledger: a criterion passes only after its own required evidence layers pass and are reviewed; pure/unit/fake by named layers; actual-model/genuine-Codex/native-compaction/artifact claims require their distinct evidence. All 40 v1 runtime criteria remain NOT RUN; no runtime implementation expanded; no live inference required for these pure negative/contract statements.
- Approved plan and human handoff preserved: neither commit touches them; `docs_consistency_check` PASSED (19 claim docs).

## Verification
Fresh full run at implementation head `1acc702353489fb7f28833e6581f34a3d3d7128d` (local gate, this session):
- `uv lock --check`: PASSED
- `uv sync --frozen --extra dev`: PASSED
- `uv run --frozen ruff check .`: PASSED (All checks passed)
- `uv run --frozen ruff format --check .`: PASSED (467 files already formatted)
- `uv run --frozen mypy src tests`: PASSED (Success: no issues found in 87 source files)
- `uv run --frozen python scripts/docs_consistency_check.py`: PASSED (19 claim docs checked)
- `uv run --frozen pytest -q`: 1528 passed, 27 skipped, 12 FAILED — the 12 are the pre-existing host-only safe-evidence permission-ordering cases (`test_safe_evidence.py` ×8, `test_safe_evidence_export.py` ×4); their FAILED node-id list is byte-identical to the pre-change baseline run. These 12 are NOT labeled pass here.
  - Host attribution evidence: this host's umask is `0002`, so pytest tmp fixture directories carry group-write bits that the safe-evidence component-walk rejects (`destination_component_writable`) before the tests' expected later rejection classes; on GitHub runners (umask 0022) they pass — the remote `test` job ran the full suite at the implementation head: 1540 passed, 27 skipped, 0 failed.
  - Owned private exact-source checkout: full committed-branch clone (incl. immutable OAP state and the valid current development manifest) into a 0700-owned root, run with `umask 077` and a private `TMPDIR`: the same 12 node ids — 12 passed in 1.52s. No shared-home permissions, validator, or test were changed.
- `uv build`: PASSED (wheel + sdist)
- `uv run --frozen python scripts/artifact_policy_check.py --dist dist --inspect`: PASSED (0 violations)
- `uv run --frozen python scripts/artifact_policy_check.py --dist dist --install-smoke`: PASSED (0 violations)
- `uv run --frozen python scripts/dev_provenance_manifest.py --verify --dist dist`: PASSED (`state=development head=1acc70235348`; fresh wheel+sdist bound)
- `uv run --frozen python -m compileall -q src tests oap/bin scripts`: PASSED
- `bash -n` over `oap/bin/*.sh` + `packaging/*.sh`: PASSED
- `git diff --check`: PASSED
- Targeted privacy/credential scan over the round diff (2123 lines): PASSED — no key/token/credential/private-IP hits; the only absolute-host paths are the order's own committed runtime-path lines
- Frozen-publication baseline comparison (29 paths, baseline→head→worktree, plus absence/no-new-record checks): PASSED (0 mismatches)
- Independent clean artifact reproduction from `git archive HEAD` in a clean temp tree: PASSED — wheel `eb241dda2e079b29190868108c488edaf98261c84119bfd405070dea98b546b9` and sdist `088997cceb6eb7d00cbde6f52a389bcd7be6498a5b18ce45a0f536de1d2dca23`, both equal to the committed development manifest and the frozen RC10 wheel (no `src/` change this round)
- `scripts/rc_record_present_rehearsal.py` at the implementation head: PASSED (`mode=development (frozen record at boundary; development provenance verified; frozen record cannot authorize this source) digest=real-record+development`)
- RC4 negative anchor: rehearsal at RC4 source `601a7f9fae19869ad8e09f10fa994550368fd87c` FAILED as required (exit 1, `stale prior-RC residue: 0.1.0-rc4`)
- Focused `pytest -q tests/test_dev_provenance.py`: 28 passed (16 pre-existing + 12 new/extended)
- No live inference, live API call, Docker activity on the protected host, or registry mutation: NOT RUN (not authorized by the order)

## Live model/service evidence
- NOT RUN. The order authorizes no live inference, API call, Docker activity on the protected host, deployment/cutover, registry mutation, or protected profile/key/model/service change. No live endpoint was contacted; no protected fixture was touched.

## GitHub CI / required checks
Implementation head `1acc702353489fb7f28833e6581f34a3d3d7128d` — all eight required exact-head checks (verified via check-runs API, `head_sha=1acc70235348...`):
- `test` SUCCESS (3m47s; run 39165687374) — includes full suite (1540 passed/27 skipped), dev-provenance gate (`development provenance OK: state=development`), artifact policy, docs gate
- `docker` SUCCESS (1m37s) — fresh wheel bound to the committed manifest, development label on built image
- `operator-session` SUCCESS (1m6s) — all phases PASSED incl. wheel-binding (state=development)
- `gateway-contract` SUCCESS (15s) — exact pinned Gateway peer, no inference
- `docker-published` SUCCESS (1m14s) — exact Gateway contract + actual pulled historical-image gates unchanged
- `CodeQL` SUCCESS (2s; run 39165685151)
- `Analyze (python)` SUCCESS (53s)
- `Analyze (actions)` SUCCESS (41s)
- All required green at drafting: YES
- Report-head checks may be pending; strategy verifies.

## Local setup/dependencies
- Repository-owned uv venv (Python 3.12.15, uv 0.12.5, locked/frozen); no new dependencies; no sudo used; no new services. The private exact-source checkout used a disposable 0700-owned root under the operator home with its own 0700 temp dir; it is inert and may be deleted. CI ran only in disposable GitHub infrastructure (synthetic registry on runner-ephemeral 18040, loopback fake upstreams on 18033/18031-class ports, all torn down by the jobs).

## Documentation
- Updated in this round: `ARCHITECTURE-for-agents.md` (+ byte-identical `oap/strategic-instructions/` mirror), `TESTING.md`, `docs/CACHE-REWORK-LEDGER.md`, `docs/DEVELOPMENT-PROVENANCE.md` (new 016-c guard documentation). Required because behavior, security/validation, and testing law changed. `docs/CACHE-REWORK.md`, `docs/CACHE-IMPLEMENTATION-PLAN.md`, and the human handoff were not touched.

## Safety/scope confirmations
- No `src/` product change; no dependency update; no image-policy, Gateway-policy, packaging-policy, registry, RC/tag/version, benchmark, or deployment change. The changed runtime wheel exists ONLY in the owned synthetic test repository.
- No secrets, raw payloads, prompts, images, or private URLs in the diff or this report (targeted scan: no hits).
- Protected 18020/Qwen/Codex fixture changed: NO. No firewall/VPN/network, systemd, model, or key mutation.
- Required tests skipped/not run: none skipped by the implementation; the 12 host-only safe-evidence failures are reported truthfully as FAILED on this host (PASSED on the GitHub runner and in the private umask-077 checkout); live-inference layers NOT RUN because not authorized.
- Scope deviation: none.
- Extra objective PR: NO (PR #24 amended only). Coding merge: NO; auto-merge: NO.
- Active/order edited: NO — committed bytes identical to the strategic-authored order; `oap/active` unchanged (`016-c`).
- Report commit report-only: yes (only `oap/reports/016-c-close-development-verifier-guards.md`, parent = implementation head).
- All 40 v1 runtime criteria: NOT RUN (planned stages); RC10 remains the historical baseline, not a rework-qualified artifact.

## Known limitations/blockers
- The 12 safe-evidence permission-ordering tests fail on this host because host umask 0002 grants group-write bits on pytest tmp fixture directories, which the (correct, unchanged) safe-evidence validator rejects as `destination_component_writable` before the tests' expected later rejection classes. This is a host-environment prerequisite, not a code regression: byte-identical FAILED node-id list before and after this round, 12/12 pass in the owned private exact-source checkout under umask 077, and 1540/27/0 on the GitHub runner.
- No blocking condition otherwise; no unambiguous safe work was left undone.

## Recommended strategic follow-up
- Factual only, strategy decides: verify the report-head checks and the remote report bytes; review the five closed guards; choose acceptance and the next suffix for objective 016 (or the 017 line per the plan).

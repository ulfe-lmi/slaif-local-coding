# OAP Coding-Agent Report — 017-n

## Work order
- Identifier: 017-n; order path: `oap/orders/017-n-observer-inventory-
  boundaries.md`; numeric objective 017
- PR mode: AMENDED_EXISTING_PR (PR #25, branch
  `oap/017-cache-read-observation`)

## Status
COMPLETE

## Executive summary
Repaired the per-request observer identity-inventory boundaries on the
inert bundle-observation surface, completing the remaining per-request
repairs required by 017-m. Three bounded defects found by independent
strategic review at the 017-m implementation head are fixed: (a) a
Responses schema-evidenced `custom_tool_call` sharing the ID of an
eligible `function_call` was invisible to the call inventory, because
only `function_call` records were inventoried; (b) `max_commands` /
`max_outputs` were enforced only over the retained eligible subset, so
unknown or malformed calls plus valid reads could evade the budget
(two unknown or two malformed calls plus one valid read under
`max_commands=2`); (c) a missing or non-string result ID disappeared
without typed observability. The selected-endpoint call inventory now
includes the `custom_tool_call` identity alongside `function_call`
BEFORE read eligibility (a colliding exact ID keeps the ambiguous
eligible chain typed and non-removable with no acquired digest/span/
proven members and no first-match; a unique unrelated opaque custom
call does not poison a separate valid read; the opaque custom input is
never captured, echoed, reinterpreted as function arguments or used as
a shell/source oracle; this earns NO custom-tool read parsing,
execution or acquisition). The inventory bounds are now enforced
against the COMPLETE relevant inventory — every schema-position call
record (unsupported names, opaque custom records, missing/empty/
malformed IDs) against `max_commands` and every relevant result record
including invalid IDs against `max_outputs` — before any unbounded
identity map or typed diagnostic is retained, yielding a fixed
non-acquiring `OVER_BOUND` instead of silently truncating and
acquiring an earlier chain while missing a later collision. Malformed
result IDs now yield fixed typed non-echoing `MISSING_RESULT_ID` /
`MALFORMED_RESULT_ID` unpaired limitations (no invented ID, no hash of
an unhashable value, no attachment to any call, no acquisition), while
well-formed independent chains remain useful within the total
inventory limits. The new public suite `TestWireFamilyInventoryAnd-
Bounds` (26 tests) in `tests/test_bundle_d10_matrix.py` plus the new
frozen probe (8/8 at the final head; 3/8 at the 017-m head — the five
inventory-bounds and result-ID negatives failing there) prove the
repaired behavior on Responses and Chat; all 17 frozen probes, the
full local gate (2299 passed / 28 standing skips / 0 failed), the
clean source-A archive reproduction, and the fresh installed-wheel
functional controls (27/27 plus 2 separate metadata assertions) pass.
This is a bounded advancement of the required observation work: the
D09 actual-trace multi-chunk/process collector remains `NOT RUN`, and
the D10 delivery claim requires independent strategic acceptance. No
capture utility/child modification, no actual capture, no process
collector, no graph/RAM/recovery/tokenizer/compiler/image/pipeline/
Gateway/legacy change; the observer stays inert; no v1 runtime
mechanism is active or qualified.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`; PR #25
  https://github.com/ulfe-lmi/slaif-local-coding/pull/25 — OPEN,
  non-draft, no auto-merge
- Base: `main` @ `96c790423f6f0097a56a0b12bacda8a9b6da6aba`
  (unchanged); head branch `oap/017-cache-read-observation`
- Starting remote SHA: `20238868c1f699a17ee23922585b3527c2b4e43b`
  (the 017-m report SELF)
- Implementation head SHA: 7f6c3e8948bfd9e01cc9efc6bc686b361e0962bf
- Report publication commit: SELF
- Implementation commits pushed before report:
  - `ce5e67ac0739ca6d81512b398a035accfc5f306b` (source A: wire-
    family inventory, complete-inventory bounds and result-ID
    observability repair; `TestWireFamilyInventoryAndBounds` suite;
    contract/TESTING/ledger/both architecture maps + byte-identical
    compact mirror; activated order and active unchanged)
  - `7f6c3e8948bfd9e01cc9efc6bc686b361e0962bf` (manifest B:
    `packaging/dev_provenance_manifest.json` refreshed — source
    `ce5e67a…`, 187 inputs, wheel `9ee76e1832c5c116…`, sdist
    `3cea1fe2c1b792fa…`; frozen RC10 publication section untouched)
- New PR this round: NO; amended existing: YES; merge performed: NO
- No reset/clean/rebase/squash/amend/force/force-with-lease; every
  prior published commit preserved (append-only history)

## Changes and files
Round diff (starting SHA .. implementation head) is exactly 12 files:
- `src/slaif_local_coding/constitution/bundles/tool_results.py` —
  `CallRecord` extended to the six-tuple `(wire_family, position,
  location, raw_id, raw_name, arguments)` (custom records carry
  `raw_id`/`raw_name`, `arguments=None`); `_call_records` inventories
  Responses `custom_tool_call` alongside `function_call` (opaque
  `input` never captured; arbitrary nested text objects and untyped
  items are not call records); `_ACQUIRABLE_CALL_FAMILIES =
  frozenset({"function_call","function"})` gates acquisition (a
  different tool name is not a different wire call family; no generic
  unknown-family wildcard recognition); `_result_entries` returns
  typed `ResultDefect` lists — `MISSING_RESULT_ID` (absent/null/empty)
  and `MALFORMED_RESULT_ID` (present non-string) at the relevant
  Responses `function_call_output` and Chat `role=tool` schema
  positions; `_pair_endpoint` now emits result-ID defects after call-
  ID defects and performs endpoint-scoped inspection with a
  `max_items` pre-check before retention, then enforces
  `max_commands` over the COMPLETE call inventory (every call record
  including unsupported names, opaque custom records and
  missing/empty/malformed IDs) and `max_outputs` over the complete
  result inventory (including invalid IDs), returning the fixed
  non-acquiring `("$", "", OVER_BOUND)` result before any identity
  map or diagnostic is built; module docstring law updated.
- `src/slaif_local_coding/constitution/bundles/observation_models.py`
  — closed-vocabulary `Limitation` additions `MISSING_RESULT_ID`,
  `MALFORMED_RESULT_ID` (documented in the observation contract).
- `tests/test_bundle_d10_matrix.py` — new public class
  `TestWireFamilyInventoryAndBounds` (26 tests, all through
  `observe_request`) plus private helpers for custom records and
  defective result IDs; class docstring law added.
- `docs/CACHE-OBSERVATION-CONTRACT.md` — D05 wire-family inventory,
  complete-inventory bounds and result-ID observability bullets,
  limitation vocabulary, boundedness paragraph, 017-n round note in
  the deferred/status sections.
- `docs/CACHE-REWORK-LEDGER.md` — 017-n stage note; D09/D10 row
  updates; objective-017 status sentence.
- `TESTING.md` — 017-n round paragraph (suite, probe, boundary
  statements).
- `ARCHITECTURE.md` and `ARCHITECTURE-for-agents.md` — objective-017
  status/history prose updated with the concise current earned
  scope (all normative law preserved; detailed round history remains
  in the ledger/immutable OAP).
- `oap/strategic-instructions/ARCHITECTURE-for-agents.md` — compact
  mirror, byte-identical to the repo map (`cmp` clean).
- `oap/orders/017-n-observer-inventory-boundaries.md` — activated
  order, exact unchanged strategic bytes.
- `oap/active` — `017-n`, exact unchanged strategic bytes.
- `packaging/dev_provenance_manifest.json` — manifest B refresh only.

## Acceptance evidence
### Requirement 1 — wire families inventoried before read eligibility
- Result: PASS.
- Evidence: frozen probe
  `check-observer-identity-inventory-boundaries.py` at the final
  head: `ordinary_supported_read_control`,
  `unrelated_custom_unique_control`,
  `custom_family_id_collision_never_acquires` PASS (the strategy-
  recorded defect — a Responses `custom_tool_call` sharing the
  eligible `function_call` ID was ignored — fails at the 017-m head
  and is covered by the collision negative). In-suite (Requirement-1
  tests of `TestWireFamilyInventoryAndBounds`, both collision
  orderings): the colliding exact ID keeps the ambiguous eligible
  chain typed `DUPLICATE_CALL_ID` at every occurrence (never first-
  match), non-removable, with NO acquired digest/span/proven-executed
  members; a unique unrelated opaque custom call is neither recorded
  as a read nor allowed to poison a separate valid chain (exact
  earned read asserted in the same payload); a custom name spelled
  like a supported tool still never acquires (family gates, not
  name); the opaque custom input is never echoed in any observation
  metadata and never reinterpreted as function arguments or a
  shell/source oracle; nested text objects and untyped items carrying
  id/name are not call records. Chat function inventory and its
  malformed-field typing are preserved unchanged (all pre-existing
  Chat tests pass). No new grammar support, no custom-tool read
  parsing/execution/acquisition earned.
### Requirement 2 — complete inventory bounded
- Result: PASS.
- Evidence: frozen probe: `unknown_calls_cannot_evade_command_
  inventory_budget` and `malformed_calls_cannot_evade_command_
  inventory_budget` PASS (at the 017-m head, two unknown or two
  malformed calls plus one valid read evaded `max_commands=2`). In-
  suite: at-limit still acquires (`test_at_limit_unknown_and_valid_
  still_acquires`, `test_outputs_at_limit_including_defects_still_
  acquires` — no blanket reject-all); one-over is the fixed
  non-acquiring `OVER_BOUND` (`test_one_over_with_unknown_calls_is_
  fixed_over_bound`, `test_chat_one_over_many_tool_calls_one_
  message`); malformed, missing and custom records all count toward
  the command bound (`test_malformed_call_ids_count_toward_bound`,
  `test_missing_call_ids_count_toward_bound`, `test_custom_records_
  count_toward_bound`); many `tool_calls` inside ONE assistant
  message bounded at-limit and one-over on Chat; a late collision
  beyond the retained prefix is still caught (`test_late_collision_
  beyond_retained_prefix`); `max_outputs` counts result records with
  invalid IDs (`test_outputs_bound_counts_invalid_result_ids`);
  explicit endpoint selection scopes the bound to the selected domain
  (Responses and Chat); mixed input remains non-acquiring under
  existing law and bounded across its inspected domains; an over-
  long container is the fixed `OVER_BOUND`. Output/diagnostic record
  counts stay bounded; no private content/ID values appear in any
  repr, error or metric.
### Requirement 3 — malformed result IDs observable
- Result: PASS.
- Evidence: frozen probe: `missing_result_id_is_observable` and
  `malformed_result_id_is_observable` PASS (at the 017-m head,
  missing or non-string result IDs disappeared without typed
  observability). In-suite: absent/null/empty result IDs yield fixed
  typed `MISSING_RESULT_ID` and present non-string result IDs (list,
  dict, number) yield `MALFORMED_RESULT_ID` on both Responses
  `function_call_output` and Chat `role=tool` positions — non-
  echoing, unpaired, never inventing an ID, never hashing an
  unhashable value, never attached to any call, never acquired
  (`test_responses_result_id_defects_are_typed`,
  `test_chat_result_id_defects_are_typed`,
  `test_malformed_result_never_attached_hashed_or_acquired`);
  result-ID defects coexist with the pre-existing duplicate-result/
  missing-call/mismatched-result/structural pre-call typing and
  namespace/domain separation, and well-formed independent chains
  remain useful within the total inventory limits
  (`test_result_id_defects_coexist_with_mismatch_typing`). Unique
  unsupported families earn no read support; opaque result families
  keep their family association rather than impersonating function
  outputs; no new native format claim.
### Requirement 4 — public regression proof
- Result: PASS (delivery claim requires independent strategic
  acceptance).
- Evidence: 26 new public tests in
  `tests/test_bundle_d10_matrix.py::TestWireFamilyInventoryAndBounds`
  all through public `observe_request` — both collision orderings,
  repeated identical/conflicting records, supported/unsupported/
  custom positive controls, missing/null/empty/list/dict/number
  result IDs, all-inventory bounds (at-limit and one-over, Responses
  and Chat, many tool_calls in one assistant message) and a late
  collision beyond the retained prefix — asserting exact valid
  digest/source-slice/members/width, input immutability (deep
  equality before/after), NO acquired digest/span/proven-executed
  state for rejected chains, bounded typed metadata and non-echoing
  representations. All previously earned 017-m numeric causality
  tests, selected/mixed/ignored-domain behavior, and all literal
  read/plan/loop positives, exact spans, aggregate work bounds and
  occurrence/member-hash laws are preserved (the full focused
  observer suite is 565 passed; no pre-existing test changed). No
  shell/filesystem/network execution oracle, no new dependency or
  framework.
### Documentation
- Result: PASS.
- Evidence: observation contract (wire-family inventory, complete-
  inventory bounds, result-ID vocabulary and law, status/deferred
  notes), TESTING.md round paragraph, ledger (017-n stage note,
  D09/D10 rows, objective-017 status), both architecture maps with
  concise current earned scope (normative law preserved), compact
  mirror `cmp` byte-identical, PR body updated (017-n round-history
  entry, earned-boundary update, 017-n evidence block). No
  architecture exception; no change to the human handoff, plan,
  frozen releases or prior OAP bytes.

## Verification
- 17 frozen strategic probes, each
  `REPO/.venv/bin/python STRATEGIC_HOME/probes/<script> --head
  7f6c3e8948bfd9e01cc9efc6bc686b361e0962bf` (canonical repo venv;
  owned 0700 temp results root outside the strategic workspace):
  PASSED — 23/23 (`check-bundle-observation.py`), 16/16
  (`check-read-option-semantics.py`), 5/5
  (`check-endpoint-selection.py`), 6/6
  (`check-root-endpoint-context.py`), 40/40
  (`check-finite-read-plans.py`), 63/63
  (`check-literal-loops.py`), 10/10
  (`check-loop-word-boundaries.py`; 162 quoted-word variants), 12/12
  (`check-real-client-capture-v2.py`), 3/3
  (`check-capture-file-boundaries.py`), 2/2
  (`check-capture-selection-boundaries.py`), 4 checks + 1 memory
  measurement (not a test)
  (`check-capture-resource-boundaries.py`), 2/2
  (`check-capture-process-boundaries.py`), 2/2
  (`check-capture-issued-registry.py`), 8/8
  (`check-capture-finalization-v3.py`), 5/5
  (`check-capture-owned-io-and-seed-v2.py`), 8/8
  (`check-observer-pairing-causality.py`) and 8/8 (new
  `check-observer-identity-inventory-boundaries.py` — 3 positive
  controls + 5 negatives; at the 017-m implementation head the same
  probe passed only 3/8) — every check/control passed with valid
  positive controls; the new probe re-run at the final head re-
  confirmed `all_checks_passed: true` before report publication.
  Every script SHA-256 verified against the immutable baseline
  `STRATEGIC_HOME/reviews/017-n-probe-hashes.json` (17/17) before and
  at the final head; no script or hash file edited.
- Focused observer suites (all 10 `tests/test_bundle_*.py` including
  the extended matrix): `uv run --frozen pytest -q tests/
  test_bundle_client_paths.py tests/test_bundle_compound_reads.py
  tests/test_bundle_d10_matrix.py tests/test_bundle_literal_loops.py
  tests/test_bundle_observation_models.py tests/test_bundle_observe.
  py tests/test_bundle_read_grammar.py tests/test_bundle_root_
  envelopes.py tests/test_bundle_shell_tokens.py tests/test_bundle_
  tool_results.py`: PASSED — 565 passed, 0 failed, 0 skipped
  (re-verified at the final implementation head before report
  publication).
- Complete final TESTING gate (non-root process-local umask 022,
  repository root; full re-run to completion as the final gate):
  - `uv lock --check`: PASSED
  - `uv sync --frozen --extra dev`: PASSED
  - `uv run --frozen ruff check .`: PASSED (all checks passed)
  - `uv run --frozen ruff format --check .`: PASSED (522 files
    already formatted)
  - `uv run --frozen mypy src tests`: PASSED (108 source files, no
    issues)
  - `uv run --frozen python scripts/docs_consistency_check.py`:
    PASSED (19 claim docs checked)
  - `uv run --frozen pytest -q`: PASSED — 2299 passed, 28 skipped
    (27 prior stage skips + exactly one 017-i real-`chown`
    environment skip — never counted passed), 0 failed, 379.74s
  - `uv build`: PASSED — wheel
    `9ee76e1832c5c11620ea884491592291c6a9b633c294d2a9998095b478e74490`
    (140705 bytes, 37 entries) / sdist
    `3cea1fe2c1b792faf826010e1edd75c546790227ad49fcef83d9700f8bd7c024`
    (716283 bytes, 185 entries), equal to the manifest digests
  - `uv run --frozen python scripts/artifact_policy_check.py --dist
    dist --inspect`: PASSED (ok, 0 violations)
  - `uv run --frozen python scripts/artifact_policy_check.py --dist
    dist --install-smoke`: PASSED (ok, 0 violations)
  - `uv run --frozen python scripts/dev_provenance_manifest.py
    --verify --dist dist`: PASSED (state=development, head
    `7f6c3e8948bf…`)
  - `python -m compileall -q src tests oap/bin scripts`: PASSED
- Earlier actual failed runs (distinct from the final gate, reported
  per the order):
  1. Pre-A/B full `pytest -q` (before the source-A/manifest-B
     commits): 2297 passed, 28 skipped, 2 expected failures —
     `test_real_development_state_consistent` and
     `test_real_repo_source_inputs_bound_to_committed_source`
     (manifest staleness by construction), resolved by manifest B;
     no code-related failure.
  2. First full gate run after the final A/B (umask 022): the six
     pre-pytest stages PASSED; `pytest -q` finished 2289 passed,
     28 skipped, 1 failed + 9 errors, all ten on TRANSIENT PyPI
     connection timeouts inside the network-dependent in-test `uv
     build` fixtures (`test_rc_record_present_rehearsal` and the
     `clean_bundle` module fixture of
     `tests/test_release_provenance_manifest.py`) — a host network
     instability at that moment (direct PyPI fetch verified
     failing-then-recovering during the round; the same tests
     passed in the pre-A/B run and in CI). The full gate was then
     re-run once to completion: the final gate above, GATE-EXIT=0
     with 0 failed. No validator or oracle was weakened and no skip
     disguised; the re-run was triggered by the actual failure only.
- `bash -n` over `oap/bin/bootstrap-two-codex-oap.sh`,
  `oap/bin/launch-coding-agent.sh`,
  `oap/bin/launch-strategic-agent.sh`, `packaging/readyz-wait.sh`
  (no shell script changed this round): PASSED
- `git diff --check origin/main..HEAD`: PASSED (clean)
- Targeted credential/raw-log/privacy scan of the round diff
  (`2023886….7f6c3e8…`): PASSED — 3 benign hits only (the activated
  order's own text; the synthetic test canary
  `CANARY-RESULT-ID-77ab2`); no bearer/key-like tokens, no
  private/loopback URLs, no host references, no API-key literals.
- Invariance: PASSED — frozen `docs/CACHE-REWORK.md` SHA-256
  `410df5c0b8f90b05220adc32c8e673b143c0cf1fa3da02270d91ac453c8
  86abd` unchanged; `docs/RC-HANDOFF.md`,
  `docs/CACHE-IMPLEMENTATION-PLAN.md`, all prior `oap/orders/*` and
  `oap/reports/*`, and `packaging/releases/` byte-unchanged in the
  round diff (the diff touches exactly the 12 listed files); compact
  mirror `cmp` byte-identical; frozen RC10 baseline re-proved in-
  suite within the 2299.
- Clean source-A `git archive` reproduction (owned 0700 temp root):
  PASSED — `git archive ce5e67a…` with utility
  `scripts/real_client_capture.py`, fake child
  `scripts/real_client_capture_fake_child.py`,
  `tests/test_real_client_capture.py` and the extended
  `tests/test_bundle_d10_matrix.py` present; `uv sync --frozen
  --extra dev` + `uv build` from the clean tree reproduced byte-
  identical wheel `9ee76e1832c5…` / sdist `3cea1fe2c1…` (equal to
  the manifest digests).
- Fresh non-editable installed-wheel functional controls (fresh
  CPython 3.12 venv in an owned 0700 temp root outside the
  repository; wheel installed non-editable, no cache): PASSED —
  27/27 functional controls: the 11 recorded 017-g observer
  functional controls (defect forms typed non-removable with no
  digest/span/phantom members; first-position defect typed; whole-
  word double-/single-quoted and plain controls earned with exact
  members; guarded ordered bundle with exact digest/slot width/
  exact content span; unguarded form typed `LOOP_ITERATION_
  UNPROVEN` with preserved requested members and no digest; repr
  privacy) PLUS all 8 public pairing/causality cases PLUS all 8 new
  inventory-oracle cases against the installed changed package. Two
  metadata/path/version assertions (site-packages path
  `…/venv2/lib/python3.12/site-packages/slaif_local_coding/__init__.
  py`; version 0.1.0) are separate from the functional count.

## Live model/service evidence
- N/A: the order authorizes offline pure/synthetic fixtures and
  owned ephemeral loopback tests only. No live inference, no actual
  client session/capture, no model/GPU/product-API/Gateway call, no
  Docker host use, no namespace/tracing experiment.
  **Protected fixture changed: NO** — Qwen/vLLM 18020,
  `qwen-serving`, models/venvs/patches/flags, API-key files,
  firewall/VPN/network, active protected Codex profiles/auth/config
  all untouched; no original raw capture read or recreated. Unknown
  startup safety remains NOT READY (no handwritten readiness
  substitution).

## GitHub CI / required checks
- Implementation-head (`7f6c3e8948bfd9e01cc9efc6bc686b361e0962bf`)
  check state, all 8 required checks present and SUCCESS (main
  workflow run 39810291495; CodeQL run 39810274679):
  - `test`: SUCCESS (4m53s)
  - `gateway-contract`: SUCCESS (17s)
  - `docker`: SUCCESS (1m41s)
  - `docker-published`: SUCCESS (1m27s, prepublication NOT RUN for
    image qualification per policy)
  - `operator-session`: SUCCESS (1m0s)
  - `CodeQL`: SUCCESS
  - `Analyze (actions)`: SUCCESS (37s)
  - `Analyze (python)`: SUCCESS (51s)
- All required green at drafting: YES.
- Report-head checks may be pending; strategy verifies.

## Local setup/dependencies
- Repository-owned `.venv` (Python 3.12, uv locked/frozen); no new
  dependency, framework or service; no sudo used. Process-local
  umask 022 for the full repository test gate (the verified context
  per TESTING.md); owned 0700 protected temp roots for probe
  results, the git-archive reproduction, and the fresh-wheel venv.
  No durable docs/config change beyond the listed round files.

## Documentation
- Updated: `docs/CACHE-OBSERVATION-CONTRACT.md` (D05 wire-family
  inventory, complete-inventory bounds, result-ID vocabulary and
  law, status/deferred notes), `TESTING.md` (017-n round
  paragraph), `docs/CACHE-REWORK-LEDGER.md` (017-n stage note;
  D09/D10 rows; objective-017 status), `ARCHITECTURE.md` and
  `ARCHITECTURE-for-agents.md` (017 status prose updated; concise
  current earned scope), byte-identical compact mirror, PR body.
  Required: behavior, configuration-adjacent contract, tests and
  limitations all changed.

## Safety/scope confirmations
- Unrelated files: none touched — round diff is exactly the 12
  listed files (11 source-A files plus 1 manifest B file).
- Secrets/raw content: none committed, printed, logged or exposed;
  synthetic fixtures only; targeted scan of the round diff clean
  (3 benign hits accounted for); reprs non-echoing by law and by
  test.
- Production/protected resources: no production system or data
  touched. Protected fixture changed: NO.
- Required tests skipped/not run: none beyond the standing skips —
  27 prior stage skips + exactly one 017-i real-`chown` environment
  skip, never counted passed. D09 actual-trace multi-chunk/process
  association and all v1 runtime/model/native/restart
  qualification remain NOT RUN (planned for their owning stages).
- Scope deviation: none — no capture utility/child modification, no
  actual capture, no process collector, no graph/RAM/recovery/
  tokenizer/compiler/image/pipeline/Gateway/legacy change; existing
  observer stays inert; no new framework/dependency or
  opportunistic refactor; no architecture exception; no change to
  human handoff/plan/frozen releases/prior OAP bytes.
- Extra objective PR: NO. Coding merge: NO. Auto-merge: not enabled.
- Active/order edited: NO (exact unchanged strategic bytes
  committed; `oap/active` = `017-n`). Report commit report-only: YES
  (staged path `oap/reports/017-n-observer-inventory-boundaries.md`
  only; sole parent = implementation head).

## Known limitations/blockers
- None blocking. Open items by design (not blockers): D09 actual-
  trace multi-chunk process completion proof and the process/chunk
  collector remain deferred to a later same-PR suffix (a later
  exact order may authorize one bounded reviewed actual capture,
  then the collector, subject to review); the D10 delivery claim
  requires independent strategic acceptance; whole-017 acceptance
  and objectives 018-024 remain with strategy.

## Recommended strategic follow-up
Factual only; strategy decides. Independent verification of the
017-n head is available: 17 frozen probes (baseline
`reviews/017-n-probe-hashes.json`), the 26-test public inventory-
boundary suite (`tests/test_bundle_d10_matrix.py::
TestWireFamilyInventoryAndBounds`), the 8/8 inventory probe at
`7f6c3e8948bfd9e01cc9efc6bc686b361e0962bf`, and the 27/27 fresh-
wheel functional controls. If accepted, the remaining 017 work is
the D09 actual-trace multi-chunk/process association (actual-trace
capture and process/chunk collector) for a later same-PR suffix;
otherwise the round stands as a bounded observation-surface repair
with D10 `PENDING`.

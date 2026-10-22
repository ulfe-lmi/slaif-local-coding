# OAP Coding-Agent Report — 017-e

## Work order
- Order: `oap/orders/017-e-echo-semantics-and-grammar-identity.md`
  (objective 017, round 017-e, AMEND_EXISTING_PR); committed
  unchanged with the first implementation commit A (SHA256
  `34f01422e90f2cbb6f9e090b390987f29bce54895c53a9f6ddeb8eac8e7a7b67`);
  `oap/active` = `017-e` (bytes `017-e\n`, SHA256
  `9182abe7520b353590dae1148ca2220b0fa3d39115d66634b6375a5aa0cb717a`);
  both committed unchanged with the first implementation commit A
  (activation bytes preserved, not edited).
- PR mode: AMENDED_EXISTING_PR — exact OPEN PR #25
  https://github.com/ulfe-lmi/slaif-local-coding/pull/25, base `main`,
  head branch `oap/017-cache-read-observation`. NO NEW PR; no coding
  merge or auto-merge.
- Starting remote PR/report head verified before mutation:
  `75d7adb029decf1be579e4ac370f3d97b111a02c` (sole parent
  `a29d4144098ba289c06d785d258cd48f1e473439`); remote `main`
  `96c790423f6f0097a56a0b12bacda8a9b6da6aba` (unchanged); local working
  tree clean at round start except the activated 017-e order (new
  untracked file) and `oap/active` (017-d -> 017-e), both committed
  unchanged in A.
- Round-start baselines (strategic probes, unchanged files, at the
  starting head, canonical repo `.venv` Python, `--head` = starting
  head): `check-bundle-observation.py` 23/23,
  `check-read-option-semantics.py` 16/16,
  `check-endpoint-selection.py` 5/5,
  `check-root-endpoint-context.py` 6/6 — all PASS with valid positive
  controls; `check-finite-read-plans.py` 36/40 with exactly the four
  ordered failures:
  `echo_quoted_n_prefix_never_strips_source`,
  `echo_quoted_n_suffix_never_strips_source`,
  `echo_quoted_ne_prefix_never_strips_source`,
  `finite_plan_grammar_identity`.

## Status
COMPLETE for the bounded 017-e correction slice (literal echo
option-semantics boundary law plus actual plan-grammar evidence
identity in the inert finite read-plan observer) — a claim for
strategic review, not acceptance. Objective 017 as a whole (D01-D10)
remains open: D09/D10 (literal loops, multi-chunk process pairing and
the remaining truncation matrix) move to later same-PR suffixes (the
earlier planned 017-e loops/chunks draft is superseded; strategy now
plans 017-f literal loops and 017-g process/chunk association, subject
to review). The bundles modules remain inert: not active in the
adapter, legacy detector unchanged. All v1 runtime criteria remain
NOT RUN.

## Executive summary
1. Echo option semantics (defects 1-3): quoting does not disable
   `echo`'s own option parser. The plan grammar now types a clean
   fully-quoted echo literal whose cooked value is dash-leading
   (`-n`, `-e`, `-E`, combinations and repetitions, either quote
   kind) as `ECHO_TARGET_UNSUPPORTED`: such commands keep their typed
   unsupported observation with the cat request preserved, no removable
   span, no valid bundle digest and no `content_span` — instead of
   inventing a false prefix/suffix boundary from matching file bytes.
   The exclusion is the ordered conservative dash-leading form (a
   lone `-` is included); non-dash-leading literals (markers, a dash
   inside the literal, the empty literal) stay earned, and exact
   anchored positions, collision safeguards and input immutability are
   unchanged. No general echo interpreter, no evaluation, no new shell
   dependency.
2. Grammar identity (defect 4): the fallback selection is explicit and
   documented: the single-command grammar (`literal-shell-read/v1`) is
   primary; a command it does not complete is evaluated by the
   finite-plan parser, and every observation that parser produces —
   complete, unsupported, nonzero, missing/truncated/running,
   malformed-content and outer-boundary-unproven — carries the actual
   `READ_PLAN_GRAMMAR` (`literal-read-plan/v1`) via the shared version
   constant (no duplicated magic strings). Observations the single
   grammar actually earned keep `READ_GRAMMAR`. The grammar label never
   changes outcome, completeness, removability or digests; an
   unsupported attempt is never a successful plan. Wrapper format
   stays a separate identity. No unrelated version/schema redesign, no
   app/cache/compiler wiring.
3. All five unchanged strategic probes now pass 90/90 at the
   implementation head with valid positive controls
   (23/23, 16/16, 5/5, 6/6, 40/40 — the finite-plan probe went from
   36/40 at the starting head to 40/40).
4. 23 new named regressions (381 -> 404 focused across
   `tests/test_bundle_*.py`): `TestEchoOptionSemantics` (7,
   primitive), `TestEchoOptionSemanticsComposition` (5, public
   `observe_request`) and `TestPlanGrammarIdentity` (11, public
   composition across every plan-grammar outcome plus single-grammar
   contrast). Full locked gate green locally (1947 passed, 27
   standing skips, 0 failed); artifacts byte-reproducible from the
   clean `git archive` of source commit A in a fresh venv, verified by
   a fresh non-editable install smoke proving safe echo and real
   grammar identity.
5. Docs/contracts updated in the same PR: observation contract (echo
   law + grammar-identity fallback law), stage ledger (exact
   corrections, named tests, remaining limitations, D09/D10
   succession), TESTING.md, `ARCHITECTURE.md`, both architecture maps
   with the byte-identical compact mirror, PR #25 description;
   development provenance manifest B refreshed (frozen RC10
   publication bytes untouched).

## Authoritative GitHub state
- Repository `ulfe-lmi/slaif-local-coding`; PR #25 OPEN, mergeable,
  base `main`, head branch `oap/017-cache-read-observation`
  (reconciled before mutation and re-verified after push).
- Starting remote PR/report head: `75d7adb029decf1be579e4ac370f3d97b111a02c`.
- Remote `main` unchanged: `96c790423f6f0097a56a0b12bacda8a9b6da6aba`.
- New PR created: NO. Existing PR amended: YES. Merge/auto-merge: NO.
- Implementation commits pushed before report (all on PR #25):
  - A = `28a7bdab44a07d5e05db5a332af1d5eadf26a4d3` — "017-e: correct
    echo option semantics and plan-grammar identity" (11 files:
    `compound_reads.py`, `tool_results.py`,
    `tests/test_bundle_compound_reads.py`,
    `docs/CACHE-OBSERVATION-CONTRACT.md`, `docs/CACHE-REWORK-LEDGER.md`,
    `TESTING.md`, `ARCHITECTURE.md`,
    `ARCHITECTURE-for-agents.md`,
    `oap/strategic-instructions/ARCHITECTURE-for-agents.md`, activated
    order + `oap/active` with unchanged activation bytes).
  - B = `43e9c645de04b6eddb6a6af21145039265a157e0` — "017-e: refresh
    development provenance manifest" (manifest-only) — the
    implementation head.
- Remote branch and PR head both equal B at publication time.

Implementation head SHA: 43e9c645de04b6eddb6a6af21145039265a157e0
Report publication commit: SELF

## Changes and files (A 11 files, +452/-38; B manifest-only 12+/12-)
Source (`src/slaif_local_coding/constitution/bundles/`):
- `compound_reads.py` (A): `_parse_statement` echo branch — after the
  clean fully-quoted check, a cooked literal starting with `-` is
  `ECHO_TARGET_UNSUPPORTED` (quoting does not disable echo's option
  parser; the actual `echo '-n'` writes nothing; command-local grammar
  semantics precede boundary matching); module docstring updated
  (grammar line and echo bullet).
- `tool_results.py` (A): imports `READ_PLAN_GRAMMAR`; the documented
  grammar-identity fallback law is stated at the plan-branch entry,
  and all six plan-branch `ReadObservation` constructors (typed
  unsupported plan, process-running, malformed-content, complete with
  proven region, outer-boundary-unproven, unproven-wrapper) now carry
  `read_grammar=READ_PLAN_GRAMMAR`; single-grammar observations keep
  the `READ_GRAMMAR` default.

Tests (`tests/test_bundle_compound_reads.py`, +23 named regressions):
- `TestEchoOptionSemantics` (7, primitive): single-quoted `'-n'`
  prefix typed (plan incomplete, cat request preserved, no span),
  double-quoted `"-n"` prefix typed, option combinations
  (`'-ne'`, `"-ne"`, `'-e'`, `"-E"`, `'-nE'`) typed, repeated option
  literals typed, unquoted option typed, dash-alone conservatively
  typed, non-dash-leading literals (marker, dash-inside, empty) stay
  earned.
- `TestEchoOptionSemanticsComposition` (5, public `observe_request`):
  `echo '-n'` prefix never strips a `-n\n`-led source (UNSUPPORTED,
  non-removable, no digest, no span, requested members preserved, plan
  grammar), `echo "-n"` double-quoted suffix likewise, `echo '-ne'`
  prefix with the fake boundary repeated inside source, source
  containing a real marker line stays typed (matching file bytes never
  establish echo output), and the earned `echo '===READ==='` marker
  control remains a complete removable bundle exposing only the pure
  file span.
- `TestPlanGrammarIdentity` (11, public composition): complete chain
  carries `READ_PLAN_GRAMMAR` (wrapper format separate); unsupported
  plan, nonzero, truncated, missing-body, process-running,
  malformed-Unicode-content and outer-boundary-collision outcomes all
  carry the plan grammar; a single complete read keeps
  `READ_GRAMMAR`; a single unsupported read is labeled by the fallback
  parser but stays UNSUPPORTED (never a successful plan); a single
  nonzero read keeps `READ_GRAMMAR`.

Docs/contracts:
- `docs/CACHE-OBSERVATION-CONTRACT.md`: intro round 017-e paragraph;
  section 4a grammar line (echo cooked value not dash-leading), echo
  bullet (option law + narrow conservative exclusion + grammar-
  semantics-precede-boundary-matching), new "Grammar identity (017-e)"
  bullet (fallback law, shared constants, wrapper-format separation);
  section 11 deferred text (superseded 017-e loops/chunks draft;
  017-f/017-g planned, subject to review).
- `docs/CACHE-REWORK-LEDGER.md`: header 017-e correction text and
  D09/D10 succession; D06 and D08 rows carry the exact 017-e named
  test evidence (stage states remain PENDING acceptance); objective
  succession 017 row updated.
- `TESTING.md`: stage-017 paragraph (017-e correction and the three
  named regression classes; D09-D10 succession corrected).
- `ARCHITECTURE.md`: stage 017-e sentence (no v1 runtime claim).
- `ARCHITECTURE-for-agents.md` + byte-identical mirror
  `oap/strategic-instructions/ARCHITECTURE-for-agents.md` (verified
  with `cmp`): read-observation bullet (echo option law + grammar
  identity law) and objective-boundary 017 row (017-e correction;
  D09/D10 to 017-f/017-g).
- `oap/orders/017-e-echo-semantics-and-grammar-identity.md` +
  `oap/active` (A): activated order committed unchanged.
- `packaging/dev_provenance_manifest.json` (B): refreshed development
  manifest bound to source A (183 inputs; `frozen_publication` and
  release sections byte-unchanged, verified by section comparison).
- PR #25 description updated around the final behavior (017-e section;
  verified byte-identical after `PATCH` via `gh api`, apart from one
  trailing newline).

## Acceptance evidence (order requirement -> behavior -> named
regressions)
| Order requirement | Earned behavior | Named regressions (all PASSED) |
| --- | --- | --- |
| Quoted option-like operands (`-n`, `-e`, `-E`, combinations/repetitions) never assumed literal+newline; both quote kinds | Dash-leading cooked echo literal typed `ECHO_TARGET_UNSUPPORTED`, plan incomplete, cat request preserved, no span/digest | `TestEchoOptionSemantics::test_single_quoted_option_prefix_is_typed`, `::test_double_quoted_option_prefix_is_typed`, `::test_option_combinations_are_typed`, `::test_repeated_option_literals_are_typed`, `::test_unquoted_option_is_typed` |
| Preserve such commands as typed unsupported with no removable span or valid bundle digest (preferred narrow correction) | Observation UNSUPPORTED/UNSUPPORTED, `removable=False`, `bundle_digest=None`, `content_span=None`, `ECHO_TARGET_UNSUPPORTED` in reasons, requested members preserved | `::test_single_quoted_option_prefix_is_typed` (region `(None, (OUTER_BOUNDARY_UNPROVEN,))`), `TestEchoOptionSemanticsComposition::test_quoted_n_prefix_never_strips_source`, `::test_double_quoted_n_suffix_never_strips_source`, `::test_ne_prefix_with_fake_boundary_inside_source` |
| No general echo interpreter/evaluation/new shell dependency; existing marker/empty/Unicode positives and labels inside source preserved | Dash-leading exclusion only; marker/dash-inside/empty literals still earn boundaries at exact anchored positions | `::test_non_option_literals_stay_earned`; `TestEchoOptionSemanticsComposition::test_single_quoted_marker_still_earned_in_source` (control: complete, removable, span == pure file span, exact digest); existing `TestEchoOuterBoundaries`/`TestOuterSourceRegions`/`TestOuterRegionComposition` unwithdrawn and passing in the 404 focused set |
| Exact anchored positions, collision safeguards and input immutability | `_observe` asserts payload deep-equality on every composition call; collision/mismatch typing unchanged | `TestEchoOptionSemanticsComposition` (all five cases through `_observe`), unchanged `TestOuterSourceRegions::test_collision_shorter_than_boundaries_is_typed`, `::test_extra_output_before_prefix_is_typed`, `::test_mismatched_suffix_is_typed` |
| Command-local grammar semantics precede boundary matching; matching file bytes cannot establish echo printed them; source containing the fake boundary covered | Plan typed before `plan_source_region` is reached; fake/real marker inside source stays source | `TestEchoOptionSemanticsComposition::test_source_containing_real_marker_stays_typed`, `::test_ne_prefix_with_fake_boundary_inside_source`; `TestEchoOptionSemantics::test_single_quoted_option_prefix_is_typed` (region None for a `-n\n`-led source) |
| No per-file versions/hashes manufactured; source bytes not normalized | Unsupported echo plans carry no digests at all; earned-bundle digest law unchanged | `TestEchoOptionSemanticsComposition` (digests absent); unchanged `TestChainedPlanComposition::test_single_member_chain_proves_member_digest` (single distinct member only) |
| Plan parser observations carry the actual `READ_PLAN_GRAMMAR` across complete, unsupported, nonzero, missing/truncated/running/malformed and outer-boundary outcomes | All six plan-branch observation constructors carry `READ_PLAN_GRAMMAR`; shared constant, no magic strings | `TestPlanGrammarIdentity::test_complete_chain_carries_plan_grammar`, `::test_unsupported_plan_carries_plan_grammar`, `::test_nonzero_chain_carries_plan_grammar`, `::test_truncated_chain_carries_plan_grammar`, `::test_missing_body_chain_carries_plan_grammar`, `::test_process_running_chain_carries_plan_grammar`, `::test_malformed_unicode_chain_carries_plan_grammar`, `::test_outer_boundary_collision_carries_plan_grammar` |
| Single grammar preserved when it earned the observation; fallback documented; unsupported single read never a successful plan | Single complete/nonzero reads keep `READ_GRAMMAR`; fallback-labeled unsupported single read stays UNSUPPORTED with no digest | `::test_single_complete_read_keeps_single_grammar`, `::test_single_nonzero_read_keeps_single_grammar`, `::test_single_unsupported_read_is_never_a_successful_plan` |
| Meaningful public-composition assertions for actual grammar selection | Every grammar assertion runs through `observe_request` (public composition), not object construction | all `TestPlanGrammarIdentity` and `TestEchoOptionSemanticsComposition` cases (via `_observe`) |
| No raw untrusted source/literals in new repr/errors/logging | New code paths raise no exceptions; limitation enums only; reprs carry spans/flags only (unchanged privacy law) | privacy scan of round-added lines (below) |

Strategic probes (unchanged files, canonical repo `.venv` Python 3.12.15,
`--head 43e9c645de04b6eddb6a6af21145039265a157e0`, verified against
`reviews/017-e-probe-hashes.json` before and after):
- `check-bundle-observation.py`: 23/23 PASS, positive control valid.
- `check-read-option-semantics.py`: 16/16 PASS.
- `check-endpoint-selection.py`: 5/5 PASS.
- `check-root-endpoint-context.py`: 6/6 PASS.
- `check-finite-read-plans.py`: 40/40 PASS (starting-head baseline
  36/40 with exactly the four ordered failures; all four now pass),
  positive control valid.
- Total 90/90 with valid positive controls; no probe edited.

## Verification
All gates ran non-root under process-local umask 022 (host umask 0002
untouched); frozen installs; canonical repo `.venv` (Python 3.12.15,
uv 0.12.5).

| Command (exact) | Result |
| --- | --- |
| `uv run --frozen pytest -q tests/test_bundle_*.py` | PASSED — 404 passed (0.99s; 381 retained + 23 new; per-file: client_paths 38, compound_reads 108 (85 retained + 23 new), observation_models 23, observe 24, read_grammar 89, root_envelopes 32, shell_tokens 13, tool_results 77) |
| `uv run --frozen pytest -q tests/test_observation.py tests/test_dependency_acquisition.py tests/test_pipeline.py tests/test_app.py tests/test_image_policy.py tests/test_tool_policy.py tests/test_dev_provenance.py tests/test_source_input_binding.py` | PASSED — 267 passed (115.71s) at manifest B; at the pre-refresh implementation tree the same set ran 265 passed with exactly the two stale-manifest cases failing on the dirty source delta (expected A/B contract condition), and re-pass 45/45 in `tests/test_dev_provenance.py` + `tests/test_source_input_binding.py` after B |
| probes `check-bundle-observation.py` / `check-read-option-semantics.py` / `check-endpoint-selection.py` / `check-root-endpoint-context.py` / `check-finite-read-plans.py` (unchanged, `--head` = implementation head) | PASSED — 23/23, 16/16, 5/5, 6/6, 40/40 (90/90); valid positive controls; exit 0 |
| `uv lock --check` | PASSED (`uv.lock` unchanged this round) |
| `uv sync --frozen --extra dev` | PASSED (31 packages) |
| `uv run --frozen ruff check .` | PASSED |
| `uv run --frozen ruff format --check .` | PASSED (498 files already formatted) |
| `uv run --frozen mypy src tests` | PASSED (104 source files) |
| `uv run --frozen python scripts/docs_consistency_check.py` | PASSED (19 claim docs checked) |
| `uv run --frozen pytest -q` | PASSED — 1947 passed, 27 skipped, 0 failed (329.04s); the 27 skips are the standing explicit optional-fixture/live-layer skips, not passes |
| `uv build` | PASSED — wheel `a3cf191d102aa118b89cf0a6f3aa0c12987649dbff34d8c03e85af3b68546431` (122969 B), sdist `9f39ff55a40bb7bd2715d224357751d37ed2bff8f1bdb12d7819b799b6644ea6` (630957 B); digests equal the development manifest |
| `uv run --frozen python scripts/artifact_policy_check.py --dist dist --inspect` | PASSED (`ok: true`, no violations) |
| `uv run --frozen python scripts/artifact_policy_check.py --dist dist --install-smoke` | PASSED (`ok: true`, no violations) |
| `uv run --frozen python scripts/dev_provenance_manifest.py --verify --dist dist` | PASSED — `development provenance OK: state=development head=43e9c645de04` |
| `python -m compileall -q src tests oap/bin scripts` | PASSED |
| `bash -n` over `oap/bin/*.sh` + `packaging/readyz-wait.sh` | PASSED (4 scripts) |
| `git diff --check 75d7adb..HEAD` | PASSED |
| Targeted privacy/credential/raw-log scan over round-added lines | PASSED — 464 added lines; outside the strategic-authored order and `oap/active` (423 lines) zero matches for credential patterns, URLs, private host paths or protected-fixture references; this report contains hashes/counts/statuses only |
| Byte-identical normative mirror | PASSED — `cmp ARCHITECTURE-for-agents.md oap/strategic-instructions/ARCHITECTURE-for-agents.md` clean |
| Frozen/handoff/prior-OAP invariance | PASSED — `docs/CACHE-REWORK.md` SHA256 `410df5c0b8f90b05220adc32c8e673b143c0cf1fa3da02270d91ac453c886abd` unchanged; `packaging/` delta since round start = development manifest refresh only (no `packaging/releases/` change); prior 016/017 orders and reports unchanged; OAP transcript delta = 017-e order addition + `oap/active` (017-d -> 017-e) + the mandated byte-identical compact mirror; frozen RC10 binding re-proved by the manifest verification above |
| Independent clean `git archive` reproduction | PASSED — `git archive` of source commit A into a fresh 0700 temp root (mode verified), fresh venv (Python 3.12.15) + frozen sync + `uv build`: wheel/sdist SHA256 byte-identical to the development manifest digests; fresh non-editable install of the wheel in a second venv; `observe_request` smoke: (1) `echo '-n' && cat A.md B.md` over a `-n\n`-led source stays UNSUPPORTED, non-removable, no digest, no span, plan grammar; (2) `cat A.md && cat B.md` COMPLETE with `read_grammar == literal-read-plan/v1`; (3) single `cat A.md` COMPLETE with `read_grammar == literal-shell-read/v1`; no raw body/chunk-id in any output; temp root removed after |

## Live model/service evidence
NOT RUN. The order authorizes no live inference or API calls; no
Qwen/vLLM, qwen-serving, protected Codex profile, or network fixture
was touched.

## GitHub CI / required checks
Check suites at implementation head
`43e9c645de04b6eddb6a6af21145039265a157e0` (CI workflow run
39502474413 and CodeQL workflow run 39502466678) — all eight required
checks present and SUCCESS (observed before the report commit):
- `test` — SUCCESS
- `docker` — SUCCESS
- `docker-published` — SUCCESS
- `gateway-contract` — SUCCESS
- `operator-session` — SUCCESS
- `CodeQL` — SUCCESS
- `Analyze (python)` — SUCCESS
- `Analyze (actions)` — SUCCESS

All required green at drafting: yes. The report-only push may trigger
new checks at the report head; strategy verifies.

## Local setup/dependencies
- Host umask 0002; every gate above ran under process-local umask 022
  (verified context; no global/home chmod; no root; no sudo).
- Python 3.12.15 via repo `.venv` (uv 0.12.5, frozen lock); no new
  dependencies; `uv.lock` unchanged.
- Temp roots/files for protected work created 0700/0600 and removed
  after use (archive-repro root mode verified 0700; removed after).

## Documentation
- Observation contract, ledger, TESTING.md, both architecture maps and
  the byte-identical compact mirror updated in this PR (same-commit
  docs law); `ARCHITECTURE.md` stage sentence extended for 017-e;
  PR #25 description updated for the 017-e correction (verified
  byte-identical after `PATCH` via `gh api`, apart from one trailing
  newline).
- No cache/runtime capability claims added: modules remain inert and
  all v1 runtime criteria remain NOT RUN.

## Safety/scope confirmations
- Protected live-host boundary: NO change to qwen-serving, its units/
  venv/models, port 18020, API-key files, firewall/VPN/bindings, or
  existing Codex profiles.
- No live inference, no host Docker execution (remote disposable CI
  runners only), no gateway/image-policy/release change.
- No new dependencies; no model weights; no secret or raw customer
  content in any commit, report, or PR text (scan above).
- Activated order/`oap/active` bytes NOT edited after activation
  (committed unchanged in A); prior orders/reports/handoff/plan/
  frozen publication bytes unchanged; strategic probes NOT edited
  (hashes verified against `reviews/017-e-probe-hashes.json`).
- Observed commands were never executed to improve observation; no
  client/adapter filesystem access; the plan parser is data-only
  (no shell execution, no stat/resolve against the adapter host).
- Final commit changes only this report path with the implementation
  head as sole parent (verified below); no merge, no auto-merge, no
  second PR for objective 017.
- No loops, process chunks or new read families were added; no
  graph/RAM/recovery/compiler/tokenizer/app integration; the
  correction touches only the inert observation surface and its
  docs/manifest.

## Known limitations/blockers
- D09/D10 (literal loops, multi-chunk process pairing and the
  remaining truncation matrix) not implemented this round — planned
  for later same-PR suffixes: 017-f literal loops and 017-g
  process/chunk association (subject to strategic review; the
  earlier planned 017-e loops/chunks draft is superseded). Objective
  017 stays open until all D01-D10 are earned and independently
  reviewed. Literal loops and wildcards remain explicitly typed
  unsupported in this slice (`TestPlanNegatives`).
- The echo exclusion is deliberately conservative: any dash-leading
  cooked literal (including a lone `-`) is typed unsupported, even
  where a particular shell would print it; this is the ordered
  narrow correction and remains a limitation of the earned echo
  surface, not of the cat/cd law.
- All v1 runtime stages (018-024: graph/admission, RAM working state,
  recovery, tokenizer/compiler, source replacement, adversarial
  acceptance, real-model qualification): NOT RUN.
- 27 standing fixture/live-layer skips are reported as skips, never as
  passes; local results do not impersonate the (separately listed)
  GitHub checks.
- COMPLETE here is a claim for strategic review, never acceptance.

## Recommended strategic follow-up (factual, non-directive)
- Independently re-run the five unchanged probes at the report head
  (they pass 90/90 at the implementation head as evidenced above).
- Verify the report-head CI checks after this report-only push.
- If the 017-e slice is accepted as earned evidence for the echo
  option law and plan-grammar identity, the remaining objective-017
  scope is D09/D10 on the later same-PR suffixes (017-f literal loops
  and 017-g process/chunk association, per the current strategic
  planning).

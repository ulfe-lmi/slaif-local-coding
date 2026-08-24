# OAP Coding-Agent Report — 004-af

## Work order

- Identifier: `004-af`
- Order path: `oap/orders/004-af-durable-suffix-protocol-and-corrected-vision-rerun.md`
- Numeric objective: `004`
- PR mode: `AMENDED_EXISTING_PR`

## Status

FAILED

## Executive summary

The durable two-letter suffix protocol and narrow repository-only vision-marker
correction were implemented and pushed to PR #6. The single authorized live
vision acceptance attempt then failed at the first acceptance assertion:
`facts.successful` was false after 81.87 seconds. No retry, alternate prompt,
request-cap change, or protected-service operation was performed. The required
post-attempt tests/build and cleanup checks ran; local formatting/type gates and
the implementation-head CI check are also recorded as failed. Success-only
objective ledger/completeness updates were not made.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #6 — https://github.com/ulfe-lmi/slaif-local-coding/pull/6 — `OPEN`, non-draft.
- Base/head: `main` / `oap/004-real-codex-governed-e2e`.
- Starting remote SHA: `f93a43dd9b5cff59ee9cb6c73a5dcf0bcc4e1647`.
- Implementation head SHA: `bdaab40610ac612adf36ff8467f948bb076286b0`.
- Report publication commit: SELF.
- Implementation commits pushed before report: `bdaab40610ac612adf36ff8467f948bb076286b0`.
- New PR this round: no; amended existing PR: yes; merge performed: NO.
- Implementation-head GitHub check: `test` FAILED; Ruff format step failed and later CI steps were skipped.

## Changes and files

- Preserved and committed the exact activated `oap/active`, `004-af` order,
  and strategic control-plane edits for one/two lowercase suffix letters.
- Updated the stale contributor suffix statement so operative repository
  documentation agrees with `b..z`, then `aa..zz` continuation authority.
- Removed the two prompt-supplied vision processing markers, marker parsing,
  `image_marker_passed`, and marker success predicates from the repository-only
  vision runner.
- Retained ordinary dependency acquisition, hidden exact final-message binding,
  session binding, outbound image facts, phase bounds, metrics, cleanup, and
  privacy behavior.
- Added focused marker-free and marker-only/marker-plus-sentinel negative tests;
  updated the vision acceptance handoff to document exact outbound image
  identity/count and lifecycle evidence without a visual benchmark or prompt
  marker.
- No production adapter source, model, service, gateway, or protected fixture
  implementation was changed.

## Acceptance evidence

### Criterion 1 — durable suffix authority

- PASSED. Both repository OAP regex definitions accept `000-a`, `004-z`,
  `004-aa`, and `004-af`, and reject uppercase, numeric, empty, and three-letter
  suffix forms. Active selection found exactly one `004-af` order and zero
  matching reports before publication. No operative text forbids `aa`.

### Criterion 2 — narrow marker correction

- PASSED. The final non-live vision suite ran `13 passed, 1 skipped`; focused
  assertions prove both prompts and retained result facts contain neither
  processing marker, and marker-only plus marker-plus-hidden-sentinel output
  fails exact binding.

### Criterion 3 — exactly one corrected live acceptance attempt

- FAILED. The exact ordered command ran once:
  `SLAIF_VISION_ACCEPTANCE=1 uv run --frozen pytest -q tests/test_vision_e2e.py -k live_vision_exec_resume_acceptance`
  Result: `1 failed, 13 deselected in 81.87s`; first failure was
  `assert facts.successful`. No field-level predicate after that assertion is
  inferred or claimed.

## Verification

- `git fetch origin --prune`: PASSED — starting remote head reconciled to the
  order’s `f93a43dd9b5cff59ee9cb6c73a5dcf0bcc4e1647`.
- `uv run --frozen python ...` suffix grammar probe: PASSED — valid legacy and
  two-letter IDs accepted; malformed/uppercase/numeric/three-letter IDs rejected.
- `uv run --frozen python oap/bin/check_state.py ...`: PASSED — active valid,
  one matching order, zero report, both FIFOs identified.
- `uv run --frozen pytest -q tests/test_vision_e2e.py -k 'not live_vision_exec_resume_acceptance'`:
  PASSED — `13 passed, 1 deselected` before the live attempt.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen ruff format --check .`: FAILED — one reformat required in
  `tests/helpers/vision_e2e_support.py`; no post-failure code repair was made.
- `uv run --frozen mypy src tests`: FAILED — one `Literal[1, 2]` argument type
  error in the new marker-free prompt assertion; no post-failure code repair
  was made.
- `env -u SLAIF_VISION_ACCEPTANCE uv run --frozen pytest -q tests/test_vision_e2e.py`:
  PASSED — `13 passed, 1 skipped`.
- `env -u SLAIF_VISION_ACCEPTANCE uv run --frozen pytest -q`: PASSED —
  `321 passed, 8 skipped`.
- `uv run --frozen python -m build --no-isolation`: PASSED — wheel and sdist
  built. Wheel boundary inspection found 23 members, zero repository/test/OAP
  members, and zero model weights; sdist contained expected source-distribution
  material and zero model weights.
- `uv run --frozen python -m compileall -q src tests`: PASSED.
- `find . -type f -name '*.sh' ... bash -n`: PASSED.
- `git diff --check`: PASSED.
- Added-line sensitive-content scan for bearer values, data-URL payloads, and
  private-key blocks: PASSED — zero matches.

## Live model/service evidence

- Read-only preflight and post-attempt state: vision unit active, PID `364444`,
  zero restarts; text unit inactive; protected port `18020` listening.
- Protected `/health` and `/v1/models` calls returned HTTP 200 before and after;
  the model identifier was `qwen3.8-27b` with context `100000`.
- Port `18021` was not listening; candidate port `18031` was free after cleanup.
- The disposable candidate, fixture, cache, session, and temporary state were
  removed by the test context. No raw response, prompt, image, tool output,
  sentinel, session ID, credential, or private payload was retained.

## GitHub CI / required checks

- At implementation head `bdaab40610ac612adf36ff8467f948bb076286b0`, required
  check `test` was observed `FAILED`.
- CI steps: frozen sync and Ruff lint succeeded; Ruff format check failed;
  mypy, pytest, build, compileall, and shell checks were skipped by CI.
- All required green at drafting: no.
- Report-head checks may be pending or failed; strategy verifies them
  independently.

## Local setup/dependencies

- Used the existing repository-local frozen `uv` environment and disposable
  temporary test state. No dependency, systemd, service, model, key, profile,
  firewall, VPN, or network configuration was changed.

## Documentation

- Updated `docs/VISION-ACCEPTANCE.md` and `CONTRIBUTING.md` within scope.
- Did not update `docs/OBJECTIVE-004-LEDGER.md` or `oap/COMPLETENESS.md` because
  the order permits those success-only updates only after a full live pass.

## Safety/scope confirmations

- Unrelated pre-existing work was preserved; only the listed order-scope files
  were staged before the implementation commit.
- Secrets, raw prompts/source/images/tool output/bodies, credentials, and model
  weights were not committed or reported.
- Protected 18020/Qwen/Codex fixture changed: NO.
- Required live retries or additional real image calls: NO.
- Extra objective PR: NO; coding merge/auto-merge: NO.
- Active/order edited by coding: NO; exact strategic bytes were committed.
- Final report commit report-only: yes.

## Known limitations/blockers

- The live runner returned `facts.successful == false` at its first post-run
  assertion. Its direct output did not provide a safe field-level verdict for
  which component of that aggregate predicate failed; no deeper cause is
  claimed.
- The implementation head has one local formatting failure, one local typing
  failure, and a corresponding failed CI check. No corrective rerun was
  authorized after the first live failure.
- Objective 004 remains open at its pre-round success-only completeness state;
  this report is not acceptance, merge, release, or a visual-quality claim.

## Recommended strategic follow-up

- Strategy should independently review the aggregate live failure and the
  implementation-head static/CI failures before deciding whether a later
  same-PR continuation is warranted. No next suffix is selected here.

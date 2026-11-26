# OAP Coding-Agent Report — 022-g

## Work order
- Identifier: 022-g; order path `oap/orders/022-g-cache-final-envelope.md`; numeric objective 022
- PR mode: AMENDED_EXISTING_PR (PR #30, remote branch `oap/022-cache-source-replacement`)

## Status
COMPLETE

## Executive summary
The 022-g scope landed at the actual `create_app` entry point: (1) the v1
transaction now counts the ACTUAL emitted final payload (the final outgoing
body after the stable placement) — the ordinary-content view is derived from
the final payload by excluding the exact authenticated governance span only,
keeping the complete system frame and separators, the byte/token/item bounds
and the separate compiled aggregate, tool, image and generation reserves, with
actual-app first-over and in-bound controls at the accepted message limit
(exercising the newly inserted Responses instructions and the Chat system
frame); and (2) the placement-ownership matcher is the DETERMINISTIC
single-pass frame the F order explicitly required: the opening delimiter
directly carries the fixed-width claim (zero-padded body CHARACTER length plus
the closed canonical opaque under the distinct claim purpose of the placement
domain, same protected per-session key material), authenticated IN PLACE
before any body copy; the ONE closing position is located from the
authenticated length; every wire separator is verified as the actual newline
of the input and the exact body is verified by the existing placement-
ownership tag over the ACTUAL wire bytes; the total verification of admitted
candidate bodies is charged before the body copy at the conservative UTF-8
byte bound and closed by a cap derived from the configured whole framed-region
compiled-block byte limit plus the fixed framing skeleton; a field carrying
more than one legitimate frame's worth of admitted bodies is the fixed typed
over-bound transform refusal (never a silent no-ownership prepend, never a
raw forward); a valid frame may follow ordinary caller text, literal
delimiter-like caller text stays data preserved byte-identical, and the
legitimate transformed replay stays the byte-identical fixed point on both
endpoints. Scoped docs updated (both architecture maps with the byte-identical
mirror, the human-facing rework section at the 022-e through 022-g earned
scope, the stage ledger's B02/R03 states and the 022 objective row). The 023
negative-path/stress-test matrix and the 024 actual-model/client stages
remain unearned (NOT RUN).

## Authoritative GitHub state
- Repository: ulfe-lmi/slaif-local-coding; PR #30
  https://github.com/ulfe-lmi/slaif-local-coding/pull/30 — OPEN
- Base: `main` at `144af0bd5e34387afcb8e3f9ddf761eabd56e817` (order-verified)
- Starting remote SHA (verified report head F): `60b063b9ba1f4aff2bc34e56f34a5d811449d6c0`
- Implementation head SHA: 49f3e54a0e75f177d3b094d020864e757ab54aad
- Report publication commit: SELF
- Implementation commits pushed before report:
  - `6e5ba8c82503a804193a4ba530cd4044f1a33758` (source A: implementation, tests, docs, unchanged transcript)
  - `49f3e54a0e75f177d3b094d020864e757ab54aad` (B: development provenance manifest only, 316 inputs, toolchain 3.12.15 / uv 0.12.5)
- New PR this round: no; amended existing PR #30: yes; merge performed: NO

## Changes and files
- `src/slaif_local_coding/constitution/bundles/v1_application.py`
  - §1: `prepare_v1_transaction` counts
    `_strip_owned_region(final_payload, ...)` — the actual emitted payload
    (the final outgoing body after the stable placement) — so the ordinary-
    content view excludes the exact authenticated governance span only and
    keeps the complete system frame and separators; the byte/token/item
    bounds, the separate compiled aggregate, tool, image and generation
    reserves are unchanged.
  - §2: the deterministic placement frame. `_compiled_region` emits
    `[slaif-compiled-context:v1:` + 8-digit zero-padded body-CHAR length +
    `:` + 43-char closed canonical claim opaque (open line 79 chars) +
    newline + body + newline + 74-char tag line + newline + 28-char footer
    (skeleton 109 chars; body > 99,999,999 chars is the typed region-length
    shape error). The claim domain `slaif-placement-ownership/v1:claim` is a
    distinct purpose of the placement domain on the SAME protected per-session
    key material; the tag domain `slaif-placement-ownership/v1` is unchanged;
    no source digest on the wire. `_owned_region_span` is ONE left-to-right
    pass: claim shape (8 ASCII digits, colon, canonical opaque) → claim MAC
    authenticated IN PLACE (O(1), no body copy) → closing-shape validation
    with equality boundary rejections before indexing (`claim_end >= n`,
    `tag_end >= n`, `body_end >= n` all stay ordinary data) → every wire
    separator verified as the actual input newline (at `claim_end`,
    `body_end`, `tag_end`) → pre-copy charge `4 * (body_len + 109)` against
    the cap; exceeding it raises the distinct typed
    `_PlacementOwnershipWorkExhausted` → digest over the ACTUAL wire bytes
    (body line plus footer line) → existing tag compare. Unauthenticated
    claim/closing shapes cost no work, so any density of literal delimiter-
    like text stays ordinary data. `work_cap = _placement_work_cap(
    plan.config.max_compiled_block_bytes)` = `4 * (limit + 109)` at the
    transaction boundary (per the operator correction: `count_compiled_block`
    already checks the WHOLE framed region against the configured compiled-
    block byte limit, so the cap is that limit plus the fixed framing
    allowance — never multiplied per file, never the older carrier-
    observation constant).
- `tests/test_app.py` — four TestV1WireClosure controls:
  - `test_responses_emitted_envelope_message_limit_first_and_replay`
  - `test_chat_emitted_system_frame_message_limit_boundary`
  - `test_placement_scan_bounded_across_shape_valid_literal_frames`
  - `test_placement_verification_work_exhaustion_refuses_typed`
- Docs: `ARCHITECTURE-for-agents.md` (+ byte-identical mirror
  `oap/strategic-instructions/ARCHITECTURE-for-agents.md`), `ARCHITECTURE.md`
  (human-facing rework section), `docs/CACHE-REWORK-LEDGER.md` (B02, R03,
  022 objective row). `SECURITY.md` verified still accurate (same key
  material, separate MAC domain, content-free wire form) — unchanged.
- Transcript: `oap/active` and `oap/orders/022-g-cache-final-envelope.md`
  committed byte-identical (order sha256 `c685a6d6…ff822`, active sha256
  `5f3582d3…40a3`); `packaging/dev_provenance_manifest.json` regenerated at B.

## Acceptance evidence
### Criterion 1 — count the emitted request envelope
- The order's bounded normal FastAPI/fake-upstream fixture set
  `max_messages=1`; its first request (one legitimate root-bearing Responses
  message, no `instructions`) returns 200 and forwards one user message plus
  the generated system instructions; replaying the exact emitted body returns
  the fixed 422 — the old count saw the source-replaced intermediate before
  the system frame/separators existed.
- Result: PASSED. `test_responses_emitted_envelope_message_limit_first_and_
  replay` (Responses: first-over at the accepted limit → fixed 422; the in-
  bound case emits and the exact emitted body replays byte-identically) and
  `test_chat_emitted_system_frame_message_limit_boundary` (Chat: one user
  message emits two frames at the limit; the second user message → fixed
  422) prove equal first/replay disposition and byte-stable output at the
  accepted message limit, exercising the newly inserted Responses
  instructions and the Chat system frame. The accepted whole optional
  omission replay and the v1 failure/status behavior stay green in the same
  focused set.
### Criterion 2 — bounded deterministic placement framing
- The F matcher's header-loop rescan of tag candidates (repeated
  overlapping-range reconstruction/hash) is replaced by the deterministic
  non-overlapping frame: one fixed-width claim per candidate, authenticated
  in place before any body copy; the closing position located from the
  authenticated length; the total verification of admitted candidate bodies
  charged before the body copy and closed by the cap derived from the
  configured compiled-render budget.
- Result: PASSED. `test_placement_scan_bounded_across_shape_valid_literal_
  frames` (a shape-valid unauthenticated fake frame — correct fixed width,
  non-canonical opaque — costs no verification work and never hides a later
  authentic frame; byte-identical replay, unchanged compile count) and
  `test_placement_verification_work_exhaustion_refuses_typed` (with a small
  configured compiled-block limit, a field carrying more admitted-body
  frames than the cap allows is the fixed typed 422
  `v1_transaction_over_bound` "governed v1 request refused" — zero main
  forward and zero compile; the single-frame-in-bound case verifies
  byte-identical). The same protected key and independent MAC domain are
  retained; the authenticated placement and the tested no-data-loss behavior
  (caller literal text, embedded literal delimiters, suffix separators,
  current region replacement, legitimate fixed-point replay) all stay green.

## Verification
- `umask 022; uv run --frozen pytest -q tests/test_app.py tests/test_v1_application.py tests/test_bundle_replace.py tests/test_bundle_tokenizer.py tests/test_bundle_budget.py tests/test_bundle_selection.py tests/test_config.py tests/test_cache.py tests/test_injection.py tests/test_compiler.py tests/test_rehydration.py tests/test_pipeline.py tests/test_dependency_acquisition.py tests/test_image_policy.py`: PASSED — 518 passed (Python 3.12.15, real exit 0; recorded before and after the doc edits)
- `uv run --frozen ruff check .` / `ruff format --check .`: PASSED
- `uv run --frozen mypy src tests`: PASSED — 205 files, no issues
- `uv run --frozen python scripts/docs_consistency_check.py`: PASSED — 19 claim docs (after all doc edits)
- 15-command locked gate at exact B: PASSED — all fifteen commands rc=0 at `49f3e54a0e75f177d3b094d020864e757ab54aad` (managed foreground driver, run directory `oap-022g-work/gate-run1`, startup pid/birth/ppid/uid/umask/source-sha256/head/parent recorded): `uv lock --check`; `uv sync --frozen --extra dev`; `ruff check .`; `ruff format --check .`; `mypy src tests`; `docs_consistency_check.py`; `umask 022; uv run --frozen pytest -q` (full suite: **7150 passed, 28 skipped, 0 failed** in 1581.05 s, real exit 0, ordinary short OS fixture scratch under /tmp, capacity and inodes verified and recorded before start); `uv build`; `artifact_policy_check.py --dist dist --inspect`; `--install-smoke`; `python --version` (Python 3.12.15); `compileall`; `dev_provenance_manifest.py --verify --dist dist`; shell `bash -n` passes; `git diff --check <main baseline> HEAD`
- GitHub checks at exact B (10 named): all `completed success` — CodeQL, Analyze (actions), Analyze (python), gateway-contract, docker, docker-published, operator-session, cache-native-containment, cache-native-fixture, test (raw JSON captured at `oap-022g-work/checks-final-022g.json`)

## Live model/service evidence
- No live model/service calls this round (order: no live service/inference,
  no profile/credential, network, Gateway, deploy, registry, cutover or
  benchmark changes). All v1 evidence is bounded fake-upstream application
  scope. Protected 18020/Qwen/Codex fixture changed: NO.

## GitHub CI / required checks
- Implementation-head (49f3e54a0e75f177d3b094d020864e757ab54aad) check state at drafting: ten named checks all `completed success` — CodeQL, Analyze (actions), Analyze (python), gateway-contract, docker, docker-published, operator-session, cache-native-containment, cache-native-fixture, test
- All required green at drafting: yes (10/10 success)
- Report-head checks may be pending; strategy verifies.

## Local setup/dependencies
- Execution in the order-designated LINKED CHECKOUT
  `/home/janezp/codex-supervision/slaif-local-coding/work-artifacts/
  oap-022g-work/checkout` (detached at verified report head F; primary
  checkout untouched, operator unstaged edits preserved).
- Repo venv rebuilt onto the pinned Python 3.12.15 before the gate (the
  pre-rebuild venv carried a non-pinned 3.14.7 interpreter; the development-
  provenance toolchain pin refused it — see process qualifications).
- No sudo, no new services, no registry/deploy/registry mutation. Durable
  captures and artifacts under the project work-artifact directory (0700/0600).

## Documentation
- Updated: both architecture maps (022-g item in both lineage blocks, byte-
  identical mirror), human-facing `ARCHITECTURE.md` rework section (heading,
  delivery status, scope sentence, detailed 022-e/f/g lineage, "only active
  mechanism" line — 023/024 kept unearned), `docs/CACHE-REWORK-LEDGER.md`
  (B02/R03 states and the 022 objective row at the 022-g earned scope only).
  `SECURITY.md` verified accurate, unchanged. Prior orders/reports and RC10
  untouched; no new planning or audit documents.

## Safety/scope confirmations
- Unrelated files: only the order scope plus the ordered doc updates;
  `AGENTS.md` operator wording edits kept UNSTAGED throughout.
- Secrets/raw content: none in any transcript, capture or report; test
  fixtures are synthetic (test marker key is a synthetic 32-byte constant).
- Protected 18020/Qwen/Codex fixture changed: NO. No additional Codex or
  model-client startup. No live inference/service/profile/credential/
  network/Gateway/deploy/registry/cutover/benchmark changes.
- Required tests skipped/not run: none in the focused set; the 023
  negative-path/stress-test matrix and 024 actual-model/client stages remain
  NOT RUN (separate stages).
- Extra objective PR: NO; coding merge: NO.
- Active/order edited: NO (committed byte-identical). Report commit
  report-only: yes.

## Known limitations/blockers
- Bounded FAKE-UPSTREAM application scope only (synthetic identity and
  fixture sources on the real app entry point); the 023 expanded negative-
  path/stress-test matrix and the 024 actual-model/genuine-Codex stages are
  the mandatory unearned v1 implementation stages (NOT RUN).
- The unreleased F wire layout made the frame format change in-scope; no
  migration or old-format acceptance exists.

## Process qualifications
- Full governance refresh (AGENTS.md, coding protocol, the complete compact
  architecture in bounded chunks, SECURITY.md, TESTING.md, exact 022-g
  order) was re-read in this process after the native context compaction at
  23:15 UTC, in the required order, before further source edits; the earlier
  in-round governance reads (after the 22:39 UTC compaction) remain process
  qualifications of this round's prior verified steps.
- Operator in-round §2 design refinements applied in-round: the deterministic
  frame (fixed-width claim, in-place claim authentication, closing position
  from the authenticated length, actual-newline wire-separator verification,
  actual-wire-byte tag digest); the pre-copy conservative UTF-8 charge after
  the fixed-size claim and closing-shape validation; the equality boundary
  rejections before indexing; the cap derived from the configured whole
  framed-region compiled-block byte limit (per the operator correction — not
  a per-file multiplication, not the 100,000-character carrier-observation
  constant).
- The linked-checkout venv was found carrying a non-pinned 3.14.7
  interpreter; the development-provenance toolchain pin (3.12.x) refused the
  manifest generation, the venv was rebuilt on the pinned 3.12.15, and the
  focused 518-test set was re-verified under 3.12.15 (518 passed, real exit
  0) before the manifest commit and the gate. The pre-rebuild focused runs
  are not claimed as 3.12 evidence.

## Recommended strategic follow-up
Factual only; strategy decides: the 023 negative-path/stress-test matrix and
the 024 actual-model/client stages remain the mandatory unearned v1
implementation stages; all 022-a through 022-g slices are PENDING strategic
review at their stated scopes.

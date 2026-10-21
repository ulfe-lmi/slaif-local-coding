# OAP Coding-Agent Report — 017-k

## Work order
- Identifier: 017-k; order path: `oap/orders/017-k-issued-selection-and-finalization.md`; numeric objective: 017
- PR mode: AMEND_EXISTING_PR (PR #25, branch `oap/017-cache-read-observation`, base `main`)
- Activation: `oap/active` = `017-k` (unique matching order); control FIFO `OK` consumed once by the wrapper before this round; not read again.

## Status
COMPLETE

## Executive summary
The four remaining ownership/finalization/accounting/fidelity defects in the
offline capture utility were repaired exactly as ordered, on top of the 017-j
head. (1) RUNTIME frame selection is now bound to the controller's ACTUAL
issued records created before each provider request (a preloaded,
anticipated, or forged call is never selected before the controller issues
it; the pure-facade candidate parsing is a distinct fixture mode, and a
constructor or manually populated state is not runtime provenance evidence).
(2) Finalization quiesces the owned provider BEFORE final
validation/publication (freeze, stop accepting, close the listening socket,
bounded handler join with honest teardown reporting) and validates/
serializes the explicit frozen frame snapshot, so a real late request at the
shutdown boundary is byte-verified and stripped to `content_unverified` with
its marker bytes reaching no persisted record. (3) EVERY HTTP method and
error-dispatch path (unsupported methods, malformed request lines,
unsupported versions) consumes the per-run budget through the
BaseHTTPRequestHandler error-dispatch fallback with fixed sanitized
non-echoing bodies, and accepted handler concurrency is bounded (hard cap 4)
with rejected over-cap connections counted. (4) Generated readiness records
round-trip the validated live-facts flag count faithfully for zero and every
nonzero known flag (the `tuple("") * count` placeholder is gone), and ACTUAL
malformed Unicode (lone surrogates) is rejected with the fixed typed
`malformed_unicode` reason before any encoding/hashing/retention, with the
raw value stored nowhere and no lossy replacement. Public
receiver/run/lifecycle regressions were added for every repaired boundary.
During verification the frozen `check-real-client-capture-v2.py` probe
exposed one in-scope regression (the 017-j public `build_selection` call
form); it was restored as an explicit pure-facade control (the runtime
path always passes the frozen snapshot) and the round commits were
restructured before report publication (disclosed under Verification). The
utility remains inert; no actual client, provider session, or model call was
made; no format or process acquisition was earned; D09/D10 remain NOT RUN.
All FOURTEEN frozen probes pass at the implementation head; the full local
gate and all eight implementation CI checks are green.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`; PR #25
  https://github.com/ulfe-lmi/slaif-local-coding/pull/25 — state OPEN,
  mergeable, not draft; base `main`
- Base `main` (`96c790423f6f0097a56a0b12bacda8a9b6da6aba`) unchanged
- Head branch `oap/017-cache-read-observation`
- Starting remote head (round start, verified by fetch + PR API):
  `e4b6c184568257e9bba025a7c4ba9c34a7abb831` (017-j report)
- Implementation head SHA: bed32f26ba7c456605562580793ae282f8001124
- Report publication commit: SELF
- Implementation commits (final branch shape; prior-round history intact):
  - `c0db839d0d7cf177484db43563a9fb89c8554a8b` — 017-k implementation/tests/
    docs + exact unchanged activated order and `oap/active` (source A)
  - `bed32f26ba7c456605562580793ae282f8001124` — development provenance
    manifest bound to source A (manifest B; = implementation head)
- New PR this round: NO; amended existing PR #25: YES; merge performed: NO

## Changes and files
Round diff `e4b6c184568257e9bba025a7c4ba9c34a7abb831..bed32f26ba7c456605562580793ae282f8001124`
(11 files, +1542/-144):

- `scripts/real_client_capture.py`:
  - RUNTIME issued-registry binding: `handle_responses_post` captures the
    controller's actual `_issued` records under the state lock BEFORE each
    provider request and passes them as `extract_frames(issued=...)`;
    only those (call ID, step position) pairs prove issuance. A preloaded,
    anticipated, or forged call is rejected `call_id_unissued` (raw values
    stored nowhere); issuance/completion is never inferred from a caller's
    predicted ID or forged earlier status at runtime. `extract_frames`
    keeps a distinct PURE-facade mode (`issued is None`: declared-step ID
    inference plus progression from the request's own completed outputs)
    for the offline fixture controls; a constructor or manually populated
    ProviderState is not runtime provenance evidence. The item family must
    match the actually offered tool schema (wrong family is typed
    `input_shape_unsupported`); valid echoed histories keep their
    occurrence order.
  - Finalization quiesce: `FakeProvider.stop()` freezes the frame state
    first (the append path rechecks the gate under the state lock, so no
    further append can happen), stops the accept loop, closes the
    listening socket, joins the serve thread, then joins in-flight handler
    work under a bounded grace (10 s) and reports `teardown_incomplete`
    honestly when a handler outlives it. Post-freeze requests are rejected
    with a fixed sanitized 503 and counted (`post_freeze_rejected`).
    `run_capture` reorders finalization: child exit → `provider.stop()` →
    `frame_snapshot()` (explicit frozen list copy) →
    `_verify_selected_content(...)` on the snapshot →
    `build_selection(frames=snapshot, ...)` → serialize once → publish the
    same bytes. Every exported text is byte-verified in the FINAL frozen
    snapshot; serialization cannot pick up a later unverified append.
  - All-method accounting: `_SilentRequestHandler.send_error` override
    consumes the per-run budget exactly once on EVERY error-dispatch path
    (unsupported methods, malformed request lines, overlong lines,
    unsupported versions) and sends a fixed sanitized body (`b"error\n"`)
    with no request-line/method echo. `do_GET`/`do_POST` keep their
    centralized pre-branch accounting; authentication failures remain
    value-free. `_OwnedThreadingHTTPServer` (ThreadingHTTPServer subclass)
    tracks handler threads, caps concurrent handlers at
    `HARD_MAX_CONCURRENT_HANDLERS = 4` (over-cap accepted connections are
    closed without a response and counted `rejected_connections`), and
    counts handler exceptions silently (no traceback echo).
  - Readiness fidelity: `load_readiness_record` reconstructs
    `detected_flags` from the validated live preflight facts
    (`count == len(facts.detected_flags)` enforced), replacing the
    `tuple("") * count` placeholder that always exported count 0 after
    loading; the record stays metadata-only (count, never flag text), the
    generated verdict stays `not_ready`, and a literal `ready` record is
    caller input, not verification.
  - Malformed Unicode: `_strict_utf8` validates strings before any
    encoding/hashing/retention on the function/custom output, custom
    input, function-argument, and relevant metadata paths; failure is the
    fixed typed `malformed_unicode` reason (added to `REJECTION_REASONS`),
    the raw value is stored nowhere (no echo in exceptions, reprs,
    digests, or records), and no lossy replacement masquerades as
    fidelity. Valid non-ASCII Unicode is processed normally. The canary
    bytes are computed safely for a malformed canary.
  - `build_selection` keeps the 017-j public call form: `frames` is an
    explicit frozen-snapshot parameter the runtime finalization path
    (run_capture) always passes; the omitted-snapshot form is the
    pure-facade fixture control over a caller-owned static frame state
    (no live receiver, no late-append surface).
  - `ProviderState` gains `frozen`, `post_freeze_rejected`,
    `rejected_connections`, `teardown_incomplete`; `_provider_summary`
    reports them in the run record. The module docstring records the
    017-k hard law.
- `tests/test_real_client_capture.py`: new public receiver/run/lifecycle
  suites — `TestIssuedRegistryRuntime` (4: preloaded first/later IDs and
  forged inbound progression never selected before issuance through
  embedded-mode fake children; actual-issued receiver control),
  `TestWrongFamilyUnderOfferedSchema` (3), `TestFinalizationQuiesce` (5:
  normal finalization control; a REAL late HTTP request injected at the
  public shutdown boundary — processed pre-freeze, byte-verified and
  stripped to `content_unverified`, marker bytes nowhere under the output
  directory; frozen-append rejection with a final snapshot; bounded stop
  under a stalled in-flight handler; the pure-facade `build_selection`
  control agreeing with the explicit-snapshot form),
  `TestMethodAccounting` (5: HEAD/FOO/malformed-line budget consumption
  under a lowered 2-request budget, fixed non-echoing bodies, bounded
  handler concurrency with a surviving server),
  `TestReadinessMetadataFidelity` (4: zero/one/multiple-flag round-trips,
  no flag-text export), `TestMalformedUnicodeStrict` (5: ACTUAL lone
  surrogates in function/custom output/input and at run level with a
  real child, non-echoing, plus a valid-Unicode control). Existing suites
  updated where the repaired surfaces changed (custom-mode family check,
  actual-surrogate argument test, input-gated module wording).
- `docs/CACHE-OBSERVATION-CONTRACT.md`: section 11 017-k paragraph (the
  017-i "unreachable by construction" wording explicitly marked a REJECTED
  historical claim); section 12 retitled for 017-i/017-j/017-k with the
  repaired hard limits (all-method budget, bounded handler work,
  finalization quiesce), the privacy law (runtime vs pure-facade
  issued-binding, malformed-Unicode law), the accurate 017-k readiness
  round-trip fidelity sentence, and the 017-k regression paragraph.
- `docs/CACHE-REWORK-LEDGER.md`: 017-k stage paragraph; D09/D10 row notes;
  the 017-i rejected-claim note; planned-succession 017 row updated.
- `TESTING.md`: the 017-i "unreachable in this round by construction"
  wording explicitly marked a REJECTED historical claim superseded by
  017-j; 017-k paragraph with the new suites and the skip accounting
  (27 prior stage skips + exactly one 017-i foreign-ownership `chown`
  environment skip; simulated-UID and new 017-k lifecycle proofs are
  passing tests, never skips).
- `ARCHITECTURE.md` + `ARCHITECTURE-for-agents.md`: 017-k stage sentence
  appended to the objective-017 prose; compact mirror
  `oap/strategic-instructions/ARCHITECTURE-for-agents.md` re-copied
  byte-identical (`cmp` clean).
- `oap/orders/017-k-issued-selection-and-finalization.md` + `oap/active`:
  committed exactly as activated (byte-unchanged; verified by the round
  diff).
- `packaging/dev_provenance_manifest.json` (manifest B commit only):
  bound to source A `c0db839d0d7cf177484db43563a9fb89c8554a8b`; 186 source
  inputs; wheel `99e5ad582232c5a2e9e717c7707162b8c57261983aa0cf472e0c4e0d9263ac71`
  (byte-identical to the 017-j wheel: `src/` unchanged this round); sdist
  `7228b67fc5d5ca4aeec8d99a631164e5d93c74b051d184cca8420e1d93ec0c08`
  (test file ships in the sdist).

## Acceptance evidence
### Area 1 — runtime selection bound to controller-actual issued records
- `check-capture-issued-registry.py` at the implementation head: 2/2 PASS
  (previously 1/2 at the 017-j head) —
  `preloaded_call_before_controller_issue_is_not_selected` and
  `actual_issued_receiver_control`, `positive_control_valid: true`.
- `TestIssuedRegistryRuntime` (4 tests): preloaded first/later IDs and
  forged inbound progression are unselected (`call_id_unissued` counts
  exact), the actually-issued echo is selected and byte-verified against
  the owned workspace, and a constructor-populated state is not runtime
  evidence. No special-casing of test IDs/markers; `procNN` values are
  synthetic fixture protocol fields, not native process evidence.
### Area 2 — quiesce before final validation/publication
- `check-capture-finalization-v3.py` at the implementation head: 8/8 PASS
  (previously 4/8 at the 017-j head) — including
  `request_at_shutdown_never_persists_unverified_text` (a REAL late HTTP
  request to the still-owned receiver at the public shutdown boundary is
  processed pre-freeze, byte-verified and stripped:
  `content_unverified == 1`, marker bytes absent from every json under the
  output directory) and `unsupported_method_consumes_request_budget`.
- `TestFinalizationQuiesce` (5 tests): normal finalization control
  (`frozen: true` in the run record); shutdown-boundary late injection;
  frozen-append rejection (503, `post_freeze_rejected == 1`, snapshot
  final and unchanged); bounded stop under a stalled in-flight handler
  (`teardown_incomplete: false`, frames empty); pure-facade
  `build_selection` control.
### Area 3 — all-method / error-path accounting + bounded handlers
- `check-capture-finalization-v3.py` 8/8 includes
  `unsupported_method_consumes_request_budget`.
- `TestMethodAccounting` (5 tests) under a lowered 2-request budget: three
  HEADs → 501/501/429 with `request_count == 3` and
  `request_limit_hit`; arbitrary `FOO`/`BREW` methods → 501 with the fixed
  `b"error\n"` body and no method echo; two malformed request lines plus
  one GET → 429 on the third with no echo of the garbage; four stalled
  handlers + a fifth connection rejected without a response
  (`rejected_connections >= 1`) with the server still serving afterwards.
  The GET control (two-request budget, third rejected) is preserved.
### Area 4 — metadata fidelity + real malformed Unicode
- `check-capture-finalization-v3.py` 8/8 includes
  `nonempty_flags_readiness_roundtrip` and
  `malformed_unicode_is_typed_and_non_echoing` (previously both FAILED at
  the 017-j head).
- `TestReadinessMetadataFidelity` (4 tests): generated zero/one/three-flag
  records round-trip byte-for-byte at the metadata level with the
  validated live-facts/count binding, the verdict stays `not_ready`, and
  no flag text is ever exported.
- `TestMalformedUnicodeStrict` (5 tests): ACTUAL lone-surrogate values
  (JSON `\ud800` escapes) in function output content, plain-string
  output, custom-tool input, and a run-level child that posts a real
  surrogate payload — each rejected `malformed_unicode` with the marker
  bytes absent from every persisted record and from all exported JSON —
  plus the valid `\u00e9` control processed normally (input immutability
  asserted throughout).

## Verification
Test context: non-root user `janezp`, repo `.venv` (uv-managed CPython
3.12.15, `uv sync --frozen --extra dev`), process-local `umask 022` for the
entire gate (0002 would make the security fixtures group-writable; 077
would mask the intentional 0755 untrusted-cache fixture); protected temp
roots created 0700/files 0600 under an owned directory; no root used.

Commit-history note (disclosure): before the final structure was reached,
two intermediate 017-k implementation commits
(`882fdc48f80482b5bf0d95d9368efa3896d02d2e` /
`ebe454cb4a40ca6237f6fe0f63e4565bd3abcaa5`) were pushed to the objective
branch. Running the 14 frozen probes at that intermediate head exposed one
in-scope regression — the frozen `check-real-client-capture-v2.py`
check `selected_synthetic_result_text_survives_for_format_fixture`
(TypeError) — because the 017-j public `build_selection` call form had
lost its omitted-snapshot form. The fix (explicit `frames` snapshot
parameter with the 017-j call form preserved as the pure-facade control,
plus a regression test) was committed and the branch was restructured
(force-with-lease, expected remote head verified) to the final shape
source A `c0db839...` → manifest B `bed32f2...`, with the full gate, all
14 probes, and CI re-run at the final head. No prior-round commit (
`e4b6c184568257e9bba025a7c4ba9c34a7abb831` or earlier) was touched.

- `uv lock --check`: PASSED (36 packages resolved, no changes).
- `uv sync --frozen --extra dev`: PASSED (31 packages checked).
- `uv run --frozen ruff check .`: PASSED (all checks passed).
- `uv run --frozen ruff format --check .`: PASSED (515 files already
  formatted).
- `uv run --frozen mypy src tests`: PASSED (no issues in 107 source
  files).
- `uv run --frozen python scripts/docs_consistency_check.py`: PASSED
  (19 claim docs checked).
- `uv run --frozen pytest -q` (full suite, umask 022): PASSED — 2225
  passed, 28 skipped (27 prior stage skips + 1 explicit 017-i
  foreign-ownership `chown` environment skip), 0 failed, 372 s.
- Focused `tests/test_real_client_capture.py` (umask 022): PASSED — 183
  passed, 1 skipped, 0 failed.
- `uv build`: PASSED — wheel
  `99e5ad582232c5a2e9e717c7707162b8c57261983aa0cf472e0c4e0d9263ac71`,
  sdist `7228b67fc5d5ca4aeec8d99a631164e5d93c74b051d184cca8420e1d93ec0c08`
  (deterministic: rebuilt at the final head and again in the clean
  archive tree, byte-identical).
- `scripts/artifact_policy_check.py --dist dist --inspect`: PASSED (ok,
  no violations; wheel 37 entries / 31 package files, sdist 184 entries).
- `scripts/artifact_policy_check.py --dist dist --install-smoke`: PASSED
  (entrypoint help/version 0, version 0.1.0, installed from the built
  wheel in a throwaway venv).
- `scripts/dev_provenance_manifest.py --verify --dist dist`: PASSED —
  `development provenance OK: state=development head=bed32f26ba7c`;
  source bound to `c0db839d0d7c`, 186 inputs, lock hash bound, frozen RC10
  publication baseline intact.
- `python -m compileall -q src tests oap/bin scripts`: PASSED.
- `bash -n` over `oap/bin/bootstrap-two-codex-oap.sh`,
  `oap/bin/launch-coding-agent.sh`, `oap/bin/launch-strategic-agent.sh`,
  `packaging/readyz-wait.sh`: PASSED (all parse).
- `git diff --check`: PASSED (clean).
- Targeted credential/raw-log/privacy scan of the round diff: PASSED — no
  real key/token/bearer patterns, no private URLs/hosts/protected service
  addresses in new code (only the synthetic in-test tokens
  `tok`/`wrong`), no raw customer content; the only literal content in
  the tests is synthetic fixture text asserted absent from all persisted
  records.
- Invariance: PASSED — `docs/CACHE-REWORK.md` SHA256
  `410df5c0b8f90b05220adc32c8e673b143c0cf1fa3da02270d91ac453c886abd`
  preserved; `docs/RC-HANDOFF.md` and `docs/CACHE-IMPLEMENTATION-PLAN.md`
  untouched by the round diff; all prior `oap/orders/*` and
  `oap/reports/*` byte-unchanged (round diff touches only the 11 listed
  files); frozen 29 publication baseline re-proved by
  `tests/test_dev_provenance.py::test_real_frozen_publication_baseline_holds`
  (passed, inside the 2225); compact mirror `cmp` byte-identical;
  `packaging/releases/` untouched (frozen binding re-proved by the
  manifest verification).
- Clean `git archive` source-A (`c0db839d0d7cf177484db43563a9fb89c8554a8b`)
  reproduction in an owned 0700 temp root: PASSED — utility
  `scripts/real_client_capture.py`, fake child
  `scripts/real_client_capture_fake_child.py`, and
  `tests/test_real_client_capture.py` present in the clean tree;
  `uv sync --frozen --extra dev` + `uv build` from the clean tree
  reproduced byte-identical artifacts (wheel `99e5ad582232...`, sdist
  `7228b67fc5d5...` — equal to the manifest digests).
- Fresh-wheel observer FUNCTIONAL controls: PASSED — fresh Python 3.12
  venv in the protected temp root; wheel installed non-editable
  (`uv pip install --no-cache-dir`); package path
  `.../venv312/lib/python3.12/site-packages/slaif_local_coding/__init__.py`
  (proves the installed wheel is used outside the repository), version
  0.1.0; wheel ships no capture utility/fixtures (37 entries, no
  `scripts/`/test entries — source-input policy). The 11 functional
  controls recorded in 017-g were re-exercised with actual
  positive/negative behavior assertions (not import smoke): the four
  quoted-prefix/suffix defect forms typed `QUOTED_OPERAND`
  non-removable with no digest/span/members at composition (parser and
  public composition agree; no phantom `A`/`.md` members) plus the
  first-position variant; whole-word double- and single-quoted controls
  and the plain controls earned with exact members; the complete guarded
  ordered bundle with exact digest/slot width/exact content span; the
  unguarded human form typed with preserved requested members and no
  digest (non-removable); and repr privacy (no raw command literal in any
  repr) — 11/11 PASS.
- Fourteen frozen strategic probes (canonical `REPO/.venv/bin/python`,
  each `--head bed32f26ba7c456605562580793ae282f8001124`; script SHA256s
  verified against `reviews/017-k-probe-hashes.json` before running — all
  14 match; scripts unmodified; result JSON written to an owned 0700 temp
  root, not the strategic workspace): ALL PASSED with
  `positive_control_valid: true` and `all_checks_passed: true`:
  - `check-bundle-observation.py`: 23/23 checks.
  - `check-read-option-semantics.py`: 16/16 checks.
  - `check-endpoint-selection.py`: 5/5 checks.
  - `check-root-endpoint-context.py`: 6/6 checks.
  - `check-finite-read-plans.py`: 40/40 checks.
  - `check-literal-loops.py`: 63/63 checks.
  - `check-loop-word-boundaries.py`: 10/10 checks (162 word variants).
  - `check-real-client-capture-v2.py`: 12/12 checks.
  - `check-capture-file-boundaries.py`: 3/3 checks.
  - `check-capture-selection-boundaries.py`: 2/2 checks.
  - `check-capture-resource-boundaries.py`: 4 checks + 1 memory
    measurement.
  - `check-capture-process-boundaries.py`: 2/2 checks.
  - `check-capture-issued-registry.py`: 2/2 checks (the 017-k added
    probe; 1/2 at the 017-j head).
  - `check-capture-finalization-v3.py`: 8/8 checks (the 017-k added
    probe; 4/8 at the 017-j head).
  (33 utility checks total; the memory measurement is not an extra test;
  the older `check-capture-finalization-boundaries.py` /
  `check-capture-finalization-v2.py` are historical, not mandatory.)

## Live model/service evidence
- Not applicable this round: no live inference, no bounded live calls, no
  service inspection, no real Codex session — the order authorizes none.
  The protected fixtures (qwen-serving, vLLM 18020, API-key files,
  firewall/VPN, active Codex profiles) are unchanged. All evidence is
  offline synthetic (fake Python children, seeded workspace files, owned
  ephemeral loopback HTTP on bind-0 ports).

## GitHub CI / required checks
- All 8 required checks SUCCESS at the implementation head
  `bed32f26ba7c456605562580793ae282f8001124` (workflow run
  `39548346471`): `test` (4m49s), `docker` (1m42s), `docker-published`
  (1m14s), `gateway-contract` (14s), `operator-session` (56s), `CodeQL`
  (3s), `Analyze (python)` (1m3s), `Analyze (actions)` (43s).
- CI state was re-verified after the final push; no failed job logs were
  needed (no failures).

## Local setup/dependencies
- Non-root user `janezp`; repository-owned `.venv` (uv-managed CPython
  3.12.15); all installs `--frozen` against the committed `uv.lock`
  (no new dependencies this round).
- Process-local `umask 022` for the full test gate (recorded above);
  probe/wheel/archive temp work in an owned 0700 directory
  (`/home/janezp/tmp/017k`, results subdirs 0700, control script 0600),
  outside the strategic workspace.
- No Docker, no namespace/tracing experiments, no network services beyond
  the owned ephemeral loopback provider (bind 0, never 18020/18031) used
  by the offline suites.

## Documentation
- `docs/CACHE-OBSERVATION-CONTRACT.md` (sections 11/12: 017-k stage and
  repaired law; rejected historical claim marked),
  `docs/CACHE-REWORK-LEDGER.md` (017-k paragraph, D09/D10 row notes,
  planned-succession row), `TESTING.md` (rejected historical claim
  marked; 017-k suites and skip accounting), `ARCHITECTURE.md` and
  `ARCHITECTURE-for-agents.md` (objective-017 017-k stage sentence) with
  the byte-identical compact mirror. The PR #25 body was updated with
  the 017-j/017-k round entries and the 017-k evidence block. No
  immutable prior order/report was edited.

## Safety/scope confirmations
- No merge, no auto-merge, no acceptance, no next-order choice; single
  PR #25 for objective 017 (no second PR); activated order/active bytes
  committed unchanged; no edit of prior round artifacts.
- No genuine installed-client session/capture/debug-models; no actual
  model/GPU/product API/Gateway call; no host Docker; no
  namespace/tracing experiment; no new dependency; no benchmark/RC/tag/
  registry/release/deployment/cutover.
- No observer grammar/graph/RAM/recovery/tokenizer/compiler/image/
  request-pipeline changes; the utility stays `fixture_authority: none`
  and inert (nothing in the adapter runtime imports it); the legacy
  detector is unchanged.
- No mutation of protected Qwen/vLLM 18020/qwen-serving/models/venvs/
  patches/flags/systemd/API-key files, active protected Codex
  profiles/auth/config, firewall/VPN/host network. Original H raw
  captures were not read or recreated.
- No secrets or raw customer content committed, printed, or logged;
  diagnostics remain fixed enums/counts/digests; synthetic-only
  fixture data is labeled as such.
- Actual format/process collector (D09/D10) and all v1 runtime
  qualification remain NOT RUN; no broad architecture/security exception
  was introduced.

## Known limitations/blockers
- The utility is a synthetic offline review surface only: it earns no
  genuine-client format authority; a future exact order (after
  independent review) may authorize one bounded reviewed actual capture,
  and the process/chunk collector follows earned format evidence.
- D09 (multi-chunk process completion, remaining truncation) and D10
  (duplicate/mismatched, substitution, unexecuted-branch matrix) remain
  NOT RUN; the expected procNN values are synthetic fixture protocol
  fields, not native process evidence.
- `build_selection`'s omitted-snapshot form is intentionally preserved
  (pure-facade fixture control; the frozen 017-j-era probe depends on
  it); it is not a runtime provenance path — run_capture always passes
  the explicit frozen snapshot.
- One foreign-ownership cleanup test remains an explicit environment
  skip (requires a real `chown` to another uid); it is never counted as
  a pass. The two intermediate 017-k commits disclosed under
  Verification were replaced on the objective branch before report
  publication; the final head and its full evidence are the
  authoritative state.

## Recommended strategic follow-up
- Independently verify this report's claims at the report head (remote
  PR head/parent/path/bytes re-run; the 14 frozen probes at the
  implementation head are already re-runnable from
  `STRATEGIC_HOME/probes` against
  `bed32f26ba7c456605562580793ae282f8001124`).
- Decide acceptance of 017-k (COMPLETE is a bounded claim, not
  acceptance) and choose the next exact order: a bounded reviewed
  actual capture, or the D09/D10 process/chunk matrix, or another
  review pass. Objective 017 remains ACTIVE through all criteria and
  018–024; the whole goal stays open.

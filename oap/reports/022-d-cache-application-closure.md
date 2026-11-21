# OAP Coding-Agent Report — 022-d

## Work order
- Identifier: 022-d; order path
  `oap/orders/022-d-cache-application-closure.md` (sha256
  `c244a94151e4c4ba89f4c396701d7f0e7106e30a81fedd1eb2c6cb2f5770efc8`,
  7,583 bytes, committed in the branch unchanged from the strategic
  authoring); numeric objective 22
- PR mode: AMEND_EXISTING_PR on the ONE existing PR 30
  https://github.com/ulfe-lmi/slaif-local-coding/pull/30, branch
  `oap/022-cache-source-replacement`, from verified report-only head
  `56cf8442812519389be6e17812641d5329038ddc` on order-verified remote
  main `144af0bd5e34387afcb8e3f9ddf761eabd56e817`. No new PR, no merge,
  no auto-merge.

## Status
COMPLETE

## Executive summary
ACTUAL RESULT: the v1 application closure is implemented at source A
`090aef28525e221a1a4eae900d45fb9da9a8ce42` on the same branch/PR 30,
amending the PR head from `56cf844…` (the 022-c report-only commit) to
implementation head B `7495672965dabbb2a2949aa2bec1175712ae92d1`
(manifest-only child). On the same ACTUAL `create_app` entry point
(`app.py`, `v1_application.py`, `bundle_replace.py`) this round closes
the 022-c gaps the order identified: (1) the closed COLD
marker/source-carrier law now runs BEFORE any cold raw acquisition,
owner allocation or checkpoint — a marker-shaped candidate inside the
ACTUAL cold-recognized root/result content spans is the fixed typed 409
with zero new owner, generation, compile or main forward, while
marker-shaped text anywhere else stays ordinary data, and a prior
session's marker presented cold to a different trusted namespace is
refused under its own distinct namespace-scoped MAC while the later
legitimate bootstrap succeeds; (2) the accepted 020
`admit_with_fence` is wired on BOTH the cold and the steady-state
transitions (an adverse durable fence or checkpoint fault is the fixed
typed 503 with zero main forward; the acquired cold owner/writer is
safely torn down on every prepublication failure; the same-process
retry stays fail-closed under its distinct fenced epoch; a fresh
process completes the publication through the store's idempotent
same-generation orphan re-publication); (3) the root-currentness 409 at
the app boundary (actual P/Q/T evidence `root_currentness_unproven` or
an established root-authority conflict: zero main forward, the retained
P/Q evidence committed, no bootstrap fallback; the accepted
component-level behavior for a genuinely issued unambiguous descendant
stays intact in the unchanged accepted lineage and is re-proven by the
component suites at B); (4) the compiled-context injection at the
endpoint-specific stable placement (Responses top-level `instructions`
preserving the caller's own instructions; Chat the first string-content
system message else inserted at the front, so an opaque marker always
accompanies its usable compiled content and off-graph content is never
promoted to a higher API role); (5) the Chat endpoint evidence at the
actual entry point (the endpoint-in-binding law: a read issued on
`responses` cannot complete on `chat`; root authority stays
Responses-only; the Chat round issues AND completes its own reads over
actual nonstream and split-SSE issuance causality); (6) the source-
change law at the app boundary (the model-issued re-read proves the
later version: EVIDENCE on the positively superseded original's
retained carrier, LIVE on the new carrier; the stale OLD transformed
body refuses with the fixed 409 marker-side refusal and no forward; a
genuine same-digest revert brings the carriers live again reusing the
retained historical payload without recompile); (7) the compiler/
budget failure law at the app boundary (the typed budget fence inside
the compiler seam before retention; the terminal failure re-served to a
later same-key/epoch request with the same fixed typed 503 refusal and
no retry loophole; recovery a new epoch in a fresh process; the 422
selection fence the last line of defense for forged/retained payloads
only); stream disconnect closes the owned upstream on the v1 path; the
ungoverned-route payload forwards byte-identical with zero compiles and
no session; and the fixed typed v1 refusal family (409
POLICY_STALE/TRANSACTION_CONFLICT, 422 SELECTION_REFUSED/
TRANSACTION_OVER_BOUND, 503 infrastructure/recovery/resource) with no
raw fallback forward. 185 focused app/selection/transaction tests pass
(true exit 0), ruff and mypy are clean, the 15-command locked gate ran
at exact B (13/15 commands rc=0; the two non-zero commands failed on a
single external host condition — the host /tmp tmpfs at its inode
limit — with the full causal evidence below), all ten exact-B GitHub
checks are SUCCESS, and the full clean-archive artifact proof passes.
Process qualifications: the source work was delivered earlier in this
same 022-d activation and re-verified green in the post-compaction
context, which also fixed the lint/typing findings the uncommitted
tests carried before the freeze; the clean-build r1/r2 install steps
failed on the same external /tmp condition and are preserved as
evidence, with the r3 run staging the install step through the
workspace-disk TMPDIR recorded in its startup.json. The 023 expanded
adversarial/lifecycle/telemetry matrix and the 024 actual-model/
genuine-Codex qualification remain NOT RUN and are not declared earned
by this round.

## Authoritative GitHub state
- Repository: ulfe-lmi/slaif-local-coding; PR 30
  https://github.com/ulfe-lmi/slaif-local-coding/pull/30 (state open,
  mergeable — re-verified this round)
- Base: main `144af0bd5e34387afcb8e3f9ddf761eabd56e817` (order-
  verified remote main, the accepted 021 merge)
- Head: oap/022-cache-source-replacement
  `7495672965dabbb2a2949aa2bec1175712ae92d1`
- Implementation head SHA: 7495672965dabbb2a2949aa2bec1175712ae92d1
- Report publication commit: SELF
- Starting remote SHA: 56cf8442812519389be6e17812641d5329038ddc (the
  022-c report-only head)
- Implementation commits pushed before report: source A
  `090aef28525e221a1a4eae900d45fb9da9a8ce42` (13 paths: 1 new + 12
  modified) and manifest-only B `7495672965dabbb2a2949aa2bec1175712ae92d1`
  (sole parent A; exactly `packaging/dev_provenance_manifest.json`
  changed; 316 source inputs; wheel
  `bcdcfa0f60b291804c198829a17863516145127c9914aff61c70f8d8973c9dd2`
  4,463,322 bytes / 89 entries; sdist
  `013ddc4982861791d38ac0cbc5eee3fcb8f674c819897c057545c09076168819`
  6,187,729 bytes / 314 entries). The exact activated order bytes and
  `oap/active` are committed in the branch and published on the PR
  (strategic-authored bytes unchanged).
- New PR this round: no. Amended existing PR: yes (PR 30 only). Merge
  performed: NO.

## Changes and files
At source A (13 paths: 1 new + 12 modified; 2,311 insertions / 80
deletions across src/ and tests/):
- `src/slaif_local_coding/app.py` (15 lines): the governed v1 request
  path reordered so the cold marker/source-carrier check runs BEFORE
  `establish_v1_session` (before any raw acquisition, owner allocation
  or checkpoint); the root-currentness 409 mapping at the app boundary;
  the endpoint-specific compiled-context placement dispatch (Responses
  top-level `instructions`; Chat first string-content system message
  else inserted at the front); the Chat endpoint issuance; the v1
  stream-disconnect close; the byte-identical ungoverned-route
  forwarding.
- `src/slaif_local_coding/constitution/bundles/v1_application.py`
  (347 lines): `establish_v1_session` re-joined over the accepted 020
  `admit_with_fence` for BOTH the cold and the steady-state
  transitions (now async, over the owned fenced IO); the safe
  prepublication cleanup of an acquired cold owner/writer on every
  prepublication failure; the same-process fail-closed fenced-epoch
  retry; the root-currentness 409 with the retained P/Q evidence
  committed and no bootstrap fallback; the typed budget fence inside
  the compiler seam before retention; the terminal compiler/budget
  failure re-served to the same-epoch repeat with the same fixed typed
  503 and no retry loophole; the fixed typed v1 refusal family.
- `src/slaif_local_coding/constitution/bundles/bundle_replace.py`
  (+54 lines): the source-change law at the transaction seam — the
  positively superseded original's retained carrier earns the
  non-resolving EVIDENCE marker without rebuilding the old entry key;
  the stale OLD transformed body refuses marker-side; the genuine
  same-digest revert reuses the retained historical payload.
- `tests/test_app.py` (+1,916 lines): the NEW `TestV1ApplicationClosure`
  suite (14 tests) plus its synthetic fixtures and fake-upstream
  handlers, over the ACTUAL `create_app` entry point with a bounded
  fake upstream.
- `tests/test_v1_application.py` (59 lines): the mechanical async
  conversion of the 18 committed 022-c app-seam tests to the now-async
  `establish_v1_session` (the fenced admit is async IO); no assertion
  changes.
- `ARCHITECTURE-for-agents.md` (6 scoped edits: the cache-profile-scope
  stale 022-a refusal sentence corrected to the 022-c/022-d wiring;
  the "V1 planned commit order (not yet implemented)" header corrected
  to the implemented scope; the dependency-bundle-law scope paragraph
  corrected; the 022-c paragraph cold clause corrected (the 022-c cold
  bootstrap performed raw acquisition before any marker gate and
  outside the fence); the NEW 022-d paragraph; the 022-d item in the
  compact objective-022 block) and its byte-identical repo mirror
  `oap/strategic-instructions/ARCHITECTURE-for-agents.md` (the
  strategic-home mirror synced to the same bytes, `cmp`-verified).
- `ARCHITECTURE.md` (6 scoped edits: the delivery-status paragraph,
  the section heading/scope line, the 022-c entry correction, the
  022-d lineage entry, the "only v1 mechanism active" line).
- `docs/CACHE-REWORK-LEDGER.md` (9 edits: R01/R02/R03/R05 and S01/S02
  scoped to PARTIAL at the app-boundary halves actually run with the
  named tests; R04 stays NOT RUN (native client compaction is 024);
  the 022-c entry corrected (the fenced path was resumed/steady-state
  at 022-c; the cold admit plus separate checkpoint corrected by
  022-d); the 022-d succession entry appended).
- `SECURITY.md` (1 edit: the "cold, resumed and steady-state owners
  alike" overclaim corrected — the fenced cold path is from 022-d).
- `docs/ADAPTER-CONFIGURATION.md` (2 edits: the 022-c marker-pre-check
  clause corrected for the cold bootstrap; the 022-d entry; the tail
  scoped "beyond the 022-d scope").
- `oap/active` (`022-c`→`022-d`) and
  `oap/orders/022-d-cache-application-closure.md` (the activated
  transcript, strategic-authored bytes unchanged).

## Acceptance evidence
### Section 1 (reject source markers before cold acquisition)
- Result: PASSED. Over the ACTUAL `create_app` entry point with
  synthetic settings and a bounded fake upstream: the first root
  envelope carrying a synthetic non-authoritative tag inside the
  recognized root content span is the fixed 409
  (`v1_transaction_conflict` / "governed v1 request refused") BEFORE
  any raw acquisition, owner allocation or checkpoint — zero main
  forward, zero compile, no live session, and the store probe for the
  fresh address reports `current_generation() == 0`; the same
  address's later legitimate root bootstraps at 200 with exactly one
  live marker, one compile, generation one and bound (1, 1) with the
  owner bound to generation one. A marker-shaped string OUTSIDE the
  actual cold-recognized source spans (an ordinary input item) stays
  data — byte-present on the wire while the legitimate root is the
  only edited carrier — and a ROOTLESS tagged payload is not a
  governed request at all (forwarded byte-identical, no session, no
  compile). The isolation proof: a marker actually issued by trusted
  session A, presented COLD to a different trusted namespace B
  (different principal/session, identical source, the same protected
  recovery root), is the fixed 409 with zero B-side acquisition; B's
  own clean identical root then bootstraps with its own compile and
  its own DISTINCT marker (the MAC is namespace-scoped), and A's
  committed state is untouched. Evidence:
  `tests/test_app.py::TestV1ApplicationClosure::
  test_cold_marker_in_root_refuses_before_any_acquisition`,
  `::test_cold_marker_outside_source_spans_stays_data`,
  `::test_cold_prior_session_marker_refused_across_sessions`
  (re-proven at exact B by the gate's full suite).
### Section 2 (preserve currentness and use the accepted recovery fence)
- Result: PASSED. The root-currentness 409 at the app boundary: the
  legitimate root (referencing A.md) bootstraps and its direct
  response issues the complete AGENTS.md+A.md read; the subsequent
  boundaryless root-bearing result yields the ACTUAL P/Q/T evidence
  `root_currentness_unproven` (the retained snapshot's outcome
  `ROOT_CURRENTNESS_UNPROVEN`, the same-run Q outcome
  `ROOT_CURRENTNESS_UNPROVEN` with the
  `OPAQUE_ROOT_BEARING_GROUP` witness class) and the transaction is
  the fixed 409 with ZERO main forward — the negative evidence is
  committed and retained (the fence generation and the state
  generation published, the bound advanced), and the identical request
  repeated is refused again with no forward and no bootstrap
  fallback. The fence-law fault test: the fault-injection test raises
  `OSError` in `os.fsync` for the round-two transition — the adverse
  durable FENCE cannot publish, so no state transition is permitted
  at all: the fixed 503 (`v1_transition_refused`) with no forward and
  the RAM revision, the durable generation and the bound all
  untouched; once the fault heals the same request earns the accepted
  currentness 409 with the fence and state generations published and
  the bound advanced. The cold prepublication failure law: the fault-
  injection test raises `OSError` in `os.fsync` starting with the
  second fsync, so the checkpoint file's fsync fails while the cold
  owner/writer is already acquired — the fixed 503
  (`v1_cold_publish_refused`) with zero main/compile, the acquired
  owner/writer torn down (no live session, `current_generation() ==
  0`, the orphan `checkpoint-1.json` unreferenced by any pointer), the
  same-process re-establishment fail-closed (the fenced epoch law mints
  a distinct epoch for the re-acquired owner, so its record can never
  match the orphan bytes and the torn-checkpoint law refuses with zero
  main forward), and the later legitimate cold startup of the same
  address in a FRESH process succeeds at generation one (the store's
  idempotent same-generation orphan re-publication: the fresh
  registry's first allocation is epoch one again, the re-derived
  record is byte-identical, the pointer references the checkpoint,
  bound (1, 1)). The accepted component lineage behavior for a
  genuinely issued unambiguous descendant is preserved in the
  unchanged accepted 018-q lineage (re-proven at B by the component
  suites in the gate's full suite); the app-boundary evidence covers
  the refusal path this round wired. C's existing ordinary failed-
  fsync replay-after-fault regression and success path are preserved
  and re-proven at B. Evidence:
  `tests/test_app.py::TestV1ApplicationClosure::
  test_unproven_currentness_refuses_with_retained_evidence`,
  `::test_adverse_fence_fault_refuses_and_heals_to_conflict`,
  `::test_cold_prepublication_failure_cleans_owner_and_recovers`;
  `tests/test_app.py::TestV1GovernedRequestPath::
  test_publish_fault_refuses_replay_until_the_generation_heals`;
  `tests/test_v1_application.py::
  test_cold_bootstrap_commits_and_publishes`, `::
  test_new_read_advances_generation_then_replays`, `::
  test_resume_restores_state_in_a_higher_epoch`, `::
  test_resumed_session_materializes_publish_and_replays_the_
  fixed_point`.
### Section 3 (complete the existing application evidence)
- Result: PASSED at the bounded fake-upstream application scope on
  BOTH endpoints. The Chat endpoint at the actual app boundary: the
  Responses bootstrap establishes the root (root authority is
  Responses-only; a Chat user message carrying the same envelope stays
  data, never a root carrier); the Chat rounds issue AND complete
  their own reads on the same chat endpoint (the call-ID binding law
  is endpoint-inclusive: a responses-issued ID can never be completed
  on chat — the typed issuance conflict); each transformed outgoing
  body carries the ACTUAL selected compiled context at the stable Chat
  system placement as the first message while every other message
  (the user root text, the assistant tool_calls, the tool result
  order) is preserved; the only Chat source carrier edited is the
  acquired tool result (raw source gone, live marker in); the Chat
  direct response's issuance freezes under THIS request's own
  represented completed-fact frontier (internal compiler traffic and
  client fabrication supply none); the resend of the transformed body
  is the byte-identical fixed point with no further compile. The Chat
  split-SSE issuance end to end: the complete tool call is assembled
  over bounded chunk seams (one frame deliberately split mid-frame),
  the issuance is registered under this request's FROZEN frontier,
  the stream passes through byte-identical, and the next Chat round
  pairs the receipt (the read acquired, the occurrence anchored under
  that frontier, the tool carrier edited, the compiled region
  extended to both blocks). The remaining R01–R05/S01–S02
  application evidence at the actual body level: exact tool
  preservation and the fixed point (R01/R02); the reduced client
  history (root envelope plus the bare exec call, NO result) carries
  no read carrier — the ordinary RAM reuse edits the root carrier from
  the retained state and reinjects the COMPLETE source-absent
  compiled working set (both rendered blocks) at the Responses stable
  placement with zero recompile (R01/R05; the fake-history reduction
  and the recorded reference-format cases are distinguished from
  native client compaction, which stays 024 — R04 NOT RUN); the
  source change/replay/revert (C04/C05/R03: the model-issued re-read
  at new bytes recompiles and marks the NEW carrier live while the
  positively superseded old ORIGINAL's retained carrier earns the
  non-resolving evidence marker without rebuilding the old entry key;
  the stale OLD transformed body is the fixed 409 with no forward;
  the further issued re-read carrying the ORIGINAL bytes is the
  deliberate revert — no recompile, the retained historical payload
  reused, the carriers live again and the v2 carrier the superseded
  evidence); different trusted namespaces with identical source (the
  cross-session cold-marker refusal above — S01 at the app boundary;
  the full adversarial isolation matrix stays 023); the signed
  identity/route protection holds through the profile-independent
  ingress layer ordered before the v1 pipeline (the existing
  service/gateway ingress suites re-proven at B, with the v1 session
  address bound to the authenticated principal/session/route — S02
  signed half); the compiler failure (the invalid compiler completion
  is never an entry: the fixed 503 with zero main forward and exactly
  ONE compile attempt; the terminal work-plane failure re-served to
  the same-epoch repeat with the same typed refusal and no retry
  loophole; the bootstrap remains committed at generation one with
  its bound; the fresh-process restart in a distinct epoch completes
  the same request with exactly one successful compile, after which
  the fixed point holds) and the budget overflow (a valid compiler
  index whose rendered block exceeds the entry's width x slot
  allowance is typed BEFORE retention — no truncation, no partial
  form ever injected, retained or forwarded — the fixed 503 with zero
  main forward and exactly ONE compile attempt; the same-epoch repeat
  re-served the same typed refusal; the fresh-process restart
  completes the same request with an in-allowance compile, after
  which the fixed point holds and the oversized statement never
  reached the model); the stream-disconnect cancellation (the cold
  bootstrap commits before the stream; the client disconnect after
  the first forwarded chunk cancels the owned upstream work — the
  upstream stream is closed — S02); and the ungoverned-route payload
  (a route whose model carries no explicit route contract is never a
  governed v1 route — its root-bearing payload crosses the wire
  byte-identical with no session, no compile and no v1 component
  touched, while the governed route's contract law stays exact — S02).
  Evidence: `tests/test_app.py::TestV1ApplicationClosure::
  test_chat_nonstream_governed_rounds_with_compiled_system_placement`,
  `::test_chat_split_sse_issuance_and_acquisition`, `::
  test_reduced_history_reinjects_source_absent_working_set`,
  `::test_source_change_stale_replay_and_revert`, `::
  test_compiler_failure_refuses_then_heals`, `::
  test_budget_overflow_refuses_then_heals`, `::
  test_v1_stream_disconnect_closes_upstream`, `::
  test_ungoverned_route_forwards_unchanged`; the 022-c
  `TestV1GovernedRequestPath` suite (6 tests, Responses boundary) and
  the 18-test `tests/test_v1_application.py` app-seam suite re-proven
  at B. Ledger states after this round: R01/R02/R03/R05 and S01/S02
  PARTIAL at their named app-boundary halves (the actual-upstream and
  023-024 halves NOT RUN); R04 NOT RUN. Synthetic fixture sources
  throughout; actual forwarding, compiles and recovery content reads
  instrumented (no counter-only substitution). The 023 expanded
  adversarial/lifecycle/telemetry matrix and the 024 actual-model/
  genuine-Codex qualification remain mandatory and NOT RUN.

## Verification
- Focused suites at source A (before the candidate freeze), true
  exits: `umask 022 && uv run --frozen pytest -q tests/
  test_app.py tests/test_v1_application.py tests/test_bundle_replace.
  py` — 185 passed, exit 0; `uv run --frozen ruff check .` —
  PASSED ("All checks passed!"); `uv run --frozen ruff format
  --check .` — PASSED (761 files); `uv run --frozen mypy src tests`
  — PASSED (205 source files); `uv run --frozen python
  scripts/docs_consistency_check.py` — PASSED (19 claim docs). All
  re-proven at exact B by gate cmd03–cmd06.
- 15-command locked gate at exact B (`gate-driver-022d.sh`, managed
  absolute-path invocation, run dir `gate-run1`, driver pid 2864642
  birth 384283329, ppid 598258, uid 1001, capture umask 077, driver
  source_sha256 `415702bf451040064b5b296aad4b52abb030b5727ba6bb936ae2b41747c404ee`,
  started 2026-11-21T02:56:55Z, head `7495672…`, tree guard
  tolerating exactly the operator's unstaged `AGENTS.md` update):
  cmd01 `uv lock --check` — PASSED; cmd02 `uv sync --frozen --extra
  dev` — PASSED; cmd03 `ruff check .` — PASSED; cmd04 `ruff format
  --check .` — PASSED (761 files); cmd05 `mypy src tests` — PASSED
  (205 files); cmd06 `python scripts/docs_consistency_check.py` —
  PASSED (19 docs); cmd07 `bash -c 'umask 022; uv run --frozen pytest
  -q'` — FAILED (externally attributed): 7122 passed, 28 skipped, 6
  failed, 16 warnings in 1497.43s (0:24:57) — ALL 14 new 022-d tests
  passed; the six failures are exclusively
  `tests/test_cache_native_fixture_controller.py::TestExporterStates`
  (017 native-fixture exporter tests, byte-identical to the 022-c
  gate where they passed), and every one of them is the identical
  `OSError: [Errno 28] No space left on device:
  '/tmp/slaif-fixture-originals-…'` raised by `os.makedirs` in the
  tests' own owned-tmpdir seam BEFORE any test logic runs — the host
  /tmp tmpfs was at its inode limit (at the failure time `df -i /tmp`:
  1,048,576 inodes used / 0 free, 100%; the /tmp content belongs to
  unrelated other-process work this round must not touch); cmd08 `uv
  build` — PASSED; cmd09 `python scripts/artifact_policy_check.py
  --dist dist --inspect` — PASSED; cmd10 `python
  scripts/artifact_policy_check.py --dist dist --install-smoke` —
  FAILED (externally attributed): "fresh wheel install failed:
  CalledProcessError" — the fresh-install step's temp files stage on
  the same exhausted /tmp tmpfs (the identical failure mode that
  stopped the clean-build r1/r2 install steps, preserved as evidence);
  cmd11 `python --version` — PASSED (`Python 3.12.15`); cmd12 `python
  -m compileall -q src tests oap/bin scripts` — PASSED; cmd13 `python
  scripts/dev_provenance_manifest.py --verify --dist dist` — PASSED
  (`development provenance OK: state=development head=
  7495672965da`); cmd14 `bash -n` over `oap/bin/*.sh
  packaging/*.sh` — PASSED; cmd15 `git diff --check
  144af0bd5e34387afcb8e3f9ddf761eabd56e817 HEAD` — PASSED. The two
  non-zero commands are fully explained by the single external host
  condition (the gate-run1 captures retain the complete tracebacks
  and the `df -i` state); every other byte of the suite — including
  all 14 new 022-d tests, the full legacy/fake-upstream regression
  and the 017-021 component suites — passed at exact B.
- TEN required exact-B GitHub checks at
  `7495672965dabbb2a2949aa2bec1175712ae92d1`: ALL 10 SUCCESS at the
  exact head (re-verified this round): test, Analyze (actions),
  Analyze (python), gateway-contract, docker, docker-published,
  operator-session, cache-native-containment, cache-native-fixture,
  CodeQL — no failures, no cancellations on this head.
- Clean exact-B archive: the r1 (`clean-build-022d`) and r2
  (`clean-build-022d-r2`) runs — archive/extract/build exit 0 with
  both artifacts byte-identical to the manifest, but the fresh
  noneditable install failed exit 2 with "No space left on device" at
  the /tmp temp path (the external inode exhaustion above); both run
  dirs are preserved as failure evidence. The r3 run
  (`clean-build-022d-r3`, driver pid 2867325, driver source_sha256
  `a371fcad08198c4b888b83897938bad4df55ef849268ed5ba8aedb2fcfbd2e38`,
  umask 077, fail-closed no-overwrite guards) staged the install
  step's temp files through the workspace-disk TMPDIR recorded in its
  `startup.json` (`install_tmpdir`): git archive of B (39,024,640
  bytes), extract and `uv build` exit 0 with BOTH artifacts
  byte-identical to the manifest (wheel
  `bcdcfa0f60b291804c198829a17863516145127c9914aff61c70f8d8973c9dd2`
  4,463,322 bytes / 89 entries; sdist
  `013ddc4982861791d38ac0cbc5eee3fcb8f674c819897c057545c09076168819`
  6,187,729 bytes / 314 entries); fresh NONEDITABLE install of the
  clean-built wheel into a venv created by the EXPLICIT Python 3.12
  interpreter exit 0, import probe exit 0 (version 0.1.0, module
  resolved inside the disposable venv only, probe records
  interpreter `3.12.15 (main, Oct  9 2026, 15:22:32) [Clang 22.1.3
  ]`, console entry point present).
- Full clean-archive BOTH artifact proof: ALL PROOF ASSERTIONS
  PASSED (helper exit 0, captured after gate cmd08 rebuilt the repo
  `dist/`; no rebuild of the frozen candidate): the FULL clean-
  archive path set — 956 files — byte-identical to Git B; the 316
  manifest source inputs byte-identical to the ORIGINAL Git A input
  map, to Git B and to the clean extracted tree; B verified
  manifest-only (sole parent A; exactly
  `packaging/dev_provenance_manifest.json` changed); every sdist
  entry (314 total) allowlisted-generated (exactly one, PKG-INFO
  `633064e62d60b8a90204ac68262debcc5df49f483bf4908637a6cfc885450824`
  22,762 bytes) or byte-identical to its Git B blob (313 verified);
  every wheel runtime entry (83 of 89) byte-identical to its Git B
  src/ blob; wheel RECORD (88 verified entries) exactly covers the
  wheel entry set with per-entry sha256 and size, unique raw rows;
  sdist PKG-INFO bytes equal wheel METADATA bytes; wheel
  entry_points exactly equal Git B pyproject `[project.scripts]`
  (`slaif-local-coding = slaif_local_coding.cli:main`); dist-info
  LICENSE/NOTICE byte-identical to Git B; repo gate `dist/` artifacts
  byte-identical to the clean artifacts; the fresh noneditable
  install imports the module from the disposable venv only under the
  explicit Python 3.12 interpreter with the console entry point
  present.
- Live model inference: NOT RUN (protected Qwen/18020 fixture
  untouched; no dev service started). Actual Codex qualification:
  NOT RUN. Native client compaction (R04): NOT RUN. No registry
  publication, deployment, benchmark or cutover. No merge, no
  auto-merge.

## Live model/service evidence
- NOT RUN. The protected Qwen/18020 service, profiles, launch/
  systemd, keys and network state were not touched; no bounded live
  call was made this round; the protected fixture is unchanged.

## Local setup/dependencies
- Repo-local uv frozen environment (Python 3.12.15) for the focused
  runs and the gate; the explicit `/home/janezp/.local/bin/
  python3.12` (3.12.15) for the fresh noneditable install venv; the
  r3 install step staged its temp files through the workspace-disk
  TMPDIR recorded in `clean-build-022d-r3/startup.json` because the
  host /tmp tmpfs was at its inode limit from unrelated other-
  process work; no new dependencies; no sudo; no durable
  configuration change.

## Documentation
- Updated in this round (same PR): `ARCHITECTURE-for-agents.md` (the
  new 022-d compact block at its earned scope — active on opted-in
  v1 routes at its bounded fake-upstream application scope on both
  endpoints, PENDING strategic review, 023-024 NOT RUN — the stale
  022-a refusal sentence, the "not yet implemented" header, the
  dependency-bundle-law scope paragraph and the 022-c paragraph cold
  clause corrected, plus the objective-022 item); its byte-identical
  mirrors (`oap/strategic-instructions/ARCHITECTURE-for-agents.md` in
  the repo; the strategic-home mirror synced to the same bytes);
  `ARCHITECTURE.md` (delivery-status paragraph, section heading/scope
  line, 022-c entry correction, 022-d lineage entry, the only-active-
  v1-mechanism line); `docs/CACHE-REWORK-LEDGER.md` (the R01/R02/
  R03/R05 and S01/S02 states scoped to the app-boundary evidence
  actually run with the named tests; R04 NOT RUN; the 022-c entry
  corrected; the 022-d succession entry); `SECURITY.md` (the fenced
  cold path from 022-d, correcting the 022-c overclaim);
  `docs/ADAPTER-CONFIGURATION.md` (the 022-c clause correction and
  the 022-d entry). No new planning or audit documents.
- Historical-report corrections (the 018-q/r/s/t pattern; the
  immutable 022-c report is NOT edited): the 022-c report's claim
  that the pre-forward protected generation ran "through the accepted
  020 owned/fenced admit/checkpoint path (cold, resumed and steady-
  state owners alike, no raw writer shortcut)" and its "marker pre-
  check before raw acquisition" phrasing are corrected in the CURRENT
  docs — the 022-c cold bootstrap performed raw acquisition and
  checkpointing in its first establish call, before any marker gate
  and outside the fence; both closed by the 022-d closure slice.

## Safety/scope confirmations
- Unrelated files: none. The branch diff from the 022-c report-only
  head `56cf844…` to B is exactly the 13 source/doc/transcript paths
  listed above plus the manifest at B; cmd15 `git diff --check
  144af0bd… HEAD` clean.
- The operator-mandated local `AGENTS.md` governance update (the
  §19 evidence-phrasing law) is preserved in the working tree
  UNSTAGED per the order; it is not committed, not a mapped
  development source input, and no gate/proof step consumes it — the
  gate and proof tree guards tolerate exactly that one modification
  and refuse any other drift.
- Secrets/raw content: none committed, printed or reported (evidence
  uses hashes, counts, command names and statuses only; synthetic
  session and marker key material stays inside the test modules and
  protected environment references).
- Protected 18020/Qwen/Codex fixture changed: NO.
- Required tests skipped/not run: live inference, actual Codex and
  native compaction are ordered NOT RUN; nothing required was
  skipped. The two externally failed gate commands are reported
  above with their full causal evidence.
- Scope deviation: none; the legacy profile and gateway contract are
  unchanged; the v1 activation is the explicit opt-in configuration
  surface only.
- Extra objective PR: NO. Coding merge: NO.
- Active/order edited: NO (committed bytes verified unchanged from
  the strategic authoring).
- Report commit report-only: yes (the SELF commit).

## Known limitations/blockers
- The 022-d qualification is BOUNDED to the fake-upstream
  application scope: synthetic identity and fixture sources, a
  bounded fake upstream for both the main forward and the direct tool-
  free compiler channel; no actual-model, live-service, genuine-
  Codex, deployment, registry or benchmark evidence is earned. The
  023 expanded adversarial/lifecycle/telemetry matrix and the 024
  actual-model/genuine-Codex qualification and immutable handoff
  remain mandatory (NOT RUN).
- EXTERNAL GATE DEVIATION: host /tmp tmpfs inode exhaustion
  (1,048,576/1,048,576 inodes used, 0 free at the failure time; the
  content is unrelated other-process work) made two locked-gate
  commands non-zero at exact B — cmd07's six
  `TestExporterStates` failures (the 017 tests' owned-tmpdir seam
  creates a literal /tmp directory and receives `OSError ENOSPC` in
  `os.makedirs` before any test logic) and cmd10's fresh-install
  temp staging. The candidate itself is clean at B: every other
  command of the gate is rc=0, all 14 new 022-d tests passed, and the
  same six tests passed in the 022-c gate on this host when /tmp
  held free inodes. A same-command re-run (or a re-run of just the
  six tests plus the install-smoke command) at exact B is re-runnable
  as-is once host /tmp inodes free; the gate-run1 captures retain the
  complete failure evidence.
- The compact architecture's "017 current earned/unearned scope and
  qualified-status lineage" paragraph carries an objective-022 status
  line that ends at 022-c and does not carry the 022-d item the
  canonical `## Objective boundaries` block (same file, earlier)
  does; all mirrors share the same bytes. Frozen at B this round, so
  recorded here for strategic follow-up rather than unfreezing the
  candidate.
- Pre-this-context source work: the 022-d §1/§2/§3 implementation
  was delivered earlier in this same activation; the post-compaction
  context re-verified it green (185 focused passed, true exit 0) and
  fixed the lint/typing findings the uncommitted tests carried before
  the freeze (ruff I001 import sort and three E501 reflows in
  `tests/test_app.py`, `ruff format` on exactly the three touched
  modules, and three mypy fixes: a response cast at
  `tests/test_app.py:2571`, an `r_result is not None` assertion split
  at `tests/test_app.py:2656`, and the established-session
  `session_owner is not None` assertion at
  `src/…/bundles/v1_application.py:569`).
- The standard control reader (managed handle 42360, the order-
  recorded PID 2620975) that consumed the single 022-d control `OK`
  frame was collected in a prior context of this process; its exit
  code is no longer retrievable, and this context confirmed the
  handle is retired (`write_stdin` → Unknown process id) with no
  reader attached to control.fifo.

## Recommended strategic follow-up
Factual only: strategic review of 022-d at its bounded application-
closure scope (fake-upstream evidence with synthetic fixture sources
on both endpoints); a same-command locked-gate re-run (or the six
`TestExporterStates` tests plus the install-smoke command) at exact B
once host /tmp inodes free, to close the externally attributed
deviation; the one-line objective-022 lineage sync in the compact
architecture's 017 lineage paragraph (known limitation above); the
immutable 022-c report's cold-path phrasing is already corrected in
the current docs; objectives 023-024 remain the mandatory unearned
v1 stages (the 023 expanded adversarial/lifecycle/telemetry matrix;
the 024 actual-model/genuine-Codex qualification and immutable
handoff).

# OAP Coding-Agent Report — 017-l

## Work order
- Identifier: `017-l`; order path `oap/orders/017-l-owned-io-and-original-seeds.md`; numeric objective 017
- PR mode: AMENDED_EXISTING_PR

## Status
COMPLETE

## Executive summary
Repaired exactly the two remaining offline capture boundaries of the inert
`scripts/real_client_capture.py` utility, as ordered:

1. **Owned accepted I/O is now closed at teardown, not only the
   listener.** `_OwnedThreadingHTTPServer` tracks every admitted owned
   request socket (bounded by the existing handler cap, registry
   discarded on thread-startup failure), and `FakeProvider.stop()` runs
   an ordered quiesce: freeze, stop accepting, effective socket
   shutdown (`SHUT_RDWR`) plus close of every admitted socket *before*
   joining the serve/handler threads, then a bounded grace join over
   `active_handlers() or active_admissions()`. The probe's in-flight
   progressing drip-body read (authenticated POST, Content-Length 1000,
   owned one-byte/0.05 s drip — a state where the per-read 2 s timeout
   cannot fire) is now closed at stop and the peer observes closure;
   repeated stop is safe; unrelated sockets/processes survive. A
   teardown that cannot complete in bound is reported honestly
   (`teardown_incomplete`) and can no longer yield a successful
   `completed` run — the fixed truthful `cleanup_failed` outcome with
   no raw error details.
2. **Original seeds are now immutable before child launch.**
   `run_capture` binds the exact original seed bytes (default
   `WORKSPACE_FILES` plus any caller-supplied extra synthetic
   `workspace_files`; extras win on name collision) after
   `setup_scratch` and *before* launch, and `_verify_selected_content`
   compares received selected text only against that pre-launch
   binding — it never re-reads a child-writable workspace file at
   finalization. A child that rewrites a legitimately issued file can
   no longer produce falsely verified/persisted text: tampered/unverified
   text is stripped with the fixed non-echoing `content_unverified`
   reason (or a typed non-echoing failure plus safe cleanup), and its
   bytes reach no persisted record, console, repr or diagnostic. Custom
   seed/path positives stay general (no A.md/alpha/marker
   special-casing); verified text still retains exact received
   text/digest under the byte cap.

Both repairs are offline, synthetic-only, stdlib-only: no new HTTP
framework or dependency, no sandbox redesign, no actual capture, no
live inference, no protected-fixture mutation. The utility remains
inert (not wired into the adapter runtime); the actual-client path
stays input-gated with the generated `not_ready` verdict; `fixture_
authority: none`; D09/D10 unchanged (NOT RUN). All FIFTEEN frozen
strategic probes (including the new v2 probe, 3/5 at the 017-k head,
now 5/5), the focused and full locked gates, the clean archive
reproduction, the fresh-wheel controls and all 8 CI checks pass at the
implementation head.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`; PR #25
  https://github.com/ulfe-lmi/slaif-local-coding/pull/25 (OPEN, not
  draft)
- Base `main` `96c790423f6f0097a56a0b12bacda8a9b6da6aba` (unchanged);
  head branch `oap/017-cache-read-observation`
- Starting remote SHA: `d11ca86febcc5debe7660bbaa1816d6b2e9a3846`
  (017-k SELF)
- Implementation head SHA: cd9f4fe4e8b85945142ba4d9cef0de7f5fd953e4
- Report publication commit: SELF
- Implementation commits pushed before report (ordinary append-only on
  the starting SHA; no reset/rebase/squash/amend/force):
  - `17e09b897362fe6098a0a6943fa9ca8b9db3e7eb` — source A: utility +
    tests + docs + exact unchanged activated order/active
  - `cd9f4fe4e8b85945142ba4d9cef0de7f5fd953e4` — manifest B:
    development provenance manifest refresh (implementation head)
- New PR this round: NO; amended existing PR #25: YES; merge
  performed: NO; auto-merge: NO

## Changes and files
Source A `17e09b897362fe6098a0a6943fa9ca8b9db3e7eb` (10 files, +872/
-62):

- `scripts/real_client_capture.py` — (1) `_OwnedThreadingHTTPServer`
  gained the bounded `_admitted` socket registry, a `_closing` flag,
  `begin_quiesce()`, `admitted_sockets()`, `active_admissions()` and
  `close_admitted_sockets()` (OSError-safe `shutdown(SHUT_RDWR)` +
  `close`; admission is refused after quiesce begins and on
  thread-startup failure the socket is discarded from the registry).
  (2) `FakeProvider.stop()` order is now: freeze → `begin_quiesce()`
  → close admitted sockets (before the serve-thread join, which can
  otherwise block up to the `serve_forever` poll interval) →
  `shutdown()` → `server_close()` → thread join → bounded grace join
  on `active_handlers() or active_admissions()` → `teardown_incomplete`
  when anything survives. (3) `_select_outcome` first:
  `teardown_incomplete` → fixed `("cleanup_failed", False)`. (4)
  `_verify_selected_content` now takes `original_seeds: dict[str,
  bytes]` and never re-reads `workspace/step.path`; unverified text is
  stripped with the fixed `content_unverified` reason/count (typed
  non-echoing failure plus safe cleanup where the record cannot be
  retained). (5) `run_capture` binds `original_seeds` from
  `WORKSPACE_FILES` plus caller-supplied `workspace_files` (extras win
  on collision) after `setup_scratch`, before launch. Cap 4 /
  all-method budgets / auth silence / finite reads / issued-registry
  snapshot / final content snapshot / no late unverified append are
  preserved.
- `tests/test_real_client_capture.py` — 8 new methods:
  `TestOwnedIoQuiesce` (4): authenticated progressing slow-drip body
  closed at stop with peer-observed closure; listener closed, port
  re-bindable, repeated stop safe, unrelated session survives;
  `teardown_incomplete` never yields a `completed` run (short grace +
  stalling `do_POST` → `cleanup_failed`, no raw error echo);
  idle-stalled read times out with complete teardown.
  `TestOriginalSeedImmutability` (4): default-seed exact received-text
  retention; custom extra `workspace_files` `C.md` exact-text
  retention (general path, not A.md/alpha); child-mutated `A.md`
  negative — `MUTATED_SEED_MARKER` absent from every persisted file,
  `content_unverified` count 1, non-echoing typed failure; unseeded
  path never verified.
- `docs/CACHE-OBSERVATION-CONTRACT.md` — owned-I/O quiesce and
  immutable-original-seed law; stale claims corrected to the actual
  active-socket/immutable-seed guarantees (concise current statement
  plus ledger link).
- `docs/CACHE-REWORK-LEDGER.md` — 017-l stage row.
- `TESTING.md` — round sentence and new test classes.
- `ARCHITECTURE.md`, `ARCHITECTURE-for-agents.md` plus the
  byte-identical compact mirror
  `oap/strategic-instructions/ARCHITECTURE-for-agents.md` (`cmp`
  clean) — capture-utility boundary sentences.
- `oap/orders/017-l-owned-io-and-original-seeds.md` (activated order,
  exact unchanged bytes) and `oap/active` (`017-l`).

Manifest B `cd9f4fe4e8b85945142ba4d9cef0de7f5fd953e4` (1 file):
`packaging/dev_provenance_manifest.json` refreshed (source `17e09b8…`,
186 inputs); wheel byte-identical to the 017-k head because `src/` is
unchanged; frozen RC10 publication section untouched.

## Acceptance evidence
### Area 1 — close owned accepted I/O, not only the listener
- Result: PASS.
- Evidence: new v2 probe
  `STRATEGIC_HOME/probes/check-capture-owned-io-and-seed-v2.py` at
  head `cd9f4fe…`: 5/5 PASS with valid positive controls, including
  `shutdown_closes_owned_inflight_request_socket` (the exact ordered
  scenario: authenticated POST body read entered at
  `request_count==1`, Content-Length 1000, owned 1-byte/0.05 s drip;
  after stop the peer observes the accepted socket closed) and
  `normal_owned_provider_shutdown_control`. New focused tests
  `TestOwnedIoQuiesce` (4/4): drip closure + repeated stop +
  unrelated-session survival + listener closed/re-bindable;
  `teardown_incomplete` → `cleanup_failed` (never `completed`) with no
  raw error details; idle-stall timeout → complete teardown. Focused
  suite 191 passed / 1 honest environment skip / 0 failed; full gate
  2233 passed / 28 skipped / 0 failed.

### Area 2 — original seeds immutable before child launch
- Result: PASS.
- Evidence: v2 probe at head: `original_seed_receiver_control` (exact
  default-seed text retained), `custom_seed_receiver_control`
  (caller-supplied extra seed path, general not hardcoded) and
  `child_mutation_cannot_redefine_permitted_original_seed` (child
  rewrite of an issued file is stripped `content_unverified`, marker
  absent from every persisted record, non-echoing) all PASS. New
  focused tests `TestOriginalSeedImmutability` (4/4) cover the same
  boundaries in-suite, including the unseeded-path negative and
  `MUTATED_SEED_MARKER` absent from every persisted file.

## Verification
- All FIFTEEN frozen strategic probes, each
  `REPO/.venv/bin/python STRATEGIC_HOME/probes/<script> --head
  cd9f4fe4e8b85945142ba4d9cef0de7f5fd953e4`: PASSED — 23/23, 16/16,
  5/5, 6/6, 40/40, 63/63, 10/10 (observer; 162 quoted-word variants),
  12/12, 3/3, 2/2, 4 checks + 1 memory measurement (not a test), 2/2,
  2/2, 8/8, 5/5 (new v2 probe; 3/5 at the 017-k head — both owned-I/O
  and original-seed negatives now pass). Every probe digest verified
  against immutable baseline
  `STRATEGIC_HOME/reviews/017-l-probe-hashes.json` (15/15, no edit to
  oracle/hash files) before running; results written under owned 0700
  temp root `/home/janezp/tmp/017l/results/`.
- `uv lock --check`: PASSED
- `uv sync --frozen --extra dev`: PASSED
- `uv run --frozen ruff check .`: PASSED
- `uv run --frozen ruff format --check .`: PASSED
- `uv run --frozen mypy src tests`: PASSED
- `uv run --frozen python scripts/docs_consistency_check.py`: PASSED
- `uv run --frozen pytest -q`: PASSED — 2233 passed, 28 skipped (27
  prior + 1 real-`chown` environment skip), 0 failed (process-local
  umask 022; full gate run once after the final manifest commit, per
  the order's no-redundant-rerun law)
- `uv run --frozen pytest -q tests/test_real_client_capture.py`:
  PASSED — 191 passed, 1 skipped (re-verified in this publication
  round, 58.12 s)
- `uv build`: PASSED — wheel `99e5ad582232c5a2e9e717c7707162b8c572619
  83aa0cf472e0c4e0d9263ac71` / sdist `147732c3be4d4a257ffb23640307937a
  394f7fce00ea89a4286dbee1b57cdc9c`, equal to the manifest digests
- `uv run --frozen python scripts/artifact_policy_check.py --dist dist
  --inspect`: PASSED — ok, 0 violations
- `uv run --frozen python scripts/artifact_policy_check.py --dist dist
  --install-smoke`: PASSED
- `uv run --frozen python scripts/dev_provenance_manifest.py --verify
  --dist dist`: PASSED
- `python -m compileall -q src tests oap/bin scripts`: PASSED
- `bash -n` over `oap/bin/bootstrap-two-codex-oap.sh`,
  `oap/bin/launch-coding-agent.sh`, `oap/bin/launch-strategic-agent.sh`,
  `packaging/readyz-wait.sh`: PASSED
- `git diff --check`: PASSED (clean)
- Targeted credential/raw-log/privacy scan of the round diff
  `d11ca86…..cd9f4fe…`: PASSED — synthetic `tok` bearer tokens and the
  strategy-authored order's own runtime-path text only; no real keys,
  no private URLs/IPs, no raw prompt/source bodies
- Invariance: PASSED — frozen `docs/CACHE-REWORK.md` SHA256
  `410df5c0b8f90b05220adc32c8e673b143c0cf1fa3da02270d91ac453c886abd`
  unchanged; `docs/RC-HANDOFF.md`, `docs/CACHE-IMPLEMENTATION-PLAN.md`,
  all prior `oap/orders/*` and `oap/reports/*` and `packaging/releases/
  ` byte-unchanged in the round diff; compact mirror `cmp` byte-identical
- Clean source-A `git archive` reproduction (owned 0700 temp root):
  PASSED — `git archive 17e09b8…` with utility/fake-child/test
  present → `uv sync --frozen --extra dev` + `uv build` →
  byte-identical wheel `99e5ad58…` / sdist `147732c3…` (equal to the
  manifest digests)
- Fresh non-editable installed-wheel functional controls (fresh
  CPython 3.12.15 venv in an owned 0700 temp root; `uv pip install
  --no-cache-dir` of the built wheel; package path proves
  site-packages outside the repository; version 0.1.0): PASSED —
  11/11 of the recorded 017-g observer controls re-exercised against
  the installed `slaif_local_coding.constitution.bundles`: the four
  quoted-word defect forms typed `QUOTED_OPERAND` non-removable with no
  digest/span/phantom members, first-position variants, whole-word
  double- and single-quoted controls and the plain control earned with
  exact members, the guarded ordered bundle (COMPLETE + exact digest +
  ordered members + slot width + exact content span), the unguarded
  human form with preserved requested members and no digest, and repr
  privacy (no raw command literal in any repr)
- All 8 required GitHub CI checks: PASSED (SUCCESS) at the
  implementation head — see below

## Live model/service evidence
- N/A: the order authorizes offline synthetic fixtures only; no live
  inference, no actual client session/capture, no model/GPU/API/Gateway
  call, no Docker host use. Protected fixtures (Qwen/vLLM 18020,
  `qwen-serving`, models/venvs/patches/flags, API-key files,
  firewall/VPN, Codex profiles/auth/config, host network) unchanged:
  NO.

## GitHub CI / required checks
- Implementation head `cd9f4fe4e8b85945142ba4d9cef0de7f5fd953e4`,
  run 39552577518 (final push of this round):
  - `Analyze (actions)` SUCCESS
  - `Analyze (python)` SUCCESS
  - `CodeQL` SUCCESS
  - `docker` SUCCESS
  - `docker-published` SUCCESS
  - `gateway-contract` SUCCESS
  - `operator-session` SUCCESS
  - `test` SUCCESS
- All required green at drafting: YES
- Report-head checks may be pending; strategy verifies.

## Local setup/dependencies
- User `janezp` (non-root; no sudo used); repository `.venv`
  CPython 3.12.15 via `uv`; process-local `umask 022` for the test
  gates (permission fixtures kept at their intended modes); owned
  protected temp roots 0700 under `/home/janezp/tmp`
  (`017l` probe results, `017l-archive.*` git-archive reproduction,
  `017l-wheel.*` fresh wheel venv); no shared host/home permission
  changes; no new dependencies; no repo-local services started.

## Documentation
- Updated (same PR, same round): `docs/CACHE-OBSERVATION-CONTRACT.md`,
  `docs/CACHE-REWORK-LEDGER.md`, `TESTING.md`, `ARCHITECTURE.md`,
  `ARCHITECTURE-for-agents.md` + byte-identical compact mirror
  `oap/strategic-instructions/ARCHITECTURE-for-agents.md`; PR #25 body
  updated with the 017-l round entry and implementation-head evidence
  block.

## Safety/scope confirmations
- Unrelated files: none touched; round diff is exactly the 11 source-A
  files plus the single manifest-B file above.
- Secrets/raw content: none in report or diff — synthetic `tok`
  bearer tokens only; no real keys, private URLs, raw prompts,
  source, tool output, images or customer data; no weights.
- Protected 18020/Qwen/Codex fixture changed: NO.
- Required tests skipped/not run: one real-`chown` environment skip in
  both focused and full gate (never counted passed); D09/D10, the
  process/chunk association collector and all v1 runtime stages remain
  NOT RUN (out of scope).
- Scope deviation: none; no opportunistic refactor/dependency/service/
  migration/architecture/gateway change; no new architecture or
  security exception; no human handoff/plan/frozen release/earlier OAP
  byte change.
- Extra objective PR: NO; coding merge: NO; auto-merge: NO;
  activated order/active edited: NO (committed with exact unchanged
  bytes); final round commit report-only: YES (single changed path
  `oap/reports/017-l-owned-io-and-original-seeds.md`; sole parent =
  implementation head).

## Known limitations/blockers
- The utility remains inert: synthetic-only `fixture_authority:
  none`; generated readiness verdict `not_ready`; actual
  format/process collector, D09/D10 and every v1 runtime stage remain
  NOT RUN. Offline synthetic evidence is not actual-format or
  genuine-client authority.
- One test is a real-`chown` environment skip, not a pass.
- Teardown is bounded: quiesce runs under the utility's existing
  bounded grace; anything left over is honestly reported as
  `cleanup_failed`, never hidden as success.
- K-round history note: K disclosed a pre-activation force-push of
  already-pushed commits; this round's order mandated append-only
  publication and this round complied (two ordinary appends on the K
  SELF; GitHub confirms no further force-pushes).

## Recommended strategic follow-up
- Strategy independently verifies the SELF claims (report commit
  parent = implementation head, remote PR head, report bytes, CI at
  the report head) and the FIFTEEN frozen probes at the final head,
  then decides acceptance for 017-l and the next order (D09/D10 still
  pending on this PR; 018–024 not started). COMPLETE here is a claim
  for that review, not acceptance.

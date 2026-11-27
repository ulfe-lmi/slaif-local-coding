# OAP Coding-Agent Report — 024-f

## Work order
- Identifier: `024-f`; order path `oap/orders/024-f-cache-real-restart-ram-hit-vision.md`; numeric objective 024.
- PR mode: AMENDED_EXISTING_PR (sole PR #32, branch `oap/024-cache-real-codex-qualification`).

## Status
PARTIAL

## Executive summary
One fresh live session against the owner-authorized private
`qwen3.8-27b` A100 Q8 service (checkpoint
`017b9c7af6b5689d5dd426a76e0bc077eb5ca20a`, C=262144, compatibility
`vllm-0.32.0-qwen38-a100-q8`, unchanged pinned tokenizer) closed the
restart and measured steady-path evidence at the exact order caps — six
actual main forwards, four actual compiler dispatches, six POST
attempts, eight-minute window not exhausted, `over_bound=false`.

Phase A ran in a fresh owned candidate process on 127.0.0.1:18031: the
accepted synthetic root bootstrap plus one eligible matched dependency
acquisition through a genuine service-issued call ID and the fixed
synthetic result (no emitted command executed). Both the approved root
and the dependency were compiled, and the protected generation was
committed (A2 recovery stage `published`, session state epoch 1,
generation 3, `resumed=false`). The source-absent steady request then
delivered two compiled blocks with zero compiler calls (stage
`compilation=hit`). Its zero protected recovery-content reads are NOT
directly measured on A: the `RecoverySession.load` counting precedent
was applied to process B in this run (B1 delta 3, B2 delta 0), and A's
"retained" recovery stage fact is the observed classification, not a
load count. Steady-request timing: wall 9723.4 ms, provider 9680.0 ms.

Phase B was an independently spawned second Python process (fresh PID,
parent = driver, distinct from the driver) using the same wheel, the
same trusted synthetic session identity and its protected store, and
the same generated marker key through a protected local reference.
A's serving runtime was stopped (port 18031 refused) while A stayed
alive as orchestrator. B's first ordinary source-absent request
required and showed the actual protected-state read (3 measured
`RecoverySession.load` calls), a new epoch (2, strictly above A2's 1)
and actual restored-entry compiler work for both entries (2 compiler
dispatches, `restored=true`), delivering the rebuilt working set (two
compiled blocks) to the provider (status 200). The immediate steady
replay in B showed zero recovery-content reads (delta 0), zero provider
compiler calls, an unchanged epoch, and byte-identical region digests
(`blocks_match_prev=true`), with status 200. These are bounded timings
for the observed requests; the local non-provider remainder includes
loopback and harness overhead.

The ordered two-image vision request in the second process observed an
actual-provider 400 (provider 7.0 ms; wall 49.2 ms). The
adapter-side transformation was measured correct before the forward:
exactly one retained image item (the newest), old-image omission,
ordinary input order, root wrapper preserved with the raw root removed,
one live marker, two compiled blocks. The request shape records
`input_image` at the top-level input list rather than in a user
message content array; that shape is recorded as a possible
explanation for the 400. The exact upstream error category is
unretained (content-free by design). Actual-model vision completion is
NOT earned.

Two order expectations failed on the preserved live facts: (1) the
whole-body raw dependency-text absence check is false in A2 and A3 —
the actual model's rendered compiled blocks carry the dependency
phrase as compiled content (the 024-d/024-e echo finding); every
carrier-level check (carrier presence, raw-span absence at the carrier,
exact shape, marker counts, tool-item identity and wrapper
preservation) passed. (2) the cross-process rendered-block identity
check is false (B1 rebuilt blocks differ from A3's blocks); separate
real-model compiles in the new epoch are not byte-deterministic, while
the in-process steady replay (B2 vs B1) is byte-identical.

Process-provenance deviation, disclosed: the order requires a fresh
source of the protected reference before each live phase. Phase A was
sourced fresh by the wrapper; the B launch inherited A's freshly
sourced environment exports instead of sourcing in its own launch
shell. After the preserved run, the private harness was corrected
(`spawn_b` live branch now sources the reference in B's own launch
shell with output suppressed, then execs the unchanged B command; the
synthetic branch stays direct-exec and source-free); `py_compile`
clean. No live re-run was performed: the order's live budget is fully
spent and the operator directed preservation without new calls.

Native Codex and native compaction remain a distinct unearned live
gate. No tracked software, docs, dependency or configuration changed;
the transcript commit carries only the activated order and `oap/active`
bytes.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`; PR #32
  `https://github.com/ulfe-lmi/slaif-local-coding/pull/32`, state OPEN.
- Base: `main` @ `fe9538452f7715c305ea2ae9da60726cb73d8d45` (verified
  base; remote main at the same commit).
- Starting remote head: `9ef305351655ed7bc69f7542ea5bc5adc6f028cf`
  (024-e report head; verified prior report/implementation).
- Implementation head SHA: 7354ef71723a8e39eee0af1ec97776d90dba04dd
- Report publication commit: SELF
- Implementation commits pushed before report: the single transcript
  commit `7354ef71723a8e39eee0af1ec97776d90dba04dd` (`024-f:
  activated order and active transcript (unchanged strategic bytes)`;
  staged paths exactly `oap/orders/024-f-cache-real-restart-ram-hit-
  vision.md` and `oap/active`).
- New PR this round: NO; amended existing PR #32: YES; merge
  performed: NO.

## Changes and files
- Tracked: transcript bytes only, sha256-verified unchanged strategic
  bytes (order `e621762b566a1b8e97836fc75ed2a008a96d5d422e23e99d70a486e30e9a9c10`,
  active `3dad5b1c944d697a069daac8b0af78f91cee4eda657af2987c6a41f825aacd60`).
  `git diff --stat 60a3b35425c484169e07b8fa6a291d29da88747d..HEAD --
  src tests docs scripts packaging` is empty.
- Untracked private harness (never committed),
  `work-artifacts/oap-024f-work/`: `harness/fixtures_024f.py`,
  `harness/b_candidate_024f.py`, `harness/driver_024f.py` (including
  the post-run compliance fix to the live `spawn_b` branch described
  above), `harness/run_024f.sh`, `venv/` (Python 3.12.15, exact wheel
  noneditable), `captures/` (content-free run facts).
- The operator's local unstaged `AGENTS.md` wording edit was preserved
  untouched in the linked checkout.

## Acceptance evidence
Content-free per-round facts were persisted (0600) under
`captures/run-6deaf5995e57ac9138b37305dd733a34-live/` (live) and
`captures/run-8d51d515366b24ed61cc9880057ebc8e-synthetic/` (preflight).
No image bytes, secrets, URLs or private call values are retained;
retained-image equality and counts are booleans/counts only.

### Criterion 1 — fresh candidate: bootstrap, acquisition, steady
- A1 (bootstrap + issuance): status 200; 1 main forward; 1 compiler
  dispatch (1 compiled block, root); recovery `cold`→`retained`
  (cold bootstrap committed the protected generation); root carrier
  live marker present, raw root span absent, root wrapper preserved.
  The actual model issued the genuine service-issued `exec_command`
  fixture read (call ID present, fixture read shape verified) —
  issuance prerequisite TRUE; the driver answered with the fixed
  synthetic result without executing any emitted command.
- A2 (acquisition): status 200; 1 main forward; 1 compiler dispatch
  (2 compiled blocks). All carrier checks passed: dependency carrier
  present with exactly one live marker and zero evidence markers, raw
  dependency span absent at the carrier, shape exact, tool call items
  match the issued call, tool-result wrapper preserved. Protected
  generation committed: recovery `steady`→`published`; session state
  after the round: epoch 1, generation 3, `resumed=false`.
- A3 (source-absent steady): status 200; 1 main forward; 0 compiler
  dispatches (stage `compilation=hit`, stage `injection=source_
  absent`, reuse `source_absent_injection`); two compiled blocks;
  zero live/evidence markers. Zero protected recovery-content reads
  are NOT directly measured on A in this run (no counting wrapper);
  the `RecoverySession.load` counting precedent is direct for
  process B below (B1 delta 3; B2 delta 0).
- Steady-request timing (A3): wall 9723.4 ms; actual provider
  exchange 9680.0 ms.
- Whole-body raw dependency-text absence expectation: FAILED in A2
  and A3 (`raw_dep_v1_absent=false`). Explanation: the actual model's
  rendered compiled block carries the dependency phrase as compiled
  content (the 024-d/024-e echo finding). Carrier-level absence at the
  dependency carrier is the earned proof and passed; absence of the
  phrase outside the emitted compiled blocks is not claimed.

### Criterion 2 — independent second process: restart, steady replay
- Process identity: fresh PID 3503728 with parent PID 3502818
  (the driver); distinct from the driver process; birth captured.
  Readiness proven by self-scoped 18031 LISTEN socket-inode ownership
  before the first `/healthz`. A's serving runtime was stopped (port
  18031 refused) while A stayed alive as the orchestrator during B.
- B1 (first source-absent request, fresh process): status 200; 1 main
  forward; 2 compiler dispatches with `restored=true` (both restored
  entries recompiled); measured protected-state read:
  `recovery_loads_delta=3` via the `RecoverySession.load` counting
  wrapper (all 3 on the session lineage); recovery events
  `resumed`+`retained`; reuse `restart_rebuild_new_epoch`; new epoch 2
  strictly above A2 epoch 1; generation 5; two compiled blocks
  delivered to the provider. Wall 28299.1 ms; provider 6279.0 ms.
- B2 (immediate steady replay): status 200; 1 main forward; 0
  compiler dispatches; `recovery_loads_delta=0` (zero recovery-content
  reads); recovery `steady`+`retained`; epoch unchanged (2); region
  digests byte-identical to B1 (`blocks_match_prev=true`). Wall
  3307.3 ms; provider 3267.0 ms. The local non-provider remainder
  includes loopback and harness overhead; these are bounded timings
  for the observed requests.
- Cross-process comparison: `b1_blocks_match_a3=false` (FAILED
  expectation) — B1's rebuilt blocks are byte-different from A3's
  blocks; separate real-model compiles in the new epoch are not
  byte-deterministic (consistent with the 024-d compiled-content-echo
  finding). `b1_epoch_new_vs_a2=true`, `b2_blocks_match_b1=true`,
  `b2_epoch_equals_b1=true`.

### Criterion 3 — two-image vision request in the second process
- B3: actual provider status 400 (provider 7.0 ms; wall 49.2 ms).
  Actual-model completion: NOT EARNED.
- Adapter-side transformation measured correct before the forward:
  `image_item_count=1` (exactly the newest image retained),
  `retained_is_newest=true`, `old_image_absent=true` (distinct
  data-URL equality verified as a boolean), ordinary input order
  preserved (`input_item_shape=["message","message","input_image"]`),
  root wrapper preserved with the raw root removed
  (`root_text_present=true`, `root_body_absent=true`), 1 live marker,
  two compiled blocks, reuse `original_present_ram_reuse`.
- Request shape recorded as a possible explanation for the 400: the
  retained `input_image` item is placed at the top level of the
  `input` list rather than inside a user message content array.
  The exact upstream error category is unretained (content-free by
  design).
- Retained image count: 1; old/new equality: distinct (booleans only);
  no image bytes logged; no real pictures used.

### Caps and bounds (live)
- Main forwards: 6 of 6 (A: 3 of 3; B: 3 of 3); actual compiler
  dispatches: 4 of 4 (A: 2 of 2; B: 2 of 2); POST attempts: 6 of 6.
  `over_bound=false`; eight-minute shared window not exhausted (run
  22:52:44Z–22:53:55Z); no retry, redirect or proxy.
- Main output bounded at 1024 tokens, compiler output at 3000,
  response 256 KiB (never crossed); upstream call bounded at 60 s
  including body.
- Ownership and cleanup proven in both phases: A server stopped and
  port 18031 refused before B; B exit 0, server stopped,
  `loads_total=3` all on the session lineage, transient config
  removed; leak scan over retained files and the transient stderr log
  passed (`leak_check_passed=true`).

## Verification
- `bash run_024f.sh synthetic` (bounded fake-peer two-process
  preflight): PASSED — run `8d51d515366b24ed61cc9880057ebc8e`,
  outcome `PASS`, caps exactly 6 main / 4 compiler / 6 POST attempts,
  B exit 0, leak check passed, both issuance prerequisites, all
  statuses 200. Under the byte-deterministic echo fake the synthetic
  cross-process digests matched (`b1_blocks_match_a3=true`); this
  run qualifies the harness only and is not actual-model evidence.
- `bash run_024f.sh live` (the single authorized live session): run
  ONCE — run `6deaf5995e57ac9138b37305dd733a34`, driver exit 1 with
  the five recorded expectation problems
  (`roundA2-outbound-raw_dep_v1_absent`,
  `roundA3-outbound-raw_dep_v1_absent`, `b-req3-status`,
  `b-req3-driver-status-400`, `cross-process-identity`); all round
  facts preserved content-free. NO live re-run performed (budget
  spent; operator-directed preservation).
- Post-run harness compliance fix (private, never committed): the
  live `spawn_b` branch now sources the protected reference in B's
  own launch shell (output suppressed, never inspected) before
  `exec`-ing the unchanged B command; the synthetic branch stays
  direct-exec and source-free; `py_compile` on all harness modules:
  PASSED.
- Wheel identity: sha256 of
  `oap-024a-work/clean-build-024a-r1/dist/slaif_local_coding-0.1.0-
  py3-none-any.whl` == `e82f5ab8b7fa7833e7fbb5734c7612f81f149d2e6a4aae1e53275004437536d3`
  (verified by the wrapper preflight and inside the driver before any
  round, `wheel_sha256_verified=true`); installed noneditable in the
  fresh 024-f venv, Python 3.12.15.
- `uv run --frozen python scripts/dev_provenance_manifest.py --verify
  --dist dist` (linked checkout): PASSED — `development provenance
  OK: state=development head=9ef305351655`.
- `git diff --check` (linked checkout): PASSED (clean).
- Unchanged-software diff: `git diff --stat
  60a3b35425c484169e07b8fa6a291d29da88747d..HEAD -- src tests docs
  scripts packaging` is empty (transcript-only delta); working tree
  clean except the preserved unstaged `AGENTS.md`. The accepted
  locked/clean-wheel evidence is preserved by unchanged software
  identity; the ten checks at this round's implementation head are
  recorded below.

## Live model/service evidence
- Candidate: one owned 127.0.0.1:18031 process per phase (the exact
  verified wheel, noneditable); readiness proven by self-scoped
  LISTEN socket-inode ownership before the first `/healthz` in each
  phase.
- Upstream: the owner-authorized private service naming the exact
  catalog slug `qwen3.8-27b` (A100 Q8; declared compiler
  `model_revision` `017b9c7af6b5689d5dd426a76e0bc077eb5ca20a`,
  compatibility `vllm-0.32.0-qwen38-a100-q8`, C=262144, unchanged
  pinned tokenizer), reached only through the single injected seam
  (closed origin + path allowlist, caps, no proxy, no retry).
- Protected reference handling: sourced fresh once for the A phase by
  the wrapper with all output suppressed; never inspected, read
  separately, printed or committed; only environment variable names
  appear in retained facts, never values. DEVIATION (disclosed): the
  B phase did not perform its own fresh source and inherited A's
  freshly sourced exports; the harness was corrected after the
  preserved run, and no call was replayed under this order.
- Bounded actual calls: 6 main (`/v1/responses`) + 4 compiler
  (`/v1/chat/completions`); statuses as recorded per round above; the
  fixture (root envelope + synthetic dependency with one eligible
  matched acquisition) is the closed driver fixture, with two
  distinct deterministic 64x64 synthetic PNG data-URLs for the
  ordered one two-image call.
- No new Codex, no temporary handoff, no protected config/service
  change, no gateway, benchmark or release action.

## GitHub CI / required checks
Implementation head `7354ef71723a8e39eee0af1ec97776d90dba04dd`:
- - `test`: completed success (15m41s)
- `gateway-contract`: completed success
- `docker`: completed success
- `docker-published`: completed success
- `operator-session`: completed success
- `cache-native-containment`: completed success
- `cache-native-fixture`: completed success
- `Analyze (actions)`: completed success
- `Analyze (python)`: completed success
- `CodeQL`: completed success
- All required green at drafting: yes
- Report-head checks may be pending; strategy verifies.

## Local setup/dependencies
- Fresh 024-f venv (uv, Python 3.12.15) with the exact wheel
  installed noneditable; the 024-e venv left untouched. No
  dependencies added; no tracked packaging change. No sudo used.

## Documentation
Not required by this order (evidence-only round; no behavior,
configuration, security, test or operational change in tracked
software). The ledger and architecture status advance only on
strategic acceptance.

## Safety/scope confirmations
- Unrelated files: untouched; the operator's unstaged `AGENTS.md`
  preserved byte-identical.
- Secrets/raw content: none retained or emitted; leak scan over all
  retained files and the transient stderr log passed (values compared
  in memory only, boolean result only).
- Production/protected resources: protected 18020/Qwen/Codex fixture
  changed: NO. No gateway mutation. No merge, no auto-merge.
- Required tests skipped/not run: the ordered live scope ran once at
  its full caps; no live re-run (budget spent, operator-directed).
  Extra objective PR: NO. Active/order edited: NO. Report commit
  report-only: yes (this commit changes only the report path).

## Known limitations/blockers
- Whole-body raw dependency-text absence expectations failed in A2
  and A3 by the actual-model compiled-content echo; carrier-level
  absence at each carrier is the earned proof, and carrier-level
  absence of the phrase outside the emitted compiled blocks is not
  claimed.
- A3's zero protected recovery-content reads are not directly
  measured on A (the `RecoverySession.load` counting wrapper was
  applied to process B only); A's steady-state `retained` recovery
  stage fact is an observed classification, not a load count.
- Cross-process rendered-block byte inequality: separate real-model
  compiles in the new epoch are not byte-deterministic; the
  in-process steady replay is byte-identical.
- Vision: actual-model completion not earned (provider 400). The
  top-level `input_image` request shape is recorded as a possible
  explanation; the exact upstream error category is unretained.
- Fresh-source-per-live-phase condition missed for B (inherited A's
  fresh source); harness corrected for future runs; no live re-run
  under this order.
- Native Codex and native compaction remain unearned (distinct live
  gate).

## Recommended strategic follow-up
Factual only; strategy decides. The provider 400 on the two-image
call coincides with the retained image being placed as a top-level
`input_image` item rather than inside a user message content array; a
bounded follow-up could settle which shape the serving model accepts.
For actual-model runs, a whole-body raw-text absence criterion may
need a carrier-scoped formulation given the compiled-content echo
recorded in 024-d/024-e and here.

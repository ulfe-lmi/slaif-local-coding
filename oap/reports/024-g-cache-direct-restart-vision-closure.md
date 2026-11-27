# OAP Coding-Agent Report — 024-g

## Work order
- Identifier: 024-g; order path `oap/orders/024-g-cache-direct-restart-vision-closure.md`; numeric objective 024
- PR mode: AMENDED_EXISTING_PR

## Status
PARTIAL

## Executive summary
One bounded live session ran on the exact unchanged wheel against the private
`qwen3.8-27b` A100 Q8 service and completed all five ordered rounds inside the
exact caps (5 main / 4 compiler / 5 POST attempts; 69 s of the 8-minute shared
window). The two 024-f conditions were closed at the measured level: each live
child launch sourced the protected reference freshly in its own shell and execed
its own candidate (A fully stopped, its PID reaped, and port closure verified
host-wide before B launched), and the nested two-image Responses vision request
completed with the exact newest image retained unchanged, the old image omitted,
and the original text and relative order preserved. B recovered on one
source-absent request into a new epoch (2, strictly above A's 1) with two
restored-entry compiler calls and delivered both rebuilt entries; the immediate
steady replay used the same B working set with zero protected loads and zero
compiler calls. The private driver's final gate exited FAILED on exactly three
leftover whole-body `a_body_present` expectations (rounds A2, B1, B2): the live
compiler's rendered text reproduces the A fixture source inside the injected
compiled region, so a whole-payload text scan finds the fixture string even
though the observed carrier span was replaced. The separately measured
carrier-level and compiled-region observations — the order's actual evidence
scope — hold in every round. The live budget is fully spent (5/5, 4/4, 5/5);
no live replay was performed or authorized, and the round's gate verdict stands
as recorded.

## Authoritative GitHub state
- Repository `ulfe-lmi/slaif-local-coding`; PR #32 state OPEN
  (https://github.com/ulfe-lmi/slaif-local-coding/pull/32)
- Base `main`; head `oap/024-cache-real-codex-qualification`
- Starting remote SHA `b61b2fe6d0c69ca93f11408d144acc18bdea0c83` (024-f report)
- Implementation head SHA: 83e4beb785e7337b7ec5b108513cbaadf368423f
- Report publication commit: SELF
- Implementation commits pushed before report: 1 — `83e4beb` (activated 024-g
  order and `oap/active` transcript; unchanged strategic bytes, verified by
  sha256 against the primary repository before staging)
- New PR this round: no; amended existing: yes; merge performed: NO

## Changes and files
- No tracked software, docs, dependency or test change in this round.
  `git diff --stat 7354ef7..83e4beb -- src tests docs scripts packaging` is
  empty; the full diff from the prior report head is exactly `oap/active`
  (2 +/-) plus the new 79-line 024-g order file.
- `uv run --frozen python scripts/dev_provenance_manifest.py --verify --dist
  dist` → `development provenance OK: state=development head=83e4beb785e7`.
- Narrow private disposable harness only (protected project root
  `work-artifacts/oap-024g-work`, never committed): `harness/candidate_024g.py`,
  `harness/driver_024g.py`, `harness/fixtures_024g.py`, `harness/run_024g.sh`.
  Four scoped harness corrections this round:
  1. the private-append helper's double file-descriptor close (the leftover
     `try` with no handler also broke module parsing; the helper now closes
     exactly once through the stream context);
  2. the nested vision `detail` value corrected from the descriptive word
     `standard` to the schema enum value `auto` in both the request builder and
     the exact retained-item comparison;
  3. a synthetic-phase-only fixed placeholder upstream credential so the dry
     run needs no real credential and inherits no session environment;
  4. the live child launch shell body replaced from a hardcoded positional
     list to `source "$0" >/dev/null 2>&1 || exit 2; exec "$@"`, because
     unbraced `$10`..`$14` expand as `$1` plus a literal digit. The exact
     forwarding was validated before live: all 12 candidate option tokens,
     including the formerly corrupted slots 10–14, arrived exact and in order,
     and a missing `$0` exits 2 with the candidate never executed.

## Acceptance evidence
Private run captures (content-free facts, 0700/0600, never committed) live
under `work-artifacts/oap-024g-work/captures/run-<id>-<phase>/` for run ids
`b0cc5d81aebc54c7882671481b83e406` (synthetic), `7f0b40974a08491cd92fb3edf240cce2`
(synthetic, post-argv-fix) and `4e03090ff594de3383ac18bc27de6525` (live).
All digests below are SHA-256 of rendered regions or configurations.

### Criterion 1 — Fresh candidate A: bootstrap + matching dependency acquisition
- A1 (live, first round): 200, 1 main forward, 1 compiler dispatch; recovery
  events `cold` → `retained`; generation 2; one compiled region
  (`525f995a…d27366`); outbound carries one authenticated live marker, the
  root carrier present with its raw span absent and the wrapper preserved.
- A2 (live, second round): 200, 1 main forward, 1 compiler dispatch; recovery
  events `steady` → `published` (protected generation earned pre-forward);
  generation 3; both validated compiled entries present as two compiled regions
  (`525f995a…d27366`, `8ec2b050…96cdf`). The model issued the dependency read
  with a real call ID; the result carried the fixed synthetic fixture content
  and no emitted command was executed.
- Original carrier replacement measured at the exact coordinates:
  `dep_v1_carrier_present=true`, `dep_v1_carrier_raw_span_absent=true`,
  `dep_v1_carrier_live_marker_count=1`, `dep_v1_carrier_evidence_marker_count=0`,
  `dep_v1_carrier_shape_exact=true`, `tool_call_items_match_issued=true`,
  `tool_result_wrapper_preserved=true`; the root carrier shows the same closed
  facts. `root_body_absent=true` in all five rounds.

### Criterion — A full stop, PID reap, port closure before B
- `a_stop`: exit_code 0, `pid_reaped=true`, `port_connect_refused=true`,
  `port_no_listener_inodes=true` (host-wide inode scan); B's ready record was
  produced only afterwards (born timestamps 00:13:09Z → 00:13:37Z, with the
  stop/reap/closure checks between). Both ready records carry the self-scoped
  18031 LISTEN socket-inode ownership proof taken before the first `/healthz`.
  The coordinator process remained, as permitted.

### Criterion 2 — B: source-absent recovery, new epoch, restored compiles, delivery
- B1: 200, 1 main forward, 2 compiler dispatches (`compile_restored_request=
  true`); session `resumed=true`, epoch 2 (strictly above A2's epoch 1),
  generation 5; `recovery_loads_delta=3` (measured reads from the selected
  protected session); reuse classes `source_absent_injection` +
  `restart_rebuild_new_epoch`; both rebuilt entries delivered as two compiled
  regions (`81cf7a18…5278`, `a72e0a62…a21a7`). Restored identity and admitted
  input matched via the owned state/observations (epoch/generation, reuse
  classes, region count).
- Separately recorded fact, as the order anticipates: the recompilation rendered
  different words — `b1_blocks_match_a2=false` and every B1 region digest
  differs from its A2 counterpart, while the rootless source-absent shape is
  otherwise identical.

### Criterion — B immediate steady replay
- B2: 200, 1 main forward, 0 compiler dispatches, `recovery_loads_delta=0`,
  `blocks_match_prev=true` (byte-identical in-process blocks, same two region
  digests as B1), reuse class `source_absent_injection`, compilation stage
  `hit`. Per-request wall/provider timings preserved in the round captures
  (B1 29 999.9/6 385.0 ms; B2 4 244.0/4 202.0 ms).

### Criterion 3 — Nested two-image vision on the one-image newest-item route
- B3: provider 200, response `completed`, 1 main forward, 0 compiler dispatches.
  Outbound closed facts: `image_item_count=1`, `retained_is_newest=true`,
  `old_image_absent=true`, `image_urls_distinct=true`,
  `retained_item_unchanged=true` (exact item equality including the schema
  `detail` value `auto`), `vision_text_present=true`, `text_before_image=true`,
  plus the two compiled regions retained. The 024-f top-level image-shape 400
  is closed: the nested `content`-array form was accepted by the live
  Responses route.
- The two images are known distinct small synthetic 64×64 PNG data URLs
  (fixture constants, not repeated here).

### Caps and window
- Totals exactly at the ordered caps: 5/5 main attempts-forwards, 4/4 compiler
  dispatches, 5/5 POST attempts; `over_bound=false`, `window_exhausted=false`
  (window 00:13:07Z → 00:14:16Z). Output token caps (1024 main / 3000
  compiler) and the 256 KiB / 60 s per-call bounds were enforced by the
  transport seam; no cap was crossed.

### Fresh per-child source and exec (the 024-f deviation, closed)
- Both live children were launched through the wrapper
  `source "$0" >/dev/null 2>&1 || exit 2; exec "$@"` with the protected
  reference as argv0, output suppressed; the reference was never inspected,
  read separately, or shared between processes. Each child materialized its
  own 0600 live config from its own freshly sourced environment
  (`live_config_removed=true` in both children's final facts); both reached the
  live upstream authenticated (all five mains returned provider 200) and both
  children's stderr leak scans were clean with the transient logs removed.
  The synthetic dry runs carry no real credential at all (fixed placeholder).

### Why the separately measured carrier and compiled-region observations are
### the binding evidence
The driver's failing expectation is a whole-body scan: it tests whether the
complete raw fixture string occurs in ANY decoded string of the outbound
payload. In a working v1 transaction that string cannot survive in the
tool-result carrier — the exact observed span is replaced, and that
replacement is what the carrier facts prove at its own coordinates
(`raw_span_absent`, one authenticated live marker, exact shape, wrapper
preserved, issued-call match). The injected compiled region, however,
legitimately contains whatever the pinned compiler model renders from that
source ("the recompilation can render different words" — and in this live run
the model's A rendering reproduces the source text). The 024-f live evidence
already established that whole-body presence/absence is confounded by compiled
content echo and is not a valid claim at this layer; the order's own scope is
carrier-level replacement plus protected generation, which is exactly what the
carrier and region observations measure. Note the asymmetry that bounds the
claim: the raw ROOT text was never echoed (`root_body_absent=true` in all five
rounds), so the scan's positive is specific to the compiled A region.

## Verification
- `bash run_024g.sh synthetic` (run `b0cc5d81…`): PASSED — driver outcome
  PASS, 5/5 main, 4/4 compiler, 5 POST, A stop/reap/port-closed, B1 epoch 2
  with 2 restored compiles, B2 zero-load/zero-compile byte-identical replay,
  B3 nested-vision success facts, leak scans clean.
- `bash run_024g.sh synthetic` (run `7f0b4097…`, after the live-launch argv
  correction): PASSED — identical closed facts; the post-edit dry path is the
  harness qualification for the live launch.
- Live launch argument-forwarding validation (inert source script, argv echo
  at the candidate position): PASSED — all 12 option tokens exact and in
  order including former slots 10–14; missing source script exits 2 with no
  candidate execution.
- `bash run_024g.sh live` (run `4e03090f…`): RAN to completion; all five
  rounds completed with the measured facts above; driver final gate FAILED
  with `round_problems = [roundA2-outbound-a_body_present,
  b-req1-outbound-a_body_present, b-req2-outbound-a_body_present]` — the three
  leftover whole-body expectations analyzed in the section above. The driver's
  stderr log was leak-scanned clean and removed by the wrapper.
- `git diff --stat 7354ef7..83e4beb -- src tests docs scripts packaging`:
  empty (no tracked code/docs/dep/test change).
- `uv run --frozen python scripts/dev_provenance_manifest.py --verify --dist
  dist`: PASSED (`development provenance OK: state=development
  head=83e4beb785e7`).
- Order/active byte verification: sha256 of both mirrored files equals the
  primary repository bytes (`f41e9f50…` order, `630efb33…` active).

## Live model/service evidence
- Service: private `qwen3.8-27b`, A100 Q8, checkpoint
  `Qwen/Qwen3.8-27B-FP8` commit
  `017b9c7af6b5689d5dd426a76e0bc077eb5ca20a` (the declared compiler
  model_revision), context 262144, compatibility
  `vllm-0.32.0-qwen38-a100-q8`, separately pinned tokenizer revision.
  No endpoint, credential, URL or key appears in this report or in any
  retained fact.
- Bounded calls: 5 main POSTs (A1, A2, B1, B2, B3) and 4 compiler dispatches,
  all provider 200; B3 response `completed`. Same origin and allowed paths
  only; no proxies, redirects or raw smoke.
- No provider credential was shared with any client process; no client
  handoff, no second Codex, no native compaction, no profile/service mutation,
  no gateway interaction.

## GitHub CI / required checks
- Implementation head `83e4beb785e7337b7ec5b108513cbaadf368423f`: all ten
  checks PASSED and independently re-verified — CodeQL, Analyze (actions),
  Analyze (python), cache-native-containment, cache-native-fixture, docker,
  docker-published, gateway-contract, operator-session, test (runs
  45915877041 / 45915872018).
- All required green at drafting: yes.
- The report-only push may trigger new checks at the report head; strategy
  verifies.

## Local setup/dependencies
- Exact unchanged wheel
  `e82f5ab8b7fa7833e7fbb5734c7612f81f149d2e6a4aae1e53275004437536d3`
  installed noneditable in a Python 3.12.15 venv
  (`work-artifacts/oap-024g-work/venv`); wheel sha256 re-verified by the
  runner before each launch and recorded in the run facts.
- Candidate served on 127.0.0.1:18031 with owned LISTEN socket-inode proof;
  the fake peer (synthetic phase only) on 127.0.0.1:18032; both released and
  verified closed after each phase.
- Protected per-session recovery store under the private run directory,
  shared by the two owned candidate processes; the synthetic marker key is
  driver-generated per run; the live marker key came from the same protected
  environment-reference mechanism.
- No sudo actions; no durable docs/config change; the transient live configs
  were removed at exit (`transient_config_removed=true`).

## Documentation
- Not required: no tracked behavior, configuration, security, test or
  operational change in this round (order scope is direct evidence only).

## Safety/scope confirmations
- Unrelated files: the only working-tree change in the linked checkout is the
  operator's local `AGENTS.md` wording, preserved UNSTAGED and uncommitted.
- Secrets/raw content: none in this report, commits or retained facts; both
  live children's stderr leak scans clean; provider error bodies never
  printed or persisted (the B3 success branch was taken, so no refusal
  category was needed).
- Protected 18020/Qwen/Codex fixture changed: NO (the protected reference was
  only sourced inside the two child launch shells with output suppressed,
  exactly as ordered).
- Required tests skipped/not run: no tracked tests were in scope (no tracked
  change); the 024-g evidence is the live session plus the synthetic
  preflight, both run.
- Extra objective PR: NO; coding merge: NO; active/order edited: NO
  (committed bytes verified identical to the strategic originals).
- Scope deviation: none; the only failed gate is the private driver's
  leftover whole-body expectation (documented above), not an adapter
  behavior.

## Known limitations/blockers
- The driver's final verdict is FAILED solely on the three whole-body
  `a_body_present` expectations; the live budget is spent (5/5, 4/4, 5/5), so
  the verdict stands for this round and cannot be re-run. The binding
  carrier/region-level evidence is preserved in the run captures.
- Genuine Codex and native compaction remain pending separate client
  authorization (explicitly out of 024-g scope).

## Recommended strategic follow-up
Factual only: the private driver's whole-body `a_body_present` expectation is
leftover 024-f machinery invalidated at this layer by compiled-content echo
and is contradicted by its own carrier facts when the live model echoes
source text; scoping that check to the carrier span (or retiring it) would let
a future same-PR round re-run the matrix if the live budget is re-authorized.

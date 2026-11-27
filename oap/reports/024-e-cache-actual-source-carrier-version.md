# OAP Coding-Agent Report — 024-e

## Work order
- Identifier: `024-e`; order path `oap/orders/024-e-cache-actual-source-carrier-version.md`; numeric objective 024.
- PR mode: AMENDED_EXISTING_PR (sole PR #32, branch `oap/024-cache-real-codex-qualification`).

## Status
COMPLETE

## Executive summary
The 024-d whole-body substring scan could not localize the dependency text,
because the actual compiler's rendered blocks can carry the source phrase as
compiled content. This round closed that exact gap: the new
carrier-attributed checks identify each original carrier location by its own
decoded position (the root envelope text item; the `function_call_output`
bound to the exact issued call ID) and prove span replacement and original
absence at those locations separately from any whole-body phrase scan. The
already-approved actual source-change/replay criterion was then exercised in
one fresh live session against the owner-authorized private `qwen3.8-27b`
A100 Q8 service, reusing the 024-d installed-wheel private driver with local
disposable edits only. All five serial rounds passed with the exact caps:
five candidate POST attempts, four actual main forwards, three actual
compiler calls; the stale transformed-body replay observed the typed 409
with zero provider forwards and zero compiler calls; the source-carrier-
removal round carried the current v2 blocks byte-identically with zero
compiler calls. No tracked product, docs, tests or dependencies changed; the
transcript commit carries only the activated order and `oap/active` bytes.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`; PR #32
  `https://github.com/ulfe-lmi/slaif-local-coding/pull/32`, state OPEN.
- Base: `main` @ `fe9538452f7715c305ea2ae9da60726cb73d8d45` (verified base).
- Starting remote head: `a453979e0dfa24983385005ffdb53b693e18b4c9`
  (024-d report head, all ten checks green at its parent).
- Implementation head SHA: 60a3b35425c484169e07b8fa6a291d29da88747d
- Report publication commit: SELF
- Implementation commits pushed before report: the single transcript commit
  `60a3b35425c484169e07b8fa6a291d29da88747d`
  (`024-e: activated order and active transcript (unchanged strategic
  bytes)`; staged paths exactly `oap/orders/024-e-cache-actual-source-
  carrier-version.md` and `oap/active`).
- New PR this round: NO; amended existing PR #32: YES; merge performed: NO.

## Changes and files
- Tracked: transcript bytes only (order + active, sha256-verified unchanged
  strategic bytes: order `d01971fa3df8742cb3c56944e9ea3799f676bffcfe670448585f868e9d9e5545`,
  active `355cf87dcfe2815866b1979385f459fcc3aa37efb5346756a5e58855278a513f`).
- Untracked private harness (never committed):
  `work-artifacts/oap-024e-work/harness/driver_024e.py`
  (024-d driver with the locally disposable 024-e edits: the carrier-
  attributed `carrier_facts` checks, the A-v2 fixture, the fresh re-read
  request item, the fake peer's second distinct issuance, the five-round
  sequence and expectations, caps 4 main / 3 compiler / 5 POST attempts)
  and `harness/run_024e.sh` (024-d wrapper with the round path/marker
  renames; launcher and transport unchanged).
- The operator's local unstaged `AGENTS.md` wording edit was preserved
  untouched in the linked checkout.

## Acceptance evidence
Content-free per-round facts were persisted atomically (0600) before each
round proceeded; the durable private captures live under
`work-artifacts/oap-024e-work/captures/run-<id>-<phase>/` (live run
`run-2a6cdda816c1aedd4aa7643f1138f6a0-live`; synthetic preflight
`run-6321f040d84e0d0653487685df3cd9b3-synthetic`; the calibration-iteration
capture `run-7697fd138d83b2ca328be2a730226efa-synthetic` is retained as the
recorded pre-fix iteration). No raw on-wire body, private path, credential
or call ID is retained; the transient driver stderr log was leak-scanned
against the sourced values and removed.

### Round 1 — bootstrap and actual issued read (live 200)
- One actual main forward, one actual compiler call (root compile), stage
  facts: recognition `root`, acquisition `replayed`, graph/admission
  `ready`, compilation `completed`, replacement `ok`, injection `compiled`,
  main upstream `provider_accepted`, recovery `retained`.
- Carrier check at the exact root text carrier: original root span absent at
  the carrier location, exactly one live marker present, envelope framing
  (`# AGENTS.md instructions for /work` header and `</INSTRUCTIONS>` tail)
  preserved byte-for-byte outside the replaced span.
- Outbound compiled blocks: exactly one (selected root); whole-body phrase
  facts recorded separately (both absent).
- Response: the service issued exactly one `exec_command` fixture read
  (`cmd_is_fixture_read`, name/call-id/arguments facts all true); the call ID
  was carried in memory only.

### Round 2 — A-v1 acquisition, carrier checks, fresh re-read request (live 200)
- One actual main forward, one new actual compiler call (A-v1; total 2);
  acquisition `accepted`, replacement `ok`, recovery `published`.
- The exact root text carrier and the matching `function_call_output` were
  checked separately: at the A-v1 carrier location the original span is
  absent and exactly one live marker is present with the proven frame
  wrapper prefix preserved; the unaffected root/tool wrapper and the issued
  `function_call` item are preserved (the outbound call item is dict-equal to
  the in-memory issued item; exactly one matching result bound to the issued
  call ID with the frame prefix intact).
- Emitted blocks: root block byte-identical to R1's root block; a new A-v1
  compiled block present (two blocks total, two live markers).
- A matching phrase in rendered context is recorded separately from carrier
  retention (both phrase facts false in this round).
- The fresh re-read was explicitly requested in this round (a distinct user
  item after the A-v1 result); the service's response issued exactly one
  further fixture read with a genuine DISTINCT call ID (prerequisite true,
  carried in memory only).

### Round 3 — A-v2 version change (live 200)
- Full predecessor history preserved; one actual main forward and exactly
  one new actual compiler call carrying A-v2 (total 3 — the cap).
- Carrier checks: the obsolete A-v1 carrier is marked with the non-resolving
  evidence marker (one evidence marker, zero live markers, original A-v1
  span absent at that location, frame prefix preserved); the A-v2 carrier's
  recognized span is replaced by a live marker (one live marker, original
  A-v2 span absent, frame prefix preserved); the root carrier stays live
  with its framing preserved; both issued call items and both result
  wrappers are preserved.
- Block facts: the root block is byte-stable (byte-identical to R2's root
  block); the obsolete A-v1 rendered block is withdrawn (not present among
  R3's regions); a new A-v2 block is present (two blocks total: 2 live
  markers, 1 evidence marker).
- Recorded separately: the actual compiler's A-v2 rendered block carries the
  A-v2 phrase as compiled content, so the whole-body absence fact is false
  in this round by design; the carrier-location facts above are the earned
  removal proof (this is the exact 024-d gap, now localized).

### Round 4 — stale transformed-body replay (live 409)
- The R2 transformed outbound body (retained in memory) was resubmitted from
  the same session. The existing marker-side replay law refused it with the
  typed 409: the A-v1 carrier's live marker is stale after the R3 version
  change.
- Directly observed: zero provider forwards in the round and zero compiler
  calls (main-forward count and compiler-attribution both unchanged across
  the request; no new main record on the seam).

### Round 5 — source carriers removed (live 200)
- A continue-only round with no source carriers. Outbound selected working
  set: two compiled blocks byte-identical, in order, to R3's current v2
  blocks (root + A-v2) — adapter history reduction, zero compiler calls
  (compilation stage `hit`, injection stage `source_absent`, reuse class
  `source_absent_injection`).
- No live or evidence markers, no tool items, no carriers present.

### Caps and bounds (live)
- Candidate POST attempts: 5 of 5; actual main forwards: 4 of 4; actual
  compiler calls: 3 of 3. Each response bounded at 256 KiB (never crossed);
  each upstream call bounded at 60 s including body; 8-minute live window
  not exhausted; no retry, redirect or proxy; no extra raw smoke.
- Main output bounded at 1024 tokens, compiler output at 3000 (config).

## Verification
- `bash run_024e.sh synthetic` (fake-peer preflight, exact case): PASSED —
  all five rounds, zero problems, identical caps, both issuance
  prerequisites, leak check passed, cleanup verified. The new checks were
  established against both the presence and the absence of synthetic
  carriers (transformed carriers in R2/R3, carrier-less R5, stale-marker
  refusal in R4). A calibration-iteration capture
  (`run-7697fd13…-synthetic`, one driver-side wrapper-check defect) is
  retained; the post-fix run is the passing preflight.
- `bash run_024e.sh live` (the single authorized live session): PASSED —
  outcome `PASS`, rounds [1,2,3,4,5], round problems none, leak check
  passed, cleanup verified (server stopped, port 18031 refused, transient
  config removed).
- Wheel identity: sha256 of
  `oap-024a-work/clean-build-024a-r1/dist/slaif_local_coding-0.1.0-py3-none-any.whl`
  == `e82f5ab8b7fa7833e7fbb5734c7612f81f149d2e6a4aae1e53275004437536d3`
  (verified again by the wrapper preflight and inside the driver before any
  round); installed noneditable in a fresh 024-e venv, Python 3.12.15.
- `uv run --frozen python scripts/dev_provenance_manifest.py --verify --dist dist`
  (linked checkout): PASSED — `development provenance OK:
  state=development head=a453979e0dfa`.
- `git diff --check` (linked checkout): PASSED (clean).
- Unchanged-software diff: `git diff --stat 7da4fa549dd54f4ec96517e67962c112716be7f2..HEAD -- src tests docs scripts packaging` is empty
  (transcript-only delta); working tree clean except the preserved unstaged
  `AGENTS.md`. Accepted locked checks and artifact proof are therefore
  reused by identity, and the ten checks at this round's implementation head
  were obtained below.

## Live model/service evidence
- Candidate: one owned 127.0.0.1:18031 process (the exact verified wheel,
  noneditable); readiness proven by self-scoped LISTEN socket-inode
  ownership before the first `/healthz`.
- Upstream: the owner-authorized private service naming the exact catalog
  slug `qwen3.8-27b` (A100 Q8; declared compiler `model_revision`
  `017b9c7af6b5689d5dd426a76e0bc077eb5ca20a`, compatibility
  `vllm-0.32.0-qwen38-a100-q8`, C=262144, unchanged pinned tokenizer),
  reached only through the single injected seam (closed origin + path
  allowlist, caps, no proxy, no retry). The protected reference was sourced
  fresh once with output suppressed; it was never inspected, read
  separately, printed or committed; endpoint/key names only appear in the
  environment, values never emitted.
- Bounded actual calls: 4 main (`/v1/responses`) + 3 compiler
  (`/v1/chat/completions`); all statuses as recorded per round above; the
  fixture (root envelope + two-version `docs/A.md` synthetic dependency) is
  the closed driver fixture, unchanged from its 024-d form except the
  A-v2 constant and the re-read request item.
- No new Codex, no temporary handoff, no protected config/service change,
  no gateway, benchmark or release action.

## GitHub CI / required checks
Implementation head `60a3b35425c484169e07b8fa6a291d29da88747d`:
- `test`: completed success
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
- Fresh 024-e venv (uv, Python 3.12.15) with the exact wheel installed
  noneditable; the 024-d venv left untouched. No dependencies added; no
  tracked packaging change. No sudo used.

## Documentation
Not required by this order (evidence-only round; no behavior, configuration,
security, test or operational change in tracked software). The ledger and
architecture status advance only on strategic acceptance.

## Safety/scope confirmations
- Unrelated files: untouched; the operator's unstaged `AGENTS.md` preserved.
- Secrets/raw content: none retained or emitted; leak scan over all retained
  files and the transient stderr log passed (values compared in memory only,
  boolean result only).
- Production/protected resources: protected 18020/Qwen/Codex fixture
  changed: NO. No gateway mutation. No merge, no auto-merge.
- Required tests skipped/not run: none for this round's scope. Extra
  objective PR: NO. Active/order edited: NO. Report commit report-only: yes
  (this commit changes only the report path).

## Known limitations/blockers
- The whole-body raw-absence facts remain false in R3/R5 by design: the
  actual compiler's rendered A-v2 block carries the A-v2 phrase as compiled
  content. Carrier-location absence (the order's criterion) is the earned
  proof; carrier-level absence of any phrase outside the emitted compiled
  blocks is not claimed.
- Native Codex compaction, process restart and vision remain later
  objective-024 evidence (unearned, unchanged).
- R4 proves the marker-side stale-reference refusal at the app boundary for
  the version-changed session; it is a refusal observation, not a forward.

## Recommended strategic follow-up
Factual only; strategy decides: the 024 carrier/version criterion now has
direct live evidence in a single fresh session; remaining objective-024
unearned stages are native compaction, process restart and vision, plus
genuine-client (genuine Codex) qualification per the order lineage.

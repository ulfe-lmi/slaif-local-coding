# OAP Coding-Agent Report — 024-d

## Work order
- Identifier: 024-d; order path: `oap/orders/024-d-cache-actual-dependency-bundle-transaction.md` (sha256 `0a9ab54f…0baf`, byte-verified copy); numeric objective: 024
- PR mode: AMENDED_EXISTING_PR (PR #32, branch `oap/024-cache-real-codex-qualification`)

## Status
PARTIAL

## Executive summary
The bounded LIVE installed-wheel dependency-bundle transaction ran as one
in-process pass-through (no relay): the exact verified development wheel
(noneditable, Python 3.12.15) under the actual `create_app` entry point on
127.0.0.1:18031, with ONE injected httpx transport seam as the single
upstream channel for both the main client and the v1 compiler client.
The synthetic dry exchange (all four rounds, same wrapper/stream path)
passed before any live call. The live session consumed its exact caps
(four main forwards, two compiler calls) and measured every ordered
transaction stage: the real model's fixture-read issuance, one validated
root compile, actual dependency admission with validated compiler work,
two compiled blocks with two live replacement markers, a byte-identical
stable replay with zero compiler dispatches, and source-absent reinjection
carrying the same two rendered blocks with zero compiler dispatches.
The whole-body dependency-absence assertion FAILED in R2/R3/R4. The
R4 occurrence (input with no source carriers, rendered blocks
byte-identical to R2) shows the whole-body scan cannot attribute
detected text to an original carrier; compiler content echo is a
possible explanation for the whole-body presence, but the harness did
not localize the occurrence in R2. Carrier-level absence is
therefore UNPROVEN (not directly measured; the outbound bodies were never
retained, by design). The accepted 024-c raw smoke was not repeated; no
consumed call was replayed.

## Authoritative GitHub state
- Repository: ulfe-lmi/slaif-local-coding; PR 32, OPEN, MERGEABLE, base `main`
- Starting remote SHA: `b62a10b2fd352f5a58b4394636f5b7e957d2ecc0`
- Implementation head SHA: 7da4fa549dd54f4ec96517e67962c112716be7f2
- Report publication commit: SELF
- Implementation commits pushed before report: the 024-d transcript commit (exact activated order + `oap/active` strategic bytes, sha256-verified against the primary; two paths only)
- New PR this round: NO; amended existing: YES; merge performed: NO

## Changes and files
No product, test, docs or dependency changes (qualification of unchanged
software). The disposable harness (`harness/driver_024d.py`,
`harness/run_024d.sh`) and all captures are private under
`work-artifacts/oap-024d-work/` and are not committed. The transcript
commit changes `oap/active` and the new order file only.

## Acceptance evidence
### Criterion 1 — synthetic dry exchange (pre-live)
- `run_024d.sh synthetic`: PASSED (exit 0). All four rounds 200; caps
  exact (4 main, 2 compiler); R1 issuance classification all true; R2
  dependency admission + second compile; R3 byte-identical outbound
  (in-memory comparison) with zero dispatches; R4 two rendered blocks
  byte-identical to R2's with zero dispatches; per-round content-free
  JSON persisted (0700/0600); leak check passed; transient config
  removed.

### Criterion 2 — live bootstrap, issuance, root compile
- R1 (live): 200; one main forward; one actual compiler call; stage
  `compilation=completed`, `replacement=ok`, `injection=compiled`;
  outbound: 1 compiled block, 1 live marker, root raw span absent
  (whole-body scan, sound for this round's root block); response
  classification: exactly one `exec_command` fixture read issued by the
  real model (all four closed booleans true); the validated issued call
  was kept in memory for the R2 submission.

### Criterion 3 — live dependency acquisition (the 024-c gap)
- R2 (live): 200; one main forward; one actual compiler call (total 2);
  stages `acquisition=accepted`, `admission=ready`,
  `compilation=completed`, `recovery=published`, `replacement=ok`;
  outbound: 2 compiled blocks, 2 live markers, root raw span absent,
  tool call + tool output items present (1/1). Tool-envelope booleans
  (in-memory): the outbound `function_call` item is dict-equal to the
  exact item the service issued in R1 (call identity/name/arguments
  unchanged), and exactly one `function_call_output` item is bound to
  that issued call ID — the fixed synthetic dependency result is bound
  to its genuine issued call, which the 024-c driver could not do.
- Whole-body dependency-absence assertion: FAILED (recorded in
  `round_problems` for R2/R3/R4). See Criterion 6 for the precise
  limitation.

### Criterion 4 — live replay
- R3 (live): 200; one main forward; zero compiler dispatches for the
  request; outbound byte-identical to the R2 outbound (in-memory
  comparison, boolean recorded); stage `reuse_class=original_present_
  ram_reuse`. Replay input: the SAME admitted original input resent
  (the R2 input; the 024-c `own_original_r2_resend` precedent).

### Criterion 5 — live source-absent reinjection
- R4 (live): 200; one main forward; zero compiler dispatches; stage
  `injection=source_absent`, `reuse_class=source_absent_injection`;
  outbound working set carries the required compiled root and dependency
  as two rendered blocks byte-identical to the R2 blocks (in-memory
  ordered comparison, boolean recorded). Adapter history-reduction
  evidence; native compaction remains pending.

### Criterion 6 — absence assertions (precise limitation)
- The whole-body scan checks exact original spans against ALL decoded
  JSON string values of the outbound body and cannot attribute an
  occurrence to an original carrier versus compiled-block content.
- The live R2/R3/R4 `raw_dep_absent` assertions are recorded FAILED.
  Compiler content echo in the rendered compiled block is a possible
  explanation for the whole-body presence (the R4 occurrence, with no
  source carriers in the input and rendered blocks byte-identical to
  R2, is consistent with it); the harness did not localize the
  occurrence in R2, so this round neither proves a carrier leak nor
  excludes one.
- Carrier-level absence of the two original spans in the live outbound
  is UNPROVEN: it was not directly measured (no span-attributed check),
  and the outbound bodies were never retained (content-free by design),
  so it cannot be measured from this run's retained data either.
- The synthetic dry run's whole-body absence assertions passed and
  remain valid at the echo-compiler scope only.

### Criterion 7 — caps and cleanup
- Live caps consumed exactly: 4/4 main forwards, 2/2 compiler calls;
  no response over the 256 KiB bound; no window exhaustion (8-minute
  window from wrapper start); no proxy, no retries (single transport,
  `retries=0`); 60 s per provider call enforced across headers, body
  iteration and close by the seam.
- Cleanup: candidate stopped, 18031 refused, transient config removed,
  transient driver stderr log leak-scanned against the sourced values
  (in memory only) and removed; protected recovery store and the
  per-round content-free facts retained under the private work root
  (0700/0600); leak check passed (no protected value in any retained
  file).

## Verification
- `work-artifacts/oap-024d-work/harness/run_024d.sh synthetic`: PASSED (exit 0; four rounds, per-round persistence, caps exact)
- `work-artifacts/oap-024d-work/harness/run_024d.sh live`: FAILED on the recorded whole-body absence assertions (exit 1; all other stages measured, caps exact) — see Criterion 6
- `uv run --frozen python scripts/dev_provenance_manifest.py --verify --dist dist` (at implementation head 7da4fa5): PASSED — `development provenance OK: state=development head=7da4fa549dd5`
- `git diff --check fe9538452f7715c305ea2ae9da60726cb73d8d45..b62a10b2fd352f5a58b4394636f5b7e957d2ecc0`: PASSED (clean)
- Wheel identity: the installed wheel's SHA-256 equals the order's exact value `e82f5ab8b7fa7833e7fbb5734c7612f81f149d2e6a4aae1e53275004437536d3` (verified by wrapper and driver before any call)

## Live model/service evidence
- Service: the owner-authorized private raw service (endpoint and
  bearer carried only in the sourced protected environment references;
  never emitted). Served model `qwen3.8-27b` on A100 Q8
  (checkpoint `Qwen/Qwen3.8-27B-FP8` at
  `017b9c7af6b5689d5dd426a76e0bc077eb5ca20a`, the exact declared
  compiler `model_revision`; compatibility identity
  `vllm-0.32.0-qwen38-a100-q8`); the separately pinned tokenizer
  revision is unchanged (bound in the wheel).
- Bounded calls: 4 main Responses forwards (store=false,
  max_output_tokens=1024) and 2 compiler chat calls (max
  3000 tokens); every round status 200; fixture unchanged (synthetic
  root/dependency fixture only; no emitted command executed).
- The accepted 024-c raw smoke was NOT repeated.

## GitHub CI / required checks
- Implementation head 7da4fa549dd54f4ec96517e67962c112716be7f2, run 45883756933 — all ten checks SUCCESS:
  - `test`: success; `gateway-contract`: success; `docker`: success;
    `docker-published`: success; `operator-session`: success;
    `cache-native-containment`: success; `cache-native-fixture`: success;
    `Analyze (actions)`: success; `Analyze (python)`: success; `CodeQL`: success
- All required green at drafting: yes
- Report-head checks may be pending; strategy verifies

## Local setup/dependencies
- Fresh wheel-only noneditable venv (Python 3.12.15, uv) under the
  private work root, bound to the exact verified wheel; no torch, no
  model loading, no image decoding; no global state touched; no sudo
  used.

## Documentation
Not required: no product, test, docs, configuration, security or
operational behavior changed by this round (qualification of unchanged
software).

## Safety/scope confirmations
- Unrelated files: preserved; the operator's local unstaged `AGENTS.md` wording edit remains unstaged and byte-untouched
- Secrets/raw content: none emitted or retained (content-free facts only; leak check passed on every retained file)
- Production/protected resources: no client handoff, no new Codex, no native handoff, no profile or service mutation, no gateway, no benchmark, no release; protected 18020/Qwen/Codex fixture changed: NO
- Required tests skipped/not run: none skipped; the native-compaction case remains PENDING (adapter history-reduction only)
- Scope deviation: none
- Extra objective PR: NO; coding merge: NO
- Active/order edited: NO (byte-verified copies); report commit report-only: YES

## Known limitations/blockers
- Carrier-level absence of the two original source spans in the live
  outbound is UNPROVEN (Criterion 6); the whole-body absence heuristic
  is unsound at real-model scale where compilation may quote source
  text into the rendered block.
- The 024-c driver evidence gap is closed for the measured stages
  (retained issued-call submission, per-round content-free persistence,
  actual outbound-body observation) but the span-removal clause of
  round 2 is not earned at the real-model scale by this run.
- Live compiler dispatch count is evidenced by the seam (2 provider
  calls) and by the per-request stage attributions (1+1); per-block
  entry-identity attribution inside the rendered blocks was not
  separately recorded.

## Recommended strategic follow-up
Factual only: a future authorized round could add a span-attributed
absence check (per-string-value carrier attribution with the rendered
region excluded) to the private harness to earn carrier-level absence
directly. Strategy decides.

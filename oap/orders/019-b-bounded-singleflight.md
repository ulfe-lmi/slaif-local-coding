# OAP work order — 019-b: bounded async single-flight and attempt ownership

AMEND_EXISTING_PR, numeric019, round019-b. NO NEW PR. Exact PR27 https://github.com/ulfe-lmi/slaif-local-coding/pull/27, branch oap/019-cache-ram-state, base main c5eb299df822875988867bf34d58de239e82657e, verified current remote report head845e9e763446d47c53e0695d84df7574d517536a. All TEN exact SELF checks SUCCESS. Source A3d3f79c85d6618206d9ea0d22b9fb9b66b80f3da, manifest-only Bc3cfc79398e6e1cd6d3bc847edf0ca8256ceb5f6. No merge/auto-merge/next-ID choice by coding.

Read S/reviews/019-a-decision.md and immutable019-a report completely; preserve all corrections and process qualifications.019-a is ACCEPTED only at INERT RAM owner/store foundation scope, not whole019. Whole018 remains accepted at complete INERT graph/currentness/admission scope, merged main c5eb299 under018-t decision. Do not repeat the closed018 audit or add discretionary requirements, planning documents or audit machinery. Fixed human CACHE-REWORK requirements and existing acceptance criteria remain unchanged.

Activation requires published exact order+active019-b and ONE valid controlOK. Current actual coding next-control reader48601, PID3250492/birth339563448/PPID3250482/UID1001, source W19a/next-control-reader-019-v1.py700 SHA895599bbb141a44f7ed5d0e6ec2173c4e57bd23b7b018d3dc5c28ad51db2229e; original controldev2304/inode10648021/UID1001/0600, responseinode10648022. Actual reader startup0002 is a preserved qualification, not a reason to restart it. Poll ONLY your48601; after valid receipt read active/order, no second control read.15365 is SPENT; root35881 SPENT. ROOT creates ONE new response reader before activation. No replay. Continue SAME RIGHT%19 early-beta/xhigh worker. No other Codex/client/subagent startup, including CI or disposable tests. Only verified crash permits restart in RIGHT with exactly codex --yolo --profile early-beta. Idle/compaction/queued tool wait is not a crash.

## Objective and boundaries

Implement the second cohesive INERT019 slice: async same-full-key single-flight, bounded leader/queue/waiter/attempt ownership, declared no-retry lifecycle, cancellation and owner/source/epoch publication fences over the ACTUAL019-a registry/owners and ACTUAL018-p/018-t records. Use an injected bounded async work seam to prove orchestration; actual compiler/tokenizer semantic validation belongs021. Whole019 pressure/source-scale/lifecycle closure remains a following same-PR round; no merge after this slice alone.020–024 remain required. Keep legacy pipeline unchanged and v1 inactive.

Read governance in required order, both architecture maps, SECURITY/TESTING, approved CACHE-REWORK and implementation plan, existing RAM contract and applicable nested instructions before edits. Reconcile remote PR/head/checks and preserve unrelated work. Existing inert attempt lifecycle/decision aids are context, not additional active scope. This order explicitly resolves their policy below. Routine cohesive implementation choices belong to coding; stop only for genuine architectural incompatibility, not ordinary interface design.

## Ratified attempt policy for this slice and subsequent021 integration

Full semantic content/configuration key and genuine live cache epoch define ONE admitted work attempt. Attempt state is separate from valid immutable prepared payload and current source selection. A later request, requestID/nonce, revision, new output directory, insertion pressure or missing valid entry never authorizes retry. There is no public reset header/tool, timed retry, best-of prompt, hidden original fallback or main-request replay.

Precisely separate pre-admission refusal from atomic claim. Before a claim, resource/concurrency queue admission may reject503 with zero invocation and no attempt. Once a bounded key reservation is accepted (including a queued reservation), the attempt is claimed; cancellation before dispatch still terminates that admitted attempt, with zero actual invocation. No silent release-and-retry loophole. Tests distinguish these boundaries and record invocation counts. Metadata for terminal failures remains bounded/charged until explicit teardown; never evict it to retry.

After claim, concurrent identical demand joins ONE shared operation/outcome. A single waiter cancellation detaches that waiter without cancelling another live waiter's work. All waiters gone cancels AND awaits owned work, leaves a terminal unsuccessful attempt. Exception, timeout, invalid/truncated/over-budget output and cancellation after claim never become valid payloads or hits. Later same-key/epoch demand gets the same fixed typed failure without another invocation: infrastructure/resource503, invalid/budget422, currentness conflict409. No raw exception content. Failure of one key must not poison unrelated keys/sessions.

A genuinely distinct semantic key may receive its own attempt. A valid A1 payload survives A2 supersession and can be reused on a genuinely proven compatible A1 revert without a third invocation. For FAILED A1→A2→genuinely new A1 revert in the SAME epoch, the original failed A1 attempt still applies: causal change alone does not reset the identical full key's attempt. Replay/equal-byte witnesses never reset either. Document this availability tradeoff honestly. Only an actual explicit teardown/new ownership lifetime or authenticated restart/recovery under020 creates a genuine new epoch; never manufacture epochs to retry an ordinary request.019-b does not implement recovery.

Supersession and late completion never make obsolete content current. Valid immutable payload retention is separate from permission to select/publish current output; don't splice old original admission entries into a new proof parent. New unrelatedB/revision alone must not force unchangedA recompilation. Do not continue unneeded work solely to manufacture historical payloads. Explicit session teardown cancels/awaits its tasks, fences all late publication and releases only its ownership, preserving unrelated sessions.

## Implementation requirements

1. Add small typed async orchestration modules under constitution/bundles (suggest ram_work.py/ram_work_models.py), tests/test_bundle_ram_work.py and ONE owning contract docs/CACHE-RAM-WORK-CONTRACT.md. Cohesive changes to019-a store/models are allowed to share atomic capacity/lifecycle control; no speculative framework or dependency. Preserve accepted018 public signatures/schemas/defaults/key recipes/refusals. No constructor flags pretending caller snapshots are verified.
2. Bind every request/attempt/task/publication to actual registered trusted namespace, owner identity, epoch and actual currently admitted full key. Resolve current admissibility from actual store state; strings alone cannot mint work. Validate shape and bounded output at this inert work boundary. An injected result proves prepared-work orchestration only, never actual compiler semantic correctness. Own the task independently of the first waiter; don't hold a thread lock across await/model IO/SSE.
3. Default ONE process-wide active leader, with explicit positive non-bool bounded configuration for pending distinct keys, waiters per key and output size/time. Choose and document conservative finite defaults/hard limits within existing law. Bound queues before retaining tasks/waiters/source references. Same-key joins should not consume another distinct-key reservation; unrelated admitted work progresses when the active leader finishes/cancels. Deterministic test barriers rather than timing guesses.
4. Extend actual shared process/session occupancy to include retained pending/active/terminal attempt metadata, historical successful payloads, task/waiter-owned references and indexes. Charge conservatively BEFORE retention/publication; account explicit bounded reservations for runtime objects not measurable safely. No total-RSS claim. Aggregate async and existing store occupancy atomically under SAME ceilings; neither synchronous admit nor lifecycle operations may bypass accounting or leave tasks detached after owner teardown. At pressure fixed503 preserves old committed state/current lookup/payloads and counters, no TTL/LRU/eviction/checkpoint IO or unbounded tombstones. Full adverse-currentness/durability boundary remains whole019/020/022; do not claim it solved by byte preservation.
5. Expected-revision/CAS remains a commit fence, never a source clock or semantic-key field. Publication rechecks actual live owner/epoch and current source-key eligibility. Superseded work cannot become current because it completes late; completion after unrelatedB may reuse unchangedA if actual current bindings still prove compatibility. Concurrent teardown/update races leave bounded truthful outcomes and no late current publication or leaked task capacity. Provide an async teardown path that awaits cleanup and a safe coherent interaction with the existing synchronous teardown (no silently orphaned work).
6. Normal resolve/hit/selection and attempt handling remain RAM-only. No new recovery store, actual compiler/tokenizer/client/model/GPU/Gateway/native call, adapter startup wiring, service mutation or v1 activation. No live tests in this round. The callback seam is synthetic; 021 owns actual tool-free authenticated compiler and tokenizer contracts.

## Required focused evidence

Compose genuine P bootstrap/issuance/observations→actual T→registered019 owner, both lean/greedy and endpoint shapes where they affect binding. Assert actual work invocation count, typed outcome, payload validity, current eligibility and occupancy/task cleanup:

- simultaneous identical misses ONE leader and shared successful immutable payload; later same-key hit zero new invocation;
- first waiter cancelled with another surviving; follower cancelled with another surviving; all departed after dispatch; queued claimed-but-not-dispatched cancellation; pre-claim capacity refusal with zero invocation;
- exception, timeout, fixed invalid/truncated/over-budget seam outcomes and later same-failed-key request, unrelated-key/session progress, terminal attempt metadata never counted as hit;
- source A1→A2 and stale completion; valid A1→A2→genuine A1 revert without third invocation; failed A1→A2→genuine A1 revert still terminal; replay cannot reactivate; unchangedA after unrelatedB;
- namespace/principal/session/config/epoch fences; teardown during queued/active/shared work, old-owner late completion refused; only owned capacity released and unrelated sessions survive;
- exact/first-over pending/waiter/output limits and combined process/session occupancy; pressure retains existing hits/state, no queue/attempt eviction; repeated hits with mechanically denied filesystem content IO after setup.

These prove the injected seam only. No actual-model/compiler/client claim; whole019 final pressure/source-scale qualification and020–024 remain mandatory. Preserve native failed/partial evidence; don't add audits merely to obtain extra counters. Run focused Ruff/format/mypy/tests after coherent changes, then final required gate once final source is ready. Fix meaningful failures, avoid repeated passing gates for wording/status labels.

## Final verification and provenance

At final clean source A, commit exact active/order with all implementation/tests/docs. Generate manifest-only B, sole parent A. Required full gate at B with parent077 and actual nonroot fullpytest child022:

1. uv lock --check
2. uv sync --frozen --extra dev
3. uv run --frozen ruff check .
4. uv run --frozen ruff format --check .
5. uv run --frozen mypy src tests
6. uv run --frozen python scripts/docs_consistency_check.py
7. uv run --frozen pytest -q
8. uv build
9. uv run --frozen python scripts/artifact_policy_check.py --dist dist --inspect
10. uv run --frozen python scripts/artifact_policy_check.py --dist dist --install-smoke
11. uv run --frozen python --version
12. uv run --frozen python -m compileall -q src tests oap/bin scripts
13. uv run --frozen python scripts/dev_provenance_manifest.py --verify --dist dist
14. bash -c 'set -e; for path in oap/bin/*.sh packaging/*.sh; do bash -n "$path"; done'
15. git diff --check c5eb299df822875988867bf34d58de239e82657e HEAD

Reuse the required workflow: ONE clean Git-B archive builds BOTH artifacts; strict A/B/input-map/archive/sdist/wheel/RECORD/metadata/licenses/entrypoint/repo-dist proof with actual counts/hashes and outer/child exits; fresh non-editable smoke is gate10. No passing broad-check repetition for labels, no stale-manifest suppression, no rewrite of frozen published artifacts and no native binary/client in CI. Required exact-B checks: test, Analyze(actions), Analyze(python), CodeQL, gateway-contract, docker, docker-published, operator-session, cache-native-containment, cache-native-fixture — all present and SUCCESS before report. A helper records its actual PID/birth/PPID/UID/umask/sourcehash/awareUTC startup before work and is0700 before execution; do not reuse historical helpers in place. No new audit framework or extra planning documents.


## Artifact locations, docs and protection

All new scratch/evidence/builds under /home/janezp/codex-supervision/slaif-local-coding/work-artifacts/oap-019b-work. Directories700/manual files600/helpers700 BEFORE execution; writing outer shells umask077. Preserve historical bytes; no home-root folders/aliases/manual tmp captures. Original FIFO paths/objects unchanged. Do not repair old modes retroactively.

Update owning RAM/work contracts, both architecture maps (THREE compact mirrors byte-identical, supervision inode10638621/UID1001/0600 preserved IN PLACE), TESTING, brief existing configuration/plan references and EXISTING stage ledger for exact implemented inert scope, ratified attempt policy and remaining whole019/020–024. Mark019-a accepted at bounded scope with qualifications by019-a decision; preserve all earlier decisions/reports. No new planning/audit docs or historical-chronicle restatement. No active-v1/readiness claim. Fix any tiny in-scope documentation punctuation naturally before final freeze; no refreeze for labels alone.

No protected Qwen/vLLM18020/qwen-serving model/checkpoint/venv/patch/launch/systemd changes; no profile/key/auth/network/firewall/VPN/binding mutations, no release/tag/RC/registry/deploy/cutover/benchmark. No new coding/native clients anywhere. Development service only18031 if a later order needs it, none required here. Routine safe tools/setup remain coding's responsibility.

## Publication and synchronization

Same PR27 only. Complete/verify PR title/body using structured payload/body-file BEFORE final report and response, keep body focused on final objective behavior and honest validation. All non-report work remote, all TEN exact-B required checks present SUCCESS before report: test, Analyze(actions), Analyze(python), CodeQL, gateway-contract, docker, docker-published, operator-session, cache-native-containment, cache-native-fixture. Report latest actual results, failed/partial/overwritten evidence and remaining criteria honestly; no universality claims. No extra ROOT approval hold.

Atomically create exactly ONE oap/reports/019-b-bounded-singleflight.md, no overwrite. Literal40hex Implementation head SHA: B and Report publication commit: SELF. Commit ONLY that report as final commit, sole parent literalB; push and verify exact remote PR head/parent/single changed report path/report bytes and unchanged active/order. No subsequent source/report/Git/PR-metadata mutation/push. Send sole exact two-byte responseOK on original FIFO, then start ONE new foreground managed next-control reader with fresh private source/startup/receipt, actual lifetime/sourcehash/awareUTC and umask077 before launch. Do not claim an old spent handle is waiting. Native task completion/idle is distinct from actively coding; continue this same instance when ROOT steers authorized remaining scope. Report blockers concretely rather than starting another client.

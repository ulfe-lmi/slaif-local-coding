# OAP Work Order — 016-a

## Objective and authority

Establish the complete architecture, security and implementation contract for the human-authorized dependency-bundle CACHE rework. The human directly instructed strategy to create the implementation plan, fix both architectures, plan successor orders and run OAP until implementation is properly delivered. This round is the bounded architecture/documentation stage, not runtime implementation or qualification.

## Independently verified GitHub baseline

- Repository `ulfe-lmi/slaif-local-coding`; objective 016; round 016-a.
- Mode CREATE_NEW_PR. Required branch `oap/016-cache-rework-contracts`; base `main`.
- Verified remote main `f3793af9e5f05bdfba19ef800eeaf57177d0ed2b`.
- Predecessor Objective 015 PR #22 is MERGED; no objective-016 PR exists.
- Unrelated open PR #23 (`docs/local-readme-logo`) is outside this order.
- Strategy safely reconciled the previously historical clean tracked checkout to detached current origin/main before activation, preserving the human untracked document byte-identically. Do not revive 005-m or amend merged PR #7.
- Re-fetch and verify current main before branching. If remote moved, report exact discrepancy and proceed only when changes are compatible with this documentation scope; never discard human work.

## Runtime communication and executor

REPO_ROOT=/home/janezp/codex-work/slaif-local-coding
STRATEGIC_HOME=/home/janezp/codex-supervision/slaif-local-coding
CONTROL_FIFO=STRATEGIC_HOME/control.fifo
RESPONSE_FIFO=STRATEGIC_HOME/response.fifo

These are explicitly configured repository-supported runtime overrides for this host, not guessed historical paths. Both actual FIFOs are current-user-owned 0600. The external visible right-pane coding wrapper has consumed the exact control OK; do not read it again. It launches a fresh `codex --yolo --profile qwen-neumann` execution with xhigh per round. Profile context is 262144, compaction threshold 222000; do not equate executor context with product-client effective context. After report publication send exact response OK and exit; the wrapper waits for subsequent control.

## Required reading and source inputs

Read current main governance, both complete `ARCHITECTURE.md` and `ARCHITECTURE-for-agents.md`, security/testing/configuration contracts, and the entire human `docs/CACHE-REWORK.md`. Its SHA256 must remain `410df5c0b8f90b05220adc32c8e673b143c0cf1fa3da02270d91ac453c886abd`.
Read the finalized strategic plan `/home/janezp/codex-supervision/slaif-local-coding/drafts/CACHE-IMPLEMENTATION-PLAN.md` completely. Copy its exact bytes to `docs/CACHE-IMPLEMENTATION-PLAN.md`. The plan explicitly resolves every section-18 decision. If an implementation impossibility or human-level risk contradicts those choices, document the exact issue; do not invent replacement policy.

## Bounded changes

1. Create the exact required branch from verified main and exactly one PR titled `Define dependency-bundle cache architecture and implementation plan`.
2. Commit the human handoff unchanged. Commit the strategic implementation plan unchanged.
3. Update `ARCHITECTURE.md` and `ARCHITECTURE-for-agents.md` coherently. Make the new profile's normative target explicit and distinguish it from current legacy implemented behavior. Cover evidence-based recursive graph/whole bundles, complete read spans, scoped lean/greedy, independent ordered identity/replay/overlap, C/32 insertion and aggregate token budgets, compile-once/epoch, RAM ownership/no eviction, exact-original recovery, transactional replacement and no hidden fallback, source-role authority, explicit failure/privacy/capacity and observability. Do not leave old blanket laws contradicting approved v1 behavior. Preserve unaffected API/Gateway/image/service boundaries and real legacy/RC10 evidence.
4. Update root `AGENTS.md`, repo strategic instruction constitution/compact architecture and `SECURITY.md` only as required to scope legacy rules and authorize the narrow explicit protected source-recovery exception. Keep core authority, report immutability, credentials/logging prohibitions and protected-service boundaries intact. Do not change any prior activated order/report. Strategic architecture copy must match the normative current compact architecture, not a weaker historical version.
5. Update `TESTING.md` and `docs/ADAPTER-CONFIGURATION.md` with planned profile contracts and the criterion-level implementation/qualification gates. Mark future configuration examples as planned/non-runnable until the config implementation lands. Do not claim new runtime keys exist yet. Defer README build-input changes to integration if necessary; plan/architecture links must work.
6. Create `docs/CACHE-REWORK-LEDGER.md` covering every named D01-D10/G01-G05/C01-C06/B01-B04/R01-R05/M01-M05/S01-S02/O01-O03 criterion. Initially runtime criteria are NOT RUN/planned; distinguish evidence, implementation and acceptance. Record the planned objective succession 016–024 and same-PR continuation discipline. Document RC10 as the historical baseline, not a rework-qualified artifact.
7. If docs landing pages need links, update only narrowly necessary documentation indexes. No runtime Python, dependencies, compiler, cache, source replacement, benchmark dispatch, artifact publication, or service changes in this round.

## Acceptance criteria

A. Exact approved handoff and finalized strategic plan are tracked, unchanged and linked.
B. Both architecture documents are coherent and complete for all ten approved rules and the strategic section-18 choices. Explicitly scoped legacy behavior does not masquerade as new-profile delivery.
C. Root/strategic law, security and testing/config docs no longer categorically prohibit required v1 protected originals or require v1 TTL/LRU/filesystem hot cache/raw fallback. V1 requirements do not weaken default logs/credentials/identity isolation.
D. The stage ledger maps all 40 named acceptance cases with honest NOT RUN states and planned evidence; no root-only success assertion.
E. Documentation/current publication/build validation and current-head required remote checks are genuinely successful. Preserve all existing frozen RC10/historical artifact bytes and provenance claims. If existing packaging gates require a source/provenance change outside documentation scope, publish precise blocker or request a bounded same-PR strategic continuation through the report rather than weakening gates or rewriting immutable records.

## Verification

Run the current locked `TESTING.md` local gate: uv lock --check; uv sync --frozen --extra dev; uv run --frozen ruff check .; uv run --frozen ruff format --check .; uv run --frozen mypy src tests; uv run --frozen python scripts/docs_consistency_check.py; uv run --frozen pytest -q; uv build; uv run --frozen python scripts/artifact_policy_check.py --dist dist --inspect; uv run --frozen python scripts/artifact_policy_check.py --dist dist --install-smoke. Also python -m compileall -q src tests oap/bin scripts; bash -n for repo OAP/packaging shell scripts; git diff --check; exact handoff/plan hashes, relative links, targeted privacy/secret scan and no prior immutable-artifact edits. Add no mirror tests just for prose. State unavailable optional peer/live tests honestly; no live model calls are authorized or needed. All required GitHub checks must be present and green; local tests do not impersonate remote checks.

## Safety and non-goals

Protected-host access is read-only; no inference, deployment or service mutations. Do not alter model/profile/API-key files, Qwen/vLLM units/ports/models/venvs/flags, network/firewall/VPN, Gateway repository/policy, registry/RC tags/records, or private benchmark histories. Never expose source payloads/secrets in reports. No production claim, benchmark dispatch, release, Gateway change, model loading or unrelated refactor. Safe repo-local tools/setup belong to coding; preserve pre-existing work. The only untracked human input authorized into this PR is exact docs/CACHE-REWORK.md.

## Publication and report

Create exactly one objective-016 PR, never merge/auto-merge. Commit strategic-authored activated order/active unchanged with intended docs, push, verify PR identity/diff and inspect/fix in-scope CI. All non-report work must be remote before capturing literal 40-hex implementation head. Atomically publish exactly one matching `oap/reports/016-a-cache-rework-contracts.md` with literal `Implementation head SHA: <40-hex>` and `Report publication commit: SELF`. Report the A–E evidence, exact tests/statuses, changed files, no runtime implementation, protected fixture unchanged, immutable handoff/plan hashes, blockers and pending checks. Final commit changes only this report, parent equals implementation head, remote PR head/path/content verified. Send exact response FIFO OK only then, make no more mutation/push, and exit. The external coding wrapper handles the next control wait.

# OAP Work Order — 003-c

## Objective

Execute the human-approved one-time recovery path for objective 003 and add the
requested MVP completeness snapshot. Open one new review PR from the existing
objective branch, add only `oap/COMPLETENESS.md`, obtain required CI for the
already implemented `003-b` work plus this documentation, and publish an
immutable report. No runtime/code/test behavior changes.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`
- Numeric objective / round: `003` / `003-c`
- PR mode: `CREATE_RECOVERY_PR_EXCEPTION` (human-approved one-time exception;
  not a replacement of immutable PR #4 or prior reports)
- Existing merged/closed PR: #4; do not edit or reopen it
- Required base: `main` at `68f212b5ad316b95fa12ef632e1538b56479081b`
- Required branch: existing `oap/003-working-set-injection-foundation`
- Verified branch head / `003-b` SELF:
  `455d5cb2bd00e7e4763b285de2d0c3c367122890`
- Required action: advance this same branch and open exactly one new recovery
  PR to `main`; no other PR; coding never merges.

## Verified context

PR #4 is merged/closed, so `003-b` could not obtain current-head CI through it.
Human approved this one-time recovery PR. Remote `main` remains at accepted
`003-a` merge commit. Protected vLLM remains PID 26028 on `0.0.0.0:18020`;
ports 18021/18031 are free. The human explicitly accepts the test-key risk and
declines rotation; coding must still avoid printing or persisting secrets.

## Scope

Add `oap/COMPLETENESS.md` with this exact estimate and structure, improving only
wording/format if needed without changing the assessment:

```markdown
# OAP MVP Completeness — 2026-08-22

Assessment target: full SME MVP represented by objectives 000–006.
Current authoritative recovery-branch readiness: ~64%.
Current merged `main` readiness before recovery merge: ~58%.
Current fixture is text-only/zero-image; no vision or production readiness is claimed.

| Objective | Weight | Complete | Evidence | Remaining gap |
|---|---:|---:|---|---|
| 000 adapter foundation, proxy, image policy | 15% | 100% | Merged PR #1; fake/live tests | None within objective |
| 001 AGENTS observation and deterministic candidates | 10% | 100% | Merged PR #2; fixtures/tests | Compiler/injection intentionally later |
| 002 compiler, validation, bounded cache | 20% | 100% | Merged PR #3; isolation/live text evidence | Request integration completed in 003-b |
| 003 selection, injection, acquisition, rehydration | 25% | 60% | PR #4 plus recovery PR; one-root pipeline/cache tests | Dependency/tool acquisition and compaction rehydration |
| 004 real Codex E2E, security/operations hardening | 20% | 15% | Metrics/security tests; service example | Actual Codex long-session/compaction/vision E2E and systemd candidate proof |
| 005 gateway integration and controlled cutover | 7% | 5% | Interface documentation only | Signed identity, gateway PR, soak, rollback-proven cutover |
| 006 reproducible SME package/release | 3% | 20% | Build/package/license/service example | Reproducible installer, capacity/runbook, tested release claims |
| **Weighted total** | **100%** | **64% on branch** | OAP orders/reports/CI | See rows above |
```

Do not alter source, tests, dependencies, configuration semantics, prior orders,
reports, or protected host state. Do not perform live model calls; existing
`003-b` evidence remains applicable because this round changes documentation
only.

## Acceptance

1. Exactly one new recovery PR exists from the required branch to `main`.
2. `oap/COMPLETENESS.md` contains the required honest table and limitations.
3. Implementation commit adds only the completeness document plus exact
   activated order/active transcript; no runtime files change.
4. Current implementation-head and report-head CI are successful.
5. Immutable `003-c` report maps every criterion and exact command status.

## Required checks

```bash
uv lock --check
uv sync --frozen --extra dev
uv run --frozen ruff check .
uv run --frozen ruff format --check .
uv run --frozen mypy src tests
uv run --frozen pytest -q
uv build
python3 -m compileall -q src tests oap/bin
bash -n oap/bin/*.sh
git diff --check 68f212b5ad316b95fa12ef632e1538b56479081b...HEAD
```

Live model calls: `NOT RUN (not required; documentation-only recovery)`.
Perform secret/raw-content and scoped-diff audits plus read-only protected-host
before/after snapshot. Wait for final report-head CI; missing/pending/failed
checks block acceptance.

## Publication contract

Push `oap/COMPLETENESS.md`, exact order, and active selector to the existing
branch; open exactly one recovery PR; verify base/head/changed paths/checks;
record implementation head; atomically publish exactly one
`oap/reports/003-c-recovery-review-and-completeness.md` as the sole report-only
SELF child changing only that report. Push it as remote head, verify parent and
bytes, then signal response FIFO `OK`. Never rewrite prior artifacts.

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

# OAP MVP Completeness — 2026-08-22

Assessment target: full SME MVP represented by objectives 000–006.
Current authoritative recovery-branch readiness: ~78%.
PR #6's base `main`, including accepted objective 003, readiness: ~74%.
Current fixture is text-only/zero-image; no vision or production readiness is claimed.

| Objective | Weight | Complete | Evidence | Remaining gap |
|---|---:|---:|---|---|
| 000 adapter foundation, proxy, image policy | 15% | 100% | Merged PR #1; fake/live tests | None within objective |
| 001 AGENTS observation and deterministic candidates | 10% | 100% | Merged PR #2; fixtures/tests | Compiler/injection intentionally later |
| 002 compiler, validation, bounded cache | 20% | 100% | Merged PR #3; isolation/live text evidence | Request integration completed in 003-b |
| 003 selection, injection, acquisition, rehydration | 25% | 100% | PR #5 through 003-e; one-root pipeline/cache tests; fake-upstream dependency acquisition, isolation, and process-local zero-root rehydration tests | None within objective; real Codex E2E evidence is objective 004 |
| 004 real Codex E2E, security/operations hardening | 20% | 35% | Prior isolated Codex CLI 0.149.0 governed-tool/cache/sentinel E2E; metrics/security tests; 004-c governance-only sentinel attempts used tools/exit 0 but ended in sanitized `sentinel_missing`; sanitized dependency-cache diagnostics are being gathered | Governance-derived sentinel success, actual forced/equivalent long-session compaction, vision-capable E2E, security hardening review, and systemd candidate proof |
| 005 gateway integration and controlled cutover | 7% | 5% | Interface documentation only | Signed identity, gateway PR, soak, rollback-proven cutover |
| 006 reproducible SME package/release | 3% | 20% | Build/package/license/service example | Reproducible installer, capacity/runbook, tested release claims |
| **Weighted total** | **100%** | **~78% on branch** | OAP orders/reports/CI | See rows above |

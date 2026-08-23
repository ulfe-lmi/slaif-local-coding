# OAP MVP Completeness — 2026-08-23

Assessment target: full SME MVP represented by objectives 000–006.
Current authoritative recovery-branch readiness: ~89%.
PR #6's base `main`, including accepted objective 003, readiness: ~74%.
The protected fixture is text-only/zero-image in this round; the repository-only
vision runner is ready, but no live vision or production readiness is claimed.

| Objective | Weight | Complete | Evidence | Remaining gap |
|---|---:|---:|---|---|
| 000 adapter foundation, proxy, image policy | 15% | 100% | Merged PR #1; fake/live tests | None within objective |
| 001 AGENTS observation and deterministic candidates | 10% | 100% | Merged PR #2; fixtures/tests | Compiler/injection intentionally later |
| 002 compiler, validation, bounded cache | 20% | 100% | Merged PR #3; isolation/live text evidence | Request integration completed in 003-b |
| 003 selection, injection, acquisition, rehydration | 25% | 100% | PR #5 through 003-e; one-root pipeline/cache tests; fake-upstream dependency acquisition, isolation, and process-local zero-root rehydration tests | None within objective; real Codex E2E evidence is objective 004 |
| 004 real Codex E2E, security/operations hardening | 20% | 90% | Prior workspace-write/native-helper diagnostics remain historical and are not governed acceptance evidence. See the concise [Objective-004 criterion ledger](../docs/OBJECTIVE-004-LEDGER.md): accepted 004-s/004-w/004-x evidence covers all non-vision criteria, and this round adds the bounded adapter-boundary simulated-compaction proof plus repository-only vision readiness support. | Live vision-capable Codex full-image then crop evidence on the human-provided fixture |
| 005 gateway integration and controlled cutover | 7% | 5% | Interface documentation only | Signed identity, gateway PR, soak, rollback-proven cutover |
| 006 reproducible SME package/release | 3% | 20% | Build/package/license/service example | Reproducible installer, capacity/runbook, tested release claims |
| **Weighted total** | **100%** | **~89% on branch** | OAP orders/reports/CI | See rows above |

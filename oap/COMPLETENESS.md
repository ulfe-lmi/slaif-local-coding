# OAP MVP Completeness — 2026-08-23

Assessment target: full SME MVP represented by objectives 000–006.
Current authoritative recovery-branch readiness: ~79%.
PR #6's base `main`, including accepted objective 003, readiness: ~74%.
Current fixture is text-only/zero-image; no vision or production readiness is claimed.

| Objective | Weight | Complete | Evidence | Remaining gap |
|---|---:|---:|---|---|
| 000 adapter foundation, proxy, image policy | 15% | 100% | Merged PR #1; fake/live tests | None within objective |
| 001 AGENTS observation and deterministic candidates | 10% | 100% | Merged PR #2; fixtures/tests | Compiler/injection intentionally later |
| 002 compiler, validation, bounded cache | 20% | 100% | Merged PR #3; isolation/live text evidence | Request integration completed in 003-b |
| 003 selection, injection, acquisition, rehydration | 25% | 100% | PR #5 through 003-e; one-root pipeline/cache tests; fake-upstream dependency acquisition, isolation, and process-local zero-root rehydration tests | None within objective; real Codex E2E evidence is objective 004 |
| 004 real Codex E2E, security/operations hardening | 20% | 40% | Prior workspace-write/native-helper diagnostics remain historical and are not governed acceptance evidence. Strategic review accepted the 004-s two-invocation global-yolo run: both crossing-boundary `GOVERNANCE-DEPENDENCY.md` byte streams matched the fixture exactly (127 bytes; SHA-256 `71f0fa5dd58c8c7f4ba6c2d40caeee9db3e9eb0b4911e9bc23ba7726fc0c5a09`); observation, successful acquisition, direct non-recursive compilation, and stable injection completed; the hidden dependency-derived sentinel passed twice; invocation 1 recorded a dependency-cache miss and two compiler-model attempts, invocation 2 a persistent cache hit and zero additional compiler-model attempts. Protected-state post-audit passed without changing the protected service | Actual forced/equivalent long-session compaction, vision-capable E2E, broader security/observability hardening review, and systemd candidate proof |
| 005 gateway integration and controlled cutover | 7% | 5% | Interface documentation only | Signed identity, gateway PR, soak, rollback-proven cutover |
| 006 reproducible SME package/release | 3% | 20% | Build/package/license/service example | Reproducible installer, capacity/runbook, tested release claims |
| **Weighted total** | **100%** | **~79% on branch** | OAP orders/reports/CI | See rows above |

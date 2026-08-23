# OAP MVP Completeness — 2026-08-23

Assessment target: full SME MVP represented by objectives 000–006.
Current authoritative recovery-branch readiness: ~74%.
PR #6's base `main`, including accepted objective 003, readiness: ~74%.
Current fixture is text-only/zero-image; no vision or production readiness is claimed.

| Objective | Weight | Complete | Evidence | Remaining gap |
|---|---:|---:|---|---|
| 000 adapter foundation, proxy, image policy | 15% | 100% | Merged PR #1; fake/live tests | None within objective |
| 001 AGENTS observation and deterministic candidates | 10% | 100% | Merged PR #2; fixtures/tests | Compiler/injection intentionally later |
| 002 compiler, validation, bounded cache | 20% | 100% | Merged PR #3; isolation/live text evidence | Request integration completed in 003-b |
| 003 selection, injection, acquisition, rehydration | 25% | 100% | PR #5 through 003-e; one-root pipeline/cache tests; fake-upstream dependency acquisition, isolation, and process-local zero-root rehydration tests | None within objective; real Codex E2E evidence is objective 004 |
| 004 real Codex E2E, security/operations hardening | 20% | 15% | Prior diagnostic elaboration is not governed E2E evidence. The historical raw probe remains narrowly `raw_bwrap_unshare_all_loopback_bootstrap_failed`; the OAP parent was independently established as host-direct/unsandboxed. Immutable 004-o records the startup placement failure. Corrected 004-p B reached Codex 0.149.0 and exited 0, but its one successful command was not the required exact `/usr/bin/true` (`command_equal=false`, origin `model_wrong_command`); A, dependency `cat`, adapter/compiler/model calls, and governed/cache E2E were gated. No Local Coding defect was tested and no protected service was changed | Exact ordinary `/usr/bin/true` B+A equivalence, dependency bytes, governance-derived sentinel success, successful ordinary-read lifecycle and cache reuse, actual forced/equivalent long-session compaction, vision-capable E2E, security hardening review, and systemd candidate proof |
| 005 gateway integration and controlled cutover | 7% | 5% | Interface documentation only | Signed identity, gateway PR, soak, rollback-proven cutover |
| 006 reproducible SME package/release | 3% | 20% | Build/package/license/service example | Reproducible installer, capacity/runbook, tested release claims |
| **Weighted total** | **100%** | **~74% on branch** | OAP orders/reports/CI | See rows above |

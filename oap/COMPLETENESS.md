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
| 004 real Codex E2E, security/operations hardening | 20% | 35% | Prior isolated Codex CLI 0.149.0 governed-tool/cache/sentinel E2E; metrics/security tests; provenance/lifecycle gating now distinguishes repository from crossing-boundary bytes; direct same-user read controls passed in both 004-f attempts, which were then classified `sandbox_denied`, so no successful governance lifecycle exists; 004-g's malformed sandbox preflight exited before the disposable read and was classified `unresolved_with_fixed_evidence`; 004-h corrected the helper invocation, but the fresh no-model read still exited before crossing-boundary bytes with first meaningful `not_found`/`not_found` evidence; 004-i verified local executable facts and classified `helper_executable_mapping_failure`; 004-j used a corrected resolved executable spelling and a direct read-only bubblewrap probe, received helper `not_found`/`not_found` plus fixed `sandbox_denied`/`bwrap_loopback_bootstrap`, and deterministically classified `bubblewrap_kernel_runtime_unsupported` after two probes, with zero governed model calls and unchanged completeness/readiness | Governance-derived sentinel success, successful ordinary-read lifecycle evidence, actual forced/equivalent long-session compaction, vision-capable E2E, security hardening review, and systemd candidate proof |
| 005 gateway integration and controlled cutover | 7% | 5% | Interface documentation only | Signed identity, gateway PR, soak, rollback-proven cutover |
| 006 reproducible SME package/release | 3% | 20% | Build/package/license/service example | Reproducible installer, capacity/runbook, tested release claims |
| **Weighted total** | **100%** | **~78% on branch** | OAP orders/reports/CI | See rows above |

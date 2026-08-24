# OAP MVP Completeness — 2026-08-24

Assessment target: full SME MVP represented by objectives 000–006.
Current authoritative recovery-branch readiness: ~91%.
Historical PR #6 base snapshot before Objective-004 acceptance, readiness: ~74%
(retained audit context only; not current branch status).
The protected vision fixture completed the single ordered full-image then crop
acceptance run. This is fixture-scoped evidence, not production readiness.

| Objective | Weight | Complete | Evidence | Remaining gap |
|---|---:|---:|---|---|
| 000 adapter foundation, proxy, image policy | 15% | 100% | Merged PR #1; fake/live tests | None within objective |
| 001 AGENTS observation and deterministic candidates | 10% | 100% | Merged PR #2; fixtures/tests | Compiler/injection intentionally later |
| 002 compiler, validation, bounded cache | 20% | 100% | Merged PR #3; isolation/live text evidence | Request integration completed in 003-b |
| 003 selection, injection, acquisition, rehydration | 25% | 100% | PR #5 through 003-e; one-root pipeline/cache tests; fake-upstream dependency acquisition, isolation, and process-local zero-root rehydration tests | None within objective; real Codex E2E evidence is objective 004 |
| 004 real Codex E2E, security/operations hardening | 20% | 100% | Prior workspace-write/native-helper diagnostics remain historical and are not governed acceptance evidence. See the concise [Objective-004 criterion ledger](../docs/OBJECTIVE-004-LEDGER.md): accepted 004-s/004-w/004-x evidence covers the non-vision criteria, and 004-al adds the single authorized live vision full/full then crop/crop run with route-scoped one-image adaptation, effective CR/LF-only binding, and privacy-safe evidence. | None within objective; gateway integration remains a separate milestone |
| 005 gateway integration and controlled cutover | 7% | 5% | Interface documentation only | Signed identity, gateway PR, soak, rollback-proven cutover |
| 006 reproducible SME package/release | 3% | 20% | Build/package/license/service example | Reproducible installer, capacity/runbook, tested release claims |
| **Weighted total** | **100%** | **~91% on branch** | OAP orders/reports/CI | See rows above |

The accepted vision fixture used context 100000 (the text configuration uses
150000), accepted one image per upstream request, and transformed full/full then
crop/crop history through the route-scoped policy. Both hidden bindings were
effective after CR/LF-only framing normalization. The fixture still emits two
leading LF bytes around the hidden sentinel, so byte-exact final formatting is
not proven or supported on this fixture. This remains a formatting limitation of
the selected Qwen fixture, not a generic whitespace-normalization allowance or a
production/cutover claim.

Objective-005-c did not complete its acceptance contract. Its disposable
PostgreSQL/gateway/candidate path reached the public model route, text, SSE,
and one-image subset and cleaned up with the protected vision fixture
unchanged. The real Codex 0.149.0 tool envelope was rejected before a public
reservation, so quota/ledger proof for that portion, complete gateway Codex
compatibility, and rollback-proven cutover remain open. Strategy must not raise
the Objective-005 completeness arithmetic from this report.

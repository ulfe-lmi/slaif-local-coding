# OAP Completeness — 2026-09-20

Assessment target: the accepted Local Coding implementation (objectives
000–012, all merged) plus the Objective-013 release-candidate stabilization
(PR #15 open as of this writing; current disposition: RC stabilization and
freeze, public final release DEFERRED to a later human decision). The
historical 013 rounds (013-a through 013-h) completed the publication
machinery (pull-based canonical compose, activated `workflow_dispatch`-only
release workflow, `docker-published` CI gate, state-aware provenance) and
pushed the historical private tags `0.1.0` + `sha-<S>` to the non-public
package at one registry digest (registry-only; never published to users;
the 013-h round ended BLOCKED at anonymous access verification). Order
013-i freezes the final source for a benchmarkable 0.1.0 RC: documentation
cleanup, deterministic build pinning, pre-freeze candidate provenance
(schema v4), the RC artifact record schema/generator, and the RC-safe
publication machinery (candidate identity `0.1.0-rc1`, private registry,
fail-closed authenticated tag checks). The RC publication is a separate
later round bound to the exact reviewed source commit; no Git tag and no
GitHub Release exist.

## Merged state (verified against GitHub on 2026-09-17)

| Objective | Merged PR | Merge commit | Accepted state |
|---|---|---|---|
| 000 adapter foundation, proxy, image policy | PR #1 | `91463ae3199dd06e0448a9422a5e713da8ee92df` | implemented and merged |
| 001 AGENTS observation and deterministic candidates | PR #2 | `176bf4d839ae9fa32d0cc3c4279a1b96220c1c61` | implemented and merged |
| 002 compiler, validation, bounded cache | PR #3 | `867ed55e7d115d960c666380ebbc5952d43d97d1` | implemented and merged |
| 003 selection, injection, acquisition, rehydration | PR #4, #5 | `68f212b5ad316b95fa12ef632e1538b56479081b`, `7a2c36a0a40958a6059a765c2f9d5e5bf4ddc161` | implemented and merged |
| 004 real Codex E2E, security/operations hardening | PR #6 | `570bd2b24ad4b041a07e0320d5ed44bc73e99ad5` | implemented and merged; real-E2E accepted (fixture-scoped) |
| 005 gateway integration and controlled cutover contract | PR #7 | `e3f10e93c1ea84bf4021fd15d566bf577d5a9dcf` | implemented and merged; accepted under its documented composed closure |
| 006 signed-request replay hardening | PR #8 | `efc4dbcd377dd796a670726b16ebc06bd54b6356` | implemented and merged |
| 007 current Gateway contract CI | PR #9 | `2041bddc5a745ef0dd4f3088c24b74b9bceefdb9` | implemented and merged; continuously Gateway-contract tested |
| 008 durable acceptance evidence | PR #10 | `1a913bf3520e7570042774ef7c8ca5153da7a671` | implemented and merged |
| 009 release candidate and operational closure | PR #11 | `4fd4502deda23ef8815740f4db0c1e615a5a1936` | reproducible package (wheel = single supported distributable) and deployment-qualified (disposable environment only); cutover NOT performed; NOT released |
| 010 pre-cutover topology and signed-ingress correctness | PR #12 | `4aa805fdd197938f1f25c9ca034c2e3c3cf2fc87` | implemented and merged; cutover prepare-only, not performed |
| 011 Docker MVP packaging and release-readiness closure | PR #13 | `e860e0bff687afded7782fb2687b5b435792459a` | Docker-qualified, LAN-visible, documentation-reconciled MVP release candidate; deployment-qualified (disposable/CI environments only); cutover NOT performed; NOT released at that objective's acceptance |
| 012 current Gateway peer re-pin | PR #14 | `a04693e6792df6a8ad4262acfb46336a0f662202` | implemented and merged; re-pinned the current Gateway peer to `1fccaa746df6cd44f1ddf8c2ec5cf6ea9f18b1cb` at that order time (contract surface byte-identical, proven at the blob level); subsequently re-pinned by Objective 013-b |
| 013 release-candidate stabilization and 0.1.0 RC freeze (MVP 0.1.0 GHCR publication and release provenance closure; public final release DEFERRED) | PR #15 (open as of this writing) | — | 013-a implementation complete and CI-verified (publication held at its R18 Gateway-peer hold); 013-b re-qualified and re-pinned the peer to `08ca421bee1ddca62078302b910e8be88cf705be` (contract surface byte-identical, blob-proven) and dispatched the publication: the historical PRIVATE tags `0.1.0` and `sha-<image-source commit>` were pushed to the NON-PUBLIC package at one registry digest (recorded in the historical OAP report evidence; `packaging/release_record.json` was never committed); the tags were never published to users and the package was never made public (013-h BLOCKED at anonymous access verification; that acceptance condition is withdrawn by the human private-RC direction). 013-i (current): RC stabilization/freeze — user-facing documentation cleanup (README/QUICKSTART/INSTALL + reconciled docs), deterministic build pinning (`hatchling==1.32.0` proven against the historical source), pre-freeze candidate provenance (schema v4) with RC artifact record schema/generator, RC-safe publication machinery (candidate identity `0.1.0-rc1`, private registry, fail-closed authenticated tag checks, private `docker-published` qualification); RC publication is a separate later round bound to the exact reviewed source commit; historical `0.1.0` tag is legacy unpublished-to-users output, NOT the RC benchmark target; pull-based installation is the canonical operator path (explicit image selection; no silent legacy default); cutover NOT performed; no real deployment yet evidenced |

Identifier note: the original planned meanings formerly associated with numeric
objectives 006–008 (for example "reproducible SME package/release") are
historical planning prose, not live objective identifiers. The original product
milestone "reproducible SME package and honest release evidence" is implemented
under the Objective-009 milestone name.

## Historical assessment (2026-08-24, retained as dated audit context)

Assessment target at the time: full SME MVP represented by objectives 000–006
under original planned semantics.
Readiness at the time: ~91% on the recovery branch.
Historical PR #6 base snapshot before Objective-004 acceptance, readiness: ~74%
(retained audit context only; not current branch status).
The protected vision fixture completed the single ordered full-image then crop
acceptance run. This is fixture-scoped evidence, not production readiness.

| Objective (original planned semantics) | Weight | Complete | Evidence | Remaining gap |
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

Objective-005-d adds security-containment evidence and a no-model differential
against the unchanged pinned gateway. Four bounded Codex variants all retained
ordinary local function/custom declarations but retained hosted search
declarations and were rejected before reservation with the fixed gateway policy
error. No configuration-only compatible variant was found; the corrected
005-c driver preflight refuses any full stage when that rejection occurs. This
does not change the 5% Objective-005 completeness arithmetic or prove gateway,
adapter, Qwen, Docker, PostgreSQL, cutover, or production acceptance.

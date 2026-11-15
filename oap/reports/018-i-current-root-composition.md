# OAP Coding-Agent Report — 018-i

## Work order
- Identifier: 018-i; order path `oap/orders/018-i-current-root-composition.md`; numeric objective 018
- PR mode: AMENDED_EXISTING_PR

## Status
COMPLETE (bounded inert slice; strategic acceptance PENDING; whole 018 remains open)

## Executive summary
Implemented ONE inert pure versioned composition of the ACTUAL 018-h
current-root selection, actual selected-root source resolution, a freshly
recomputed 018-f least fixed point (selected root as NEW supplier) and the
018-g admission entries under the ACTUAL 018-c canonical recipe with the
selected governing digest. Durable A-H original-API matrix (44 definitions /
166 cases) added; contract, human/compact ARCH, TESTING, ledger, append-only
018-h process addendum and ALL3 compact mirrors updated. Exact-15 gate,
clean-B BOTH artifact proof and CI all green at the implementation head. The
I9 post-refresh NEW-root mixed-bundle shape remains a documented UNREACHED
limitation (the unmodified public H acquisition refuses it before I; the old
H law was not broadened and no positive was manufactured).

## Authoritative GitHub state
- Repository: ulfe-lmi/slaif-local-coding
- PR: #26 https://github.com/ulfe-lmi/slaif-local-coding/pull/26 (open, mergeable)
- Base: main ffaabf4b4d9ce3a9cb7a48e12ab7d8847999adef; head branch oap/018-cache-graph-bundles
- Starting remote SHA: 1b9d1d0e966970096961888f35bf26eafd7f8af5 (018-h SELF)
- Implementation head SHA: 60635fb7a61047328c119a8d5d286a5c213798de
- Report publication commit: SELF
- Implementation commits pushed before report: A 8ad47631a9658b6a186741fc3bd2868faed3465a (source), B 60635fb7a61047328c119a8d5d286a5c213798de (development provenance manifest, 257 inputs, sole parent A); pushed together
- New PR this round: NO; amended existing PR 26: YES; merge performed: NO
- PR title/body updated metadata-only before this report

## Changes and files
- NEW `src/slaif_local_coding/constitution/bundles/current_root_composition_models.py` and `current_root_composition.py` (public entry `derive_current_root_composition`); private narrow seams in `root_lineage.py` (`_selection_kernel`), `current_graph.py` (selected-root-region validation + `_derive_graph` seam), `current_admission.py` (file-entry assembly with selected-root-digest filter); ALL old public signatures/defaults/schemas/versions/refusals preserved
- NEW `tests/test_current_root_composition.py` (44 definitions / 166 cases)
- NEW `docs/CACHE-CURRENT-ROOT-COMPOSITION-CONTRACT.md` (contract/policy v1)
- Updated `ARCHITECTURE.md`, `ARCHITECTURE-for-agents.md` (mirrors byte-equal; strategic inode 10638621/1001/0600 in place), `TESTING.md`, `docs/CACHE-REWORK-LEDGER.md`, `oap/REPORT-CORRECTIONS.md` (append-only 018-h process addendum)
- Committed unchanged: the activated order (SHA 47344711... verified) and `oap/active` (018-i)

## Acceptance evidence (exact captures in W18i; both read endpoints, both admission modes)
- A bootstrap/ENVELOPE, genuine issued READ refresh, descendant revert, rootless continuation, old/known-new/shifted replay no-ops, unknown changed envelope whole refusal: PASSED
- B root edge withdrawal, cycle-only loss, independent alternate preservation, restoration from the same retained originals: PASSED
- C I canonical keys vs the INDEPENDENT original-C oracle, unchanged source under changed governing root, equal-byte witness no false miss: PASSED
- D incompatible/equal maxima, child-of-one vs compatible bytes, child-of-all, delayed older receipt, genuine late NONROOT ancestor, no partial outputs on conflict: PASSED
- E current/staled root reads, proven matching root segments, root-bearing boundaryless bundles no promotion, competing segments refused, I9 stale root not admitted while lean nonroot still admits: PASSED
- F native initial-EXEC/poll, Unicode/CRLF/empty text with proven spans, unsupported/unissued typed retained uncertainty: PASSED
- G every new/inherited cap at-limit/first-over with target-reaching sentinels, independent phase ceilings, cumulative vs batch scope, long-workspace reservations, H-namespace retention cap: PASSED
- H foreign/malformed/coherently-unsupported versions, forged keys/provenance, closed bound fences before first dump, no-host-IO/private-repr, 1:1 limitation mapping: PASSED

## Verification
- `uv run --frozen python scripts/docs_consistency_check.py`: PASSED (pre-commit and gate cmd06)
- `uv run --frozen ruff check .` / `ruff format --check .` / `uv run --frozen mypy src tests`: PASSED (pre-commit and gate cmd03-05)
- `uv run --frozen pytest -q tests/test_current_root_composition.py`: PASSED 166/166 pre-commit
- Full suite pre-commit (DEVIATION, recorded below): FAILED exit 1 — 2 failed, 5471 passed, 28 skipped (629.14s); both failures are the state-dependent real-repo provenance-binding tests refusing the dirty pre-A tree by design; the same tests PASS at clean B inside the ordered gate
- ONE foreground-managed exact-15 at clean B (driver PID 3909412 umask 0077; cmd07 child PID 3909619 umask 0022; live metadata in gate-driver-meta.json): PASSED, all 15 literal exits 0; cmd07 5473 passed, 28 skipped (670.64s); cmd13 manifest verify OK
- ONE exact-B clean git-archive BOTH wheel/sdist build (archive 20971520 B, 854 files) + full strict proof: PASSED, all assertions — 257 manifest inputs verified vs Git B and clean tree; sdist 255 entries (254 source + 1 generated PKG-INFO 22728 B == wheel METADATA); wheel 58 entries (52 runtime + 6 dist-info; RECORD 57 rows + RECORD row); entry_points/LICENSE/NOTICE/.gitignore/repo-dist identity/repo-clean asserted
- `git diff --check ffaabf4b... HEAD` (gate cmd15): PASSED

## Live model/service evidence
NOT RUN — the order prohibits live model/upstream/Gateway calls; no protected fixture touched.

## GitHub CI / required checks
At implementation head B, 10/10 check runs SUCCESS (test, docker, gateway-contract, operator-session, cache-native-containment, cache-native-fixture, docker-published, CodeQL, Analyze x2). All required green at drafting: yes.

## Local setup/dependencies
None new (repo venv via `uv --frozen`; no sudo; no service mutation).

## Documentation
Updated as listed (contract + ARCH/TESTING/ledger + mirrors reconciled); 018-i PENDING acceptance at its bounded inert scope in all mirrors.

## Process qualifications (this round)
1. Pre-commit preliminary full-suite run executed as a managed background handle before A/B existed (deviation from the order's "no extra background suite" in the final-gate section): actual terminal outcome 2 failed / 5471 passed / 28 skipped, exit 1, on the dirty pre-A tree (the two state-dependent provenance tests, correct fail-closed behavior pre-commit; exact captures + process metadata preserved in W18i run-precommit-v1). It is never a final pass; the ordered exact-15 is the gate evidence.
2. Two PR-body verification captures were first written under /tmp (deviation from "No manual/tmp"); exact bytes preserved verbatim with hashes in W18i pr-body-verification; no /tmp evidence used thereafter.
3. The 018-h process qualifications (12-worker-ack/13-ROOT-error-pair capture-overwrite uncertainty, executed E-F scratch `sed -i` mutation, extra detached 077 suite interruption + appended status note, detached control-wait/managed receipt adoption, report-omitted standalone fields) stand in the 018-h report and the append-only `oap/REPORT-CORRECTIONS.md` addendum committed in A.

## Known limitations/blockers
- I9 UNREACHED: four post-refresh NEW-root mixed-bundle controls are refused by the UNMODIFIED public H acquisition before I (original harness failure + exact captures preserved; not relabeled); the I9 filter is proven over reachable stale-root/bootstrap-compatible shapes.
- Inert slice: never active in the adapter runtime; all v1 runtime criteria remain NOT RUN.
- 018-h accepted only at its bounded scope; whole 018 still unmerged.

## Recommended strategic follow-up
Factual only: whole-018 criterion audit precedes merge; 019 RAM, 020 recovery, 021 tokenizer/compiler, 022 wire, 023 fullstack, 024 actual-model qualification remain mandatory. Strategy decides scope and any old-H rework for the UNREACHED shape.

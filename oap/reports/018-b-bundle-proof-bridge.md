# OAP Coding-Agent Report — 018-b

## Work order
- Identifier: 018-b; order: `oap/orders/018-b-bundle-proof-bridge.md`
  (22855 B, unchanged activated bytes); numeric objective 018
- PR mode: AMENDED_EXISTING_PR (PR 26, branch `oap/018-cache-graph-bundles`)

## Status
COMPLETE (at the ordered inert-slice scope; a claim, never acceptance)

## Executive summary
Implemented the ordered inert bundle-proof bridge slice: typed
bundle-proof models plus a pure collector with public
`observe_bundle_proof`/`observe_bundle_proofs`, self-contained
whole-bundle source proofs (exact aggregate bytes/text, ordered
segments, original carrier/piece spans and call/result positions/IDs),
the finite unique-marker partition proof, bridge-owned cumulative
preflight ledgers, the dual path-bound law, and the same-occurrence
consistency (seam) law — including the inherited 018-a
conflicting-root-path-read law (proven single-occurrence root-path
digest differing from the established root digest refuses
`root_conflict`/`COMPETING_ROOTS` with no retained bundles; boundaryless
or repeated groups never infer a root hash). New versioned contract, 88
pure no-host-IO tests, docs/ledger/architecture reconciled. After a
material mid-round source correction (the root-path law, A2), the final
head B2 passed the full 15-command gate, all TEN checks, and the
clean-archive BOTH-artifact proof. Published per the order's standard
autonomous publication authorization (the 018-a four-hash pre-approval
procedure is historical).

## Authoritative GitHub state
- Repository: ulfe-lmi/slaif-local-coding; PR 26
  https://github.com/ulfe-lmi/slaif-local-coding/pull/26 OPEN
- Base: main `ffaabf4b4d9ce3a9cb7a48e12ab7d8847999adef`; head branch
  `oap/018-cache-graph-bundles`
- Starting remote SHA this round:
  `96afcb243759a395b1bbb86b8befcf847fcb640a` (018-a SELF, sole parent
  B2 `06ca21c5ff477c8cb895a39525f520bad3db288b`)
- Implementation commits pushed before report:
  - A  `815e60ac04b06bf0d335b56d535a99fcda66717f` (12 files: bridge
    modules, 77-test suite, contract, docs, order/active bytes)
  - A2 `944ea6efc18fedfb59d8b1cf362a79068be84239` (3 files: the
    conflicting-root-path-read law + 11 regressions + contract wording)
  - B  `5db59908dd9749c2144f2de2bd91e5d258f3b4de` (manifest-only at A;
    SUPERSEDED by B2 after the material A2 change, preserved)
- Implementation head SHA: 08cf6b3762af111a2d933c002dfe6015c8b8a2b5
  (B2, manifest-only at A2: 221 inputs, wheel `41a7d2e4…`, sdist
  `5446239b…`)
- Report publication commit: SELF
- New PR this round: NO; amended existing PR 26: YES; merge performed: NO
- PR title/body updated for 018-a accepted + 018-b scope (incl. the
  root-path law and 88-test count); server bytes verified

## Changes and files
- A (12 files): `bundles/bundle_proof.py` (new, ~1900 lines),
  `bundles/bundle_proof_models.py` (new, 732), `bundles/__init__.py`
  (+exports), `tests/test_bundle_proof.py` (new, 1822 lines),
  `docs/CACHE-BUNDLE-PROOF-CONTRACT.md` (new, 328), ledger,
  ARCHITECTURE-for-agents.md (+ compact mirror), ARCHITECTURE.md,
  TESTING.md, `oap/active`, `oap/orders/018-b-bundle-proof-bridge.md`
- A2 (3 files): `bundle_proof.py` (+25), `test_bundle_proof.py` (+148,
  11 regressions), `CACHE-BUNDLE-PROOF-CONTRACT.md` (+10, section 2)
- B/B2 (1 file): `packaging/dev_provenance_manifest.json`

## Acceptance evidence (pointers)
- Gate b2 (authoritative, B2): 15/15 commands rc=0 with per-command
  direct exits + driver log 03:10:39Z→03:21:06Z, driver 2350024,
  `gate.exit=pass`, wrapper terminal exit 0. cmd07 full suite under
  nonroot child process-local umask 022: **4035 passed, 28 skipped**
  in 615.94 s, direct exit 0.
- Gate b1 (B, 4024/28) and clean-build-b1/proof (PASS at B) are
  SUPERSEDED by the material A2 change; preserved untouched at their
  labeled W18b paths (evidence index).
- Clean archive B2 BOTH-artifact proof: 804 files; all assertions
  PASSED, direct exit 0 — 221 manifest inputs == Git A2/B2/clean tree;
  219 sdist entries (218 source + generated PKG-INFO); 44 wheel (38
  runtime + 6 dist-info) with strict unique RECORD coverage;
  PKG-INFO==METADATA; entrypoints/LICENSE/NOTICE; repo/clean/manifest
  hash+size equality.
- ROOT independent B2 artifact audit: ACTUAL PASS, direct exit 0
  (script `probes/018-b-artifact-independent-v3.py`, run capture
  `probes/018-b-artifact-run-v2.status.json`; ROOT-executed, labeled
  as such) — 804 archive files, 221 manifest inputs == Git A2/B2,
  strict unique RECORD, PKG-INFO==METADATA 22728 B.
- TEN checks at B2 `08cf6b37`: test, docker, docker-published,
  operator-session, gateway-contract, cache-native-fixture,
  cache-native-containment, CodeQL, Analyze (python), Analyze (actions)
  — all completed/success.
- ROOT-executed probes (labeled ROOT-executed, not coding runs):
  root-path consistency v1 24 PASS/12 FAIL at B1 (the defect), v2
  post-fix 233/233 PASS: the combined 78 extended root-path + 51
  contract + 104 public cohort executed against the pre-format
  (pre-A2) source at stable collector 088f9450; A2 AST equivalence
  reviewed by ROOT (committed root-guard AST exactly equal, other 16
  source files byte-identical); the 233 probe was NOT re-run at
  A2/B2.
- 017 ACCEPTED/merged at `ffaabf4b` under its bounded qualifications
  (`reviews/017-am-decision.md`; report
  `oap/reports/017-am-native-single-and-original-syntax-evidence.md`).
  018-a ACCEPTED at its bounded inert graph-foundation scope WITH
  PROCESS QUALIFICATIONS (`reviews/018-a-decision.md`; canonical report
  `oap/reports/018-a-cache-graph-foundation.md`).

## Verification
- `uv lock --check` / `uv sync --frozen --extra dev` / ruff check /
  ruff format --check / `mypy src tests` / docs_consistency_check:
  PASSED (gate b2 cmd01–06, direct exits 0)
- `uv run --frozen pytest -q` (child umask 022): 4035 passed,
  28 skipped, direct exit 0
- `uv build` + artifact_policy_check --inspect / --install-smoke:
  PASSED (cmd08–10)
- `dev_provenance_manifest.py --verify --dist dist`: PASSED (cmd13)
- bash -n oap/bin/*.sh packaging/*.sh; `git diff --check ffaabf4b… HEAD`:
  PASSED (cmd14–15)
- focused pre-commit A2 checks (pytest test_bundle_proof 88 tests,
  ruff check, ruff format, mypy, docs): all PASSED after two mechanical
  style fixes (first-run ruff failures preserved under focused-b2/)

## Live model/service evidence
None ordered, none performed. No live vLLM/gateway calls; no protected
fixture touched; known-synthetic fixtures only; no client/model startup.

## GitHub CI / required checks
All TEN required checks SUCCESS at implementation head B2 before the
report commit (see Acceptance evidence). Report-head checks may be
pending at push time; strategy verifies.

## Local setup/dependencies
Repo-local `.venv` via `uv` frozen (Python 3.12); NO new dependencies;
no services; no sudo used.

## Documentation
`docs/CACHE-BUNDLE-PROOF-CONTRACT.md` (new versioned contract, incl.
the explicit section-2 conflicting-root-path-read rule),
`docs/CACHE-REWORK-LEDGER.md`, `ARCHITECTURE-for-agents.md` (3 compact
mirrors byte-equal), `ARCHITECTURE.md`, `TESTING.md`; PR26 title/body.

## Safety/scope confirmations
- Unrelated files staged: NO (explicit path staging only)
- Secrets/raw customer content in report/evidence: NO
- Protected 18020/Qwen/Codex fixture changed: NO
- Extra objective PR: NO; coding merge: NO; auto-merge: NO
- Active/order bytes edited: NO (committed unchanged)
- Report commit report-only: YES (sole parent literal B2)
- No live upstream/model/Codex E2E; bounded fake fixtures only

## Known limitations / process qualifications
1. The slice is INERT: no v1 runtime, no G03 admission, no
   compiler/cache-hit claim. Remaining numeric-018 scope (018-c+:
   G03–G05, C01/C02/C04–C06, remaining S01) and objectives 019–024
   (RAM 019, recovery 020, tokenizer/compiler 021, transactional wire
   022, full-stack 023, actual-model/genuine-client 024) remain
   mandatory unearned stages.
2. 28 skipped tests: pre-existing honest skips, unchanged across
   rounds; individual skip reasons are not enumerated in this report.
3. Gate b1 driver prep metadata bugs (preserved in b1 artifacts, fixed
   in b2 preparation, never patched on a live run): `$20`-vs-`${20}`
   start_ticks (bogus value preserved), child meta `cat /proc/self/stat`
   measured `cat`, `$CAP` not exported → child meta redirect
   `/gate-driver-meta.json: Permission denied` (preserved in b1
   gate-cmd07.err; b1 child uv/pytest birth came from independent live
   observations by ROOT and coding), nested awk btime quoting. b2
   driver fixed all four in preparation and passed a metadata-only
   own-child rehearsal (8/8 field checks) before launch; b2
   driver/child meta are fully coherent.
4. b2 live observation: the kernel `children` file returned EMPTY for
   uv 2350198 while pytest 2350206's own PPid=2350198; the chain
   driver→uv→pytest is proven by each process's OWN /proc stat PPid
   fields (recorded in gate-live-observation-v2.txt; the first
   observation file with a `$20` slip is preserved as v1-faulty).
5. A pre-commit development full-suite run (before A) was piped
   (`pytest -q | tail -3`): its pytest exit is UNKNOWN / terminal-
   unmeasured; the authoritative recorded results are the direct-exit
   gate cmd07 runs above.
6. B1-era manifest-generation captures were written to
   `/tmp/w18b-manifest-generate.{out,err}` (outside W18b); actual modes
   preserved, no retroactive chmod. The A2/B2 generation was captured
   under W18b/focused-b2/. Two W18b probe JSONs remain at actual mode
   0664 (prior 077 subshell covered mkdir only); preserved, no chmod.
7. The B1 gate/clean-build/proof evidence is preserved but SUPERSEDED
   by the material A2/B2 refresh (order: never relabel previous
   results).
8. The 233-check ROOT probe runs are ROOT-executed (labeled as such)
   against the pre-format (pre-A2) source; the coding-side equivalent
   coverage at B2 is the 88-test repository suite plus the gate b2
   full suite.

## Recommended strategic follow-up
- Review/accept the 018-b inert slice at its bounded scope (contract,
  tests, gate b2, clean proof, and the root-path law above).
- Continue numeric 018 with the next ordered suffix (admission/
  identity/version scope), then objectives 019–024.

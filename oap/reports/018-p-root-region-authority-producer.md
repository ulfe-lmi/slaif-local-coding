# OAP Coding-Agent Report — 018-p

## Work order
- Identifier: 018-p; order path `oap/orders/018-p-root-region-authority-producer.md`
  (SHA256 b57d4c9af0d97751f30a27c39b0e3f3d52060fcdcfe77d92a9c386c08daf8ffc);
  numeric objective 018.
- PR mode: AMENDED_EXISTING_PR (PR 26, branch `oap/018-cache-graph-bundles`,
  base `main`).

## Status
COMPLETE

## Executive summary
Delivered the separate explicitly versioned PURE root-region
producer/validator/authority/selection surface: new modules
`root_region_lineage_models` / `root_region_lineage` under
`src/slaif_local_coding/constitution/bundles/` with the new
`cache-root-region-lineage/v1` / `root-region-lineage-policy/v1`
contract and the `read_region` provenance kind, plus the new
`docs/CACHE-ROOT-REGION-LINEAGE-CONTRACT.md`. Under this NEW contract a
genuinely issued, complete, uniquely attributable NEW root region inside
an ordinary mixed-only read acquires source evidence AND authority with NO
independent singleton; repeated/opaque/partial/truncated/nonzero/unpaired/
unsupported reads gain no new exception; fact-count and root-member-byte
retention is preflighted before materialization under the unchanged H
ceilings; ONE new-operation outer at the unchanged RootLineageBounds
couples the actual D work with independent inherited domains; the old H/O
law is intact and the existing old I honestly refuses the region-version
state. The slice is inert and PENDING strategic review at its bounded inert
scope: whole 018 remains open (the next same-018 consumer round must
consume the SAME legitimate new state into the actual graph/admission) and
019–024 remain mandatory.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`; PR 26
  https://github.com/ulfe-lmi/slaif-local-coding/pull/26 (open)
- Base: `main` at ffaabf4b4d9ce3a9cb7a48e12ab7d8847999adef (unchanged)
- Head branch: `oap/018-cache-graph-bundles`
- Starting remote SHA: 5ea518fa7eb340cfc197623185f529a49b1e4a93
  (the 018-o SELF, verified via `git ls-remote` and the GitHub API before
  mutation)
- Implementation head SHA: e7529448315837e2573cddac018822c5821a8258
- Report publication commit: SELF
- Implementation commits pushed before report:
  568144777d747f9e401c9d702383f031251e6803 (source A, 16 files) and
  e7529448315837e2573cddac018822c5821a8258 (manifest-only B, 1 file)
- New PR this round: no; amended existing PR: yes; merge performed: NO

## Changes and files
17 non-report paths across the two implementation commits.

Source commit A (16 files):
- NEW `src/slaif_local_coding/constitution/bundles/root_region_lineage_models.py`
  (typed records RootRegionLineageNamespace/State/Fact,
  RootRegionReadProvenance, RootRegionLineageTransition,
  RootRegionSelectionResult; closed actual-field fences; fixed non-echoing
  str/repr; the namespace factory `make_root_region_lineage_namespace`).
- NEW `src/slaif_local_coding/constitution/bundles/root_region_lineage.py`
  (public `bootstrap_root_region_lineage`, `observe_root_region_lineage`,
  `register_root_region_issuance`, `register_root_region_receipt`,
  `select_current_root_region`, `validate_root_region_lineage_state`; the
  private region-acquisition policy; the ONE new-operation outer).
- MODIFIED `causal_history.py` (a new private
  `region_root_acquisition` flag on the actual D lineage context,
  default `False`; the NEW region-acquisition policy is reached only
  through that private flag; public D schema and behavior unchanged).
- MODIFIED `bundle_proof.py` (private unique-root mixed acquisition
  gating inside the D observation, active only under the new private
  flag; no new public accessors).
- MODIFIED `current_root_composition.py` (the documented narrow explicit
  old-I rejection boundary for the region-version state, raised BEFORE
  any old positive work).
- NEW `tests/test_root_region_lineage.py` (223 cases; the durable A–L
  matrix over BOTH read endpoints and BOTH admission modes).
- NEW `docs/CACHE-ROOT-REGION-LINEAGE-CONTRACT.md` (the versioned
  root-region contract, 10 sections).
- MODIFIED `docs/CACHE-ROOT-LINEAGE-CONTRACT.md` (O ACCEPTED with process
  qualifications + region pointer), `docs/CACHE-CURRENT-ROOT-COMPOSITION-CONTRACT.md`
  (O ACCEPTED + the narrow old-I region-state refusal),
  `docs/CACHE-REWORK-LEDGER.md` (O accepted / P pending / 018-p clause),
  `TESTING.md`, human `ARCHITECTURE.md` (both status locations), and ALL
  THREE compact mirrors (repo `ARCHITECTURE-for-agents.md`,
  `oap/strategic-instructions/ARCHITECTURE-for-agents.md`, and the
  supervision S copy written in place — supervision inode 10638621 /
  UID 1001 / mode 0600 preserved; all three final copies byte-identical).
- Transcript: exact activated order file added and `oap/active` updated
  (strategic bytes committed unchanged).

Manifest-only commit B (1 file): `packaging/dev_provenance_manifest.json`
(262 inputs at source A).

## Acceptance evidence
### Criterion 1 — issued-descendant mixed-only positives, NO independent singleton
- PASSED. Test blocks A/B: bootstrap v1 plus a genuinely issued
  descendant mixed-only read with new complete root v2 plus nonroot
  source (root first/middle/last, Unicode/CRLF and genuine empty root),
  actual selected root v2, root byte length distinct from aggregate, exact
  original segment/member/carrier coordinates and original proof identity,
  on BOTH endpoints and BOTH admission modes — 223-case module matrix,
  literal exit 0, stderr 0 (protected W18p capture r24).

### Criterion 2 — frozen partial order (revert / historical / delayed / replay)
- PASSED. Test blocks B/C: new singleton and mixed region histories
  interoperate; genuine new-region v1-after-v2 deliberate revert selects
  the old bytes; known historical source retention; delayed old receipts;
  replay preserves exact prior state; equal-byte independent witness
  growth with per-pair identity on FINAL-state facts.

### Criterion 3 — authority law (unissued-unproven, conflicts, precedence)
- PASSED. Test block C: unissued mixed-only source stays
  ROOT_SOURCE_UNPROVEN with no governing authority; later actual
  issuance/receipt earns authority on the SAME retained state;
  incomparable differing regions conflict with no selection; genuine
  region descendant-of-all resolves; child-of-one cannot dominate;
  envelope-alone authorization refuses atomically; same-batch
  independently authorized region plus matching changed envelope respects
  deterministic refusal precedence.

### Criterion 4 — no-exception shapes and hard gates
- PASSED. Test blocks D/F/G/I/J: repeated-root operands including hidden
  opaque second operand; missing marker (MARKER_MISSING); truly
  unsupported grammar; pending/truncated/nonzero/unpaired retention with
  exact old semantics; wrong path/workspace; cross-namespace / coherent
  unsupported-version / CAS gates on ALL FOUR operations; malformed
  record/flags; detached proof/owner/segment/member/digest/length; exact
  inherited resource first-over and actual outer precharge negatives;
  privacy errors/reprs fixed and non-echoing on the tested representation
  surface.

### Criterion 5 — resulting states, original identity, honest old-I refusal
- PASSED. Test block E: resulting states support subsequent new-version
  registration, observation, validation and selection; original
  anchor/occurrence/proof identity by reference; the existing old I
  raises the documented fixed private ValueError at the first
  state-shape gate BEFORE any old positive work (typed fail-closed,
  tested); all old positive behavior/types/schemas/versions/recipe bytes
  intact.

### Criterion 6 — ONE new-operation outer and measured boundaries
- PASSED. Test block F: sequence work cap, bootstrap work cap with the
  MEASURED constructor-entry boundary (separately measured at-limit and
  one-below), fact-count cap across BOTH read provenance kinds, logical
  root bytes with a mixed aggregate strictly larger than the stricter H
  logical-root cap while root+anchor fits, independent inherited D/B
  domains and the diagnostics ceiling; real-class `__init__` counters
  preserve class identity; a first-over candidate allocates NEITHER the
  provenance NOR the fact.

### Criterion 7 — privacy and closed host-IO purity
- PASSED. Test blocks K/L: fixed non-echoing privacy law with
  NONROOT-body, ROOT-source and ID-field canaries over KNOWN SYNTHETIC
  fixture sources (the canaries prove the tested operational
  representation surface, not a blanket no-secrets claim anywhere); the
  closed 24-facility host-IO surface (filesystem/socket/process) trapped
  across the ENTIRE public path (factory, bootstrap, issuance,
  observation, validation, selection, receipt, replay, fixed refusals)
  with operational-representation canaries and unchanged canonical
  payload serialization.

### Criterion 8 — old H/O/I compatibility unchanged
- PASSED. 573 old H/O/I compatibility tests pass unchanged (unchanged
  product since focused-hoi-r11); the full gate cmd07 (5894 passed / 28
  skipped) includes them.

### Criterion 9 — documentation and mirrors
- PASSED. New contract + cross-references + ledger + TESTING + human
  architecture + all three compact mirrors updated; O recorded as
  ACCEPTED at its bounded inert scope WITH PROCESS QUALIFICATIONS
  (`S/reviews/018-o-decision.md`) with P PENDING and whole 018 open /
  consumer + 019–024 mandatory; `docs_consistency_check.py` clean (19
  claim docs); supervision mirror written in place preserving inode
  10638621 / UID 1001 / mode 0600.

## Verification
- `uv run --frozen pytest -q tests/test_root_region_lineage.py`: PASSED —
  223 cases, literal exit 0, stderr 0 (protected W18p capture r24;
  earlier draft captures r4/r6/r8/r15/r16 preserved as failures).
- Old H/O/I focused compatibility: PASSED — 573 tests, literal exit 0.
- `uv run --frozen ruff check .`: PASSED (clean).
- `uv run --frozen ruff format --check .`: PASSED (clean).
- `uv run --frozen mypy src tests`: PASSED (clean).
- `uv run --frozen python scripts/docs_consistency_check.py`: PASSED
  (clean, 19 claim docs).
- ONE foreground-managed exact-15 ordered gate at clean B
  `e7529448315837e2573cddac018822c5821a8258`: PASSED — all 15 literal
  exits 0 (gate.exit=pass); driver 1583793/birth301567748/PPID598258/
  umask 0077 at 13:10:59Z on a clean tree at B; cmd07 child 1583957 with
  process-local umask 0022, ACTUAL pytest 1583965/birth301567835/
  PPID1583957/UID1001 verified through the bounded owned driver/uv tree;
  cmd07 full pytest: 5894 passed / 28 skipped / 675.57 s / stderr 0;
  honest stderr lengths: cmd01 28 B, cmd02 30 B, cmd08 197 B (ordinary
  successful diagnostics), all others 0.
- ONE clean exact-B git-archive BOTH build: PASSED — archive / extract /
  build internal literal exits 0 (873 files); wheel 502409 B / 60
  entries (sha256 01ce8874d7fd6343d98a7debb8b4349f5c984f79120fac79f7d8fd9c6fe45ea4)
  and sdist 1874539 B / 260 entries (sha256
  c61c2ca228d6323ebdcb08fb4139b652ca2c7455ebbce68ec91b4fde52b21085)
  byte-equal the manifest. Qualification: the invocation was
  `bash build.sh 2>&1 | tail -25`, so the observed outer shell exit is
  the TAIL exit and the build driver's own literal exit is UNKNOWN (not
  rerun); the three internal step exits and all artifact bytes are
  independently verified (see Process qualifications).
- ONE strict artifact proof over the same clean-built artifacts (no
  rebuild): PASSED — literal exit 0, stderr 0, ALL PROOF ASSERTIONS
  PASSED; 873 Git/archive files, 262 manifest inputs, 260 sdist entries,
  60 wheel entries and all 59 non-RECORD rows checked, including
  metadata, entry points and licenses; scope/head/source-A labels
  correctly say 018-p (proof JSON
  `clean-build-artifact-proof-p1.json`, 0600; driver 1634483, umask 0077,
  13:29:59Z–13:30:05Z).
- Independent frozen-B synthetic probes (strategic, same commit): PASSED
  — 7 probes literal exit 0 / stderr 0 with stable before/after source
  hashes and clean unchanged B (producer APIs, causality,
  provenance/owner forgery, retention boundaries, privacy/purity;
  `S/reviews/018-p-frozen-probe-runs-v1.json`).
- GitHub CI at implementation head B `e7529448315837e2573cddac018822c5821a8258`:
  PASSED — all 10 checks completed/success: `Analyze (actions)`,
  `Analyze (python)`, `CodeQL`, `cache-native-containment`,
  `cache-native-fixture`, `docker`, `docker-published`,
  `gateway-contract`, `operator-session`, `test` (verified via the
  GitHub check-runs API; strategic durable record
  `S/reviews/018-p-B-CI-allgreen-v1.json`).

## Live model/service evidence
- NOT RUN. This round is an inert typed-module slice: no live model or
  service calls are required or authorized by the order, and no
  protected Qwen/vLLM/Codex fixture was touched.

## GitHub CI / required checks
- Implementation-head check state (B e7529448315837e2573cddac018822c5821a8258):
  all 10 checks `completed`/`success` — `Analyze (actions)`, `Analyze
  (python)`, `CodeQL`, `cache-native-containment`, `cache-native-fixture`,
  `docker`, `docker-published`, `gateway-contract`, `operator-session`,
  `test` (GitHub check-runs API; strategic durable record
  `S/reviews/018-p-B-CI-allgreen-v1.json`).
- All required green at drafting: yes (at B e7529448315837e2573cddac018822c5821a8258)
- Report-head checks may be pending; strategy verifies.

## Local setup/dependencies
- No new dependencies; `uv lock --check` and `uv sync --frozen --extra
  dev` pass in the gate (commands 1–2). Repo venv only. No sudo used this
  round.

## Documentation
- Updated (same PR): new `docs/CACHE-ROOT-REGION-LINEAGE-CONTRACT.md`;
  root-lineage contract (O status + region pointer), current-root
  composition contract (O status + narrow old-I region-state refusal),
  stage ledger, `TESTING.md`, human `ARCHITECTURE.md` (both status
  locations), and all THREE compact architecture mirrors (supervision
  copy in place, inode 10638621 / UID 1001 / mode 0600 preserved;
  final three copies byte-identical).

## Safety/scope confirmations
- Unrelated files: none touched; only the 17 in-scope non-report paths
  plus the report commit.
- Secrets/raw content: no real credentials, customer data or private
  corpus content observed in or included in the transcript, report or
  evidence this round; the K/L canaries are KNOWN SYNTHETIC fixtures that
  prove the tested fixed non-echoing representation surface, not a
  blanket no-secrets claim anywhere.
- Production/protected resources: protected 18020 / Qwen / Codex
  fixture changed: NO; no gateway, network, firewall or profile
  mutation; no model/native/client startup; no model calls.
- Required tests skipped: 28 explicit skips reported by the full suite
  (the same count as prior accepted rounds); the per-skip identities and
  reasons were not individually re-labeled this round, and no full
  rerun was performed solely for labeling.
- Scope: the implementation scope is preserved, with the process
  deviations listed under Process qualifications (no product-scope
  deviation). Extra objective PR: NO. Coding merge: NO.
- Active/order edited: NO (activated order bytes committed unchanged;
  order SHA256 verified before and after).
- Report commit report-only: yes (staged single path, verified at
  publication).

## Known limitations / process qualifications
Limitations (truthful):
- The slice is PENDING strategic review at its bounded inert scope; this
  report is a claim, not acceptance. No v1 runtime, model/client
  qualification, deployment, release or cutover claim is made.
- Whole 018 remains open: root currentness after uncertain root-bearing
  reads and the consumer round that consumes the legitimate new region
  state into the actual graph/admission are still pending; the 018-i..m
  repair-chain statuses remain as recorded; objectives 019–024 remain
  mandatory.

Process qualifications (this round, preserved; no blanket
prior-capture-discipline claim):
- 27 manual captures were first created 0664/0644 (writing shells and
  redirects missing the SAME-shell umask 077) and were restricted in
  place to 0600 without byte edit (the r12 pair and 25 lint/type
  captures). ROOT independently before/after-audited 19 of them
  (`S/reviews/018-p-preflight-capture-modes-v1.json`); the remaining 8
  rest on this worker's own evidence — no ROOT comprehensive audit of
  all 27 is claimed.
- The initial `captures/fence-debug-p1.out` diagnostic capture was
  created 0664 (the tee command omitted the SAME-shell umask 077; the
  Python child umask does not affect tee) and restricted in place to 0600
  (independent selection check
  `S/reviews/018-p-fence-diagnostic-mode-v1.json`, inode 12454190).
- The `manifest-p1.out` / `manifest-p1.err` captures were created 0664
  (manifest shell omitted the parent umask 077) and restricted in place
  to 0600 (`S/reviews/018-p-manifest-capture-modes-v1.json`).
- The first clean-build invocation used `bash build.sh 2>&1 | tail -25`;
  the observed outer exit is therefore the TAIL exit and the build
  driver's own literal exit is UNKNOWN (not rerun). The three internal
  archive/extract/build step exits are each literal 0 and the
  independent direct strict proof is literal 0; no rebuild was used to
  hide that qualification.
- Preserved draft failures (evidence, never rerun to erase): r4/r6
  draft-oracle/fixture failures; r8 was a missing test import PLUS an
  actual old-I internal ValidationError boundary defect on the
  unsupported region-version state, repaired by the documented narrow
  explicit guard (in-scope product code, NOT harness-only); r15
  (provenance class aliases replaced by counting functions broke
  isinstance) and r16 (aggregate==cap fixture) were harness-only.
  Preserved draft tooling failures, succinctly: the nested-`source_A`
  KeyError in this worker's own proof-JSON verification one-liner, the
  stale /tmp PR-body snapshot mismatch, and the expected exclusive-create
  refusals.
- The first focused driver ran `uv run` without `--frozen` (later
  drivers use `uv run --frozen`); that preliminary exit lives only in
  tool/TUI evidence (no exit sidecar file is claimed).
- The local tracking ref `origin/oap/018-cache-graph-bundles` was stale
  at the N SELF 22f927b3 because `remote.origin.fetch` maps only 005/017/
  main; resolved by an explicit ref fetch and cross-checked against
  `git ls-remote` and the GitHub API (live branch = O SELF 5ea518f, the
  order's starting point). No reset, force-push or remote config edit.
- The PR description was replaced with the concise strategic v1 body per
  ROOT direction (server body/title byte-verified after the structured
  PATCH); the previous exact 10934 B body is retained byte-identical
  under W18p (mode 0600, owner-writable; not enforced read-only).
- The gate driver's human comment records its mechanical-rebind lineage
  (from the 018-o o1 driver); its 15 actual command pins/paths/labels
  were verified correct against B e7529448 and no label-only rerun was
  performed.

## Recommended strategic follow-up
Factual only; strategy decides. Strategic review of 018-p at its bounded
inert scope using this report, the 7 independent frozen-B probes, the
exact-15 gate, the clean build + strict proof and the exact-B CI. If
accepted, activate the same-018 consumer round that consumes the
legitimate new region state into the actual graph/admission; whole 018
and 019–024 remain open/mandatory until then.

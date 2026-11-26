# OAP Coding-Agent Report — 022-b

## Work order
- Identifier: 022-b; order path `oap/orders/022-b-cache-pure-source-transaction.md`; numeric objective 22
- PR mode: AMEND_EXISTING_PR on the ONE existing PR 30
  https://github.com/ulfe-lmi/slaif-local-coding/pull/30, branch
  `oap/022-cache-source-replacement`, from report-only head
  `51e8d89ffc0e335594be6dcfddaa25662d817b49` and order-verified remote
  main `144af0bd5e34387afcb8e3f9ddf761eabd56e817`. No new PR, no merge,
  no auto-merge.

## Status
COMPLETE

## Executive summary
ACTUAL RESULT: the pure exact-span source-replacement and reference
transaction (docs/CACHE-IMPLEMENTATION-PLAN.md policy 12,
docs/CACHE-REWORK.md section 11) is implemented at source A
`336df36edf97d4f628c6cd8027914c35d965a329` on the same branch/PR 30,
amending the PR head from `51e8d89…` to implementation head B
`ed5215780f9051b80f104afa26e9e4cc94040a36` (manifest-only child). The
versioned `cache-bundle-replace/v1` pure transaction
(`src/slaif_local_coding/constitution/bundles/bundle_replace.py` +
`bundle_replace_models.py`) over ACTUAL 017/018/019/021 records:
(1) the edit plan is derived from the actual current decoded request,
the accepted 017 observations, the original 018-p proof/occurrence and
018-t admission witnesses and the actual prepared 021 working set; every
retained witness re-joins through ITS OWN owner proof bound to the same
original call ID, each piece re-joins through the CURRENT accepted 017
observation with exact re-proven digest/character/UTF-8-byte facts, and
genuinely absent carriers earn zero edits; (2) the closed carrier law:
the root content span excludes its delimiters and environment tail,
both accepted read endpoints are joined, and a governing root selected
through a read/read_region keeps its carrier a tool result with that
exact (occurrence, segment) coordinate skipped by the FILE join so the
same root region is never double-edited; repeated byte- and
scope-identical root envelopes are idempotent, each accepted same-scope
occurrence joined to its own carrier (a foreign-workspace same-bytes
envelope fails closed `CARRIER_UNRESOLVED` all-or-nothing);
(3) the two unambiguously versioned opaque marker kinds (live
reference; non-resolving evidence) authenticated with a domain-
separated standard HMAC under supplied private per-session key
material, scoped to the complete trusted namespace, original role,
exact occurrence or root-source identity and the segment/carrier
association, the wire exposing only the versioned kind tag plus the
fixed-length canonical base64url MAC tag; the closed replay scan gate
replays an accepted marker content-free at its shifted coordinates to
the fixed point while a stale live reference, forged, cross-namespace,
malformed, unknown-version, moved or kind-incompatible marker always
refuses; the marker claim stays at its earned scope (this pure round
verifies and re-joins markers and persists no new observation);
(4) the positive-supersession evidence law: a known positively
superseded original earns the non-resolving evidence marker only from
the ACTUAL same-run E overlay group facts (PROVEN_CHANGE on an admitted
path row with no KNOWN_CONTENT_CONFLICT/OWNERSHIP_AMBIGUITY blocker)
and the ACTUAL same-run P/Q root lineage — a retained unissued digest,
mere absence from selection or uncertain attribution never proves; the
eligible-source constraint keeps PROVEN_CHANGE on a never-admitted path
from removing anything (unrelated off-graph tool output stays
byte-identical); the old envelope's evidence identity is bound to the
immutable old source/anchor digest in the trusted workspace, never a
reconstructed old entry key; a prepared optional source omitted by the
accepted selection earns the same non-resolving marker, never a
dangling live reference; (5) all edits are planned and applied
atomically on a deep copy (the input is never mutated) preserving
roles, non-source text, wrappers, prefix/suffix, printed delimiters,
Unicode/CRLF outside the edits, images and every tool ID/name/
argument/status/order; native initial-EXEC and poll piece
associations are preserved and replayed through the CURRENT
process/proof per-piece source sub-spans; (6) every committed edit is
earned by the narrow durable-generation handoff (the ACTUAL accepted
`RecoveryPublishResult`/pointer and the EXACT retained
`RamStateSnapshot` by identity — a boolean or free integer never
establishes preparation); (7) the plan-13 typed all-or-nothing failure
families (nonusable selection and over-bound 422; missing/failed/
mismatched durability 503; span/marker/namespace conflicts 409); the
explicit entry-point guard paths are proven over ONE prepared fixture
(durable refusals with zero output and unmutated input; the VALID
source-absent pairing with zero edits carrying the exact prepared
selected compiled blocks and missing-binding guidance; the genuinely
unsupported/nonzero/truncated paired read unchanged under its own
limitation while the other eligible reads stay edited). In addition,
order item 6: the 022-a TOML migration privacy edge is fixed — under a
selected v1 profile a malformed explicitly supplied legacy `[cache]`
or `[constitution.rehydration]` field now rejects at the fixed
migration refusal without standalone nested validation and without
echoing either synthetic canary, while legacy profile loading is
unchanged (two real-TOML-path canary tests in `tests/test_config.py`).
`create_app`'s fixed v1 startup refusal is unchanged; the transaction
stays INERT (no wire/HTTP integration, no actual upstream tool
issuance, no recovery IO, no v1 runtime activation). Live model
inference and actual Codex qualification remain NOT RUN.

## Authoritative GitHub state
- Repository: ulfe-lmi/slaif-local-coding; PR 30
  https://github.com/ulfe-lmi/slaif-local-coding/pull/30 (state open)
- Base: main `144af0bd5e34387afcb8e3f9ddf761eabd56e817` (order-verified
  remote main, the accepted 021 merge)
- Head: oap/022-cache-source-replacement
  `ed5215780f9051b80f104afa26e9e4cc94040a36`
- Implementation head SHA: ed5215780f9051b80f104afa26e9e4cc94040a36
- Report publication commit: SELF
- Implementation structure: source A `336df36edf97d4f628c6cd8027914c35d965a329`
  (the 022-b transaction slice; the 022-b commits on the branch since the 022-a report-only head `51e8d89…`: `f67fd8c` activated order/active
  bytes (unchanged strategic bytes), `f11fcb4` migration-boundary law
  (order item 6), `b3f6038` read carriers + retained/current proof join
  + closed replay scan gate, `3d72306` positive-supersession predicate,
  `9398938` proof bridge + OVER_BOUND law + entry-point smoke,
  `78e138b` transaction replay surface, `4313e7d` repeated root-
  envelope idempotence, `336df36` the remaining in-scope transaction
  surface) and manifest-only B `ed5215780f9051b80f104afa26e9e4cc94040a36`
  (sole parent A; exactly `packaging/dev_provenance_manifest.json`
  changed; 313 source inputs; wheel `50f806c8…` 4,432,007 bytes; sdist
  `bcd86af1…` 6,113,810 bytes). The exact activated order bytes and
  `oap/active` are committed in the branch and published on the PR
  (blob sha256-verified against the working tree at B).

## Changes and files
At source A (10 paths: 3 new + 7 modified):
- `src/slaif_local_coding/constitution/bundles/bundle_replace.py`
  (new: the policy-12 pure transaction + closed replay scan gate)
- `src/slaif_local_coding/constitution/bundles/bundle_replace_models.py`
  (new: the contract models)
- `tests/test_bundle_replace.py` (new: 88 focused transaction tests
  over ACTUAL 017/018/019/021 records)
- `src/slaif_local_coding/config.py` (order item 6 migration-boundary
  law: under a selected v1 the legacy conflict-target sections bypass
  standalone nested validation and reach the fixed migration refusal
  first; the 022-a ruff-format line-wrap repair of the same function)
- `tests/test_config.py` (two real-TOML-path canary tests for order
  item 6; 143 focused config tests)
- `ARCHITECTURE-for-agents.md` (022-b compact paragraph at earned
  scope; the two objective-022 boundary lines; the 021-paragraph tail)
- `oap/strategic-instructions/ARCHITECTURE-for-agents.md` (byte-
  identical mirror of the compact map; the strategic-home mirror was
  synced to the same bytes outside the repository)
- `ARCHITECTURE.md` (delivery-status paragraph, both spots)
- `docs/ADAPTER-CONFIGURATION.md` (022-b status note; no configuration
  surface changed)
- `docs/CACHE-REWORK-LEDGER.md` (022 row scoped to evidence actually
  run)
At manifest-only B (1 file): `packaging/dev_provenance_manifest.json`
(source A 336df36; objective 022-b; 313 inputs). No other path changed
on the branch (the base→B diff is exactly the 10 listed paths).

## Acceptance evidence
### Criterion 1 (edit plan from actual records)
- Result: PASSED. The actual entry point derives spans from the
  decoded current request joined to the accepted 017 observations, the
  retained 018-p proof/occurrence and the 018-t witnesses; the focused
  fixture proves the four LIVE edits (root envelope content span
  excluding delimiters/environment tail, the two proven partitioned
  splices at their own segments, the singleton read), the read-root
  no-double-edit fence, the shared-entry distinct retained
  coordinates (partitioned A|B with B at segment 1 plus identical
  standalone B at segment 0, lean preservation of A and the printed
  delimiter), the boundaryless whole-bundle background splice, and the
  native multi-piece replay/moved-tag evidence through the CURRENT
  per-piece source sub-spans with Unicode/CRLF preserved. Evidence:
  `tests/test_bundle_replace.py` (88 passed at source A; re-proven at
  exact B by gate cmd07 rc=0).
### Criterion 2 (atomic, unmutated, durable-earned)
- Result: PASSED. All edits apply on a deep copy with the input
  byte-identical after every OK and every refusal; the durable-
  generation guard admits only the actual `RecoveryPublishResult`/
  pointer plus the EXACT retained snapshot by identity; missing/
  failed/mismatched generation or snapshot refuses the fixed
  `GENERATION_NOT_DURABLE` 503 with zero output and the input
  unmutated; all-or-nothing (one refusal refuses every planned edit).
  Evidence: the entry-point guard tests over ONE prepared fixture
  (durable family; source-absent pairing; unsupported/nonzero/
  truncated paired read) in `tests/test_bundle_replace.py`
  `TestEntryPointGuards`, 3 passed at source A, re-proven at exact B.
### Criterion 3 (two versioned opaque HMAC marker kinds; closed replay gate)
- Result: PASSED. Both kinds authenticate under the domain-separated
  HMAC scoped to namespace/role/occurrence-or-root-source/segment-
  carrier; the wire form exposes only the versioned kind tag plus the
  fixed-length base64url MAC tag (no source identities, no key
  material in any repr/error); the closed replay scan gate passes
  accepted replays to the fixed point and refuses stale/forged/
  cross-namespace/malformed/moved/kind-incompatible markers; accepted
  replay creates no second edit and changes no authority; ordinary
  text outside marker carriers keeps its own role. Evidence: the
  marker/gate tests (moved-tag, tampered, stale-live, historical
  idempotence, raw replay vs stale live token) in
  `tests/test_bundle_replace.py`.
### Criterion 4 (positive supersession + selection omission)
- Result: PASSED. The non-resolving evidence marker is emitted only
  for actually authoritative old facts from the ready same-run P/Q
  lineage plus the same-run E overlay group facts (PROVEN_CHANGE, no
  conflict/ambiguity blocker); a retained unissued digest, mere
  absence from selection or uncertain attribution never proves; the
  eligible-source constraint leaves off-graph tool output byte-
  identical; the old-envelope evidence identity is bound to the
  immutable old source/anchor digest (a second valid root change re-
  derives the same tag, never invalidating already-issued evidence);
  an omitted prepared optional source earns the marker, never a
  dangling live reference, with required content and exact
  missing-binding guidance retained. Evidence: the supersession-
  predicate tests (proven_change positive, ownership_ambiguity
  negative, absent-group-record negative, never-admitted-path
  negative), the three-edit retained-anchor replay test (current root
  LIVE in its read carrier + read LIVE + old authoritative anchor
  EVIDENCE, transformed replay verifying all three and refusing the
  stale live format) and the omission tests in
  `tests/test_bundle_replace.py`.
### Criterion 5 (selected blocks + missing-binding guidance carried)
- Result: PASSED. Every successful pure result carries the exact
  selected compiled blocks and actual missing-binding guidance; the
  source-absent pairing (a payload with neither root nor retained read
  carriers) returns OK with zero edits/markers and the payload
  byte-identical while carrying the exact prepared selected blocks and
  guidance; original root/FILE/greedy-background roles are preserved
  and off-graph content gains no system authority. Marker validation
  is usable before observation: `verify_marker` is the pure
  validation primitive (a valid transformed root or tool marker is
  never accepted as a new raw source proof and retains no stale
  compiled payload), and the request replacement path performs its
  geometry observation before its final replay scan; the actual
  pre-acquisition wiring into lineage/state is still unearned and
  belongs to the later same-022 application slice. Evidence: the
  marker-validation tests (valid transformed marker is not a raw
  source proof), the source-absent guard test and the working-set
  assertions throughout `tests/test_bundle_replace.py`.
### Criterion 6 (022-a TOML migration privacy edge)
- Result: PASSED. Under a selected v1 profile a malformed explicitly
  supplied legacy `[cache]` field and a malformed
  `[constitution.rehydration]` field each reject at the fixed
  migration refusal on the real TOML path, with neither synthetic
  canary present in the rendered error; empty/default versus
  explicitly supplied behavior and existing legacy loading are
  unchanged (regression suite 143 passed). Evidence: the two canary
  tests in `tests/test_config.py` (lines 991–1020) and
  `src/slaif_local_coding/config.py` `load_settings`.

## Verification
- Focused suites at source A (before the candidate freeze):
  `tests/test_bundle_replace.py` 88 passed; `tests/test_config.py`
  143 passed; the ordered app/selection regression
  `umask 022 && uv run --frozen pytest -q tests/test_config.py
  tests/test_app.py tests/test_bundle_selection.py` 212 passed, exit
  0; ruff check, ruff format --check, mypy (src tests) and
  `scripts/docs_consistency_check.py` (19 docs) clean before the
  freeze and re-proven at exact B by gate cmd03–cmd06 rc=0.
- 15-command locked gate at exact B (`gate-driver-022b.sh`, managed
  absolute-path invocation, run dir `gate-run1`, driver pid 1893489
  birth 375536883, ppid 598258, uid 1001, capture umask 077, driver
  source_sha256
  `123dbcf94a9548565555ef21cc9d30d68e3570ef4ade928340cb7db04ec7db7e`,
  started 2026-11-20T02:39:10Z, head `ed52157…`): ALL 15 commands
  rc=0 — cmd01 `uv lock --check`; cmd02 `uv sync --frozen --extra
  dev`; cmd03 `ruff check .`; cmd04 `ruff format --check .`; cmd05
  `mypy src tests`; cmd06 docs consistency; cmd07 full `uv run
  --frozen pytest -q` under umask 022 — 7076 passed, 28 skipped,
  16 warnings, 1491.91 s (0:24:51); cmd08 `uv build`; cmd09
  artifact policy inspect (no violations, `ok: true`); cmd10
  artifact policy install-smoke (fresh disposable venv, `ok: true` —
  the required supported Python 3.12 fresh noneditable install
  smoke, module imported from the disposable venv only); cmd11
  Python 3.12.15; cmd12 compileall; cmd13
  `dev_provenance_manifest.py --verify --dist dist`; cmd14 shell
  syntax; cmd15 `git diff --check 144af0bd… HEAD`. PASSED.
- TEN required exact-B GitHub checks at `ed52157…`: ALL pass —
  test (pass, 13m7s), Analyze (actions) (pass, 39s), Analyze
  (python) (pass, 1m18s), CodeQL (pass, 2s), cache-native-
  containment (pass, 33s), cache-native-fixture (pass, 1m36s),
  docker (pass, 1m51s), docker-published (pass, 1m19s), gateway-
  contract (pass, 21s), operator-session (pass, 1m5s). Exactly two
  first-attempt workflow runs on this SHA (44658332028,
  44658335218), both `success` — no failures, no retries. All
  required green at drafting.
- Clean exact-B archive, one clean build (`build-022b.sh`, run dir
  `clean-build-022b`, fail-closed no-overwrite guards): git archive of
  B (38,543,360 bytes, 949 files), extract and `uv build` exit=0 with
  BOTH artifacts byte-identical to the manifest (wheel
  `50f806c89023554ec0d949bbbd0b25a28c1f879570387ac0c6ed0587b9856d6f`,
  4,432,007 bytes, 87 entries; sdist
  `bcd86af1247a8ce7942aae30cf369a2193c14bd284735da9484e5744151495d4`,
  6,113,810 bytes, 311 entries); fresh NONEDITABLE install of the
  clean-built wheel into a venv created by the EXPLICIT Python 3.12
  interpreter `/home/janezp/.local/bin/python3.12` (3.12.15) exit=0
  with import probe (version 0.1.0, module resolved inside the
  disposable venv only, probe records interpreter `3.12.15 (main, Oct
  9 2026, 15:22:32) [Clang 22.1.3 ]`, console entry point present).
- Full clean-archive BOTH artifact proof (`artifact-proof-022b.py`,
  `clean-build-artifact-proof-022b.json`): ALL PROOF ASSERTIONS
  PASSED — 949 clean-archive files byte-identical to Git B (full path
  set); 313 manifest source inputs byte-identical to the ORIGINAL Git
  A, to Git B and to the clean tree; B manifest-only (sole parent A,
  exactly the manifest path changed); every sdist entry
  allowlisted-generated (one, PKG-INFO) or byte-identical to Git B;
  every wheel runtime entry byte-identical to Git B `src/`; wheel
  RECORD exactly covers the entry set with per-entry sha256 digest
  and size (unique raw rows, no collapsing); PKG-INFO bytes equal
  wheel METADATA bytes; entry_points equal pyproject
  `[project.scripts]`; LICENSE/NOTICE byte-identical; repo gate
  `dist/` artifacts byte-identical to the clean artifacts; fresh
  install interpreter recorded as 3.12.15.
- Live model inference: NOT RUN (protected Qwen/18020 fixture
  untouched; no dev service started). Actual Codex qualification:
  NOT RUN. No registry publication, deployment, benchmark or
  cutover. No merge, no auto-merge.

## Live model/service evidence
- NOT RUN. The protected Qwen/18020 service, profiles, launch/systemd,
  keys and network state were not touched; no bounded live call was
  made this round; the protected fixture is unchanged.

## Local setup/dependencies
- Repo-local uv frozen environment (Python 3.12.15) for the gate;
  `/home/janezp/.local/bin/python3.12` (3.12.15) for the explicit
  fresh noneditable install venv; no new dependencies; no sudo; no
  durable configuration change.

## Documentation
- Updated in this round (same PR): `ARCHITECTURE-for-agents.md` (new
  022-b compact paragraph at its earned scope, including the marker-
  claim scope limit and the read-root no-double-edit fence; the two
  objective-022 boundary lines and the 021-paragraph tail updated so
  022-b is PENDING strategic review and the later same-022
  application wiring plus 023-024 remain unearned); its byte-
  identical mirrors (`oap/strategic-instructions/ARCHITECTURE-
  for-agents.md` in the repo; the strategic-home mirror synced to the
  same bytes); `ARCHITECTURE.md` (delivery-status paragraph, both
  spots); `docs/ADAPTER-CONFIGURATION.md` (status note; no
  configuration surface changed and the `create_app` refusal is
  unchanged); `docs/CACHE-REWORK-LEDGER.md` (022 row scoped to
  evidence actually run). No new planning or audit documents.

## Safety/scope confirmations
- Unrelated files: none. The branch diff from the 022-a report-only
  head `51e8d89…` to B is exactly the 10 source/doc paths listed
  above plus the manifest at B, plus the two activated transcript
  paths committed unchanged from the strategic authoring (`oap/
  active` `022-a`→`022-b` and the new
  `oap/orders/022-b-cache-pure-source-transaction.md`); cmd15
  `git diff --check 144af0bd… HEAD` clean.
- Secrets/raw content: none committed, printed or reported (evidence
  uses hashes, counts, command names and statuses only; synthetic
  session key material stays inside the test module).
- Protected 18020/Qwen/Codex fixture changed: NO.
- Required tests skipped/not run: live inference and actual Codex
  are ordered NOT RUN; nothing required was skipped.
- Scope deviation: none; `create_app` refusal kept; no wire/HTTP,
  recovery IO or v1 runtime activation added.
- Extra objective PR: NO. Coding merge: NO.
- Active/order edited: NO (committed bytes verified unchanged).
- Report commit report-only: yes (pending the SELF commit).

## Known limitations/blockers
- The v1 runtime remains unwired by design: `create_app` refuses a
  selected v1 profile; the 022-b transaction is a pure, inert
  payload/reference and compiled-context pairing. No upstream-body,
  readiness, recovery-IO or v1 runtime qualification is earned; the
  full R01–R05/S01–S02 actual-upstream evidence and the same-022
  application wiring (plus 023-024) remain mandatory later stages
  (NOT RUN).
- This report is a claim until strategic review; no acceptance or
  merge is claimed.

## Recommended strategic follow-up
Factual only: strategic review of 022-b at its bounded pure-
transaction scope; the next same-022 slice is the application wiring
(HTTP integration, upstream tool issuance, recovery IO, R01–R05/
S01–S02 evidence), then 023-024.

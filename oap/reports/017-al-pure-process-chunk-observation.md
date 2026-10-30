# OAP Round Report — 017-al: pure D09 process/chunk observation (inert)

Status: COMPLETE at the ordered pure-inert scope (all TEN required current CI
checks SUCCESS at B; 13/13 locked gate commands exit 0 with the disclosed
driver-continuation structure; independent artifact proof cited). The D09
actual-trace process-completion qualification remains NOT RUN (explicit later
scope). No merge, no auto-merge, no second PR; PR25 remains OPEN.

- Round: 017-al (AMEND_EXISTING_PR, numeric 017, PR25)
- Branch: `oap/017-cache-read-observation`, base main `96c790423f6f0097a56a0b12bacda8a9b6da6aba`
- Starting remote HEAD: `2498503865c8b8ae4bca20bbd9283dc999644a1c` (017-ak report-only SELF)
- Repository: https://github.com/ulfe-lmi/slaif-local-coding; PR: https://github.com/ulfe-lmi/slaif-local-coding/pull/25 (OPEN)
- Activated order: `oap/orders/017-al-pure-process-chunk-observation.md` (17736 B, SHA256 `d58663f451b8210dd3d7d4598cc1c5388597288b3aceebb53421610747a0d29f`, committed unchanged at A); `oap/active` = `017-al\n` (7 B, SHA256 `eef5cac75158f496cb5801cb48c19e38f935fb36f2f5cecf92fbf5ca45b3868c`) — order and active bytes unchanged at B (re-verified in the inventory; the verifier re-checks them at SELF)
- Implementation head SHA: a8697e4ddf7b2cb8631f071be2530d47ef579a5f
- Report publication commit: SELF

## Literal heads and changed scope

| commit | role | changed paths |
|---|---|---|
| `29a84374c4c6aae2eb4caff81e5f3fe88f83d7d4` (A, parent `2498503`) | implementation + docs + activation | 48 paths: 4 source, 5 docs, 3 oap, 33 fixtures, 3 tests |
| `a8697e4ddf7b2cb8631f071be2530d47ef579a5f` (B, implementation head) | manifest only | `packaging/dev_provenance_manifest.json` (parent A; A..B diff = exactly this file) |

Source (new D09 collector; in-memory pure, never wired into adapter execution):

- `src/slaif_local_coding/constitution/bundles/process_chunks.py` (NEW, +1376;
  61827 B, SHA256
  `b96fa1f7aabb4c238999c2940f8f022d78517caf82a4f35677cb38b3e496021b`): pinned
  native 0.164.0 exec-wrapper parser with bounded header preflight (line-count
  AND char-window; `WRAPPER_HEADER_OVER_BOUND` distinct from
  `MALFORMED_WRAPPER`), eligibility-independent owner inventory with
  negative-only ambiguity (competing owners are never silently dropped; an
  incomplete inventory returns the fixed nonacquiring overbound state),
  blocked-exec/orphan-poll origin law, the unassignable-arg orphan-poll law
  (window = exec ISSUE position < poll ISSUE position < terminal-RESULT
  position or none; any bounded own result record with a well-formed native
  header — running/final/unknown-status — invalidates the affected
  potentially-open chain; late delivery retained; duplicates never repair; no
  SID coercion; no inferred execution; `PROCESS_CHAIN_CONFLICT`), poll
  argument law, chain law, occurrence hash law, absolute-offset region
  mapping, and linear digest assembly.
- `src/slaif_local_coding/constitution/bundles/observation_models.py`
  (263-line delta; SHA256
  `c715203f2e069deb28962f6ba5a5e3c20fcd42090d64bee5c58f760634c5e4eb`):
  `OBSERVER_VERSION = "cache-bundle-observation/2"` version law (additive),
  `NativeWrapperFacts` / `ProcessPiece` / `ProcessPoll` / `ProcessObservation`
  models, `ProcessOutcome` additions (four new `process_*` limitations:
  `process_session_conflict`, `process_poll_invalid`, `process_chain_conflict`,
  `process_truncated`; plus `wrapper_header_over_bound`), additive
  `ObservationReport.processes` (default empty) and five new
  `ObservationBounds` fields with fixed defaults; operational str/repr
  redaction at the nested model level.
- `src/slaif_local_coding/constitution/bundles/observe.py` (+18): public
  composition runs the process collector and attaches the result to the
  report.
- `src/slaif_local_coding/constitution/bundles/__init__.py` (exports, 29-line
  delta).

Fixtures: 5 NEW `process_*` files (SYNTHETIC-DERIVED pinned 0.164.0 frames,
explicitly labeled) + 28 pre-existing fixtures changed ONLY in their
`parser_versions.observer` declaration (`cache-bundle-observation/1` → `/2`);
no recorded request/response content changed in any pre-existing fixture.

Tests: `tests/test_bundle_process_chunks.py` (NEW, 82 tests in 9 classes:
`TestNativeWrapperParser`, `TestPollArgumentLaw`, `TestChainLaw`,
`TestUnidentifiedPollLaw`, `TestIdentityCollisions`, `TestBounds`,
`TestRegionAndDigests`, `TestComposition`, `TestPrivacy`);
`tests/test_bundle_observation_models.py` (2-line delta);
`tests/test_bundle_observe.py` (6-line delta).

Docs: human `ARCHITECTURE.md` (concise current-status paragraph; collector
earned pure inert; actual-trace + native-single gaps explicit);
`ARCHITECTURE-for-agents.md` compact — ALL THREE copies byte-equal 41933 B
SHA256 `cd213873f794c8bfb2d47d9689c417050d6261f584b21ff994703ecd47afaaff`
(repo, tracked `oap/strategic-instructions/` copy, strategic-home synchronized
in place with inode 10638621 / mode 600 preserved); `TESTING.md` (D09 suite
sentence + CI-table row); `docs/CACHE-OBSERVATION-CONTRACT.md` (new section 5a
process/chunk law incl. the corrected Polls negative-uncertainty rule and the
five-limitation version paragraph; section 7 vocabulary; section 8 fixed
defaults + preflight; section 9 `<private-id>` privacy; section 10
SYNTHETIC-DERIVED fixture provenance; section 11b D09 row: 82 focused tests /
9 classes / `TestUnidentifiedPollLaw` public, NOT RUN tail);
`docs/CACHE-REWORK-LEDGER.md` (D09 row PARTIAL with earned/carry states; 017
status row: 017-a..017-ak published while 017-al active).

## Typed interface, version, bounds, compatibility

- Entry: the PUBLIC `observe_request` (Responses and Chat supported domains);
  the report gains the additive `processes` field. Every `/1` field keeps its
  exact meaning and single-result behavior.
- Format identities: pinned native `codex-native-exec-wrapper/v1` (distinct
  from the legacy `codex-exec-wrapper/v1`, whose source-is-source law is
  preserved exactly); process grammar `process-chunk/v1`.
- Observer version: `cache-bundle-observation/2`. Old `/1` reports remain
  loadable (new fields take empty defaults). `/2` output carries `processes`
  and requires a `/2` consumer: raw `/1` and `/2` reports are not equal
  modulo `observer_version` alone — the additive-field projection (drop
  `processes`) is the accurate comparison.
- Fixed bounds (documented defaults, fail-closed overbound refusal):
  `max_process_sessions=4`, `max_process_polls=12`, `max_process_pieces=13`,
  `max_process_source_chars=1_000_000`, `max_process_source_bytes=1_000_000`
  (cumulative UTF-8 byte bound checked on bounded original-string ranges
  before copying/retention).
- Privacy: private call/process/session IDs are exact internally but all
  str/repr suppress values with fixed placeholders, including nested
  `NativeWrapperFacts` / `ProcessPoll`; no raw source or IDs in
  logs/metrics/errors; payload stays byte-for-byte structurally unchanged;
  no hidden persistent process registry, cross-request cache, or replay owner.

## Verification

Execution-head honesty: the focused/bundle/probe results below are
DEVELOPMENT-time invocations made before the A/B commits; source identity
is stated per batch, with no blanket all-development-source claim: the
collector `process_chunks.py` (SHA256 `b96fa1f7…`) is byte-identical to
the A/B source in every one of them; the coding-authored focused-82,
bundle-672, and final 94-case runs additionally bind the final
`observation_models.py` (SHA256 `c715203f…`, byte-identical to A/B) as
recorded in their state snapshots; ROOT's 87-capture package ran at the
same collector but at `observation_models.py`
`fa9aa785fac2b40345b02d109c545b48305cc88a1017a61f8c58d0602482a8e2` — a
mid-development model version from before the final docstring correction
(final B models is `c715203f…`). Nothing was re-run at B merely to
relabel it; the later model docstring update plus the full frozen pytest
and the 13-command gate at clean B cover the final state. The gate, CI,
and clean-build facts are measured AT B (`a8697e4d`, clean tree).

### Focused and suite checks (development invocations; re-covered by the full B pytest)

- 82/82 focused tests in `tests/test_bundle_process_chunks.py` PASS
  (development invocation before A; `TestUnidentifiedPollLaw` exercises
  the PUBLIC `observe_request` composition (responses + chat endpoints);
  low-level parser/bounds cases stay direct).
- Bundle suites (`tests/test_bundle_*.py`): 672 PASS (development
  invocation after final source, before the A/B commits).
- The static checks were ALSO executed at B as gate commands 03-06:
  `ruff check` clean; `ruff format --check` (600 files already formatted);
  `mypy` 124 source files, no issues; docs consistency OK (19 claim docs
  checked).

### Adversarial probe battery (development-time; 94 = 87 PUBLIC composition + 7 DIRECT entry; 94/94 at source b96fa1f7)

- 7 (direct serial entry; the 7-case script defaults to DIRECT, per its
  own captured `entry=direct`) + 26 (public extended) + 43 (header-owner
  matrix) + 3 (poll-claim standalone, incl. the two independent valid
  chains control) + 15 (unidentified-poll v3, incl. the two chronology
  controls: late-delivery invalidation and pre-future-exec isolation) =
  94 PASS. ROOT's 87 public captures are the independent verification at
  the same collector (`b96fa1f7…`), with its
  `package_sources.observation_models.py` at `fa9aa785…` (mid-development,
  before the final docstring correction; final B models is `c715203f…`,
  covered by the later model docstring update and the full B gate — no
  probe rerun or relabel). The coding-authored 94-case snapshot is
  mixed-scope (87 public + 7 direct), not 94 independent ROOT/public
  cases; its final batch at models `c715203f…` supports the final model
  as recorded.
- ROOT independently verified the same source: v3 15/15
  (`reviews/017-al-unidentified-poll-run3.*`), header matrix 43/43
  (`reviews/017-al-header-owner-matrix-run4.*`), extended 26/26
  (`reviews/017-al-public-extended-run7.*`), poll-claim 3/3
  (`reviews/017-al-poll-claim-standalone-run6.*`), package hash stable
  throughout. Coding-authored same-source state snapshots:
  `reviews/017-al-battery-run-at-b96fa1f7.json`,
  `reviews/017-al-battery-final-state.json` (0600).
- All probe inputs are synthetic: the five new `process_*` fixtures are
  SYNTHETIC-DERIVED from the closed AJ 0.164.0 wrapper evidence; the
  pre-existing fixtures retain their earlier original provenance (only
  the observer-version metadata changed). This is NOT full D09
  qualification.

### Locked 13-command gate (at B, clean tree; each command captured separately; protected 0700 WAL run dir, explicit 0600 captures)

1. `uv lock --check` — PASSED (exit 0)
2. `uv sync --frozen --extra dev` — PASSED (exit 0)
3. `uv run --frozen ruff check .` — PASSED (exit 0, "All checks passed!")
4. `uv run --frozen ruff format --check .` — PASSED (exit 0, 600 files already formatted)
5. `uv run --frozen mypy src tests` — PASSED (exit 0, 124 source files)
6. `uv run --frozen python scripts/docs_consistency_check.py` — PASSED (exit 0, 19 claim docs)
7. `(umask 022) uv run --frozen pytest -q` — PASSED (exit 0): **3745 passed, 28 skipped in 613.11 s**
8. `uv build` — PASSED (exit 0, continuation)
9. `uv run --frozen python scripts/artifact_policy_check.py --dist dist --inspect` — PASSED (exit 0, continuation)
10. `uv run --frozen python scripts/artifact_policy_check.py --dist dist --install-smoke` — PASSED (exit 0, continuation)
11. `uv run --frozen python --version` — PASSED (exit 0, Python 3.12.15, continuation)
12. `uv run --frozen python -m compileall -q src tests oap/bin scripts` — PASSED (exit 0, continuation)
13. `uv run --frozen python scripts/dev_provenance_manifest.py --verify` — PASSED (exit 0, "development provenance OK: state=development head=a8697e4ddf7b", continuation)

Pytest mode law measured while live (bounded direct /proc reads of the known
attested PIDs only, no global scans): driver 513826 (birth 192362569, uid
1001, umask 0077, ppid 1 after setsid); uv 513972 (birth 192362642, uid 1001,
umask 0022, cmdline `uv run --frozen pytest -q`); pytest 513983 (birth
192362644, uid 1001, umask 0022, PPID 513972).

**Gate structure disclosure (material, preserved as measured):**

- (a) The gate was NOT a single uninterrupted driver run. The original driver
  aborted at line 94 — `gate.err`: "driver.sh: line 94: t0: unbound variable"
  — AFTER writing `cmd-07.exit=0` and the full pytest summary. Known
  diagnostic bug: the cmd-07 wall-time echo references `run_cmd`-local `t0`
  outside its scope under `set -u`.
- (b) The original driver's own shell exit code is UNMEASURED and is NOT
  fabricated; `gate.exit` remains 0 bytes (precreated) exactly as the
  original driver produced it.
- (c) Commands 08-13 ran ONCE in a separate immutable continuation driver at
  the same clean B. All refusal guards passed: exact HEAD B clean; original
  cmd 01-07 all exit 0 with full summary; original driver/uv/pytest
  authoritatively gone at their known births; no prior continuation execution
  recorded (a failed birth query is a refusal, not an absence; a repeat
  execution is refused). `continuation.exit=0` was written to its own file;
  the original `gate.exit` was left untouched.
- (d) The continuation was launched background setsid; ROOT's
  foreground-preferred instruction arrived while it was already executing.
  Disclosed, not relabeled.
- (e) The first terminal record
  (`gate-terminal-record.json`, preserved as initial snapshot) carried a
  mistyped 63-char continuation script hash; the corrected
  `gate-terminal-record-v2.json` computes every hash with hashlib over the
  actual files (continuation script `4f6e214d2b7e1b6d4be820eaf846df285c22c03503043f97614a133a5029b7fb`,
  original driver `25b837b7df3ca6064968f94f651108af4fb9fea689041a4c55bd7d1360186a94`).
  No gate rerun; all captures untouched.

### Artifacts, clean build, and independent proof

- Continuation cmd 08 `uv build` (exit 0) produced both artifacts in the repo
  `dist/`: sdist `slaif_local_coding-0.1.0.tar.gz` 1138229 B / 206 entries
  SHA256 `69d1e61a630dc2c4d834ebbdc9784a6cb245af72b204d465a0c9a549ec1e66cb`;
  wheel `slaif_local_coding-0.1.0-py3-none-any.whl` 162876 B / 38 entries
  SHA256 `e8cc0b97857718608679a488088dc48a8c53adfef3a6cdbfdea2040d5f68db4e`;
  cmd 09 inspect and cmd 10 install-smoke OK; cmd 13 manifest verify OK
  (manifest inputs = 208, bound to B).
- Independent clean build (protected WAL `clean-build1`, `build.sh`
  `413f556c…`, exact-B guard, fresh-path refusal, full stdout/stderr
  retention, true exits): exit 0 from `git archive` at B into a clean tree;
  BOTH rebuilt artifacts byte-identical to the repo `dist/`, the gate
  continuation artifacts, and the manifest.
- ROOT independent complete source + generated-metadata proof
  (`reviews/017-al-B-clean-artifact-review.json`): 208 manifest inputs
  clean/Git-B equal; all 205 sdist source entries byte-equal to Git B; all 32
  wheel runtime sources byte-equal to Git B (plus LICENSE/NOTICE); generated
  PKG-INFO == wheel METADATA (22728 B, METADATA SHA256
  `6203857c01e28f8449586465b0c775cbce78e793ad726a1f821c104eda297674`); all 38
  wheel RECORD entries validated; entrypoints equal pyproject. Read-only, no
  rebuild, no client/model/service execution.
- `sdist-proof.sh` (`dae4741e…`) was prepared under the WAL for exactly this
  source/generated-metadata proof but was NOT executed — the independent
  proof above covers it; no rebuild or rerun for the label.

### CI

ALL TEN required current-head checks SUCCESS at B `a8697e4d` (`test`,
`docker`, `docker-published`, `operator-session`, `gateway-contract`,
`cache-native-fixture`, `cache-native-containment`, `CodeQL`,
`Analyze (python)`, `Analyze (actions)`); ROOT saved
`reviews/017-al-B-all-ten-ci-success.json` (2026-10-29T21:59:29Z). These are
B-head checks, not SELF-head checks, and not acceptance.

## Provenance: actual versus synthetic-derived

- Only the FIVE NEW `process_*` fixtures are SYNTHETIC-DERIVED from the
  closed AJ actual attempt's verified known-synthetic selected 0.164.0
  wrapper evidence (attempt `65578d064ab7cc8e41b9a3f0ad266e3dd7119878`,
  run `e51da1e99c4341a48c6ca9f0e9ff62e6`), incl. pure-cat adaptations
  labeled as such. The 28 pre-existing fixtures retain their EARLIER
  ORIGINAL provenance; only their observer-version metadata changed
  (`parser_versions.observer` /1 → /2; no recorded content changed). No
  historical seeds or sources were recovered; no new actual native
  observation was made; no customer/private history or credentials touched.
- The AJ actual format attempt is closed/spent and is referenced by its
  immutable records only (protected native record 12503 B SHA256
  `72a1db20a88fa06d3580fafc89e0b28209206e69d8722d537ef0ec440560f4a3`;
  verified selected export 8252 B SHA256
  `23127fd83851ee690dcbbf35e39ac07c10e4c94e495a7d37034923e7432aad8e`). The
  measured bounded `native_ready=true` verdict belongs to that one AJ attempt
  only.
- This round performed no NEW manual native/fixture/Docker-admission/model/
  service work, no real model/Gateway call, no service/profile/network
  mutation, and claims no new Codex/native startup; the protected live
  host (Qwen 18020, qwen-serving, keys, firewall/VPN) is untouched; no new
  adapter or protected service deployment. The EXISTING CI Docker/build
  and Python-fixture jobs (their unchanged, explicitly allowed scopes) ran
  at B among the ten checks; that is unchanged verification scope, not new
  Docker work.

## Process and privacy limitations; setup disclosures

- No raw private request/source/image/credential in this report, the logs,
  or the tooling; known-synthetic content only; private IDs suppressed in
  operational repr; payload structurally unchanged; no hidden persistent
  registry or cross-request cache. This report is a claim, never
  self-acceptance.
- Gate disclosures (a)-(e): see the gate section above (diagnostic abort,
  UNMEASURED original driver shell exit, detached continuation, v1 record
  hash typo with v2 correction).
- (f) Design-file chronology: `design/design.md` was initially created 0664
  under the 0700 parent, then removed and recreated 0600 with the
  then-current bytes (equal at recreation). It was subsequently EXPANDED to
  the current 12671 B (SHA256
  `12b03f46fe60f50e863c0b5daa1edbae77f33401be22b89753ac34ad7a39322f`), so
  the current hash does NOT prove the initial-creation bytes, and no
  all-creation 0600 compliance is claimed. The initial-mode deviation is
  stated plainly; no cleanup/rerun to relabel evidence.
- (g) Probe-output location/mode deviation: an early manual probe run wrote
  outputs under `/tmp/final` (dir 0775; the copied `.out` capture was 0664,
  not protected-0600 at creation). The strategic-home `reviews/` copies of
  those probe outputs (e.g. `017-al-unidentified-poll-run4.out`,
  `017-al-battery-final-state.json`, 0600) are CODING-authored snapshots of
  the `/tmp` outputs — preserved as-is with their origin and actual modes,
  never relabeled as ROOT-owned evidence. Known-synthetic content only; no
  real/private exposure evidenced. Later gate/build evidence lives under the
  WAL (0700 dirs, explicit 0600 captures).
- (h) Synchronization: the ONE coding control reader (managed handle 45550 /
  Python 370735 / birth 191412687, retry1 helper
  `f48510172aa43d21011ad70a0a6c4fb3add21cfc386ab3607c056b801d8f618d`)
  consumed this round's ONE activation OK and is terminal/spent; no second
  control read, no wire replay, no new reader.
- (i) Retention scope and actual modes, stated as measured: protected 0700
  WAL dirs hold the gate captures (0600), drivers (0700), records (0600),
  the clean-build tree/archive/artifacts (tool-created modes preserved as
  actual), the design (0600), and the final report/tools/new inventory
  (0600). Public-PR-text metadata snapshots, per ROOT remeasurement:
  `publication/pr25-current.json` = 0600; `publication/pr25-current-body.txt`
  = 0664; the original `delivery/pr25-after-al-edit.json` = 0664 — all
  inside 0700 dirs; the first two are preserved as-is, the third per the
  disclosed replacement below. No blanket all-private-files-0600 claim is
  made.
- (k) Metadata-snapshot replacement (disclosed, not relabeled): the
  original `delivery/pr25-after-al-edit.json` (0664, the first post-edit
  remote PR snapshot) was REPLACED during v1 tooling preparation — the old
  file is now ABSENT and was not reconstructed or chmod-repaired; the
  replacement `delivery/pr25-after-al-edit-0600.json` (0600) holds
  byte-identical content (a copy, not a fresh measurement of a different
  state). It was therefore NOT preserved as-is; the measured origin, the
  0664 → 0600 mode change, and the equal bytes are stated honestly.
- (j) `cmd-07.err` (preserved as-is) records pytest OLD-temp garbage
  collection of `/tmp/pytest-of-janezp` with BOTH error kinds: `[Errno 13]
  PermissionError` (scandir) and `[Errno 39] OSError Directory not empty`.
  The test command itself did not fail (exit 0; 3745 passed / 28 skipped).
  No complete /tmp audit is claimed, no broader 'benign' label is made
  beyond the measured non-failure, and no cleanup or rerun was authorized
  or performed.

## RUN versus SKIPPED versus NOT RUN

RUN: at B — the 13 locked gate commands (structure disclosed), including
the full frozen pytest 3745 passed / 28 skipped; ruff/mypy/docs-
consistency (gate commands 03-06); the clean build + independent
source/generated-metadata proof; all TEN CI checks. Development-time
(collector `b96fa1f7…` byte-identical to A/B in all runs; coding final
batches also at final models `c715203f…`; ROOT's 87-capture at
mid-development models `fa9aa785…`, pre-final-docstring-fix; NOT re-run
at B): 82 focused process tests; 672 bundle-suite tests; the 94-case
probe battery (87 public composition + 7 direct entry; coding-authored
mixed-scope snapshot; ROOT's 87 public captures independent at the same
collector, per the hash-scope note above).

SKIPPED: 28 (pre-existing honest skips in the full pytest suite at B).

NOT RUN (explicit, remain mandatory — this round changed none of these):

- D09 actual-trace process-completion qualification (genuine multi-chunk
  process completion on an actual trace).
- Ordinary already-exited native single-final frames: they remain OUTSIDE
  public acquisition (legacy `MALFORMED_WRAPPER` gap, contract section 5a);
  stating the gap explicitly rather than claiming all native single-result
  support.
- Required-syntax ls+cat / unguarded-labeled-loop variants (pending scope
  audit).
- The EACH seven required-family acquisition audit/remediation, including
  concrete unsupported families 5/6/7 (later same-PR gate).
- Whole-017 strategic acceptance + merge + remote-main verification, all
  BEFORE any 018-024 activation.

## Remaining scope

The shipped wheel contains the inert collector only; the adapter runtime
behavior is unchanged and the approved v1 runtime profile
(`docs/CACHE-REWORK.md`) remains pending. D09 stays PARTIAL at
pure-inert scope until the NOT RUN items above are earned. The scoped
decisions of earlier rounds (incl. the AJ actual format qualification,
ACCEPTED with process qualifications) remain binding as recorded;
whole-017 remains unaccepted.

## Known limitations / blockers

- No blocker for the ordered pure scope. For later D09 completion: an actual
  trace with genuine multi-chunk process completion must be qualified under
  a separate authorized round; the legacy single-final native frame gap
  needs its own bounded decision; the EACH seven-family audit is a required
  same-PR gate before whole-017.

## Recommended strategic follow-up

1. D09 actual-trace process-completion qualification (separate authorized
   round; reuse the pure collector as the observer under test).
2. Bounded decision on ordinary already-exited native single-final frames
   (close or narrow the legacy `MALFORMED_WRAPPER` gap deliberately).
3. EACH seven required-family acquisition audit/remediation (families 5/6/7
   included), then whole-017 acceptance/merge and remote-main verification
   before 018-024.

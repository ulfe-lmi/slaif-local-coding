# OAP Coding-Agent Report — 017-i

## Work order
- Order: `oap/orders/017-i-offline-process-capture-utility.md`
  (objective 017, round 017-i, AMEND_EXISTING_PR); committed
  unchanged with implementation commit A (SHA256
  `f428a7e54a33a8b90079d64afd887d460124218a9c9ee64769948bb2d20a5494`).
- `oap/active` = `017-i` (bytes `017-i\n`, SHA256
  `19a1687096fc62ec7bf9582fa9fc9951dc56cbf72388cc1a60342a3bdbf95e69`);
  committed unchanged with A (activation bytes preserved, not edited).
- PR mode: AMENDED_EXISTING_PR — exact OPEN PR #25
  https://github.com/ulfe-lmi/slaif-local-coding/pull/25, base `main`,
  head branch `oap/017-cache-read-observation`. NO NEW PR; no coding
  merge or auto-merge.
- Starting remote PR/report head verified before mutation:
  `24449a1469c8bb66f57c0249b766d13bc330158d` (the 017-h report head);
  remote `main` `96c790423f6f0097a56a0b12bacda8a9b6da6aba`
  (unchanged). Working tree at round start held only the activated
  017-i order (new untracked) and `oap/active` (017-h -> 017-i), both
  committed unchanged in A.
- This worker resumed an in-progress round: a prior worker in this
  round had left uncommitted utility/child/test drafts. This round
  fixed those drafts (test-suite syntax and embedded-child-source
  defects, a non-reentrant lock self-deadlock on the provider 429
  path, missing finite read timeouts, a synthetic-binary generator
  defect, an exit-code probe contract defect, a readiness-record
  metadata-only violation, and a survivor-liveness assertion ordering
  bug), completed the order-mandated docs, and ran the full gate.
  Nothing from the interrupted 017-h scratch was read, copied or
  recreated; no 017-h artifact was touched.

## Status
COMPLETE — bounded claim for strategic review. The offline
process-capture utility, its synthetic offline child, its offline
adversarial suite, and the order-mandated documentation updates are
landed, gated, and published at the implementation head. The
actual-client path is unreachable by construction (startup readiness
is `not_ready`); no actual client, provider session or model call was
made; the actual capture and the process/chunk collector remain
NOT RUN. D09/D10 remain NOT RUN.

## Executive summary
1. Landed `scripts/real_client_capture.py` (schema family
   `slaif-real-client-capture-*-v1`): a stdlib-only, explicit
   opt-in, fail-closed capture utility for independent strategic
   review. Hard caps enforced in code and only lowerable by config:
   one actual attempt, 20 requests, 120 s deadline, 1 MiB per
   inbound request, 256 KiB aggregate selected, 4 MiB aggregate
   child output, one concurrent child. Non-resettable O_EXCL attempt
   ledger (claim before any genuine launch, consume exactly once
   with the truthful outcome). Owned process-group supervision:
   new session/group, bounded in-memory drain (byte counts only),
   SIGTERM/SIGKILL on deadline or output cap, group-gone verified
   after both normal exit and timeout, unrelated sessions never
   signalled. Finite reads on the owned fake provider: a stalling or
   truncated client (malformed, chunked, oversized, invalid-length
   payload) is rejected with a sanitized status and the handler
   thread cannot be pinned (bounded connection read timeout;
   the pre-existing 429 self-deadlock from a nested lock
   acquisition was fixed and is regression-tested). Privacy law
   enforced in code: bounded in-memory parsing with recursion
   guard, log-silent provider, fixed enum/count diagnostics,
   allowlisted synthetic extraction (closed declared step table,
   causal call-ID pairing, canary rejection, exact-byte output
   digests, no raw content/credentials/headers ever persisted or
   echoed). Readiness evaluation is metadata-only and can only
   ever produce `not_ready` in this version (candidate
   plugin/telemetry/update controls unverified from local static
   evidence; the H-round startup plugin sync is the recorded
   motivation). CLI: `check` (read-only preflight + readiness
   record; exit 3 = not_ready) and `run`.
2. Landed `scripts/real_client_capture_fake_child.py`: a wholly
   synthetic child used ONLY by the offline test suite (pinned
   injected path, no installed-client fallback). It models the
   declared read/sleep steps against the in-process fake provider,
   emits the declared leak markers only when requested, writes
   three environment facts to its child CODEX_HOME, and never
   executes incoming commands or persists provider traffic.
3. Landed `tests/test_real_client_capture.py`: the offline
   adversarial suite (113 tests). Coverage: fail-closed limits
   resolution; synthetic-binary preflight (version/hash/flag
   binding); static readiness `not_ready` law; attempt-ledger
   claim/consume/no-reset; closed external authorization record;
   raw-socket provider robustness (auth, request limit, malformed
   JSON/headers/Unicode, chunked forms, oversized/invalid-length
   bodies, stalled reads); allowlist extraction (declared vs
   undeclared, unknown item types bounded and digested, canary
   rejection without echo, exact-byte digests with raw content
   absent, causal transitions without flattening); child
   supervision (deadline/output-cap kills of the owned group only,
   unrelated-session survivor untouched, environment isolation,
   child-failure/provider-error outcomes); end-to-end synthetic
   runs (happy path, custom mode, deadline timeout with grandchild,
   request limit, selected over-bound, canary, child failure,
   provider error, undeclared command, tool-mode mismatch);
   actual-client fail-closed gates (opt-in, bindings, readiness,
   consumed-attempt, preflight failure); workspace/cleanup
   ownership guards; CLI surface; and static guards (stdlib-only
   imports, OAP decoupling, no installed-client fallback, no raw
   persistence, marker non-leakage).
4. Documents updated as ordered (offline utility described only;
   017-h recorded as interrupted PARTIAL non-delivery with nothing
   earned; future actual capture and process collector NOT RUN; no
   new architecture/security exception):
   `docs/CACHE-OBSERVATION-CONTRACT.md` (section 11 deferred
   history plus new section 12 documenting the utility),
   `docs/CACHE-REWORK-LEDGER.md` (intro, D09/D10 state notes,
   planned-succession 017 row), `TESTING.md` (v1 planned layers:
   017-h/017-i facts, named offline suite, honest skip),
   `ARCHITECTURE-for-agents.md` (Objective boundaries 017 list),
   `ARCHITECTURE.md` (stage status), and the compact mirror
   `oap/strategic-instructions/ARCHITECTURE-for-agents.md` kept
   byte-identical (`cmp` clean).
5. No product observer or runtime change: nothing in the adapter
   runtime imports or consults the utility; `src/` is untouched;
   the utility never reads or modifies `oap/active` or
   `oap/orders`; no dependency, service, gateway or migration
   change.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`; PR #25 OPEN
  https://github.com/ulfe-lmi/slaif-local-coding/pull/25
- Base `main` (`96c790423f6f0097a56a0b12bacda8a9b6da6aba`,
  unchanged); starting remote PR head
  `24449a1469c8bb66f57c0249b766d13bc330158d`
- Implementation head SHA: e79263d627deb7244119d2bfb08e18d81654eb13
- Report publication commit: SELF
- Implementation commits pushed before report: 2
  - A `d9efbae85a388389afcea255563891517fcf6100` — "017-i: land
    offline process-capture utility (inert) and offline tests"
    (3 new code files, 5 doc files, compact mirror, unchanged
    activated order + active; 11 files, +4801/−16)
  - B `e79263d627deb7244119d2bfb08e18d81654eb13` — "017-i: refresh
    development provenance manifest" (packaging/
    dev_provenance_manifest.json only; binds source A to the
    development artifact pair)
- New PR this round: no. Amended existing: yes. Merge performed: NO.
- Remote head verified after push: `git ls-remote origin
  refs/heads/oap/017-cache-read-observation` =
  `e79263d627deb7244119d2bfb08e18d81654eb13`.
- PR body updated (round history 017-h + 017-i entries and 017-i
  evidence block) via REST PATCH; content verified by refetch.

## Changes and files
- `scripts/real_client_capture.py` (new): the utility (see
  Executive summary 1). Schema family
  `slaif-real-client-capture-{run,selection,readiness,
  authorization,control}-v1`.
- `scripts/real_client_capture_fake_child.py` (new): synthetic
  offline child (Executive summary 2).
- `tests/test_real_client_capture.py` (new): offline adversarial
  suite (Executive summary 3).
- `docs/CACHE-OBSERVATION-CONTRACT.md`: section 11 deferred
  history (017-g published; 017-h interrupted PARTIAL
  non-delivery, nothing earned; 017-i offline utility); new
  section 12 (limits, privacy law, unreachable actual-client
  path, offline verification).
- `docs/CACHE-REWORK-LEDGER.md`: intro 017-h/017-i paragraphs;
  D09/D10 state notes; planned-succession 017 row.
- `TESTING.md`: v1 planned-layers 017-h/017-i facts; named
  offline suite; synthetic evidence is not actual-format
  evidence; honest environment skip documented.
- `ARCHITECTURE-for-agents.md` + `oap/strategic-instructions/
  ARCHITECTURE-for-agents.md` (byte-identical mirror): Objective
  boundaries 017 list extended (017-h/017-i).
- `ARCHITECTURE.md`: stage status paragraph 017-h/017-i facts.
- `packaging/dev_provenance_manifest.json`: development
  manifest B (source A binding; frozen RC10 publication section
  untouched).
- `oap/orders/017-i-offline-process-capture-utility.md`,
  `oap/active`: committed unchanged (activation bytes).
- No other files modified; `src/` untouched; no `oap/` order or
  report bytes edited; no dependency or lock change.

## Acceptance evidence
### Criterion: bounded offline utility, no actual launch this round
- `scripts/real_client_capture.py` implements the exact order
  limits fail-closed (`HARD_MAX_ACTUAL_ATTEMPTS=1`,
  `HARD_MAX_REQUESTS=20`, `HARD_DEADLINE_SECONDS=120.0`,
  `HARD_MAX_INBOUND_BYTES=1 MiB`, `HARD_MAX_SELECTED_BYTES=256
  KiB`, `HARD_MAX_CHILD_OUTPUT_BYTES=4 MiB`);
  `CaptureLimits.resolved` rejects over-hard/invalid values
  (focused tests PASSED).
- Actual-client path unreachable by construction:
  `evaluate_startup_readiness` returns only `not_ready` with
  closed reasons; `run_capture` requires opt-in + binding +
  `ready` record + authorization + unconsumed claim, all before
  launch. Focused fail-closed gate tests PASSED. Bounded read-only
  `check` against the installed `codex-cli 0.162.1` binary
  (read-only `--version`/`exec --help` probes only) returned
  `verdict=not_ready` with closed reasons and exit 3 (see Live
  section). No actual client was launched in this round.
### Criterion: offline tests meaningful, no genuine client/model/provider
- All tests use injected synthetic child executables (pinned
  paths) or in-process owned ephemeral-loopback provider; static
  guard tests prove stdlib-only imports, OAP decoupling, no
  installed-client fallback, no raw-content persistence, and
  leak-marker non-leakage. Focused suite PASSED (112 passed, 1
  honest environment skip, 0 failed).
### Criterion: docs/contracts updated in the same PR
- Observation contract section 12, stage ledger, TESTING.md,
  compact architecture + byte-identical mirror, human
  architecture all state the offline-only scope, the 017-h
  PARTIAL non-delivery, and NOT RUN for actual capture/collector;
  docs consistency gate PASSED.
### Criterion: full locked gate + provenance + probes + CI
- See Verification and GitHub CI sections. All required green at
  drafting.

## Verification
Test context: non-root user `janezp`, process-local `umask 022`
for every pytest run; repo venv via `uv`; no root used anywhere;
no global permission changes.

- `uv lock --check`: PASSED (lock up to date; 36 packages).
- `uv sync --frozen --extra dev`: PASSED (31 packages checked).
- `uv run --frozen ruff check .`: PASSED (All checks passed;
  511 files).
- `uv run --frozen ruff format --check .`: PASSED (511 files
  already formatted).
- `uv run --frozen mypy src tests`: PASSED (no issues found in
  107 source files).
- `uv run --frozen python scripts/docs_consistency_check.py`:
  PASSED (19 claim docs checked).
- `umask 022 && uv run --frozen pytest -q tests/test_real_client_capture.py`:
  PASSED — 112 passed, 1 skipped, 0 failed. The single skip is
  honest and environment-bound:
  `test_cleanup_refuses_foreign_root` requires `chown` to another
  uid (uid `daemon`), unavailable to a non-root user; it runs
  wherever that capability exists.
- `umask 022 && uv run --frozen pytest -q` (full suite at final
  head): PASSED — 2154 passed, 28 standing skips, 0 failed
  (377.86 s).
- `uv build`: PASSED (sdist + wheel built from source A).
- `uv run --frozen python scripts/artifact_policy_check.py --dist dist --inspect`:
  PASSED (`ok: true`, no violations).
- `uv run --frozen python scripts/artifact_policy_check.py --dist dist --install-smoke`:
  PASSED (`ok: true`, no violations).
- `uv run --frozen python scripts/dev_provenance_manifest.py --verify --dist dist`:
  PASSED (`development provenance OK: state=development
  head=e79263d627de`; source binding
  `d9efbae85a388389afcea255563891517fcf6100`, objective 017-i;
  wheel `99e5ad582232c5a2e9e717c7707162b8c57261983aa0cf472e0c4e0d9263ac71`,
  sdist `641c628dbe66216ac3bc736b725c4dbc67ccdc2be9512b7a8097c16c54bd2c6d`;
  frozen RC10 publication baseline intact).
- `python -m compileall -q src tests oap/bin scripts`: PASSED.
- `bash -n` over `oap/bin/*.sh` and `packaging/*.sh`: PASSED
  (all shell scripts parse).
- `git diff --check`: PASSED (no whitespace errors).
- Targeted credential/raw-log/privacy scan over the three new
  files: PASSED (no real key/token/bearer patterns; only the
  synthetic in-test token; no raw captured content; synthetic
  leak markers asserted absent from all persisted records).
- Compact mirror invariance: PASSED —
  `cmp ARCHITECTURE-for-agents.md oap/strategic-instructions/
  ARCHITECTURE-for-agents.md` byte-identical after edits.
- `docs/CACHE-REWORK.md` invariance: PASSED (not modified;
  SHA256 `410df5c0b8f90b05220adc32c8e673b143c0cf1fa3da02270d91ac453c886abd`
  preserved).
- Seven frozen strategic probes with canonical
  `REPO/.venv/bin/python --head
  e79263d627deb7244119d2bfb08e18d81654eb13` (probe script SHA256s
  verified against `reviews/017-i-probe-hashes.json` before
  running; scripts unmodified):
  - `check-bundle-observation.py`: PASSED — 23/23 checks.
  - `check-read-option-semantics.py`: PASSED — 16/16 checks.
  - `check-endpoint-selection.py`: PASSED — 5/5 checks.
  - `check-root-endpoint-context.py`: PASSED — 6/6 checks.
  - `check-finite-read-plans.py`: PASSED — 40/40 checks.
  - `check-literal-loops.py`: PASSED — 63/63 checks.
  - `check-loop-word-boundaries.py`: PASSED — 10/10 checks
    (six variant groups covering 162 quoted-word variants).
  All with `positive_control_valid: true` and
  `all_checks_passed: true`.
- Real-Codex E2E: NOT RUN (not ordered; the order authorizes no
  actual client invocation).
- Live bounded inference: NOT RUN (not authorized by this order).

## Live model/service evidence
- No live inference performed; no model, provider or client
  session call of any kind.
- Bounded read-only local inspection of the installed
  `codex-cli 0.162.1` binary
  (`/home/janezp/.codex/packages/standalone/releases/
  0.162.1-x86_64-unknown-linux-musl/bin/codex`, SHA256
  `628e35487d888a28f0427fc37501da529dd3d81fcbad7a2c3421c1e8670d92e1`
  re-verified before use): one `check` invocation (read-only
  `--version` and `exec --help` probes, bounded output, no
  session, no network) returned
  `check: verdict=not_ready reasons=plugin_catalog_sync_control_unverified,
  telemetry_update_control_unverified flags=16 version=0.162.1
  sha256=628e35...` with exit code 3 — honest NOT READY,
  metadata-only output (flag count only, no help text).
- No pre-existing image proxy assumed or touched. Protected
  fixtures unchanged: `qwen-serving`, vLLM 18020, API-key files,
  firewall/VPN/routing, existing Codex profiles — all untouched.
  The H-round scratch root was already removed by the 017-h
  closeout; nothing of it was read, copied or recreated.

## GitHub CI / required checks
- Implementation-head check state at
  `e79263d627deb7244119d2bfb08e18d81654eb13` (PR #25):
  - `test`: pass (4m38s)
  - `docker`: pass (1m33s)
  - `docker-published`: pass (1m7s)
  - `gateway-contract`: pass (22s)
  - `operator-session`: pass (1m20s)
  - `CodeQL`: pass (3s)
  - `Analyze (python)`: pass (1m18s)
  - `Analyze (actions)`: pass (29s)
- All required green at drafting: yes (8/8 pass).
- Report-head checks may be pending; strategy verifies.

## Local setup/dependencies
- Existing repo venv (Python 3.12.15, uv 0.12.5, frozen lock;
  `uv.lock` SHA256 `1237cbd179f71b99984c80f927529549f5e61eb705585ef9cf2ab0fa9e26764a`);
  no new dependency, no lock change, no new service. No sudo
  used. No durable docs/config changes beyond the listed
  repository docs. `dist/` rebuilt locally for the gate (not
  committed). No protected host/home permissions changed; test
  roots created 0700/files 0600 by the utility itself.

## Documentation
- Updated (same PR): `docs/CACHE-OBSERVATION-CONTRACT.md`
  (section 11 + new section 12), `docs/CACHE-REWORK-LEDGER.md`,
  `TESTING.md`, `ARCHITECTURE-for-agents.md`,
  `oap/strategic-instructions/ARCHITECTURE-for-agents.md`
  (byte-identical mirror), `ARCHITECTURE.md`. Why: behavior,
  configuration surface, security law, tests and limitation
  claims changed exactly as the order requires; the offline-only
  scope and NOT READY readiness law are stated without a new
  architecture or security exception.

## Safety/scope confirmations
- Unrelated/pre-existing work preserved: working tree at round
  start held only the activated order + active (committed
  unchanged) and the prior worker's uncommitted drafts of the
  three in-scope new files (completed and committed in A). No
  reset/clean/overwrite; no `git add -A`; explicit paths only.
- Secrets/raw content: none committed, printed, logged or
  persisted; synthetic in-test token only; readiness/selection/
  run records are metadata-only (enums, counts, digests);
  0600/0700 on protected records; targeted scan PASSED.
- Production/protected resources: NO mutation. Protected
  18020/Qwen/Codex fixture changed: NO (not ordered). No
  release, cutover, merge or auto-merge. No next-ID/suffix
  choice; strategy owns acceptance and the next round.
- Local results do not impersonate required GitHub checks;
  skipped/pending/missing reported distinctly and never as pass.

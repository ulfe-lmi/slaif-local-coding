# OAP Round Report — 017-u: complete group observation and evidence finalization

- Objective: 017 (`AMEND_EXISTING_PR`; PR25
  https://github.com/ulfe-lmi/slaif-local-coding/pull/25; branch
  `oap/017-cache-read-observation`; base `main` @
  `96c790423f6f0097a56a0b12bacda8a9b6da6aba`)
- Order: `oap/orders/017-u-complete-group-observation-and-evidence-finalization.md`,
  SHA256 `b8d38c0a89fdb1905d069c7f98b43494b8bec1e3f32d22f3daeec2129548a13f`,
  committed byte-unchanged in source A; `oap/active` = `017-u\n` unchanged.
- Starting state: T SELF `e6631e151385e52115a32632cd177a42c9a61041`
  (report-only), sole T implementation parent
  `911781ef3a35577666d0a4f5300b46077ca6f67c`; T source A
  `d9ade801a1cb0c60c45387269ca560f481e2e88a`. GitHub reconciled before
  mutation (remote PR head = T SELF; base unchanged).
- Status: COMPLETE
- Implementation head SHA: f9d9caaa18264fab5f19cc37230a4d608a44eafc
- Report publication commit: SELF

## Outcome (bounded, honest)

The order's single bounded outcome is delivered: the inert
native-handoff preparation workflow now observes process groups under the
correct complete-inventory law — a stat-unreadable but positively existing
PID can no longer mint a complete-group or complete-stop fact — with public
tracked regressions, the frozen/installed/archive evidence re-qualified at
the literal implementation head, all ordered gates and all 10 implementation
checks SUCCESS, and this evidence record finalized. Nothing native was
executed: NO native launch (including help/version), NO worker stop, NO
local Docker operation, NO TTY/host-job manipulation, NO new rehearsal or
fixture admission, NO auxiliary handoff signal. The one S admission remains
consumed; the S/R/Q/P/T reports remain immutable; whole 017 (D01-D10,
including D09) and 018-024 remain incomplete; the v1 runtime remains
unimplemented; no acceptance is claimed.

## 1. Complete-group observation law repair (order section 2)

Defect (strategic review 11, `reviews/017-t-group-readability-review-11.md`):
in `scripts/cache_native_fixture_native_prep.py`, both
`collect_worker_group` and `collect_stop_observation` treated every
`stat()` failure as "the member raced away", i.e. a listed row whose entry
positively still exists but whose stat is unreadable was counted as
non-membership. A valid otherwise-complete group with one such row therefore
(1) claimed a complete G inventory and (2) minted a complete stop receipt.

First probe evidence (unchanged strategic probe
`probes/check-native-group-readability-mocked.py`, 4 cases, trusted fake
process table): 3/4 at the T implementation, native-source module SHA
`92ca10353c7cdd5640ceadefb530d0f95dd53c62f126d66d26ae5ff9e0577d11`, fixture
SHA `8bd4e1f6ddf807c6c8b1e433df3b5de3ea6765ed300127c9b1c7b379bbf858d2`
(`reviews/017-t-group-readability-first-911781ef3a35.json`,
2026-10-26T04:04:08Z): complete-stopped-group positive, running-group-member
refusal and verified-vanished-member positive PASS;
`unreadable_still_existing_member_never_complete_stop` FAILS; valid
positive present. No actual process, signal, Docker/native, owner action or
OAP mutation was used.

Repair (order section 2 items 1-4, implemented in the two collectors and
their public workflow paths):

- Every listed row is tri-state resolved through the existing bounded
  read-only absence seam `_verified_absence(table, pid)` (its historical
  `pid_present` contract is preserved, not inverted: True = verified
  absent, False = exists, None = unknown; missing capability or failed
  presence evidence stays unknown). Only a VERIFIED gone row may be skipped,
  under the existing bounded-churn law. An existing-but-unreadable (False)
  or unknown (None) row is a closed non-echoing refusal: new closed token
  `prep-group-incomplete` in the group inventory (added to the module's
  closed `PREP_REASONS` vocabulary), and the existing
  `prep-stop-unobserved` in the stop predicate. Raw stat/cmdline/path/
  exception content is never exposed.
- Refused prepare/observe/record_stop raise before `_baseline`, `_group`,
  `_subject_receipt` or `_stop_receipt` are touched, so a failed or
  incomplete measurement cannot silently replace a valid identity baseline
  or create a past stop; a refused stop leaves `stop_recorded` false, so no
  later snapshot can claim restoration from that failed event.
- No new watcher, PID controller, host signal, budget, filesystem oracle or
  general framework; caps, time bounds and closed errors unchanged; the
  membership cap (256) is unaffected by verified churn; a valid fully
  observed group still completes (no always-unready stub).

Post-repair independent root re-verification: same probe, same fixture,
source SHA `11c737a9e71111cb3705b76ad7e7997789c12359e8500c6d008bbb6c95f2bd07`
→ 4/4 PASS with the valid positive preserved and source/fixtures stable
(`reviews/017-u-group-readability-repair-11c737a9e711.json`,
2026-10-26T04:33:36Z).

## 2. Public local proof (order section 3)

Seven new tracked public regressions were added to
`tests/test_cache_native_fixture_native_prep.py` (prep suite 117 → 124), all
pure/fake plus the existing tiny exact-owned Python child discipline:

1. `test_public_stop_tri_state_matrix` — public prepare/record_stop matrix
   over complete / running-member / verified-gone / unreadable-existing;
   after the refusal `flow._stop_receipt is None` (no past stop minted).
2. `test_worker_group_tri_state_inventory` — group inventory tri-state
   (complete accepted; running member refused; verified-gone tolerated;
   unreadable-existing → `prep-group-incomplete`).
3. `test_unreadable_initial_prepare_refused_then_recovered` — failed initial
   prepare mints no baseline; a later healthy prepare recovers.
4. `test_repeated_prepare_and_observe_failure_preserve_baseline` — repeated
   prepare/observe failures preserve the original identity baseline
   (snapshot equality plus direct `flow._baseline` checks).
5. `test_capability_less_table_never_mints_completeness` — a table without
   the presence capability never mints completeness (unknown ≠ verified
   gone); the same healthy flow still completes, so this is not an
   always-unready stub.
6. `test_failed_stop_cannot_claim_restoration` — after a refused stop the
   verdict is `worker-stop-unmeasured`; a later GENUINE stop is recorded and
   `collect_restoration(..., stop_receipt=receipt)` reports restored True
   only from that recorded receipt.
7. `test_membership_cap_unaffected_by_verified_churn` — at the 256 limit,
   verified-gone hidden PIDs do not consume budget; one over →
   `prep-proc-overbound`.

Existing negatives retained: the legitimate no-TTY metadata, PTY
qualification, executable/context agreement, S-scope and stop/restoration
negatives, and the closed-reason vocabulary test
(`test_prep_reasons_closed_vocabulary` now covers `prep-group-incomplete`).
No test signals the real worker/Bash group or any unrelated process.

Focused verification at the pre-commit checkpoint (repo Python 3.12 venv):
prep 124 + binding 45 + artifact-policy 7 = 176 PASS; the 12 strategic
selected probes (11 T probes + the 4-case group-readability probe) all PASS;
mypy `src tests` 0 errors (116 files); `ruff check .` clean;
`ruff format --check .` clean (554 files); `scripts/docs_consistency_check.py`
OK (19 claim docs).

## 3. Independent root evidence (attributed, not repeated)

- `reviews/017-u-independent-preparation14-f9d9caaa1826.json`: root
  preparation14 PASS at literal implementation head `f9d9caaa` — 67 actual
  assertions, all useful positives preserved, source/fixtures/head/worktree
  stable, private 14 hashes verified before/after; includes the repaired
  complete-G unreadable-vs-gone case. Scoped WIP-to-final public-fake proof,
  not final-head/U/native acceptance by itself.
- `reviews/017-u-group-readability-repair-11c737a9e711.json`: independent 4/4
  group-readability re-verification (section 1).
- `reviews/017-t-group-readability-first-911781ef3a35.json`: the first 3/4
  probe evidence at the T implementation (defect proof, preserved).

## 4. Final verification at the implementation head f9d9caa (order section 5)

All commands below ran in the repository
`/home/janezp/codex-work/slaif-local-coding` at the committed candidate
(working tree clean at B `f9d9caa`), with the repo Python 3.12 venv
(`.venv/bin/python`).

Final full TESTING gate (ONE shell, `umask 022 &&` for the whole chain,
same shell as the pytest invocation):

- `uv sync --frozen --extra dev` — OK
- `.venv/bin/python -m pytest tests/ -q -p no:cacheprovider` —
  **3138 passed, 28 skipped, 0 failed** in 500.64s (0:08:20), exit 0
  (T-era total was 3131 passed / 28 skipped; +7 exactly the new tracked
  tests)
- `.venv/bin/python -m compileall -q src scripts` — OK
- `.venv/bin/ruff check .` — All checks passed
- `.venv/bin/ruff format --check .` — OK
- `.venv/bin/mypy src tests` — Success: no issues found in 116 source files
- `.venv/bin/python scripts/docs_consistency_check.py` — OK (19 claim docs)
- `uv lock --check` — OK (36 packages)
- `.venv/bin/python scripts/artifact_policy_check.py --inspect` — ok, no
  violations (sdist 193 entries, wheel 37 entries, 31 package files)
- `.venv/bin/python scripts/artifact_policy_check.py --install-smoke` — ok,
  no violations (entrypoint help/version exit 0 in a temp venv)
- `uv build --out-dir dist` — OK

Artifacts at the final candidate:

- wheel `slaif_local_coding-0.1.0-py3-none-any.whl`:
  SHA256 `1f2ebaff444be1ae90a7f1d863f462abcc82ff28caca448e28c206699fa4b50c`,
  142,753 bytes, 37 entries — BYTE-IDENTICAL across P/R/S/T/U (U touches no
  `src/`).
- sdist `slaif_local_coding-0.1.0.tar.gz`:
  SHA256 `b3376a077f06f9a87a95c66d5500d9b13a9b3609b44868c1125a7962c13ee5b1`,
  879,955 bytes, 193 entries. It legitimately differs from the T-era sdist
  (`91a29829b547…`, 876,601 bytes) because the seven new tracked tests sit
  in the sdist-shipped `tests/test_cache_native_fixture_native_prep.py`; no
  packaged source changed.
- Development manifest B (`packaging/dev_provenance_manifest.json`, objective
  017-u, source A `5f6bcdb…`): 195 complete inputs; `--verify` OK
  (state=development).

Clean git-archive reproduction (both artifacts, venv/output outside the
source tree):

- `git archive` of the literal implementation head `f9d9caa` extracted to
  `/home/janezp/oap-017u-work/slaif-local-coding-u`: all 195 manifest
  source inputs present with matching SHA256 (0 missing, 0 mismatched) and
  all 30 installed Python module bytes matched wheel↔archive
  (`archive-wheel-identity-f9d9caa.json`).
- ACTUAL `uv build` executed inside the clean archive tree with out-dir
  outside the source tree: both artifacts byte/hashes/sizes identical to the
  manifest and to the repo `dist/` (`archive-build-receipt-f9d9caa.json`).

Installed functional proof: fresh `uv venv --python 3.12` (Python 3.12.15)
OUTSIDE the checkout at `/home/janezp/oap-017u-work/fresh-venv-312`,
non-editable install of the archive-built wheel, then the 27 UNIQUE
functional case checks (14 inventory-totality + 5 inventory-allocation + 8
private-ID-representation): **27/27 PASS**, identity assertions separate
and all true (site-packages outside the repo, version 0.1.0, no repo path on
`sys.path`) — `installed-functional-f9d9caa.json`.

Frozen 21 at the LITERAL implementation head `f9d9caa`, repo Python 3.12
venv interpreter only (the ambient `python3` lacks `prometheus_client`; see
the retained R-era interpreter diagnostic): **21/21** probes exit 0 with all
checks passed, valid positive controls, and the frozen baseline probe
hashes unchanged before/after (`probes-final-f9d9caa.json`, runner
`run_frozen21.py`, baseline `reviews/017-p-probe-hashes.json`).

## 5. GitHub CI (all 10 implementation checks)

Run `40271373342` at head `f9d9caaa18264fab5f19cc37230a4d608a44eafc`
(created 2026-10-26T04:53:35Z, completed 04:58:56Z, conclusion success).
All 10 required checks present and SUCCESS:

| check | job id | result |
|---|---|---|
| test | 121404713933 | SUCCESS (04:53:37 → 04:58:56, 5m19s) |
| Analyze (actions) | — | SUCCESS |
| Analyze (python) | — | SUCCESS |
| gateway-contract | 121404713963 | SUCCESS |
| docker | 121404714064 | SUCCESS |
| docker-published | 121404713926 | SUCCESS |
| operator-session | 121404713747 | SUCCESS |
| cache-native-containment | 121404713965 | SUCCESS |
| cache-native-fixture | 121404713954 | SUCCESS |
| CodeQL | — | SUCCESS |

Verified via `gh pr view 25 --json statusCheckRollup` (all 10 entries
COMPLETED/SUCCESS) and the run jobs API. No Codex execution in CI.

PR25 metadata (PRE-SELF, exact owned files only): body refreshed with a new
"017-u complete-group observation (INERT; native NOT RUN)" section and the
round-history line extended with the 017-u report name; title unchanged
(244 chars; the 017-u suffix would exceed 256, so it was not appended).
PATCHed via `gh api -X PATCH …/pulls/25`.

## 6. Append-only clarifications to the T record (order section 4)

These clarify the immutable T report; no T bytes were touched.

1. **T§9 signal scope.** T§9's unqualified "NO host signal of any kind"
   overstates its scope: the tiny exact-owned test children were
   killed/waited by permitted test cleanup, as T§4 already describes. No
   real worker, Bash group or unrelated process was signalled, and no worker
   stop occurred. This was an allowed test action, not a protected-host
   violation.
2. **Explicit Status field.** T omitted the protocol Status field. This U
   report includes it (Status: COMPLETE for THIS order's bounded scope).
   That does not change that whole 017 and 018-024 remain incomplete, and T
   is not retroactively assigned or edited.
3. **Historical auxiliary log.** The empty historical auxiliary launch log
   proves neither pass nor process death. The prior launch-attribution /
   liveness uncertainty is preserved; T's "dead" shorthand is not primary
   liveness evidence unless existing closed evidence establishes more. The
   separately retained successful frozen21 results remain qualifying. No
   private captures were reopened and no S attempt was re-run to
   manufacture attribution.
4. **Distinct binding probes.** The seven-case public order-binding proof
   (`probes/check-native-order-binding-public-mocked.py`, 7 cases) and the
   four-case actual file-replacement proof
   (`probes/check-native-binding-file-replacement.py`, 4 cases) are
   DISTINCT; T§5's binding label does not make the file-replacement probe
   seven cases. Both retain valid positives and their exact case counts.
5. **Distinct mode-audit scopes.** T§1 cites the initial 13-entry pass1
   mode audit; a separate 38-entry / 22-temporary-metadata pre-SELF audit
   was reported in coding UI. Those scopes are distinct. U retains its own
   fresh explicit final audit (section 9), not a reuse of an early
   inventory.

## 7. NOT RUN (explicit)

- NO native launch of any kind (including help/version) in U.
- NO worker stop, NO TTY/job manipulation, NO host signal.
- NO local Docker operation (native/Docker backend paths remain
  implemented-but-unexecuted in the inert workflow).
- NO new rehearsal, NO new fixture admission; the single S admission at
  `2a9c44e…` / run `c8fed899…` remains consumed.
- D09 remains `NOT RUN`; the real native handoff is a separately activated
  order.
- NO protected Qwen/vLLM/qwen-serving/model/GPU/Gateway change; NO
  benchmark/RC/tag/registry/release/deployment/cutover; NO merge or
  auto-merge; no second PR; no next numeric objective.
- Legacy default unchanged; v1 runtime not implemented; whole 017 and
  018-024 remain required.

## 8. Preserved failures and disclosures

- T preliminary failures (preserved in T evidence, not restated as U
  results): two artifact-policy failures (host-specific endpoint fixture in
  an sdist-shipped file, later replaced with a synthetic TEST-NET
  reservation) and two stale-provenance failures (WIP runs against pre-A
  inputs). None recurred at the U final candidate: artifact-policy
  `--inspect`/`--install-smoke` clean and provenance regenerated from
  committed A before the final gate.
- U fresh final mode audit (section 9) initially found five owned files at
  0644 (`wheel_control_017u.py`, `/tmp/u-gate/*.log`); exact-path
  `chmod 600` applied to those five only, re-audit clean. No recursive or
  blanket chmod; no global/home chmod.
- The R-era A4 `git add -A` deviation remains disclosed in the immutable R
  report; U staged exact paths only (source A: 10 exact paths; manifest B:
  1 exact path; report commit: 1 exact path).
- Wheel/sdist identities and the carried S measured facts are bound to
  their respective heads (section 10); nothing here is a post-SELF repair
  or a claim over earlier rounds.

## 9. Evidence root and file audit (fresh, explicit)

Fresh protected U evidence root `/home/janezp/oap-017u-work/` (mode 0700,
uid 1001). Owned entries (all mode 0600 uid 1001 after the exact-path fix
above):

- `run_frozen21.py` — frozen-21 runner at literal `f9d9caa`
- `probes-final-f9d9caa.json` — frozen-21 result (21/21, hashes unchanged)
- `archive-wheel-identity-f9d9caa.json` — 195/195 inputs, 30/30 modules
- `archive-build-receipt-f9d9caa.json` — clean-archive actual-build receipt
- `installed-functional-f9d9caa.json` (+`.err`) — 27/27 installed controls
- `wheel_control_017u.py` — installed-27 driver (U venv identity)
- `owned-files-audit-preself.json` — this audit receipt (15 entries, 0
  nonconforming after the exact-path fix)

Excluded tool trees retaining intended permissions:
`slaif-local-coding-u/` (git archive), `archive-build-f9d9caa/` (build
out-dir), `fresh-venv-312/` (venv). Owned `/tmp` round metadata
(`/tmp/pr25-body-u.md`, `/tmp/u-gate/*.log`) audited 0600 uid 1001. No T
report bytes were altered; no older artifact was blanket-chmodded.

## 10. Identities and limitations

- Source A: `5f6bcdb5f1311e2954222e739121a3c143d99958`
  (`017-u: complete-group observation tri-state law and documentation`;
  parent T SELF `e6631e151385e52115a32632cd177a42c9a61041`; 10 exact paths:
  3 compact architecture mirrors, ARCHITECTURE.md, TESTING.md,
  docs/CACHE-OBSERVATION-CONTRACT.md, docs/CACHE-REWORK-LEDGER.md,
  oap/active, the activated order, the module and the test file).
- Manifest B / implementation head: `f9d9caaa18264fab5f19cc37230a4d608a44eafc`
  (sole parent A; manifest only).
- Three compact architecture mirrors byte-identical at source A
  (SHA256 `535659643814683df73d0700362428971ef47b0a3b822d2f987c95ae82dd1d25`):
  `ARCHITECTURE-for-agents.md`,
  `oap/strategic-instructions/ARCHITECTURE-for-agents.md`, and the root
  strategic copy.
- Development manifest: 195 inputs; wheel
  `1f2ebaff444be1ae90a7f1d863f462abcc82ff28caca448e28c206699fa4b50c`
  (142,753 B) byte-identical P/R/S/T/U; sdist
  `b3376a077f06f9a87a95c66d5500d9b13a9b3609b44868c1125a7962c13ee5b1`
  (879,955 B) — test-only change from T-era sdist.
- Frozen 21, installed 27 and clean-archive build are scoped proofs at the
  literal `f9d9caa`; they are not final S/whole-017 acceptance, not native
  qualification, and not a v1 runtime claim.
- Local results do not impersonate the required GitHub checks (which
  passed, section 5); green CI is necessary, not sufficient; a report is a
  claim, not acceptance.

# OAP Coding-Agent Report — 017-aj

## Work order
- Identifier: 017-aj; order path: `oap/orders/017-aj-native-process-format-qualification.md`; numeric objective: 017
- PR mode: AMENDED_EXISTING_PR

## Status
COMPLETE

## Executive summary
The ONE admitted actual attempt (attempt head P, run `e51da1e99c4341a48c6ca9f0e9ff62e6`) executed the real native format qualification on the bounded reference fixture and PASSED (operator terminal exit 0). The four serial format cases byte-verified against the immutable pre-launch seed originals; the 8252 B retained FULL four-case capture was revalidated before teardown and qualified by the shared strict full consumer (the only form that qualifies); publication kept the owner-FIRST ordered separation and closed the journal with ONE pass entry, one-shot, no fresh-path retry, no cached-finalize upgrade. ALL EIGHT separate facts verified. No source/helper/test/lock/workflow file changed in the round; the ONE admission is terminal, never reset, retried or relabeled. Delivery: docs A plus two small factual docs corrections, then manifest-only B; the prescribed locked 13-command gate PASSED 13/13 once at clean B (3663 passed, 28 skipped, 0 failed); all 10 required CI checks SUCCESS at B. D09 remains NOT RUN; no generic native-ready, whole-017 or v1 runtime claim; 018-024 remain mandatory.

## Authoritative GitHub state
- Repository `ulfe-lmi/slaif-local-coding`; PR #25 OPEN — https://github.com/ulfe-lmi/slaif-local-coding/pull/25
- Base `main` `96c790423f6f0097a56a0b12bacda8a9b6da6aba`; head branch `oap/017-cache-read-observation`
- Starting remote SHA this round: `507885f2c94ae0811c33f2cb2b1f1f54acd7e9ca` (the AI round's report SELF)
- Pre-attempt activation commit: `65578d064ab7cc8e41b9a3f0ad266e3dd7119878` (P; `oap/active` → 017-aj + activated order file only; pushed before the attempt; the actual attempt stays bound to P and made no repository change)
- Implementation head SHA: 8fc4c5e697fa534741ac14f542a5122788f3dd9d
- Report publication commit: SELF
- Delivery commits pushed before report: 4 — `bc907fbb34042fa4be5e61e449d76ddfc919196e` (docs A), `f7fd0c00a6a6530514e07b41aa592c9245bb73a4` (docs correction), `b63145c129ea30df7c6fec48565d57f8e7d92f95` (docs correction), `8fc4c5e697fa534741ac14f542a5122788f3dd9d` (manifest-only B)
- New PR this round: NO; amended existing: YES; merge performed: NO

## Changes and files
- A `bc907fb`: exactly six doc paths — `ARCHITECTURE.md` (+54), `ARCHITECTURE-for-agents.md` (+52), `oap/strategic-instructions/ARCHITECTURE-for-agents.md` (byte-copy), `TESTING.md` (+57), `docs/CACHE-OBSERVATION-CONTRACT.md` (+62), `docs/CACHE-REWORK-LEDGER.md` (one ledger line). All three compact copies byte-equal after sync (repo 664, strategic-instructions 664, strategic-home 600 inode-preserved).
- `f7fd0c0` / `b63145c`: two small factual corrections (retained metadata holds key names plus sha only; host-side synthetic envfile explicitly used by the Docker attach was removed during owned cleanup; measured bounded `native_ready=true` verdict distinct from no generic claim).
- B `8fc4c5e`: `packaging/dev_provenance_manifest.json` only (bound to source `b63145c`; 201 source inputs; wheel 142753 B SHA-256 `1f2ebaff…a4b50c` byte-identical to the AG-qualified wheel; sdist 1119910 B SHA-256 `8cc4491c…b293b6` / 199 entries).
- PR #25 body/title updated (metadata only; no implementation commit).
- NO source/helper/test/lock/workflow change anywhere in the round (P→B diff = the six doc paths + the manifest; all 17 helpers byte-identical P/B/clean tree).

## Acceptance evidence
### Criterion 1 — ONE actual attempt, terminal PASS at bounded scope
- ONE reviewed private non-Codex operator, ONE managed foreground procedure, ONE terminal admission; SAME worker stopped once by exact-group TSTP (monitor ON before any setter); operator terminal exit 0. Facts by immutable reference: `reviews/017-aj-actual-qualification-review.json` and the linked actual records.
### Criterion 2 — actual four-case format workload, byte-verified
- Seeds: 5 files / 2894 B pre-launch originals, SHA `e4b63fd9…ef86`. Cases: complete 494 B read; genuine initial-running exec, 1536 B output (CRLF and non-ASCII) over ONE poll in TWO non-empty pieces; successful 0 B empty output; deliberate bounded truncation (200 B at 24 effective tokens), never acquiring. Measured: 5 issued calls, 1 poll, 7 model POSTs (planned minimum 6; the ONE extra POST's purpose UNMEASURED — no retained body/status trace, no forensics). Separate ledgers: the 7 model POSTs were fixture-internal to the owned reference fixture's fake provider; controller export ledger 9 requests / 7561 output bytes; host-side fixture-scoped control: 2 API requests (2 admitted / 0 refused) plus 38 Docker admissions; healthz 1; physical 16 cumulative TCP-handler cap preserved; exact physical TCP admission count NOT retained.
### Criterion 3 — retained FULL capture, strict-full qualification, owner-FIRST publication
- 8252 B retained FULL four-case capture (SHA `23127fd8…ad8e`, exporter uid 21001) revalidated BEFORE teardown; qualified by the shared strict full four-case consumer (only strict full qualifies). Publication: owner's OWN successful retention receipt FIRST → retained AJ record SECOND (retained `attempt=running` = publication-time fact) → journal LAST (ONE entry, pass); one-shot, no fresh-path retry, no cached-finalize upgrade.
### Criterion 4 — cleanup, same-job restoration, functional input
- Exact-CID and image teardown 404-verified, unrelated sentinel survived; the host-side synthetic env file (attempt's synthetic CODEX_HOME and provider-key values, 0600) was removed during the owned work-root cleanup; the retained protected AJ records hold the exact known synthetic selected call/result frames plus key names and SHA only. SAME Bash job (job 1, `fg %1`) restored the worker foreground (re-measured, monitor ON); saved TTY attributes restored TCSANOW with no input flush (readback-equal, dev 28 ino 21); functional input verified by the root with an actual read-only tool probe (`git rev-parse --verify HEAD` → literal P).
### Criterion 5 — admission terminal, no source change
- `.oap-local/017-aj/` admission terminal pass, consumed, never reset/retried/relabeled; P→B diff contains no runtime/tests/locks/workflows; 17 helpers (14 py + 3 Dockerfiles) byte-identical.
### Criterion 6 — locked gate, artifact/source proof, CI
- Gate 13/13 at clean B; clean-archive both-artifact rebuild byte-identical to manifest B; all 10 required checks SUCCESS at B.

## Verification
- Prescribed locked 13-command gate at clean B (once, driver 248747, same-shell umask 077; nonroot umask-022 pytest child in invocation 7): ALL PASSED —
  1. `uv lock --check` PASSED
  2. `uv sync --frozen --extra dev` PASSED
  3. `uv run --frozen ruff check .` PASSED
  4. `uv run --frozen ruff format --check .` PASSED
  5. `uv run --frozen mypy src tests` PASSED
  6. `uv run --frozen python scripts/docs_consistency_check.py` PASSED
  7. nonroot022 child `uv run --frozen pytest -q` PASSED (3663 passed, 28 skipped, 0 failed, 613.89 s)
  8. `uv build` PASSED
  9. `uv run --frozen python scripts/artifact_policy_check.py --dist dist --inspect` PASSED
  10. `uv run --frozen python scripts/artifact_policy_check.py --dist dist --install-smoke` PASSED
  11. `uv run --frozen python --version` PASSED (Python 3.12.15)
  12. `uv run --frozen python -m compileall -q src tests oap/bin scripts` PASSED
  13. `uv run --frozen python scripts/dev_provenance_manifest.py --verify` PASSED
  Mode law measured live: driver 248747 (uid 1001, umask 0077), uv 248892 (uid 1001, umask 0022, birth 190645431). The driver's own `/proc/<pid>/children`-based pytest-child lookup reported NOT-FOUND (path unavailable on this host) and that fact is preserved; the actual pytest child 248903 (PPID 248892, uid 1001, umask 0022, birth 190645433) is established by root's independent bounded all-thread `task/*/children` read — `reviews/017-aj-final-gate-live-context.json`, `reviews/017-aj-final-gate-result.json`. All 39 gate captures 0600 uid 1001 under the 0700 run dir.
- `git archive` at B (stdout empty, `--output` to protected 0600 file; never emitted to tool output) + clean-tree extraction: PASSED — 201 input-map entries git-B == clean tree; 17 helpers identical; `uv build` from the clean tree exit 0, BOTH artifacts byte-identical to manifest B and repo `dist/`; 198 source-bearing sdist entries byte-exact vs the clean tree; wheel METADATA == sdist PKG-INFO (22728 B). The first manual entry-proof invocation failed on its own script (sdist prefix not stripped; wheel opened as tar) and was corrected in place — a manual-verification setup occurrence, not a product/gate failure — `reviews/017-aj-clean-artifact-independent-review.json`.
- CI at implementation head B: PASSED — all 10 required checks SUCCESS (`test`, `docker`, `docker-published`, `operator-session`, `gateway-contract`, `cache-native-fixture`, `cache-native-containment`, `CodeQL`, `Analyze (python)`, `Analyze (actions)`) — `reviews/017-aj-B-all-ten-ci-success.json`.
- Live model/service evidence: the attempt's model traffic (7 POSTs) was fixture-internal to the owned reference fixture's fake provider; host-side fixture-scoped control admissions (2 API requests, 2 admitted / 0 refused; 38 Docker admissions) occurred on the host control surface, not inside the CID; no real model, Gateway or protected-service call; bounded calls only.
- Protected 18020/Qwen/Codex fixture changed: NO.

## GitHub CI / required checks
- Implementation head B: all 10 required checks SUCCESS (see Verification).
- All required green at drafting: YES (at B).
- Report-head checks may be pending; strategy verifies.

## Local setup/dependencies
- Repo venv Python 3.12.15, uv 0.12.5, frozen installs; no new dependencies, no sudo. The attempt ran the owned fixture owner/controller/fake provider under the reference fixture (owned fixture scope only); no new adapter or protected-service deployment, and no repo-local service change.
- The observed manual docs-generation Python invocations in this delivery round ran without `-B`; that is recorded as a bounded delivery qualification for those invocations only — no universal `-B` compliance claim and no historical audit.

## Documentation
- Updated: human `ARCHITECTURE.md`; all three compact `ARCHITECTURE-for-agents.md` copies (byte-equal); `TESTING.md`; `docs/CACHE-OBSERVATION-CONTRACT.md`; `docs/CACHE-REWORK-LEDGER.md` — measured actual paragraphs with the exact boundary (bounded `native_ready=true` verdict for this reference-fixture attempt only; D09 NOT RUN; 018-024 mandatory).

## Safety/scope confirmations
- No real credentials or private customer content retained; the retained evidence is narrowly verified synthetic data: the host-side synthetic envfile did persist its synthetic CODEX_HOME/provider-key values (0600) until the owned cleanup, and the retained protected AJ records contain the exact known synthetic selected call/result frames plus key names and SHA. No complete historical privacy/raw-log audit claim is made.
- No unrelated files touched; production/protected resources unchanged; no merge, no auto-merge, no second PR.
- Five bounded process deviations of the attempt itself are disclosed by immutable reference in the qualification review (ROOT aux detector false assumptions cleared by Ctrl-U with no signal/flush; ROOT aux pane_current_command==docker false; phase-reader opened_epoch pre-open; earlier curl bounds / stage-log setup; stage log O_EXCL 0600 precreated after approval).
- Delivery process deviations (this report round): `gh pr edit` GraphQL projectCards deprecation error; the first REST PATCH attempt stored a literal `@file` path string as the PR body, immediately corrected with a JSON `--input` PATCH (final body as reviewed); the first manual artifact entry-proof script bug corrected in place (above).

## Known limitations / blockers
- D09 (genuine multi-chunk process completion and the process/chunk association) remains NOT RUN; the AJ format PASS is bounded to this ONE reference-fixture attempt and the measured `native_ready=true` verdict is recorded for it only.
- Required-syntax matrix (contract section 11b): each handoff 6.2 family literal carries its exact EARNED / RECOGNIZED-ONLY / UNSUPPORTED status; the `ls`+`cat` variant and the unguarded/labeled loop variants remain pending scope audit, and D01-D10 strategic acceptance remains PENDING.
- No blocker to this delivery; whole-017 acceptance remains with strategy.

## Recommended strategic follow-up
- Accept the 017-aj actual format qualification records (bounded scope) by immutable reference.
- Then whole-017 acceptance per the contract (including an actual D09 multi-chunk qualification and the pending required-syntax variants), after which 018 activation (requires whole-017 merged + remote-main verified) and the 018-024 succession remain mandatory.

## Supporting files (protected inventory)
- Explicit 27-entry inventory (path/size/full SHA-256/uid/mode): `/home/janezp/oap-017aj-work/delivery/supporting-file-inventory.json`, 6172 B, SHA-256 `870896ec26652bdf23324bc301e1817c7f9c2bef1545fb56cccb37d56e58fcae` — retained AJ records, stage log, frozen operator/runbook/checks candidates, phase-control wait helper, gate aggregates + live measurements + driver, clean-archive captures + both rebuilt artifacts, final PR payload files.

# OAP Coding-Agent Report — 024-k

## Work order
- Identifier: 024-k; order path: `oap/orders/024-k-cache-qualification-evidence-and-artifact-handoff.md`; numeric objective 024
- PR mode: AMENDED_EXISTING_PR (PR #32)

## Status
COMPLETE

## Executive summary
The round closed the 024 cache-qualification evidence and delivered the development
artifact handoff on PR #32: the strategy-completed genuine native run was reviewed
against the closed content-free qualification record and its key rows independently
verified; the ledger now records the earned R04 scope and the related R01/R05/M01
native halves, the M02 real-model direct-restart/vision evidence, and the 024-b through
024-k round statuses with the handoff record (all pending strategic acceptance); the
private 024-h harness ASGI receive-branch defect was corrected with the existing fake
preflight and a focused end-of-request receive check both passing; stable
project-contained copies of the verified 024-j development wheel and sdist (exact
manifest provenance, both digests matching the 024-j manifest) were delivered; the
development provenance manifest was re-bound to the documentation-only source commit,
with the rebuilt wheel verified byte-identical to the live-tested wheel and the ledger
confirmed as the sole changed mapped input (the sdist re-digested for that
documentation-bound change). No live model call, Codex startup, release, deployment,
gateway, or benchmark work occurred in this round.

## Authoritative GitHub state
- Repository: ulfe-lmi/slaif-local-coding; PR #32 OPEN
  (https://github.com/ulfe-lmi/slaif-local-coding/pull/32)
- Base: `main`; head branch: `oap/024-cache-real-codex-qualification`
- Starting remote SHA (024-j report head): `b93554a71f91d7e038c1be92886c0ae6f9deff92`
- Implementation head SHA: `f50a0a66e67f0f95c5c171e692ec0b251546d69e`
- Report publication commit: SELF
- Implementation commits pushed before report:
  - `b63767031283d1012544565474d1f70ce6102bbb` — source A' (ledger update + activated 024-k transcript; 3 files, 80 insertions, 7 deletions)
  - `f50a0a66e67f0f95c5c171e692ec0b251546d69e` — development provenance manifest at A' (manifest-only, 1 file, 5 insertions, 5 deletions; first parent A')
- New PR this round: no; amended existing PR #32: yes; merge performed: NO

## Changes and files
- `docs/CACHE-REWORK-LEDGER.md` — six line replacements, State cells only: R04
  (NOT RUN → EARNED at the bounded 024-k native scope with its recorded
  qualifications); R01 and R05 (appended the actual-upstream native halves, both now
  EARNED at their app-boundary plus bounded 024 native scopes); M01 (appended the
  measured actual-model normal-path half, now EARNED); M02 (stays PARTIAL; appended
  the real-model direct-restart and vision evidence with its recorded
  qualifications); 024 objective row (appended the 024-b through 024-k round
  statuses, the artifact-handoff digests/provenance block, and the pending-strategic-
  acceptance note). Approved criterion text and test boundaries unchanged; no new
  plan or unrelated documentation. `git diff --numstat` = 6/6 lines.
- `oap/orders/024-k-cache-qualification-evidence-and-artifact-handoff.md` +
  `oap/active` — exact activated transcript, committed byte-unchanged (024-j → 024-k).
- `packaging/dev_provenance_manifest.json` — re-bound at source A' (319 inputs;
  wheel digest unchanged, sdist digest updated for the documentation-bound change).
- Private (project-work-artifact only, never committed): the 024-h harness ASGI
  receive-branch correction in
  `oap-024h-work/harness/candidate_024h.py` (`_FactMiddleware._receive` post-body
  branch now delegates to the real ASGI receive instead of returning a fabricated
  `http.disconnect` after the final request-body frame) and the focused check
  `oap-024h-work/harness/receive_focus_check_024k.py`.

## Acceptance evidence
### Criterion 1 — Closed evidence review and independent verification
- The closed qualification record
  (`oap-024h-work/strategy-client/native-024j-qualification.json`) and its referenced
  private run facts were reviewed; artifact provenance binds source
  `7d2e7de09c9107d82b9329eb8ac86926112c1e5d` and manifest head
  `d0cf62ca554ac5cb3be6a4531a0ba87bd1ba289e`, with the wheel and sdist digests exactly
  matching the 024-j manifest.
- Key rows independently verified against the private observer run facts and the
  native session record (structural verification only; raw content stays private):
  - combined read: ONE actual `exec_command` invocation read the two full files
    together, matched their exact combined bytes, and retained the tool wrapper
    through the source-span replacement;
  - manual `/compact` completed exactly once at `2026-11-27T16:06:31.058Z`; the
    replacement history kept the exact root with six message items and no tool/source
    carrier (the native session record shows exactly one compaction event at that
    timestamp, six message items after it, and one `function_call` + one
    `function_call_output` — the combined read);
  - warm and post-compaction requests 4, 7 and 8 used the same two byte-identical
    compiled regions with zero compiler dispatches and zero recovery reads; both
    post-compaction requests kept the root carrier with the source span replaced and
    omitted the dependency carrier;
  - the real bundle-level no-tool follow-up stated both applicable rules;
  - the successful run: eight real main requests returned 200 and two real compiler
    calls occurred; per-request compiler attribution is NOT claimed (the private
    observer did not correlate concurrent rows);
  - the separate real root-present request: exact before/after prefix and suffix
    hashes matched outside the replaceable span despite the old wrapper predicate's
    false result; no lost-root recovery claim.
- Scope disclosure recorded: with subagent tools advertised, an actual 4,411-character
  function description would hit the existing 4,096-character bound (kept closed; the
  run disabled them). The per-file attribution question was declined, consistent with
  the bounded combined-bundle evidence. Prior 024-c through 024-g independent findings
  are preserved in the ledger.
- Result: evidence consistent across the closed record, the observer facts, and the
  native session structure. PASSED (at its bounded closed-facts scope).

### Criterion 2 — Bounded ledger update
- Only the existing qualification references changed (six line replacements in State
  cells; criterion wording and test boundaries preserved): R04 EARNED at the bounded
  024-k native scope with qualifications; R01/R05/M01 appended with the native halves;
  M02 stays PARTIAL with the real-model direct-restart/vision evidence and its
  qualifications appended; the 024 row records the 024-b through 024-k round statuses
  (PASS/PARTIAL per round), the artifact handoff block (both digests, manifest at
  `d0cf62c`, source `7d2e7de`), and "all 024 evidence remains pending strategic
  acceptance".
- `scripts/docs_consistency_check.py`: OK (19 claim docs checked). PASSED.

### Criterion 3 — Private harness receive-branch correction
- The defect: the private 024-h inbound observer returned a fabricated ASGI
  `http.disconnect` after the final request-body frame, which cancelled the first
  valid native stream. The successful live run's in-memory change delegated
  subsequent receives to the real ASGI receive; that exact correction is now applied
  to the project-private harness (`candidate_024h.py` post-body branch:
  `return await receive()`). No product stream or cache code changed; no new
  diagnostic mechanism added.
- Focused check (`receive_focus_check_024k.py`, which extracts the ACTUAL shipped
  `_receive` source and runs a streaming scenario with the client staying connected,
  with the pre-fix literal as control): PASSED, exit 0 — fixed path
  {sent_chunks 3, cancelled false, completed true, final_disconnect_seen true,
  post_body_real_receive_calls 4}; pre-fix control {cancelled true, sent_chunks 0,
  post_body_real_receive_calls 0}.
- Existing fake preflight (`bash harness/run_024h.sh`, its pinned 024-a-wheel venv):
  new run facts `outcome: PASS`, 4/4 main and 2/2 compiler within bounds,
  `over_bound: false`, `round_problems: []`, R3 blocks byte-identical to the
  previous round (fixed point), `wrapper_shape_check` all true (the prior
  wrapper-flag qualification preserved), ready socket-inode ownership proven, stop
  facts clean, `wheel_sha256_verified: true`, venv Python 3.12.15. The preflight is
  product-independent ASGI-protocol verification (it pins the 024-a wheel); the
  024-j wheel's live qualification is the strategy native run above. PASSED.

### Criterion 4 — Development artifact handoff
- Stable project-contained copies delivered under
  `/home/janezp/codex-supervision/slaif-local-coding/work-artifacts/oap-024a-work/024k-artifact-handoff/`
  (directory mode 0700):
  - `slaif_local_coding-0.1.0-py3-none-any.whl` — sha256
    `0a02f93b5f9bacaf0f3e86186265884fafdab5a8a999d0ef89d2fa92b48a3c4c` (4,490,994 B)
  - `slaif_local_coding-0.1.0.tar.gz` — sha256
    `80811eef23927b90293123da4fc1dbaec25653d7ab493bf61232333b0e37453c` (6,295,950 B)
  - `dev_provenance_manifest-at-d0cf62c.json` — sha256
    `e94e103dd8a89a50b379d963839ff85935eeda50c77eb5508f81118f54f8cfd1`
- Both archives match the 024-j manifest and the source/provenance commits named by
  the order (re-verified by digest in this round). These archives remain the 024-j
  bytes and are preserved as the original handoff. PASSED.

### Criterion 5 — Provenance refresh, wheel identity, sdist documentation-bound digest
- Source A' (`b63767031283d1012544565474d1f70ce6102bbb`) changes the tracked mapped
  inputs by exactly one file: `docs/CACHE-REWORK-LEDGER.md` (the order transcript and
  `oap/active` are not artifact inputs; `git diff --name-only b93554a..A'` = ledger,
  order, active only).
- Clean rebuild at A' (umask 022, `uv build`, fresh `dist/`): wheel sha256
  `0a02f93b5f9bacaf0f3e86186265884fafdab5a8a999d0ef89d2fa92b48a3c4c` — BYTE-IDENTICAL
  to the live-tested 024-j wheel; sdist sha256
  `94e2200a669343efd62353adbcc9e8fd325dc61cdc2667059dcd3297f4f51e7d` (6,297,593 B,
  317 entries) — the new documentation-bound digest, recorded separately. The sdist's
  ledger member was verified byte-equal to the A' ledger, and the sdist still contains
  no AGENTS.md and no oap/ content, so the ledger is the sole changed mapped input.
- Development provenance refreshed: `--generate` at A' (319 inputs; wheel digest
  unchanged, sdist digest updated) committed manifest-only as B''
  (`f50a0a66e67f0f95c5c171e692ec0b251546d69e`); `--verify --dist dist` reports
  `development provenance OK: state=development head=f50a0a66e67f`. PASSED.

## Verification
- `uv lock --check`: PASSED (exit 0)
- `uv sync --frozen --extra dev`: PASSED (exit 0)
- `uv run --frozen ruff check .`: PASSED (exit 0)
- `uv run --frozen ruff format --check .`: PASSED (exit 0)
- `uv run --frozen mypy src tests`: PASSED (exit 0; "Success: no issues found in 208 source files")
- `uv run --frozen python scripts/docs_consistency_check.py`: PASSED (OK, 19 claim docs checked)
- `umask 022; uv run --frozen pytest -q`: PENDING — the pre-existing managed local
  full-suite run (started on the A' tree content before the A' commit; identical
  content) was still running at publication (last observed progress 34%); controlled
  log: `/home/janezp/codex-supervision/slaif-local-coding/work-artifacts/oap-024a-work/gate-024k.log`.
  Cited separately for the tested wheel: the 024-j full local gate over the
  byte-identical wheel `0a02f93b…` at source `7d2e7de`/manifest `d0cf62c` — 7232
  passed, 29 skipped, 0 failed. Per the order and operator instruction, no additional
  full run was started.
- `uv build`: PASSED (exit 0; wheel byte-identity verified in Criterion 5)
- `uv run --frozen python scripts/artifact_policy_check.py --dist dist --inspect`: PASSED (exit 0)
- `uv run --frozen python scripts/artifact_policy_check.py --dist dist --install-smoke`: PASSED (exit 0)
- `uv run --frozen python scripts/dev_provenance_manifest.py --verify --dist dist`: PASSED (development provenance OK)
- Interpreter: `uv run --frozen python --version` → Python 3.12.15 (repo venv)
- `uv run --frozen python -m compileall -q src tests oap/bin scripts`: PASSED (exit 0)
- `git diff --check origin/main..HEAD`: PASSED (exit 0, no whitespace errors)
- Harness: focused receive check PASSED (exit 0); existing fake preflight `outcome: PASS` (facts recorded in Criterion 3)

## Live model/service evidence
- This round: NONE from the coding agent — no model calls, no Codex startup, no
  live upstream request, no protected-fixture contact, no release/deployment/gateway/
  benchmark work.
- The strategy-completed genuine native run (recorded via the closed content-free
  facts reviewed in Criterion 1): actual 0.164.0 Codex binary, installed 024-j wheel,
  qwen3.8-27b A100 Q8 direct through the loopback adapter, read-only fixture
  workspace, standard Responses, grammar-based patch and subagent tools disabled;
  eight main requests 200, two compiler calls, single session lineage, clean
  teardown; the protected worker/profile restored and all test listeners closed per
  the order.

## GitHub CI / required checks
- Observed at implementation head `f50a0a66e67f0f95c5c171e692ec0b251546d69e` before
  the report commit: Analyze (actions) pass; gateway-contract pass;
  cache-native-containment pass; CodeQL skipping; Analyze (python) pending;
  cache-native-fixture pending; docker pending; docker-published pending;
  operator-session pending; test pending.
- All required green at drafting: NO (pending items recorded as PENDING per the
  order, for strategic follow-through; not waited on twice for the unchanged suite).
- Report-head checks may be pending; strategy verifies.

## Local setup/dependencies
- Python 3.12.15 repo venv (`checkout/.venv`), `uv` locked/frozen installs, umask 022
  test/build context; harness driver venv under the private 024-h work directory.
  No new services, no sudo, no protected-config change.

## Documentation
- Updated: `docs/CACHE-REWORK-LEDGER.md` only (six State-cell line replacements, per
  the order's bounded scope). The provenance manifest is a tracked artifact-input
  record, refreshed as ordered. No new plan or unrelated documentation added.

## Safety/scope confirmations
- Unrelated files: AGENTS.md (operator local wording) remains UNSTAGED and was never
  committed; this round's tracked changes are exactly the ledger, the activated
  024-k transcript, `oap/active`, the manifest, and this report.
- Secrets/raw content: none in Git or this report; the private run facts and native
  session record are referenced by closed content-free facts only; no bodies,
  prompts, credentials, or private transport details reproduced.
- Protected 18020/Qwen/Codex fixture changed: NO.
- Release/deployment/gateway/benchmark dispatch/real upstream request/Codex
  startup: NONE performed.
- Extra objective PR: NO; coding merge: NO; active/order bytes edited: NO;
  report commit report-only: yes.

## Known limitations/blockers
- The full local pytest at A' is PENDING in its pre-existing managed run (controlled
  log cited above); no second full run was started, per order/operator instruction.
- GitHub CI items listed as pending at the implementation head.
- Per-request compiler attribution is uncorrelated by the private observer and not
  claimed; no lost-root recovery claim; the 4,411-vs-4,096 subagent-tool description
  bound is a disclosed scope fact; the 024-d whole-body presence remains
  unlocalized (compiler content echo recorded as a possible explanation only); all
  024 evidence remains pending strategic acceptance.

## Recommended strategic follow-up
Factual only; strategy decides: verify the report-head CI items (pending at the
implementation head) and the outcome of the managed local pytest run in the cited
controlled log before acceptance/merge of PR #32.

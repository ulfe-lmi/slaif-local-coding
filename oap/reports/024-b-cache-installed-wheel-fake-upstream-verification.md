# OAP Coding-Agent Report — 024-b

## Work order
- Identifier: 024-b; order path `oap/orders/024-b-cache-installed-wheel-fake-upstream-verification.md`; numeric objective 024
- PR mode: AMENDED_EXISTING_PR

## Status
COMPLETE (the sole installed-wheel loopback probe evidence gap is closed; the actual-model, genuine-Codex and native-compaction criteria remain pending as ordered)

## Executive summary
024-b closed the single remaining 024-a evidence gap: the installed-wheel loopback probe test, which had skipped in the 024-a runs, was executed once against the 024-a clean-built wheel (SHA-256 `e82f5ab8b7fa7833e7fbb5734c7612f81f149d2e6a4aae1e53275004437536d3` verified before the run). The test launched the exactly installed adapter on 18031 and its probe-owned synthetic peer on 18032 serially and passed, earning the complete content-free fact record (seven main forwards, two compiler calls, dependency replacement and source-absent reinjection, zero new compiles on replay, both listeners cleaned up, the actual interpreter and install method). The intervening diff from the 024-a implementation head changes only the transcript (oap/ paths), so the identified 024-a locked gate and clean artifact proof are reused for the identical software inputs, with provenance verification and the diff check rerun at the new head. No real inference is authorized by the order and none was performed; the actual-model, genuine-Codex and native-compaction criteria stay pending.

## Authoritative GitHub state
- Repository: ulfe-lmi/slaif-local-coding; PR https://github.com/ulfe-lmi/slaif-local-coding/pull/32 (OPEN, non-draft, unchanged branch `oap/024-cache-real-codex-qualification`)
- Base: `main` at `fe9538452f7715c305ea2ae9da60726cb73d8d45` (the order's verified base); round-start remote head `511595704efdfe52832fc1c191abcaced1c77689` (the 024-a report-only head) and prior implementation `745e892a5077679c7f43aac3460d6cf11bbd65b9` as stated by the order
- Implementation head SHA: d47068851682cac2e41243c47574b00d476f32af
- Report publication commit: SELF
- Implementation commits pushed before report: `d47068851682cac2e41243c47574b00d476f32af` (transcript-only: the unchanged activated 024-b order and `oap/active`; sole parent `511595704efdfe52832fc1c191abcaced1c77689`)
- New PR this round: NO; amended existing PR #32: YES; merge performed: NO

## Changes and files
- `oap/orders/024-b-cache-installed-wheel-fake-upstream-verification.md` (new; the unchanged strategic bytes copied from the primary checkout, sha256 `f2b961261341f30b135e05b167bc4a8aed366d429acf5c5a1a385a788e35a6ca`, byte-verified against the primary)
- `oap/active` (`024-a` → `024-b`; unchanged strategic bytes, sha256 `de47e1483b58bd1c96bd7e3d50f1b8380bc44dbf5097df1bd3b016c34b34e5ca`, byte-verified against the primary)
- No product, test, script, packaging, documentation or manifest change.

## Acceptance evidence
### Criterion 1 — the sole installed-wheel loopback probe, executed
- Result: PASSED at its stated scope (fake peers only; no real inference).
- Preconditions recorded before the run (captured in the 024-b work directory): the 024-a clean-built wheel under `work-artifacts/oap-024a-work/clean-build-024a-r1/dist/` verified at SHA-256 `e82f5ab8b7fa7833e7fbb5734c7612f81f149d2e6a4aae1e53275004437536d3`; 18031 and 18032 free (0 listeners); interpreter Python 3.12.15 via `uv run --frozen`; no actual credential sourced (the test sets no key environment references; the probe generates its own synthetic credentials).
- Exact run (umask-022 test context, unmasked exit): `SLAIF_LIVE_TEST=1 SLAIF_V1_PROBE_WHEEL=<024-a clean dist wheel> SLAIF_V1_PROBE_WHEEL_SHA256=e82f5ab8b7fa7833e7fbb5734c7612f81f149d2e6a4aae1e53275004437536d3 uv run --frozen pytest -q tests/test_live.py::TestLiveV1Qualification::test_probe_run_completes_with_content_free_facts` → PASSED — 1 passed in 8.44s, pytest exit 0. The test launched the exact installed adapter (a fresh candidate venv from the exact wheel on 18031) and its own synthetic peer on 18032 serially; the protected private evidence (facts file 0600 inside the 0700 run directory) stayed in the fresh pytest scratch path, with the content-free fact record copied into the 024-b work directory.
- Verified facts (from the single-line content-free `v1-probe-facts-v1` record, run_id `51542b5225992375a7dfcaf52e38d5b7`, all asserted by the passing test):
  - Seven main forwards: `main_forward_count` 7, `requests_used` 7, all seven rounds (r1-bootstrap, r2-acquire, r3-replay, r4-source-absent, r5-stream, r6-stream-cancel, r7-post-cancel) returned 200.
  - Two compiler calls: `compiler_call_count` 2; `root_demand_carries_root_source` and `file_demand_carries_file_source` true (the actual compiler demands carry the exact decoded sources); `file_demand_foreign_candidate_count` 0.
  - Dependency replacement: r1 root bootstrap with `r1_root_source_absent` true alongside `r1_live_markers` 1 and `r1_compiled_blocks` 1; r2 acquisition with `r2_root_source_absent` and `r2_file_source_absent` true alongside `r2_live_markers` 2 and `r2_compiled_blocks` 2 (raw originals gone from the actual forwarded bodies, live markers in).
  - Source-absent reinjection: the r4 round reconstructs the required working set with `r4_root_source_absent` and `r4_file_source_absent` true, `r4_compiled_blocks` 2 and `r4_new_compiler_calls` 0.
  - Zero new compiles on replay: `r3_fixed_point` true with `r3_new_compiler_calls` 0, `r7_fixed_point` true with `r7_new_compiler_calls` 0, and `r6_forward_matches_r2` true.
  - Streaming and cancellation: `r5_completed` true (first SSE event `response.created`), `r6_cancelled` true; `deadline_ok` true, `response_bytes_ok` true; healthz/readyz/models all 200.
  - Model contract: `model_contract_ok` true for the declared model `qwen38-27b` (the operator's permitted catalog slug).
  - Cleanup: after the run both 18031 and 18032 refuse connections and the run lock is released (asserted by the test); exactly one fresh 0700 run directory with exactly one 0600 facts file whose `run_id` matches.
  - Content-free: the test asserts that no fixture source text (root body, dependency body or read command) crosses the probe's stdout boundary, and the retained record carries only closed facts.
  - Actual interpreter and install method: the test ran under Python 3.12.15 (`uv run --frozen`); the candidate venv interpreter is Python 3.12.15, and its `direct_url.json` records a noneditable install of the exact SHA-verified 024-a clean-built wheel (no editable marker). The plain wheel install uses runtime dependency resolution (fastapi>=0.116<1, httpx>=0.28<1, prometheus-client>=0.22<1, pydantic>=2.11<3, tokenizers==0.22.2, uvicorn>=0.35<1); no lock file exists in the candidate venv. A dependency-lock verification of the candidate venv was NOT run, so none is reported.

### Criterion 2 — reused 024-a locked gate and clean artifact proof for identical software inputs
- Result: PASSED (reused at the identified 024-a heads; re-verifications rerun at the new head).
- Intervening diff proof: `git diff --name-only 745e892a5077679c7f43aac3460d6cf11bbd65b9 d47068851682cac2e41243c47574b00d476f32af` yields exactly `oap/active`, `oap/orders/024-b-cache-installed-wheel-fake-upstream-verification.md` and `oap/reports/024-a-cache-actual-model-qualification-preparation.md` — zero paths outside `oap/`, i.e. the intervening diff changes only the transcript and the software inputs are identical.
- Reused: the 024-a fifteen locked verification commands at `745e892a5077679c7f43aac3460d6cf11bbd65b9` (all fifteen rc=0; the umask-022 full pytest 7209 passed, 29 skipped) and the 024-a full clean-archive artifact proof at `745e892a5077679c7f43aac3460d6cf11bbd65b9` (all assertions passed; rebuilt artifacts byte-identical to the manifest and to the repo gate `dist/`; fresh explicit Python 3.12.15 noneditable install verified).
- Rerun provenance verification against the wheel/sdist at T: the gate `dist/` artifacts remain byte-identical to the manifest (wheel `e82f5ab8…`, sdist `0a7b084b…`); `uv run --frozen python scripts/dev_provenance_manifest.py --verify --dist dist` → PASSED (exit 0; "development provenance OK: state=development head=d47068851682").
- Rerun diff check at T: `git diff --check fe9538452f7715c305ea2ae9da60726cb73d8d45 d47068851682cac2e41243c47574b00d476f32af` → PASSED (exit 0, no output).

### Criterion 3 — ten implementation-head checks
- Result: all ten checks PASSED — CodeQL pass; Analyze (actions) pass; Analyze (python) pass; cache-native-containment pass; cache-native-fixture pass; docker pass; docker-published pass; gateway-contract pass; operator-session pass; test pass (12m55s).

## Verification
- `SLAIF_LIVE_TEST=1 SLAIF_V1_PROBE_WHEEL=<024-a clean dist wheel> SLAIF_V1_PROBE_WHEEL_SHA256=e82f5ab8b7fa7833e7fbb5734c7612f81f149d2e6a4aae1e53275004437536d3 uv run --frozen pytest -q tests/test_live.py::TestLiveV1Qualification::test_probe_run_completes_with_content_free_facts` (umask-022 context, Python 3.12.15): PASSED — 1 passed in 8.44s, unmasked exit 0
- `uv run --frozen python scripts/dev_provenance_manifest.py --verify --dist dist` at T: PASSED — exit 0
- `git diff --check fe9538452f7715c305ea2ae9da60726cb73d8d45 <T>`: PASSED — exit 0, no output
- The 024-a fifteen locked verification commands at `745e892a5077679c7f43aac3460d6cf11bbd65b9`: PASSED (reused, not rerun — identical software inputs per the transcript-only intervening diff above) — all fifteen rc=0; full pytest 7209 passed, 29 skipped
- The 024-a full clean-archive artifact proof at `745e892a5077679c7f43aac3460d6cf11bbd65b9`: PASSED (reused, not rerun — identical software inputs) — all assertions passed
- Live model tests beyond the one ordered installed-wheel probe: NOT RUN — no real inference is authorized by this order and none was performed

## Live model/service evidence
- No real inference was performed in this round. The single run is the installed-wheel loopback probe against the probe-owned synthetic peer (fake peers only); no real credential was sourced, no client handoff occurred, and no protected change was made.
- The operator permits real use only of catalog `qwen3.8-27b` on A100 Q8. The strategy-recorded gateway-side facts for that service (model list 200 with that slug, `/health` 404, `/healthz` 200, Codex reasoning-envelope 400, plain Responses 200 SSE ending `response.failed`, plain Chat 200 with the expected synthetic text) mean real gateway Chat access exists while the private candidate main/compiler route still is unavailable; the actual candidate-model, genuine-Codex and native-compaction criteria therefore remain pending.

## GitHub CI / required checks
- Implementation head `d47068851682cac2e41243c47574b00d476f32af`: all ten checks PASSED — CodeQL pass; Analyze (actions) pass; Analyze (python) pass; cache-native-containment pass; cache-native-fixture pass; docker pass; docker-published pass; gateway-contract pass; operator-session pass; test pass (12m55s)
- All required green at drafting: yes
- Report-head checks may be pending; strategy verifies.

## Local setup/dependencies
- The same linked checkout and pinned Python 3.12.15 venv (uv 0.12.5); no sudo, no new services. Durable 024-b evidence under `work-artifacts/oap-024b-work` (0700): the run startup capture, the unmasked test console log, the content-free fact record (0600), the scratch run-directory location, the interpreter/install-method facts, and the rerun provenance/diff-check captures.

## Documentation
- Not required: this round changes no behavior, configuration, security, tests, operation or limitation — it commits only the unchanged activated order/active transcript. The installed-wheel probe is the same documented opt-in test from 024-a, now run at its evidence scope.

## Safety/scope confirmations
- Unrelated files: none; the operator's existing local `AGENTS.md` bytes remain UNSTAGED in the linked checkout (the sole working-tree entry; never staged).
- Secrets/raw content: none printed, committed or retained beyond the closed content-free fact record; the protected facts file stays 0600 under its 0700 run directory in the fresh pytest scratch path.
- Protected 18020/Qwen/Codex fixture changed: NO. No real key sourced; no service, Gateway, network or profile change; no client handoff; no new Codex or model-client startup; no deployment, registry or release.
- Extra objective PR: NO (the same PR #32 was amended). Coding merge: NO; auto-merge: NO.
- Active/order edited: NO (unchanged strategic bytes copied from the primary, sha256-verified). Report commit report-only: yes (verified at publication).

## Known limitations/blockers
- The actual-model, genuine-Codex and native-compaction criteria remain pending as ordered. The operator-permitted real use (catalog `qwen3.8-27b` on A100 Q8) is not authorized for real inference in this round, and the strategy-recorded gateway-side facts (`/health` 404; plain Responses ending `response.failed`) show the private candidate main/compiler route is still unavailable for a real invocation.

## Recommended strategic follow-up
Factual only; strategy decides. A later exact order can name the authorized upstream serving the origin health path, the protected credential references, the per-call budgets and the observed model contract for the first real invocation; the genuine-compaction layer separately requires the human-approved protected client-profile routing change (the provider `base_url` pointed at the loopback candidate with the supported local compaction mode staying on the ordinary `/v1/responses` path).

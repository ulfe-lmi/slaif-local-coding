# OAP Coding-Agent Report — 024-j

## Work order
- Identifier: 024-j; order path `oap/orders/024-j-native-responses-function-namespaces.md` (activated bytes sha256 `5eb29730748c89ad5ca9ce50af45bb8ac235e0fca2481789c483f092127cc904`, committed unchanged); numeric objective 024.
- PR mode: AMENDED_EXISTING_PR (PR #32, branch `oap/024-cache-real-codex-qualification`, base `main`).

## Status
COMPLETE

## Executive summary
The demonstrated ordinary Responses compatibility gap in the governed v1
accounting path is closed: the closed budget mapper now counts the standard
Responses function namespace tool shape through the pinned Qwen/vLLM
effective-name projection, and the Responses `function_call` history counts
the optional `namespace` field under the pinned truthy-prefix rule. The
projection is accounting-only — the forwarded wire keeps the actual standard
declarations, namespace fields, call IDs and results. Flat tool behavior, the
closed fail-closed shape handling and the existing bounds are preserved. The
focused, broad, static, documentation, build and provenance gates all pass
locally at the implementation head; nine of ten GitHub checks pass at that
head and the `test` job was still running when this report was drafted.

## Authoritative GitHub state
- Repository `ulfe-lmi/slaif-local-coding`; PR #32
  https://github.com/ulfe-lmi/slaif-local-coding/pull/32 — OPEN, base `main`,
  head `oap/024-cache-real-codex-qualification`.
- Starting remote SHA (round start): `55ab5ddbde676c1fb2d592c0e91a1840dd4f4ccf`
  (the 024-i report head; first parent
  `2a7b6db2f68de6782b9ead82eaa7b4be417b3da8`).
- Implementation head SHA: d0cf62ca554ac5cb3be6a4531a0ba87bd1ba289e
- Report publication commit: SELF
- Implementation commits pushed before the report:
  - A `7d2e7de09c9107d82b9329eb8ac86926112c1e5d` — the tested source diff
    (`v1_application.py`, `tests/test_v1_application.py`, `tests/test_app.py`,
    `ARCHITECTURE-for-agents.md`, plus the unchanged activated order and
    `oap/active`).
  - B `d0cf62ca554ac5cb3be6a4531a0ba87bd1ba289e` — the manifest-only
    development provenance manifest bound to source A (sole changed path
    `packaging/dev_provenance_manifest.json`, verified with `git show --stat`).
- New PR this round: NO; amended existing: YES; merge performed: NO.

## Changes and files
- `src/slaif_local_coding/constitution/bundles/v1_application.py`:
  - `_envelope_tools(payload, endpoint)`: a new `type == "namespace"` branch,
    Responses endpoint only. The namespace `name` must be a non-empty string
    and `tools` must be a list; each inner entry must be a flat
    `{"type": "function"}` shape with a non-empty string name, a string
    description (default empty) and dict parameters (default empty). Projected
    specs are emitted in declaration order as `namespace__name` with the
    function description and parameters kept; an empty inner list contributes
    no effective tools. The flat behavior, unknown top-level types and
    malformed shapes are unchanged and fail closed. A namespace on the Chat
    endpoint, or an unsupported nested type, stays the fixed typed 422.
  - `_envelope_structure` Responses `function_call` branch: the optional
    `namespace` is counted under the pinned vLLM truthy rule — absent, null or
    an explicitly empty string keeps the flat name, a truthy string prefixes
    the counted name (`namespace__name`), and a non-string non-null value is
    the closed invalid shape (fixed typed 422). Wire call IDs and result
    pairing are untouched; the projection is accounting-only.
  - No new bounds: `config.max_tools` (default 512, range 1..4096) is
    enforced by the existing `BundleBudgetPlan` counting over the flattened
    effective tool tuple, and the existing `BudgetToolSpec` name-length bound
    yields the fixed typed refusal for an over-long effective name.
- `tests/test_v1_application.py`: eight new unit test functions (23 focused
  unit cases with the parametrized tables expanded) over the observed shape
  (10 flat functions, two namespaces holding five and three declarations):
  the declaration-order projection; closed-form preamble counting under the
  real pinned tokenizer; the 17-fits/18-crosses `max_tools` boundary with
  `detail == "tools"`; the empty-namespace no-contribution; fourteen
  unsupported-shape closed refusals (missing/empty/non-string namespace name,
  non-list tools, inner not-dict/unsupported type/missing type/missing name/
  empty name, non-string description, non-dict parameters, namespace on Chat,
  unsupported top-level type); the actual wire shape (`type=function_call`,
  `name=a1`, `namespace=alpha`) counted as `alpha__a1` with the wire call
  preserved; the truthy-prefix table (absent/null/`""` flat, `"alpha"`
  prefixed, `1` refused); the 272-character effective-name closed refusal.
- `tests/test_app.py` (`TestV1WireClosure`): two new app-boundary cases.
  (1) The observed flat + two-namespace Responses shape over a deterministic
  fake upstream: HTTP 200, one main forward and one compile, outbound
  `tools` equal to the input `tools` (the standard namespace structure
  preserved), the `function_call` item keeping `name="alpha0"`,
  `namespace="alpha"` and its `call_id`, one live `[slaif-live:v1:` marker on
  the replaced root source, and the raw root source absent from the forwarded
  body. (2) The same shape at `max_tools=17`: the fixed typed 422
  `v1_selection_refused` with zero main forwards and one compile attempt; the
  identical request at `max_tools=18` on a fresh store: 200, one forward.
- `ARCHITECTURE-for-agents.md`: the detailed 022-e closed-mapper
  compatibility sentence gains one "Corrected in 024-j" clause recording the
  namespace projection rule and its accounting-only scope. No ledger entry,
  no objective-boundary recap and no new plan for this pending round.
- `oap/orders/024-j-native-responses-function-namespaces.md` + `oap/active`:
  committed byte-unchanged (the activated transcript).
- `packaging/dev_provenance_manifest.json`: refreshed at B against source A
  (319 inputs; wheel sha256
  `0a02f93b5f9bacaf0f3e86186265884fafdab5a8a999d0ef89d2fa92b48a3c4c`, sdist
  sha256 `80811eef23927b90293123da4fc1dbaec25653d7ab493bf61232333b0e37453c`);
  development state, not a release candidate, not released.

## Acceptance evidence
### Criterion 1 — focused regression over the observed shape; the Qwen accounting projection and tool order
- PASSED — `tests/test_v1_application.py` new cases: the projection emits
  `namespace__name` in declaration order with descriptions and parameters
  kept; the closed-form preamble count is proven under the real pinned
  tokenizer; flat behavior and tool order are preserved.
### Criterion 2 — real app transaction against a deterministic fake upstream; standard outbound namespace structure preserved
- PASSED — `TestV1WireClosure::test_responses_namespace_tools_forward_preserved_and_counted`:
  200, one main forward, one compile, outbound `tools` equal to the input,
  the call item keeps the wire `name`/`namespace`/`call_id`, the live marker
  is present and the raw root source is absent from the forwarded body.
### Criterion 3 — applicable closed shapes and bounds
- PASSED — the fourteen unsupported-shape closed refusals, the
  empty-namespace no-contribution, the flattened `max_tools` boundary
  (17 fits / 18 crosses, `detail == "tools"`) and the over-long effective
  name refusal: every unsupported shape stays the fixed typed 422, the
  existing `max_tools` bound applies to the flattened count, and the
  empty-string namespace keeps the flat name.
### Criterion 4 — namespaced function-call counted history where supported
- PASSED — `test_namespaced_function_call_history_is_counted`: the actual
  wire shape is counted as `alpha__a1` with the wire call/result unchanged.
### Criterion 5 — exact clean noneditable development wheel and sdist with normal source/provenance lineage
- PASSED — `uv build` at B: `slaif_local_coding-0.1.0.tar.gz` (6,295,950
  bytes, 317 entries) and `slaif_local_coding-0.1.0-py3-none-any.whl`
  (4,490,994 bytes, 90 entries); `artifact_policy_check.py --dist dist
  --inspect` and `--install-smoke`: `ok: true`, `violations: []`, fresh
  noneditable Python 3.12.15 install; `dev_provenance_manifest.py --verify
  --dist dist`: `development provenance OK: state=development
  head=d0cf62ca554a`. The sdist and wheel contain no `AGENTS.md`/`oap/`
  entry, so the recorded artifact bytes are clean against source A.
### Criterion 6 — focused and applicable broad checks
- PASSED — see Verification.
### Criterion 7 — existing affected compatibility/testing contracts updated
- PASSED — the single detailed 022-e closed-mapper clause in
  `ARCHITECTURE-for-agents.md`; `scripts/docs_consistency_check.py` passes.

## Verification
(all commands in the linked checkout, `umask 022`, Python 3.12.15, frozen uv;
real exits captured without masking pipelines)
- `uv lock --check`: PASSED (exit 0)
- `uv sync --frozen --extra dev`: PASSED (exit 0)
- `uv run --frozen ruff check .`: PASSED (exit 0)
- `uv run --frozen ruff format --check .`: PASSED (exit 0)
- `uv run --frozen mypy src tests`: PASSED (exit 0)
- `uv run --frozen python scripts/docs_consistency_check.py`: PASSED (exit 0)
- `uv run --frozen pytest -q` (umask 022): PASSED (exit 0) —
  `7232 passed, 29 skipped, 16 warnings in 1624.17s`
- `uv build`: PASSED (exit 0)
- `uv run --frozen python scripts/artifact_policy_check.py --dist dist --inspect`:
  PASSED (exit 0)
- `uv run --frozen python scripts/artifact_policy_check.py --dist dist --install-smoke`:
  PASSED (exit 0)
- `uv run --frozen python scripts/dev_provenance_manifest.py --verify --dist dist`:
  PASSED (exit 0)
- `uv run --frozen python --version`: PASSED — Python 3.12.15
- `uv run --frozen python -m compileall -q src tests oap/bin scripts`: PASSED
  (exit 0)
- per-file syntax scan of `oap/bin/*.py` and `scripts/*.py`: PASSED
  (0 failures)
- `git diff --check origin/main..HEAD`: PASSED (exit 0)
- Focused set before the broad run (recorded in the round): 23 unit + 2 app
  cases PASSED; the broader v1 application/budget/selection/replace suites
  196 passed; `TestV1WireClosure` 94 passed.

## Live model/service evidence
- NONE this round: no model call, no Codex startup, no protected-fixture
  contact (the order prohibits them).
- The retained 024-i closed observations are recorded here only as order
  facts (no raw bodies enter this repository or this report): the genuine
  0.164.0 retry seed (10 flat functions plus two standard Responses
  namespaces holding five and three function declarations, all object
  parameters) was refused with HTTP 422 `v1_selection_refused`; the
  empty-tools auxiliary request was countable and received HTTP 200; the
  separate backend run returned `v1_compiler_refused` with cause
  unestablished and is retained as an observed live outcome. The source read
  and the genuine compaction remain pending.

## GitHub CI / required checks
Checks observed at implementation head
`d0cf62ca554ac5cb3be6a4531a0ba87bd1ba289e` before the report commit:
- `docker`: PASS (1m48s)
- `operator-session`: PASS (1m12s)
- `CodeQL`: pass
- `cache-native-fixture`: pass
- `docker-published`: pass
- `gateway-contract`: pass
- `Analyze (actions)`: pass
- `Analyze (python)`: pass
- `cache-native-containment`: pass
- `test`: PENDING at drafting — the order explicitly permits honestly
  recording still-pending implementation CI for strategic follow-through.
- All required green at drafting: NO (`test` pending); report-head checks may
  be freshly triggered by the report push, and strategy verifies.
- Process note: at source A `7d2e7de`, the first run's `docker` and
  `operator-session` jobs failed in about 13-14 seconds; their job logs (read
  directly by the operator/strategy) show the committed development provenance
  manifest still bound the previous source snapshot `e3d7bf2` — specifically
  `v1_application.py` and the two test files. Manifest-only commit B refreshes
  the binding to A; at B both jobs PASS, and the A..B diff touches only the
  manifest.

## Local setup/dependencies
- Linked checkout
  `/home/janezp/codex-supervision/slaif-local-coding/work-artifacts/oap-024a-work/checkout`,
  repository venv (Python 3.12.15), frozen uv (lock check clean); no new
  dependencies; no sudo action. The gate log is retained under the private 024
  work-artifact directory (`oap-024a-work/gate-024j.log`); no runtime assets
  enter the repository.

## Documentation
- Updated (scoped): the single "Corrected in 024-j" clause in the detailed
  022-e closed-mapper sentence of `ARCHITECTURE-for-agents.md` — the existing
  compatibility contract text for the new namespace shape. Per the operator
  instruction, no ledger entry, no objective-boundary recap and no new plan
  for this pending round. `docs/CACHE-TOKEN-COMPILER-CONTRACT.md` needs no
  change (its tool-accounting text is generic to the effective counted tools
  and carries no flat-only statement).

## Safety/scope confirmations
- Unrelated files: `AGENTS.md` keeps the operator's local wording and stays
  unstaged/uncommitted; no other unrelated file touched.
- Secrets/raw content: none committed, printed or reported; the private
  request-shape records stay under the 024-h work directory and are referenced
  by closed facts only.
- Protected 18020/Qwen/Codex fixture changed: NO. No gateway routing, no live
  call, no benchmark, no client handoff.
- Required tests skipped/not run: none beyond the 29 honest fixture-gated
  skips of the suite (as in prior rounds).
- Extra objective PR: NO; coding merge: NO; active/order edited: NO (the
  committed order bytes are sha256-unchanged); report commit report-only: yes.

## Known limitations/blockers
- The GitHub `test` job at the implementation head was still running at
  drafting; strategy verifies the final exact-head checks per protocol.
- The retained `v1_compiler_refused` backend observation from 024-i keeps its
  cause unestablished; the source read and the genuine compaction remain the
  next authorized live steps (strategy-owned).
- The actual-model, genuine-client and genuine-compaction criteria remain
  NOT RUN and unearned.

## Recommended strategic follow-up
Factual only: wait for the `test` job (and any report-head rerun) on the final
exact head, then review. The next authorized native check in the visible right
pane can exercise the namespace shape against the candidate; the pending
source read and genuine compaction steps remain open under objective 024.

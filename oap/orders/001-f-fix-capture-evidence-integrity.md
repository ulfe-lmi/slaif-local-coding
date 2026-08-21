# OAP Work Order — 001-f

## Objective

Amend objective-001 PR #2 only. Correct the final capture-evidence integrity and
mixed-marker strictness defects: report the actual captured user-item location
rather than a hardcoded canonical location, keep provider-request fixture bytes
free of provenance-only fields, and ensure any malformed/duplicate supported
project marker invalidates the captured root instead of returning one incomplete
root. Preserve all accepted objective-000/001 behavior and exclusions.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`
- Numeric objective / round: `001` / `001-f`
- PR mode: `AMEND_EXISTING_PR`
- Existing PR: #2, `https://github.com/ulfe-lmi/slaif-local-coding/pull/2`
- Required base: `main` at
  `91463ae3199dd06e0448a9422a5e713da8ee92df`
- Required head: `oap/001-agents-observation-manifest`
- Current verified remote head:
  `f77e9c8307b4556c971caf4c44b5d2c0e04ee5b1`
- Prior implementation SHA:
  `dc7feb66d5f65c8d002eb5515ec31eec4d2fc410`
- Prior report SELF:
  `f77e9c8307b4556c971caf4c44b5d2c0e04ee5b1`; sole parent is literal
  implementation SHA and only changed path is immutable `001-e` report
- PR state: OPEN, non-draft, correct base/head/title, mergeable/clean; current
  report-head `CI` / `test` SUCCESS
- Required action: **NO NEW PR**; no coding merge/auto-merge.

Reconcile GitHub and preserve every prior order/report byte.

## Independently reproduced gaps

Current head produces:

```text
one valid supported user project block + second malformed supported marker
  -> roots=1, complete=false, parsing_error
  required -> roots=0, complete=false, parsing_error

helper raw marker at $.input[1].content[0].text
  -> sanitized facts report $.input[0].content[0].text
  required -> facts distinguish actual location from canonical output location

canonical project fixture top-level keys
  -> input, model, sanitized_provenance
  required -> provider-payload fixture contains only model and input;
     safe provenance lives separately
```

The hardcoded fact can make reports falsely claim a real captured index. The
extra provenance field was not in the provider request and violates the ordered
minimal fixture allowlist. A malformed second marker must prevent a unique
captured root, not coexist with one.

## A. Truthful actual versus canonical capture facts

- `minimize_with_facts` must retain the actual sanitized marker JSON path derived
  from the raw request (for example `$.input[1].content[0].text`) in a clearly
  named `actual_user_marker_location` fact.
- If canonical minimized output intentionally normalizes the sole item to input
  index 0, report a separate fixed `canonical_user_marker_location`; never
  substitute it for actual evidence.
- Preserve actual role/type, marker count, optional-instructions corroboration,
  content byte length/hash equality, endpoint completion, and canonical output
  digest as safe facts. Do not expose raw strings/paths/internal content.
- Add helper tests with valid markers at several input/content indexes proving
  actual facts are exact, canonical fixture bytes remain identical, and no index
  is hardcoded as empirical evidence.
- Rerun three fresh disposable Codex 0.149.0 captures. Report each actual safe
  structural path/role/type and optional corroboration separately; require their
  canonical model/input fixture bytes to remain byte-identical. Do not claim the
  actual index is stable unless the three facts prove it.

## B. Provider fixture versus provenance separation

- `project_instructions_responses.json` must contain only fields that represent
  the minimized provider request needed by detector tests: synthetic `model` and
  canonical `input` user/`input_text` envelope. Remove `sanitized_provenance` and
  every helper-only fact from that payload.
- Store safe synthetic provenance in the fixture README or a clearly separate
  non-request provenance file never passed to `observe_request`/live upstream.
  Document its schema and synthetic-only values.
- Tests must assert the canonical request fixture top-level key set is exactly
  `{model,input}`, contains no auth/IDs/tools/metadata/provenance/internal prompt,
  and still detects one exact root/hash/candidate manifest.
- Helper canonical output must match this request-only fixture. Facts are returned/
  printed separately and cannot alter fixture bytes.

## C. Unique-valid-marker strictness

- In the captured user-envelope detector, if any marker-bearing item in a
  supported top-level user/`input_text` position is malformed, duplicated,
  unsafe, or unsupported, return no project root and fixed incomplete reason—even
  when exactly one other valid item exists.
- Likewise, a duplicate/malformed parseable top-level instructions corroboration
  must invalidate/no-root according to the `001-e` contract.
- Do not let malformed markers in assistant/tool/metadata/arbitrary unsupported
  positions poison or establish a valid captured user root; parent context still
  matters.
- Add exact tests for valid+malformed, valid+unsafe, valid+duplicate, valid plus
  unsupported-position marker, malformed-only, and one-valid-only. Assert roots,
  completeness/reasons, exact byte forwarding, safe metrics, and one upstream
  request.
- Preserve plain mention/quote behavior, optional matching corroboration, exact
  hashing/tail exclusion, safe paths, input-file/tool supplements, extraction/
  spans/budgets, and all earlier false-positive tests.

## D. Cumulative evidence

Run and report:

```bash
uv lock --check
uv sync --frozen --extra dev
uv run --frozen ruff check .
uv run --frozen ruff format --check .
uv run --frozen mypy src tests
uv run --frozen pytest -q
SLAIF_LIVE_TEST=1 uv run --frozen pytest -q tests/test_live.py
uv build
python3 -m compileall -q src tests oap/bin
bash -n oap/bin/*.sh
git diff --check 91463ae3199dd06e0448a9422a5e713da8ee92df...HEAD
```

Required non-CI proof:

- three fresh captures pass; actual locations truthfully reported; canonical
  request-only fixture bytes identical;
- full foreground live matrix passes;
- canonical valid and matching-corroboration variants yield expected root/
  candidate deltas;
- valid+malformed/unsafe/duplicate, malformed-only, instructions-only, mismatch,
  plain mention, wrong role variants yield zero project-root delta and exactly
  one unchanged upstream request;
- candidate/capture processes stopped.

No long-session/compaction/compiler/cache/injection claim.

## E. Scope and safety

Change only detector strictness, capture helper/facts, primary fixture/provenance,
tests, necessary docs/metrics status, and OAP transcript. No compiler/model call,
ranking/confidence/priority, cache/persistence, acquisition, injection, cross-
request state, client filesystem/external fetch, gateway, public auth/TLS,
deployment, cutover, active profile switch, unrelated dependency/refactor, or
protected permission remediation.

Never commit/log/report raw capture, internal prompts/instructions, real source/
paths/tool output/body/images, IDs, auth/cookies/keys/private URLs/session/account/
environment data. Synthetic values and sanitized structural facts only.

No change/stop/restart to protected Qwen/vLLM/systemd/key/network/Codex profile/
OAP wrapper state. Candidate remains CPU-only/loopback 18031 and is stopped.
Preserve mode-0777 vision env byte-for-byte and these hashes:

- vision env `affabb5701b67b5fcb7cab2e3ae1835e84e19dc98a7f1eb245cf3e49b76b3b5b`
- vision unit `fc88870b4f4afee214c25dc9ec544c4178c300bf4d78092a4d12787a955e2e94`
- vision start script `8c87e0104b25c9600235a97555c4b0a1d0ea55d34ccb4094af428c8b4501f89f`
- Qwen profile `18ead58ac440d29ce2e86addf855c24f471021c6050d4da685320a2cf6eb62eb`
- coding overlay `cc243c7057f00cb15a06a5be63c6d811f8f473e367d521b1b6ea6207c794509a`
- OAP runtime env `22fdefd324d631353f1b9fedad3bad1fc75577073794a882ce2dd57bc5794bf1`

Verify PID/start/command/listeners/hashes before/after; only 18020 listens at
report time.

## F. Same-PR publication

1. Amend only PR #2 / `oap/001-agents-observation-manifest`; **NO NEW PR**,
   no merge/auto-merge.
2. Preserve prior orders/reports. Commit exact `001-f` order and active selector
   unchanged with remediation.
3. Push all non-report work, inspect/fix CI, capture final literal implementation
   SHA after every non-report change is remote.
4. Atomically publish exactly:

```text
oap/reports/001-f-fix-capture-evidence-integrity.md
```

5. Report literal implementation SHA plus `Report publication commit: SELF`;
   remote SELF changes only report, first parent is literal SHA, and it is PR
   head before `OK`.
6. Report three actual/canonical locations honestly, fixture/provenance separation,
   mixed-marker zero-root evidence, cumulative tests/live/checks, protected state/
   hashes, limitations, and explicit `extra PR NO`, `coding merge NO`,
   `auto-merge NO`, `protected change NO`. No later mutation/push before signal.

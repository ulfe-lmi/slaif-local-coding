# OAP Work Order — 001-d

## Objective

Amend objective-001 PR #2 only. Resolve the `001-c` partial result by replacing
the unreproduced developer-item capture provenance with a safely minimized,
freshly reproducible Codex CLI 0.149.0 fixture and a narrow detector rule for the
actual observed provider-bound structure: a project marker in top-level
`instructions` corroborated by the corresponding top-level user `input_text`
item. Preserve strict false-positive resistance, exact source hashing,
deterministic candidate extraction, all bounds/privacy/compatibility behavior,
and every explicit later-objective exclusion.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`
- Numeric objective / round: `001` / `001-d`
- PR mode: `AMEND_EXISTING_PR`
- Existing PR: #2, `https://github.com/ulfe-lmi/slaif-local-coding/pull/2`
- Required base: `main` at
  `91463ae3199dd06e0448a9422a5e713da8ee92df`
- Required head branch: `oap/001-agents-observation-manifest`
- Current verified remote head:
  `434c97a3b5475606ed2d4fb3d85a6038afbd1fcf`
- Prior implementation SHA:
  `ddbc096c212ada5e58df2d71ad34ddc2a5a37c3c`
- Prior report SELF:
  `434c97a3b5475606ed2d4fb3d85a6038afbd1fcf`; sole parent is the literal
  implementation SHA and only changed path is the immutable `001-c` report
- Prior report status: `PARTIAL` because fresh capture did not reproduce the
  claimed developer parent/role
- PR state: OPEN, non-draft, correct base/head/title, mergeable/clean; current
  report-head workflow `CI` / `test` SUCCESS
- Required action: **NO NEW PR**. Amend PR #2 only; no coding merge/auto-merge.

Reconcile GitHub before mutation. Preserve all prior orders/reports exactly;
later evidence must explicitly correct, never rewrite, the historical `001-a`
developer-capture claim.

## Strategic decision from empirical evidence

The architecture explicitly lists the exact current Codex effective-AGENTS wire
marker as an empirical question. The safe `001-c` disposable capture established:

```text
Codex CLI: 0.149.0
custom provider request reached loopback fake Responses endpoint: YES
project marker in claimed developer item: NO
project marker in top-level instructions: YES
project marker in top-level user/input_text item: YES
helper rewrote role or emitted false-equivalent fixture: NO
```

Strategy therefore rejects the unreproduced developer-item shape as the primary
captured contract. The current actual positions may become the captured evidence
class only after a new minimizer proves their exact safe relationship. Do not
simply allow arbitrary top-level instructions or user text independently.

## A. Capture and minimize the actual structure safely

Extend the executable disposable helper to derive a sanitized structural fixture
from the fresh current capture without writing/printing the raw provider request.

The helper must, in memory:

1. locate every string containing the unique synthetic project marker/sentinel;
2. record only safe structural facts: JSON field path, parent role, item type,
   occurrence count, extracted logical project label after privacy mapping,
   exact synthetic instruction-content byte length/hash, and whether occurrences
   agree; do not expose unrelated string content;
3. require exactly the documented top-level `instructions` occurrence and one
   top-level `input` user/`input_text` occurrence, or fail closed with a sanitized
   structural reason;
4. extract the uniquely delimited synthetic project block/content from each and
   prove logical path and exact content hash/length agree before emitting;
5. replace the random disposable absolute repository directory only with a fixed
   documented synthetic logical label while preserving the exact synthetic inner
   instruction bytes used for detector/hash tests;
6. discard authorization/headers, internal prompts/instructions outside the
   project block, unrelated tools/items, user request/tail/environment content,
   IDs, loopback/host paths, session/account values, and response data;
7. emit a deterministic minimal fixture containing only the synthetic model and
   the two actual structural evidence positions needed by the detector, with
   clearly synthetic safe prefix/suffix placeholders if surrounding-position
   behavior must be represented.

Run the helper in a new disposable home/repository/endpoint and require it to
write a fixture structurally equivalent to the committed actual-shape fixture.
Record only sanitized counts/roles/types/hash-equality/status in the report. No
raw capture or internal prompt may enter files, stdout/stderr, report, Git, or CI.

Rename/rewrite fixture/provenance descriptions so:

- the current top-level-instructions + user-input pair is the one captured Codex
  0.149.0 shape;
- the former developer-item fixture is removed or explicitly relabeled a
  synthetic supplemental shape with no capture provenance claim;
- input-file/tool fixtures remain synthetic supplements;
- historical `001-a`/`001-c` reports remain immutable and the new report states
  the correction plainly.

CI consumes only sanitized committed fixtures/helper unit tests and still needs
no Codex binary, login, network, or secret.

## B. Narrow corroborated current-Codex detector rule

Implement only the exact rule supported by the sanitized capture:

- inspect the top-level `instructions` field and the exact top-level `input`
  user/`input_text` location observed by the helper;
- locate a uniquely delimited effective `AGENTS.md` project block in each using a
  documented, bounded, non-recursive parser;
- require exactly one supported occurrence in each position;
- require the same privacy-safe logical AGENTS label and exact observed inner
  instruction UTF-8 hash/byte length in both positions;
- create one root with both evidence locations/types retained deterministically;
- hash/enumerate exact inner instruction content, not internal instructions,
  user request/environment tail, envelope delimiters, or sanitized fixture
  placeholders.

Fail/no-detect or fixed-incomplete—never guess—when:

- only top-level instructions or only user input contains a marker;
- content/path hashes differ;
- either position has duplicates, nested/arbitrary parent, assistant/tool/
  developer-supplemental-only marker, wrong role/type, unsupported suffix/prefix,
  malformed/ambiguous delimiters, or unsafe logical path;
- user prose merely quotes/mentions `AGENTS.md`;
- top-level instructions contains an unrelated documentation/example marker;
- the helper/detector cannot prove unique corroboration.

The actual user item may contain captured structural tail material after the
project block only if the sanitized fixture proves that exact boundary. Parse and
discard that tail according to a narrow structural delimiter rule; never include
it in the source hash/candidate manifest. Do not reintroduce the broad prefix
acceptance fixed in `001-c` for the old developer-item supplemental shape.

The old full-match developer synthetic variant may remain tested only if clearly
named/documented supplemental and it does not establish current capture
provenance. Prefer removing unsupported surface if it adds no needed compatibility.

## C. Exact tests and evidence

Add CI-running tests for:

```text
fresh minimized actual Codex 0.149.0 fixture detects one root
root contains both stable evidence locations and exact synthetic hash/length
top-level instructions only -> no root
user/input_text only -> no root
mismatched content/path hash -> no root/incomplete fixed reason
duplicate occurrence in either position -> no root/incomplete
assistant/tool/developer supplemental/arbitrary nested/metadata markers -> no actual pair
plain mention/quote and unrelated internal-instructions example -> no root
captured allowed user tail boundary accepted but excluded from hash/candidates
unproved prefix/suffix/two envelopes/malformed delimiter -> no root
unsafe absolute/traversal/URL/encoded logical labels remain privacy-safe reject
LF/CRLF/trailing whitespace/Unicode exact inner-content hash contract
multiple separate valid paired roots deterministic and bounded if captured policy supports them
all 001-b tool/input-file/path/candidate/span/evidence-budget tests green
route-enabled/disabled byte identity, safe metrics, fallback exactly one upstream
all objective-000 image/proxy/SSE/tool/error/body/depth/live regressions green
```

Tests for the helper/minimizer must use only synthetic raw-like payloads and assert
it rejects relocated/missing/duplicate/mismatched markers and never emits unrelated
fields. A changed detector cannot be accepted merely because the old fixture still
passes.

## D. Documentation and honest claims

Correct README, adapter docs, and fixture provenance to describe:

- exact captured 0.149.0 two-position corroboration and minimization;
- which surrounding material is structurally observed but discarded;
- exact source-content hashing and safe logical-path treatment;
- old developer shape's synthetic-only/removal status and immutable historical
  report correction;
- conservative failure for future/unsupported versions;
- observation-only/request-only scope and absence of compiler/ranking/cache/
  acquisition/injection/rehydration/multi-user production behavior.

Do not claim universal Codex wire compatibility or actual long-session behavior.

## E. Cumulative verification

Run and report at least:

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

Required non-CI evidence:

- fresh disposable Codex 0.149.0 helper run: PASSED and fixture-equivalent;
- bounded foreground candidate full accepted live matrix: PASSED;
- actual-shape synthetic pair through candidate: HTTP 200, exactly +1 root and
  expected candidate count;
- instructions-only, user-only, mismatch, and duplicate variants: HTTP 200 with
  zero root/candidate deltas and exactly one unchanged upstream request;
- candidate/capture servers stopped afterward.

If fresh capture varies again or cannot prove the pair, publish `PARTIAL|BLOCKED`
without broadening detection or fabricating equivalence; strategy will review.

## F. Scope, security, privacy, and protected host

Change only capture/minimization fixture/helper, project detector/contracts,
tests, necessary docs/metrics status, and OAP transcript. No model compiler/call,
semantic ranking/confidence/priority/P0–P4 rules, cache/persistence, dependency
acquisition, injection/replacement, cross-request state, client filesystem or
external network/Git/GitHub lookup, gateway, public auth/TLS, deployment, cutover,
profile switch, unrelated dependencies/refactors, or protected permission fix.

Never commit/log/report raw capture, real prompts/internal instructions/source/
paths/tool output/body/images, hashes, IDs, auth/cookies/keys/private URLs/session/
account data. Synthetic fixture values and sanitized structural facts only.
Runtime remains CPU-only, bounded, loopback-only, route-scoped, ephemeral, and
semantics-preserving.

Absolutely no change/stop/restart to `qwen-serving-vision.service`, inactive
`qwen-serving.service`, PID/port 18020, Qwen checkout/venv/model/checkpoint/
patches/launch flags, systemd units, key file, firewall/VPN/network, active Codex
profile/login/catalog/session/compaction, or OAP wrapper. Preserve known mode-0777
vision env byte-for-byte.

Required unchanged hashes:

- vision env `affabb5701b67b5fcb7cab2e3ae1835e84e19dc98a7f1eb245cf3e49b76b3b5b`
- vision unit `fc88870b4f4afee214c25dc9ec544c4178c300bf4d78092a4d12787a955e2e94`
- vision start script `8c87e0104b25c9600235a97555c4b0a1d0ea55d34ccb4094af428c8b4501f89f`
- Qwen profile `18ead58ac440d29ce2e86addf855c24f471021c6050d4da685320a2cf6eb62eb`
- coding overlay `cc243c7057f00cb15a06a5be63c6d811f8f473e367d521b1b6ea6207c794509a`
- OAP runtime env `22fdefd324d631353f1b9fedad3bad1fc75577073794a882ce2dd57bc5794bf1`

Verify before/after PID/start time/command/listeners/hashes. At report time only
protected 18020 listens; 18021/18031 are free.

## G. Local execution authority

Coding owns safe repo-local helper/minimizer/tests, disposable synthetic Codex
home/repository/catalog, temporary loopback endpoint, candidate, bounded live
calls, GitHub publication, and CI diagnosis. Do not recruit human/strategy for
routine execution.

## H. Same-PR publication and immutable report

1. Amend only PR #2 / `oap/001-agents-observation-manifest`; **NO NEW PR**,
   no merge, no auto-merge.
2. Preserve all prior orders/reports. Commit exact `001-d` order and active
   selector unchanged with remediation.
3. Push all non-report work, inspect/fix same-PR CI, and capture final literal
   implementation SHA after every non-report change is remote.
4. Atomically publish exactly:

```text
oap/reports/001-d-align-detector-with-current-codex-capture.md
```

5. Report `Implementation head SHA: <literal 40-hex>` and
   `Report publication commit: SELF`; remote SELF changes only this report, first
   parent is literal implementation SHA, and it is current PR head before `OK`.
6. Report sanitized capture structure/counts/equality, fixture correction,
   detector pairing/failure rules, every criterion/test/live result, current
   checks, protected state/hashes, limitations, and explicit `extra PR NO`,
   `coding merge NO`, `auto-merge NO`, `protected change NO`. Make no later
   mutation/push before signaling.

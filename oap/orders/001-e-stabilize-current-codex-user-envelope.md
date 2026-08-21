# OAP Work Order — 001-e

## Objective

Amend objective-001 PR #2 only. Complete empirical Codex 0.149.0 envelope
support using the stable minimum observed in both safe disposable captures: one
top-level `input` item with role `user`, one `input_text` content item, and one
uniquely delimited effective `AGENTS.md` project block. Treat a matching
top-level `instructions` project block as optional corroboration because it
appeared in one capture and was absent in the next. Require three fresh runs to
normalize to the same safe user-envelope fixture before acceptance.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`
- Numeric objective / round: `001` / `001-e`
- PR mode: `AMEND_EXISTING_PR`
- Existing PR: #2, `https://github.com/ulfe-lmi/slaif-local-coding/pull/2`
- Required base: `main` at
  `91463ae3199dd06e0448a9422a5e713da8ee92df`
- Required head branch: `oap/001-agents-observation-manifest`
- Current verified remote head:
  `2233fedc914eda7de5490c3f3dc2b4b604a5d04c`
- Prior implementation SHA:
  `64339aec47a4e91986d8827c3c7da39d8fe06855`
- Prior report SELF:
  `2233fedc914eda7de5490c3f3dc2b4b604a5d04c`; sole parent is literal
  implementation SHA and only changed path is immutable `001-d` report
- Prior report status: `PARTIAL`; it intentionally did not add an unreproduced
  two-position rule
- PR state: OPEN, non-draft, correct base/head/title, mergeable/clean; current
  report-head `CI` / `test` SUCCESS
- Required action: **NO NEW PR**. Amend PR #2 only; no coding merge/auto-merge.

Reconcile GitHub before mutation and preserve every prior order/report byte.

## Empirical basis and strategic rule

Two consecutive safe Codex CLI 0.149.0 custom-provider captures established:

```text
capture c: user/input_text project marker YES; top-level instructions marker YES
capture d: user/input_text project marker YES; top-level instructions marker NO
developer project item in either fresh capture: NO
```

The stable current-Codex evidence is therefore the exact user/input_text project
envelope. Top-level instructions is optional corroboration, not a prerequisite.
This is not arbitrary user prose detection: parent, role, item type, marker,
logical path, delimiters, uniqueness, and allowed captured tail are all required.

## A. Normalize three fresh captures to one safe fixture

Modify the disposable helper/minimizer to accept only:

- exactly one project marker in a supported top-level `input` user/`input_text`
  item;
- zero or one parseable project-block occurrence in top-level `instructions`;
- if instructions occurrence exists, exact logical-label/content hash/length
  agreement with the user occurrence;
- no marker in any other path/role/type and no duplicate user/instructions
  occurrence;
- the exact captured user suffix grammar: no suffix/terminal newline or the one
  bounded `<environment_context>...</environment_context>` structural tail
  already observed. Environment/tail bytes are discarded, not hashed.

Fail closed on missing user marker, duplicate/relocated marker, unsafe path,
mismatched optional corroboration, malformed delimiter, or unsupported tail.

Emit one deterministic minimized fixture containing only:

```text
synthetic model
one top-level user/input_text item
privacy-mapped synthetic logical project label
exact synthetic inner AGENTS instruction bytes
safe synthetic environment-tail placeholder only if needed to test structure
```

Do not include optional top-level instructions in the canonical minimized fixture;
the user shape is the stable minimum. The helper may return a separate in-memory/
sanitized run fact `instructions_corroborated=true|false`, but that fact must not
make otherwise equivalent fixture bytes differ. Never write/print raw request,
internal instructions, host path, IDs, tools, other input, user prompt, environment
content, auth, headers, or response.

Run the helper three times in three new temporary homes/repositories/endpoints.
All three must:

- reach and complete the fake Responses endpoint;
- find exactly one supported user marker;
- produce byte-identical canonical minimized fixture output after privacy mapping;
- report only safe structural position/role/type, optional-corroboration boolean,
  content length/hash equality, and success;
- leave no raw capture or temporary persistent state.

Replace/rename the committed primary captured fixture with this canonical actual
user-envelope shape. Relabel/remove the old developer fixture as synthetic-only;
input-file/tool fixtures remain synthetic supplements. Update provenance to
correct the historical immutable claims without editing old reports.

If any of the three runs lacks or relocates the user marker or canonical outputs
differ, publish `PARTIAL|BLOCKED`; do not broaden the rule.

## B. Exact current user-envelope detector

Add a dedicated bounded parser/walker for the captured primary evidence:

- inspect only the exact top-level Responses `input` user/`input_text` position;
- require one uniquely delimited project block beginning at the captured boundary;
- require exact `# AGENTS.md instructions for <label>`, blank-line,
  `<INSTRUCTIONS>`, inner content, and closing delimiter grammar;
- allow only the helper-proven terminal newline/environment-context tail;
- validate/privacy-map the logical label with the shared safe AGENTS path policy;
- hash and enumerate only exact inner instruction UTF-8 bytes;
- retain the user item location as project evidence.

Top-level `instructions` behavior:

- absence or no project block does not invalidate the user root;
- exactly one parseable project block may add corroborating evidence only if its
  safe logical label and exact inner content hash/length match;
- a parseable duplicate or mismatched project block marks fixed incomplete/no-
  detection; it must not override the user source;
- an arbitrary mention/example that is not the exact block grammar is ignored and
  does not establish or invalidate a root.

False-positive requirements:

- user plain mention, quote, partial marker, wrong role/type/parent, nested/
  metadata/assistant/tool/developer-supplemental-only marker, malformed/duplicate
  block, unsafe label, and unsupported tail do not establish the captured root;
- a manually constructed exact supported user envelope is intentionally evidence
  because it is semantically the same client-supplied effective-governance form,
  not arbitrary prose. Document this trust boundary honestly.

The old full-match developer shape may remain only as clearly synthetic
supplemental evidence if strategically useful; it cannot be described as current
captured Codex behavior. Prefer removing it if unnecessary.

## C. Exact tests

CI-running tests must prove:

```text
canonical fresh user-envelope fixture -> one root
exact inner content hash/length/candidates and stable evidence location
three-run minimizer normalization with optional instructions present/absent
user-only captured shape accepted
user + matching instructions accepted with corroborating evidence
instructions only rejected
user + mismatched/duplicate instructions incomplete/no root
duplicate/relocated/missing user marker rejected by minimizer/detector
plain mention/quote/partial/wrong role/type/parent/nested/assistant/tool rejected
captured environment tail allowed but excluded from source hash/candidates
arbitrary suffix/prefix/two blocks/malformed delimiters rejected
unsafe logical path classes rejected/privacy-safe
LF/CRLF/trailing whitespace/Unicode exact inner hash contract
old developer fixture synthetic-only/removal status tested/documented
all input-file/tool/reference/path/span/budget/identity/fallback tests green
route enabled/disabled request bytes and exactly one upstream call unchanged
all objective-000 proxy/image/SSE/tool/error/body/depth/live tests green
```

Helper tests use synthetic raw-like payloads only and assert output allowlisting;
CI does not invoke Codex or need login/network/secrets.

## D. Live and cumulative verification

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

- three fresh disposable Codex 0.149.0 captures: all PASSED and canonical fixture
  bytes equivalent; optional instructions presence reported safely per run;
- foreground candidate full accepted live matrix: PASSED;
- canonical user-only request: HTTP 200, root +1, expected candidate delta;
- matching optional-instructions variant: HTTP 200, one root with safe count delta;
- instructions-only, mismatch, duplicate, plain mention, and wrong-role variants:
  HTTP 200, zero root/candidate delta, exactly one unchanged upstream request;
- candidate/capture servers stopped afterward.

No actual compaction/long-session compliance or semantic-governance claim.

## E. Documentation and scope

Correct fixture provenance, README, and adapter docs with:

- the stable captured user/input_text primary evidence and three-run result;
- optional instructions corroboration variability;
- exact delimiter/tail/hash/path contract and client-supplied trust boundary;
- developer/input-file/tool synthetic supplement labels;
- immutable historical claim correction;
- conservative future-version failure;
- observation-only/request-only scope with no compiler/ranking/cache/acquisition/
  injection/rehydration/multi-user production behavior.

Only capture helper/minimizer/fixture, detector/models if needed, tests, docs/
metrics statuses, and OAP transcript may change. No model compiler/call, semantic
ranking/confidence/priority/P0–P4, cache/persistence, acquisition, injection/
replacement, cross-request state, client filesystem or external fetch/Git/GitHub,
gateway, public auth/TLS, deployment, cutover, profile switch, unrelated dependency/
refactor, or protected permission remediation.

## F. Security, privacy, and protected host

Never commit/log/report raw capture, real internal instructions/prompts/source/
paths/tool output/body/images, IDs, hashes, auth/cookies/keys/private URLs/session/
account/environment data. Synthetic fixture values and sanitized structural facts
only. Runtime stays CPU-only, bounded, route-scoped, ephemeral, semantics-
preserving, and loopback-only on 18031 for tests.

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

## G. Local authority and report

Coding owns safe repo-local helper/minimizer/tests, three disposable synthetic
Codex homes/repositories/catalogs, temporary loopback endpoints, foreground
candidate, bounded live calls, commits/push, and CI diagnosis. Do not recruit
human/strategy for routine execution.

Publication:

1. Amend only PR #2 / `oap/001-agents-observation-manifest`; **NO NEW PR**,
   no merge, no auto-merge.
2. Preserve all prior orders/reports. Commit exact `001-e` order and active
   selector unchanged with remediation.
3. Push all non-report work, inspect/fix same-PR CI, capture final literal
   implementation SHA after every non-report change is remote.
4. Atomically publish exactly:

```text
oap/reports/001-e-stabilize-current-codex-user-envelope.md
```

5. Report literal implementation SHA plus `Report publication commit: SELF`;
   remote SELF changes only this report, first parent is literal implementation
   SHA, and it is PR head before `OK`.
6. Report sanitized three-run structural facts/optional corroboration, canonical
   fixture correction, detector rules, all tests/live/checks, protected state/
   hashes, limitations, and explicit `extra PR NO`, `coding merge NO`,
   `auto-merge NO`, `protected change NO`. No later mutation/push before signal.

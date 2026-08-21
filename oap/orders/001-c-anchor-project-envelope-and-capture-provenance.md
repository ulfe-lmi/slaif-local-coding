# OAP Work Order — 001-c

## Objective

Amend objective-001 PR #2 only. Make captured Codex project-instruction
detection require the complete supported envelope—not merely a valid prefix—and
make the sanitized fixture refresh procedure genuinely reproducible with a
fully specified temporary custom-provider/fake-Responses skeleton. Preserve all
accepted `001-a`/`001-b` detector, extractor, bounds, privacy, compatibility,
and protected-host behavior.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`
- Numeric objective / round: `001` / `001-c`
- PR mode: `AMEND_EXISTING_PR`
- Existing PR: #2, `https://github.com/ulfe-lmi/slaif-local-coding/pull/2`
- Required base: `main` at
  `91463ae3199dd06e0448a9422a5e713da8ee92df`
- Required head branch: `oap/001-agents-observation-manifest`
- Current verified remote head:
  `d12d51dabaa17192a62c99994daa4ea8f2724688`
- Prior implementation SHA:
  `71b59c72c9ee39d952bda8a0a8181f5bb2f68861`
- Prior report SELF:
  `d12d51dabaa17192a62c99994daa4ea8f2724688`; sole parent is the literal
  implementation SHA and only changed path is the immutable `001-b` report
- PR state at review: OPEN, non-draft, correct base/head/title,
  mergeable/clean; current report-head `CI` / `test` SUCCESS
- Required action: **NO NEW PR**. Amend PR #2 only; no coding merge/auto-merge.

Reconcile GitHub before mutation and preserve every prior order/report byte.

## Independently reproduced final detection gap

Against current PR head, this supported-position developer item incorrectly
produces one root:

```text
# AGENTS.md instructions for repo

<INSTRUCTIONS>
MUST read SAFE.md
</INSTRUCTIONS>
ordinary extra text
```

The project regex uses a start anchor and permits a newline after the closing
tag without requiring end-of-string, so a valid prefix plus unrelated suffix is
accepted. The `001-b` order requires a full anchored marker/envelope and rejects
ordinary content around it. The safely captured fixture itself still detects.

## A. Complete-envelope contract

- Parse the supported Codex 0.149.0 project-instruction item with a true complete
  match. Allow only the documented envelope and an explicitly documented terminal
  newline policy; no non-whitespace prefix/suffix, second envelope, user text,
  metadata-like tail, or bytes after the closing delimiter may be ignored.
- Define exactly which delimiter newline belongs to the envelope versus exact
  observed instruction content. Preserve current exact UTF-8 hashing semantics:
  LF/CRLF/content trailing whitespace/Unicode differences remain distinct and
  no line-ending or content normalization occurs.
- Do not weaken the `001-b` parent/role/item/path rules. Identical complete text
  under assistant/tool/user/metadata or wrong item type remains no-detect.
- Unsupported/extra-text shapes no-detect rather than hashing a prefix. The main
  request remains byte-identical and forwards exactly once with safe bounded
  observation status.

Add exact tests for:

```text
captured fixture exact envelope accepted
accepted terminal LF and CRLF policy
non-whitespace prefix rejected
same-line and next-line suffix rejected
extra blank line plus suffix rejected
two concatenated envelopes rejected
missing/mismatched/open closing tag rejected
closing-tag text inside instruction content handled deterministically/no prefix match
content LF/CRLF/trailing newline/whitespace/Unicode hash and byte-length contract
all 001-b role/type/path false-positive regressions remain green
```

## B. Reproducible safe capture provenance

The current provenance skeleton names a temporary provider and base URL but omits
the custom provider's required wire API, credential environment mapping, selected
synthetic model, and exact stream/non-stream fake response behavior. Correct it
so another operator can reproduce the capture without guessing or modifying an
active profile.

- Document the exact non-secret temporary configuration/CLI skeleton used for
  Codex 0.149.0, including model, custom provider name, `base_url`,
  `wire_api="responses"`, throwaway `env_key`, and every required flag such as
  `--ephemeral`, `--ignore-user-config`, and disposable repository working path.
- Prefer a temporary `CODEX_HOME` configuration example or fully quoted `-c`
  overrides that are known to parse. Do not write to the real Codex home/profile,
  login, catalog, sessions, or compaction settings.
- Specify the minimal loopback fake endpoint request capture and response
  behavior actually required by the CLI, including whether the request asks for
  streaming and the exact safe terminal SSE/Responses event class or JSON form
  used to let the disposable command end. Use placeholders, synthetic IDs/model,
  and a throwaway key value only—never a real credential or captured raw body.
- Document the in-memory minimization allowlist: retain only the synthetic
  developer/`input_text` project item and necessary synthetic model/envelope
  structure; discard auth, headers, IDs, host path, internal prompts, unrelated
  tools/items, user/session/account values, and response content before writing.
- Validate the documented procedure by rerunning it once in a new disposable
  directory/temporary loopback endpoint, or provide a small repo test helper that
  makes the exact safe skeleton executable. Report sanitized version/status and
  fixture-equivalent structural facts only. CI must still require no Codex binary,
  login, network, or secret.
- Continue clearly labeling input-file/tool fixtures as synthetic supplements,
  not captured provider shapes or universal compatibility.

## C. Cumulative verification

Run all objective-001 adversarial/boundary/fixture tests plus every accepted
objective-000 regression. In particular, rerun the exact strategic suffix
reproducer and all `001-b` assistant/wrong-type/wrong-tool/traversal/sentence-
final/evidence-budget cases.

Required commands:

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

Rerun the bounded foreground candidate matrix and the exact captured synthetic
project-envelope HTTP 200/root+candidate metric delta. The extra-suffix variant
must forward with no root delta. Stop candidate/capture processes afterward.
No actual Codex long-session/compaction or semantic-governance claim.

## D. Scope, security, privacy, and protected host

Only project-envelope parsing/tests, fixture provenance/safe capture helper if
needed, necessary docs, and OAP transcript may change, plus directly required
small refactors. No compiler/model call/ranking/confidence/priority, cache/
persistence, acquisition, injection/replacement, cross-request state, client
filesystem/network/Git/GitHub lookup, gateway, public auth/TLS, deployment,
cutover, active profile switch, unrelated dependency/refactor, or protected
permission remediation.

Never commit/log/report real prompts/source/paths/tool output/bodies/images,
hashes, IDs, auth/cookies/keys/private URLs/session/account data or raw capture.
Synthetic fixture values only. Runtime observation remains ephemeral, CPU-only,
bounded, route-scoped, and semantics-preserving.

Absolutely no change/stop/restart to `qwen-serving-vision.service`, inactive
`qwen-serving.service`, PID/port 18020, Qwen checkout/venv/model/checkpoint/
patches/launch flags, systemd units, key file, firewall/VPN/network, active Codex
profile/login/catalog/session/compaction, or OAP wrapper. Preserve the known
mode-0777 vision env file byte-for-byte.

Required unchanged hashes:

- vision env `affabb5701b67b5fcb7cab2e3ae1835e84e19dc98a7f1eb245cf3e49b76b3b5b`
- vision unit `fc88870b4f4afee214c25dc9ec544c4178c300bf4d78092a4d12787a955e2e94`
- vision start script `8c87e0104b25c9600235a97555c4b0a1d0ea55d34ccb4094af428c8b4501f89f`
- Qwen profile `18ead58ac440d29ce2e86addf855c24f471021c6050d4da685320a2cf6eb62eb`
- coding overlay `cc243c7057f00cb15a06a5be63c6d811f8f473e367d521b1b6ea6207c794509a`
- OAP runtime env `22fdefd324d631353f1b9fedad3bad1fc75577073794a882ce2dd57bc5794bf1`

Verify before/after PID/start time/command/listeners and hashes. At report time
only protected 18020 listens; 18021/18031 are free.

## E. Local execution authority

Coding owns safe repo-local tests, disposable synthetic capture repository,
temporary loopback fake endpoint, foreground candidate, bounded live calls,
GitHub publication, and CI diagnosis. Do not recruit human/strategy for routine
execution.

## F. Same-PR publication and immutable report

1. Amend only PR #2 / `oap/001-agents-observation-manifest`; **NO NEW PR**,
   no merge, no auto-merge.
2. Preserve all prior orders/reports. Commit exact `001-c` order and updated
   `oap/active` unchanged with remediation.
3. Push all non-report work, inspect/fix same-PR CI, and capture the final literal
   implementation SHA after every non-report change is remote.
4. Atomically publish exactly:

```text
oap/reports/001-c-anchor-project-envelope-and-capture-provenance.md
```

5. Report `Implementation head SHA: <literal 40-hex>` and
   `Report publication commit: SELF`; remote SELF changes only this report, first
   parent is the literal implementation SHA, and it is current PR head before
   response `OK`.
6. Report exact envelope grammar/newline/hash behavior; suffix reproducer;
   capture command/provider/fake-response skeleton and sanitized rerun result;
   cumulative commands/counts/live evidence; current checks; protected hashes/
   state; limitations; and explicit `extra PR NO`, `coding merge NO`,
   `auto-merge NO`, `protected change NO`. Make no later mutation/push before
   signaling.

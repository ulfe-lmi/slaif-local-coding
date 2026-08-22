# OAP Work Order — 003-b

## Objective

Amend objective-003 PR #4 only to integrate the already merged compiler, cache,
working-set selector, and injection contracts into explicit adapter routes for
one complete observed root. The pipeline must run after image policy, preserve
original governance-bearing requests on compiler/cache/selection failure,
inject idempotently before upstream forwarding, and expose only safe metrics.
Do not implement file acquisition, tool-output ingestion, compaction rehydration,
gateway identity, or cutover.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`
- Numeric objective / round: `003` / `003-b`
- PR mode: `AMEND_EXISTING_PR`
- Existing PR: #4, `https://github.com/ulfe-lmi/slaif-local-coding/pull/4`
- Required base: `main`
- Verified base SHA: `867ed55e7d115d960c666380ebbc5952d43d97d1`
- Required head: `oap/003-working-set-injection-foundation`
- Current verified remote head / `003-a` report SELF:
  `a2c4cac4425acec04263ae99d34af9ce5371c653`
- Prior implementation SHA:
  `47dae670e94afa700aa5fa0f416e28e595cdb91d`, verified sole first parent of
  report SELF
- Report commit changes only immutable
  `oap/reports/003-a-working-set-and-injection-contracts.md`; remote/local blob
  SHA is `435abcf0232cc02c6bcbab787c9df21e9b191e52`
- PR state: OPEN, non-draft, correct base/head, MERGEABLE/CLEAN; current-head
  `CI` / `test` SUCCESS
- Required action: **NO NEW PR**; no coding merge/auto-merge.

Preserve every prior order/report byte and reconcile remote state before mutation.

## Independently verified current state

Remote objective `003-a` is merged into authoritative main:

```text
PR #4: MERGED
main merge commit: 68f212b5ad316b95fa12ef632e1538b56479081b
main parents: 867ed55... / a2c4cac...
main tree equals accepted PR head tree: yes
open objective PRs: none at post-merge reconnaissance
```

Live host facts verified read-only immediately before activation:

```text
host/user: hinton1 / janezp
vLLM PID: 26028 on 0.0.0.0:18020
user qwen-serving.service: active/running; same PID/start time
qwen-serving-vision.service: inactive/dead
ports 18021/18031: free
preferred upstream: http://127.0.0.1:18020/v1
current model capability: text-only / zero-image
```

The coding-loop wrapper prompt still contains generic historical “vision service”
wording. That wrapper text is outside this repository and must not be changed by
coding; repository docs remain governed by the verified text-only facts.

## Bounded scope

### A. Explicit route-level enablement and local single-user identity

Extend validated configuration without changing defaults:

- global `[constitution] enabled` may become boolean, but default remains false;
- each route gains explicit `constitution_enabled = false` by default;
- integration requires both global and route enablement;
- when global integration is enabled, require explicit nonempty configured
  `principal`, `session`, and `repository` identity fields;
- these are static local-appliance identifiers for the private single-user MVP;
  never derive them from caller headers, body, model, or source content;
- retain stripping of all client-supplied SLAIF/internal identity headers;
- document that signed multi-user gateway identity remains future work and this
  configuration must not be represented as multi-user production safety.

Validate finite bounds for cache/compiler/selector/injection as already defined;
fail startup on invalid policy, missing identity, or unsafe combination.

### B. Request-only observation source handoff

Add an in-memory, request-scoped way to obtain exact source bytes corresponding
to complete observation roots. Do not persist raw source or add it to serialized
observation models/logs. Preserve hash validation and existing detector behavior.

For this round, process only when after-image-policy observation yields exactly
one complete root. Zero roots and multiple/incomplete roots remain semantically
unchanged with an explicit safe metric reason. Use that root’s exact bytes,
logical path/hash, deterministic candidates, and validated metadata for optional
compilation.

### C. Pipeline ordering and semantics

For an explicitly enabled route, after JSON bounds/route selection/image policy:

1. observe exactly one complete root and obtain its in-memory bytes;
2. use direct non-recursive compiler settings constructed from validated config;
3. use the hardened derived cache with configured static identity;
4. compile/cache as implemented, including one-slot scheduling and deduplication;
5. select one bounded working set from the compiled root (no acquired dependency
   indexes exist yet);
6. inject using the endpoint-specific idempotent transform;
7. serialize deterministically and forward the transformed JSON body while
   preserving streaming choice, tools, usage fields, unrelated envelope values,
   and image policy results;
8. release resources and record bounded metrics.

Failure separation is mandatory:

- compiler timeout/status/schema failure, cache unavailability, and working-set
  essential overflow preserve the original post-image-policy request and forward
  normally;
- malformed transform payload, unsupported injection shape, duplicate/conflicting
  marker, or ambiguous root handling returns a deterministic sanitized 4xx before
  upstream;
- image enforcement remains independent and must not be bypassed;
- no compiler call may traverse this adapter’s public listener;
- cancellation releases compiler/cache slots and closes upstream work.

Because no acquired dependencies exist yet, valid missing P1 entries appear as
acquisition instructions in rendered context. Do not fetch them or pretend their
content is present.

### D. Safe observability

Add bounded counters/histograms for constitution enabled/disabled/skipped
reasons, compilation outcome, cache outcome, selection failure, injection
outcome/failure, and duration by endpoint/route. Labels must be fixed and safe.
Never include source paths/content/hashes, prompts/output, identity values,
cache keys, model-visible text, images, or request-derived high-cardinality data.

### E. Tests and live evidence

Use fake upstream tests to prove at least:

- disabled/default routes make zero constitution pipeline calls;
- exactly-one-root enabled Responses and Chat requests receive stable injected
  instructions/system message before upstream;
- identical repeat uses persistent cache hit under explicit static identity;
- zero/multiple/incomplete root requests remain unchanged without compilation;
- compiler failure forwards original governance-bearing request unchanged;
- cache unavailable degrades without losing governance;
- injection conflict/unsupported shape fails closed without upstream call;
- SSE/tools/streaming behavior and image policy results remain preserved;
- no raw source/body/model output appears in logs/metrics/errors;
- cancellation/slot release behavior remains covered;
- public internal headers remain stripped and cannot activate integration.

Run the established full static/unit/fake/build gates. Then perform bounded live
testing against preferred loopback upstream using a temporary repo-owned adapter
on `127.0.0.1:18031`: health/readiness/models, one synthetic AGENTS-enabled
text/tool or text request miss, identical repeat hit, ordinary SSE if practical,
and stop the temporary process. The live image case remains truthfully skipped
because the protected fixture accepts zero images. Record sanitized status/
outcome/count/timing evidence only; never print secrets/raw bodies/source.

## Explicit non-goals

Do not acquire referenced files, ingest paired tool outputs, implement
compaction rehydration/history reduction, add admin/cache endpoints, introduce
signed gateway identity, alter quota/accounting/TLS/routing, copy gateway code,
change model/service flags, cut over either OAP Codex agent, or claim production/
multi-user/vision readiness. Do not edit merged OAP history or reference proxy
provenance.

## Acceptance criteria

### Criterion A — explicit safe activation

Default behavior remains unchanged. Integration occurs only with global plus
route enablement and complete static local identity; client headers cannot
enable or influence it. Invalid combinations fail startup/configuration.

### Criterion B — correct one-root pipeline

Fake-upstream evidence proves exact observation-to-compiler-cache-selector-
injection ordering, deterministic transformed upstream body, missing-P1
instruction presence, and preservation of unrelated request semantics.

### Criterion C — isolation and reuse

Repeated identical requests use versioned/isolated persistent cache identity.
Different principal/session/repository/source/model/schema/version/bounds do not
cross-hit. Absent/invalid identity disables persistent reuse rather than guessing.

### Criterion D — failure and safety semantics

Compiler/cache/selection failures preserve original governance-bearing requests.
Injection marker/shape failures fail closed. Image policy remains independent.
Streaming/tools/errors/disconnect behavior remains preserved.

### Criterion E — observability and privacy

Metrics contain only bounded counts/timings/states. Focused scans prove no raw
source/body/output/credential leakage in code paths/logs/metrics/report.

### Criterion F — live candidate evidence

Bounded live compiler/cache and ordinary text/SSE-or-tool checks pass on temporary
loopback adapter 18031; repeat cache-hit behavior is demonstrated. Live image
case is SKIPPED due independently verified zero-image capability and is not counted
as vision support. Temporary process is stopped and port freed.

### Criterion G — documentation honesty

Docs describe local single-user static identity, pipeline ordering/failure
behavior, privacy, metrics, limitations, and explicitly exclude acquisition,
rehydration, signed multi-user identity, real Codex E2E, gateway integration,
vision readiness, and cutover.

## Required verification and evidence

Run and report exact statuses:

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
git diff --check 867ed55e7d115d960c666380ebbc5952d43d97d1...HEAD
```

Also include focused pipeline/cache/isolation/failure tests, secret/raw-content
scan, scoped diff audit, and protected-host before/after snapshot. Wait for final
report-head GitHub CI; pending/failed/cancelled/missing checks block acceptance.

## Security, privacy, resource, protected-host constraints

Raw prompts/source/images/tool output/response bodies/secrets must never enter
repository, logs, metrics, reports, cache payloads, or transcript evidence. Bound
all input/output/cache/time/concurrency. Adapter/compiler remain CPU-only.
Protected-host access is read-only reconnaissance plus bounded authenticated API
calls through the temporary candidate adapter. Explicitly prohibited: changes to
port 18020, qwen units/process/flags/model/checkpoint/venv/patches, systemd, API
keys, firewall/VPN/network bindings, active Codex profiles, or either OAP agent
route. Candidate binds only loopback 18031 temporarily.

## Publication and immutable report contract

Push amendments to exact branch `oap/003-working-set-injection-foundation`; never
create another PR or merge. Before report, push all non-report work and record
literal implementation head. Atomically publish exactly one new immutable
`oap/reports/003-b-request-pipeline-integration.md`. Its publication commit
(`SELF`) must be sole final round commit, have literal implementation head as
first parent, change only that report path, and be pushed as remote PR head before
response FIFO `OK`.

Report every criterion/command with exact
`PASSED|FAILED|SKIPPED|NOT RUN|BLOCKED|PENDING|MISSING` labels, implementation
SHA, `SELF`, PR/checks, sanitized live facts, scope confirmations, and
limitations. Never rewrite prior artifacts.

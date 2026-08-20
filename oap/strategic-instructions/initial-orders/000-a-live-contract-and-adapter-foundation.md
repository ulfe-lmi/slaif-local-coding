# OAP Work Order — 000-a

> **DRAFT UNTIL STRATEGIC ACTIVATION.** Replace all `VERIFY:` values from live
> GitHub/host inspection. Then atomically copy to `oap/orders/`, write
> `oap/active=000-a`, and signal. Coding must never execute this draft directly.

## Objective

Create exactly one new PR implementing the first usable SLAIF Local Coding MVP
slice:

1. establish locked Python project/CI baseline;
2. implement a faithful private async OpenAI-compatible adapter on
   `127.0.0.1:18031` forwarding to the already-running local vLLM service;
3. integrate route-scoped newest-image-only request adaptation from the supplied
   reference proxy behavior;
4. preserve text, ordinary function tools, SSE streaming, errors, usage, and
   disconnect semantics;
5. validate with fake upstream and bounded live calls to the current vision-mode
   vLLM REST API;
6. leave the model, vLLM, current Codex vision path, network, keys, and active
   profiles unchanged.

Do not implement constitutional compilation/cache/injection in objective 000.

## GitHub objective state

- Repository: `VERIFY: owner/slaif-local-coding`
- Repository URL: `VERIFY: URL`
- Numeric objective: `000`
- Execution round: `000-a`
- PR mode: `CREATE_NEW_PR`
- Existing PR: `N/A` after verification
- Base branch: `VERIFY: remote default, expected main`
- Starting base SHA: `VERIFY: literal 40-hex`
- Required head branch: `oap/000-adapter-foundation`
- Required PR title: `[OAP 000] Add live-tested adapter foundation and image policy`
- Required PR readiness: non-draft

Strategic MUST verify no existing objective-000 PR before activation.

## Strategic context

The current local Qwen/VLLM setup is already useful for Codex and vision. The supplied reference proxy demonstrates one concrete compatibility algorithm:
recursively remove every older `input_image`/`image_url` item and retain the
newest. It is reference code only; no deployed legacy image proxy is assumed. The final behavior belongs
inside one private server-side model-compatibility layer immediately before
vLLM, behind the separate SLAIF API Gateway.

Objective 000 proves this common adapter point and request fidelity. It must not
risk the endpoint used by the coding Codex itself. The candidate runs on 18031;
the current Codex/vLLM path remains untouched.

## Current independently verified state

Complete immediately before activation and record literal evidence in this
section:

- Remote default branch/SHA: `VERIFY`
- Open PRs and objective-000 duplicates: `VERIFY`
- Clean/known working tree and bootstrap commit: `VERIFY`
- Current user and host: `VERIFY`
- `qwen-serving` unit/service state: `VERIFY`
- Exact current vLLM process command (redacted secrets): `VERIFY`
- Actual bind/listeners for 18020/18031 and any unexpected 18021 listener: `VERIFY`
- Actual upstream base URL/model ID: `VERIFY`
- Actual vision-enabled configuration and effective max image count: `VERIFY`
- Confirm no pre-existing image-cap proxy is deployed; if contrary live evidence exists, record exact service/process safely: `VERIFY`
- Coding Codex active profile/provider endpoint: `VERIFY`
- API-key source mechanism/path/env name, value never printed: `VERIFY`
- Authenticated `/health` and `/v1/models` status: `VERIFY`
- Port 18031 free: `VERIFY`

Historical documents are evidence only; if current state differs, update this
order before activation. Do not activate with unresolved service facts.

## Required files to inspect

At minimum:

```text
AGENTS.md
OAP-COMMUNICATION-coding-agent.md
ARCHITECTURE-for-agents.md
SECURITY.md
TESTING.md
config/adapter.example.toml
docs/LIVE-TEST-ENVIRONMENT.md
docs/IMPLEMENTATION-ROADMAP.md
references/qwen38_vision_image_cap_proxy.py
```

Inspect protected live files/processes read-only only as needed to establish the
verified state. Never copy secrets into repository or report.

## Scope

### A. Project and CI foundation

Create a conventional `src/` Python 3.12 package, exact-name chosen consistently
(e.g. `slaif_local_coding`), with:

- `pyproject.toml`;
- committed `uv.lock`;
- frozen install/test commands;
- Ruff, mypy, pytest/pytest-asyncio configuration;
- CI workflow on supported Ubuntu/Python 3.12;
- console/module entry point;
- version source;
- deterministic configuration contract;
- README/quickstart updates needed for this implemented slice.

Use current stable, compatible, permissively licensed dependencies. Minimum
expected runtime classes: FastAPI/Starlette, HTTPX, Pydantic settings, Uvicorn;
Prometheus client only if used by the bounded metrics implementation. Record
license review. Do not add model/torch/image-processing dependencies.

### B. Async adapter foundation

Implement a CPU-only ASGI service with local endpoints:

```text
GET /healthz
GET /readyz
GET /metrics                    private/local MVP
```

Faithfully forward at least:

```text
GET  /health
GET  /v1/models
POST /v1/responses
POST /v1/chat/completions
```

Requirements:

- bind `127.0.0.1:18031` by candidate/example config;
- upstream URL configurable; no hard-coded production address in application;
- upstream auth from protected environment/file configuration; never log/return
  secret; do not blindly forward external bearer as upstream credential;
- bounded body and connection/read/write/pool timeouts;
- remove hop-by-hop headers and caller-spoofed internal/debug headers;
- preserve relevant content type/status/headers/error body/usage;
- stream SSE incrementally without full-response buffering;
- flush chunks promptly and cancel/close upstream on client disconnect;
- no automatic retries after a request may have reached upstream unless proven
  safe; document exact policy;
- sanitized 502/503 behavior on upstream failure;
- readiness validates static configuration and bounded upstream availability
  according to documented policy;
- no raw request/response/prompt/source/tool/image logging.

Architecture should make future policies an ordered typed request pipeline, not
one monolithic handler. Objective 000 may include only identity/request context,
route selection, image policy, and forwarding stages; leave explicit extension
interfaces for later constitution stages without implementing them.

### C. Route/model policy

Implement validated configuration equivalent to:

```text
route ID/model match
max_images_per_request
image_overflow_policy = retain_newest | reject | passthrough
enable_responses
enable_chat_completions
```

Unknown policy/capability must fail startup/readiness rather than guess. Default
must not silently transform every model. The tested Qwen Codex vision route is
explicitly configured `max_images_per_request=1`, `retain_newest`.

No public gateway identity contract is required yet. Listener is loopback-only.
Document that production service auth/signed identity arrives in objective 005.

### D. Newest-image policy

Port the proven algorithm as a pure tested policy module, not by importing or
running a separate client-side proxy.

Support at least:

- Responses content item `{"type":"input_image", ...}`;
- Chat content item `{"type":"image_url", ...}`;
- nested lists/dictionaries used by captured request shapes.

For configured `retain_newest`, count all supported image items in deterministic
request traversal order and remove every image except the newest. Preserve all
non-image values and relative order. Zero/one images are byte-semantically
unchanged after JSON parsing/serialization. Verify transformed final count does
not exceed limit.

For `reject`, return deterministic API-shaped 400/422 without upstream call.
For `passthrough`, do not rewrite. Unknown/ambiguous over-limit image shape fails
closed; never silently discard content not recognized as supported image item.

Expose safe response/metric metadata as counts only (`seen`, `removed`, policy,
route), never image content/URL/data. Do not require a public diagnostic header;
if included for MVP, it must be disabled by default and contain counts only.

Document semantic limitation: newest-only supports Codex full-image→crop history;
it does not preserve explicit multi-image comparison.

### E. Metrics and logs

Provide bounded private metrics/log fields sufficient to diagnose:

- requests/status/latency by endpoint/route;
- upstream failures/timeouts/disconnects;
- stream/non-stream mode;
- image items seen/removed/rejected;
- readiness state.

No raw body, prompt, source path/content, image, tool arguments/output,
authorization, URL query secret, or unbounded high-cardinality label. Request ID
must be generated/trusted safely and sanitized.

### F. Packaging for candidate testing

Provide:

- example TOML/env configuration without secrets;
- repo-local development start command;
- user-level systemd template/example for candidate service on 18031, but do not
  install/enable it unless order explicitly permits temporary candidate use;
- health/readiness/stop commands;
- exact rollback = stop candidate/remove repo-owned candidate state; current
  Codex/vLLM path requires no rollback because it must remain unchanged.

A temporary user service named distinctly from the model service is allowed
only if it binds 18031, uses repo/venv, does not persist secrets in unit text,
and is stopped/removed or clearly documented at report end. Prefer foreground
process for tests.

## Non-goals

- No constitutional `AGENTS.md` detection, file ranking, compiler call, cache,
  pseudo-context injection, rehydration, or compaction logic.
- No SLAIF API Gateway code/change/deployment/key/accounting integration.
- No public listener/TLS/NGINX/firewall/VPN change.
- No modification/restart/reconfiguration of qwen-serving/vLLM/model/weights/
  checkpoint/quantization/patches/venv/systemd/port 18020.
- No modification of active coding/strategic Codex profiles, keys, account,
  session, compaction threshold, or model catalog.
- No cutover, profile switch, route switch, gateway route, production deploy.
- No ChatGPT UI, admin GUI, database, Redis, distributed cache, queue.
- No image decode/re-encode/resize/OCR/content analysis.
- No custom/freeform `apply_patch`, hosted tools, web search, MCP, file search,
  code interpreter, computer use.
- No broad refactor of bootstrap governance/architecture.
- No claim of generic model compatibility, production readiness, privacy/
  security certification, or frontier-model equivalence.

## Acceptance criteria

1. Exactly one non-draft objective-000 PR exists with required base/head/title;
   coding agent never merges.
2. Python 3.12 project has committed lock, frozen local/CI install, formatting,
   lint, typing, unit/contract tests, build/package smoke, license/provenance docs.
3. Candidate starts on 127.0.0.1:18031 and forwards configured endpoints to live
   vLLM without changing port 18020 or the active Codex profile/provider path.
4. Fake-upstream tests prove status/header/body/error/tool/usage fidelity and
   incremental SSE forwarding; disconnect closes/cancels upstream.
5. Image tests prove zero/one unchanged, multiple leaves exactly newest across
   Responses and Chat shapes, non-image order preserved, reject avoids upstream,
   passthrough unchanged, unknown policy fails closed.
6. Policy is explicit route/model configuration and not global.
7. Bounded authenticated live tests pass against current vLLM for health/models,
   plain Responses, ordinary function tool, SSE stream, multi-turn tool output,
   one image, and two-image request through candidate retaining newest. Any
   unsupported current provider shape is reported exactly, not hidden.
8. Live tests use small outputs, serial execution, no raw payload/secret logs,
   and leave service/model state unchanged.
9. Metrics/log tests prove only safe bounded metadata; secret/raw-content scans
   find no leakage in tracked files/test output/application logs.
10. Documentation accurately describes implemented behavior, route semantics,
    candidate start/config, live-test opt-in, protected fixture, limitations,
    gateway separation, and no cutover.
11. Before/after evidence confirms vLLM 18020 process/command and active Codex provider path,
    systemd/config/profile/firewall/VPN/key files were not changed by objective.
12. Final report-only SELF commit and OAP transcript satisfy protocol.

## Verification required

Coding determines exact commands from implemented project, but must include and
report at least equivalent of:

```bash
uv lock --check
uv sync --frozen --all-groups
uv run --frozen ruff check .
uv run --frozen ruff format --check .
uv run --frozen mypy src tests
uv run --frozen pytest -q
uv build
python -m compileall -q src tests oap/bin
bash -n oap/bin/*.sh
```

Fake-upstream suites must explicitly cover:

```text
non-stream text; provider error; auth replacement; hop-by-hop stripping
ordinary function call and function_call_output continuation
SSE event order/chunking/usage; client disconnect; upstream timeout
image zero/one/multiple for Responses+Chat; reject; passthrough; malformed input
body/config bounds; no raw logging; metrics label bounds
```

Live suite is opt-in, e.g. `SLAIF_LIVE_TEST=1`, and must:

- discover key from protected configured mechanism without printing it;
- run serially with bounded output/timeouts;
- call candidate 18031, not bypass it except comparative diagnostic clearly
  labeled;
- verify model ID and event/tool structures;
- use safe synthetic images/requests;
- record sanitized counts/status/timing only;
- skip/block honestly if live service/credential unavailable.

Also run:

```bash
git diff --check <base>...HEAD
git diff --name-only <base>...HEAD
git status --short
gh pr view <PR> --json number,url,state,isDraft,baseRefName,headRefName,headRefOid
gh pr diff <PR> --name-only
gh pr checks <PR>
```

Inspect service/listener/process/profile state before and after using read-only
commands. Hash relevant protected config files before/after when readable without
secret output; record hashes/metadata only. Do not fail because secret file
content is intentionally unread/restricted.

## Documentation required

Update/create as needed:

- README quickstart for implemented candidate slice;
- configuration reference;
- image-policy contract/limitations;
- testing/live-test instructions;
- candidate operations/systemd example;
- architecture only if implementation materially requires an explicitly
  strategic-approved correction; otherwise do not rewrite architecture;
- third-party notices/modified-derived-code attribution.

Do not document future constitution/compiler/cache as implemented.

## Safety / security / protected-host constraints

- No secret values in commands, shell history literals, logs, tests, report,
  screenshots, Git, PR, CI, or metrics.
- No production/customer data.
- Candidate loopback only; no network/firewall widening.
- No 18020/Qwen/vLLM/current-Codex-profile mutation.
- No model download/duplicate model process/GPU memory allocation by adapter.
- No image/source/prompt persistence.
- Bounded live test load; stop on GPU/service instability and report.
- Preserve unrelated work and bootstrap documents.
- Passwordless sudo only for safe repo-local build/test dependencies; not for
  protected service/network mutation.

## Local execution capability

Coding agent owns venv/dependency installation, fake upstream, test tools,
foreground candidate process, and safe diagnostics. Do not ask human/strategy to
run ordinary commands or paste logs. Genuine blockers: GitHub/network/credential
access, protected resource, current-service instability, unsafe authority
expansion, architecture/product ambiguity.

## GitHub workflow

1. Fetch/reconcile remote.
2. Create required fresh branch from current verified base.
3. Commit activated order+active unchanged with implementation work.
4. Stage explicit paths only; never `git add .`/`-A`/`--all`.
5. Push implementation and create exactly one required non-draft PR.
6. Inspect/fix safe in-scope CI failures.
7. Push all non-report work; capture literal implementation head SHA.
8. Atomically publish matching report; final commit changes only report.
9. Push/verify report SELF commit as current PR head and parent=implementation
   SHA.
10. No further mutation/push; exact response FIFO `OK`; never merge.

## Required report

Publish exactly:

```text
oap/reports/000-a-live-contract-and-adapter-foundation.md
```

Use full coding protocol report contract. Include:

- exact verified initial/final live service/listener/profile facts, sanitized;
- PR/base/head/start SHA/implementation SHA/SELF;
- exact dependencies and license/provenance result;
- exact fake/live commands/results and test counts;
- SSE/tool/image-policy evidence;
- whether any live test skipped/blocked and why;
- before/after protected-file hashes/process command/listener/unit states without
  contents/secrets;
- explicit `18020 changed NO`, `qwen-serving changed NO`,
  `Codex profiles changed NO`, `firewall/VPN/key files changed NO` unless a
  contradiction is truthfully reported as failure;
- all GitHub check states;
- limitations and strategic recommendation;
- coding merge `NO`, extra PR `NO`, report-only SELF verification.

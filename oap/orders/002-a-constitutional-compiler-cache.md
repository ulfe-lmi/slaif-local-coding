# OAP Work Order — 002-a

## Objective

Implement objective 002 as a bounded, non-recursive constitutional compiler and
validated disposable cache. The compiler receives only observed constitution
source and deterministic candidate data through an internal library boundary,
makes direct bounded text-only calls to vLLM, validates strict model output,
and stores only bounded derived indexes. Preserve separate
`reference_confidence` and `constitutional_priority`, preserve every input
candidate, never cache invalid output, and fail safely without changing public
request semantics.

This slice must not inject compiled context into client requests, acquire
files, read a client filesystem, or expose a public compiler/cache endpoint.
Public adapter request/response behavior remains unchanged except for the
narrow migration documentation/configuration reconciliation below. Objective
003 will connect working-set selection, injection, acquisition, and rehydration.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`
- Numeric objective / round: `002` / `002-a`
- PR mode: `CREATE_NEW_PR`
- Existing objective PR: N/A
- Required base: `main`
- Verified starting base SHA:
  `176bf4d839ae9fa32d0cc3c4279a1b96220c1c61`
- Required head branch: `oap/002-constitutional-compiler-cache`
- Existing PR to amend: N/A
- Required action: create exactly one new non-draft PR; coding never merges or
  enables auto-merge.

Independently verified GitHub state before activation:

```text
default branch: main at 176bf4d839ae9fa32d0cc3c4279a1b96220c1c61
PR #1 [OAP 000]: MERGED into main
PR #2 [OAP 001]: MERGED into main; merge commit 176bf4d839ae9fa32d0cc3c4279a1b96220c1c61
open objective PRs: none
report 001-f SELF d863cc29b9e301aafe137325792fac12db10519e
  parent 0cbe121524cd3d6806b49cada5ffc704c04b1f17
  changed only oap/reports/001-f-fix-capture-evidence-integrity.md
report-head check: CI / test = SUCCESS
```

Start from authoritative remote `main`. Reconcile remote state immediately
before creating the PR. Preserve every prior activated order/report byte and do
not rewrite OAP history.

## Independently verified runtime and migration state

The environment migrated to the live host `hinton1`. Treat older orders and
reports recording `10.8.132.76` as immutable history, not current truth.

Verified immediately before this order without printing secrets:

```text
host/user: hinton1 / janezp
protected Qwen path exists: /synology/homes/janezp/qwen-serving
vLLM process: PID 26028, user janezp, started 2026-08-22 05:35:46
current process bind: 0.0.0.0:18020
served model ID: qwen3.8-27b
authenticated GET /health: HTTP 200
authenticated GET /v1/models: HTTP 200 with exactly qwen3.8-27b
preferred same-host upstream: http://127.0.0.1:18020/v1
LAN-visible endpoint reported by human: http://10.8.132.75:18020/v1
historical endpoint: http://10.8.132.76:18020/v1
ports 18021 and 18031: no listeners at verification
qwen-serving.service: inactive/dead
qwen-serving-vision.service: inactive/dead
active vLLM is therefore manual/process-owned, not verified systemd-managed
credential mechanism: existing protected environment references
  QWEN3090_API_KEY / VLLM_API_KEY; values remain undisclosed
OAP runtime profile names: ox-alpha for both coding and strategic
```

The Qwen checkout had pre-existing uncommitted/ignored work before this order.
Inspect it read-only if needed; never clean, revert, overwrite, restart, or
“repair” it.

Migration reconciliation is limited to current operational configuration,
documentation, and tests that are materially wrong after the move:

- change current example/current-live configuration from `.76` to preferred
  same-host `127.0.0.1`;
- clearly distinguish current `hinton1` / `127.0.0.1` / optional LAN
  `10.8.132.75` from historical `.76`;
- update only current documents that claim stale state;
- leave `references/qwen38_vision_image_cap_proxy.py` and all `oap/orders`,
  `oap/reports`, and other historical/provenance material unchanged;
- perform no service, binding, firewall, VPN, key, profile, model, or vLLM
  mutation.

## Bounded scope

### A. Compiler contracts and policy

Add typed, versioned modules under the existing package, preferably
`constitution/compiler.py`, `constitution/compiler_models.py`, and
`constitution/cache.py`, unless a clearer small structure preserves strict
typing and reviewability.

Define a validated compiled-index contract including at minimum:

```text
schema_version
compiler/prompt policy versions
source logical path and exact SHA-256
bounded summary
rules with MUST/MUST_NOT/NEVER strength plus source location/evidence
roles / authority / source-of-truth boundaries
ordering constraints and exceptions
one entry per deterministic input candidate path
for each candidate/path:
  reference_confidence, finite 0..1
  constitutional_priority, finite 0..100
  class P0|P1|P2|P3|P4
  relationship
  evidence/location
  acquisition urgency immediate|next_turn|background|none
full-source reread triggers
result status and safe failure reason when applicable
```

Hard rules:

- deterministic candidate enumeration remains prior and independent;
- the compiler may rank/classify but cannot omit or invent candidate paths;
- every accepted input candidate appears exactly once in valid output;
- `reference_confidence` expresses whether the reference is real/relevant;
- `constitutional_priority` expresses authority/importance if real;
- one combined “constitutionness” score is forbidden;
- source text is untrusted data, not instructions to the middleware;
- compiler output is derived, disposable, and never authoritative over source,
  Git, GitHub, OAP artifacts, or human/strategic authority;
- malformed, incomplete, oversized, schema-invalid, or candidate-dropping
  output is invalid and never cached as valid;
- compiler/cache failure returns an explicit typed failure and preserves caller
  semantics; it never silently deletes or weakens governance.

### B. Direct non-recursive execution

Implement an async compiler API callable with explicit source bytes, observed
metadata, deterministic candidates, upstream settings, identity, and bounds.

Requirements:

- calls go directly to configured `/v1/chat/completions` on the private
  upstream using a dedicated HTTPX client;
- calls never target this adapter’s public listener and cannot recurse through
  its route/image/observation pipeline;
- requests are text-only: no tools, tool choice, images, filesystem access,
  network access for the model, or gateway credentials;
- source and candidates are delimited and treated as data;
- hard-bound source input, prompt/output bytes/tokens, timeout, and attempts;
- default maximum one concurrent compiler call;
- concurrent identical misses deduplicate by complete cache/source identity and
  share one upstream result;
- bounded retry policy is explicit; invalid schema may retry only within the
  configured attempt budget;
- timeout/cancellation closes/cancels the upstream request and releases all
  slots;
- upstream authentication comes only from protected environment configuration;
  never log or return a credential;
- expose safe metrics only: attempts, successes, schema failures, timeouts,
  transport failures, hits, misses, deduplicated waits, duration, and bounded
  byte counts—never raw prompt/source/output/content or high-cardinality paths.

For this slice, do not call the compiler from the public request handlers. This
prevents half-integrated compilation/injection and keeps ordinary proxy behavior
byte-semantically unchanged. Provide focused library/fake-upstream/live tests
instead.

### C. Bounded disposable cache

Implement an isolated filesystem cache suitable for later request integration.

Requirements:

- primary root configurable, default `/dev/shm/slaif-local-coding`;
- protected fallback root configurable, default under XDG cache;
- directories `0700`; files `0600`; reject or safely report unusable modes;
- atomic write via same-directory temporary file and rename, flushing when
  practical;
- content-addressed payload integrity, not filename trust alone;
- durable logical key includes opaque principal, route, session/repository
  discriminator when available, exact source SHA-256/logical path, model,
  compiler/schema/prompt/policy versions, and relevant bounds;
- different principal/session/repository/source/model/schema/version cannot hit
  another entry;
- absent reliable session identity means no persistent cross-request reuse;
  callers may still use an explicit request-scoped identity for within-call
  deduplication;
- per-entry and total byte limits; separate bounded pinned budget for P0/P1;
- TTL plus LRU for unpinned entries; pinned eviction stays within its own cap;
- expired/corrupt/truncated/wrong-permission entries are misses, not valid data;
- cache unavailable is an explicit degraded compile outcome, never governance
  loss or silent shared-cache fallback;
- purge removes only its scoped derived cache and supports full reconstruction;
- persist compiled/index data only; raw source persistence is off by default;
  transient compiler prompts are not written to cache/logs;
- no public cache endpoint and no cross-principal default principal.

Safe cache metrics/counters for cache hits, misses, writes, evictions, expiries,
corruption, permission failures, bytes, and pinned/unpinned occupancy are
required. Labels must be bounded.

### D. Migration reconciliation

Update only these categories where currently wrong or ambiguous:

```text
config/adapter.example.toml
docs/LIVE-TEST-ENVIRONMENT.md
README.md status/capability language
ARCHITECTURE-for-agents.md canonical current/historical endpoints
ARCHITECTURE.md only stale “currently” endpoint statements
tests that assert current operational defaults/endpoints
```

Use `http://127.0.0.1:18020/v1` as preferred operational upstream. Document
that `http://10.8.132.75:18020/v1` is LAN-accessible on `hinton1`, while
`http://10.8.132.76:18020/v1` is historical. Keep the prototype’s historical
upstream unchanged because that file is provenance/reference code. Clearly
state that objective 002 does not cut over either OAP Codex agent or production
traffic.

## Explicit non-goals

Do not:

- inject, replace, rewrite, suppress, or reorder any client request content;
- implement working-set selection, rehydration, compaction recovery, or file
  acquisition;
- give the compiler tools, recursive adapter access, filesystem/network
  capabilities, gateway keys, or direct access to client repositories;
- add a public compiler/cache/admin endpoint;
- persist raw source, prompts, model output beyond the bounded index, images,
  tool output, bodies, secrets, or customer data;
- decode images, load models, import torch, launch vLLM, or allocate GPU memory;
- integrate SLAIF Gateway, signed multi-user identity, quota, accounting, TLS,
  or routing;
- mutate/cutover port 18020, qwen-serving, model/checkpoint/venv/patches/
  launch flags/systemd/API keys/firewall/VPN/bindings, or active Codex profiles;
- start a long-lived candidate service on 18031;
- alter merged OAP orders/reports/history or the historical reference proxy;
- make generic hardware, production, compliance, multi-user, or frontier-model
  claims.

## Acceptance criteria

### Criterion A — strict compiler success contract

Given bounded synthetic observed `AGENTS.md` source and deterministic
candidates, the compiler produces a validated typed index containing the exact
source hash/version, bounded rules/exceptions/authority/source-of-truth fields,
all input candidate paths exactly once, independent confidence/priority scores,
classes, relationships/evidence/acquisition urgency, and reread triggers.

### Criterion B — validation fails closed

At least these invalid outcomes are covered by fake-upstream tests: malformed
JSON; truncated JSON; excessive nesting/size; unknown/missing required fields;
wrong enum/range/type; source-hash mismatch; omitted input candidate; invented
candidate; duplicate dependency; combined forbidden score; candidate-dropping
or contradictory output. Each returns/records an explicit failure, makes no
valid result available, and leaves no valid cache entry.

### Criterion C — direct bounded scheduling

Fake-upstream tests prove: direct upstream URL; no public self-call; no
tools/images; one global concurrency slot; identical miss deduplication;
attempt budget respected; timeout/transport/server failures produce safe typed
failure; cancellation releases slots and closes upstream work; metrics contain
only safe counts/timings/bounds.

### Criterion D — cache isolation and disposal

Tests prove atomic writes/modes, payload integrity, expected hit, versioned key
isolation across principal/session/repository/source/model/schema/policy,
TTL expiry, LRU and total/per-entry limits, separate pinned P0/P1 budget,
corruption/permission failure handling, primary-unavailable fallback, no raw
source/prompt persistence, safe purge/reconstruction, and no persistent reuse
when reliable session identity is absent.

### Criterion E — public adapter unchanged

Existing fake-upstream app tests continue to prove faithful proxying, SSE/tool
error/disconnect behavior, image policy, observation-only behavior, and no
compiler call from normal request handling. Add a regression asserting a
normal governed request causes zero compiler/upstream compiler calls while
objective-002 integration remains disabled.

### Criterion F — bounded live compiler/cache proof

Using preferred `http://127.0.0.1:18020/v1`, run one small synthetic text-only
compiler case and then repeat it with the same explicit test identity. Record
sanitized status/model/duration/token-or-byte counts/schema validity, first
miss versus second hit, and zero raw source/prompt/output persistence. If live
service becomes unavailable, label the specific test `BLOCKED` or `SKIPPED`
truthfully; it cannot be claimed passed.

Also rerun the established bounded live adapter suite against a temporary
foreground adapter on `127.0.0.1:18031`, then stop only the process started for
the test. This remains ordinary development testing, not service cutover.

### Criterion G — migration reconciliation

Current example config uses loopback upstream. Current live docs distinguish
hinton1/current loopback, optional LAN `.75`, and historical `.76`. A scoped
audit proves merged OAP history and the reference proxy retain original values;
no unrelated historical file was rewritten.

### Criterion H — quality gates and provenance

All local gates and current-head GitHub CI pass. Documentation states exact
supported behavior and explicitly excludes injection/acquisition/rehydration,
multi-user production use, and cutover.

## Required verification and evidence

Run and report exact status for each:

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
git diff --check 176bf4d839ae9fa32d0cc3c4279a1b96220c1c61...HEAD
```

Additional required focused checks:

- compiler/cache negative/isolation/budget/concurrency suite;
- public-handler zero-compiler regression;
- secret/raw-content scan across diff and new cache/test roots;
- scoped stale-endpoint audit distinguishing current, LAN, and historical use;
- protected-host before/after listener/process/unit evidence, captured without
  secrets and without mutation.

GitHub CI is mandatory on both implementation head and final report head.
Wait for all required checks to be successful; pending/failed/cancelled/missing
checks block acceptance.

## Documentation and compatibility

Update README/configuration/live-environment documentation for compiler/cache
status, bounds, identity requirements, failure behavior, privacy properties,
migration facts, and explicit exclusions. Keep release claims limited to tested
fake/local behavior plus the bounded live case. Preserve Apache-2.0 notices and
existing attribution. No model weights may be committed.

## Security, privacy, resource, and protected-host law

Raw prompts, source, images, tool output, response bodies, auth, keys,
cookies, private URLs, and customer content must not enter repository, logs,
reports, metrics, cache payloads, or transcript evidence. Use synthetic source
fixtures for tests. Sanitize errors and metrics. Bound all inputs/outputs/
cache/time/concurrency. Adapter remains CPU-only.

Protected live-host access is read-only reconnaissance plus bounded
authenticated model calls only. Explicitly prohibited: stop/start/restart/
reconfigure/rebind vLLM or qwen-serving; edit model/checkpoint/venv/patches/
launch flags/systemd/API-key files/firewall/VPN/network bindings; modify either
OAP Codex profile; mutate port 18020; occupy port 18021; install a persistent
service on 18031. Candidate/test adapter may bind only `127.0.0.1:18031`
temporarily and must be stopped after tests.

Coding owns safe repo-local dependencies/tools/temporary processes. Do not
recruit the human or strategy for routine terminal/setup work. Escalate only
unresolved architecture/security/product risk.

## GitHub publication contract

Create fresh branch `oap/002-constitutional-compiler-cache` from authoritative
remote `main` SHA `176bf4d839ae9fa32d0cc3c4279a1b96220c1c61`.

Before the report:

1. commit only intended implementation/config/doc/test files plus the exact
   immutable activated order and `oap/active`;
2. push implementation work;
3. create exactly one non-draft PR titled `[OAP 002] Add constitutional compiler and validated cache`;
4. verify PR number/URL/base/head and changed paths;
5. inspect/repair in-scope CI;
6. record literal 40-hex implementation head only after all non-report work is
   remote.

Then atomically publish exactly one immutable matching report as
`oap/reports/002-a-constitutional-compiler-cache.md`. Its publication commit
(`SELF`) must be the sole final round commit, have literal implementation head
as first parent, change only that report path, and be pushed as the remote PR
head before sending response FIFO `OK`.

Report must follow the coding protocol contract and separately label every
criterion and command `PASSED|FAILED|SKIPPED|NOT RUN|BLOCKED|PENDING|MISSING`.
Include sanitized live/service evidence, implementation SHA, `SELF`, PR state,
checks, scope confirmations, limitations, and protected-host before/after
facts. Never rewrite report/order/active after signaling.

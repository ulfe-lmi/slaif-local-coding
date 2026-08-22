# OAP Work Order — 002-b

## Objective

Amend objective-002 PR #3 only. Close the independently verified cache-security,
cache-bound, and migration-documentation gaps from `002-a`. Preserve the
library-only compiler boundary and all objective exclusions. Explicitly record
the current host's text-only/zero-image model capability without attempting any
protected-service change; rely on existing fake image-policy tests and merged
objective-000 historical vision evidence for vision behavior.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`
- Numeric objective / round: `002` / `002-b`
- PR mode: `AMEND_EXISTING_PR`
- Existing PR: #3, `https://github.com/ulfe-lmi/slaif-local-coding/pull/3`
- Required base: `main`
- Verified base SHA: `176bf4d839ae9fa32d0cc3c4279a1b96220c1c61`
- Required head: `oap/002-constitutional-compiler-cache`
- Current verified remote head / `002-a` report SELF:
  `fe936c1bc706207f5c3fb81d6a08d1d1a228fbc9`
- Prior implementation SHA:
  `62463f1818b33237c1e3992afb00b24dcd8b9575`; it is the sole first parent of
  report SELF
- Report commit changes only immutable
  `oap/reports/002-a-constitutional-compiler-cache.md`; remote/local blob SHA is
  `7b548ed427cc2ccde14c17d86600ad28cc0efe81`
- PR state: OPEN, non-draft, correct base/head, mergeable/CLEAN; current-head
  `CI` / `test` SUCCESS
- Required action: **NO NEW PR**; no coding merge/auto-merge.

Reconcile GitHub before mutation and preserve every prior order/report byte.

## Independently verified current runtime facts

Verified immediately before this order without printing secrets:

```text
host/user: hinton1 / janezp
user systemd qwen-serving.service: active/running, MainPID 26028,
  started Sat 2026-08-22 05:35:46 CEST
qwen-serving-vision.service: inactive/dead
vLLM listener: unchanged at 0.0.0.0:18020, PID 26028
authenticated /health: HTTP 200
authenticated /v1/models: HTTP 200; exactly one model ID qwen3.8-27b
current process launch class: language-model-only
current live image probe evidence from 002-a: upstream returned HTTP 400 and
  declared capacity for zero images
ports 18021 and 18031: free after testing
```

Therefore current operational documentation must not describe this service as a
live vision service. The older vision-mode deployment remains valid historical
provenance only. Do not restart, reconfigure, enable another unit, alter flags,
or attempt to “restore” vision capability in this objective.

## Independently verified gaps

### Gap A — current capability documentation overstates vision

Current README/live-environment/architecture text still refers to the migrated
service as vision or says vision capability is merely unconfirmed. Live evidence
now proves text-only/zero-image behavior. Documentation and tests must state the
current fact while preserving the distinction from historical vision-mode
records.

### Gap B — cache root trust is insufficient

`_safe_prepare` accepts an already-existing directory based on mode alone. It
does not reject a symlink or a directory owned by another UID. Thus a predictable
fallback such as `/tmp/slaif-local-coding-cache` can be pre-created by another
local user and mistaken for protected cache storage. Cache shard directories and
entry files need equivalent ownership/type/mode checks.

### Gap C — restart cleanup and occupancy are not bounded

At startup, `_load_existing` discovers entries and ignores invalid/expired files.
It neither removes those artifacts nor bounds discovery if many stale files
exist. This weakens the disposable/bounded cache law across restarts.

### Gap D — persistent identity omits output-affecting bounds

The cache key includes source/model/schema/compiler/prompt versions and output
tokens, but not other deterministic resource/policy bounds that affect whether a
derived result should be reused. Configuration also does not expose several
compiler bounds implemented only as library defaults.

## Bounded scope

### A. Cache safety and isolation hardening

Harden every cache root, fallback root, shard directory, entry file, and
temporary-file path:

- reject symlinks;
- require current effective UID ownership;
- require directory mode exactly `0700`, file mode exactly `0600`;
- fail closed to degraded/unavailable rather than use an untrusted path;
- preserve atomic writes and safe temporary cleanup;
- ensure fallback selection cannot adopt a hostile pre-created directory;
- replace the `/tmp` example fallback with a protected user-cache path such as
  `${XDG_CACHE_HOME:-$HOME/.cache}/slaif-local-coding`.

Bound startup reconciliation:

- add an explicit finite startup scan/discovery limit;
- remove expired, corrupt, malformed, wrong-mode, wrong-owner, symlinked, or
  otherwise invalid derived JSON/temp artifacts encountered during the bounded
  scan;
- if discovery exceeds the configured bound, mark cache unavailable/degraded
  with a fixed safe reason instead of silently operating on partial state;
- keep process-local metadata bounded;
- prove restart behavior for valid hit, expired removal, corruption removal, and
  over-limit refusal;
- do not delete authoritative user files outside the configured dedicated cache
  root.

Extend persistent identity to include every deterministic, output-affecting
bound, at least:

```text
source byte bound
rendered prompt byte bound
output token bound
output byte bound
candidate count bound
JSON depth bound
reasoning effort/policy
```

Keep principal/session/repository/route/source/path/model/schema/compiler/prompt
isolation intact. Add focused tests proving changing any included bound does not
hit an old entry.

Expose the compiler/cache bounds needed to construct these identities through
validated configuration while retaining finite ranges and safe defaults. Keep
public request integration false-only.

### B. Capability and migration documentation correction

Update current operational docs/tests to state:

```text
current hinton1 service: text-only / zero-image capable
preferred upstream: http://127.0.0.1:18020/v1
optional LAN upstream: http://10.8.132.75:18020/v1
historical endpoint: http://10.8.132.76:18020/v1
historical vision deployment/evidence: preserved as provenance, not current
```

Remove unsupported current “vision service” wording from active architecture/
operations documents where it contradicts verified state. Clearly say objective
000 previously passed live one/two-image policy tests against the prior vision
deployment, while objective 002’s current live image assertion was skipped due
zero-image capability. No merged OAP artifact may be edited.

### C. Acceptance clarification for unavailable current vision fixture

Because the current protected fixture is text-only, do not mutate it. The
current live image/two-image case remains truthfully `SKIPPED` or `BLOCKED` with
the sanitized zero-image reason. For objective-002 acceptance:

- fake-upstream image policy and public-handler regression must pass;
- current live compiler/cache and text/tool/stream/multiturn cases must pass;
- current live image evidence is explicitly not required while the verified
  fixture has zero-image capability;
- no production/vision-readiness claim may be made.

This clarification is based on independently verified current runtime facts; it
does not weaken the image transform tests or prior objective-000 history.

## Explicit non-goals

Do not:

- inject compiled context into requests;
- implement acquisition, working-set selection, rehydration, compaction recovery,
  gateway integration, signed multi-user identity, or cutover;
- add public compiler/cache/admin endpoints;
- persist raw prompts/source/images/tool output/response bodies/secrets;
- enable request-handler compilation or loosen `enabled = false`;
- modify port 18020, either qwen unit, vLLM flags/model/checkpoint/venv/patches,
  systemd state, API keys, firewall/VPN/network bindings, Codex profiles, or
  either OAP agent route;
- edit merged OAP orders/reports/history or reference proxy provenance;
- claim current vision support, production readiness, generic hardware support,
  multi-user safety, compliance, or frontier-model equivalence.

## Acceptance criteria

### Criterion A — untrusted cache roots rejected

Tests prove a symlinked root, foreign-owned directory, bad shard type/owner/mode,
and bad entry type/owner/mode are rejected or treated as corruption without use.
A protected fallback under the user cache is used when the primary is unusable;
an untrusted fallback is never adopted.

### Criterion B — bounded disposable restart behavior

Tests prove startup recognizes valid entries, removes expired/corrupt/invalid
entries, respects the scan limit, and marks excessive unknown state unavailable
rather than partially trusting it. Occupancy and eviction remain bounded.

### Criterion C — complete versioned cache identity

Every newly included bound changes the key and prevents an old hit. Existing
principal/session/repository/source/model/schema/version isolation remains
green. Missing session/repository still prevents persistent reuse.

### Criterion D — configuration contract

Validated settings expose the new bounds with finite limits and safe defaults.
Invalid policies fail startup/library construction. Public handler integration
remains disabled and the zero-compiler-call regression passes.

### Criterion E — truthful current capability and migration docs

Docs/tests distinguish current text-only operation, optional LAN access, loopback
preference, and historical `.76`/vision provenance. No current vision-service
overclaim remains in active operations/architecture text. Merged history remains
byte-preserved.

### Criterion F — cumulative objective-002 quality

All required static/unit/fake/build gates and current GitHub CI pass. The live
compiler/cache proof from `002-a` remains valid evidence for unchanged covered
behavior; rerun focused live compiler/cache tests if code paths changed. Current
text/tool/stream/multiturn live suite passes. Current image test is conditionally
skipped with the exact verified zero-image reason and is never reported as a live
pass.

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
git diff --check 176bf4d839ae9fa32d0cc3c4279a1b96220c1c61...HEAD
```

Also include focused cache security/restart/identity tests, public zero-compiler
regression, scoped stale-endpoint/current-capability audit, secret/raw-content
scan, and protected-host before/after read-only evidence. Wait for final-head CI;
pending/failed/cancelled/missing checks block acceptance.

## Security, privacy, resource, protected-host constraints

No secrets/raw customer content in repository/logs/report/cache/transcript.
Cache stores validated derived indexes only. All paths/files remain private and
owner-checked. Bound scans, entries, bytes, concurrency, time, attempts, and
model output. Adapter/compiler remain CPU-only.

Protected-host access is read-only reconnaissance plus bounded authenticated API
calls only. No service/config/profile/network mutation. Candidate adapter, if
needed, binds only loopback `127.0.0.1:18031` temporarily and is stopped after
tests.

## Publication and immutable report contract

Push amendments to exact branch
`oap/002-constitutional-compiler-cache` and verify they advance only PR #3.
Never create another PR or merge.

Before report, push all non-report work and record literal implementation head.
Then atomically publish exactly one new immutable
`oap/reports/002-b-harden-cache-and-reconcile-capability.md`. Its publication
commit (`SELF`) must be sole final round commit, have literal implementation head
as first parent, change only that report path, and be remote PR head before
signaling response FIFO `OK`.

Map every criterion to concrete evidence. Label each command/test
`PASSED|FAILED|SKIPPED|NOT RUN|BLOCKED|PENDING|MISSING`. Include implementation
SHA, `SELF`, PR state/checks, sanitized live facts, scope confirmations, and
limitations. Never rewrite prior reports/orders/active bytes.

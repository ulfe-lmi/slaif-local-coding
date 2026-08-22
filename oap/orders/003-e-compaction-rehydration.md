# OAP Work Order — 003-e

## Objective

Amend objective-003 PR #5 to complete bounded compaction/new-context
rehydration. After a successful explicitly enabled constitution pipeline round,
retain only validated derived indexes and safe working-set metadata in a
process-local, identity-isolated, TTL/LRU-bounded state. On a later request from
the same configured local identity that no longer observes a root, reinject the
last valid constitution working set idempotently. Do not claim real Codex E2E,
production multi-user safety, vision readiness, or cutover.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`
- Numeric objective / round: `003` / `003-e`
- PR mode: `AMEND_EXISTING_PR`
- Existing PR: #5, `https://github.com/ulfe-lmi/slaif-local-coding/pull/5`
- Required base: `main` at `68f212b5ad316b95fa12ef632e1538b56479081b`
- Required head: `oap/003-working-set-injection-foundation`
- Current verified remote head / `003-d` SELF:
  `dbc8f4947e510bbdc41729a8746ecf3691844e99`
- Prior implementation SHA:
  `ea561cd31663fafcf5c8ca5454fab8513d0bf876`, verified sole parent of SELF
- PR state: OPEN, non-draft, MERGEABLE/CLEAN; implementation/report-head
  `CI` / `test` SUCCESS
- Required action: **NO NEW PR**; no coding merge/auto-merge.

Preserve every prior order/report byte and reconcile remote before mutation.

## Verified context

Objective `003-d` independently passed local gates (`240 passed`, seven opt-in
live skips), static/type/build checks, secret scanning, and both current-head CI
checks. It implements request-only dependency acquisition but explicitly leaves
compaction rehydration missing. Protected vLLM remains PID 26028 on
`0.0.0.0:18020`; current fixture is text-only/zero-image.

## Bounded scope

### A. Identity-isolated rehydration state

Add process-local state inside the constitution pipeline, not persistent cache
and not public state:

- key includes complete static identity (principal/route/session/repository),
  model, root source hash/path, compiler/schema/prompt versions, selector/render
  policy, relevant bounds, and endpoint-independent index data;
- store validated root and acquired dependency indexes plus dependency
  inclusion metadata; never raw prompts/source/images/tool output/request
  bodies/secrets/cache keys;
- hard-bound entries, per-entry bytes, total bytes, TTL, and LRU;
- newest successful working set replaces prior entry for the same key;
- different identities/models/schema/compiler/policy/source can never cross-hit;
- expired/corrupt/oversized state is discarded as a miss;
- state is intentionally lost on process restart; document that property;
- cancellation/failure does not populate state; only successful validated
  injection does.

### B. Rehydration behavior

For an enabled route:

- if exactly one complete root is observed, compile/acquire/select/inject as in
  `003-d` and replace state only after successful injection;
- if zero roots are observed, find a valid state entry for the exact current
  identity/model/policy and reconstruct/inject the last validated working set;
- multiple or incomplete roots continue to preserve semantics safely with fixed
  metrics rather than guessing;
- recompute rendering through the existing selector so byte accounting/order/
  marker remain deterministic;
- use the existing endpoint-specific idempotent injector; exact repeated content
  is idempotent, while conflicting/malformed markers fail closed;
- do not bypass image policy, JSON bounds, route selection, header stripping, or
  upstream error/stream behavior;
- compiler calls must be zero on pure rehydration requests unless new root
  content is observed.

### C. Observability/configuration/docs

Add finite configuration for rehydration TTL/entry/total bounds and safe metrics
for populated, hit, stale/expired, isolated miss, injected, skipped, and failure
states by endpoint/route. Labels remain bounded and free of paths/hashes/content.
Update README/config/architecture documentation to distinguish simulated/new-
context rehydration from actual Codex compaction E2E, which remains objective
004. Update `oap/COMPLETENESS.md`: objective 003 becomes 100%, overall branch
readiness approximately 74%; explicitly move remaining evidence responsibility
to objective 004 and preserve text-only/no-production limitations.

## Explicit non-goals

No client filesystem/network access; no recursive acquisition; no persistent
cross-process/session database; no signed gateway identity; no admin endpoints;
no service/profile/model/network changes; no real Codex execution; no vision or
production claims; no rewrite of prior OAP artifacts/history.

## Acceptance criteria

1. First governed request populates validated rehydration state only after
   successful injection.
2. A subsequent zero-root request from the same identity/model/policy receives
   equivalent stable constitution injection with zero compiler calls.
3. Different principal/session/repository/route/model/schema/version/bound does
   not cross-hit.
4. TTL expiry, LRU/total-byte pressure, corruption/invalid type, and process
   restart produce safe misses without governance deletion or unsafe reuse.
5. New observed root replaces state; multiple/incomplete roots and disabled/
   spoofed-header requests preserve existing behavior.
6. Responses and Chat injection remain idempotent; conflicts fail closed;
   images/tools/SSE/errors/disconnect behavior remains preserved.
7. Metrics contain only bounded states/counts/timings and focused scans prove no
   raw content leakage.
8. Documentation/completeness reflect tested scope and remaining objective-004
   work honestly.

## Required verification

Run exact statuses for:

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
git diff --check 68f212b5ad316b95fa12ef632e1538b56479081b...HEAD
```

Add focused fake-upstream tests for population, zero-root rehydration, isolation,
TTL/LRU/restart, replacement, conflict, privacy, and proxy preservation. Bounded
live test must use temporary adapter on loopback 18031: first synthetic-root
request, then compacted/zero-root request, proving compiler-call count does not
increase and injected context remains present; stop the temporary process. Live
image remains SKIPPED due verified zero-image capability. Include secret/raw scan,
scoped diff audit, completeness check, and protected-host before/after snapshot.

## Publication contract

Push amendments to exact PR #5 branch; never create another PR or merge. Record
literal implementation head after all non-report work is remote. Atomically
publish exactly one immutable `oap/reports/003-e-compaction-rehydration.md`;
SELF must be sole final commit, parent equals implementation head, change only
that report, and be remote PR head before response FIFO `OK`. Label every
criterion/command with exact status and never rewrite prior artifacts.

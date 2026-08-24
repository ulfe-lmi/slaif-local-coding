# OAP Work Order — 004-w

## Objective

Amend objective-004 PR #6 with a focused production security/privacy/
observability hardening review of the implemented adapter, constitution
pipeline, compiler/cache, and streaming proxy. Fix only concrete defects found,
add negative regression evidence, and preserve all accepted 004-s governed E2E
behavior. Do not revisit Codex sandbox/compaction diagnostics or expand into
gateway/systemd/vision work.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`
- Numeric objective / round: `004` / `004-w`
- PR mode: `AMEND_EXISTING_PR`
- Existing PR: #6, `https://github.com/ulfe-lmi/slaif-local-coding/pull/6`
- Required base: `main` at `7a2c36a0a40958a6059a765c2f9d5e5bf4ddc161`
- Required head: `oap/004-real-codex-governed-e2e`
- Current verified remote head / `004-v` SELF:
  `894c730e6d22371ed7f8d087769c0237871ee085`
- Prior implementation SHA:
  `4a1d5982520eb75bac6c8b6158c64e03a8348b8f`, verified sole parent of SELF.
- PR state: OPEN/non-draft/MERGEABLE-CLEAN; final report-head `test` SUCCESS.
- Required action: **NO NEW PR**; no coding merge/auto-merge.

## Strategic context

Accepted evidence now includes faithful proxy/image behavior, bounded compiler/
cache/injection/rehydration unit and fake-upstream coverage, and successful
two-invocation global-yolo governed E2E with exact dependency bytes, sentinel,
cache reuse, and compiler suppression. Objective 004 remains 40% because actual
compaction and vision are unproven and security/operations gaps remain.

This round must review production code and installed artifacts, not inflate the
repository-only E2E diagnostics. Existing tests/green CI are evidence inputs,
not proof that no defect exists.

## Bounded threat and failure review

Inspect the complete PR production diff and current effective configuration
against `AGENTS.md`, `ARCHITECTURE-for-agents.md`, `SECURITY.md`, and
`TESTING.md`. Produce a fixed findings matrix with `PASS | DEFECT_FIXED |
BLOCKED | NOT_APPLICABLE`, concrete code/test evidence, and no raw secrets/data.

### A. Request/auth/header boundaries

- external caller cannot spoof trusted principal/session/route/request ID or
  internal compiler-bypass state;
- service auth forwarding/stripping is exact; no raw external key enters cache
  identity, metrics, logs, or sanitized errors;
- hop-by-hop plus `Connection`-named headers are stripped both directions;
- query strings/private URLs and auth/cookies are not labels/log output;
- unknown route/policy/capability fails startup/readiness or request closed,
  never guesses.

### B. Content/privacy/error boundaries

- no raw prompt/source/code/tool output/image/request/response/model/compiler
  prose is logged, persisted, returned in diagnostics, metrics, or exceptions;
- raw-source persistence remains off by default; temporary/cache modes and
  ownership are enforced without symlink/traversal/unsafe deletion;
- malformed/oversized/deep JSON and unknown over-limit image shapes fail
  deterministically without unsafe passthrough;
- upstream/validation/compiler/cache errors are sanitized and do not echo
  bodies, credentials, internal paths, or private endpoints.

### C. Compiler/cache/governance isolation

- compiler calls remain direct, authenticated, tool-free, text-only,
  non-recursive, max-one-concurrent, bounded in source/prompt/output/time;
- invalid/time-out/transport compiler results never cache as valid and never
  silently delete governance-bearing request semantics;
- deterministic candidates cannot be erased by model ranking;
- cache/rehydration identity includes every principal/session/repository/source/
  model/schema/policy/version dimension and never crosses tenants;
- missing identity disables unsafe cross-request reuse;
- TTL/LRU/bytes/pinned budgets, atomic writes, integrity, permissions, and
  restart scans remain bounded and fail safely.

### D. Streaming/resource/operational observability

- HTTPX/ASGI path does not buffer full SSE responses; order/status/errors/usage/
  tool events remain faithful;
- downstream disconnect cancels/closes upstream and does not leak task/socket;
- connect/read/write/pool timeouts, backpressure, body limits, JSON depth, and
  compiler saturation are explicit and bounded;
- no duplicate model process, torch/image decode, or unbounded thread/process/
  retry behavior exists;
- metrics labels are fixed low-cardinality values and expose counts/timings/
  states only; `/metrics` remains private by deployment contract;
- health/readiness accurately distinguish process health, config validity,
  cache degradation, and upstream availability without leaking internals.

## Fix authority and constraints

Implement minimal typed production/test/doc fixes only for direct findings in
the matrix. Do not refactor unrelated code, add dependencies, weaken validation,
broaden support/readiness claims, or modify repo-only Codex diagnostics except
to keep tests compiling after a directly related contract change.

No protected host/service/profile mutation. Primary verification is pure/fake
upstream. One bounded candidate-on-18031 live health/readiness/text/tool/stream/
disconnect smoke may run only if needed to validate a concrete production fix;
otherwise label live calls NOT RUN (not required). Never rerun compaction,
workspace, bubblewrap, or vision tests.

## Acceptance criteria

1. A complete fixed findings matrix covers every A-D item with concrete source/
   test evidence and strongest remaining risk.
2. Every discovered in-scope defect is minimally fixed with negative regression
   coverage; no known critical/high defect is deferred silently.
3. Secret/raw/private-path static and runtime-log/metric/error scans pass using
   synthetic canaries without reporting the canaries.
4. Header spoofing, identity isolation, compiler recursion/failure, cache
   permissions/bounds, malformed inputs, streaming disconnect/cancellation, and
   metric-cardinality negative tests pass.
5. Installed wheel contains production code only; repo E2E helpers remain
   non-runtime; dependency/lock changes are absent unless separately justified
   and approved by the order (none expected).
6. Docs/security/testing/configuration claims match actual behavior and retain
   text-only/yolo-E2E/compaction/vision/systemd limitations.
7. Protected state remains unchanged; exact local gates and implementation/
   report-head CI pass.

## Required verification

Record lock check, frozen sync, Ruff check/format, mypy, focused security/
privacy/proxy/compiler/cache/disconnect tests, full pytest, build, wheel/sdist
inspection, compileall, shell syntax, diff check; fixed findings matrix; secret/
raw/private-path scans; synthetic canary absence from captured logs/errors/
metrics; header/auth/cache-identity/recursion/bounds/cancellation evidence;
dependency and scoped-diff audits; protected-host before/after snapshot; and
current GitHub checks. Wait for final report-head CI.

## Completeness and non-goals

Keep objective 004 at 40% / branch ~79% pending strategic review. On full
hardening success, strategy may raise objective 004 to 60% / branch ~83%; coding
leaves percentages unchanged. Remaining gaps remain compaction, vision-capable
E2E, and systemd candidate proof.

No gateway, signed multi-user release, service installation/cutover, compaction,
vision, sandbox, model, or protected-host work. No production/compliance/security
certification claim.

## Publication contract

Push amendments to exact PR #6 branch; never create another PR or merge. Record
literal implementation head after all non-report work is remote. Atomically
publish exactly one immutable
`oap/reports/004-w-security-observability-hardening-review.md`; SELF must be the
sole final commit, its first parent must equal the implementation head, it must
change only that report, and it must be remote PR head before response FIFO
`OK`.

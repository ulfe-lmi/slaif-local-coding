# OAP Work Order — 003-a

## Objective

Begin objective 003 with a bounded, library-only working-set selector and
API-valid idempotent injection contract for Responses and Chat Completions.
Transform validated compiled indexes into a stable, byte-bounded reconstructed
constitution block and insert it without mutating any other request semantics.

Public request handlers must remain disabled from compiler/cache/injection
integration in this round. This creates the tested foundation for a later
`003-b` request-pipeline slice; it does not implement acquisition, compaction
rehydration, gateway identity, or cutover.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`
- Numeric objective / round: `003` / `003-a`
- PR mode: `CREATE_NEW_PR`
- Existing objective PR: N/A
- Required base: `main`
- Verified starting base SHA:
  `867ed55e7d115d960c666380ebbc5952d43d97d1`
- Required head branch: `oap/003-working-set-injection-foundation`
- Required action: create exactly one new non-draft PR; coding never merges or
  enables auto-merge.

Post-merge state independently verified before activation:

```text
objective 002 PR #3: MERGED
remote main: 867ed55e7d115d960c666380ebbc5952d43d97d1
main tree equals accepted PR head tree: yes
open PRs: none
```

Start from authoritative remote `main`. Reconcile immediately before mutation.
Preserve all prior OAP orders/reports/history.

## Independently verified runtime context

```text
host/user: hinton1 / janezp
protected vLLM: PID 26028 on 0.0.0.0:18020
user qwen-serving.service: active/running since Sat 2026-08-22 05:35:46 CEST
qwen-serving-vision.service: inactive/dead
current model capability: text-only / zero-image, as established in objective 002
ports 18021 and 18031: free
preferred upstream: http://127.0.0.1:18020/v1
```

No live model call is required by this library-contract round. Protected-host
access is read-only reconnaissance only; do not mutate any protected service,
profile, network, key, model, systemd, firewall, or VPN state.

## Bounded scope

### A. Typed working-set selection

Add a strict, versioned selector under the constitution package, such as
`working_set.py`, plus models as needed. Input must be an already validated
root `CompiledIndex`, optional acquired dependency indexes keyed by their exact
safe logical paths, explicit policy/budget, and stable metadata. The selector
must never read files, browse repositories, call models, access cache internals,
or perform network I/O.

Deterministic output must include:

- bounded reconstructed constitution summary/rules;
- role, authority, source-of-truth, ordering, exception, and reread fields;
- root source logical path/hash/version;
- each root dependency classified as `included`, `missing`, or `omitted`;
- missing P1 acquisition instructions containing exact repository-relative paths
  and urgency, without pretending content was available;
- explicit marker that this is reconstructed context and authoritative sources
  override it;
- selector/schema/render versions and a deterministic content hash of rendered
  text;
- bounded status/reasons suitable for metrics—never raw source/model output.

Ordering must be stable and explicit:

1. P0 root constitution first;
2. acquired P1 dependencies next, ordered by path then source hash;
3. missing P1 acquisition list, ordered by urgency rank then path;
4. acquired P2/P3 if budget permits, ordered by constitutional priority
   descending, then path, then source hash;
5. omit P4 rather than exceed budget.

Hard rules:

- measure and enforce rendered bytes as UTF-8 against a finite configured cap;
- omit whole lowest-priority optional entries deterministically when needed;
- never truncate normative text silently;
- if the essential P0 block cannot fit, return a typed failure rather than an
  unsafe partial law;
- preserve independent reference confidence and constitutional priority;
- never invent paths or silently erase known dependencies;
- expose no cache mechanics, cache keys, timestamps, credentials, raw source,
  prompts, images, or tool output in model-visible text.

### B. Pure idempotent injection transforms

Add separate, explicitly endpoint-scoped transforms for:

```text
POST /v1/responses
POST /v1/chat/completions
```

Requirements:

- Chat Completions receives one stable system instruction inserted at the
  earliest valid position without changing existing message order or content.
- Responses uses its stable top-level instructions location. Preserve existing
  instructions; if present, combine deterministically rather than overwrite.
- Use a versioned marker that clearly identifies reconstructed context and says
  repository/Git/GitHub/source authority overrides it.
- Detect the same marker/version/content idempotently and leave the payload
  semantically unchanged.
- A conflicting/duplicate/malformed marker fails closed with a typed error; no
  second injection and no silent replacement.
- Reject unsupported payload shapes, non-string existing Responses instructions,
  and ambiguous Chat structures without upstream forwarding.
- Preserve all unrelated fields, tools, metadata, message/item order, usage
  controls, and supported envelope values.
- Prove zero-image transformation for payloads containing zero or multiple
  supported image items; this module must never touch images.
- Return safe counts only: endpoint, insertion/update/idempotent outcome, rendered
  bytes, included/missing/omitted dependency counts. Never log or expose rendered
  raw source-derived customer content outside the intentionally transformed
  request object.

### C. Disabled public integration contract

Extend validated configuration for selector/render versions and finite working-
set/acquisition bounds while retaining:

```toml
[constitution]
enabled = false
```

The literal public-handler type/configuration constraint must remain false-only.
Add or retain a regression proving normal governed requests make zero compiler,
cache-write, selector, and injection calls. Document that this is objective
`003-a` foundation behavior, not end-to-end constitution virtualization.

### D. Documentation

Update README/architecture/configuration documentation to describe the new
contracts, deterministic ordering, budget/failure semantics, idempotence,
privacy boundary, and explicit current exclusions. Keep release language limited
to tested library behavior; do not claim compaction compliance, production
multi-user safety, vision readiness, or Codex E2E support.

## Explicit non-goals

Do not:

- wire selector/injection into public request handlers or enable compilation;
- read client filesystems or acquire referenced files;
- implement incremental acquisition from tool outputs or compaction recovery;
- add cache purge/admin/public endpoints;
- introduce signed multi-user identity or gateway integration;
- alter image policy, proxy fidelity, compiler validation, cache trust, or
  dependency versions except where required by typed configuration additions;
- start persistent services or make live model calls;
- mutate port 18020, either qwen unit, vLLM flags/model/checkpoint/venv/patches/
  launch flags/systemd/API-key files/firewall/VPN/network bindings, or active
  Codex profiles;
- edit prior OAP artifacts/history or claim current vision capability.

## Acceptance criteria

### Criterion A — deterministic working set

Given synthetic P0 root and P1–P4 dependency indexes, output ordering, statuses,
confidence/priority separation, acquisition instructions, versions, hashes, and
source-authority marker are deterministic across repeated runs.

### Criterion B — bounded fail-safe selection

Tests prove UTF-8 byte accounting, optional omission in stable order, missing-P1
instructions, essential-overflow typed failure, prohibition of silent truncation,
and no model-visible cache mechanics/raw content.

### Criterion C — idempotent API-specific injection

Responses and Chat tests prove stable insertion, preservation of unrelated
envelope/order/content, repeated-injection idempotence, conflicting-marker fail-
closed behavior, unsupported-shape rejection, and unchanged image items/counts.

### Criterion D — public handlers remain inert

Validated configuration accepts only disabled constitution integration. A normal
governed request causes zero compiler/cache/selector/injection invocations and
continues to preserve existing proxy/image/observation behavior.

### Criterion E — quality/documentation

All local gates and final-head CI pass. Docs accurately distinguish implemented
contracts from future pipeline integration, acquisition, rehydration, real Codex
E2E, production identity, gateway integration, and cutover.

## Required verification and evidence

Run and report exact statuses:

```bash
uv lock --check
uv sync --frozen --extra dev
uv run --frozen ruff check .
uv run --frozen ruff format --check .
uv run --frozen mypy src tests
uv run --frozen pytest -q
uv build
python3 -m compileall -q src tests oap/bin
bash -n oap/bin/*.sh
git diff --check 867ed55e7d115d960c666380ebbc5952d43d97d1...HEAD
```

Include focused selector/injection tests and the public zero-invocation
regression. Because no runtime request integration or live-model code path is
added, live model calls are `NOT RUN (not required by 003-a)`, not skipped passes.
Perform a secret/raw-content scan of the diff and protected-host before/after
read-only snapshot. Wait for final report-head GitHub CI; pending/failed/
cancelled/missing checks block acceptance.

## Security, privacy, resource constraints

Use synthetic indexes/fixtures only. Never commit/print raw prompts, repository
source, images, tool output, response bodies, cookies, bearer tokens, API keys,
or customer data. Render only derived bounded summaries/rules/instructions.
Bound bytes, entries, depth, and processing. Adapter/compiler remain CPU-only.
No raw-content logging or persistence.

## Publication and immutable report contract

Create fresh branch `oap/003-working-set-injection-foundation` from remote main
SHA `867ed55e7d115d960c666380ebbc5952d43d97d1`.

Before report, commit only intended implementation/config/doc/test paths plus
exact activated order and `oap/active`; push implementation work; create exactly
one non-draft PR titled
`[OAP 003] Add working-set and injection contracts`; verify PR number/URL/base/
head/changed paths; inspect/repair in-scope CI; record literal implementation
head only after all non-report work is remote.

Then atomically publish exactly one immutable
`oap/reports/003-a-working-set-and-injection-contracts.md`. Its publication
commit (`SELF`) must be sole final round commit, have literal implementation head
as first parent, change only that report path, and be pushed as remote PR head
before sending response FIFO `OK`. Map every criterion to concrete evidence using
exact status labels, include sanitized protected-host evidence, and never rewrite
prior artifacts after signaling.

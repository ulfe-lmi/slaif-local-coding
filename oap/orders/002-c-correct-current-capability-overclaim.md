# OAP Work Order — 002-c

## Objective

Amend objective-002 PR #3 only to remove the remaining current-service vision
overclaim from active architecture documentation and add a focused regression
guard. This is a documentation/test-only continuation; change no runtime code,
configuration behavior, protected service, or prior OAP history.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`
- Numeric objective / round: `002` / `002-c`
- PR mode: `AMEND_EXISTING_PR`
- Existing PR: #3, `https://github.com/ulfe-lmi/slaif-local-coding/pull/3`
- Existing PR canonical URL: `https://github.com/ulfe-lmi/slaif-local-coding/pull/3`
- Required base: `main`
- Verified base SHA: `176bf4d839ae9fa32d0cc3c4279a1b96220c1c61`
- Required head: `oap/002-constitutional-compiler-cache`
- Current verified remote head / `002-b` report SELF:
  `fc1b1cffd1f1a7d16976ba19f97952b15ddd703f`
- Prior implementation SHA:
  `9192dea62dccdb76801733b958a8bfd5e3f3c63c`; verified sole first parent of the
  `002-b` SELF
- `002-b` report commit changes only its exact report path; remote/local blob
  SHA is `d7ab0849723df7a6723d18e79988f06508baa222`
- PR state: OPEN, non-draft, correct base/head, MERGEABLE/CLEAN; current-head
  `CI` / `test` SUCCESS
- Required action: **NO NEW PR**; no coding merge/auto-merge.

Preserve every prior order/report byte and reconcile remote state before
mutation.

## Independently reproduced gap

Active `ARCHITECTURE.md`, in the “Protected live system under test” topology,
currently says:

```text
Qwen/vLLM vision service
```

This contradicts the same PR’s corrected facts: the current `hinton1` service is
language-model-only/text-only and declared zero-image capability. README and
live-environment docs are correct. The report claim that no active vision-service
overclaim remains is therefore not currently true. Historical references to the
prior vision deployment elsewhere are valid and must remain.

## Bounded scope

1. In active `ARCHITECTURE.md`, replace the current-topology label with
   `Qwen/vLLM text-only service` or equivalent wording that unambiguously
   describes the currently verified fixture.
2. Preserve nearby historical statements about the prior vision deployment where
   they are explicitly historical.
3. Extend focused configuration/documentation regression coverage to assert:
   - the exact current-topology overclaim
     `Qwen/vLLM vision service` is absent from active `ARCHITECTURE.md`;
   - an explicit current `text-only` fact remains present;
   - optional LAN `.75` and historical `.76` distinctions remain represented by
     existing tests/documentation.
4. Make no unrelated refactor, prose rewrite, dependency change, runtime change,
   configuration semantic change, or OAP history rewrite.

## Explicit non-goals

Do not mutate vLLM/qwen-serving, model flags, systemd units, API keys, network
bindings, firewall/VPN, Codex profiles, either OAP route, or any protected host
state. Do not enable compiler request integration or alter cache/compiler
runtime behavior. Do not edit merged orders/reports/history. Do not claim current
vision support or production readiness.

## Acceptance criteria

### Criterion A — corrected active architecture

The active architecture current-topology block identifies the protected system as
text-only and does not contain the exact overclaim
`Qwen/vLLM vision service`. Historical vision statements remain clearly scoped as
prior deployment/provenance.

### Criterion B — regression guard

Focused tests fail if the exact current-topology vision overclaim returns and pass
with the corrected text-only wording plus retained migration distinctions.

### Criterion C — unchanged runtime behavior

The implementation diff for this round contains only active architecture
documentation and focused test guard changes. No source/config/runtime behavior
changes are present relative to
`9192dea62dccdb76801733b958a8bfd5e3f3c63c`.

### Criterion D — cumulative objective evidence

All static/unit/fake/build gates and final-head GitHub CI pass. The `002-b`
current live compiler/cache and text/tool/stream/multiturn evidence remains valid
because this round changes no runtime code. Its live image case remains honestly
skipped due to the independently verified zero-image current fixture; it is not
counted as a vision pass.

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
git diff --check 176bf4d839ae9fa32d0cc3c4279a1b96220c1c61...HEAD
```

Run the focused documentation/configuration regression explicitly and include
its command/status. Because this round is documentation/test-only, do not rerun
live model calls; label them `NOT RUN (not required; runtime unchanged)` while
citing the immutable `002-b` live evidence for cumulative behavior. Wait for
final report-head CI; pending/failed/cancelled/missing checks block acceptance.

Perform a secret/raw-content scan of this round’s diff and a protected-host
read-only before/after snapshot sufficient to show PID 26028, user
`qwen-serving.service`, listener `0.0.0.0:18020`, inactive vision unit, and free
18021/18031 remained unchanged. Do not print secrets.

## Publication and immutable report contract

Push only intended paths to exact branch
`oap/002-constitutional-compiler-cache`, verify PR #3 advances, inspect/repair
in-scope CI, then record literal implementation head after all non-report work is
remote.

Atomically publish exactly one new immutable
`oap/reports/002-c-correct-current-capability-overclaim.md`. Its publication
commit (`SELF`) must be sole final round commit, have literal implementation head
as first parent, change only that report path, and be pushed as remote PR head
before response FIFO `OK`. Report every criterion and command with exact status
labels; never rewrite prior artifacts.

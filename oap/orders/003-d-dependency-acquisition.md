# OAP Work Order — 003-d

## Objective

Amend objective-003 PR #5 to acquire referenced constitutional dependencies only
when their exact content crosses the API boundary through an evidenced
`input_file` or paired local-tool result. Compile acquired dependencies
incrementally with the existing bounded compiler/cache, include them in working-
set selection, and preserve safe behavior for missing, ambiguous, oversized, or
invalid dependencies. Do not implement compaction rehydration.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`
- Numeric objective / round: `003` / `003-d`
- PR mode: `AMEND_EXISTING_PR`
- Existing PR: #5, `https://github.com/ulfe-lmi/slaif-local-coding/pull/5`
- Required base: `main` at `68f212b5ad316b95fa12ef632e1538b56479081b`
- Required head: `oap/003-working-set-injection-foundation`
- Current verified remote head / `003-c` SELF:
  `9c35edc35ed8a911de64eea561066d2cb7a26a25`
- Prior implementation SHA:
  `94ed20371d1693a2e4d415de56d770db03957441`, verified sole parent of SELF
- PR state: OPEN, non-draft, MERGEABLE/CLEAN; implementation and report-head
  `CI` / `test` SUCCESS
- Required action: **NO NEW PR**; no coding merge/auto-merge.

Preserve all prior orders/reports bytes and reconcile remote before mutation.

## Verified context

PR #5 is the human-approved recovery review vehicle for numeric objective 003
and remains intentionally open. It currently contains tested one-root
pipeline integration but lacks dependency acquisition and compaction
rehydration. Protected vLLM remains PID 26028 on `0.0.0.0:18020`; current
fixture is text-only/zero-image; ports 18021/18031 were free.

## Bounded scope

### A. Deterministic dependency observation

Extend request-only observation so a root’s accepted candidate path can match:

- an `input_file` item whose filename exactly equals the repository-relative
  candidate and whose content is a string;
- an exact `exec_command` read call (`cat`, bounded `head -n`, bounded `tail`,
  or bounded `sed -n`) paired one-to-one by call ID with exactly one string
  function/tool output;
- equivalent Responses and Chat Completions pairings already used for roots.

Hard requirements:

- never read filesystem/network/repository; use only content in the request;
- reuse one strict repository-path validator for root and dependency labels;
- reject absolute, Windows, UNC, URL, traversal, ambiguous, control-character,
  overlong, and unsupported paths without acquisition;
- require exact candidate-path equality, unique unambiguous pairing, valid
  roles/types, and bounded UTF-8 content;
- hash exact bytes and retain provenance/location only in request memory;
- do not place raw source or hashes in logs/metrics/public observation JSON;
- duplicate, malformed, mismatched, extra, or unsafe dependency evidence yields
  “not acquired” plus a fixed safe reason—not silent acceptance.

### B. Incremental compilation and selection

After successful one-root root compilation:

1. identify root-declared dependency paths whose exact content was observed in
   the same request;
2. compile at most a configured finite number per request (default four,
   hard maximum 16), using existing direct compiler/cache contracts;
3. derive each dependency’s own deterministic candidate list from its observed
   text, but do not recursively fetch newly discovered files in this round;
4. accept an acquired index only when source path/hash/length match, schema is
   valid, candidate set is exact, scores are independent, and cache rules pass;
5. pass only validated indexes to `select_working_set` under exact declared
   paths;
6. keep missing/invalid dependencies as acquisition instructions; never omit
   essential law silently or block the ordinary request for optional failure;
7. preserve one global compiler slot, deduplication, timeout, cancellation,
   static identity isolation, and all existing cache bounds/versioning.

A root with no observed dependencies must behave exactly as `003-b`.

### C. Safe metrics and configuration

Add finite configuration for maximum per-request dependency acquisitions.
Expose only bounded counters/timings/states such as observed, acquired, cache
hit/miss, rejected/invalid/too-large, and selection inclusion counts. Never log
paths/content/hashes/identity/body/output. Update README/configuration docs and
keep explicit exclusions: no client filesystem access, no recursion/fetching,
no compaction rehydration, no signed multi-user identity, no cutover.

### D. Completeness update

Update `oap/COMPLETENESS.md` factual evidence/completion fields only: objective
003 moves from 60% to 75% because acquisition is implemented and tested; overall
branch readiness becomes approximately 68%. Compaction rehydration remains
explicitly missing. Do not claim production/vision/Codex E2E readiness.

## Explicit non-goals

No client filesystem/network access; no recursive acquisition; no arbitrary
tool-output ingestion; no compaction/new-context rehydration; no signed gateway
identity; no public admin endpoints; no service/model/profile/network mutation;
no change to image policy or proxy fidelity; no rewrite of prior OAP artifacts.

## Acceptance criteria

1. Fake-upstream test proves root + observed P1 dependency produces two compiler
   operations on first request, validated dependency inclusion in injected
   context, then persistent cache reuse on identical repeat.
2. Both `input_file` and paired Responses/Chat tool-result acquisition paths are
   covered with deterministic ordering and exact path matching.
3. Unsafe/ambiguous/duplicate/mismatched/oversized/invalid dependency evidence
   is not acquired; root governance is still injected safely with missing-P1
   instruction and fixed metrics.
4. Acquisition count/budget limits, independent confidence/priority, versioned
   isolation, cancellation/slot release, and no-cross-identity cache behavior
   are tested.
5. Zero-dependency `003-b` behavior remains unchanged; image policy, tools,
   SSE/stream choice, errors, and unrelated envelope fields remain preserved.
6. Documentation and completeness table reflect tested behavior and remaining
   gaps without overclaim.
7. All required local gates and current implementation/report-head GitHub CI
   pass.

## Verification

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
git diff --check 68f212b5ad316b95fa12ef632e1538b56479081b...HEAD
```

Add focused dependency observation/acquisition/isolation/failure tests. Bounded
live testing must exercise one synthetic root + one observed dependency miss and
identical hit through temporary loopback adapter 18031, then stop it. Live image
remains SKIPPED due verified zero-image capability. Include secret/raw-content
scan, scoped diff audit, and protected-host before/after snapshot.

## Publication contract

Push to exact PR #5 branch; never create another PR or merge. Before report,
push all non-report work and record literal implementation head. Atomically
publish exactly one immutable
`oap/reports/003-d-dependency-acquisition.md` whose SELF is sole final commit,
has literal implementation head as first parent, changes only that report, and
is pushed as PR head before response FIFO `OK`. Label every criterion/command
with exact status and never rewrite prior artifacts.

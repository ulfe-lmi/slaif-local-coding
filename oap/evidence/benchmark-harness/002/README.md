# Corrected dual-lane benchmark harness — archive 002

## Status

**PRELIMINARY DIAGNOSTIC RESULTS FROM A FAILED/INCOMPLETE QUALIFICATION.**

This directory preserves the public-safe source and evidence for the corrected
GPU2/GPU3 qualification conducted on 2026-09-29 through 2026-09-30. It is
intended to let the benchmark and product maintainers reproduce the harness
logic, inspect the observed failures, and design a successor.

It is not a qualified harness, benchmark freeze, pilot, main result, product
acceptance, release artifact, or authorization to dispatch more runs. The
qualification verdict is false. No formal pilot, main, or extension run
occurred.

Archive 001 remains the immutable source record for the human-invalidated
single-lane harness; its outcomes remain unpublished. Archive 002 neither
rewrites nor relabels archive 001.

## Start here

1. Read [`PROBLEM-INDEX.md`](PROBLEM-INDEX.md) for the failures and unresolved
   questions that need engineering attention.
2. Read [`QUALIFICATION-AUDIT.md`](QUALIFICATION-AUDIT.md) for the complete
   qualification verdict and accounting boundary.
3. Inspect [`PRELIMINARY-RESULTS.csv`](PRELIMINARY-RESULTS.csv),
   [`PARTIAL-CHECK-SCORES.md`](PARTIAL-CHECK-SCORES.md), and
   [`JUDGE-CHECKS.csv`](JUDGE-CHECKS.csv) for every attempted workload and its
   independent-judge outcome.
4. Read [`CONTEXT-FAILURE.md`](CONTEXT-FAILURE.md) before diagnosing the
   long-context failures. They are not established context-window overflows.
5. Read [`TOKEN-SCORE-CORRELATION.md`](TOKEN-SCORE-CORRELATION.md) and
   [`TELEMETRY-SUMMARY.md`](TELEMETRY-SUMMARY.md) for resource accounting and
   its limitations.
6. Extract `harness.tar.gz`, verify it with `HARNESS-CONTENTS.sha256`, then run
   its offline suite. The archive exposes task seeds and answer material for
   diagnosis, so those tasks are no longer suitable as hidden evaluation data.

Example integrity check from this directory:

```bash
archive_dir="$PWD"
tmpdir="$(mktemp -d)"
tar -xzf harness.tar.gz -C "$tmpdir"
(cd "$tmpdir" && sha256sum -c "$archive_dir/HARNESS-CONTENTS.sha256")
```

## Contents

- [`harness.tar.gz`](harness.tar.gz) — deterministic sanitized snapshot of the
  corrected benchmark harness, including tasks, judges, schedules, schemas,
  protocol documents, and regression tests.
- [`HARNESS-CONTENTS.sha256`](HARNESS-CONTENTS.sha256) — hashes for the 110
  files in the extracted `harness/` tree.
- [`qwen-neumann-models.json`](qwen-neumann-models.json) — verbatim
  human-supplied Codex model catalog used to correct worker metadata.
- [`SOURCE-IDENTITY.md`](SOURCE-IDENTITY.md) — source, client, worker, and
  product identities and the attempt/source chronology.
- [`PRELIMINARY-RESULTS.csv`](PRELIMINARY-RESULTS.csv) — one row for each of the
  14 corrected-candidate workload attempts.
- [`JUDGE-CHECKS.csv`](JUDGE-CHECKS.csv) — every independent functional check,
  without answer values or subject content.
- [`JUDGE-CONTROLS.csv`](JUDGE-CONTROLS.csv) — content-free outcomes for the
  six known-correct and deliberately defective judge controls.
- [`PARTIAL-CHECK-SCORES.md`](PARTIAL-CHECK-SCORES.md) — descriptive component
  scores and their scientific limitations.
- [`TOKEN-SCORE-CORRELATION.md`](TOKEN-SCORE-CORRELATION.md) — per-attempt
  backend token use, wall time, preliminary score, and provisional energy.
- [`TOKENS-PER-PASSED-CHECK.md`](TOKENS-PER-PASSED-CHECK.md) — the requested
  prompt/generated-token ratio orderings, with their scoring limitations.
- [`ADAPTER-MECHANISMS.csv`](ADAPTER-MECHANISMS.csv) — content-free per-attempt
  image/governance/cache/rehydration counters where an adapter was used.
- [`CONTEXT-FAILURE.md`](CONTEXT-FAILURE.md) — focused long-context diagnosis.
- [`TELEMETRY-SUMMARY.md`](TELEMETRY-SUMMARY.md) — recorder coverage,
  attribution, cadence, and clock limitations.
- [`QUALIFICATION-AUDIT.md`](QUALIFICATION-AUDIT.md) — final qualification
  checklist and attempt accounting.
- [`REDACTIONS.md`](REDACTIONS.md) — exact public-export boundary.
- [`MANIFEST.sha256`](MANIFEST.sha256) — hashes for every committed file here
  except the manifest itself.

## Headline findings

- 14 workload attempts: 8 `SUBMITTED`, 6 `SUBJECT_ERROR`.
- 14/14 measurements were valid and drained; there were no hidden retries.
- Independent functional success: 1/14.
- Web: one 8/8 pass and four 6/8 failures.
- Web DIRECT terminated when accumulated history exceeded the backend's
  16-image request limit; the direct arm intentionally had no image-history
  workaround.
- Terminal: no pass; two 4/5 and three 1/5 results.
- Context: all four conditions ended before the final 16-fact query; all scored
  0/16. `BOTH` emitted one typed structural compaction and advanced one
  invocation farther than the other conditions.
- All-attempt backend use: 78,622,898 prompt and 1,792,720 generated tokens
  across 792 completed requests. Client and backend totals overlap and are not
  added.
- Qualification remains false on context-sequence completion, accepted
  shared-host interference criteria, and independent recorder/VM clock
  alignment.

These are preliminary diagnostic observations with very small, unbalanced
cells. They are not treatment-effect estimates.

## Private evidence boundary

Raw Codex events, prompts, responses, tool output, rollout databases, subject
workspaces, screenshots, adapter logs, backend credentials, endpoint addresses,
physical GPU UUIDs, PIDs, and raw host telemetry are deliberately absent. A
separate private handoff was preserved for authorized maintainers. This public
archive is sufficient to audit the harness and content-free outcomes, but it
cannot independently reconstruct private subject content.

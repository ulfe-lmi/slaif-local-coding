# Invalidated independent benchmark harness — archive 001

## Status

**INVALIDATED AND CANCELLED BY HUMAN AUTHORITY.**

This directory preserves the complete nonsecret harness source and a sanitized
testing trail for the independent SLAIF benchmark harness that ran on
2026-09-28 through 2026-09-29. It is historical evidence only. It is not a
qualified harness, freeze, pilot, main result, release artifact, or authorization
to resume experiments.

The source archive includes explicitly identified post-invalidation repair
changes requested by the human owner. Those changes were not used by any
preserved attempt and have not been empirically qualified. See
[`POST-INVALIDATION-CHANGES.md`](POST-INVALIDATION-CHANGES.md).

The human instruction at cancellation was:

> cancel all tasks, this harness is declared invalid

No formal pilot, main, or extension run occurred. No benchmark freeze or stage
approval was created.

## Contents

- [`harness.tar.gz`](harness.tar.gz) — deterministic archive containing the
  complete executable nonsecret source, task seeds, judges, schemas, scripts,
  tests, protocol documents, historical package manifest, and identified
  post-invalidation repair changes; invalid-harness result artifacts are excluded
- [`HARNESS-CONTENTS.sha256`](HARNESS-CONTENTS.sha256) — per-file hashes for the
  files inside the extracted `harness/` tree
- [`qwen-neumann-models.json`](qwen-neumann-models.json) — verbatim Codex model
  catalog supplied by the human after cancellation and installed by the repair
  candidate into every fresh worker home
- [`subject-config.reference.toml`](subject-config.reference.toml) — safe adapted
  reference for the human-supplied Codex TOML; the real credential remains an
  environment variable and the operational URL is rendered per condition
- [`POST-INVALIDATION-CHANGES.md`](POST-INVALIDATION-CHANGES.md) — chronology
  separating the configuration used by the invalid attempts from later repairs
- [`TESTING-PROCEDURE.md`](TESTING-PROCEDURE.md) — result-free chronology of
  setup, checks, workload execution procedure, discovered methodological defects,
  and cancellation
- [`REDACTIONS.md`](REDACTIONS.md) — exact public-copy exclusions and replacements
- [`MANIFEST.sha256`](MANIFEST.sha256) — SHA-256 for every committed file in this
  archive except the manifest itself

## Provenance

- Private source snapshot root: withheld from the public archive
- Private freeze-relevant tree hash before redaction:
  `d3e7e04bcac3f37f0a69f4c9cc6fdf048284e132823ca74c1dbfd7d8be63a151`
- Freeze-relevant file count before redaction: 101
- Execution design: one measured GPU lane; four conditions executed serially
- Subject client: Codex CLI 0.149.0
- Backend model label: `qwen3.8-27b`
- Final tested product candidate: `slaif-local-coding` 0.1.0-rc7
- RC7 source: `ae6271318627703785f42de57d893c9be3b980c9`
- RC7 image digest:
  `sha256:a3782915da58a403fd0f7991c57f9954b07bfb9377e4730715c0fb7398f901db`
- RC7 merged record commit: `d0bf3a47eec6b52b0127f8cac5e483c8c0f5b13c`

RC2 attempts and the RC2 compatibility defect remain part of the chronological
trail and retain their original identity. They were not relabeled as RC7.

## What is excluded

The public repository does not contain backend credentials, GitHub/Docker auth,
private `.local` evidence, raw Codex events, native rollout databases, adapter
logs, subject workspaces, screenshots, host recorder data, private endpoint
addresses, physical GPU UUID, or absolute VM-private paths.

Those exclusions prevent this archive from proving claims that depended on raw
or host-side evidence. Missing observations remain missing; nothing is converted
to zero or pass.

## Publication boundary

Qualification/task outcomes from this invalid harness are intentionally not
published. This archive contains no per-condition status, task score, judge
result, token total, wall time, success/failure table, or preliminary-result
claim. Exact private attempts remain preserved outside the public repository.

## Why the harness was invalidated

The final audit had unresolved methodological defects, including:

1. fresh subject Codex homes received scalar context settings but no frozen
   `model_catalog_json` entry for the custom model, causing fallback metadata;
2. the context workload's four-hour wall bound could stop the sequence before
   the final query and conflicted with a later human instruction not to stop for
   time/tokens;
3. the long-context error path did not preserve the exact upstream rejection
   body needed for a reliable diagnosis;
4. client usage delta-versus-cumulative semantics were not calibrated;
5. native image-view evidence was not reliably extracted from private client
   state;
6. required host-recorder cadence, clock, exclusivity, and shared-host
   contamination evidence was incomplete;
7. cancellation occurred before the planned procedure completed.

The detailed attempt trail remains private under the publication boundary above.

## Safety

Do not use this archive to restart the benchmark. Any successor must create a
new harness/protocol identity, correct the documented defects, rerun complete
qualification, freeze exact inputs, and obtain a new human approval binding the
exact freeze and schedule.

This public archive contains the historical task seeds, judges, rubric, and
context answer key. They are disclosed for audit and defect repair and are no
longer suitable as hidden evaluation material. A successor benchmark must use a
new independently protected task/judge set and must not mount this public archive
or the product repository into a measured subject.

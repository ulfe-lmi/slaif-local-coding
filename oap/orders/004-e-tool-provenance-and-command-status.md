# OAP Work Order — 004-e

## Objective

Amend objective-004 PR #6 to distinguish repository-file bytes from observed
tool-output bytes and require a successful command lifecycle before classifying
a governance-derived sentinel failure. Correct the `004-d` interpretation if the
hash mismatch is expected boundary normalization rather than cache contamination.
Then run at most two fresh, bounded real-Codex diagnostic/sentinel invocations
only after the command-success precondition is observable.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`
- Numeric objective / round: `004` / `004-e`
- PR mode: `AMEND_EXISTING_PR`
- Existing PR: #6, `https://github.com/ulfe-lmi/slaif-local-coding/pull/6`
- Required base: `main` at `7a2c36a0a40958a6059a765c2f9d5e5bf4ddc161`
- Required head: `oap/004-real-codex-governed-e2e`
- Current verified remote head / `004-d` SELF:
  `7d76caca14179d3350ccf703cee7f504096ec530`
- Implementation heads: `e9719b7b809937d79ad7435aba0d0eb0f30fc426`, then
  `9368614090aad1df7f5e05e1aa3f2df11730c662`; SELF parent verified.
- PR state: OPEN/non-draft/MERGEABLE-CLEAN; implementation/report-head CI all
  SUCCESS.
- Required action: **NO NEW PR**; no coding merge/auto-merge.

## Verified diagnostic facts

For one fresh invocation with an initially empty adapter/cache:

```text
repository dependency SHA-256 prefix: 4eae19d4cd72
persisted dependency index source prefix: d636d893e8a9
dependency metric deltas: miss +1, hit +0
command events: started +1, completed +0, failed +1
result: sentinel_missing
```

Adapter validation requires a compiled index source hash to equal the exact
bytes passed by observation. Therefore the mismatch most likely reflects a
difference between on-disk fixture bytes and tool output crossing the API
boundary (such as trailing-newline normalization or tool transformation), not
invalid cache payload storage. Separately, the failed command lifecycle means
sentinel failure cannot yet be attributed to model governance compliance.

## Bounded scope

### A. Provenance distinction

Extend sanitized E2E facts to separately record:

```text
repository dependency SHA-256 and byte length
observed crossing-boundary dependency SHA-256 and byte length
equality and, if unequal, whether bytes differ only by terminal whitespace
cache stored source-hash equality against observed bytes (not disk bytes)
```

Use these facts to correct classifications:

- observed-vs-repository terminal-whitespace difference is
  `tool_boundary_normalization`, not cache contamination;
- different non-whitespace observed bytes require `observation_mismatch`;
- cache stored source must match observed crossing-boundary bytes;
- never expose raw content; hashes, lengths, boolean shape, and fixed reasons are
  sufficient.

### B. Command lifecycle gate

Parse bounded command lifecycle status without retaining command output:

- require evidence of exactly one intended read call;
- distinguish started/completed/failed and capture exit status only as a fixed
  success/failure state;
- if no successful completed read exists, classification is
  `command_failed` or `command_incomplete`, not governance-derived
  `sentinel_missing`;
- do not run a second invocation in the same attempt after a failed command;
  allow at most two fresh attempts total for this round.

### C. Fixture/prompt clarity

You may simplify the delegated dependency to a short single-line directive while
preserving root→dependency acquisition and governance-only sentinel behavior.
The prompt may require reading that exact file and following its final-response
directive, but must not contain/reveal the token. Do not weaken validation or
accept a token from any other channel.

### D. Evidence/docs

Update focused tests and documentation for provenance fields, whitespace
classification, lifecycle gating, and corrected `004-d` interpretation. If a
successful completed command produces the dependency token in the final agent
message, update objective 004 completion from 35% to 40% and branch readiness
from ~78% to ~79%. Otherwise leave values unchanged and report exact fixed
failure reason.

## Explicit non-goals

No raw command/output/content persistence; no cache semantic weakening; no
retry loop beyond two fresh attempts; no forced compaction/vision/gateway/
systemd/production claims; no protected host/model/key/network/systemd/profile
mutation; no rewrite of prior OAP artifacts.

## Acceptance criteria

1. E2E facts distinguish repository bytes from crossing-boundary bytes and
   correctly classify terminal-whitespace normalization.
2. Cache validation compares against observed bytes, not disk bytes.
3. Sentinel classification is gated on a successfully completed ordinary read.
4. At most two fresh live invocations produce exact sanitized outcome evidence.
5. Focused tests prove hash/length/lifecycle classification and privacy.
6. Documentation/completeness reflect the actual result without overclaim.
7. All required local gates and current implementation/report-head CI pass.

## Required verification

Run exact lock/frozen sync/Ruff/check/format/mypy/full pytest/build/
compileall/shell syntax/diff-check gates. Include focused provenance/command
tests, secret/raw scan, scoped diff audit, and protected-host before/after
snapshot. Wait for final report-head CI; missing/pending/failed checks block.

## Publication contract

Push amendments to exact PR #6 branch; never create another PR or merge. Record
literal implementation head after non-report work is remote. Atomically publish
exactly one immutable
`oap/reports/004-e-tool-provenance-and-command-status.md`; SELF must be sole
final commit, parent equals implementation head, change only that report, and be
remote PR head before response FIFO `OK`.

# OAP Work Order — 004-an

## Objective

Record an explicit immutable correction for the malformed implementation SHA in
historical report 004-k without editing that report, then verify every
Objective-004 report commit/parent/path mechanically. This is OAP audit metadata
only: no product, test-helper behavior, acceptance, service, completeness, or
documentation claim change.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`.
- Numeric objective / round: `004` / `004-an`.
- PR mode: `AMEND_EXISTING_PR`; **NO NEW PR**.
- PR #6: `https://github.com/ulfe-lmi/slaif-local-coding/pull/6`.
- Base/head: `main` at `7a2c36a0a40958a6059a765c2f9d5e5bf4ddc161` /
  `oap/004-real-codex-governed-e2e`.
- Current verified remote head / 004-am SELF:
  `ff51b8803942ca042d7812925fd64650de7973e2`.
- 004-am implementation parent:
  `2606de4c8cfc458d564ac8ac76189c706ecfefd6`.
- PR OPEN/non-draft/MERGEABLE/CLEAN; report-head `test` SUCCESS.
- Same PR only; coding never merges or enables auto-merge.

## Exact audit defect

Mechanical review of the 39 current `oap/reports/004-*.md` files found 38
correct literal implementation-SHA/report-parent relationships and one malformed
historical literal:

```text
report: oap/reports/004-k-unship-and-consolidate-e2e-diagnostics.md
report SELF commit: a29f3f97e61ce3bf40de86259798a34cce8db2b8
actual sole parent / implementation commit:
  349a0afda7777870adc79952f9a77201470565b3
malformed literal printed in immutable 004-k report:
  349a0fda7777870adc79952f9a77201470565b3
```

The immutable report omitted one `a` after `349a0`. Its SELF commit changes only
the exact 004-k report path and its actual sole parent is the implementation
commit above. The implementation/report tree itself is intact; the defect is
the literal transcription in report prose.

## Requirements

1. Never edit/rewrite 004-k, its order, its report commit, or any other prior
   immutable order/report.
2. Add one concise non-immutable audit index, `oap/REPORT-CORRECTIONS.md`, that
   records:
   - correction date/round;
   - exact affected report/SELF;
   - malformed literal and corrected actual parent;
   - independent commands/evidence establishing sole parent and report-only
     diff;
   - statement that historical prose remains immutable and the correction does
     not alter implementation, acceptance, or product behavior.
3. Add or run a bounded mechanical verifier over every Objective-004 report:
   - locate exactly one commit adding each report;
   - require that commit changes only that report;
   - parse a literal 40-hex implementation SHA and compare to sole parent;
   - apply the single explicit 004-k correction mapping from the audit index;
   - fail on any other missing/malformed/mismatched/duplicate report mapping.
4. Prefer a one-shot verification command/report evidence; do not add a general
   production dependency or runtime feature. A small repository-only OAP audit
   script/test is allowed only if needed to make the correction mechanically
   durable and bounded.
5. Report exact totals and zero unresolved problems after applying only the
   explicit correction.
6. Do not change completeness, Objective-004 product evidence, current docs,
   tests unrelated to OAP audit, or live fixture state.

## Safety and verification

- No model call or service operation. Human-selected vision remains active;
  text remains inactive; verify read-only.
- No secrets/raw content/customer data.
- Diff limited to exact active/order, correction index, optional bounded OAP
  audit support/test, and final report.
- Run the mechanical audit, Ruff/format/mypy/full pytest/build/compileall/shell/
  diff/precise sensitive scans in proportion to actual files, and require
  current implementation/report-head CI green.

## Publication contract

Push exact active/order and bounded correction metadata/support to the same PR.
Push all non-report work first and record literal SHA. Publish exactly one
immutable `oap/reports/004-an-correct-historical-report-sha-audit.md` with
literal implementation SHA and `Report publication commit: SELF`; SELF changes
only report, parent equals implementation SHA, and is remote head before FIFO
`OK`.

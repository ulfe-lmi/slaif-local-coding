# OAP Report Corrections

This non-immutable index records a transcription correction without changing
any historical OAP report.

## 004-an — 2026-08-24

The sole correction mapping for this audit is:

- Affected report: `oap/reports/004-k-unship-and-consolidate-e2e-diagnostics.md`
- Affected SELF commit: `a29f3f97e61ce3bf40de86259798a34cce8db2b8`
- Malformed implementation SHA literal: `349a0fda7777870adc79952f9a77201470565b3`
- Corrected actual sole parent: `349a0afda7777870adc79952f9a77201470565b3`

Independent evidence for the correction:

- `git show -s --format='%H %P' a29f3f97e61ce3bf40de86259798a34cce8db2b8`
  returns the SELF commit followed by the corrected sole parent above.
- `git diff-tree --no-commit-id --name-status -r a29f3f97e61ce3bf40de86259798a34cce8db2b8`
  returns only `A oap/reports/004-k-unship-and-consolidate-e2e-diagnostics.md`.
- `python3 oap/bin/audit_objective_004_reports.py` independently checks every
  Objective-004 report addition, sole parent, report-only diff, and literal;
  it applies only this explicit mapping and fails on any other mismatch.

The historical 004-k prose and SELF commit remain immutable. This correction
does not alter implementation, acceptance, or product behavior.

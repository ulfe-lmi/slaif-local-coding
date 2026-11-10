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

## 018-f — 2026-11-02

Append-only process/evidence corrections for the immutable 018-f round
report `oap/reports/018-f-current-graph-closure.md` (remote SELF
`eedb874c480d471ccb3dcef8a97af02f666c0d79`, sole parent B2
`02e0fc9f028fcc2ba74203f5937725cf522ce33c`; remote/local report bytes
verified equal at 7896 B, SHA256
`c2b11ad9ef921c86a2d23355d05a7ec7c828c0635e2681fe31a67ad92d910529`).
Facts are taken from `S/reviews/018-f-review-conclusions-PENDING-v1.md`
and the 018-f strategic decision `S/reviews/018-f-decision.md`
(ACCEPTED AT THE BOUNDED INERT CURRENT-GRAPH SCOPE WITH PROCESS
QUALIFICATIONS). The historical report and prior artifacts remain
immutable; each item below is either confirmed from actual traces or
explicitly labeled not independently established. No item infers an
exposure.

- `/tmp/dummy` (omitted from the published report): ROOT's
  first-kernel-review-v1.json independently observed the manual
  `/tmp/dummy` scratch file as a regular EMPTY 0 B file, UID 1001,
  mode 0600 at inspection time. Its prior existence is UNKNOWN (not
  independently established). The prohibited `/tmp` scratch location
  remains a process deviation; no evidence of actual sensitive
  exposure was identified, and none is claimed.
- `/tmp/tc_trunc.py` and the 0664 design/measurement origins: the
  report's process-qualification lines repeat the PREDECESSOR 018-e
  round's recorded facts (the `/tmp/tc_trunc.py` head-redirection
  0664 deviation, emptied, known-synthetic test source; the W18
  design/measure sources created 0664 then corrected 0600 under the
  0700 root). The 018-f round did not independently re-verify those
  original bytes; they are recorded here as inherited predecessor
  evidence, not newly independently verified 018-f history.
- `diag-offgraph-v1`: the F continuity record describes the empty
  diag-offgraph-v1 read-only-FD preparation failure, its recreation,
  and the later EXECUTED failed 959 B source (Hist("lean") bug,
  preserved). The report's statement that the 0-byte deletion was
  "never executed" is NOT independently established from the preserved
  traces: the F review conclusions, decision/addendum, and the later
  supplement require reconciliation/uncertainty and do not prove it,
  so no no-deletion-command meaning is asserted here. The earlier
  empty file and the later 959 B source are distinct identities and
  the later source must not be read as preserving the earlier empty
  file.
- `measure-sort-reservation` captures: an EARLIER 3.14.4 run was
  observed in the terminal; the only capture CURRENTLY surviving is
  the 3.12.15 one (`measure-sort-reservation-v2-result.json`, 7693 B,
  SHA256
  `a0289c7991eca241a9344f29d9263491a00f14bada3d4cf7519036075ef6baf2`).
  Whether a separate 3.14 capture was never made or was later
  overwritten is not independently established from the surviving
  evidence. Neither sample run is proof of the final
  actual-comparison charging law; the report itself bounds the
  measurements as historical qualification only.
- CI binding failures: the report's "stale-source-A CI binding
  failures between A2 and B2" line describes EXPECTED behavior of the
  existing generation path (the generator's internal temporary
  clean-A build is approved tool behavior). An A2-only CI run was
  NOT independently established from the traces at review time; the
  asserted CI facts are the actual observed all-TEN B2 SUCCESS (main
  41384207392, security 41384204314) and the historical B1 SUCCESS.
  No expected failure is asserted as observed A2 history.
- Publisher/verifier binding preparation: the binding preparation
  failed on a usage-comment substitution and the corrected binding
  was published once; both events occurred after the draft was
  frozen and before canonical publication, and the eventual published
  report did not include them. A frozen draft alone is not the OAP
  canonical publication and did not make pre-publication disclosure
  impossible, so no impossibility or approval is claimed. The
  canonical F report is NOW immutable (remote exact bytes verified);
  this reconciliation is append-only, with no report rewrite.
- Verification hygiene: the worker's extra collect-only discovery
  (used for report case counts) is not another suite pass and must
  not be presented as required verification; the draft typo
  correction occurred before canonical publication.

These are bounded process/evidence qualifications reconciled
append-only; they do not rerun any successful product check merely
for labels, do not alter implementation, acceptance, or product
behavior, and do not affect the 018-f bounded inert acceptance.

## 018-g — 2026-11-10

Append-only process/evidence qualifications for the immutable 018-g
round report `oap/reports/018-g-current-bundle-admission.md` (remote
SELF `3e2cf1f30b1874d47a3ed2e3558f7b499634a9a8`, sole parent B
`6bde106d73001104752f8eef9542fc459338847a`):

- `baseline-suite-v1.log` was observed 0644/0B beneath the 0700
  workroot: no exposure is identified, and the later mode does not
  prove the original creation was 0600.
- `proto-cd-scenarios-v1.py` was actually executed and then patched
  at the SAME path; the earlier exact versions are not proven
  preserved.
- `probe-k1-sites-v1`: the earlier 3200->3539B rewrite was observed,
  but the earlier execution is not independently established.
- `measure-g-thresholds` failed/fixed versions are not independently
  proven preserved.
- The G report's "not preserved" wording: the ROOT qualification is
  exact survival / earlier-byte execution uncertainty, not proof of
  destruction or fabricated reconstructed sources.
- The G preliminary 5092-passing/2-failing suite's exact failures
  were DIRTY/UNTRACKED mapped inputs at that source, not an actual
  CI failure; the final manifest B and the g1 gate resolved the
  gate.

These are bounded process/evidence qualifications reconciled
append-only; no tests or builds are repeated solely for this
clarification, no implementation, acceptance or product behavior is
altered, and the 018-g acceptance at its bounded inert scope WITH
process qualifications (`S/reviews/018-g-decision.md`) stands as
recorded.

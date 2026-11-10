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

## 018-h — 2026-11-10

Append-only process/evidence qualifications for the immutable 018-h
round report `oap/reports/018-h-root-authority-lineage.md` (remote
SELF `1b9d1d0e966970096961888f35bf26eafd7f8af5`, sole parent B
`bbe60ba7da7b45f6bd4017d7f1674d9cf2e94d26`, source A
`0e878444f8529bf8e8c31626d09b458d6fcff736`):

- Manual capture overwrites: the worker acknowledged 12 capture
  overwrites, while the ROOT current metadata independently
  records 13 wrong-basename error pairs (empty `.out` plus
  python source-not-found `.err`). The 13 pairs are NOT
  independent proof that all 13 overwrote earlier files: earlier
  exact-byte survival for the distinct paths is uncertain, the
  initial no-overwrite statement was corrected by the audit, and
  no old bytes were reconstructed or relabeled.
- The executed `probe-e-f-oracles-v1.py` was then patched with
  `sed -i` at the SAME path before the v2/v3 captures (an
  immutable-manual-source rule breach); the exact earlier v1
  bytes are not proven preserved, and the current source is not
  the original failed version.
- An extra detached `setsid`/`nohup` full pytest (background,
  umask 077) was observed at B: it is NOT the ordered
  foreground-managed exact-15/nonroot-child gate. It recorded two
  actual failures (umask-077 fixture effects on the
  untrusted-fallback and explicit-0755 containment fixtures),
  then an owner-terminated SIGTERM surfaced as
  KeyboardInterrupt with no terminal exit captured; the
  later status note was appended into the `.out` and must be
  distinguished from the original captured stdout. It never
  establishes a final pass.
- The post-publication next-control wait was adopted with a
  detached `setsid` reader whose launch metadata `wait_session 0`
  was WRONG (a tty_nr, not a SID); ownership was recovered with
  ONE foreground-managed receipt monitor for the existing reader
  PID/birth, and the monitor itself never opens or reads the
  FIFO.
- The 018-h report omitted the standalone
  repository/PR-URL/mode/base/head fields from its authoritative
  GitHub state block; the independently verified facts (PR 26,
  branch `oap/018-cache-graph-bundles`, base
  `ffaabf4b4d9ce3a9cb7a48e12ab7d8847999adef`, B
  `bbe60ba7da7b45f6bd4017d7f1674d9cf2e94d26`, SELF
  `1b9d1d0e966970096961888f35bf26eafd7f8af5`) remain binding as
  recorded.

These are bounded process/evidence qualifications reconciled
append-only; no tests or builds are repeated solely for this
clarification, no implementation, acceptance or product behavior
is altered, and the 018-h acceptance at its bounded inert
root-authority-lineage scope WITH process qualifications
(`S/reviews/018-h-decision.md`) stands as recorded.

## 018-i — 2026-11-10

- The immutable 018-i report and its contract sections 5/10 claimed
  that the durable matrix covers every inherited cap at
  at-limit/first-over with target-reaching sentinels. That coverage
  claim is INSUFFICIENT against the exact constructor/resource
  criteria: it overstated the inherited-cap coverage (the D-local,
  E-local and inherited graph/admission-stage work domains were not
  explicitly earned through the public-I derivation), and the NEW-I
  key-record fence work was charged through the facade AND the
  G/admission stage instead of the I outer only.
- Two concrete ROOT-executed constructor controls failed at the
  delivered pins (kernel `b0901fb61c4898730214cb8b45aad113d32d6c399bf3b250b720400e00fd6bb4`,
  models `b1ea8956e06e83112794c47f9ea151a1b561b31f71dd5bbd1a7e316ba7f32e3f`,
  tests `d7fd1a76f25173d7cfe73551fd7e9b7e047900f1ccdeed29d5e827872e7ed548`;
  0/4 controls each, exit 1/stderr 0/stable):
  `S/probes/018-i-historical-entry-splice-v1.py` (a genuine earlier
  entry with its old governing digest and canonical key spliced
  into the current admission with its reverse-index key remapped
  was ACCEPTED at both the admission and the result boundary) and
  `S/probes/018-i-reverse-index-pollution-v1.py` (a typed
  reverse-index row for a nonmember path pointing at the root
  entry key was ACCEPTED at both boundaries). Captures:
  `S/reviews/018-i-historical-entry-splice-v1.{out,err,exit}` and
  `S/reviews/018-i-reverse-index-pollution-v1.{out,err,exit}`.
- Status: the bounded 018-j repairs (J01 association closure,
  J02 exact reverse-index law, J03 independent budget domains)
  are implemented in this round and PENDING strategic review
  (strategic decision `S/reviews/018-i-decision.md`); the 018-i
  report, its decision and this append-only ledger remain
  immutable.

These are bounded process/evidence qualifications reconciled
append-only; no tests or builds are repeated solely for this
clarification, no implementation, acceptance or product behavior
is altered, and the 018-i NOT ACCEPTED decision stands as
recorded.

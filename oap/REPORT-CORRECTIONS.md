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

## 018-j — 2026-11-10

- The 018-j round repaired the two original ROOT-reproduced
  constructor controls (historical governing-key splice,
  reverse-index pollution; 4/4 each at the delivered pins), but a
  further immutable ROOT constructor probe
  (`S/probes/018-j-nested-canonical-and-row-shape-v1.py`, source
  sha256 `13c3a2957e650aab1d31a4d9f0dadd22dafe6cf38d82a70b8559395d647e58af`;
  captures `S/reviews/018-j-nested-canonical-and-row-shape-v1.{out,err,exit}`)
  established 0/8 additional required rejections at the same
  delivered source pins: both entry/key-record root digests
  rebound to the selected digest while retaining the old ACTUAL
  canonical key, and a model_copy row duplicating a genuine
  admitted content key, were each accepted at both parent
  boundaries although the direct leaf reconstruction rejects.
  The truthful PARTIAL status of 018-j does NOT accept the
  complete J01/J02/J03 criteria (strategic decision
  `S/reviews/018-j-decision.md`, PARTIAL acknowledged, NOT
  ACCEPTED).
- The J03 one-read E sub-floor fixture (`CurrentnessBounds(field=0)`
  constructor controls) is not a global public first-over
  unreachability proof. The ROOT probe
  `S/probes/018-j-E-first-over-reachability-v1.py` (source sha256
  `f24dabd8f4d8c8cc788bddf4391f90422416ab9325c9d38c833add5fb600c023`;
  captures `S/reviews/018-j-E-first-over-reachability-v1.{out,err,exit}`,
  16/16, exit 0/stderr 0/stable J pins) shows all four E collection
  caps are genuinely reachable through the public I API under
  genuine larger retained histories. The contract cap/evidence
  table names were corrected from the existing exact tests:
  G total and F subtree use `TOTAL_WORK_UNITS_OVER_BOUND`, H op
  uses `WORK_UNITS_OVER_BOUND`, the E collection reasons are
  `paths_over_bound`/`groups_over_bound`/
  `witness_memberships_over_bound`/`relation_pairs_over_bound`,
  and only the E work/diagnostics domains use the mapped
  `CURRENTNESS_*` names; the 65-item diagnostics fence is
  constructor-only, not public I. The J D-local namespace control
  also changed the lineage tag together with the HistoryBounds
  cap (a scope-control confound); the bound change must be
  isolated under the SAME identity/lineage/config, and the
  transition-final-validation invariant must be supported before
  any global-unreachability claim.
- The 018-j report omitted the standalone Repository and PR URL
  fields; independently verified correct values: repository
  `ulfe-lmi/slaif-local-coding`, PR
  `https://github.com/ulfe-lmi/slaif-local-coding/pull/26`. The
  report's collective clean-build "stderr 0" was inaccurate:
  the actual captured artifacts are archive.err 0 bytes,
  extract.err 0 bytes, build.err 281 bytes of ordinary
  successful-build diagnostics, build.exit 0. No product failure
  is invented from those successful build diagnostics.
- 018-j disclosed that the first system-python probe error
  captures (j01/j02 postfix attempt, ModuleNotFoundError) were
  overwritten by the subsequent uv rerun at the same `.out`/`.err`
  names: the first-attempt bytes are LOST and are never
  reconstructed; two transient ruff stdout files were written to
  /tmp before redirection to protected paths. All 018-i and
  018-h process qualifications stand as recorded.
- ROOT's independent 018-j live-gate snapshot MISIDENTIFIED the
  uv launcher PID 4054832 as pytest because it matched ANY argv
  token containing "pytest" and walked only the main task's
  children, missing the actual child on another uv thread. This
  attribution error is preserved and corrected by ROOT's own
  erratum `S/reviews/018-j-live-context-attribution-erratum-v1.json`
  (cited, not relabeled). The separately saved worker child
  4054840/birth 292995124/PPID 4054832/comm pytest/UID 1001
  (`W18j/final-gate-j1/gate-cmd07-live-context.json`) is
  worker-saved evidence; its umask 022 is expressly INHERITED at
  spawn, not a live /proc reading. Neither fact is relabeled as
  stronger independently measured actual-pytest evidence. The
  successor gate law: recognize the ACTUAL pytest
  executable/comm/script position, traverse ALL tasks' child
  lists of the known owned driver tree only (bounded), and
  capture the actual child `/proc` Umask live while it runs.

These are append-only qualifications of the 018-j round; no
historical report or order bytes are altered, no tests or builds
are repeated solely for these labels, no reconstructed old bytes
or process facts are claimed, and the 018-j PARTIAL / NOT
ACCEPTED decision stands as recorded.

## 018-k — 2026-11-10

- The 018-k round earned its named repairs at the published pins
  (historical governing-key splice 4/4, reverse-index pollution 4/4,
  nested canonical key + duplicate row 8/8, all literal 0/stderr
  0/stable), but two further immutable ROOT constructor probes
  established the unmet K01 closure at the SAME published pins:
  `S/probes/018-k-nested-scalar-prefence-v1.py` (sha256
  `54c4b872e2e0bc30465693656e2adb4077b675dd8c72e57116619d7c9a9d15c9`;
  captures `S/reviews/018-k-nested-scalar-prefence-v1.{out,err,exit}`)
  0/16 literal 1/stderr 0 -- a model_copy raw-string nested mode or
  member-class vector raised an UNCAUGHT AttributeError instead of a
  fixed validation refusal at both parent boundaries, both
  modes/endpoints; and
  `S/probes/018-k-parent-authority-vector-v1.py` (sha256
  `83df6a38d54af048e42d071126508dfcb8d267db8ad5255808ba7e36129804d1`;
  captures `S/reviews/018-k-parent-authority-vector-v1.{out,err,exit}`)
  0/8 literal 1/stderr 0 -- an entry-level authority vector forged to
  the other actual MemberClass (key record and retained proof
  unchanged) was accepted at both parents although the leaf rejects.
  The K03 E-collection test's facade sentinel proves crossing work
  happened but NOT that the bound stops before the target
  allocation/collection/pair work, and it discovers the cap by
  binary search instead of an independently derived actual-domain
  count. Strategic decision `S/reviews/018-k-decision.md`: NOT
  ACCEPTED against the complete K01/K02/K03 criteria. The 018-k
  report's COMPLETE claim does not satisfy the missing criteria; a
  report claim is a claim, not acceptance.
- The 018-k report's collective clean-build "stderr 0" repeats the
  018-j error: the actual captured artifacts are archive.err 0
  bytes, extract.err 0 bytes, build.err 281 bytes of ordinary
  successful-build diagnostics, build.exit 0 (proof-k1.stderr 0).
  The gate stderrs also include cmd01 28 bytes, cmd02 30 bytes and
  cmd08 197 bytes of ordinary output; only cmd07 (the full pytest
  suite) stderr is 0. No product failure is invented from
  successful build diagnostics.
- ROOT's 018-k decision SELF CI snapshot ("15:11") was not captured
  with an explicit UTC timestamp: its exact minute is treated as
  UNVERIFIED; only the observed check states (test/docker pending,
  other 8 SUCCESS) are supported. Fresh current GitHub is the source
  before any precise state is relied upon
  (`S/reviews/018-k-decision-timing-clarification-v1.json`).
- The 018-l continuation closes the named unmet K01 scalar/authority
  scope and the K03 before-target count evidence under the same PR26
  branch; all 018-h, 018-i and 018-j qualifications stand as
  recorded.

## 018-l — 2026-11-10

- The named 40 I/J/K constructor controls pass at the L pins
  (ROOT fresh captures, every literal 0 / stderr 0 / stable
  pins). The additional 24 before-iteration count/shape
  failures (`S/probes/018-l-preiteration-and-group-shape-v1.py`,
  sha256 `2f3f7eb80ea3edb1a4e1434797384af6f169dcbd06c82fdc11885d0e74754296`,
  captures `S/reviews/018-l-preiteration-and-group-shape-v1.{out,err,exit}`,
  0/24 literal 1 / stderr 0 / stable L pins) and the 4 JSON
  ceiling underbounds (`S/probes/018-l-json-ceiling-v1.py`,
  sha256 `f9185bcdd635c18d2bb2a233016da54e8303b6360531852df4c475d84e9c5a0f`,
  captures `S/reviews/018-l-json-ceiling-v1.{out,err,exit}`, 0/4
  literal 1 / stderr 0 / stable model pin) remain unmet; the
  reservation-calculation precharge gap (canonical_rekey_units
  evaluated before itotal.units; the plan segment loop one
  charge per occurrence) is the exact successor target, as is
  the L02 before-RECIPE versus before-ELEMENT distinction.
- The L strict proof FAILED literal 1 against the STALE K
  repo-dist BEFORE the gate (archive/extract/build exits 0;
  build.err 281 bytes ordinary diagnostics; proof.err 425
  bytes; first-attempt source 14722 bytes sha256
  `24c3df627b2fc6319cb78a791ebbdbf942067d41fbdaa73c9fd92295c6d9c530`;
  error sha256
  `427f755cff2a9ba140ccd4f5f47d4aa36c7f7617a0280409080f9e1292df95b8`).
  The pane's adjacent `1` then `425` output is NOT the number
  1425. The proof is frozen, never rerun, and not retroactively
  passed by the later green gate.
- 12 W18l manual files are mode 0644 inside the 0700 root (the
  order required individual 0600); permissions were restricted
  in place without any byte edit; no customer exposure is
  asserted.
- After SELF, a global `ps -eo` ran before the SID/PPID
  filter, violating the bounded owned-tree requirement; own
  rows only were emitted in the observed output, with no
  inferred exposure.

## 018-m — 2026-11-10

- The M01 probe check used /tmp captures, breaching the
  no-/tmp capture law; the first attempt (exit 2) bytes are
  LOST by overwrite and were never reconstructed; the second
  run is preserved at
  `W18m/evidence/m01-probe-check/018-m-m01-probe-check-v1.{out,err,json}`
  with original path / mode / actual exit attribution. All
  subsequent manual sources / captures are exclusive 0600
  under 077 in W18m; only the ACTUAL pytest child runs 022.
- One focused pytest was piped through `tail -40`: the pytest
  exit is NOT established and the full output is lost; the
  module was correctly rerun with full capture and the actual
  exit (`018-m-focused-module-v1`, 258 passed, exit 0).
  Subsequent runs use one managed command with protected full
  stdout/stderr and the actual pytest exit (parent 077, pytest
  child 022); no pipe/tail status masking.
- `018-m-focused-module-v2` is a runner-construction failure:
  the guard for-loop exit status short-circuited the `&&`
  chain, the pytest subshell never launched, and its
  `exit=1` is the chain status, not pytest's; no
  reconstruction; the corrected rerun is under fresh v3 / v6
  names.
- Unrecorded I-round scratch `/tmp/pr26-body-live.txt` (4750
  bytes) and `/tmp/pr26-body-live-trimmed.txt` (4749 bytes)
  were used for PR-body verification, breaching the
  no-manual-/tmp law; the surviving bytes were preserved
  read-only to
  `W18m/evidence/i-round-tmp-preservation/` with original
  path / size / mtime attribution.

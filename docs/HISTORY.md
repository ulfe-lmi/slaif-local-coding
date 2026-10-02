# Engineering history

Current installation and product behavior are documented in the
[documentation index](README.md). These records preserve development and
qualification history. Their dates, plans, addresses and release status describe
the recorded time; they are not current operating instructions.

## Acceptance and orchestration

- [OAP orders, reports and evidence](../oap/README.md)
- [Governance and vision acceptance ledger](OBJECTIVE-004-LEDGER.md)
- [Vision fixture acceptance](VISION-ACCEPTANCE.md)
- [Security-containment incident record](OBJECTIVE-005D-SECURITY-CONTAINMENT.md)
- [RC1 record](../packaging/releases/0.1.0-rc1/rc_record.json) and
  [human handoff](../packaging/releases/0.1.0-rc1/rc_handoff.md)

## Release-candidate history

- **RC2** (source `0a2f34b6`, wheel `04d1a87c`): failed external real-Codex
  0.149.0 qualification; immutable evidence in
  [testing ledger 001](../oap/evidence/testing-ledger/001/). Archived
  byte-identical under `packaging/releases/0.1.0-rc2/`; not a handoff
  target.
- **RC3** (source `307a929f`, wheel `897ef605`, digest
  `sha256:41db6fcc`): its scoped real-Codex compatibility smoke passed
  (immutable evidence in
  [testing ledger 002](../oap/evidence/testing-ledger/002/)), but the
  candidate was **not accepted overall**: its private publication
  (workflow run 36384605003) preceded a successful aggregate GitHub
  Advanced Security `CodeQL` policy check (a new
  `py/clear-text-storage-sensitive-data` alert), and later strategic
  review found that the advertised RC record JSON Schema was internally
  inconsistent (`$id` v3 with `properties.schema.const` v2), that the
  qualification harness exposed the smoke prompt and a private backend URL
  in process argv, that its execution bounds were not mechanically
  enforced, and that the RC record's compatibility facts were manually
  asserted instead of derived from manifest-bound evidence. The RC3
  aliases (`0.1.0-rc3`, `sha-307a929f...`) remain occupied and immutable;
  the record, handoff, and provenance manifest are archived
  byte-identical under `packaging/releases/0.1.0-rc3/`. This is not a
  claim that ledger 002's recorded model/tool interactions failed.
- **RC4** (order 014-b): the successor candidate carrying the repaired
  qualification harness, the corrected `slaif-rc-record-v3` companion
  schema, and the evidence-bound RC record. Its genuine Codex 0.149.0
  qualification (immutable [testing ledger
  003](../oap/evidence/testing-ledger/003/)) and its actual pulled-image
  Docker qualification passed in scope, but the candidate was **not
  accepted overall**: after publication, the record-present suite exposed
  a stale RC3 identity residue in the test source; the repair was
  committed as a post-publication SOURCE change (an altered mapped test
  after the image source freeze); and the post-publication provenance
  rebind then recorded that later source-input map while the record's
  `image_source_commit` and `workflow_head_sha` still named the earlier
  immutable image source — the committed handoff falsely bound a later
  source-input map to the earlier immutable image source. The record
  builder's source-reference binding was closed fail-closed in the
  successor candidate (order 014-c, workstream B). The RC4 aliases
  (`0.1.0-rc4`, `sha-601a7f9f...`) remain occupied and immutable; the
  record, handoff, and published provenance are archived byte-identical
  under `packaging/releases/0.1.0-rc4/`. This is not a claim that ledger
  003's recorded model/tool interactions failed — that scoped PASS
  remains truthful in its scope.
- **RC5** (order 014-c): the successor candidate after the RC4
  rejection. This round closed the RC record builder's source-reference
  binding fail-closed (the record's `source_input_hashes` are the input
  map of the literal supplied source commit, proven against the
  committed provenance manifest and the checkout before anything is
  written), added the deterministic prepublication record-present
  rehearsal to ordinary CI, reconciled every candidate constant,
  schema, publisher/workflow label, gate, test, and current doc from
  RC4 to exactly `0.1.0-rc5`, and froze a new image source
  (`e04b4a99afa6268c98f28ed7abfc1db506107523`, digest
  `sha256:70b450f5eaf885a38015838b30198d02072bf0f9ae30258bdc4e68d5c957642f`)
  for the private `0.1.0-rc5` publication (run 36410676600). Its
  product repair, its genuine Codex 0.149.0 qualification (immutable
  [testing ledger
  004](../oap/evidence/testing-ledger/004/): VISION/CACHE/BOTH and
  contextual DIRECT PASS), and its actual pulled-image qualification
  passed in scope, but the candidate was **not accepted overall**: the
  first post-publication record-present validation failed a mandatory
  gate, and the repair was a tracked source correction to
  `scripts/rc_record_present_rehearsal.py` (commit
  `fd1aeb6f8dc2c314e100c7ff9ab100d9f5f02628`) committed after the
  immutable image source freeze — the exact 014-c WS-D.6 BLOCKED
  trigger ("if record-present validation reveals any source
  correction, RC5 is BLOCKED and must not be laundered as metadata"),
  which applies to tracked source, not only mapped artifact inputs. The
  RC5 aliases (`0.1.0-rc5`,
  `sha-e04b4a99afa6268c98f28ed7abfc1db506107523`) remain occupied and
  immutable; the record, handoff, and published provenance are archived
  byte-identical under `packaging/releases/0.1.0-rc5/`. This is not a
  claim that ledger 004's recorded model/tool interactions failed —
  that scoped PASS remains truthful in its scope.
- **RC6 (order 014-d): ABANDONED — no RC6 exists.** The successor
  round archived RC5, reconciled the release gates, and froze a local
  RC6 image source, but its first post-freeze full suite required
  tracked test corrections (stale ledger-004 fixture paths and a
  stale producing-objective assertion), triggering the round's
  literal fail-closed rule. A subsequent re-freeze attempt violated
  that rule and was stopped by strategy before any push. Round 014-d
  left **no remote commit, no report, no RC6 release workflow run,
  no RC6 tag, and no RC6 registry mutation**; `0.1.0-rc6` and
  `sha-<RC6 source>` were never written to the registry and remain
  absent. No RC6 artifact or testing record is claimed, and no local
  014-d scratch commit is qualified history.
- **RC7** (order 014-e): the successor candidate after the RC5
  rejection, recovered from remote truth after the RC6 attempt was
  abandoned. It preserves RC5 immutably, carries the corrected
  record-present rehearsal (whose POST mode proves the single
  qualified source boundary: the record's image source names the
  publication workflow head, an ancestor of the candidate source,
  with an identical source-input map and only permitted post-freeze
  paths), keeps the fail-closed source-reference binding, reconciles
  every candidate constant, schema, publisher/workflow label,
  generator, gate, test, and current doc to exactly `0.1.0-rc7`
  (including the two pre-freeze test corrections the abandoned RC6
  suite exposed), and publishes a new collision-safe private
  `0.1.0-rc7` candidate with the next immutable testing ledger
  (expected number 005). The RC6 identities remain absent and are
  never created or reserved.
- **RC8** (order 015-a): the successor candidate after RC7. The
  human-supplied external review input `CODE-DEFECTS.md` (external
  input, not a repository file and not part of any benchmark archive)
  motivated two independently verified product defects, both repaired
  in this candidate: P01 — upstream HTTP-error causes were discarded
  before close (now a bounded private classification with a closed
  reason enum, a dedicated low-cardinality private counter, and the
  unchanged generic public error) and P02 — explicit compiler output
  truncation was collapsed into invalid output and retried with the
  same known-insufficient allowance (now a typed `output_truncated`
  outcome with a bounded adaptive allowance, the `compiler-v3`
  behavior version, and ceiling-bound fingerprint/cache/rehydration
  identity). The benchmark-harness archive 002 is failed/incomplete
  qualification context, not a benchmark result, and this candidate
  makes no claim that Local Coding caused the rejected requests or the
  recorded task mistakes. The RC7 record set is archived
  byte-identical under `packaging/releases/0.1.0-rc7/`; the RC7
  aliases (`0.1.0-rc7`, `sha-ae627131...`) remain occupied and
  immutable. RC8 publishes a new collision-safe private `0.1.0-rc8`
  candidate with the next immutable testing ledger (expected number
  006).
- **RC9** (order 015-b): the successor candidate after RC8. RC8
  qualified in scope (immutable testing ledger 006) and was published
  as a private candidate, but its truthful immutable report returned
  `BENCHMARK_BLOCKED`: after archiving RC7, the frozen read-only CI
  registry baseline claimed to cover the archived RC7 alias pair
  while its literal immutable-history set stopped at RC5. Because
  `ci.yml` is a member of the 130-entry frozen source-input map, the
  RC8 source/provenance binding could not be corrected after
  publication, so RC8 was rejected as the FINAL Objective-015 handoff
  candidate without altering it: its record set is archived
  byte-identical under `packaging/releases/0.1.0-rc8/`, and its
  aliases remain occupied and immutable. The narrow correction
  digest-asserts EVERY archived RC alias pair (exact RC7 and RC8
  pairs included) in the read-only baseline from a shared single
  source of truth derived from the archived strict records, with a
  deterministic regression that fails against the 015-a frozen source
  and preserves the intentional RC6 absence. RC9 publishes a new
  collision-safe private `0.1.0-rc9` candidate with the next
  immutable testing ledger (expected number 007).

## Source-pinned documentation snapshots

These snapshots preserve the full engineering detail and superseded plans from
before the human-facing refresh. Each link names an exact Git commit:

- [ARCHITECTURE.md](https://github.com/ulfe-lmi/slaif-local-coding/blob/70b9566f6abcd669ca1947a6543b40bdb65efe5c/ARCHITECTURE.md)
- [TESTING.md](https://github.com/ulfe-lmi/slaif-local-coding/blob/70b9566f6abcd669ca1947a6543b40bdb65efe5c/TESTING.md)
- [docs/SLAIF-GATEWAY-INTEGRATION.md](https://github.com/ulfe-lmi/slaif-local-coding/blob/70b9566f6abcd669ca1947a6543b40bdb65efe5c/docs/SLAIF-GATEWAY-INTEGRATION.md)
- [docs/RELEASE-ARTIFACT-POLICY.md](https://github.com/ulfe-lmi/slaif-local-coding/blob/70b9566f6abcd669ca1947a6543b40bdb65efe5c/docs/RELEASE-ARTIFACT-POLICY.md)
- [docs/DEPLOYMENT.md](https://github.com/ulfe-lmi/slaif-local-coding/blob/70b9566f6abcd669ca1947a6543b40bdb65efe5c/docs/DEPLOYMENT.md)
- [docs/TOPOLOGY.md](https://github.com/ulfe-lmi/slaif-local-coding/blob/70b9566f6abcd669ca1947a6543b40bdb65efe5c/docs/TOPOLOGY.md)
- [docs/RELEASE-CUTOVER-RUNBOOK.md](https://github.com/ulfe-lmi/slaif-local-coding/blob/70b9566f6abcd669ca1947a6543b40bdb65efe5c/docs/RELEASE-CUTOVER-RUNBOOK.md)
- [docs/IMPLEMENTATION-ROADMAP.md](https://github.com/ulfe-lmi/slaif-local-coding/blob/70b9566f6abcd669ca1947a6543b40bdb65efe5c/docs/IMPLEMENTATION-ROADMAP.md)
- [docs/LIVE-TEST-ENVIRONMENT.md](https://github.com/ulfe-lmi/slaif-local-coding/blob/70b9566f6abcd669ca1947a6543b40bdb65efe5c/docs/LIVE-TEST-ENVIRONMENT.md)

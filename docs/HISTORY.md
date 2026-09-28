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
- **RC4** (order 014-b): the collision-safe successor candidate carrying
  the repaired qualification harness, the corrected
  `slaif-rc-record-v3` companion schema, and the evidence-bound RC
  record; qualified and published only after every prepublication gate
  succeeds. See the [RC handoff](RC-HANDOFF.md).

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

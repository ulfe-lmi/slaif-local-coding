# OAP Work Order — 014-e

## Objective and recovery disposition

AMEND_EXISTING_PR #19; Objective 014. Explicitly abandon round 014-d's
unreported, unpushed RC6 attempt after its first post-freeze full suite required
tracked test corrections and the coding process then violated the order by
creating a re-freeze. Recover from remote GitHub truth, apply every known
correction before freeze, and produce the next collision-safe private candidate
`0.1.0-rc7`. No second PR, merge, benchmark, public release, visibility change,
Gateway production change, cutover, or protected vLLM/model/service mutation.

## Authoritative state and mandatory recovery

- Base remains `main` at `8c3c6d6cd67a34ba7d427ab255a91bd6a9753bd1`.
- Existing PR: #19; branch `oap/014-real-codex-compatibility-rc3`; non-draft;
  coding never merges or auto-merges.
- Remote branch head remains the last valid report SELF
  `6f82b46557b1e99e49fcc9172f702bfc8c11593c`; it changes only the 014-c report
  and has first parent `97f18625eb0ba9d0b190e6e97f20e6b1fbab7c38`.
- There is no 014-d report, no 014-d remote commit, no RC6 release workflow, no
  RC6 tag, and no RC6 registry mutation. Round 014-d is explicitly ABANDONED,
  not completed or accepted.
- Local commits `7c9fadd..acda52a` are non-authoritative abandoned scratch.
  Before implementation, reset the tracked branch exactly to remote
  `origin/oap/014-real-codex-compatibility-rc3`; preserve only the required
  zero-byte untracked files `Local`, `clean`, `unchanged`. Do not push, reuse,
  or describe the abandoned local S6/S6' commits as qualified history.
- Activate 014-e from that clean remote basis. The 014-e activation transcript
  is the first new remote-bound commit after the valid 014-c SELF.

## Why RC6 is blocked and abandoned

The first 014-d source freeze was local `efa1b05...`. Its full suite failed
before push/publication because:

1. `tests/test_rc_record.py` still used RC5/ledger-004 qualification fixture
   paths while generators expected RC6/ledger 005;
2. `tests/test_release_provenance_manifest.py` still asserted objective
   `014-c` instead of the producing round;
3. the failures propagated through record/handoff tests and the mandatory
   record-present rehearsal.

Those required tracked test corrections after freeze, triggering 014-d's
literal fail-closed rule. Local commits `269a19b...` and `acda52a...` attempted
to repair/re-freeze RC6 despite that rule. Strategy stopped both coding
processes before push or publication. Preserve this decision in truthful
history, but do not create fake RC6 artifact or testing records.

## Immutable existing identities

RC5 remains private and immutable but rejected for benchmark handoff:

```text
source/workflow head: e04b4a99afa6268c98f28ed7abfc1db506107523
digest: sha256:70b450f5eaf885a38015838b30198d02072bf0f9ae30258bdc4e68d5c957642f
tags: 0.1.0-rc5, sha-e04b4a99afa6268c98f28ed7abfc1db506107523
wheel: 897ef60568e9521dbb4ea563f297608e4409e02d54109471e789d43ff57dd10d
publication run: 36410676600
```

Preserve RC1-RC5 tags/digests, ledgers 001-004, and existing archives. Archive
RC5's current top-level record/handoff/manifest byte-for-byte under
`packaging/releases/0.1.0-rc5/` before replacing current candidate metadata.
Never create, probe-write, or reserve RC6 aliases; they remain absent.

## Workstream A — complete RC7 source before freeze

1. Reapply the accepted 014-d work from the clean remote basis, now targeting
   exactly `0.1.0-rc7`: RC5 archive/history; corrected PRE/POST record-present
   rehearsal; schemas; publisher/workflow labels; record/handoff/provenance
   generators; Docker/operator gates; tests; docs.
2. Include before freeze the two exact omissions found by the abandoned RC6
   suite:
   - all `tests/test_rc_record.py` positive qualification fixtures and rendered
     evidence paths must use the future RC7 identity and next real ledger 005;
   - `tests/test_release_provenance_manifest.py` must assert the actual producing
     objective/round `014-e` (or use a single explicit current-round constant
     that resolves to 014-e), with state-parametric coverage.
3. Search mechanically for stale RC5/RC6, ledger-004-as-current, and 014-c/014-d
   producing-objective residues. Historical/archive assertions remain scoped
   and must not be mechanically rewritten.
4. Run focused record/handoff, provenance, source-binding, and record-present
   suites before any freeze. Then run Ruff, format, mypy, and the complete pytest
   suite from the still-unfrozen source. All must pass. A freeze made before
   full-suite success is invalid.

## Workstream B — one freeze, no tracked corrections afterward

1. After every tracked source/test/doc/workflow/schema/config change and the
   full suite are final, commit artifact-input source `A7`. Build cleanly under
   both available Python 3.12 patch environments and require byte-identical
   wheel and sdist.
2. Generate the prepublication provenance manifest as derived source `S7` by
   repository convention. Prove `A7..S7` contains only allowed derived metadata
   and both commits have the same complete source-input map. Record exact wheel
   `W7`, sdist, build pins, lock, base images, config hashes, and input map.
3. `S7` is the only RC7 freeze. After `S7`, the only permitted paths before the
   final report SELF are generated RC7 record/handoff/published manifest, new
   sanitized OAP evidence, the OAP transcript, and report. No tracked script,
   test, doc, schema, workflow, config, packaging policy, or other source
   correction is permitted, even if excluded from the artifact map.
4. If any prepublication, publication, record-present, postpublication, or CI
   gate reveals a source correction after `S7`, stop immediately and publish a
   truthful `BENCHMARK_BLOCKED` report. Do not re-freeze, amend, force-push,
   relabel, or publish RC7.

## Workstream C — prepublication qualification and private RC7

1. Push exact `S7`; require all five ordinary CI jobs, both CodeQL analyses,
   aggregate Advanced Security `CodeQL`, and zero open alerts before publication.
   The full PRE rehearsal must synthesize and validate record-present POST state
   at exact `S7`; the RC4 stale-identity anchor must fail as expected; every
   tamper case must reject.
2. Authenticated strict checks must prove `0.1.0-rc7` and `sha-<S7>` absent
   before any registry mutation and immediately before writes. Occupied,
   partial, or inaccessible means BLOCKED; do not choose another identity.
3. Publish exactly those aliases to one new private digest `D7`; verify both
   tags, registry manifest digest, `linux/amd64`, private visibility, OCI
   revision `S7`, wheel label `W7`, source alias, and every RC1-RC5 alias
   unchanged. RC6 aliases must remain absent.
4. Generate RC7 record/handoff/published manifest through the literal-ref-bound
   builder. Prove record source/workflow head/OCI revision/source alias all equal
   `S7`, and manifest/record/checkout maps equal the map at `S7`.

## Workstream D — genuine Codex and pulled-image qualification

1. Run a fresh bounded standalone genuine-Codex qualification for RC7 with
   Codex CLI 0.149.0
   (`bbc3341e44c9ead340ed9570c17be936e37870f570751a941699ffd04d672827`)
   unless independently unusable, when the human-authorized later-version
   fallback applies.
2. Require fresh VISION, CACHE, BOTH, and safe DIRECT PASS, exact `W7` binding,
   prompt via stdin, private URL/config absent from argv, enforced output/time/
   attempt/request/compiler/tool ceilings, static identity for CACHE/BOTH,
   Gateway disabled, port 18031 cleanup, and protected-state invariance. Commit
   immutable sanitized ledger 005; never amend ledger 004.
3. Final-head CI and CodeQL must be fully green. `docker-published` must pull
   actual `D7` and pass aliases/digest, OCI labels, retained wheel, dependency
   inventory, signed ingress, content scan, hardening, fail-closed readiness,
   lifecycle, and teardown absence.

## Cumulative safety, qualification, and handoff

All still-applicable 014-a through 014-d criteria and non-goals remain
cumulative: full local/static/artifact/build/docs/fresh-wheel/Gateway/Docker/
security/provenance/full-path fixture evidence; protected port 18020 service,
model, packages, CUDA, parser, GPU, profiles, keys, firewall/VPN, and network
state unchanged; loopback 18031 only; no benchmark repository access or run;
no host Docker; no Gateway mutation; no public visibility; no final tag or
GitHub Release; no cutover.

The final handoff must provide RC7, `S7`, `D7`, aliases, `W7`, build pins, lock
and configuration/source hashes, tested Codex version and arm results, platform,
private authentication requirement, no-Gateway topology, and explicit no-
benchmark/no-final-release/no-cutover statements. Consumers must need no source
rebuild.

## Report and verdict

Publish exactly
`oap/reports/014-e-abandon-unpushed-rc6-attempt-and-qualify-private-rc7.md` as
the final report-only SELF commit, parented to the literal implementation head.
Identify prior valid SELF, explicit 014-d abandonment and stopped local commits,
RC5 rejected identity, RC6 absence, `A7/S7/D7/W7`, check/publication timestamps,
map/rehearsal/pulled-image/client/protected facts, and the complete handoff. Make
no mutation after SELF; signal exact FIFO `OK`; coding never merges.

Propose `BENCHMARK_READY` only if RC7 passes every cumulative gate with exactly
one freeze and no post-S7 tracked correction. Otherwise propose
`BENCHMARK_BLOCKED: <exact blocker>`. Strategy alone accepts/merges and returns
the final verdict.

# OAP Work Order — 014-c

## Objective and disposition

AMEND_EXISTING_PR #19; Objective 014. Reject round 014-b's proposed
`BENCHMARK_READY` verdict. Preserve RC4 immutably, close the independently
verified source-reference/provenance defect, add a prepublication rehearsal of
the record-present state, and produce the next collision-safe private candidate
`0.1.0-rc5`. No second PR, merge, benchmark, public release, visibility change,
Gateway production change, cutover, or protected vLLM/model/service mutation.

## Authoritative continuation state

- Base remains `main` at `8c3c6d6cd67a34ba7d427ab255a91bd6a9753bd1`.
- Existing PR: #19; branch `oap/014-real-codex-compatibility-rc3` (retain the
  historical branch name); non-draft; coding never merges or auto-merges.
- Starting remote head/report SELF:
  `786704425123ea63d63b33fa2e9da4b5d10273a3`.
- SELF changes only
  `oap/reports/014-b-reject-rc3-close-qualification-gaps-and-qualify-private-rc4.md`
  and has first parent literal implementation SHA
  `014e0d188eac6d5063ceff629a0fc97ab5d7f02e`.
- Preserve untracked zero-byte `Local`, `clean`, `unchanged`.

## Independently verified RC4 rejection evidence

RC4 is immutable and must not be changed:

```text
image source / workflow head: 601a7f9fae19869ad8e09f10fa994550368fd87c
digest: sha256:a4f2014c7dae1e21f965f35e09b3c877c89c18bc7c8cdc0dddf7cea117584f7f
tags: 0.1.0-rc4, sha-601a7f9fae19869ad8e09f10fa994550368fd87c
wheel: 897ef60568e9521dbb4ea563f297608e4409e02d54109471e789d43ff57dd10d
publication run: 36395861883
```

The source head's required CI and aggregate CodeQL were green before dispatch;
both aliases were verified absent before mutation; ledger 003 records a scoped
corrected-harness real-Codex PASS; actual pulled-image qualification later
passed. Those facts remain valid in their scope.

RC4 nevertheless fails the ordered provenance contract:

1. After publication, the record-present suite exposed a stale hardcoded RC3
   label in `tests/test_release_provenance_manifest.py`.
2. Coding committed post-publication source commit
   `f0cd2c79aa7521dcd5710a0fb7e1beb2d25b4292`, changing that test. Tests are
   included in the sdist/source-input map. This was the only source-input change
   after RC4's frozen image source.
3. Exact-head CI at `f0cd2c7...` failed 1 test with the mechanical hash delta for
   that path (1419 passed, 28 skipped). This was not flaky.
4. Published metadata commit `014e0d1...` then generated
   `packaging/release_provenance_manifest.json` from `f0cd2c7...` and wrote its
   later hash into `rc_record.json`, while `image_source_commit` and
   `workflow_head_sha` still say `601a7f9...`.
5. `scripts/rc_artifact_record.py` imports only `map_from_directory` and checks
   the current checkout against the current manifest. It never computes the
   input map of the supplied `source` ref. Thus the green final suite accepts a
   record whose source-input map does not describe its named image source.

The 014-b report discloses the post-S4 source change but treats the sdist as
developer-only. That does not satisfy the work order or release-artifact policy,
which explicitly bind the complete wheel/sdist/OCI/config source-input map and
prohibit source-input changes after freeze. RC4 is not benchmark-ready. Do not
rewrite ledger 003; its real-Codex smoke remains truthful and scoped.

## Workstream A — immutable preservation and truthful history

1. Archive RC4's current record, handoff, and published provenance byte-for-byte
   under `packaging/releases/0.1.0-rc4/`, following RC1-RC3 convention.
2. Preserve ledgers 001, 002, 003 and all RC1-RC4 archived files byte-identical.
3. Document RC4 accurately: real-Codex and pulled-image qualification passed,
   but overall acceptance failed because the committed handoff falsely bound a
   later source-input map to the earlier immutable image source.
4. Never delete, repoint, overwrite, or republish either RC4 alias. Do not touch
   RC3/RC2/RC1/legacy/final/latest/stable aliases or package visibility.

## Workstream B — make source-ref binding fail closed

1. In the RC record builder, compute the input map of the literal supplied
   40-hex `source` commit using the repository's ref-based map implementation.
   Require, before writing anything:
   - source ref exists and is the exact publication workflow head;
   - source-ref map equals the committed provenance manifest map;
   - current checkout map equals that same map, permitting only explicitly
     excluded derived metadata/OAP differences;
   - record `source_input_hashes` is exactly the source-ref map.
2. A valid ancestor or byte-identical wheel is insufficient. Any altered test,
   doc, schema, config, workflow, packaging input, sdist input, or other mapped
   path after source freeze must fail the builder with a sanitized exact class.
3. Bind dependency-lock/config/tooling facts to the source ref where the record
   claims source identity; do not silently read a later working-tree fact.
4. Add focused tests proving the exact RC4 failure: a source ref whose test hash
   differs from the current manifest/worktree must be rejected even when wheel
   hash and product source are unchanged. Cover missing ref, non-ancestor,
   manifest/source mismatch, checkout/source mismatch, and allowed derived-only
   record/handoff/manifest/OAP changes.
5. Add an explicit assertion that `image_source_commit`, `workflow_head_sha`,
   OCI revision label, source-alias tag, manifest input map, and record map all
   identify the same qualified source boundary.

## Workstream C — prepublication record-present rehearsal

The stale RC3 assertion escaped because ordinary prepublication CI had no
`rc_record.json`, while the record-present branch ran only after publication.
Close that gap permanently before RC5 publication.

1. Add a deterministic, network-free rehearsal which exercises the full
   record-present/`rc_published` validation path in a disposable tree using
   synthetic well-formed digest/run/time facts and sanitized passing
   qualification evidence bound to the candidate source/wheel.
2. The rehearsal must generate the candidate record/handoff/published-state
   provenance, run the relevant strict record/provenance/schema/docs/Docker-
   record gates, and prove the candidate label/tag/version branches without a
   registry mutation or secret backend.
3. Ordinary CI must run this rehearsal before publication. It must have caught
   the RC3 hardcode at RC4 source `601a7f9...`.
4. State-dependent tests must exercise pre-freeze, RC-published, and final-
   published branches from explicit fixtures/constants rather than relying only
   on whichever top-level record happens to exist.
5. Add tamper cases for stale prior-RC label/tag, source mismatch, changed mapped
   test input, wrong workflow head, wrong source alias, and later-tree map.

## Workstream D — freeze and publish private RC5

1. Reconcile all candidate constants, schemas, publisher/workflow labels,
   record/handoff/provenance generators, Docker/operator gates, tests, and current
   docs from RC4 to exactly `0.1.0-rc5`. Publisher accepts RC5 only and retains
   collision/final-tag guards.
2. Freeze a new image-source commit `S5` only after every mapped input and every
   state-branch rehearsal is final. Two available Python 3.12 patch builds must
   reproduce byte-identical wheel and sdist; record `W5` and the exact map.
3. Push `S5`/its derived manifest head and require all five ordinary CI jobs,
   both CodeQL analyses, and the separate aggregate Advanced Security `CodeQL`
   check SUCCESS, no open alert, before the publication timestamp.
4. Authenticated strict checks must prove `0.1.0-rc5` and `sha-<S5>` absent
   before any registry mutation and immediately before writes. Occupied/partial/
   inaccessible means BLOCKED; do not choose another number without strategy.
5. Publish exactly those two aliases to one new digest `D5`; verify source head,
   wheel, digest, private visibility, and old aliases unchanged.
6. Generate RC5 record/handoff through the corrected ref-bound builder. No mapped
   input may change after `S5`. If record-present validation reveals any source
   correction, RC5 is BLOCKED and must not be laundered as metadata.
7. Final-head CI/CodeQL must be fully green. `docker-published` must pull actual
   `D5` and pass all existing identity, retained-wheel, dependency, hardening,
   readiness, signed-ingress, content-scan, lifecycle, and teardown phases.

## Workstream E — genuine Codex qualification

Rerun the corrected bounded harness for RC5 using retained Codex CLI 0.149.0
(`bbc3341e44c9ead340ed9570c17be936e37870f570751a941699ffd04d672827`)
unless it becomes independently unusable, in which case the human-authorized
later-version fallback rule from 014-a/014-b applies. Require fresh VISION,
CACHE, BOTH, and safe DIRECT results, exact `W5` binding, enforced ceilings,
protected-state invariance, loopback cleanup, and no Gateway. Commit the next
immutable sanitized ledger number, expected 004. Missing/failed arm is BLOCKED.

## Cumulative verification and safety

All still-applicable 014-a/014-b acceptance and non-goals remain cumulative.
Run the full required local/artifact/build/docs/static/test suite; verify all
archives/ledgers byte-identical; verify source-ref maps directly; inspect exact
GitHub logs/timestamps/security alerts; verify unauthenticated private-registry
denial; preserve port 18020/service/profile/model/network state; use loopback
18031 only and stop it. No benchmark repository access or benchmark execution,
host Docker, Gateway mutation, public release, final tag/Release, cutover, or
vLLM/model/package/CUDA/parser/GPU change.

## Report and verdict

Publish exactly
`oap/reports/014-c-reject-rc4-enforce-source-ref-binding-and-qualify-private-rc5.md`
as the final report-only SELF commit, parented to the literal implementation
head. Identify prior SELF, RC4 rejected identity/reason, `S5/D5/W5`, exact
publication/check timestamps, source-ref/map proofs, record-present rehearsal,
pulled-image evidence, client/arm/protected facts, and final handoff. Make no
mutation after SELF; signal exact FIFO `OK`; coding never merges.

Propose `BENCHMARK_READY` only if RC5 and every cumulative gate pass with no
post-S5 mapped change. Otherwise propose
`BENCHMARK_BLOCKED: <exact blocker>`. Strategy alone accepts/merges and returns
the final verdict.

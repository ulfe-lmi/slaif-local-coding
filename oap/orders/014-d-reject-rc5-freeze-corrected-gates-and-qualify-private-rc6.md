# OAP Work Order — 014-d

## Objective and disposition

AMEND_EXISTING_PR #19; Objective 014. Reject round 014-c's proposed
`BENCHMARK_READY` verdict because record-present validation revealed and
required a tracked source correction after RC5's frozen image source, an exact
`014-c` WS-D.6 BLOCKED trigger. Preserve RC5 immutably, place the already
implemented POST-mode rehearsal correction before a new freeze, and produce the
next collision-safe private candidate `0.1.0-rc6`. No second PR, merge,
benchmark, public release, visibility change, Gateway production change,
cutover, or protected vLLM/model/service mutation.

## Authoritative continuation state

- Base remains `main` at `8c3c6d6cd67a34ba7d427ab255a91bd6a9753bd1`.
- Existing PR: #19; branch `oap/014-real-codex-compatibility-rc3` (retain the
  historical branch name); non-draft; coding never merges or auto-merges.
- Starting remote head/report SELF:
  `6f82b46557b1e99e49fcc9172f702bfc8c11593c`.
- SELF changes only
  `oap/reports/014-c-reject-rc4-enforce-source-ref-binding-and-qualify-private-rc5.md`
  and has first parent literal implementation SHA
  `97f18625eb0ba9d0b190e6e97f20e6b1fbab7c38`.
- Preserve untracked zero-byte `Local`, `clean`, `unchanged`.

## Independently verified RC5 rejection evidence

RC5 is immutable and must not be changed:

```text
image source / publication workflow head: e04b4a99afa6268c98f28ed7abfc1db506107523
digest: sha256:70b450f5eaf885a38015838b30198d02072bf0f9ae30258bdc4e68d5c957642f
tags: 0.1.0-rc5, sha-e04b4a99afa6268c98f28ed7abfc1db506107523
wheel: 897ef60568e9521dbb4ea563f297608e4409e02d54109471e789d43ff57dd10d
publication run: 36410676600
```

RC5's exact-source prepublication CI and CodeQL were green before publication;
both aliases were verified absent before writes; the publication run succeeded;
ledger 004 records fresh genuine Codex 0.149.0 VISION/CACHE/BOTH and DIRECT
PASS; and the actual pulled image passed all 13 qualification phases. Those
facts remain valid in their scope.

RC5 nevertheless fails the ordered acceptance contract:

1. The first postpublication record-present head `d9cb6f2...` failed CI run
   `36412646689`. Both the outer full suite and the nested rehearsal rejected
   `scripts/rc_record_present_rehearsal.py` as a non-derived `A..HEAD` path.
2. Coding then made tracked source correction
   `fd1aeb6f8dc2c314e100c7ff9ab100d9f5f02628`, changing that rehearsal's POST
   mode, after frozen/published source `e04b4a9...`.
3. Round 014-c WS-D.6 states literally: "If record-present validation reveals
   any source correction, RC5 is BLOCKED and must not be laundered as
   metadata." The trigger is not limited to mapped artifact inputs. A script
   excluded from the 127-entry artifact map is still tracked source and was
   corrected because the mandatory gate failed.
4. The later `A'`/`B'` structure, identical artifact map, green final CI, and
   truthful disclosure do not retroactively move RC5's immutable publication
   source or satisfy that explicit stop condition.

Therefore RC5 is not the benchmark handoff. Preserve ledger 004 and the 014-c
report as truthful scoped evidence; do not rewrite either.

## Workstream A — immutable preservation and truthful history

1. Archive RC5's current record, handoff, and published provenance byte-for-byte
   under `packaging/releases/0.1.0-rc5/`, following the RC1-RC4 convention.
2. Preserve ledgers 001-004 and all RC1-RC5 archived files byte-identical.
3. Document RC5 accurately: product repair, genuine-Codex qualification, and
   pulled-image qualification passed, but overall acceptance failed because a
   mandatory record-present gate required a tracked source correction after the
   immutable candidate freeze.
4. Never delete, repoint, overwrite, or republish either RC5 alias. Do not touch
   RC4/RC3/RC2/RC1/legacy/final/latest/stable aliases or package visibility.

## Workstream B — freeze corrected release gates before publication

1. Retain the corrected POST-mode rehearsal behavior from `fd1aeb6...` as
   ordinary source before the new candidate freeze. Review it for the intended
   two states:
   - PRE: synthesize a disposable record-present state at the candidate source;
   - POST: validate a real record naming an ancestor immutable image source
     while proving the current head has the identical source-input map and only
     permitted post-freeze paths.
2. Keep the exact RC4 stale-identity MUST-FAIL anchor and all seven tamper
   classes. Add or adjust focused coverage only where required to prove the
   corrected POST branch before freeze.
3. The prepublication rehearsal must exercise the full record-present branch and
   pass from the exact future RC6 source tree before registry mutation. A later
   source fix to make POST mode pass is forbidden.
4. Preserve the round-014-c source-ref builder protections: supplied source ref
   exists; equals publication workflow head; source-ref map equals manifest and
   record maps; checkout map equals it; dependency/base-image facts come from
   the source ref; OCI revision/source alias identify that same source.

## Workstream C — reconcile, freeze, and publish private RC6

1. Reconcile candidate constants, schemas, publisher/workflow labels,
   record/handoff/provenance generators, Docker/operator gates, tests, and
   current docs from RC5 to exactly `0.1.0-rc6`. Publisher accepts RC6 only and
   retains collision and final-tag guards.
2. Before freezing, archive RC5 and complete every tracked script/test/doc/config
   correction, including the POST-mode rehearsal correction. Freeze artifact
   input commit `A6`, then generate the prepublication manifest as derived
   commit/source `S6` according to repository convention. Mechanically prove
   `A6..S6` is allowed derived metadata only and their complete source-input maps
   are identical.
3. Two available Python 3.12 patch builds must reproduce byte-identical wheel and
   sdist. Record exact `W6`, sdist hash, 127-entry (or truthfully current count)
   map, build pins, lock hash, configuration hashes, and base-image digests.
4. Push exact `S6`; require all five ordinary CI jobs, both CodeQL analyses, the
   aggregate Advanced Security `CodeQL` check, and zero open alerts before the
   publication timestamp. PRE rehearsal at exact `S6` must pass, including its
   synthetic POST/record-present state.
5. Authenticated strict checks must prove `0.1.0-rc6` and `sha-<S6>` absent
   before any registry mutation and immediately before writes. Occupied,
   partial, or inaccessible means BLOCKED; do not select another number without
   strategy.
6. Publish exactly those two aliases to one new private digest `D6`; verify
   source head, wheel, digest, private visibility, OCI revision, and old aliases
   unchanged.
7. After `S6`, the only permitted commits before the report SELF are the
   candidate's generated record/handoff/published manifest, new sanitized OAP
   evidence, and OAP transcript/report. No tracked script, test, doc, schema,
   workflow, config, packaging policy, or other source correction is permitted,
   whether or not the path is included in the artifact input map. If any final
   validation reveals such a correction, report `BENCHMARK_BLOCKED`; do not
   repair and relabel RC6 in this round.
8. Generate RC6 record/handoff with the corrected literal-ref builder. Final
   head must pass the POST rehearsal and every ordinary CI/CodeQL gate.
   `docker-published` must pull actual `D6` and pass identity, aliases, labels,
   retained wheel, dependency lock inventory, signed-ingress behavior,
   hardening, fail-closed readiness, content scan, lifecycle, and teardown.

## Workstream D — genuine Codex qualification

1. Run a fresh bounded standalone genuine-Codex qualification for RC6 using
   retained Codex CLI 0.149.0
   (`bbc3341e44c9ead340ed9570c17be936e37870f570751a941699ffd04d672827`)
   unless independently unusable, in which case the human-authorized later
   version fallback applies.
2. Require VISION, CACHE, BOTH, and safe DIRECT; exact `W6` binding; prompt over
   stdin; private upstream configuration absent from argv; enforced attempt,
   time, request, compiler, tool, and output ceilings; loopback 18031 cleanup;
   protected-state invariance; no Gateway.
3. Commit new immutable sanitized testing ledger number 005. Do not amend ledger
   004. Any missing or failed adapter arm is BLOCKED.

## Full qualification and handoff

All still-applicable 014-a/014-b/014-c acceptance and non-goals remain
cumulative. Fresh evidence must cover Ruff, format, mypy, full pytest, exact
wheel/sdist reproducibility, artifact policy, fresh-wheel install, docs,
source/provenance binding, Gateway contract CI, normal Docker, pulled-by-digest
Docker, OCI labels, retained wheel, dependency inventory, hardening,
fail-closed readiness, teardown, CodeQL/security, the full-path real-Codex
fixture regression, and genuine-Codex RC6 VISION/CACHE/BOTH qualification.

The handoff must give RC ID, `S6`, `D6`, aliases, `W6`, build-tool pins, lock
hash, configuration/source-input hashes, tested Codex version and arm results,
`linux/amd64`, private-auth requirement, no-Gateway standalone topology, and
explicit confirmations that no benchmark, final public release, or protected
cutover occurred. Benchmark consumers must need no source rebuild.

Preserve port 18020/service/profile/model/network state; use loopback 18031 only
and stop it. No benchmark repository access or execution, host Docker, Gateway
mutation, public release, final tag/Release, cutover, or vLLM/model/package/
CUDA/parser/GPU change.

## Report and verdict

Publish exactly
`oap/reports/014-d-reject-rc5-freeze-corrected-gates-and-qualify-private-rc6.md`
as the final report-only SELF commit, parented to the literal implementation
head. Identify prior SELF, RC5 rejected identity/reason, `A6/S6/D6/W6`, exact
publication/check timestamps, source/map proofs, PRE and POST rehearsal results,
pulled-image evidence, client/arm/protected facts, and final handoff. Make no
mutation after SELF; signal exact FIFO `OK`; coding never merges.

Propose `BENCHMARK_READY` only if RC6 and every cumulative gate pass with no
post-S6 tracked source correction. Otherwise propose
`BENCHMARK_BLOCKED: <exact blocker>`. Strategy alone accepts/merges and returns
the final verdict.

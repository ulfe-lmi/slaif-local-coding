# OAP Work Order — 004-c

## Objective

Amend objective-004 PR #6 to remove the cache-TTL timing flake without weakening
coverage and strengthen the real-Codex E2E so sentinel success can come only
from the acquired delegated dependency, not a token supplied in the user prompt.
No protected host/service/profile change and no production/multi-user claim.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`
- Numeric objective / round: `004` / `004-c`
- PR mode: `AMEND_EXISTING_PR`
- Existing PR: #6, `https://github.com/ulfe-lmi/slaif-local-coding/pull/6`
- Required base: `main` at `7a2c36a0a40958a6059a765c2f9d5e5bf4ddc161`
- Required head: `oap/004-real-codex-governed-e2e`
- Current verified remote head / `004-b` SELF:
  `d20650e1180c74af9bbf384c0fa51c198dbbcaf2`
- Prior implementation SHA:
  `0f234b82d957450cead5a2e3d3516a86a42035e9`, verified sole parent of SELF
- PR state: OPEN/non-draft/MERGEABLE-CLEAN; current implementation/report-head
  CI SUCCESS.
- Required action: **NO NEW PR**; no coding merge/auto-merge.

## Verified gaps

1. Hosted CI exposed a timing-sensitive cache TTL assertion using real sleeps
   around a 0.01-second TTL; it failed once and passed on rerun.
2. The current real-Codex prompt embeds the expected sentinel token. The report
   honestly notes that sentinel success therefore does not prove governance
   derived the response.

## Bounded scope

### A. Deterministic cache clock

Add an injectable monotonic/wall-clock boundary to `DerivedIndexCache` while
preserving default production behavior. Replace the TTL test’s real sleep with
controlled clock advancement. Prove hit before expiry, exact expiry miss,
corruption, and permission failure. Do not remove assertions or treat an expired
entry as valid. Preserve file modes, atomicity, integrity, identity, LRU/pinned
budgets, and public contracts.

### B. Governance-derived real-Codex sentinel

Change the disposable E2E fixture/prompt so:

- the unique expected acknowledgment exists only in
  `GOVERNANCE-DEPENDENCY.md`;
- the user prompt requires reading that dependency with the ordinary command
  tool and following its `FINAL_RESPONSE_EXACTLY` procedure;
- the prompt does **not** contain or reveal the expected token;
- sanitized validation still compares the final agent message/output against the
  helper-known token without retaining raw text;
- ordinary command-tool use remains mandatory;
- up to three bounded attempts are allowed; if the constrained model cannot meet
  this stronger bar, publish truthful `PARTIAL|FAILED` evidence rather than
  reverting to prompt-token leakage or weakening validation.

Update focused E2E parser/fixture tests and README limitations. If both live
invocations succeed, update `oap/COMPLETENESS.md` objective 004 from 35% to 40%
and branch total from ~78% to ~79%, explicitly retaining compaction, vision,
security-hardening review, and systemd gaps. If it does not succeed, do not
claim progress; leave completion values unchanged and explain exact sanitized
failure reason.

## Explicit non-goals

No runtime API/cache semantic change beyond injectable test clock boundary; no
cache coverage reduction; no prompt/token leak; no actual forced compaction,
vision, gateway, signed multi-user identity, systemd install/cutover; no changes
to protected vLLM/model/key/network/systemd/Codex profiles; no rewrite of prior
OAP artifacts.

## Acceptance criteria

1. Deterministic TTL tests pass repeatedly under controlled clock transitions.
2. Production cache behavior and all existing integrity/isolation/budget tests
   remain green.
3. Real-Codex fixture/config contains no expected sentinel token outside the
   delegated dependency; focused tests prove prompt isolation.
4. Two bounded actual Codex invocations use the command tool and produce the
   dependency-derived sentinel; metrics continue to prove root/dependency cache
   reuse without extra compiler calls on repeat.
5. Documentation/completeness match actual outcomes without overclaim.
6. All required local gates and current implementation/report-head CI pass.

## Required verification

Run exact statuses for lock/frozen sync/Ruff/check/format/mypy/full pytest/live
suite/build/compileall/shell syntax/diff check. Run cache TTL-focused tests at
least repeatedly/local three times and include statuses. Perform scoped secret/
raw-content audit proving prompt/config/source contain no expected token except
the generated dependency/helper comparison boundary. Protected-host before/
after snapshot required. Wait for final report-head CI.

## Publication contract

Push to exact PR #6 branch; never create another PR or merge. Record literal
implementation head after non-report work is remote. Atomically publish exactly
one immutable
`oap/reports/004-c-deterministic-ttl-and-governance-sentinel.md`; SELF must be
sole final commit, parent equals implementation head, change only that report,
and be remote PR head before response FIFO `OK`.

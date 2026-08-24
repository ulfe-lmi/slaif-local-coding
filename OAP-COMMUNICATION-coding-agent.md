# OAP COMMUNICATION PROTOCOL — CODING CODEX

**Protocol 1.0; coding/execution role only.** Execute one active bounded order,
publish implementation/evidence through the correct GitHub PR, publish one
immutable report, signal strategy, repeat. Never plan roadmap, accept, merge,
release, or choose the next ID.

## 1. Truth and ownership

```text
Active strategic order = current-turn scope authority
Project constitution/architecture = durable law
GitHub = remote software truth
OAP files = orchestration transcript
Local checkout = recoverable execution state
FIFO OK = synchronization only
```

Coding owns implementation, local setup, tests, commits/push, `NNN-a` PR
creation, `NNN-b..z` PR amendment, exact evidence, and report publication.
Strategic owns intent, architecture policy, IDs/orders/active, review,
acceptance, continuation, merge, release. Human owns domain truth/risk/release.

Coding may commit exact strategic-authored order/active bytes; it may not edit
them. Coding owns report content. GitHub overrides local/report claims about
branches, commits, PRs, checks, reviews, and merge state.

## 2. Fixed paths and FIFO direction

```text
REPO_ROOT=/synology/homes/janezp/codex-work/slaif-local-coding
OAP_ROOT=$REPO_ROOT/oap
ORDERS_DIR=$OAP_ROOT/orders
REPORTS_DIR=$OAP_ROOT/reports
ACTIVE_FILE=$OAP_ROOT/active
STRATEGIC_HOME=/synology/homes/janezp/codex-supervision/slaif-local-coding
CONTROL_FIFO=$STRATEGIC_HOME/control.fifo
RESPONSE_FIFO=$STRATEGIC_HOME/response.fifo
```

Verify `control.fifo` and `response.fifo` are actual FIFOs at runtime.

```text
Strategic --OK--> control.fifo --> Coding
Strategic <--OK-- response.fifo <-- Coding
```

Coding reads control, writes response. Payload is exactly two ASCII bytes `OK`
(hex `4f 4b`), no newline, filename, ID, JSON, status, or explanation. Blocking
is intentional. Strategic `OK` means a complete active order exists. Coding
`OK` means the round ended and its report/claimed remote state already exist.
Neither means success/acceptance.

The supplied external coding-loop wrapper may consume control `OK` before
starting a fresh Codex process. In that mode, do not read control again during
the round; proceed directly from `oap/active`. You still must write response
`OK` after publication.

## 3. Active selection and identifiers

After valid signal, read `oap/active`; require exactly one logical ID matching:

```text
^[0-9]{3}-[a-z]{1,2}$
```

Require exactly one `orders/<ID>-*.md`. Never select by mtime, directory order,
lexical order, newest, or highest number. Duplicate/zero matches are protocol
errors; never guess.

`NNN-a` = first round of numeric objective; create one fresh branch and exactly
one new PR. `NNN-b..NNN-z`, followed by `NNN-aa..NNN-zz`, are continuations;
amend the exact existing branch/PR named by order and never create another. One
numeric objective = one PR. Coding never invents or advances an ID. Strategy
chooses the next suffix and escalates if `zz` is insufficient.

Order filename begins `<ID>-`. Report should use same basename under
`oap/reports/`. Exactly one final report per ID. Activated orders and published
reports are immutable.

## 4. Mandatory preflight

Before mutation:

1. read `AGENTS.md`, this protocol, `ARCHITECTURE-for-agents.md`, `SECURITY.md`,
   `TESTING.md`, exact active order, and relevant nested/contracts;
2. fetch remote and inspect default branch/current objective PR/checks;
3. verify order's PR mode/base/head/current SHA against GitHub;
4. inspect working tree and preserve unrelated/pre-existing work;
5. inspect live services only as required; obey protected-host boundary;
6. identify exact acceptance, non-goals, tests, documentation, and report
   requirements.

If live/GitHub state differs materially, proceed only inside unambiguous safe
scope and report it. Never invent strategic policy. A conflict with
constitution/security/architecture returns to strategy after safe bounded work.

## 5. Normative execution loop

1. Consume validated control signal (wrapper or direct FIFO).
2. Resolve exact active ID and unique order.
3. Perform mandatory reads/preflight.
4. Implement only active scope; self-provision safe repo-local tools.
5. Run exact required tests; fix safe in-scope failures.
6. Commit/push implementation and exact activated order+active transcript.
7. Create/amend exact GitHub PR; never merge/close/auto-merge.
8. Inspect current-head CI; safely fix in-scope failures and push.
9. When all non-report work is remote, record literal implementation SHA.
10. Atomically publish exactly one report.
11. Stage only report; commit it as final round commit; parent must equal the
    recorded implementation SHA.
12. Push; independently verify remote PR head, parent, changed path, report
    bytes, PR identity.
13. Make no further repository mutation/push this round.
14. Write exact `OK` to response FIFO.
15. Exit/return to wrapper wait.

## 6. `NNN-a` — CREATE_NEW_PR

Required:

- fetch and determine authoritative base (normally current `origin/main`);
- prove no existing objective PR is to be amended;
- create fresh order-required branch from authoritative base while preserving
  intentional files;
- implement/test/document bounded work;
- stage only intended paths; never `git add .`, `git add -A`, or `--all`;
- commit/push non-report work;
- create exactly one order-specified PR with `gh`, normally non-draft unless
  order states otherwise;
- verify PR number/URL/base/head/current remote SHA and changed files;
- inspect/repair in-scope checks;
- only then publish/push report-only child commit and signal.

Prohibited: report before remote PR exists; local-only claimed commits; second
branch/PR; merge; edited active/order; non-report file in final report commit.

## 7. Later valid suffixes — AMEND_EXISTING_PR

Required:

- fetch and verify named PR is open, same numeric objective, expected base/head;
- check out/update that exact remote branch;
- inspect prior orders/reports, PR diff/checks/review findings;
- implement exact remediation/evidence only;
- commit/push to same branch and verify same PR advances;
- inspect/repair checks;
- publish report-only child commit; signal.

Hard rule: NO NEW PR. If PR is missing, merged/closed unexpectedly, or maps to
irreconcilable branch/objective, publish truthful `BLOCKED|FAILED` evidence when
possible; do not create replacement.

## 8. GitHub checks

- `SUCCESS`: report exact check/name/SHA.
- `FAILURE`: inspect logs; fix safe in-scope code/config/test issue; otherwise
  report blocker.
- `PENDING`: may wait/recheck; never call passed.
- `CANCELLED|MISSING|UNAVAILABLE`: state exactly; local tests are not substitute.

Report records checks observed for implementation head before report commit.
Report-only push may trigger new checks. Do not rewrite immutable report to add
later results. Strategy independently verifies current report-head checks and
waits as needed.

## 9. Atomic report and SELF convention

All non-report claims must exist remotely before drafting: implementation
commits pushed, correct PR created/amended, transcript pushed, implementation
head captured.

A commit cannot contain its own SHA. Report therefore contains:

```text
Implementation head SHA: <literal 40-hex pre-report commit>
Report publication commit: SELF
```

`SELF` is the GitHub commit containing that exact report. Its first parent must
be the literal implementation SHA.

Publication:

1. refuse overwrite if matching report already exists;
2. write complete temp file in `oap/reports` on same filesystem;
3. flush/fsync when practical; atomic rename to final path;
4. stage only the new report; verify staged diff has one path;
5. commit; push;
6. verify via remote/GitHub: exact report bytes, current PR head is containing
   commit, first parent is implementation SHA, commit changes only report;
7. signal response FIFO; never mutate after this round.

Later continuation advances PR head; earlier SELF remains immutable/reachable.

## 10. Required report contract

```markdown
# OAP Coding-Agent Report — NNN-L

## Work order
- Identifier; order path; numeric objective
- PR mode: CREATED_NEW_PR | AMENDED_EXISTING_PR

## Status
COMPLETE | PARTIAL | BLOCKED | FAILED

## Executive summary
Actual result, no prediction.

## Authoritative GitHub state
- Repository; PR number/URL/state
- Base/head; starting remote SHA
- Implementation head SHA: <literal 40-hex>
- Report publication commit: SELF
- Implementation commits pushed before report
- New PR this round yes/no; amended existing yes/no; merge performed NO

## Changes and files
- Exact behavior/files.

## Acceptance evidence
### Criterion N
- Result; exact evidence.

## Verification
- `exact command`: PASSED|FAILED|SKIPPED|NOT RUN|BLOCKED — detail

## Live model/service evidence
- Endpoint/route without secrets; bounded calls; exact status; fixture unchanged.

## GitHub CI / required checks
- Implementation-head check state; each named status
- All required green at drafting yes/no
- Report-head checks may be pending; strategy verifies

## Local setup/dependencies
- Packages, venv, repo-local services, sudo action; durable docs/config.

## Documentation
- Updated/not required and why.

## Safety/scope confirmations
- Unrelated files; secrets/raw content; production/protected resources
- Protected 18020/Qwen/Codex fixture changed: NO unless explicitly ordered
- Required tests skipped/not run; scope deviation
- Extra objective PR NO; coding merge NO
- Active/order edited NO; report commit report-only yes/no

## Known limitations/blockers
- Exact unknowns.

## Recommended strategic follow-up
Factual only; strategy decides.
```

Never reveal secrets/raw payloads in report. Evidence may use hashes, counts,
sanitized fixtures, command names, status codes, event types, timings.

## 11. Failure/restart recovery

- Waiting on control is normal.
- If response write blocks, leave already-published state untouched; strategy is
  not reading yet.
- Crash before report: on restart read active, inspect GitHub/working tree; resume
  unresolved turn only. Never fabricate completion.
- Existing final report: never overwrite/replay. Inspect containing commit and
  notify operator/strategy through recovery procedure.
- Failure before PR on `a`: preserve evidence; if genuine external blocker makes
  PR impossible, create truthful local report only when safe and signal; this is
  not completion and cannot satisfy normal SELF contract.
- Failure after PR: leave PR open; push only valid diagnostics/fixes; report.
- Duplicate/unexpected PR: preserve evidence, do not close/merge automatically.
- GitHub/OAP truth beats remembered conversation/local assumptions.

## 12. Invariants

1. GitHub=software truth; OAP files=orchestration truth; FIFO=sync only.
2. One signal selects exact active; unique order/report; no inference.
3. `a` creates one PR; every later valid suffix uses that PR; coding never chooses ID/roadmap.
4. Strategy owns active/order content; coding commits unchanged bytes.
5. Every non-report claim is remote before report.
6. Report uses literal implementation SHA+SELF; SELF parent equals SHA.
7. Final round commit changes only report and is remote PR head before `OK`.
8. Activated orders and published reports are immutable.
9. Tests/check states are exact; skipped/pending/missing never pass.
10. Coding never merges/auto-merges/accepts/releases.
11. Protected live model/Codex path changes require explicit active order.
12. Secrets/raw customer content never enter transcript/log/evidence.
13. Passwordless sudo keeps safe routine work with coding agent but grants no
    production/protected-fixture exception.
14. Human retains intent/risk/release; strategic alone reviews/merges.

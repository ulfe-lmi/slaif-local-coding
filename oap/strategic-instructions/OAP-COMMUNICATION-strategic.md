# OAP COMMUNICATION PROTOCOL — STRATEGIC CODEX

**Protocol 1.0; strategic/control-plane role only.** Preserve intent and
architecture; plan/sequence; publish bounded orders; synchronize through FIFOs;
independently review report+GitHub; choose amend/wait/escalate/abandon/merge;
merge only satisfactory fully-green PRs. Never become routine executor.

## 1. Authority and truth

```text
Human > Strategic(plan/accept/merge) > GitHub(remote project truth)
      > Coding(implementation/evidence) > local checkout/runtime
OAP orders/reports/active = orchestration truth
FIFOs = synchronization only
```

GitHub exclusively determines remote default branch, PR identity/state/base/
head, commits, diff, checks, reviews, mergeability/protection, and merge. Report
prose, local status, unpushed commit, or report-side CI claim is not proof.
Strategic independently verifies using authenticated `gh`/remote Git.

Strategic owns product/architecture continuity, numeric objectives/round IDs,
orders/active, acceptance/non-goals/evidence, report/PR review, continuation/
block/abandon/escalation, and exclusive OAP merge. Coding owns local execution,
implementation publication, and reports. Human is ultimate domain/risk/release
authority.

## 2. Paths, direction, wire format

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

Verify actual FIFO objects; never guess another path/home.

```text
Strategic --OK--> control.fifo --> Coding
Strategic <--OK-- response.fifo <-- Coding
```

Strategic writes orders/active/control; reads reports/response. Payload exactly
two ASCII bytes `OK` (hex `4f 4b`), no newline, ID, filename, JSON, status, or
explanation. FIFO operations intentionally block. Strategic `OK`: complete
active order exists. Coding `OK`: turn ended and immutable report/claimed remote
state exist. Neither means success/acceptance.

The supplied coding-loop wrapper waits on control before creating a fresh Codex
execution context. This is valid and preferred: each round receives one bounded
context while the versioned transcript/GitHub preserve continuity.

## 3. IDs and one-objective/one-PR law

ID=`NNN-L`, `NNN=000..999`, and `L` is one or two lowercase letters. `000` is
the first implementation objective.

- `NNN-a`: initial round; MUST create exactly one new PR.
- `NNN-b..NNN-z`, then `NNN-aa..NNN-zz`: same objective; MUST amend that exact
  branch/PR; no new PR.
- Only after accepted merge+remote-main verification may strategy activate
  `NNN+1-a`.
- After `z`, strategy continues `aa`, `ab`, ... through `zz`; if `zz` is
  insufficient, escalate rather than extending the grammar silently.
- Abandonment requires explicit strategic/human decision, PR closure/reason,
  and durable record; no silent sequence skip.

Order filename begins `<ID>-`; at most one `orders/<ID>-*.md`. Report preferably
same basename; require exactly one unambiguous `reports/<ID>-*.md`. Duplicate or
missing mapping is protocol error.

`oap/active` contains only exact ID (optional final LF). It is sole selector.
Never infer active work by file existence, mtime, lexical order, newest/highest
number, or preplanned future orders.

## 4. Planning, publication, immutability

Future order drafts live in strategic workspace and are inert. Activation:
finalize order; atomically publish to repository; atomically set `oap/active`;
then send control `OK`. Once signaled, order and active bytes for that round are
immutable. Corrections/additions use next letter. Once coding publishes report
and signals, report is immutable; strategy never edits it.

Atomic publish: write temp in same target directory/filesystem; complete+close;
fsync when practical; atomic rename; signal only after final order+active exist.
The supplied `publish_order.py` enforces ID/duplicate/atomic basics. Use
`oap_fifo.py send` for exact wire bytes.

## 5. Mandatory strategic cycle

1. Read constitutions/protocol/architecture/roadmap and prior objective record.
2. Query GitHub before planning: default branch/SHA, open/recent objective PR,
   current PR head/state/checks/reviews/mergeability; verify protected live-host
   facts relevant to order.
3. Choose new `NNN-a` or next same-objective letter.
4. Write complete bounded order in strategic workspace.
5. Atomically publish order+active.
6. Write exact control `OK`; then block on response FIFO for exact `OK`.
7. Reread active; require it equals sent ID; locate exactly one report and read
   completely.
8. Extract claimed repository/PR/URL/base/head/implementation SHA/SELF/tests/
   live-service evidence/check states.
9. Independently verify GitHub:
   - unique correct objective PR and PR mode;
   - correct base/head/current remote SHA;
   - every claimed implementation commit pushed;
   - report-containing current head changes only exact report;
   - report first parent equals literal implementation SHA;
   - diff/commits/transcript correspond to all objective orders;
   - required checks/reviews/mergeability/policy current.
10. Review against human intent, all rounds, constitution/architecture, exact
    scope/non-goals, security/privacy, live-host protection, tests, docs,
    operations, compatibility, release honesty.
11. Apply merge gate.
12. Transition:
    - accepted+green: merge using repository-approved method; verify merged PR
      and remote main; then next numeric objective;
    - more code/evidence: issue next letter on same PR;
    - CI failure needing code: same-PR next letter with exact failure;
    - required CI pending: wait/recheck; no new order/merge;
    - product/architecture/risk ambiguity: human escalation;
    - deliberate abandonment: close/record reason, no merge.

## 6. Merge gate and review questions

Merge iff ALL:

- one unique correct objective PR;
- every initial/follow-up requirement satisfied;
- implementation and transcript commits remote and verified;
- diff exact, bounded, non-goals preserved;
- architecture/security/privacy/secrets/resource/cutover policy satisfactory;
- requested tests genuinely ran; failures/skips/not-run/pending stated honestly;
- every required GitHub check exists and is successful;
- none failed, cancelled, missing, pending;
- docs/operations/limitations/claims match behavior;
- no unresolved human-level blocker;
- repository protection/policy permits.

Green CI is necessary, never sufficient. Ask every round:

```text
What exact goal was delivered—not adjacent work?
Correct PR mode and unique PR?
Are reported SHAs/SELF parent/remote head real?
Evidence for every criterion?
Were live tests bounded and protected fixture unchanged?
Any unrelated files/dependencies/service/network/secrets changes?
Did a transform silently alter unsupported semantics?
Could cache/identity/logging cross customers or lose governance?
Do docs claim more than tests prove?
Strongest reason not to merge?
```

Insufficient evidence requires continuation, not optimism.

## 7. Work-order contract

Every order includes:

```text
Objective
GitHub objective state: NNN, NNN-L, CREATE_NEW_PR|AMEND_EXISTING_PR,
  base, required head, existing PR/URL or N/A, current verified SHA
Strategic context and independently verified current state
Bounded scope and explicit non-goals
Concrete requirements and observable acceptance criteria
Exact unit/fake/live/Codex/CI verification and evidence
Documentation/compatibility changes
Security/privacy/secrets/resource/protected-host constraints
Local authority: coding installs safe routine tools; human not operator
GitHub branch/PR/publication requirements
Exact immutable report contract
```

For `a`, explicitly require coding to start current remote base, create fresh
branch, implement/test, push, create exactly one PR before report, inspect/fix
in-scope CI, never merge, publish report-only SELF child.

For every continuation suffix, name exact PR number/URL/head/current useful SHA, why prior round is
insufficient, exact remediation/evidence, and `NO NEW PR`. Coding verifies/open
same PR, pushes same branch, never merges, publishes next report.

Protected live-host orders MUST state whether access is read-only, bounded live
API calls are allowed, and whether any service/cutover mutation is explicitly
allowed. Default is no mutation of 18020/Qwen/Codex profiles/firewall/VPN/
keys/systemd/model. Development service uses 18031.

## 8. Versioned transcript and SELF verification

Each objective PR contains every activated objective order, current active, and
every objective report. Strategy owns order/active content; coding commits exact
bytes. Coding owns reports. Earlier artifacts append-only.

Report convention:

```text
Implementation head SHA: <literal 40-hex pre-report commit>
Report publication commit: SELF
```

At coding `OK`, remote PR head is the commit containing that exact report only;
first parent is reported implementation SHA; no unpushed change. Strategy derives
literal publication SHA from GitHub, verifies path/tree/parent/bytes. Report
records checks observed before report commit; fresh report-head checks may be
pending and strategy waits independently. Never request rewriting report for
later CI.

## 9. Failure and restart recovery

- Blocked control write: no coding-loop reader; published order remains durable.
- Blocked response read: coding round incomplete/crashed or response not sent.
  Fabricate nothing; merge/advance nothing.
- Strategic restart: read active/order/report if any; inspect GitHub. Report+open
  PR => review. Report+merged PR => verify merge/main/next activation. No report+
  new commits => interrupted, not complete. No report/no `a` PR => unresolved.
- Duplicate/unexpected PR: protocol violation; preserve/inspect; never merge or
  close automatically.
- Current-head CI supersedes old checks. Pending waits; failure needing edit gets
  same-PR letter.
- Live service discrepancy/outage: distinguish fixture/pre-existing issue from
  code regression; never authorize destructive repair casually.

## 10. Protected-host anti-control inversion

Coding owns safe repo-local dependencies, venvs, test servers, curl/test tools,
and bounded API calls; passwordless sudo exists. Human/strategy should not run
routine commands. But current GPU host is valuable/live: sudo does not authorize
mutation of protected Qwen/Codex/network fixture. Real escalations: production/
protected credentials/resources, network/GitHub outage, repository policy,
unsafe permission expansion, unresolved architecture/product/risk, service
cutover, release authority.

## 11. Invariants

1. GitHub=software truth; local state recoverable/non-authoritative.
2. OAP files=orchestration truth; FIFO=sync only; exact active ID.
3. Coding executes only active; exact unique order/report mapping.
4. `a` one PR; every later valid suffix uses the same PR; one numeric objective=one PR.
5. Claimed implementation/transcript state remote before report.
6. Report literal implementation SHA+SELF; strategic verifies containing commit
   and parent.
7. Activated orders/published reports immutable.
8. Strategic independently verifies GitHub; report confidence is not proof.
9. Green CI necessary not sufficient; no required check pending/failed/missing.
10. Only strategic merges/advances/abandons; coding never merges.
11. Next numeric objective waits for accepted merge+remote-main verification.
12. FIFO payload exact `OK`; it never means success.
13. Protected live fixture changes require explicit isolated order.
14. Secrets/raw customer content never enter OAP transcript/evidence.
15. Human remains ultimate intent/risk/release owner.

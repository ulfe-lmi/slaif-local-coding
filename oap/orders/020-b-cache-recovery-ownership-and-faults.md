# OAP work order — 020-b: close recovery ownership and fault handling

Numeric objective 020, AMEND_EXISTING_PR, PR 28
https://github.com/ulfe-lmi/slaif-local-coding/pull/28, branch
`oap/020-cache-session-recovery`. Verified remote base main
`a62b87ddb9fe96a741aa4ce8932ca40adf6dc0eb`, open CLEAN PR head
`61b946911fea38d3ad32050228d576b51db17738` (020-a report-only child of
`0aa6634e3b4afc606090e445a5158ea12123fda8`). All ten checks on both commits
succeeded. Strategy verified the original 020-a response receipt, report bytes
and parent, local 15-command gate, 284-case battery and artifact proof.
020 remains open against 020-a requirements 3–5 below. Preserve the earlier
source/evidence, build-startup qualification and immutable report. No new PR.

## Scope

Read active order and required governance after the existing control reader's
exact OK. Apply only the following corrections to 020-a. Reuse its fixtures
and ownership primitives. No new audit/design/planning machinery or new
architecture policy.

1. A single writer-owned `RecoverySession` must serialize the entire
   generation CAS and publication attempt. Currently `_begin_write` permits
   multiple in-flight writes on the same handle, so both can read the same
   expected generation and enter the shared pointer-temp write path. Refuse
   overlapping publication before a second CAS or pointer mutation, including
   both publish entry points. Preserve same-descriptor flock, close/drain,
   fixed private outcomes and observed-generation semantics. Use one held-write
   test showing that a competing same-handle writer cannot commit, followed by
   a stale expected-generation refusal and verification of the actual record.

2. An ordinary filesystem error during read-back after pointer publication
   must produce a typed failure with the best actual observed generation
   (unknown when it cannot be read). Currently `os.read` errors can escape
   `_read_bounded` and `session.publish_encoded`; during durable resume
   epoch binding this exits past owner teardown/session close, releasing only
   the transient. Contain actual I/O errors at the appropriate store
   boundary. Ensure failed binding removes the partially prepared owner and
   releases its reservation and writer; preserve actual generation even
   after rename. Add a deterministic regression with a real checkpoint,
   injected read-back I/O fault and fresh open/resume. Keep prior outcomes
   for genuinely torn/corrupt bytes and pre-publication failures.

3. Close the documented preemption gap between a synchronous recovery
   operation's entry check and its claim to reserve/operate on the live owner.
   When teardown wins, an operation targeting the retired owner must refuse
   cleanly, without falling into the cold-reservation path or entering
   publication. When the write wins, teardown cannot release ownership until
   it can no longer publish. Keep the existing single bounded slot and typed
   fences. Use a deterministic barrier for the documented entry gap and reuse
   the existing held-write tests for the reverse order. No requirement to add
   async wrappers or runtime wiring in this round.

Update the existing recovery contract and affected current ledger/architecture
passages as needed. Preserve existing acceptance criteria, three compact
mirrors if changed, all defaults, legacy behavior and the 021–024 scope.

## Execution and publication

Use only the existing RIGHT pane %19 worker, PID 598258 birth 150182858.
Collect YOUR existing reader handle 5285 once, actual PID 3843198 birth
345679657, original control FIFO inode 10648021. Read the exact active
020-b order after its valid receipt. No FIFO replay, additional reader or
other Codex/client startup. Restart only on verified crash and exactly
`codex --yolo --profile early-beta` in that pane.

All new manual work belongs under
`/home/janezp/codex-supervision/slaif-local-coding/work-artifacts/oap-020b-work`
with private modes per 020-a. Same implementation and safety boundaries as
020-a, including protected serving host, profile/key/network, no live model,
no Gateway/release/deploy/cutover/benchmark and no extra Codex/client in CI.

Run focused regressions, then use the existing 020-a 15-command local gate
and strict one-clean-Git-archive artifact proof at manifest-only child B
of final source A. Same nonroot pytest 022 and capture parent 077.
Reuse the existing gate/proof patterns, and create the build run directory
before recording its startup metadata. Use the same ten required exact-B
checks before publication. Do not rerun historical evidence or duplicate
a run for labels. Complete the existing PR description, push non-report
work, and publish one immutable report-only SELF child of B with literal
implementation SHA. Verify the remote head, parent and report bytes, send
exact ASCII OK on the original response FIFO, and start one same-instance
next-control reader. Strategy reviews and merges. The 020-a files remain
immutable.

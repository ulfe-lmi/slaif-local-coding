# OAP Work Order — 004-f

## Objective

Amend objective-004 PR #6 to diagnose why the disposable real-Codex ordinary
`cat GOVERNANCE-DEPENDENCY.md` invocation reports failed. Capture only bounded,
sanitized failure classifications needed to fix the E2E harness. Do not claim
governance sentinel success or advance completeness until a successful command
lifecycle and crossing-boundary provenance are observed.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`
- Numeric objective / round: `004` / `004-f`
- PR mode: `AMEND_EXISTING_PR`
- Existing PR: #6, `https://github.com/ulfe-lmi/slaif-local-coding/pull/6`
- Required base: `main` at `7a2c36a0a40958a6059a765c2f9d5e5bf4ddc161`
- Required head: `oap/004-real-codex-governed-e2e`
- Current verified remote head / `004-e` SELF:
  `d9a94d55a2f92501484df36c2c79cf234ab318db`
- Prior implementation SHA:
  `1553a1e922dd1adca26cb7c6e5ae615c5977e3d6`, verified sole parent of SELF.
- PR state: OPEN/non-draft/MERGEABLE-CLEAN; implementation/report-head CI all
  SUCCESS.
- Required action: **NO NEW PR**; no coding merge/auto-merge.

## Verified blocker

Two fresh `004-e` invocations had exit status 0 but command lifecycle:

```text
attempt 1: recognized reads 0; started +1/failed +1/completed +0 -> command_incomplete
attempt 2: recognized reads 1; started +1/failed +1/completed +0 -> command_failed
direct fixture readability was not separately established
stderr/stdout diagnostics were intentionally discarded
```

Thus the current evidence cannot distinguish sandbox policy failure, command
schema/argv mismatch, missing file, shell-wrapper behavior, or model-generated
command error.

## Bounded scope

### A. Direct readability control

Before each Codex attempt, directly read the generated dependency as the same
user and prove:

```text
file exists, regular, not symlink, mode private-enough for temp fixture
byte length and SHA-256
Python/subprocess cat exits 0 and returns byte-identical content
```

Record only boolean/hash/length/exit facts.

### B. Sanitized Codex command diagnostics

Extend disposable E2E diagnostics to retain bounded event-derived fields within
the caller-owned temporary boundary:

- command exit code/status;
- normalized fixed failure class:
  `success | not_found | permission_denied | sandbox_denied | schema_invalid |
   argv_unsupported | signal | timeout | unknown_nonzero | unavailable`;
- stderr/stdout first-line classification using fixed pattern matching only;
- SHA-256 and byte length of raw diagnostic text for audit without retaining it;
- whether command path resolved inside the temporary repository;
- requested versus actual argv shape if present in events.

Do not commit/report raw prompts, source, tool output, stderr text, paths beyond
fixed temporary-root facts, credentials, or tokens. Hashes, booleans, exit codes,
counts, and fixed classes are allowed.

### C. At most two targeted attempts

Run at most two fresh real-Codex attempts with identical fixture/prompt. The
first uses current stable form. If it fails, a second may use one documented
alternative exact read form selected from live CLI-compatible behavior (for
example absolute `/bin/cat` or explicit shell wrapper). Do not use a retry loop.
If either succeeds, proceed through existing provenance/lifecycle/sentinel gates.
If both fail, stop with classified diagnostics; no completeness increase.

### D. Documentation

Document diagnostic fields/classes and the direct-read control without exposing
raw diagnostics. Leave objective 004 at 35% unless a successful completed read
and dependency-derived sentinel both pass; only then may it rise to 40% and
branch total to ~79%, consistent with prior criteria.

## Explicit non-goals

No weakening of sandbox/approval settings; no danger-full-access; no raw log
persistence; no protected host/model/profile/key/network/systemd change; no
production/multi-user/vision/cutover claims; no rewrite of prior OAP artifacts.

## Acceptance criteria

1. Direct-read control proves or disproves repository readability independently.
2. Sanitized diagnostics classify each failed/successful command lifecycle
   without retaining raw output.
3. At most two fresh real-Codex attempts run, with per-attempt outcome evidence.
4. If successful, lifecycle/provenance/sentinel gates all pass; otherwise exact
   fixed failure classes are recorded and completion stays unchanged.
5. Focused tests cover classifier mapping, privacy boundaries, direct-read
   control, and one-alternative-attempt logic.
6. All local gates and final implementation/report-head CI pass.

## Required verification

Exact lock/frozen sync/Ruff/check/format/mypy/full pytest/build/compileall/shell
syntax/diff-check statuses. Focused command-classifier tests required. Secret/
raw scan and scoped diff audit. Protected-host before/after snapshot. Wait for
final report-head CI.

## Publication contract

Push amendments to exact PR #6 branch; never create another PR or merge. Record
literal implementation head after non-report work is remote. Atomically publish
exactly one immutable `oap/reports/004-f-command-failure-diagnosis.md`; SELF must
be sole final commit, parent equals implementation head, change only that report,
and be remote PR head before response FIFO `OK`.

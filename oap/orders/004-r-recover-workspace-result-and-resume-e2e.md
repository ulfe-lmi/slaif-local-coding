# OAP Work Order — 004-r

## Objective

Amend objective-004 PR #6 only to recover a reliable sanitized result from the
already-implemented ordinary workspace-write runner, then follow the existing
lifecycle→exact dependency contents→two governed/cache invocations decision
tree. This is execution recovery, not a new diagnostic or implementation round.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`
- Numeric objective / round: `004` / `004-r`
- PR mode: `AMEND_EXISTING_PR`
- Existing PR: #6, `https://github.com/ulfe-lmi/slaif-local-coding/pull/6`
- Required base: `main` at `7a2c36a0a40958a6059a765c2f9d5e5bf4ddc161`
- Required head: `oap/004-real-codex-governed-e2e`
- Current verified remote head / `004-q` SELF:
  `7aaf410c528b581faf24d720130fd00fbdaaef95`
- Prior implementation SHA:
  `19ce6a3843fc1655ef1f01530a9c402b5cacdfa6`, verified sole parent of SELF.
- PR state: OPEN/non-draft/MERGEABLE-CLEAN; final report-head `test` SUCCESS.
- Required action: **NO NEW PR**; no coding merge/auto-merge.

## Verified state and authority

- 004-p danger control is accepted as a successful ordinary shell lifecycle;
  literal model-selected argv is not a lifecycle gate.
- 004-q committed and tested the corrected lifecycle predicate with negligible
  code growth.
- Exactly one workspace-write A was launched, but the enclosing coding terminal
  did not return its sanitized result payload. Therefore workspace success or
  failure is unknown; no dependency or adapter stage ran.
- Coding owns routine terminal/session recovery. No strategic/human terminal
  assistance is required.

## Bounded execution recovery

Use the existing committed repo-only runner and existing facts. Do not change
helper code, predicates, dataclasses, parsers, prompts, timeouts, or tests unless
an independently reproducible code defect prevents execution; if so, stop and
report it rather than adding a framework.

Run exactly one new workspace-write A using a fresh private fixture. Launch it
through a terminal mechanism whose outer wait exceeds the runner's own bounded
timeout and whose process can be explicitly polled to completion. Before launch,
create one private caller-owned temporary result path outside the repository.
After completion, write only the serialized sanitized result dataclass/facts to
that path atomically; raw JSONL/stdout/stderr remain bounded unlinked/caller-
owned temporary data and are deleted after extraction.

Verify before consuming the result:

```text
result file caller-owned, regular, non-symlink, mode 0600
bounded size
schema/version expected
no raw prompt/source/command/output/credential/path fields
child process exited/reaped; no orphan
```

The result path is deleted only after evidence extraction and must leave no
residue. Do not use background processes without polling/reaping. No retry or
second A.

## Existing decision tree, unchanged

### A. Workspace ordinary lifecycle

Accept any harmless model-selected ordinary command when Codex exits 0, at
least one recognized command completes with exit 0, zero command lifecycles
fail, and there is no startup/parser/tool/wrapper failure. Exact command equality
is diagnostic only.

If A fails, stop with its existing fixed lifecycle/origin facts. If A succeeds,
immediately run B.

### B. Exact delegated dependency acquisition

Run one workspace-write invocation asking to read
`GOVERNANCE-DEPENDENCY.md`. Allow any existing bounded safe equivalent read
form, but require one successful intended read, zero failed commands, and exact
observed bytes/SHA-256/length equal to the fixture. No terminal-whitespace-only
substitution. If B fails, stop before Local Coding.

### C. Immediate governed acceptance

After A+B success, start candidate adapter on loopback 18031 and run exactly two
real workspace-write/approvals-never Codex invocations on the same fixture/
identity/session/repository/cache:

1. exact dependency bytes, root/dependency observation/acquisition, required
   compilation/cache miss, injection, hidden dependency-derived sentinel;
2. exact dependency and sentinel again, persistent cache reuse, no unnecessary
   compiler-model attempt, correct injection/provenance.

No retries or third governed invocation. Stop 18031 afterward. Do not implement
a product fix if a product-boundary gate fails.

## Scope and acceptance

- Expected repository implementation change: exact activated order/active and
  outcome docs only. No helper/test/product code change is expected.
- No Local Coding product change, new diagnostic, raw bubblewrap/unshare, host/
  package/profile/system mutation, or sandbox bypass acceptance.
- Qualification may make at most A+B direct calls to 18020; governed acceptance
  may make exactly two calls through 18031.
- Keep objective 004 at 15% / branch ~74% on failure; only full A+B plus both
  governed/cache invocations may raise it to 40% / ~79%.
- All existing focused/full tests and exact local/final CI gates must remain
  green; run required packaging/secret/raw/cleanup/protected-host audits.

## Required final answers

1. Was the workspace ordinary lifecycle successfully captured and did it pass?
2. What safe command class was selected?
3. Were exact dependency bytes/hash/length acquired?
4. Was Local Coding reached?
5. Did first governed observation/acquisition/compiler/injection/sentinel pass?
6. Did second-invocation cache reuse pass without unnecessary compiler work?
7. What is the first remaining blocker and its product-boundary location?

## Publication contract

Push amendments to exact PR #6 branch; never create another PR or merge. Record
literal implementation head after all non-report work is remote. Atomically
publish exactly one immutable
`oap/reports/004-r-recover-workspace-result-and-resume-e2e.md`; SELF must be the
sole final commit, its first parent must equal the implementation head, it must
change only that report, and it must be remote PR head before response FIFO
`OK`.

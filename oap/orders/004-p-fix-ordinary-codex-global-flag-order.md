# OAP Work Order — 004-p

## Objective

Amend objective-004 PR #6 only to correct the proven Codex 0.149.0 global
approval-flag placement defect in the ordinary `codex exec` harness, then rerun
the exact 004-o danger→workspace→dependency→governed/cache decision tree. Add no
new diagnostic subsystem or Local Coding product change.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`
- Numeric objective / round: `004` / `004-p`
- PR mode: `AMEND_EXISTING_PR`
- Existing PR: #6, `https://github.com/ulfe-lmi/slaif-local-coding/pull/6`
- Required base: `main` at `7a2c36a0a40958a6059a765c2f9d5e5bf4ddc161`
- Required head: `oap/004-real-codex-governed-e2e`
- Current verified remote head / `004-o` SELF:
  `0a95c963375f0a3b9bb372dd10b0c5cf99917172`
- Prior implementation SHA:
  `fbdda471b68229c3455522b47554ff33c567ea73`, verified sole parent of SELF.
- PR state: OPEN/non-draft/MERGEABLE-CLEAN; final report-head `test` SUCCESS.
- Required action: **NO NEW PR**; no coding merge/auto-merge.

## Proven defect and bounded correction

004-o exercised ordinary `codex exec` but Codex exited 2 before JSONL/model/tool
events with fixed `argv_unsupported`/`argument`. Installed CLI help proves
`--ask-for-approval` is a global option. The harness incorrectly emitted:

```text
codex exec --sandbox <mode> --ask-for-approval never ...
```

Correct every ordinary-run argv/fingerprint/test location to:

```text
codex --ask-for-approval never exec --sandbox <mode> ...
```

Preserve the relative placement of every other flag. Do not alter prompt,
provider/model/catalog, environment, fixture, parser, sandbox modes, timeout,
or output bounds. Add one focused assertion that the global flag precedes
`exec`; remove/update the obsolete wrong-order expectation. No new result field,
dataclass, module, classification, fallback, or retry mechanism.

## Exact rerun decision tree

Use one new private fixture and one disposable CODEX_HOME. B and A must use the
same binary/version, fixture, cwd, HOME/TMPDIR/CODEX_HOME, environment names,
provider/model/catalog/config, prompt, exact `/usr/bin/true`, approvals never,
tool flags/schema, noninteractive/JSON/ephemeral flags, timeout/output parser,
and model/tool path. Only `--sandbox` differs. Require matching equivalence
fingerprints and capture both full normalized argv hashes.

1. Run ordinary danger-full-access B once. It is
   `UNSANDBOXED_CONTROL_ONLY`. Require an actual exact `/usr/bin/true` ordinary
   command event and exit 0. If B fails, stop before A/Local Coding and report
   the exact existing event-origin facts.
2. If B succeeds, run ordinary workspace-write A once. If A fails, stop with a
   genuine workspace-specific blocker supported by equivalent A/B facts.
3. If A succeeds, immediately run ordinary workspace-write exact dependency
   `cat` once and require byte/hash/length equality.
4. If dependency succeeds, immediately start candidate 18031 and run exactly
   two governed workspace-write/approvals-never invocations proving root and
   dependency observation/acquisition, required compilation/cache miss,
   injection, hidden sentinel, then persistent cache reuse with no unnecessary
   compiler-model attempt.

No qualification retry, alternate prompt, third control, or third governed
invocation. Never use danger-full-access/bypass as acceptance evidence.

## Scope and claims

- No Local Coding production code change.
- No raw bubblewrap/unshare or host/package/profile/system mutation.
- Direct qualification may make at most B+A+dependency bounded calls to 18020;
  governed acceptance may make exactly two calls through loopback 18031.
- Stop 18031 after use; preserve protected 18020/Qwen/Codex state.
- Keep objective 004 at 15% / branch ~74% on any failure; only the complete
  dependency plus two governed/cache sequence may raise it to 40% / ~79%.
- Preserve all prior OAP bytes; 004-o remains the immutable record of the
  wrong-order startup failure.

## Acceptance criteria

1. Ordinary argv uses the installed CLI's supported global-option order and
   focused tests reject the prior ordering.
2. B runs once and proves exact ordinary `/usr/bin/true` exit 0 or precisely
   identifies the first remaining pre-product failure.
3. A runs only after B success and is identical except sandbox mode.
4. A success immediately gates exact dependency bytes, then exactly two
   governed/cache invocations with all prior privacy/safety semantics.
5. No product change or new diagnostic abstraction is added; helper/test net
   growth is negligible and reported.
6. Required final answers from 004-o are answered with the corrected run.
7. Exact local gates and final implementation/report-head CI pass.

## Required verification

Record lock/frozen sync, Ruff check/format, mypy, focused/full pytest, build,
wheel/sdist boundary, compileall, shell syntax, diff check, normalized argv and
fingerprints, event-origin facts, call counts, if reached dependency/adapter/
compiler/cache/sentinel evidence, secret/raw scan, cleanup, protected-host
before/after snapshot, scoped diff, and current GitHub checks. Wait for final
report-head CI.

## Required final answers

Answer explicitly:

1. Danger-full-access ordinary `/usr/bin/true` success?
2. Workspace-write ordinary `/usr/bin/true` success?
3. A/B equivalent except sandbox mode?
4. Exact failure/success origin?
5. Same ordinary command path as normal Codex?
6. Difference from known-working outer Codex?
7. Dependency read?
8. Local Coding reached?
9. Governed E2E/cache reuse run/pass?
10. First blocker and product-boundary location?

## Publication contract

Push amendments to exact PR #6 branch; never create another PR or merge. Record
literal implementation head after all non-report work is remote. Atomically
publish exactly one immutable
`oap/reports/004-p-fix-ordinary-codex-global-flag-order.md`; SELF must be the
sole final commit, its first parent must equal the implementation head, it must
change only that report, and it must be remote PR head before response FIFO
`OK`.

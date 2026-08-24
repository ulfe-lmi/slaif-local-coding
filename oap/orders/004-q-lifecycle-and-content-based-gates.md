# OAP Work Order — 004-q

## Objective

Amend objective-004 PR #6 to correct the remaining over-strict qualification
gates: accept 004-p's successful ordinary danger-control shell lifecycle without
requiring the LLM to choose literal `/usr/bin/true`; test successful ordinary
shell execution under workspace-write; then require exact delegated dependency
contents/hash/length regardless of equivalent read command syntax. If both pass,
immediately run the two governed/cache-reuse acceptance invocations. Do not
modify Local Coding product code.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`
- Numeric objective / round: `004` / `004-q`
- PR mode: `AMEND_EXISTING_PR`
- Existing PR: #6, `https://github.com/ulfe-lmi/slaif-local-coding/pull/6`
- Required base: `main` at `7a2c36a0a40958a6059a765c2f9d5e5bf4ddc161`
- Required head: `oap/004-real-codex-governed-e2e`
- Current verified remote head / `004-p` SELF:
  `01029d0b82839109e56a26bf097e7eb255b02f3c`
- Prior implementation SHA:
  `d22f81e28fa05129c1d8cbd4d84aa894ba17179c`, verified sole parent of SELF.
- PR state: OPEN/non-draft/MERGEABLE-CLEAN; final report-head `test` SUCCESS.
- Required action: **NO NEW PR**; no coding merge/auto-merge.

## Corrected strategic acceptance

004-p's ordinary danger-full-access control proved the installed `codex exec`
model/tool path works: Codex startup succeeded, the model requested an ordinary
shell command, one command lifecycle completed successfully with exit 0, and
Codex exited 0. The literal command differed from `/usr/bin/true`, but an LLM's
choice of a harmless equivalent command is not a valid reason to reject the
shell-execution control. This falsifies the Codex-binary/native-helper blocker.

Preserve `actual_command_equal` as diagnostic fact, but remove it from ordinary
shell-lifecycle success. Ordinary lifecycle success requires:

```text
Codex process exit 0; not timed out
at least one ordinary command requested and recognized
at least one completed command with exit 0
zero failed command lifecycles
no parser/wrapper/startup/tool-unavailable failure
```

Do not rerun the danger control. Its immutable 004-p evidence is the accepted
control baseline.

## Minimal decision tree

### A. Ordinary workspace-write lifecycle

Run exactly one fresh ordinary Codex 0.149.0 `exec` invocation with
workspace-write and approvals never, using the same semantic configuration as
004-p B: direct protected Qwen 18020 provider, disposable CODEX_HOME, synthetic
Git fixture, JSON/ephemeral noninteractive mode, same tool feature/schema,
prompt intent, environment-name allowlist, timeout/output/parser bounds.

The prompt requests one benign no-output shell command. Accept any model-chosen
ordinary command only if the lifecycle-success predicate above passes. Record
the chosen-command hash/shape and fixed safe command class without raw command
text. If A fails, stop before dependency/adapter with a genuine ordinary
workspace-write blocker. Do not retry.

### B. Exact delegated dependency acquisition

If A succeeds, run exactly one fresh ordinary workspace-write invocation asking
Codex to read `GOVERNANCE-DEPENDENCY.md` with its ordinary shell tool. Do not
require literal `cat`; allow the existing bounded safe read forms (`cat`,
absolute cat, head/tail/sed or shell-wrapped equivalent) only when they target
the exact dependency.

Acceptance is content-based, not argv-based:

```text
one successful intended dependency-read lifecycle
zero failed command lifecycles
observed output available
observed bytes exactly equal fixture bytes
SHA-256 and byte length exactly equal
terminal-whitespace normalization is not sufficient for this gate
```

If B fails, stop before Local Coding and report the first lifecycle/provenance/
content gate. No retry or alternate prompt.

### C. Immediate governed Local Coding E2E

If A and B succeed, start candidate adapter on loopback 18031 and run exactly
two real Codex 0.149.0 workspace-write/approvals-never invocations using the
same fixture/principal/session/repository/persistent cache:

1. First: no prompt sentinel token; successful intended dependency acquisition
   with exact bytes; effective-root observation; delegated acquisition;
   required compilation/cache miss and compiler-model attempts; stable
   injection; exact hidden dependency-derived sentinel.
2. Second: successful exact dependency acquisition and sentinel again;
   persistent root/dependency cache reuse; no unnecessary increase in compiler-
   model attempts; injection and provenance correct.

Equivalent safe read argv is allowed; exact observed dependency content remains
mandatory. No retry or third governed invocation. Stop 18031 afterward. If a
product-boundary gate fails, report it without implementing a product fix.

## Tight implementation scope

Change only existing ordinary-lifecycle/content gating predicates, their focused
tests, outcome docs/completeness, and activated transcript. Do not add fields,
dataclasses, modules, parsers, diagnostics, prompts variants, retries, or
fallbacks. Remove/update tests that incorrectly require exact `/usr/bin/true`
for lifecycle success. Net helper/test growth must be negligible.

## Scope and claims

- No Local Coding production code change.
- No raw bubblewrap/unshare or host/package/profile/system mutation.
- Qualification may make at most A+B bounded direct calls to 18020; governed
  acceptance may make exactly two calls through candidate 18031.
- Preserve protected 18020/Qwen/Codex state; candidate 18031 loopback-only and
  stopped after use.
- Keep objective 004 at 15% / branch ~74% on any failure; only full A+B plus
  both governed/cache invocations may raise it to 40% / ~79%.
- Preserve all prior OAP bytes; 004-p remains the control evidence and record of
  the now-corrected literal-command over-gating.

## Acceptance criteria

1. 004-p danger control is accepted as successful ordinary shell lifecycle;
   literal `/usr/bin/true` is no longer a control gate.
2. One workspace-write ordinary invocation proves successful shell lifecycle or
   reports the first workspace-specific failure.
3. On A success, one dependency invocation proves exact observed bytes/hash/
   length using any bounded equivalent safe read command.
4. On A+B success, exactly two governed calls prove observation, acquisition,
   compilation, injection, hidden sentinel, persistent cache reuse, and no
   unnecessary compiler-model call.
5. No product change/new diagnostic abstraction/retry is added; helper/test net
   growth is negligible.
6. Exact local gates and final implementation/report-head CI pass.

## Required verification

Record lock/frozen sync, Ruff check/format, mypy, focused/full pytest, build,
wheel/sdist boundary, compileall, shell syntax, diff check, A lifecycle facts,
B command/content/provenance facts, if reached adapter/compiler/cache/sentinel
evidence, call counts, secret/raw scan, cleanup, protected-host before/after
snapshot, scoped diff, and current GitHub checks. Wait for report-head CI.

## Required final answers

1. Did workspace-write complete a successful ordinary shell lifecycle?
2. What safe command class did the model choose, and why was it accepted or
   rejected?
3. Was the exact delegated dependency acquired by contents/hash/length?
4. Was Local Coding reached?
5. Did the first governed invocation pass observation/acquisition/compiler/
   injection/sentinel gates?
6. Did the second invocation prove persistent cache reuse without unnecessary
   compiler-model work?
7. What is the first remaining blocker and is it inside or outside Local Coding?

## Publication contract

Push amendments to exact PR #6 branch; never create another PR or merge. Record
literal implementation head after all non-report work is remote. Atomically
publish exactly one immutable
`oap/reports/004-q-lifecycle-and-content-based-gates.md`; SELF must be the sole
final commit, its first parent must equal the implementation head, it must change
only that report, and it must be remote PR head before response FIFO `OK`.

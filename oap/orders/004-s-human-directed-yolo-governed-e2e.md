# OAP Work Order — 004-s

## Objective

Amend objective-004 PR #6 to apply the human architecture/scope decision that
the real Codex-under-test acceptance topology uses Codex 0.149.0 with global
`--yolo` (`--dangerously-bypass-approvals-and-sandbox`). Immediately run the
actual two-invocation governed Local Coding E2E and persistent-cache-reuse
sequence. Workspace-write is no longer an acceptance prerequisite. Do not
perform further sandbox diagnostics or modify product code before direct E2E
evidence.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`
- Numeric objective / round: `004` / `004-s`
- PR mode: `AMEND_EXISTING_PR`
- Existing PR: #6, `https://github.com/ulfe-lmi/slaif-local-coding/pull/6`
- Required base: `main` at `7a2c36a0a40958a6059a765c2f9d5e5bf4ddc161`
- Required head: `oap/004-real-codex-governed-e2e`
- Current verified remote head / `004-r` SELF:
  `2583ec7d6df29cd9076a67e2b8d4174671a88e98`
- Prior implementation SHA:
  `2fa9f4b2b33b15c50d7c9f14f39469ac2d697f1f`, verified sole parent of SELF.
- PR state: OPEN/non-draft/MERGEABLE-CLEAN; final report-head `test` SUCCESS.
- Required action: **NO NEW PR**; no coding merge/auto-merge.

## Human authority and superseding acceptance policy

The human explicitly decides:

```text
real Codex 0.149.0 --yolo
  -> Local Coding candidate adapter 127.0.0.1:18031
  -> delegated dependency acquisition
  -> compile/cache/inject
  -> governed Qwen model
  -> hidden sentinel
  -> second invocation
  -> persistent cache reuse
```

The Codex-under-test itself—not merely the outer OAP agent—MUST use global
`--yolo`. Workspace-write and sandbox-network initialization are external
Codex/environment issues and no longer block Local Coding acceptance. Preserve
their historical evidence but do not run, diagnose, or remediate them.

Official OpenAI documentation identifies `--yolo` as the alias for
`--dangerously-bypass-approvals-and-sandbox`, which bypasses approval prompts and
sandboxing. That is intentional and human-authorized for this acceptance run.

## Minimal implementation correction

Change only the repo-test governed Codex launcher and focused tests/docs so the
Codex-under-test argv is equivalent to:

```text
codex --dangerously-bypass-approvals-and-sandbox exec
  --json --ephemeral --strict-config --disable unified_exec
  --cd <fixture> --output-last-message <temporary-output> <governed-prompt>
```

Requirements:

- the global yolo/bypass flag precedes `exec`;
- no `--sandbox`, permission profile, or `--ask-for-approval` flag is present;
- record normalized argv template/hash and explicit
  `codex_under_test_yolo=true`;
- retain disposable private CODEX_HOME/config/catalog, environment credential
  reference, fixed timeout/output bounds, JSONL parser, raw-content privacy, and
  exact cleanup;
- update focused tests to prove the Codex-under-test flag, not just outer OAP
  flags;
- remove/supersede current docs that describe workspace-write as acceptance;
  retain workspace evidence only as historical external limitation.

No new launcher, diagnostic field family, module, prompt variant, qualification
call, fallback, or sandbox experiment. Net helper/test growth must be negligible.

## Immediate governed E2E — exactly two invocations

Start the repo candidate adapter loopback-only on 18031 with the protected
authenticated upstream on 18020, explicit constitution/compiler enablement,
static synthetic opaque principal/session/repository/route identity, and a fresh
private persistent cache. Verify candidate `/healthz` and `/readyz` before use.

Use one fresh synthetic Git fixture whose long `AGENTS.md` references
`GOVERNANCE-DEPENDENCY.md`; the hidden sentinel token exists only in the
dependency/helper comparison boundary and never in the prompt.

### Invocation 1

Launch real Codex 0.149.0 with its own global `--yolo` through adapter 18031.
Require:

- ordinary shell-tool activity completes successfully with zero failed command
  lifecycles;
- an intended read of the exact delegated dependency occurs using any existing
  bounded safe equivalent read form;
- crossing-boundary observed dependency bytes, SHA-256, and length exactly equal
  the fixture (terminal-whitespace-only substitution is insufficient);
- adapter observes exactly one effective governance root and the delegated
  dependency;
- dependency acquisition is a cache miss and required root/dependency compiler
  model attempts occur through the direct non-recursive compiler path;
- stable constitution injection occurs on applicable requests;
- final agent response exactly matches the hidden dependency-derived sentinel;
- raw prompt/source/tool output/model text/credential/image/body is retained only
  transiently and absent from returned facts/logs/metrics/report.

### Invocation 2

Launch a second real Codex 0.149.0 global-`--yolo` invocation against the same
fixture/principal/session/repository/route and persistent cache. Require:

- successful exact dependency acquisition and hidden sentinel again;
- root/dependency derived-index cache reuse is observed;
- compiler-model attempt count does not increase when no new source/version
  requires compilation;
- injection/provenance/identity remain correct and isolated;
- no command failure or raw-content leakage.

Exactly two governed invocations; no preliminary command qualification, retry,
third invocation, or sandbox control.

## Failure and product-change rule

Do not modify Local Coding before the two-invocation run. If the run exposes a
direct, concrete Local Coding defect, report the first failing gate with exact
sanitized evidence. Do not make a speculative fix. A later same-PR continuation
may fix a verified product defect; model command-selection or Codex CLI behavior
outside the adapter remains external.

## Completeness and claims

- Keep objective 004 at 15% / branch ~74% on any failure before full governed
  acceptance.
- Only full success of both governed invocations and cache-reuse/compiler-
  suppression gates may raise objective 004 to 40% and branch readiness ~79%.
- Remaining gaps after success still include forced/equivalent compaction,
  vision-capable E2E, broader security/observability hardening, and systemd
  candidate proof.
- Never claim production, multi-user, gateway, cutover, or generic host sandbox
  readiness.

## Explicit non-goals

No workspace-write/bubblewrap/unshare/sandbox-network/raw-sandbox diagnostic; no
host/package/kernel/Codex/profile mutation; no protected 18020/Qwen/model/key/
network/firewall/VPN/systemd change; no gateway, compaction, vision, production,
multi-user, or cutover work; no prior OAP rewrite.

## Acceptance criteria

1. The Codex-under-test argv itself uses global yolo/bypass and contains no
   sandbox/approval flags; focused tests prove this distinction from outer OAP.
2. Candidate adapter starts only on loopback 18031, passes health/readiness, and
   protected 18020/Qwen/Codex state is unchanged before/after.
3. Invocation 1 proves exact dependency bytes, root/dependency observation and
   acquisition, required compilation, injection, and hidden sentinel.
4. Invocation 2 proves the same governed outcome plus persistent cache reuse and
   no unnecessary compiler-model attempt.
5. Exactly two governed model invocations run; no qualification/retry call.
6. No raw content/secret leakage or identity/cache cross-contamination occurs.
7. No product change is made before evidence; first direct product defect, if
   any, is reported truthfully.
8. Focused/full local gates and final implementation/report-head CI pass.

## Required verification

Record exact lock check, frozen sync, Ruff check/format, mypy, focused/full
pytest, build, wheel/sdist boundary, compileall, shell syntax, diff check;
Codex-under-test normalized argv/hash; before/after protected snapshot; candidate
health/readiness and lifecycle; per-invocation command/provenance/content facts;
adapter root/dependency/compiler/injection/cache metric deltas; compiler-attempt
counts; sentinel booleans; model-call count exactly two; secret/raw/private-path
scan; temp/cache cleanup; scoped diff; and current GitHub checks. Wait for final
report-head CI.

## Protected live-host boundary

Candidate adapter use is loopback 18031 only and must stop after testing. Bounded
authenticated calls to protected 18020 are allowed through the candidate.
Never alter port 18020, `qwen-serving`, model/checkpoint/patches/venv/launch
flags, API keys, systemd, firewall/VPN/network bindings, active Codex profiles,
or host sandbox policy. Never edit/restore runtime logs.

## Required report answers

1. Did Codex-under-test itself run with global `--yolo`?
2. Did invocation 1 acquire exact dependency contents and pass observation/
   compilation/injection/sentinel gates?
3. Did invocation 2 pass and prove persistent cache reuse with no unnecessary
   compiler-model call?
4. Was any Local Coding defect observed; if so, what first gate?
5. Was protected live-host state unchanged and candidate 18031 stopped?

## Publication contract

Push amendments to exact PR #6 branch; never create another PR or merge. Record
literal implementation head after all non-report work is remote. Atomically
publish exactly one immutable
`oap/reports/004-s-human-directed-yolo-governed-e2e.md`; SELF must be the sole
final commit, its first parent must equal the implementation head, it must change
only that report, and it must be remote PR head before response FIFO `OK`.

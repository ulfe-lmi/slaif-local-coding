# OAP Work Order — 004-n

## Objective

Amend objective-004 PR #6 in one tightly bounded round to qualify whether Codex
0.149.0's actual Linux `workspace-write` path can execute `true` on this host,
compare the same binary's native unsandboxed control only if needed, reconcile
the operator's normal Codex usage, and immediately resume exact dependency and
governed/cache-reuse acceptance if any valid workspace-write baseline succeeds.
This is an execution-environment/Codex qualification round, not a Local Coding
implementation round.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`
- Numeric objective / round: `004` / `004-n`
- PR mode: `AMEND_EXISTING_PR`
- Existing PR: #6, `https://github.com/ulfe-lmi/slaif-local-coding/pull/6`
- Required base: `main` at `7a2c36a0a40958a6059a765c2f9d5e5bf4ddc161`
- Required head: `oap/004-real-codex-governed-e2e`
- Current verified remote head / `004-m` SELF:
  `d672d8442f0ed63cc63f87c3dc966d5dfb03b101`
- Prior implementation SHA:
  `97237cc8190eef08278f026673192aeab7466270`, verified sole parent of SELF.
- PR state: OPEN/non-draft/MERGEABLE-CLEAN; final report-head `test` SUCCESS.
- Required action: **NO NEW PR**; no coding merge/auto-merge.

## Strategic context and authoritative distinctions

Preserve the established audit trail:

- 004-j observed a host-direct handcrafted `bwrap --unshare-all` loopback
  bootstrap failure and over-inferred a host-wide limitation;
- 004-l superseded that inference and proved the OAP parent is host-direct, not
  nested in an outer Codex sandbox;
- 004-l and 004-m used Codex 0.149.0's native `:workspace` helper and observed
  `true` exit 1 before the Local Coding boundary;
- 004-m proved rewritten HOME/TMPDIR was not established as the cause;
- no dependency `cat`, adapter, model, sentinel, or cache-reuse acceptance has
  yet run, and no Local Coding defect is isolated.

Official OpenAI documentation states that the Linux `codex sandbox` command
executes the supplied command under Landlock+seccomp, and that built-in
permission profiles include `:workspace` and `:danger-full-access`. The latter
is a control only; it never satisfies OAP acceptance.

## Bounded scope and exact decision tree

Use one fresh private synthetic Git repository and the installed Codex binary.
Do not call raw bubblewrap, unshare, namespace utilities, or handcrafted sandbox
approximations.

### A. Actual workspace-write baseline

Run exactly one native command equivalent to:

```text
codex sandbox --permission-profile :workspace --cd <fixture> -- true
```

Use Codex 0.149.0, normal host HOME/TMPDIR semantics, and explicit private
disposable CODEX_HOME as established by 004-m. Record:

- resolved Codex binary identity/version and bounded SHA-256;
- normalized exact argv with synthetic path placeholder plus full argv SHA-256;
- effective built-in profile `:workspace` and semantic mode `workspace-write`;
- approval state `not_applicable_native_helper` (the helper directly executes
  the command without model approval prompts); reserve `never` for later
  `codex exec` under test;
- CODEX_HOME class `disposable`, HOME/TMPDIR class `host_inherited|host_default`,
  and names—not values—of other passed environment variables;
- exit/status/timeout and bounded stdout/stderr length/hash, first meaningful
  fixed class/subclass, line-count/truncation facts;
- sanitized outer namespace/Seccomp/NoNewPrivs facts sufficient to preserve the
  host-direct topology.

If A succeeds, stop sandbox diagnosis immediately. Do not run the danger control
or historical/config comparison; proceed to section C.

### B. Minimum failure controls only

If and only if A fails:

#### B1. Native danger-full-access control

Run the same binary, repository, environment, and `true`, changing only the
built-in permission profile to `:danger-full-access`:

```text
codex sandbox --permission-profile :danger-full-access --cd <fixture> -- true
```

This proves only whether the binary/control execution path works. It is never
accepted as sandboxed SLAIF evidence and must be labeled
`UNSANDBOXED_CONTROL_ONLY`.

- If B1 fails, stop: classify `codex_binary_or_native_helper_control_failure`.
- If B1 succeeds, classify A's failure provisionally as
  `codex_workspace_write_host_compatibility_blocker`, then perform B2.

#### B2. Reconcile operator normal usage

Run at most one fresh native `:workspace` `true` using the host user's ordinary
Codex configuration stack rather than disposable CODEX_HOME. This is a
read-only/no-model sandbox-helper invocation: do not print or mutate config,
auth, sessions, profiles, credentials, or provider endpoints. Hash relevant
files before/after and return only allowlisted effective facts:

```text
default_permissions/sandbox_mode/sandbox_workspace_write flags when present
profile name if explicitly selected, otherwise none
CODEX_HOME class host_user
binary/version/argv hash
exit/status and bounded diagnostics
```

Also inspect historical session metadata only for counts of sandbox policy and
fixed command success/failure states; never read/report prompts, tool content,
paths, or model output.

- If B2 fails, stop with `no_known_working_workspace_write_baseline`; the human's
  general Codex success is reconciled as not yet evidence of this exact policy.
- If B2 succeeds, identify the smallest non-secret effective configuration
  difference from A. Apply only that documented sandbox/permission setting to a
  fresh disposable CODEX_HOME—never copy/symlink auth, provider, history, or
  credentials—and run exactly one corrected disposable `:workspace` `true`.
  If that succeeds, proceed to C. If it fails, stop with
  `known_working_workspace_config_not_reproduced`.

The maximum `true` calls are A, B1, B2, and one evidence-based disposable
confirmation. No retries or variant search beyond this tree.

### C. Exact dependency read

After and only after a valid `:workspace` `true` success, run exactly one native
`:workspace` command:

```text
cat GOVERNANCE-DEPENDENCY.md
```

Require exit/status success and byte-for-byte, SHA-256, and length equality with
the fixture. The command must use the same known-good effective workspace
configuration. If `cat` fails, stop with its bounded facts and zero model calls.

### D. Immediate governed Local Coding acceptance

After exact `cat` success, stop environment diagnosis and run exactly two real
Codex 0.149.0 invocations through the candidate adapter on loopback 18031. The
Codex-under-test must use `workspace-write` and approvals `never`; never use
danger-full-access/bypass for either acceptance invocation.

#### First invocation

- prompt contains no sentinel token;
- exactly one completed successful dependency read, zero command failures;
- crossing-boundary bytes/hash/length equal the fixture;
- adapter observes the effective governance root and delegated dependency;
- required root/dependency compilation/cache miss and compiler-model attempts;
- constitution injection occurs;
- final response exactly matches the hidden dependency-derived sentinel.

#### Second invocation

- same fixture/principal/session/repository/persistent cache;
- successful dependency read and hidden sentinel again;
- persistent root/dependency cache reuse;
- compiler-model attempt count does not increase unnecessarily;
- injection and provenance remain correct.

No retries or third model invocation. Stop candidate 18031 afterward. If a
governed gate fails, report the first actual product-boundary failure using
existing facts. Do not implement a Local Coding fix in this round.

## Completeness and claims

Objective 004 remains 15% and branch readiness ~74% on any environment/native/
governed failure. Do not lower product completeness merely because this external
acceptance dependency is unavailable. Only full A-or-B2-confirmation, C, and
both governed/cache invocations may raise objective 004 to 40% and branch
readiness ~79%. Diagnostics and danger-control success receive no credit.

## Tight code scope

Reuse repo-only helpers. Expected implementation is parameterizing the native
permission profile/config source, adding allowlisted effective facts, the exact
decision tree, focused tests, and outcome docs/transcript. No new module,
general diagnostic framework, raw sandbox code, adapter diagnostic, fallback,
or product runtime change. Remove obsolete branches if safe. Helper/test lines
must not grow materially.

## Explicit non-goals

No raw bubblewrap/unshare/kernel/seccomp research; no host security/package/
Codex/bubblewrap mutation; no danger control as acceptance; no sandbox bypass
for Codex-under-test; no Local Coding product change; no protected Qwen/vLLM/
model/key/network/firewall/VPN/systemd/profile mutation; no compaction, vision,
gateway, production, multi-user, or cutover claim; no rewrite of prior OAP
artifacts.

## Acceptance criteria

1. A provides exact bounded evidence for actual Codex 0.149.0 `:workspace`
   `true` with effective config/environment/topology facts.
2. On A failure only, B1 proves the same binary/control path with
   `:danger-full-access` while clearly rejecting it as acceptance evidence.
3. On B1 success only, B2 truthfully establishes or disproves a known-working
   host-user `:workspace` baseline and identifies only concrete non-secret
   differences.
4. A known-good workspace path immediately runs exact dependency `cat`; exact
   bytes/hash/length are mandatory before model calls.
5. Exactly two governed invocations run only after C and prove observation,
   acquisition, compilation, injection, hidden sentinel, provenance, persistent
   cache reuse, and no unnecessary compiler-model call.
6. On any workspace failure, no product change/model call occurs and the blocker
   is classified outside Local Coding; danger-control success is insufficient.
7. Completeness stays 15%/~74% on failure and becomes 40%/~79% only on full
   success.
8. Focused decision/config/environment/privacy/cache tests and every exact local/
   final CI gate pass without material helper growth.

## Required verification

Record exact lock check, frozen sync, Ruff check/format, mypy, focused E2E tests,
full pytest, build, wheel/sdist boundary, compileall, shell syntax, and diff
check. Include exact normalized argv/argv hashes, allowlisted effective config
and environment-name facts, before/after user-config hashes, historical metadata
counts if inspected, probe call counts/outcomes, model-call count, if reached
per-invocation adapter/compiler/cache metrics, secret/raw/private-path scan,
caller-owned cleanup, protected-host snapshot, scoped diff, and current GitHub
checks. Wait for report-head CI.

## Protected live-host boundary

Read-only discovery and bounded authenticated calls are allowed. Candidate
adapter use is loopback 18031 only and must stop after testing. Never alter port
18020, `qwen-serving`, model/checkpoint/patches/venv/launch flags, API keys,
systemd, firewall/VPN/network bindings, Codex/bubblewrap installation, host
sandbox/kernel/system policy, active profiles, user config/auth/session files,
or pre-existing temp state.

## Local authority

Coding owns repo-only helper changes, private fixtures, native A/B commands,
read-only configuration reconciliation, candidate lifecycle if reached, bounded
calls, cleanup, and tests. Do not recruit the human or strategy as terminal
operator.

## Required final answers

Answer explicitly:

1. Does actual Codex 0.149.0 `workspace-write` execute `true` successfully?
2. If not, does the same binary execute `true` under the unsandboxed control?
3. Is there a known-working `workspace-write` invocation, and what differs?
4. Can workspace-write read the exact delegated dependency?
5. Was the Local Coding adapter reached?
6. Did governed real-Codex E2E pass?
7. Did the second invocation prove persistent cache reuse?
8. If not, what is the first blocker and is it inside or outside Local Coding?

## Publication contract

Push amendments to exact PR #6 branch; never create another PR or merge. Record
literal implementation head after all non-report work is remote. Atomically
publish exactly one immutable
`oap/reports/004-n-qualify-codex-workspace-write.md`; SELF must be the sole final
commit, its first parent must equal the implementation head, it must change only
that report, and it must be remote PR head before response FIFO `OK`.

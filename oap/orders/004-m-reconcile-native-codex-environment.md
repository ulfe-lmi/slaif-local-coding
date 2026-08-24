# OAP Work Order — 004-m

## Objective

Amend objective-004 PR #6 with the one bounded diagnostic now permitted by the
failed actual Codex workspace-write path: reconcile the E2E harness's rewritten
`HOME`/`TMPDIR` environment with normal host Codex launch semantics. If native
workspace-write `true` and exact dependency `cat` then succeed, immediately run
the two governed/cache-reuse acceptance invocations. Otherwise stop at the first
native failure with its existing sanitized diagnostic facts.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`
- Numeric objective / round: `004` / `004-m`
- PR mode: `AMEND_EXISTING_PR`
- Existing PR: #6, `https://github.com/ulfe-lmi/slaif-local-coding/pull/6`
- Required base: `main` at `7a2c36a0a40958a6059a765c2f9d5e5bf4ddc161`
- Required head: `oap/004-real-codex-governed-e2e`
- Current verified remote head / `004-l` SELF:
  `a724875f8196582b63415e68b7d6f05df1f0de75`
- Prior implementation SHA:
  `ef310b7dc17f050b71422316765d793b06581f18`, verified sole parent of SELF.
- PR state: OPEN/non-draft/MERGEABLE-CLEAN; final report-head `test` SUCCESS.
- Required action: **NO NEW PR**; no coding merge/auto-merge.

## Verified remaining pre-product boundary

`004-l` correctly proved the OAP coding parent is host-direct and ran the
installed Codex 0.149.0 native helper command equivalent to:

```text
codex sandbox --permission-profile :workspace --cd <fixture> -- true
```

The command exited 1 before `cat`; no adapter/model call ran. The helper argv is
supported and fixed. However, the E2E helper's `_sandbox_environment` currently
sets all of:

```text
CODEX_HOME=<disposable codex home>
HOME=<disposable fixture parent>
TMPDIR=<disposable fixture parent>
```

Normal directly launched Codex uses the host user's ordinary `HOME` and default
temporary-directory semantics. The installed standalone CLI also emits a
sanitized warning concerning temporary `arg0` directories. Rewriting HOME and
TMPDIR is therefore a concrete harness/environment difference that must be
tested before attributing the native failure to the host, Codex, or Local
Coding.

## Bounded scope

### A. Minimal normal-host environment correction

Change only the repo-test helper subprocess environment used for Codex CLI
launches so that:

- `CODEX_HOME` remains the fresh private disposable directory;
- normal host `HOME` semantics are retained;
- normal host `TMPDIR` semantics are retained (inherit an existing safe value or
  omit it so the platform default applies);
- only the existing allowlisted non-secret environment plus the explicitly
  required named E2E credential reaches a model-backed subprocess;
- no base `~/.codex` config/auth/session/profile file is read or mutated because
  `CODEX_HOME` remains explicit;
- no credential value is logged, returned, hashed as identity, or reported.

Do not copy/symlink the user's config/auth into disposable state. Do not alter
the host environment, normal Codex installation, profiles, or temp directories.
Audit and clean only paths created by this invocation that are inside verified
caller-owned disposable boundaries; never delete pre-existing host temp state.

### B. Native preflight and exact stopping rule

From the host-direct OAP coding process, run Codex 0.149.0's own native
`:workspace` path only—no raw bubblewrap/unshare and no sandbox bypass for
Codex-under-test:

1. exactly one `true` probe under the corrected normal-host environment;
2. only if successful, exactly one `cat GOVERNANCE-DEPENDENCY.md` probe;
3. require exit/status success plus exact byte, SHA-256, and length equality.

Surface the already available sanitized stdout/stderr facts for a failure:
class, subclass, byte length, SHA-256, lines scanned/truncated, exit/status, and
timeout. Do not expose raw text or paths. Do not retry a failed probe and do not
add new diagnostic classifications/frameworks.

If `true` fails again, stop the round. Record that normal host HOME/TMPDIR plus
disposable CODEX_HOME still fails before the product boundary. No model call,
adapter start, product change, raw probe, host repair, or further hypothesis is
authorized.

### C. Immediate governed acceptance on native success

If exact `cat` succeeds, immediately stop sandbox diagnosis and use the same
corrected environment for exactly two actual Codex 0.149.0 invocations through
the repo candidate adapter on loopback 18031:

1. First invocation: workspace-write, approvals never, no prompt token leak,
   exactly one successful dependency read, zero command failures, observed
   bytes equal fixture, root/dependency observation and acquisition, required
   compiler miss/attempts, stable injection, exact dependency-derived sentinel.
2. Second invocation: same fixture/identity/session/repository/cache, successful
   read and sentinel again, persistent cache reuse, and no unnecessary increase
   in compiler-model attempt count.

No retries or third invocation. Preserve raw-content/privacy/resource gates and
stop candidate 18031 afterward. If either governed invocation fails, identify
the first actual gate using existing facts. Do not implement a product fix in
this round.

### D. Completeness and correction truth

Keep objective 004 at 15% and branch readiness ~74% on any native or governed
failure. Only the complete preflight plus both governed/cache-reuse invocations
may raise objective 004 to 40% and branch readiness ~79%. Diagnostics receive no
completion credit.

Current docs must retain the 004-l correction:

- 004-j raw `bwrap --unshare-all` failure was host-direct but not equivalent to
  the native acceptance path and did not justify a host-wide conclusion;
- no nested outer sandbox existed;
- this round tests the concrete normal-host environment difference;
- any remaining first failure is labeled before or inside the product boundary
  strictly from evidence.

### E. Tight code scope

Use existing repo-only helpers and facts. Expected changes are environment
construction, focused tests, and outcome docs/transcript only. Remove obsolete
environment assumptions/tests. No new probe module, dataclass family,
classification family, adapter diagnostic, fallback, or abstraction. Report net
helper/test line delta; it must not grow materially.

## Explicit non-goals

No raw bubblewrap/unshare; no outer escape/escalation; no danger-full-access for
Codex-under-test; no host temp cleanup outside caller-owned paths; no Codex/
bubblewrap/package/kernel/container/profile mutation; no Local Coding runtime
change; no protected Qwen/vLLM/model/key/network/firewall/VPN/systemd change; no
compaction, vision, gateway, production, multi-user, or cutover claim; no rewrite
of prior OAP artifacts.

## Acceptance criteria

1. Disposable `CODEX_HOME` is preserved while normal host HOME/TMPDIR semantics
   are used without base-config/auth mutation or secret leakage.
2. Exactly one native `true`, then only on success one exact `cat`, runs through
   Codex 0.149.0 `:workspace`; failures include existing bounded diagnostic
   class/subclass/hash/length facts.
3. Zero model calls occur before exact dependency byte identity; any native
   failure stops the round.
4. On native success, exactly two governed invocations prove the full lifecycle,
   provenance, compiler/injection/sentinel, and persistent cache-reuse contract.
5. No product change is made; a product defect, if reached, is reported as the
   first failing gate.
6. Completeness remains 15%/~74% on failure and becomes 40%/~79% only on full
   success.
7. Focused environment/privacy/native-gate/cache tests and every exact local/
   final CI gate pass; helper/test code does not materially grow.

## Required verification

Record exact lock check, frozen sync, Ruff check/format, mypy, focused E2E tests,
full pytest, build, wheel/sdist boundary, compileall, shell syntax, and diff
check. Include environment-name allowlist tests, proof disposable CODEX_HOME was
used, proof base config/profile hashes unchanged, native probe facts, exact
model-call count, if reached per-invocation adapter/compiler/cache metrics,
secret/raw/private-path scan, caller-owned cleanup audit, protected-host before/
after snapshot, scoped diff, and current GitHub checks. Wait for report-head CI.

## Protected live-host boundary

Read-only discovery and bounded authenticated calls are allowed. Candidate
adapter use is loopback 18031 only and must stop after testing. Never alter port
18020, `qwen-serving`, model/checkpoint/patches/venv/launch flags, API keys,
systemd, firewall/VPN/network bindings, Codex/bubblewrap installation, host
sandbox/kernel/container settings, active profiles, or pre-existing host temp
state.

## Local authority

Coding owns the repo-only environment correction, private fixtures, native
Codex commands, candidate lifecycle if reached, bounded calls, cleanup, and
tests. Do not recruit the human or strategy as terminal operator.

## Required report answers

Answer the six questions from 004-l again, updated by this experiment, and state
whether rewritten HOME/TMPDIR was the harness fault. If governed execution is
not reached, explicitly state that no Local Coding defect has yet been tested.

## Publication contract

Push amendments to exact PR #6 branch; never create another PR or merge. Record
literal implementation head after all non-report work is remote. Atomically
publish exactly one immutable
`oap/reports/004-m-reconcile-native-codex-environment.md`; SELF must be the sole
final commit, its first parent must equal the implementation head, it must change
only that report, and it must be remote PR head before response FIFO `OK`.

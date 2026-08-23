# OAP Work Order — 004-o

## Objective

Amend objective-004 PR #6 in one blocker-resolution round to test the ordinary
Codex 0.149.0 model→shell-tool execution path with truly equivalent
danger-full-access and workspace-write controls for `/usr/bin/true`, localize
the existing `not_found` classification to its actual layer, and immediately
resume exact dependency plus governed/cache-reuse acceptance if workspace-write
succeeds. Do not modify Local Coding product code.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`
- Numeric objective / round: `004` / `004-o`
- PR mode: `AMEND_EXISTING_PR`
- Existing PR: #6, `https://github.com/ulfe-lmi/slaif-local-coding/pull/6`
- Required base: `main` at `7a2c36a0a40958a6059a765c2f9d5e5bf4ddc161`
- Required head: `oap/004-real-codex-governed-e2e`
- Current verified remote head / `004-n` SELF:
  `fcd45a0aa0cef326143ece0f4f39f7957fa1943c`
- Prior implementation SHA:
  `f24a0509448dddf9185121c55fc9461425aa2c2c`, verified sole parent of SELF.
- PR state: OPEN/non-draft/MERGEABLE-CLEAN; final report-head `test` SUCCESS.
- Required action: **NO NEW PR**; no coding merge/auto-merge.

## Strategic context

Preserve the correction trail:

- 004-j overclaimed from a handcrafted raw-bubblewrap probe;
- 004-l corrected it and proved there is no nested outer sandbox;
- 004-l/m native `:workspace` helper calls failed before `true`;
- 004-n's native `:workspace` and native `:danger-full-access` helper controls
  both failed with `not_found`, so the failure is not isolated to workspace
  policy and the special helper may not represent ordinary Codex tool use;
- dependency `cat`, adapter 18031, governed model, sentinel, and cache reuse
  remain untested; no Local Coding defect exists in evidence.

Official OpenAI documentation distinguishes noninteractive `codex exec` with
model-generated commands from the special `codex sandbox` developer command.
This round tests the former. No raw bubblewrap/unshare work is allowed.

## Exact ordinary-command topology

Use the host-direct OAP coding process to launch the installed Codex 0.149.0
binary in noninteractive `exec --json --ephemeral` mode against a fresh private
synthetic Git repository and a direct, bounded, authenticated local-Qwen
provider on protected loopback 18020. This qualification traffic does not pass
through Local Coding.

The model prompt must require exactly one ordinary shell-tool call with exact
command `/usr/bin/true`, wait for the result, then return one fixed synthetic
acknowledgment. Disable/enable only the same known command-tool feature setting
for both controls. Do not use `codex sandbox`, raw bwrap, or a handcrafted
command runner for the decisive A/B experiment.

## A/B equivalence contract

Create one fixture, one disposable CODEX_HOME/config/catalog, one direct model
provider, one prompt, and one parser contract. Run both controls serially with
`--ephemeral` so no session state persists. Assert and report a fingerprint over
all fields below excluding only sandbox mode:

```text
Codex binary/version/hash
cwd and fixture identity hash
HOME/CODEX_HOME/TMPDIR classes
environment-variable name allowlist
provider/model/catalog/config hashes
prompt hash/length
requested executable /usr/bin/true
approval policy never
tool feature flags and tool schema/catalog
noninteractive/JSON/ephemeral flags
timeout/output bounds
event/parser version
```

The A/B equivalence fingerprint must match exactly. Also record full normalized
argv hashes and normalized argv templates with `<fixture>`/`<codex-home>`
placeholders. If equivalence cannot be established, stop with
`ab_equivalence_unproven`; do not attribute differences to sandbox mode.

## Minimal decision tree

### B — ordinary danger-full-access control first

Run exactly one real Codex session with:

```text
codex exec --sandbox danger-full-access --ask-for-approval never ...
model requests shell command /usr/bin/true exactly once
```

This is `UNSANDBOXED_CONTROL_ONLY`, never acceptance evidence. Do not use
`--dangerously-bypass-approvals-and-sandbox` for Codex-under-test.

- If B fails, do not run A. Isolate the first ordinary-path failure and stop
  before Local Coding.
- If B succeeds with one actual `/usr/bin/true` execution and exit 0, run A.

### A — ordinary workspace-write

Run the identical real Codex session, changing only sandbox mode to
`workspace-write`.

- If A fails, classify a genuine `ordinary_codex_workspace_write_blocker` only
  after the equivalence fingerprint passes and B succeeded.
- If A succeeds with exact command and exit 0, stop command diagnosis and move
  immediately to the dependency read.

Maximum qualification model calls before dependency read: two (B then A). No
retries, alternate prompts, or third control.

## Prove the real origin of `not_found` or any replacement failure

For each control, retain raw JSONL/stdout/stderr only inside bounded unlinked or
caller-owned temporary storage until evidence extraction. Never commit, log, or
report raw content. Independently parse the bounded raw event structure and
return only:

- Codex process exit/status/timeout and stream hashes/lengths;
- model tool request count/name and exact-command equality/hash;
- event item ID/type and lifecycle started/completed/failed counts;
- actual command representation and `/usr/bin/true` equality boolean;
- command exit/status and bounded output hash/length;
- parser recognized/rejected counts and fixed reason;
- classification origin:
  `codex_startup | model_no_shell_call | model_wrong_command |
   tool_unavailable | codex_command_execution | event_parser |
   wrapper_exit_translation | success | unresolved_with_fixed_evidence`;
- first meaningful fixed stderr/event class/subclass and structural location,
  without raw text.

Before runs, prove `/usr/bin/true` exists, is regular, executable, and that the
prompt/requested command is exactly `/usr/bin/true`. Success requires an actual
ordinary command event for that exact path with exit 0; a model acknowledgment
alone is insufficient.

If B fails, compare only against the already-running normal OAP Codex execution
surface using sanitized facts: invocation form, model/provider/profile class,
CODEX_HOME/HOME/TMPDIR class, tool feature/schema, JSON/noninteractive mode,
PATH/environment names, and sandbox/bypass label. Do not launch additional
models, read raw historical prompts/tool output, or inspect unrelated host
state. Identify the smallest plausible surface difference supported by facts;
do not implement a speculative fix.

## Exact dependency and governed acceptance after A success

### Dependency read

Using the same known-good ordinary workspace-write configuration, run exactly
one real Codex invocation whose model calls the ordinary shell tool exactly once
with `cat GOVERNANCE-DEPENDENCY.md`. Require successful lifecycle, exit 0, and
byte-for-byte/SHA-256/length equality with the fixture. No prompt sentinel token.

### Governed Local Coding E2E

After exact dependency success, start the repo candidate adapter on loopback
18031 and run exactly two actual Codex 0.149.0 workspace-write/approvals-never
invocations against the same fixture/principal/session/repository/cache:

1. First: exactly one successful dependency read, zero command failures,
   crossing-boundary byte equality, effective-root observation, delegated
   acquisition, required compilation/cache miss and compiler-model attempts,
   stable constitution injection, and exact hidden dependency-derived sentinel.
2. Second: successful read/sentinel again, persistent root/dependency cache
   reuse, unchanged compiler-model attempt count when no new compilation is
   required, injection and provenance correct.

No retry or third governed call. Stop 18031 afterward. If a gate fails, report
the first product-boundary failure and do not implement a product fix in this
round.

## Known-normal comparison

B success itself establishes a known-working ordinary Codex shell execution in
the OAP harness. If B fails, use only sanitized facts from the current working
outer OAP Codex session as the known-normal comparison. State explicitly that
the outer session uses an OpenAI GPT-5.6 profile and sandbox bypass and may use a
different code-mode/unified execution surface; therefore it is a falsification
signal, not proof that the disposable local-Qwen noninteractive path is valid.

Do not run another historical/profile matrix or another diagnostic objective.

## Completeness and claims

Keep objective 004 at 15% and branch readiness ~74% on any control, workspace,
dependency, or governed failure. Do not lower Local Coding completeness because
an external qualification dependency fails. Only exact B+A success, dependency
bytes, and both governed/cache invocations may raise objective 004 to 40% and
branch readiness ~79%. Danger-control or diagnostic success receives no credit.

## Tight implementation scope

Use existing repo-only fixture/process/event helpers. Expected work is a small
ordinary-command runner/result contract, sandbox parameterization, independent
event-origin assertions, focused A/B equivalence/gating tests, and outcome docs/
transcript. No new module, general diagnostic subsystem, raw sandbox code,
adapter diagnostic, fallback, or production runtime change. Remove now-unused
special-helper branches if safe. Helper+test line growth must be justified and
materially smaller than 004-n's growth.

## Explicit non-goals

No Local Coding product code change; no raw bubblewrap/unshare/kernel/seccomp
investigation; no host/package/Codex/profile/system mutation; no danger control
as acceptance; no bypass flag for Codex-under-test; no protected Qwen/vLLM/
model/key/network/firewall/VPN/systemd mutation; no compaction, vision, gateway,
production, multi-user, or cutover claim; no prior OAP rewrite.

## Acceptance criteria

1. One ordinary Codex model→shell path B run proves exact `/usr/bin/true` exit 0
   or precisely localizes the first failure before Local Coding.
2. A runs only after B success; A/B equivalence is cryptographically/factually
   established with sandbox mode as the sole difference.
3. `not_found` or replacement classification is traced to an exact event/process/
   parser/wrapper layer, not inferred from a generic regex alone.
4. On B failure, the known-normal outer Codex difference is reported narrowly
   and the round stops with no A, dependency, adapter, or product change.
5. On A success, exact dependency read runs immediately; exact bytes/hash/length
   are mandatory before adapter acceptance.
6. After dependency success, exactly two governed calls prove observation,
   acquisition, compilation, injection, hidden sentinel, persistent cache reuse,
   and no unnecessary compiler-model call.
7. No product change occurs; first external or product-boundary failure is
   stated truthfully.
8. Completeness stays 15%/~74% on failure and becomes 40%/~79% only on full
   success.
9. Focused equivalence/event-origin/privacy/gating/cache tests and all exact
   local/final CI gates pass without material helper bloat.

## Required verification

Record exact lock check, frozen sync, Ruff check/format, mypy, focused E2E tests,
full pytest, build, wheel/sdist boundary, compileall, shell syntax, and diff
check. Include normalized argv/fingerprints, executable facts, effective config/
environment-name facts, raw-boundary hashes/lengths, structural event origin,
model/control call counts, if reached dependency and per-invocation adapter/
compiler/cache evidence, secret/raw/private-path scan, cleanup, protected-host
snapshot, scoped diff, and current GitHub checks. Wait for report-head CI.

## Protected live-host boundary

Qualification may make at most B+A+dependency bounded authenticated calls
directly to protected 18020; governed acceptance may make exactly two further
calls through candidate 18031. Never change 18020, `qwen-serving`, model/
checkpoint/patches/venv/launch flags, keys, systemd, firewall/VPN/network,
Codex installation/profiles, or host sandbox policy. Candidate 18031 is
repo-owned, loopback-only, and must stop after use.

## Local authority

Coding owns repo-only helper changes, private fixture/config, bounded direct
qualification calls, candidate lifecycle if reached, evidence extraction,
cleanup, and tests. Do not recruit the human or strategy as terminal operator.

## Required final answers

1. Can ordinary Codex 0.149.0 execute `/usr/bin/true` under danger-full-access?
2. Can it execute `/usr/bin/true` under workspace-write?
3. Were A/B identical except sandbox mode?
4. Where exactly did `not_found` or the actual failure originate?
5. Did the harness exercise the same ordinary command path as normal Codex use?
6. What differs from the known-working outer Codex invocation?
7. Was the delegated dependency read?
8. Was Local Coding reached?
9. Did governed E2E and cache reuse run/pass?
10. What is the first blocker, and is it inside or outside Local Coding?

## Publication contract

Push amendments to exact PR #6 branch; never create another PR or merge. Record
literal implementation head after all non-report work is remote. Atomically
publish exactly one immutable
`oap/reports/004-o-ordinary-codex-shell-control.md`; SELF must be the sole final
commit, its first parent must equal the implementation head, it must change only
that report, and it must be remote PR head before response FIFO `OK`.

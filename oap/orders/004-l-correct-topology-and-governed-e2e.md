# OAP Work Order — 004-l

## Objective

Amend objective-004 PR #6 in one corrective round to supersede the overbroad
004-j/004-k sandbox conclusion, document the actual OAP execution topology, and
test the intended product property through Codex 0.149.0's own host-direct
`workspace-write` execution path. If native `true` and exact dependency `cat`
pass, immediately run the two-invocation governed E2E/cache-reuse acceptance
sequence. Do not add another diagnostic framework or alter Local Coding absent
direct product-defect evidence.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`
- Numeric objective / round: `004` / `004-l`
- PR mode: `AMEND_EXISTING_PR`
- Existing PR: #6, `https://github.com/ulfe-lmi/slaif-local-coding/pull/6`
- Required base: `main` at `7a2c36a0a40958a6059a765c2f9d5e5bf4ddc161`
- Required head: `oap/004-real-codex-governed-e2e`
- Current verified remote head / `004-k` SELF:
  `a29f3f97e61ce3bf40de86259798a34cce8db2b8`
- Prior implementation SHA:
  `349a0fda7777870adc79952f9a77201470565b3`, verified sole parent of SELF.
- PR state: OPEN/non-draft/MERGEABLE-CLEAN; final report-head `test` SUCCESS.
- Required action: **NO NEW PR**; no coding merge/auto-merge.

## Human correction and independently verified topology

The human reports normal direct Codex use on this host, falsifying any
unqualified host-wide bubblewrap claim. Strategic review independently verified:

```text
OAP strategic Codex: --dangerously-bypass-approvals-and-sandbox
OAP coding Codex:    --dangerously-bypass-approvals-and-sandbox
outer coding PID:    Seccomp=0, NoNewPrivs=0
outer namespaces:    host initial user/mount/network/PID namespace IDs
```

Therefore the 004-j direct bubblewrap child was **not** nested inside an outer
Codex OS sandbox. It was launched host-direct by an unsandboxed OAP coding
process. No escalation/escape mechanism is needed or authorized for this round.

However, 004-j hand-built a raw command containing `bwrap --unshare-all` and
observed loopback-interface bootstrap failure around `RTM_NEWADDR`. That proves
only that this constructed all-namespace/network probe fails in this context.
It does **not** establish that the host/kernel cannot support ordinary Codex or
every Codex sandbox configuration. The historical classifications
`bubblewrap_kernel_runtime_unsupported` in 004-j and repeated 004-k prose are
overbroad and must be explicitly superseded, not silently preserved.

Historical local session metadata also shows the recent OAP sessions used
`danger-full-access`; it does not independently prove successful command use
under the exact `workspace-write` policy. This round supplies that missing
experiment.

## Bounded scope

### A. Durable correction without rewriting history

Preserve every prior order/report byte. Add current README/TESTING/completeness
language stating:

1. observed: raw `bwrap --unshare-all` failed during loopback namespace setup;
2. previously inferred: host/kernel bubblewrap runtime unsupported;
3. correction: that inference was too broad because the handcrafted probe is
   not the acceptance topology or necessarily Codex's native policy path;
4. established: the OAP parent was host-direct/unsandboxed, so the evidence is
   not a nested-outer-sandbox artifact;
5. unknown until this round: whether Codex 0.149.0's actual host-direct
   workspace-write path can run commands and whether governed Local Coding E2E
   passes.

Use the narrower historical description
`raw_bwrap_unshare_all_loopback_bootstrap_failed`. Do not retain
`bubblewrap_kernel_runtime_unsupported` as a current conclusion or product/
host capability statement.

### B. Actual Codex workspace-write preflight only

From the already host-direct OAP coding process, use Codex 0.149.0's own native
sandbox execution interface and exact `workspace-write`/`:workspace` policy.
Do not call raw `bwrap`, `unshare`, namespace utilities, or a handcrafted
approximation.

Use one fresh private synthetic repository and disposable Codex state. Execute
the minimum sequence, stopping on first failure:

1. native workspace-write `true`;
2. native workspace-write `cat GOVERNANCE-DEPENDENCY.md`;
3. require exit success and byte-for-byte equality, SHA-256 equality, and length
   equality with the fixture dependency.

Record only CLI version, exact policy labels, parent topology booleans,
exit/status, bounded hashes/lengths, byte-identity, and fixed failure class.
No raw paths, argv, config, source, stdout/stderr, or credentials in returned
facts/report. These are no-model native Codex sandbox commands; spend no model
call until all three steps pass.

Do not use `--dangerously-bypass-approvals-and-sandbox` for Codex-under-test.
The under-test policy remains `workspace-write` with approvals `never`. The
outer OAP coding agent's existing host-direct bypass is execution topology, not
an acceptance shortcut, and must be recorded distinctly.

If the actual Codex path fails, stop this round with exact first-failure
evidence, zero governed/model calls, and no product changes. Only that outcome
may justify a later diagnostic order; do not speculate or repair host/package
state now.

### C. Immediate governed E2E after preflight success

If and only if native `true` and exact dependency `cat` succeed, stop sandbox
diagnosis immediately. Start the repo candidate adapter on loopback 18031 using
the protected upstream on 18020 and run exactly two actual Codex 0.149.0
invocations against the same private fixture/session/cache:

#### First invocation

- Codex-under-test uses its own `workspace-write` sandbox and approvals never;
- prompt does not contain the expected sentinel token;
- exactly one successful ordinary dependency read completes with zero command
  failures;
- crossing-boundary dependency bytes/hash/length equal the fixture;
- adapter observes the effective root and delegated dependency;
- compiler/cache evidence shows required root/dependency compilation on miss;
- stable constitution injection occurs;
- final response exactly satisfies the dependency-derived sentinel.

#### Second invocation

- same fixture, opaque identity/session/repository, and persistent cache;
- exactly one successful ordinary dependency read and sentinel again;
- dependency/root cache reuse is observed;
- compiler model-attempt count does not increase unnecessarily;
- injection and ordinary tool lifecycle remain successful.

No retries or third invocation. If either invocation fails, report the first
actual failing gate. Do not add adapter diagnostics, fallbacks, abstractions, or
runtime changes unless the evidence directly identifies a Local Coding product
defect; this order does not authorize implementing such a newly discovered
defect.

### D. Truthful completeness reset/reassessment

The prompt-leaked 004-a sentinel and failed 004-c through 004-j sequences do not
constitute valid governed E2E completion. Before outcome accounting, correct
objective 004 from 35% to its pre-E2E evidence baseline **15%**, and branch
readiness from ~78% to **~74%**. Diagnostic elaboration receives no completion
credit.

Only if the complete native preflight plus both governed invocations and cache-
reuse gates pass may objective 004 become **40%** and branch readiness **~79%**.
Remaining gaps must still name compaction, vision-capable E2E, broader security
hardening/observability, and systemd candidate proof. Any failure leaves the
corrected 15%/~74% values.

### E. Tight implementation and evidence

Use the repo-only helpers created by 004-k. Remove raw-bubblewrap execution code
and current overbroad outcome branches/tests if no longer needed for retained
behavior; immutable reports remain the audit trail. Add only the minimal native
preflight/topology facts and tests required by this order. No new general
diagnostic framework. Report helper/test line delta and keep it materially
smaller than the post-004-k baseline unless direct evidence requires otherwise.

## Explicit non-goals

No raw bubblewrap/unshare probe; no outer sandbox escape/escalation; no
danger-full-access for Codex-under-test; no host/kernel/container/package/Codex
repair or mutation; no protected Qwen/vLLM/model/key/network/firewall/VPN/
systemd/profile change; no forced compaction, vision, gateway, production,
multi-user, or cutover claim; no rewrite of prior OAP artifacts.

## Acceptance criteria

1. Current docs/completeness explicitly supersede the 004-j/004-k overclaim and
   accurately distinguish host, outer OAP, Codex-under-test, and Local Coding.
2. Sanitized `/proc`/wrapper evidence proves the outer OAP coding process is
   host-direct (no outer Codex sandbox); no nested-sandbox claim remains.
3. Codex 0.149.0's native workspace-write path, not raw bwrap, runs `true` then
   exact dependency `cat`, or stops with the exact first native failure.
4. Zero model calls occur before exact cat byte/hash/length identity.
5. After native success, exactly two governed invocations prove lifecycle,
   provenance, observation/acquisition/compilation/injection, sentinel, and
   persistent cache reuse with no unnecessary compiler-model call.
6. No Local Coding product change is made absent a directly evidenced product
   defect; a newly discovered defect is reported, not speculatively fixed.
7. Completeness is 15%/~74% on any failure and 40%/~79% only on full success,
   with remaining gaps explicit.
8. Repo-only helper changes are minimal; raw-bwrap obsolete code/current
   overclaim is removed while historical OAP evidence remains immutable.
9. Focused topology/native-preflight/gating/privacy/cache tests and all exact
   local gates/final CI pass.

## Required verification

Record exact lock check, frozen sync, Ruff check/format, mypy, focused E2E tests,
full pytest, build, wheel/sdist boundary, compileall, shell syntax, and diff
check. Include wrapper-flag and `/proc` namespace/seccomp/NoNewPrivs facts;
native-preflight fixed evidence; model-call count; if run, per-invocation
sanitized adapter metrics and compiler-attempt deltas; secret/raw/private-path
scan; scratch cleanup; scoped diff; protected-host before/after snapshot; and
current GitHub checks. Wait for final report-head CI.

## Protected live-host boundary

Read-only discovery and bounded authenticated calls are allowed. Candidate
adapter use is loopback 18031 only and must stop after testing. Never alter port
18020, `qwen-serving`, model/checkpoint/patches/venv/launch flags, API keys,
systemd, firewall/VPN/network bindings, Codex/bubblewrap installation, host
sandbox/kernel/container settings, or active Codex profiles. Never edit/restore
protected runtime logs.

## Local authority

Coding owns safe repo-local helper correction, temporary fixtures, native Codex
preflight, candidate-process lifecycle, bounded calls, cleanup, and tests. Do
not recruit the human or strategy as terminal operator. No host escalation is
needed because the outer coding process is already verified host-direct.

## Required report answers

Answer explicitly with evidence:

1. Was 004-j's host-wide `bubblewrap_kernel_runtime_unsupported` conclusion
   justified?
2. Was its raw bwrap probe host-direct or nested inside an outer sandbox?
3. Was the observed failure a nested-sandbox artifact?
4. Can host-direct Codex 0.149.0 use its own native workspace-write path here?
5. In the corrected topology, does governed Local Coding E2E and cache reuse
   pass?
6. If not, what is the first actual remaining Local Coding/product defect—or is
   the first failure still before the product boundary?

## Publication contract

Push amendments to exact PR #6 branch; never create another PR or merge. Record
literal implementation head after all non-report work is remote. Atomically
publish exactly one immutable
`oap/reports/004-l-correct-topology-and-governed-e2e.md`; SELF must be the sole
final commit, its first parent must equal the implementation head, it must change
only that report, and it must be remote PR head before response FIFO `OK`.

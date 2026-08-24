# OAP Work Order — 004-j

## Objective

Amend objective-004 PR #6 to distinguish a Codex sandbox executable-visibility
or installation-layout defect from an underlying bubblewrap/kernel runtime
failure using a final bounded, read-only, no-model probe set. If a supported
executable spelling resolves the helper, prove the governed read; otherwise
return the exact external boundary without mutating the host.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`
- Numeric objective / round: `004` / `004-j`
- PR mode: `AMEND_EXISTING_PR`
- Existing PR: #6, `https://github.com/ulfe-lmi/slaif-local-coding/pull/6`
- Required base: `main` at `7a2c36a0a40958a6059a765c2f9d5e5bf4ddc161`
- Required head: `oap/004-real-codex-governed-e2e`
- Current verified remote head / `004-i` SELF:
  `499bb6fdbcde0f824eec87c8dda6225eb9874712`
- Prior implementation SHA:
  `e176d235d75b2ba956b65af33470dd1a6c89c49f`, verified sole parent of SELF.
- PR state: OPEN/non-draft/MERGEABLE-CLEAN; final report-head `test` SUCCESS.
- Required action: **NO NEW PR**; no coding merge/auto-merge.

## Verified gap

The correctly formed Codex 0.149.0 `:workspace` helper cannot run a fixed
`/bin/true` probe even though that executable is locally present, regular,
executable, and non-symlink. It returns fixed `not_found` before any workspace or
target test. This rules out the dependency and temporary-root hypotheses but
does not distinguish Codex helper path/install behavior from bubblewrap/kernel
runtime behavior.

## Bounded scope

### A. Installed executable visibility

Record only fixed/hashed facts for the installed Codex launcher, its resolved
binary directory, system `bwrap`, and `true`/`cat` candidates:

- exists/regular/executable/symlink booleans;
- resolved basename class and same-file booleans for `/bin` versus `/usr/bin`
  candidates;
- binary version or SHA-256 where already safe and bounded;
- expected companion-name presence booleans, if the installed layout references
  companions; never report directory listings or full paths.

Do not edit/reinstall Codex, bubblewrap, PATH, profiles, permissions, packages,
kernel settings, or host files.

### B. Final no-model split

Run at most three additional no-model commands total, with existing time/output/
line/privacy bounds and no network:

1. Corrected Codex `:workspace` helper with the independently resolved real
   `true` executable path if it differs from `/bin/true`, otherwise relative
   `true` through the sanitized inherited PATH.
2. Only if needed, the corresponding resolved `cat` against the synthetic
   dependency in the same disposable repository.
3. A minimal direct system-bubblewrap probe executing fixed `true` with a
   read-only root view and disabled network/isolated namespaces, solely to
   classify bubblewrap/kernel viability. Use no writable host bind, shell,
   model, adapter, sudo, or protected path mutation.

The direct bubblewrap command must be constructed from fixed argv, run inside a
fresh caller-owned temporary boundary, and expose only exit/status, bounded
hash/length, and fixed diagnostic classes/subclasses. Raw argv paths,
environment, mount details, stdout/stderr, and private paths must not enter
tests/docs/report.

### C. Deterministic outcome

Classify exactly one:

```text
codex_helper_path_spelling_defect
codex_sandbox_installation_layout_defect
bubblewrap_kernel_runtime_unsupported
codex_helper_unresolved_external_failure
workspace_sandbox_available
```

Do not call a missing companion or path layout a kernel failure. Do not call a
direct bubblewrap failure a product-code regression. Focused tests must cover
the decision table, stopping budget, privacy, and negative ambiguity cases.

### D. Governed proof or external blocker

If a supported Codex helper path returns the exact dependency bytes, update only
the fixture command-path selection proven necessary and run at most two fresh
governed Codex invocations through candidate port 18031 with workspace-write,
approvals never, disposable state, and all lifecycle/provenance/cache/sentinel
gates.

If no supported helper path succeeds, run zero model calls and stop at the fixed
external boundary. Do not repair/reinstall/upgrade/downgrade Codex or bubblewrap
and do not mutate host sandbox/kernel/container configuration in this order.

Only the full governed gate may raise objective 004 from 35% to 40% and branch
readiness from ~78% to ~79%; otherwise preserve current values.

### E. Complexity discipline

Reuse the existing bounded probe/result machinery. Do not add another general
diagnostic framework or retain speculative branches after the boundary is
known. Remove newly introduced redundant/dead probe helpers when safe, while
preserving all prior public/tested contracts and immutable OAP history. Report
net production/test line impact and justify any material growth.

## Explicit non-goals

No package/CLI/bubblewrap reinstall or upgrade; no host/kernel/container change;
no danger-full-access, sandbox bypass, approval weakening, read-only
substitution, custom profile, sudo, broad filesystem trace, protected Qwen/
vLLM/model/key/network/firewall/VPN/systemd/profile mutation, compaction,
vision, gateway, production, multi-user, or cutover claim.

## Acceptance criteria

1. Sanitized installed-layout facts and at most three no-model probes separate
   Codex helper path/layout from direct bubblewrap/kernel viability.
2. One deterministic fixed outcome is supported without raw path/diagnostic/
   environment leakage or overclaim.
3. Any command-path correction is proven by exact helper byte identity; host or
   package remediation is not performed.
4. Governed calls run only after helper success, at most two, with every prior
   semantic/safety gate.
5. Focused tests cover argv safety, decision/stopping logic, privacy/bounds, and
   model gating.
6. Diagnostic implementation remains proportionate; redundant/dead scaffolding
   is removed where safe and net line impact is reported.
7. Documentation/completeness match the actual result.
8. All exact local gates and final implementation/report-head CI pass.

## Required verification

Record exact lock check, frozen sync, Ruff check/format, mypy, full pytest,
build, compileall, shell syntax, and diff-check statuses. Run focused sandbox
runtime/layout/decision/privacy/model-gate tests. Include secret/raw/private-path
scans, scratch-residue and scoped diff audits, current GitHub checks, and
protected-host before/after snapshot. Established opt-in live-suite skips remain
skips. Wait for final report-head CI.

## Protected live-host boundary

Read-only discovery and bounded authenticated calls are allowed. Candidate
adapter use is loopback 18031 only and must stop after testing. Never alter port
18020, `qwen-serving`, model/checkpoint/patches/venv/launch flags, API keys,
systemd, firewall/VPN/network bindings, Codex/bubblewrap installation, host
sandbox/kernel/container settings, or active Codex profiles. Never edit/restore
protected runtime logs.

## Local authority

Coding owns safe repo-local implementation, synthetic temporary probes, cleanup,
and tests. Do not recruit the human or strategy as terminal operator. Return a
genuine external remediation boundary to strategy/human rather than changing it.

## Publication contract

Push amendments to exact PR #6 branch; never create another PR or merge. Record
literal implementation head after all non-report work is remote. Atomically
publish exactly one immutable `oap/reports/004-j-sandbox-runtime-boundary.md`;
SELF must be the sole final commit, its first parent must equal the
implementation head, it must change only that report, and it must be remote PR
head before response FIFO `OK`.

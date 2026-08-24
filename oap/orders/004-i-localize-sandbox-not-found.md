# OAP Work Order — 004-i

## Objective

Amend objective-004 PR #6 to localize the corrected Codex sandbox helper's
`not_found` failure to command resolution, executable/root mapping, or the
disposable workspace location using a tiny no-model differential matrix. Apply
only an evidence-proven disposable-fixture correction, then permit the governed
proof solely if the same `:workspace` helper reads byte-identically.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`
- Numeric objective / round: `004` / `004-i`
- PR mode: `AMEND_EXISTING_PR`
- Existing PR: #6, `https://github.com/ulfe-lmi/slaif-local-coding/pull/6`
- Required base: `main` at `7a2c36a0a40958a6059a765c2f9d5e5bf4ddc161`
- Required head: `oap/004-real-codex-governed-e2e`
- Current verified remote head / `004-h` SELF:
  `1f125fd3255a8911414392a7d692f049720556f5`
- Prior implementation SHA:
  `91259bfdae6c1da3c2ca2791da196a40e23d003e`, verified sole parent of SELF.
- PR state: OPEN/non-draft/MERGEABLE-CLEAN; final report-head `test` SUCCESS.
- Required action: **NO NEW PR**; no coding merge/auto-merge.

## Verified gap

`004-h` ran the correctly formed installed-CLI helper with built-in
`:workspace`, semantic `workspace-write`, no positional platform token, and
bounded meaningful-line parsing. It exited 1 with fixed class/subclass
`not_found`/`not_found`, while the target existed as a regular in-root file.
No model call ran. That evidence does not yet distinguish:

```text
helper command/executable mapping failure
workspace root not mapped inside sandbox
temporary-root policy incompatibility
target path mapping failure
```

Do not label this host/kernel sandbox incompatibility without differential
evidence.

## Bounded scope

### A. Sanitized executable and root facts

Before helper calls, record only fixed/hashed facts:

- `/bin/true`, `/bin/pwd`, and `/bin/cat` exist/regular/executable/symlink
  booleans and resolved-path basename class; no full paths;
- disposable repository and target containment, type, mode class, byte length,
  and hash;
- temporary-root class `system_tmp | repo_owned_scratch | other`, never its raw
  path;
- installed Codex version and selected `:workspace` profile facts.

Do not report raw symlink targets, environment values, private paths, source, or
diagnostics.

### B. No-model differential matrix

Run at most four corrected `codex sandbox --permission-profile :workspace`
helper calls total, stopping once the boundary is proven:

1. `/bin/true` in the fresh system-temporary repository;
2. `/bin/pwd` in that repository if needed;
3. `/bin/cat GOVERNANCE-DEPENDENCY.md` in that repository if prerequisites
   permit;
4. the same `/bin/cat` against a fresh private caller-owned scratch repository
   located beneath the current product checkout, only if the system-temp result
   indicates root mapping rather than executable failure.

Every call must keep fixed time/output/line bounds and return only exit/status,
hash/length, first meaningful class/subclass, command-kind label, root-class
label, and byte-identity where applicable. No shell wrapper, network, model,
adapter, sudo, host mutation, raw output, or retry loop.

The repo-owned scratch path must be random, private mode, excluded from staging,
verified caller-owned, and removed after evidence extraction. It may contain
synthetic data only. Never clean or delete any pre-existing path.

### C. Deterministic localization

Classify exactly one:

```text
helper_executable_mapping_failure
workspace_mapping_failure_system_tmp
target_mapping_failure
workspace_sandbox_available_system_tmp
workspace_sandbox_available_repo_scratch
host_sandbox_runtime_failure
unresolved_with_fixed_evidence
```

Tests must prove the decision table and that no single `not_found` result is
overinterpreted. A host runtime classification requires the trivial executable
probe to reach a fixed sandbox-runtime diagnostic, not merely fail to find a
target.

### D. Evidence-proven correction and governed gate

If only the system temporary root is unmapped and repo-owned scratch succeeds,
change the E2E fixture root to a private caller-owned repo-scratch boundary with
guaranteed cleanup and no Git staging. Document the portability limitation.
Do not make that change for any other outcome.

After and only after a `:workspace` helper returns the exact dependency bytes,
run at most two fresh governed Codex invocations through the candidate adapter
on 18031 with workspace-write, approvals never, disposable `CODEX_HOME`, and all
existing lifecycle/provenance/cache/sentinel gates. Otherwise run zero model
calls.

If and only if the full governed gate passes—exactly one intended completed
read, zero command failures, observed-byte hash/length, cache source equality,
and dependency-derived sentinel—raise objective 004 from 35% to 40% and branch
readiness from ~78% to ~79%. Otherwise keep values unchanged.

## Explicit non-goals

No danger-full-access, sandbox bypass, approval weakening, read-only
substitution, custom profile invention, host/kernel/container repair, broad
filesystem probing, protected Qwen/vLLM/model/key/network/firewall/VPN/systemd/
profile mutation, compaction, vision, gateway, production, multi-user, or
cutover claim. No rewrite of prior OAP artifacts.

## Acceptance criteria

1. Sanitized facts distinguish executable availability from system-temp and
   repo-scratch workspace/target mapping.
2. At most four no-model helper calls implement the exact stopping matrix and
   produce one deterministic localization without raw content/path leakage.
3. Any fixture-location correction is justified by a successful repo-scratch
   byte-identical control and includes private ownership and exact cleanup.
4. Governed model calls run only after helper byte identity, at most two, with
   all prior safety and semantic gates.
5. Focused tests cover the matrix, stopping, bounds, privacy, scratch ownership/
   cleanup, classification, and model gate.
6. Documentation/completeness state the actual result and portability limit.
7. All exact local gates and final implementation/report-head CI pass.

## Required verification

Record exact lock check, frozen sync, Ruff check/format, mypy, full pytest,
build, compileall, shell syntax, and diff-check statuses. Run focused sandbox
matrix/localization/scratch-cleanup/model-gate tests. Include secret/raw/private-
path scans, scoped diff audit, Git status proving no scratch residue, current
GitHub checks, and protected-host before/after snapshot. Established opt-in live
suite skips remain skips. Wait for final report-head CI.

## Protected live-host boundary

Read-only discovery and bounded authenticated calls are allowed. Candidate
adapter use is loopback 18031 only and must stop after testing. Never alter port
18020, `qwen-serving`, model/checkpoint/patches/venv/launch flags, API keys,
systemd, firewall/VPN/network bindings, host sandbox/kernel/container settings,
or active Codex profiles. Never edit/restore protected runtime logs.

## Local authority

Coding owns safe repo-local implementation, synthetic temporary/scratch
fixtures, diagnostics, cleanup, and tests. Do not recruit the human or strategy
as terminal operator. Any required host mutation is outside this order and must
be reported.

## Publication contract

Push amendments to exact PR #6 branch; never create another PR or merge. Record
literal implementation head after all non-report work is remote. Atomically
publish exactly one immutable `oap/reports/004-i-localize-sandbox-not-found.md`;
SELF must be the sole final commit, its first parent must equal the
implementation head, it must change only that report, and it must be remote PR
head before response FIFO `OK`.

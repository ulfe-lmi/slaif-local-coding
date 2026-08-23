# OAP Work Order — 004-h

## Objective

Amend objective-004 PR #6 to correct the malformed `004-g` Codex sandbox
preflight, classify the first meaningful bounded diagnostic rather than a
warning preamble, and rerun the no-model workspace sandbox proof. Only after a
valid helper read succeeds may the existing bounded governed Codex proof run.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`
- Numeric objective / round: `004` / `004-h`
- PR mode: `AMEND_EXISTING_PR`
- Existing PR: #6, `https://github.com/ulfe-lmi/slaif-local-coding/pull/6`
- Required base: `main` at `7a2c36a0a40958a6059a765c2f9d5e5bf4ddc161`
- Required head: `oap/004-real-codex-governed-e2e`
- Current verified remote head / `004-g` SELF:
  `9b8efb292d6b1d3d082566b98e20c849d1598538`
- Prior implementation SHA:
  `1ee3c9b8ef1bac348d87eeec38ec89ab194caa87`, verified sole parent of SELF.
- PR state: OPEN/non-draft/MERGEABLE-CLEAN; final report-head `test` SUCCESS.
- Required action: **NO NEW PR**; no coding merge/auto-merge.

## Independent strategic review finding

`004-g` is PARTIAL and cannot establish its claimed same-policy helper result:

1. Installed Codex CLI 0.149.0 help says
   `codex sandbox [OPTIONS] [COMMAND]...`; it exposes no `linux` subcommand.
   The implementation instead builds `codex sandbox linux ...`, so `linux` is
   a positional command token, not a platform selector.
2. The official current configuration reference distinguishes sandbox mode
   `workspace-write` from built-in permission profile `:workspace`. The
   implementation passes `--permission-profile workspace-write`, which is not
   the documented built-in profile name.
3. The 302-byte stderr began with a warning. `_binary_stream_facts` retained
   only the first physical line for classification; warning filtering therefore
   produced fixed subclass `empty` and discarded the bounded meaningful line(s)
   needed to diagnose the actual exit.

Thus `unresolved_with_fixed_evidence` is not host-sandbox evidence. It is an
invalid-invocation/parser result and must not trigger host/kernel escalation.
Official references used for this correction:

- `https://learn.chatgpt.com/docs/developer-commands?surface=cli`
- `https://learn.chatgpt.com/docs/config-file/config-reference`

## Bounded scope

### A. Correct installed-CLI helper command

Build the no-model helper from the installed CLI contract, equivalent to:

```text
codex sandbox --permission-profile :workspace --cd <disposable-repository> --
  /bin/cat GOVERNANCE-DEPENDENCY.md
```

Use the actual supported short/long flags reported by 0.149.0. Do not include a
`linux` positional token. Do not use `workspace-write` as a permission-profile
name. Record fixed facts showing the requested built-in profile `:workspace`
and its semantic workspace-write policy; never report raw resolved config.

If the installed helper rejects `:workspace`, stop with exact fixed
`invocation_config_precedence_error` evidence. Do not guess another custom
profile, mutate user config, or fall through to unsandboxed execution.

### B. First meaningful diagnostic classification

Within the existing hard byte bound, scan a small fixed maximum number of
stderr/stdout lines and classify the first nonempty, non-warning line. Hash and
count the complete bounded stream as before. Never retain/return/report raw
lines. Prove with tests that:

- one or multiple warning preambles do not hide a following bwrap, permission,
  not-found, argv, or schema failure;
- warning-only streams remain `unavailable`/`empty`;
- line count/line length/output byte bounds hold;
- returned dataclasses/reports contain no raw diagnostic or private path.

### C. Rerun and gate governed work

Run exactly one corrected no-model helper preflight on a fresh disposable
fixture. If it produces exit 0 and byte-identical dependency output, classify
`workspace_sandbox_available` and then run at most two fresh actual Codex
invocations using the existing `workspace-write`, approvals-never, disposable
provider/repository, lifecycle/provenance/cache/sentinel gates.

If the corrected helper fails, run no model invocation. Report the exact fixed
meaningful diagnostic class/subclass and boundary classification. A genuine
`host_sandbox_bootstrap_unsupported` result requires a correctly formed helper
command plus a bounded diagnostic that directly supports it; otherwise use the
applicable invocation/root/unresolved class.

No danger-full-access, bypass, approval weakening, `read-only` substitution, or
host/kernel/container mutation is allowed.

### D. Outcome and documentation

If and only if a fresh governed attempt completes exactly one intended read,
zero failed commands, observed-byte provenance, cache source equality, and the
dependency-derived sentinel, update objective 004 from 35% to 40% and branch
readiness from ~78% to ~79%. Otherwise keep values unchanged and replace no
prior history; document this round's exact result.

Correct README language that currently describes `codex sandbox linux` as a
valid preflight. Preserve the immutable `004-g` order/report as historical
evidence; do not rewrite it.

## Explicit non-goals

No host/kernel/container repair; no custom permission-profile invention; no
danger-full-access or sandbox bypass; no protected Qwen/vLLM/model/key/network/
firewall/VPN/systemd/profile mutation; no compaction, vision, gateway,
production, multi-user, or cutover claim; no raw diagnostic persistence; no
rewrite of prior OAP artifacts.

## Acceptance criteria

1. Preflight argv matches installed CLI 0.149.0 and documented `:workspace`
   profile semantics, with no positional `linux` token.
2. Bounded first-meaningful-line parsing exposes the actual fixed diagnostic
   class/subclass after warning preambles without retaining raw text.
3. Exactly one corrected no-model preflight produces byte-identical success or
   a valid fixed failure classification.
4. Governed model attempts run only after helper success, at most two total,
   retaining all workspace-write/lifecycle/provenance/cache/sentinel gates.
5. Focused tests cover argv, config rejection, warning filtering, bounds,
   privacy, classification, and governed-run gating.
6. Documentation/completeness reflect the actual result without rewriting
   history or overclaiming host failure.
7. All exact local gates and final implementation/report-head CI pass.

## Required verification

Record exact lock check, frozen sync, Ruff check/format, mypy, full pytest,
build, compileall, shell syntax, and diff-check statuses. Run focused sandbox
argv/parser/classifier/gating tests. Include secret/raw/private-path scans,
scoped diff audit, current GitHub checks, and protected-host before/after
snapshot. The established opt-in live-suite skips remain skips. Wait for final
report-head CI.

## Protected live-host boundary

Read-only discovery and bounded authenticated calls are allowed. Candidate
adapter use is loopback 18031 only and must stop after testing. Never alter port
18020, `qwen-serving`, model/checkpoint/patches/venv/launch flags, API keys,
systemd, firewall/VPN/network bindings, host sandbox/kernel/container settings,
or active Codex profiles. Do not edit/restore runtime logs appended by bounded
calls.

## Local authority

Coding owns safe repo-local implementation, temporary fixtures, diagnostics,
and tests. Do not recruit the human or strategy as terminal operator. A genuine
host sandbox incompatibility is reported for later strategy/human decision; it
is not repaired in this order.

## Publication contract

Push amendments to exact PR #6 branch; never create another PR or merge. Record
literal implementation head after all non-report work is remote. Atomically
publish exactly one immutable
`oap/reports/004-h-correct-sandbox-preflight-invocation.md`; SELF must be the
sole final commit, its first parent must equal the implementation head, it must
change only that report, and it must be remote PR head before response FIFO
`OK`.

# OAP Work Order — 004-k

## Objective

Amend objective-004 PR #6 to remove the real-Codex E2E/sandbox diagnostic
harness from the shipped production package, consolidate superseded round-
specific probe machinery into maintainable repo-only test support, and perform a
focused security/privacy review of the remaining subprocess/raw-data boundaries.
Do not change adapter runtime behavior or attempt the externally blocked sandbox
repair.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`
- Numeric objective / round: `004` / `004-k`
- PR mode: `AMEND_EXISTING_PR`
- Existing PR: #6, `https://github.com/ulfe-lmi/slaif-local-coding/pull/6`
- Required base: `main` at `7a2c36a0a40958a6059a765c2f9d5e5bf4ddc161`
- Required head: `oap/004-real-codex-governed-e2e`
- Current verified remote head / `004-j` SELF:
  `d8a53ae0faf6b4ff43847cfb481c9a87461cf435`
- Prior implementation SHA:
  `c18280b38f0e268562f614e10d17d1a14fead8f7`, verified sole parent of SELF.
- PR state: OPEN/non-draft/MERGEABLE-CLEAN; final report-head `test` SUCCESS.
- Required action: **NO NEW PR**; no coding merge/auto-merge.

## Independently verified cleanup need

Current PR state has:

```text
src/slaif_local_coding/e2e.py: 3406 lines
tests/test_e2e.py: 2000 lines
production imports of slaif_local_coding.e2e: zero
test imports: tests/test_e2e.py only
wheel payload: slaif_local_coding/e2e.py, 128849 bytes
```

The module contains subprocess execution, temporary credentials/configuration,
raw event parsing, sandbox/bubblewrap probes, and host-layout diagnostics. Those
are valuable repo-only verification tools but are not adapter runtime behavior
and should not expand the installed production attack surface. Rounds 004-g
through 004-j also accumulated intermediate probe APIs/tests after the final
external boundary became known.

## Bounded scope

### A. Remove test-only machinery from production artifacts

- Move the real-Codex fixture/launcher/event/sandbox diagnostic support out of
  `src/slaif_local_coding` into repo-only test support, preferably coherent
  modules under `tests/helpers/`.
- Delete `src/slaif_local_coding/e2e.py` after all imports migrate.
- Do not expose equivalent code from another installed package/module or console
  entry point.
- Preserve only imports from production modules genuinely needed to exercise
  real adapter contracts; never duplicate production compiler/cache logic into
  test helpers.
- Update README/TESTING documentation to describe this as repository test
  support, not a production library API.

Prove the built wheel contains no real-Codex launcher, sandbox/bubblewrap probe,
temporary credential/config writer, or `e2e.py` equivalent. Inspect the sdist
truthfully: repo test support may remain in source distributions if packaging
policy includes tests, but it must be labeled non-runtime.

### B. Consolidate accumulated diagnostics

Preserve the current useful capabilities:

- private synthetic fixture and disposable Codex home;
- bounded real-Codex launcher and sanitized event/lifecycle/provenance facts;
- successful-read/sentinel/cache gate;
- final bounded sandbox-runtime boundary probe and its fixed classification;
- privacy/bounds/cleanup controls.

Remove or collapse superseded intermediate 004-g/004-h/004-i wrappers,
duplicated dataclasses, speculative classifications, unused branches, and tests
that merely restate implementation internals rather than a retained behavioral
contract. Keep the immutable orders/reports unchanged as historical evidence.

Prefer a few cohesive helper modules over another monolith. Report before/after
line counts for shipped production, repo-only helpers, and tests. Net production
package must decrease by the full current E2E module. Repo-only helper+test lines
must not increase; any failure to materially reduce the accumulated 5,406-line
helper/test total requires explicit evidence and strategic review.

### C. Focused security/privacy review

Review every retained subprocess/temp/raw-data boundary and prove:

- fixed argv or strictly validated bounded argv construction; no shell=True;
- explicit timeout, stdin closure, bounded stdout/stderr/events, and process
  cleanup/cancellation;
- private temporary modes/ownership, no unsafe pre-existing-path deletion, and
  exact scratch cleanup;
- credentials referenced only by environment name/value at subprocess boundary,
  never committed/logged/reported/hashed as identity;
- raw prompts/source/events/model output/diagnostics remain in caller-owned
  temporary/unlinked storage and never enter returned dataclasses, logs,
  metrics, docs, reports, or exception strings;
- no protected-host mutation or sandbox bypass path exists.

Add/fix focused negative tests for any identified gap. Report concrete findings
and remediation; do not claim a broad security audit or certification.

### D. Preserve outcomes and external blocker

Preserve the verified `bubblewrap_kernel_runtime_unsupported` result as a
repo-test limitation and keep objective 004 at 35% / branch readiness ~78%.
Run no governed model, candidate adapter, direct bubblewrap, or protected
upstream calls in this cleanup round. No host/package remediation is authorized.

## Explicit non-goals

No adapter request/response/compiler/cache/image behavior change; no Codex or
bubblewrap install/upgrade/repair; no host/kernel/container change; no
danger-full-access or sandbox bypass; no protected Qwen/vLLM/model/key/network/
firewall/VPN/systemd/profile mutation; no compaction, vision, gateway,
production, multi-user, or cutover claim; no rewrite of prior OAP artifacts.

## Acceptance criteria

1. Production `src` and wheel contain no real-Codex E2E/sandbox diagnostic
   module or equivalent runtime payload; production imports remain clean.
2. Repo-only helpers retain the current necessary E2E gates and final external
   boundary while superseded/duplicated scaffolding is materially consolidated.
3. Focused security/privacy review covers every retained subprocess/temp/raw
   boundary, with negative tests and exact findings.
4. No shell execution, unbounded output/process, credential leak, unsafe cleanup,
   sandbox bypass, or protected-host mutation path remains.
5. Before/after line counts and wheel/sdist contents are reported truthfully;
   production decreases by the full E2E module and helper+test total does not
   grow.
6. README/TESTING and completeness accurately label repo-only support and the
   unchanged external sandbox blocker/readiness.
7. All existing behavior tests, exact local gates, and final implementation/
   report-head CI pass.

## Required verification

Record exact lock check, frozen sync, Ruff check/format, mypy, full pytest,
build, compileall, shell syntax, and diff-check statuses. Run focused helper
security/privacy/bounds/cleanup tests. Inspect wheel and sdist member lists;
prove no installed E2E diagnostic payload. Include import scan, line-count
comparison, secret/raw/private-path scan, subprocess/shell audit, scratch-residue
check, scoped diff audit, and current GitHub checks. No live model/service call is
required; label it NOT RUN (cleanup-only). Wait for final report-head CI.

## Protected live-host boundary

Only read-only listener/service/profile facts may be checked. Never start the
candidate adapter or call/mutate port 18020, `qwen-serving`, model/checkpoint/
patches/venv/launch flags, API keys, systemd, firewall/VPN/network bindings,
Codex/bubblewrap installation, host sandbox/kernel/container settings, or active
Codex profiles.

## Local authority

Coding owns repo-local refactoring, packaging inspection, tests, and safe
temporary cleanup. Do not recruit the human or strategy as terminal operator.

## Publication contract

Push amendments to exact PR #6 branch; never create another PR or merge. Record
literal implementation head after all non-report work is remote. Atomically
publish exactly one immutable
`oap/reports/004-k-unship-and-consolidate-e2e-diagnostics.md`; SELF must be the
sole final commit, its first parent must equal the implementation head, it must
change only that report, and it must be remote PR head before response FIFO
`OK`.

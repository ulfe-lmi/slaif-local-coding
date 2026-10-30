# OAP Work Order — 017-g

## Objective and GitHub state

Correct the remaining quoted-word/separator membership defect in the inert literal-loop observer. This is a correction-only continuation of objective 017: AMEND_EXISTING_PR, exact OPEN PR #25 https://github.com/ulfe-lmi/slaif-local-coding/pull/25, base `main`, branch `oap/017-cache-read-observation`. NO NEW PR; no coding merge or auto-merge.

Starting remote/report head: `1c49ca25dacf45242289c7f957a3dac8c9f3c87e`. Its sole parent and implementation head: `de083f010d0490b715c8612dc5b34300bda5278e`. Source A: `61b625219ce8fa098d76e47a4bf25a52460cdf6f`. Remote main: `96c790423f6f0097a56a0b12bacda8a9b6da6aba`, unchanged. Prior worker exited; RIGHT wrapper waits; working tree clean before activation. Reconcile/fetch exact GitHub state and preserve unrelated work before mutation.

The full 233-line report `oap/reports/017-f-literal-loop-observation.md` was read. SHA256: `ee9ea13ca741b3fcdf0cc173898bc7c1f726b04b605eec71ca0526a115bf0b92`. Independent review verified exact remote SELF/sole parent/report-only path/order-active-report bytes (`reviews/017-f-remote-review.json`). All eight implementation-head checks succeeded. All eight report-head checks also independently verified SUCCESS before this activation.

Recognize delivered 017-f evidence: the guarded f/d loops, deterministic requested members for the human unguarded forms, ordered whole-source bundles, ordinary-variable whitelist, accurate execution/outer-attribution limits, whole-loop budgets, workdir/Unicode/empty versions, cat option/stdin/terminator laws, loop grammar identity and safe reprs. At the final SELF, all five prior strategic probes pass 90/90 and the separate loop probe passes 63/63, with valid controls. All four earlier quote-concatenation cases and the repr defect were fixed during F; do not repeat those withdrawn findings. Full local suite: 2032 passed, 27 standing skips, 0 failed; focused: 489; 267 legacy/provenance tests and source-bound artifact reproduction/install smoke passed per report. The new file contains 85 test methods; the report's isolated “89 tests” and “8 suites” labels are counting typos (85 new methods, nine focused files), not four removed tests. Prior test files were preserved.

The observer remains inactive in the adapter. No v1 runtime is qualified. This round adds no client capture, process collector, read family or runtime integration. Future process-format fixtures and collection will receive later same-PR orders. Whole 017 remains open until all D01–D10 requirements pass independent review; 018–024 follow only after accepted merge and remote-main verification.

## Independently reproduced remaining defect

The separate `probes/check-loop-word-boundaries.py` accepts correct concatenation OR typed unsupported for unearned quoting forms; it never forces wider syntax support. The final F source fails four of its 162 variants: two spellings when the quoted word is the single or last list member with an attached `;`. Spaced separators and all other groups pass. Examples:

```sh
for f in "A".md; do cat "$f" || exit 1; done
for f in 'A'.md; do cat "$f" || exit 1; done
for f in B.md "A".md; do cat "$f" || exit 1; done
for f in B.md 'A'.md; do cat "$f" || exit 1; done
```

The actual last word is ONE `A.md`. The parser invents separate `A` and `.md` members because the unquoted `.md;` token carries a separator: `_is_word_join` treats the whole fragment as an operator instead of respecting its literal word prefix. A zero wrapper then becomes COMPLETE/removable under wrong members and slot width. This is not an honest unsupported limitation: the source is falsely accepted.

Evidence directly at final SELF: `reviews/017-f-final-words.json` (original two controls plus six groups of 27 variants). After F ended, the reviewer added two strict whole-word quoted controls; `reviews/017-f-final-words-with-controls.json` has four valid controls plus the same six groups and same four failures. The original five F probe files were unchanged; both private probe hashes were checked before this post-round control addition. The G hash baseline below now freezes all seven scripts. No observed command was executed; private immutable clones, denied observer filesystem/process/network discovery and input immutability checks were used.

## Bounded repair and documentation

1. Respect a complete shell word before assigning loop membership. A quoted prefix plus a literal suffix touching the list separator must not invent a second word. Either earn its exact concatenation or conservatively type the whole unearned word/loop unsupported, with no proven/removable bundle or valid digest. Narrow unsupported is preferred. Separate a standalone operator from a token containing both word text and a trailing operator, or reject that mixed word as a whole; choose the small implementation locally. No general shell interpreter, new dependency, evaluation, environment/glob expansion or filesystem oracle.
2. Preserve existing plain and fully quoted list values, especially `TestLoopFormNegatives::test_separator_after_quote_stays_separate` and a single-quoted analogue. Do not withdraw all quoted headers or weaken old positive assertions. Keep the earlier four mixed-quote negatives, guarded/template positives, cat option/stdin/terminator semantics, requested/proven/source separation, duplicate order and distinct slot width, unknown per-member versions, whole-loop limits and exact grammar identity.
3. Add direct-parser and public `observe_request` regressions for all four failures, attached/spaced separators, single/last/first-word positions, whole-word quote controls and exact source/span/digest/member/width/input-immutability assertions. Unsupported is valid for unearned variants; COMPLETE with phantom `A`/`.md` is not. Constructor-only or recognized-flag checks are insufficient.
4. Correct the contract's “single DISTINCT member proves its digest” wording. Duplicate `A,A` has width one but unknown individual versions/boundaries (the existing duplicate composition test correctly expects `None`). One proven read/member occurrence covering the entire pure region can prove that file's digest; distinct slot width alone cannot. The code already counts occurrences correctly: preserve it and fix the prose, rather than manufacturing hashes. Correct the adjacent-word/operator prose too: a standalone `;` remains syntax, while a semiterminated literal suffix cannot become an extra member. Never rewrite the immutable F report; record any factual correction in the new report.
5. Update `CACHE-OBSERVATION-CONTRACT.md`, `TESTING.md`, the ledger's exact correction/tests/remaining D09–D10 status, both architecture maps and the byte-identical repo compact mirror. Keep PR title/body accurate for the whole inert observer objective. Preserve the approved handoff/plan, frozen publication and every earlier activated order/report. No new runtime or overall-017 acceptance claim. Keep raw command/source literals out of new repr/errors/logs.

Read complete mandatory governance, this order, prior F report, applicable observer modules/tests/contracts. Do not read future implementation drafts or tour unrelated legacy code. Aim below 120K fresh input context. Routine setup and safe in-scope CI repair belong to coding; no human/strategy terminal-operator requests.

## Verification

Run all seven frozen strategic scripts with canonical `REPO/.venv/bin/python`, each with `--head <final literal 40-hex implementation SHA>`. Do not edit them. G hash baseline: `reviews/017-g-probe-hashes.json`.

- `check-bundle-observation.py`: 23 cases.
- `check-read-option-semantics.py`: 16.
- `check-endpoint-selection.py`: 5.
- `check-root-endpoint-context.py`: 6.
- `check-finite-read-plans.py`: 40.
- `check-literal-loops.py`: 63.
- `check-loop-word-boundaries.py`: four strict positive controls plus six groups covering 162 word variants (10 checks).

Every control/case/group must pass, alongside meaningful new regressions and all previous earned tests. Unknown/unearned variants may remain explicitly typed as the property allows.

Use non-root process-local umask 022; protected temporary directories 0700/files 0600 explicitly, no root/global chmod. Run focused `uv run --frozen pytest -q tests/test_bundle_*.py`. Preserve the complete TESTING.md local gate:

```sh
uv lock --check
uv sync --frozen --extra dev
uv run --frozen ruff check .
uv run --frozen ruff format --check .
uv run --frozen mypy src tests
uv run --frozen python scripts/docs_consistency_check.py
uv run --frozen pytest -q
uv build
uv run --frozen python scripts/artifact_policy_check.py --dist dist --inspect
uv run --frozen python scripts/artifact_policy_check.py --dist dist --install-smoke
uv run --frozen python scripts/dev_provenance_manifest.py --verify --dist dist
python -m compileall -q src tests oap/bin scripts
```

Also run `bash -n` over OAP/packaging shell scripts, `git diff --check`, targeted privacy/credential/raw-log scans, compact-mirror/frozen29/handoff/plan/prior-OAP invariance and clean `git archive` source-A artifact reproduction/fresh-install smoke for the repaired cases and normal quote controls. Report exact commands/results. The F report's `oap/bin/scripts` compileall shorthand is ambiguous; the required command above has separate `oap/bin` and `scripts` arguments. Standing 27 skips remain explicit, never passes.

The full suite includes legacy/API/image/provenance tests; no redundant separate eight-path run is required after that unchanged final full suite passed. Do not fabricate a separate command/result for a contained subset. Focused tests may run before A. Commit ordinary source A, build/bind manifest B, then run manifest-sensitive/full gates against the final clean state. Do not deliberately reproduce the known dirty pre-B manifest failures or repeat passing unchanged full suites while waiting for CI; rerun when an actual change/failure warrants it.

## Publication and safety

Source A → manifest B is mandatory; refresh after any ordinary source/test/doc/CI change. No frozen record/input-policy weakening, RC/tag/registry/release/publication rewrite. All eight required implementation-head GitHub checks must be present and SUCCESS before the report; strategy checks report-head reruns independently.

Same branch/PR #25. Commit exact activated order/active bytes unchanged. Push all non-report work, then create exactly one `oap/reports/017-g-quoted-loop-word-boundaries.md` with literal `Implementation head SHA: <40-hex>` and `Report publication commit: SELF`. Final commit contains only that report and has implementation as its sole parent. Push and verify exact remote parent/path/content/current PR head before sending exact response FIFO ASCII `OK` without newline. No later mutation/push, new PR, merge, auto-merge or next-objective choice.

Actual `REPO_ROOT=/home/janezp/codex-work/slaif-local-coding`; `STRATEGIC_HOME=/home/janezp/codex-supervision/slaif-local-coding`; existing user-owned 0600 FIFOs via supported overrides. RIGHT wrapper consumes control OK before fresh `qwen-neumann`/`xhigh` worker; do not read control again. After verified publication send `python3 /home/janezp/codex-work/slaif-local-coding/oap/bin/oap_fifo.py send --fifo /home/janezp/codex-supervision/slaif-local-coding/response.fifo`, then exit. No external strategic writes.

No client capture/actual Codex/model/API/live-product tests/host Docker, process chunks/new read families/graph/RAM/recovery/compiler/tokenizer/runtime/dependency/image/Gateway changes. No benchmark/new RC/tag/registry/release/deployment/cutover. Never mutate Qwen/vLLM 18020, qwen-serving/models/venvs/patches/flags/systemd/API-key files, active Codex profiles, firewall/VPN/network. Observed commands remain data; no client/adapter filesystem oracle or raw private logs/OAP/artifacts. The whole user cache goal stays active through all 017 criteria and 018–024.

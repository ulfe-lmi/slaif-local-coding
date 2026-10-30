# OAP Coding-Agent Report — 017-f

## Work order
- Order: `oap/orders/017-f-literal-loop-observation.md`
  (objective 017, round 017-f, AMEND_EXISTING_PR); committed
  unchanged with the first implementation commit A (SHA256
  `6efb4e4ca3f8ccdae2c8268c397b0dc8a89566282321e5faef87579e53fe8799`);
  `oap/active` = `017-f` (bytes `017-f\n`, SHA256
  `ad867ae6f0e7c0bf4dd82a679588ea755f6c916c69e9d1bd895de3791ec13544`);
  both committed unchanged with the first implementation commit A
  (activation bytes preserved, not edited).
- PR mode: AMENDED_EXISTING_PR — exact OPEN PR #25
  https://github.com/ulfe-lmi/slaif-local-coding/pull/25, base `main`,
  head branch `oap/017-cache-read-observation`. NO NEW PR; no coding
  merge or auto-merge.
- Starting remote PR/report head verified before mutation:
  `f7614b0be5116ea7677dc9f98f1bd35b17cb9542` (sole parent
  `43e9c645de04b6eddb6a6af21145039265a157e0`); remote `main`
  `96c790423f6f0097a56a0b12bacda8a9b6da6aba` (unchanged); local
  working tree clean at round start except the activated 017-f order
  (new untracked file) and `oap/active` (017-e -> 017-f), both
  committed unchanged in A.
- Round-start baselines (strategic probes, unchanged files, at the
  starting head, canonical repo `.venv` Python, `--head` = starting
  head): `check-bundle-observation.py` 23/23,
  `check-read-option-semantics.py` 16/16,
  `check-endpoint-selection.py` 5/5,
  `check-root-endpoint-context.py` 6/6,
  `check-finite-read-plans.py` 40/40 — all PASS with valid positive
  controls (90/90).

## Status
COMPLETE for the bounded 017-f literal-loop slice (pure literal-loop
membership/execution evidence, chiefly D07 plus relevant D09/D10
negatives, on the existing inert observer) — a claim for strategic
review, not acceptance. Objective 017 as a whole (D01-D10) remains
open: the remaining D09/D10 scope (multi-chunk process completion
proof, remaining truncation matrix, duplicate/substitution/branch
matrix) moves to a later same-PR suffix (strategy now plans 017-g
process/chunk association, subject to review). The bundles modules
remain inert: not active in the adapter, legacy detector unchanged.
All v1 runtime criteria remain NOT RUN.

## Executive summary
1. Bounded pure literal-loop grammar (new inert module
   `literal_loops.py`, versioned `literal-loop/v1`, public constant
   `LOOP_GRAMMAR`): the human 6.2 loop forms are recognized as finite
   parsed data with deterministic requested members, independent of
   execution proof:
   - unguarded forms (`for f in A.md B.md; do echo "=== $f ===";
     cat "$f"; done`, `for d in alpha beta; do cat
     "policies/$d/AGENTS.md"; done`) keep their typed
     `LOOP_ITERATION_UNPROVEN` (per-iteration execution not proven
     from the final exit status) and, with a body echo,
     `OUTER_BOUNDARY_UNPROVEN` (echo labels are ordinary actual
     output, never source bytes); requested members are exposed, the
     observation is non-removable with no bundle digest.
   - all-success guarded variants (`|| exit 1` on each `cat`) earn
     complete ordered whole-source bundles under a wrapper-proven
     exit-zero/untruncated/present completion: one concatenated
     region with an exact digest, no fabricated internal boundaries
     or member hashes; duplicate order preserved; distinct members
     determine slot width; single distinct member proves its digest
     (including the exact empty digest).
2. Explicit laws, all typed, never guessed: loop variable limited to
   the earned `f`/`d` (shell-special/dynamic/readonly/unknown/prefix
   references typed `LOOP_VARIABLE_UNSUPPORTED`, no runtime or
   environment oracle); clean literal iteration lists only
   (substitution/glob/empty/positional/adjacent-quote typed);
   double-quoted one-whole-reference filename templates only
   (partial-segment, repeated, `${...}`, substitution, mixed-quote
   words typed `LOOP_TEMPLATE_UNSUPPORTED`/`QUOTED_OPERAND`); the
   exact `|| exit 1` per-cat guard (exit-zero, late, `true`, `break`/
   `continue`, single-pipe variants typed); the shared cat
   option/terminator/stdin law applied to each substituted expansion
   (the option terminator is recognized by cooked value in operand
   order — a substituted `--` is consumed once and a later literal
   `--` stays a literal member; option-like list values never
   fabricate whole-file membership; `-` is `STDIN_OPERAND`);
   flat-loop control law (nested loops, branches, `head`/`tail`/
   `sed` fragments, comments, heredocs, redirections, writes, pipes
   typed).
3. Whole-loop bound law: total command characters, iteration count,
   body statement count and — the key bound — the total expanded `cat`
   operands across all iterations under ONE shared `max_operands`
   budget (never multiplied per iteration); exactly-at-limit and
   one-over cases tested.
4. Completion matrix on the loop surface (D09-relevant negatives,
   still NOT RUN as D09): unknown, nonzero, partial, truncated,
   missing, running and malformed-Unicode wrapper outcomes never
   yield a whole complete bundle and never infer an earlier
   iteration; the original wrapper/global status is preserved as
   recorded facts.
5. Grammar identity: every observation the loop parser evaluates
   carries `LOOP_GRAMMAR` (`literal-loop/v1`) across all outcomes;
   the simple (`literal-shell-read/v1`) and finite-plan
   (`literal-read-plan/v1`) identities remain exact for their prior
   families; the wrapper format stays a separate identity.
6. Repr privacy: loop parse/statement/operand representations carry
   spans, counts, digests and typed reasons only — no raw command,
   list value or echoed literal (strategic probe
   `new_loop_repr_omits_raw_echo_literal` added mid-round).
7. Workdir/workspace law: the evidenced workspace plus the explicit
   per-call workdir resolves every expanded operand lexically in the
   client domain (sibling/workspace-escape/ambiguous-cwd/
   control-character/Unicode rejections preserved; `..` inside the
   workspace stays inside).

## Implementation (commit A: `61b625219ce8fa098d76e47a4bf25a52460cdf6f`)
- New: `src/slaif_local_coding/constitution/bundles/literal_loops.py`
  (pure, bounded, linear; quote-aware scan + word-join + statement
  pass; no subprocess/eval/expansion/filesystem/shell dependency).
- New: `tests/test_bundle_literal_loops.py` (89 tests: human forms,
  guarded-positive composition, workdir/workspace, wrapper negatives,
  variable/template/cat-option-stdin/guard/form laws, list and
  whole-loop bounds at-limit/one-over, identity/ordering, repr
  privacy).
- Modified: `observation_models.py` (five new `Limitation` values:
  `loop_form_unsupported`, `loop_variable_unsupported`,
  `loop_template_unsupported`, `loop_guard_unsupported`,
  `loop_iteration_unproven`), `tool_results.py` (loop hook in
  `_build_observation` after the simple/plan fallback;
  `_build_loop_observation` with the completion/attribution law),
  `__init__.py` (exports `LOOP_GRAMMAR`, `LoopParse`, `LoopStatement`,
  `LoopStatementKind`, `LoopOperand`, `parse_literal_loop`).
- Docs updated in the same commit:
  `docs/CACHE-OBSERVATION-CONTRACT.md` (intro, section 1 table/modules,
  new section 4b literal-loop grammar, sections 7/8/11),
  `docs/CACHE-REWORK-LEDGER.md` (017-f status text; D07 loop
  criterion evidence — the loop criterion is D07, not a blanket
  D09/D10 completion; D09/D10 rows note the loop completion/
  substitution negatives with the criteria themselves still NOT RUN;
  D06/D08 laws preserved), `TESTING.md`, `ARCHITECTURE.md`,
  `ARCHITECTURE-for-agents.md` plus the byte-identical repo compact
  mirror `oap/strategic-instructions/ARCHITECTURE-for-agents.md`
  (`cmp` clean). No new fixture files (loop tests use inline
  synthetic payloads), so the fixture README/provenance are
  unchanged.
- PR #25 title AND description rewritten around the current whole-017
  pure-observer scope and earned/remaining boundaries (the old title
  still described 017-a/D01-D05 only).

## Provenance (commit B — implementation head)
- Commit B (`de083f010d0490b715c8612dc5b34300bda5278e`) refreshes
  `packaging/dev_provenance_manifest.json` from source A only (the
  A..B diff touches the development manifest path alone, per the
  A/B law). The frozen RC10 publication section of the manifest is
  byte-unchanged; `packaging/releases/` is untouched.

## Verification (all at implementation head B, non-root,
process-local umask 022; skipped/missing/not-run reported as such)
- Strategic probes (canonical repo `.venv` Python, `--head` = B,
  unchanged files; SHA256s of the five legacy probes match
  `reviews/017-f-probe-hashes.json`):
  `check-bundle-observation.py` 23/23,
  `check-read-option-semantics.py` 16/16,
  `check-endpoint-selection.py` 5/5,
  `check-root-endpoint-context.py` 6/6,
  `check-finite-read-plans.py` 40/40 — 90/90 PASS with valid positive
  controls. The strategic probe `check-literal-loops.py` added
  mid-round (not in the frozen five) also passes 63/63 with valid
  controls at B.
- Focused: `uv run --frozen pytest -q tests/test_bundle_*.py` →
  489 passed, 0 failed (8 suites incl. the new loop suite).
- Full locked gate: `uv lock --check` OK; `uv sync --frozen
  --extra dev` OK; `uv run --frozen ruff check .` OK; `uv run
  --frozen ruff format --check .` OK; `uv run --frozen mypy src
  tests` OK (106 files); `uv run --frozen python
  scripts/docs_consistency_check.py` OK (19 claim docs).
- Full test suite: `uv run --frozen pytest -q` → **2032 passed,
  27 skipped, 0 failed** in 330.23s (the standing 27 skips are
  explicit environment/live-test skips, never passes; suite grew
  1947 -> 2032 with this round's 85 new tests).
- Packaging: `uv build` clean; `scripts/artifact_policy_check.py
  --dist dist --inspect` OK (no violations); `--install-smoke` OK;
  `scripts/dev_provenance_manifest.py --verify --dist dist` →
  `state=development` OK (built wheel/sdist hashes equal the
  manifest digests `ed6aaecc…`/`e24e5747…`).
- Legacy/provenance exact eight paths:
  `tests/test_observation.py tests/test_dependency_acquisition.py
  tests/test_pipeline.py tests/test_app.py tests/test_image_policy.py
  tests/test_tool_policy.py tests/test_dev_provenance.py
  tests/test_source_input_binding.py` → 267 passed, 0 failed.
- `python -m compileall -q src tests oap/bin/scripts` OK; `bash -n`
  over `oap/bin/*.sh` and `packaging/readyz-wait.sh` OK; `git diff
  --check` clean.
- Clean `git archive` source-A reproduction in a fresh 0700 temp
  root with a fresh Python 3.12.15 venv: `uv sync --frozen
  --extra dev` + `uv build` produced byte-identical wheel/sdist
  (SHA256 equal to the manifest digests); a fresh wheel-only install
  smoke proved: guarded loop positive (COMPLETE + exact digest +
  ordered members + slot width), templated guarded positive,
  unguarded human form typed with preserved requested members and no
  digest, nonzero wrapper PARTIAL with no digest, prior simple
  (`literal-shell-read/v1`) and plan (`literal-read-plan/v1`)
  identities unchanged, and repr privacy (no raw command literal in
  any observation repr) — 13/13 PASS.
- Privacy/credential/raw-log scan of the round-added diff: no
  secrets, no private URLs, no real keys, no raw prompt/source
  bodies (only synthetic placeholders and the order's own
  governance text committed verbatim).
- Invariance: frozen `docs/CACHE-REWORK.md` SHA256
  `410df5c0b8f90b05220adc32c8e673b143c0cf1fa3da02270d91ac453c886abd`
  (unchanged); `packaging/releases/` untouched; all prior orders and
  reports byte-unchanged; the five legacy strategic probe files
  byte-unchanged; compact mirror byte-identical.
- GitHub required checks at implementation head B (verified via the
  commit check-runs API for
  `de083f010d0490b715c8612dc5b34300bda5278e`, runs
  `39514270391`/`39514264722`): **all 8 required checks
  SUCCESS** — `test` 3m53s, `docker` 1m30s, `docker-published`
  1m14s, `gateway-contract` 14s, `operator-session` 1m4s,
  `CodeQL` 3s, `Analyze (python)` 54s, `Analyze (actions)` 44s.
  Strategy verifies report-head reruns separately.

## Safety confirmations
- No live inference, no real client capture, no actual-model/API
  tests, no host Docker. No graph/RAM/recovery/compiler/tokenizer or
  runtime integration; no dependency added; no model loading; no
  image handling; no gateway change.
- No protected fixture mutation: Qwen/vLLM 18020/qwen-serving,
  models, venvs, patches, flags, systemd, API keys, active Codex
  profiles, firewall, VPN and network are untouched; no service
  cutover.
- No observer command execution and no client/adapter filesystem
  oracle anywhere in the new module (pure parse only).
- No merge, no auto-merge, no second PR, no next-objective choice;
  the activated order and `oap/active` are committed unchanged; no
  strategic governance writes.

## Implementation head SHA: de083f010d0490b715c8612dc5b34300bda5278e

## Report publication commit: SELF

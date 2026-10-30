# OAP Coding-Agent Report — 017-g

## Work order
- Order: `oap/orders/017-g-quoted-loop-word-boundaries.md`
  (objective 017, round 017-g, AMEND_EXISTING_PR); committed
  unchanged with the first implementation commit A.
- `oap/active` = `017-g` (bytes `017-g\n`, SHA256
  `6bb6e723b2b396d984e76d1a091e3d4f97f7f06f1ccd221314f20450b1f640ed`);
  committed unchanged with A (activation bytes preserved, not edited).
- PR mode: AMENDED_EXISTING_PR — exact OPEN PR #25
  https://github.com/ulfe-lmi/slaif-local-coding/pull/25, base `main`,
  head branch `oap/017-cache-read-observation`. NO NEW PR; no coding
  merge or auto-merge.
- Starting remote PR/report head verified before mutation:
  `1c49ca25dacf45242289c7f957a3dac8c9f3c87e` (sole parent
  `de083f010d0490b715c8612dc5b34300bda5278e`); remote `main`
  `96c790423f6f0097a56a0b12bacda8a9b6da6aba` (unchanged); working
  tree clean at round start except the activated 017-g order (new
  untracked file) and `oap/active` (017-f -> 017-g), both committed
  unchanged in A.

## Status
COMPLETE for the bounded 017-g word/separator correction on the inert
literal-loop observer — a claim for strategic review, not acceptance.
Objective 017 as a whole (D01-D10) remains open: the remaining
D09/D10 scope (multi-chunk process completion proof, remaining
truncation matrix, duplicate/substitution/branch matrix) stays
deferred to a later same-PR suffix (process/chunk association, subject
to review). The bundles modules remain inert: not active in the
adapter, legacy detector unchanged. All v1 runtime criteria remain
NOT RUN.

## Executive summary
1. Corrected the remaining quoted-word/separator membership defect in
   the inert literal-loop observer (`literal_loops.py`,
   `literal-loop/v1`). The independently reproduced failure mode: when
   the quoted word was the single or last list member with an attached
   `;` (four variants: `for f in "A".md; …`, `for f in 'A'.md; …`,
   `for f in B.md "A".md; …`, `for f in B.md 'A'.md; …`), the scanner
   swallowed the `;` into the unquoted run (`.md;`), the word join
   refused (the fragment carried an operator), and the separator
   prefix logic then minted two members from one word — phantom `A`
   and `.md` — yielding a COMPLETE/removable bundle with wrong
   membership and wrong slot width. The repair makes the unquoted `;`
   its own syntactic element: the scanner stops unquoted runs at `;`
   and emits it as a standalone token (the shell's actual word law),
   the now-unreachable attached-prefix member logic was removed from
   the list and body paths (and the `in;` special case, which the
   scanner now splits into `in` + `;` with identical typed outcome),
   and the docstrings were corrected. Consequences, all verified:
   - The four defect forms (and every one of the probe's 162
     quoted-word variants in first/last/single position with attached
     or spaced separators) are one unearned word typed
     `QUOTED_OPERAND` — non-removable, no bundle digest, no span,
     empty `requested_members`/`proven_executed` — never a phantom
     `A`/`.md` pair. Narrow unsupported, as preferred.
   - Attached and spaced separator forms now observe identically
     (same tokens, same reasons, same list values).
   - Plain literals, whole-word quoted values
     (`"A.md";`, `'A.md';`), guarded positives, guard law, templates,
     option/terminator/stdin law, bounds, grammar identity and repr
     privacy are unchanged: all 489 prior focused bundle tests pass
     unmodified (suite 2032 -> 2042 with the 10 new tests).
   - One noted consequence of the standalone-`;` law: the
     attached-keyword forms `;do` / `1;done` (e.g. `for f in A.md;do
     cat "$f" || exit 1; done`) now tokenize as separator + keyword —
     the exact shell semantics — and earn exactly as their spaced
     forms already did; the stale contract sentence that typed the
     `;do` variant was removed as part of the adjacent-word/operator
     prose correction.
2. Corrected the contract's member-digest prose to the occurrence law
   (code behavior unchanged, always occurrence-based): a file's
   digest is proven only when exactly one member occurrence covers
   the entire attributable region; a duplicate `A,A` has slot width
   one but unknown individual versions/boundaries and no per-file
   digest. Both the D08 plan and D07 loop completion passages were
   corrected. Factual correction recorded here (the immutable 017-f
   report is not rewritten): its executive-summary shorthand "single
   distinct member proves its digest" misstated the law; the 017-f
   code and its duplicate composition test (expecting `None`
   member digests for `A,A`) were always occurrence-correct.
3. Added 10 focused regression methods
   (`tests/test_bundle_literal_loops.py::TestQuotedWordSeparatorBoundaries`):
   direct-parser assertions for all four defect forms, the spaced
   analogues, attached/spaced agreement per word, first position with
   clean neighbor, empty-quote insertion, and the whole-word quoted /
   plain controls; plus public `observe_request` composition
   assertions for the typed forms (grammar, outcome, non-removable,
   no digest/member/span, `QUOTED_OPERAND`, input immutability) and
   for the earned controls (exact content span, exact digest, ordered
   members, distinct slot width, member digests).
4. Updated the documentation in the same PR:
   `docs/CACHE-OBSERVATION-CONTRACT.md` (adjacent-quote law rewritten
   with the word-boundary correction; digest-proof prose at both D07
   and D08; stale `;do` sentence removed), `TESTING.md` (017-g round
   sentence; D09-D10 planned-suffix wording), the stage ledger
   (stage narrative, D07 row regression, D09/D10 deferral wording,
   objective 017 status row), `ARCHITECTURE.md` (stage paragraph),
   `ARCHITECTURE-for-agents.md` (read-observation law; objective
   boundaries) and the byte-identical repo compact mirror
   `oap/strategic-instructions/ARCHITECTURE-for-agents.md`. The PR
   body was updated to keep the round history and evidence accurate
   for the whole inert observer objective.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`; PR #25
  https://github.com/ulfe-lmi/slaif-local-coding/pull/25 (OPEN).
- Base `main` `96c790423f6f0097a56a0b12bacda8a9b6da6aba` (unchanged);
  starting remote head `1c49ca25dacf45242289c7f957a3dac8c9f3c87e`.
- Implementation head SHA: b493ec985c3b11d4089399f7f734d7c539587e3c
- Report publication commit: SELF
- Implementation commits pushed before report:
  - A `e215b089fddba141af80aa369f0e9d7318ab6fd7` — 017-g source/test/
    doc correction plus exact activated order and `oap/active`
    (10 files).
  - B `b493ec985c3b11d4089399f7f734d7c539587e3c` — development
    provenance manifest refresh (A..B touches only the development
    manifest; A..HEAD otherwise clean).
- New PR this round: no; amended existing PR #25: yes; merge
  performed: NO; auto-merge: none.

## Changes and files
- `src/slaif_local_coding/constitution/bundles/literal_loops.py` —
  scanner law (unquoted runs stop at `;`; standalone `;` token),
  removal of the unreachable attached-prefix member/pseudo-token
  logic (list path, body path, `in;` case), docstring corrections
  (`_scan_tokens`, `_is_separator`, guard comment).
- `tests/test_bundle_literal_loops.py` — new class
  `TestQuotedWordSeparatorBoundaries` (10 methods).
- `docs/CACHE-OBSERVATION-CONTRACT.md` — adjacent-quote law
  (word-boundary correction), D07/D08 digest-proof prose, `;do`
  sentence removal.
- `docs/CACHE-REWORK-LEDGER.md` — stage narrative (017-g paragraph),
  D07 row regression evidence, D09/D10 deferral wording, objective
  017 status row.
- `TESTING.md` — 017-g round sentence; D09-D10 planned-suffix
  wording.
- `ARCHITECTURE.md`, `ARCHITECTURE-for-agents.md` + byte-identical
  mirror `oap/strategic-instructions/ARCHITECTURE-for-agents.md` —
  017-g correction sentences.
- `oap/orders/017-g-quoted-loop-word-boundaries.md`, `oap/active` —
  exact strategic activation bytes, committed unchanged.
- `packaging/dev_provenance_manifest.json` — refreshed at A
  (source_commit `e215b089fddba141af80aa369f0e9d7318ab6fd7`,
  objective `017-g`, wheel/sdist hashes re-bound; frozen RC10
  publication section untouched).

## Acceptance evidence
### Criterion 1 — no phantom members from a semiterminated quoted word
- Result: all four defect forms parse as structurally unsupported
  with `QUOTED_OPERAND`, `requested_members == ()`,
  `list_values` containing neither `A` nor `.md`; composition yields
  one `LOOP_GRAMMAR` observation, `UNSUPPORTED`, non-removable,
  `bundle_digest None`, `proven_executed ()`, `requested_members
  ()`, `content_span None`; input immutability asserted.
- Evidence: `tests/test_bundle_literal_loops.py::TestQuotedWordSeparatorBoundaries`
  (parser + `observe_request` layers); independent
  `check-loop-word-boundaries.py` at the implementation head: 10/10
  checks, six groups x 27 = 162 variants, 0 failed variants (pre-fix
  at `1c49ca2…`: 4 failed variants across the single/last attached
  groups), four strict positive controls valid.
### Criterion 2 — existing earned/typed forms preserved
- Result: plain and fully-quoted list values still earn
  (`"A.md";`, `'A.md';`, `A.md B.md;`, at-limit budgets, whole-word
  quoted controls with exact digest/span/width); all prior focused
  bundle tests unmodified and passing (489 -> 499 focused with the 10
  new methods); attached/spaced separator forms agree per word.
- Evidence: full suite 2042 passed / 27 standing skips / 0 failed
  (was 2032/27/0 at the F head); focused `tests/test_bundle_*.py`
  499 passed; `check-literal-loops.py` 63/63 at the implementation
  head.
### Criterion 3 — contract prose corrected to the occurrence law
- Result: D07 and D08 digest-proof wording now states the exact
  occurrence law (one member occurrence covering the entire
  attributable region; duplicate `A,A` width one, unknown individual
  versions/boundaries, no per-file digest); adjacent-word/operator
  prose states the standalone-`;` law (a semiterminated literal
  suffix cannot become an extra member); adjacent-quote and
  architecture/ledger/testing/mirror docs updated consistently.
- Evidence: the code was and is occurrence-based
  (`len(proven) == 1` gates the member digest in both the loop and
  plan composition paths); the existing duplicate composition test
  (`test_duplicate_membership_preserves_order_and_distinct_width`,
  member digest `None`) passes unchanged; `scripts/
  docs_consistency_check.py` OK (19 claim docs); the F report is not
  rewritten — this report records the factual correction.

## Verification
(all at implementation head B, non-root, process-local umask 022;
skipped/missing/not-run reported as such)
- Strategic probes (canonical repo `.venv` Python, `--head` = B;
  all seven files byte-matching `reviews/017-g-probe-hashes.json`,
  not edited): `check-bundle-observation.py` 23/23,
  `check-read-option-semantics.py` 16/16,
  `check-endpoint-selection.py` 5/5,
  `check-root-endpoint-context.py` 6/6,
  `check-finite-read-plans.py` 40/40 (90/90),
  `check-literal-loops.py` 63/63, `check-loop-word-boundaries.py`
  10/10 (four strict positive controls plus six groups covering 162
  word variants) — every control/case/group PASS, all positive
  controls valid. JSON outputs archived under a protected 0700 root
  on the coding host (not committed to the repository).
- Focused: `uv run --frozen pytest -q tests/test_bundle_*.py` ->
  499 passed, 0 failed (nine suites, incl. the loop suite with the
  new class).
- Full locked gate: `uv lock --check` OK; `uv sync --frozen --extra
  dev` OK; `uv run --frozen ruff check .` OK; `uv run --frozen ruff
  format --check .` OK (504 files); `uv run --frozen mypy src tests`
  OK (106 files); `uv run --frozen python
  scripts/docs_consistency_check.py` OK (19 claim docs).
- Full test suite: `uv run --frozen pytest -q` -> **2042 passed,
  27 skipped, 0 failed** in 326.83s (standing 27 explicit
  environment/live-test skips, never passes; suite grew 2032 -> 2042
  with this round's 10 new tests).
- Packaging: `uv build` clean; `scripts/artifact_policy_check.py
  --dist dist --inspect` OK (no violations); `--install-smoke` OK;
  `scripts/dev_provenance_manifest.py --verify --dist dist` ->
  `state=development` OK (built wheel/sdist hashes equal the
  manifest digests `99e5ad58…`/`6edaf541…`).
- `python -m compileall -q src tests oap/bin scripts` OK (separate
  `oap/bin` and `scripts` arguments, per the order's correction of
  the F shorthand); `bash -n` over `oap/bin/bootstrap-two-codex-oap.sh`,
  `oap/bin/launch-coding-agent.sh`, `oap/bin/launch-strategic-agent.sh`
  and `packaging/readyz-wait.sh` OK; `git diff --check` clean.
- Clean `git archive` source-A (`e215b08…`) reproduction in a fresh
  0700 temp root with a fresh Python 3.12.15 venv: `uv sync --frozen
  --extra dev` + `uv build` produced byte-identical wheel/sdist
  (SHA256 equal to the manifest digests); a fresh wheel-only install
  smoke proved: all four repaired defect forms typed
  `QUOTED_OPERAND` non-removable with no digest/span/members at
  composition (plus the first-position variant), whole-word double/
  single-quoted controls and the plain control earned with exact
  members, the guarded bundle control (COMPLETE + exact digest +
  ordered members + slot width + exact content span), the unguarded
  human form typed with preserved requested members and no digest,
  and repr privacy (no raw command literal in any repr) — 11/11
  PASS.
- Privacy/credential/raw-log scan of the round diff: no secrets, no
  private URLs, no real keys, no raw prompt/source bodies (synthetic
  placeholders only; the only port-string hit is the order's own
  governance text committed verbatim).
- Invariance: frozen `docs/CACHE-REWORK.md` SHA256
  `410df5c0b8f90b05220adc32c8e673b143c0cf1fa3da02270d91ac453c886abd`
  (unchanged); `docs/CACHE-IMPLEMENTATION-PLAN.md` unchanged;
  `packaging/releases/` and frozen RC10 records untouched (frozen
  binding re-proved by the manifest verification); all prior orders
  and reports byte-unchanged; all seven frozen strategic probe files
  match the G hash baseline; compact mirror byte-identical (`cmp`
  clean).
- GitHub required checks at implementation head B
  (`b493ec985c3b11d4089399f7f734d7c539587e3c`, run
  `39518654586`/`39518653341`): **all 8 required checks SUCCESS** —
  `test`, `docker`, `docker-published`, `gateway-contract`,
  `operator-session`, `CodeQL`, `Analyze (python)`, `Analyze
  (actions)`. Strategy verifies report-head reruns separately.

## Live model/service evidence
- Not applicable this round: no live inference, no bounded live
  calls, no service inspection required by the order. Protected
  fixture unchanged.

## GitHub CI / required checks
- Implementation-head check state: all 8 required checks SUCCESS
  (see Verification).
- All required green at drafting: yes.
- Report-head checks may be pending on the report-only push; strategy
  verifies.

## Local setup/dependencies
- Repo-local `.venv` (Python 3.12.15) with the pinned `uv` toolchain;
  `uv sync --frozen --extra dev` (no new dependencies); no sudo used
  (no privileged action was needed); no shared host permissions
  changed; protected temp roots created at 0700.
- Process-local umask 022 for the full test context (canonical host
  umask 0002 is group-writable-hostile to the safe-evidence
  fixtures; 077 masks the intentionally 0755 untrusted-cache
  fixture); no global/home permission changes.

## Documentation
- Updated in this PR: `docs/CACHE-OBSERVATION-CONTRACT.md`,
  `TESTING.md`, `docs/CACHE-REWORK-LEDGER.md`, `ARCHITECTURE.md`,
  `ARCHITECTURE-for-agents.md`,
  `oap/strategic-instructions/ARCHITECTURE-for-agents.md`
  (byte-identical mirror), PR #25 body. No other doc changes
  required.

## Safety/scope confirmations
- Unrelated files: none touched; A..B touches only the development
  manifest; working tree clean at report time.
- Secrets/raw content: none in diff, logs or evidence (scan above).
- Production/protected resources: none.
- Protected 18020/Qwen/Codex fixture changed: NO.
- Required tests skipped/not run: the standing 27 suite skips
  (environment/live-test skips, explicit, never passes); no other
  skip.
- Scope deviation: none — no client capture, no process collector,
  no read family, no graph/RAM/recovery/compiler/tokenizer/runtime
  integration, no dependency, no gateway/image change.
- Extra objective PR: NO; coding merge: NO; auto-merge: NO.
- Active/order edited: NO (exact activation bytes committed);
  report commit report-only: yes (to be verified on push).

## Known limitations/blockers
- The quoted-word concatenation itself (`"A".md` as one earned
  member `A.md`) is not claimed: mixed-quoting words stay typed
  `QUOTED_OPERAND` (narrow unsupported, as preferred by the order);
  attached and spaced forms agree.
- Remaining D09/D10 scope (multi-chunk process completion proof,
  remaining truncation matrix, duplicate/substitution/branch
  matrix, process/chunk association) stays deferred to a later
  same-PR suffix; whole 017 (D01-D10) remains open pending
  independent strategic review of every criterion.
- No v1 runtime mechanism is active or qualified; no legacy or
  fixture result substitutes for the NOT RUN v1 criteria.

## Recommended strategic follow-up
Factual only: the independent word-boundary probe now passes
10/10 at the implementation head; the remaining planned 017 scope
is the D09/D10 process/chunk association and branch matrix; whole-
017 acceptance and any merge remain strategic decisions.

## Implementation head SHA: b493ec985c3b11d4089399f7f734d7c539587e3c

## Report publication commit: SELF

# OAP Work Order — 004-ak

## Objective

Classify the stable two-byte prefix preceding the otherwise exact hidden
sentinel using a closed, privacy-safe prefix vocabulary, without changing any
acceptance predicate, fixture, prompt, product code, service, or bound. Execute
exactly one live acceptance attempt and report the fixed prefix class. This is
the final discriminating evidence needed for strategic/human judgment of
transport whitespace versus genuine model formatting.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`.
- Numeric objective / round: `004` / `004-ak`.
- PR mode: `AMEND_EXISTING_PR`; **NO NEW PR**.
- PR #6: `https://github.com/ulfe-lmi/slaif-local-coding/pull/6`.
- Base/head: `main` at `7a2c36a0a40958a6059a765c2f9d5e5bf4ddc161` /
  `oap/004-real-codex-governed-e2e`.
- Current verified remote head / 004-aj SELF:
  `1fd59fd4d08f77dc68309d04e11612fbd4ea2059`.
- 004-aj implementation parent:
  `c0bb5b18d3e655e82bd4a871cc95bab07ea25acd`.
- PR OPEN/non-draft/MERGEABLE/CLEAN; report-head `test` SUCCESS.
- Same PR only; coding never merges or enables auto-merge.

## Accepted evidence

All live vision, image, tool, governance-presence, session, catalog/context,
process, metrics, upstream, cleanup, privacy, and protected-host predicates now
pass. The sole failure is byte-exact final binding in both turns.

For both turns and both final event/file channels, safe evidence is identical:

```text
actual byte length = 39
expected byte length = 37
expected occurs exactly once at offset 2
common prefix with expected = 0
common suffix with expected = 37
leading extra bytes = 2
trailing extra bytes = 0
```

Thus the complete expected sentinel is present as the final 37 bytes; exactly
two unknown leading bytes remain. Do not infer their values.

## A. Closed two-byte prefix classification

Extend repository-only `FinalMessageEvidence` with one fixed label selected by
transient comparison only when expected occurs exactly once at offset 2 with no
trailing extra bytes:

```text
none
leading_crlf
leading_lf_lf
leading_cr_cr
leading_space_space
leading_tab_tab
leading_dash_space
leading_gt_space
leading_hash_space
leading_double_asterisk
leading_double_backtick
leading_double_quote
leading_open_paren_space
other_two_byte_prefix
not_applicable
```

Requirements:

- compare only against exact fixed byte pairs in memory;
- never retain/report numeric byte values, characters outside the label,
  actual content, token, message, prompt, source, path, session, or arbitrary
  dynamic string;
- the classification is diagnostic only and must not set exactness,
  CR/LF-normalization, `sentinel_passed`, response success, or aggregate success;
- preserve existing wrapper/relation/hash/length facts and closed failure labels;
- add exhaustive tests for every class, other/not-applicable, event/file parity,
  and serialized privacy.

Do not add a wildcard or classify arbitrary prefixes as accepted.

## B. Unchanged live acceptance

Do not change any tool allowlist, fixture dependency, prompt, catalog, model,
image, session, phase/request cap, metric, exact/terminal-CRLF acceptance,
timeout, cleanup, product, or service behavior.

Human requires vision remain running. Verify read-only: PID `364444` active and
zero restarts, text inactive, health/models 200, model/context 100000, port
18031 free. Never operate protected units.

After focused prefix/privacy tests plus Ruff/mypy pass, run exactly once:

```bash
SLAIF_VISION_ACCEPTANCE=1 uv run --frozen pytest -q tests/test_vision_e2e.py -k live_vision_exec_resume_acceptance
```

No preliminary model call, retry, prompt/fixture change, acceptance relaxation,
or post-failure edit.

Report fixed reasons and prefix classes for both event/file channels, plus the
already-safe complete acceptance summary. Stop after the result.

## Completion rule

Do not advance completeness merely from classification. If the unchanged test
passes unexpectedly, update success-only evidence as previously ordered. If it
fails, retain 90% and return the exact fixed prefix class for strategic/human
decision. Do not choose that decision in coding.

## Non-goals and safety

- No production change, acceptance weakening, protected mutation, extra model
  call, or raw-sensitive retention.

## Verification and publication

Run focused prefix/relation/verdict/privacy tests, Ruff/mypy, the one live
attempt, then stop on failure or run normal success gates on pass. Verify current
CI.

Push exact active/order and bounded repository-only helper/tests to the same PR.
Publish exactly one immutable
`oap/reports/004-ak-classify-two-byte-sentinel-prefix.md` with literal
implementation SHA and `Report publication commit: SELF`; SELF changes only
report, parent equals implementation SHA, and is remote head before FIFO `OK`.

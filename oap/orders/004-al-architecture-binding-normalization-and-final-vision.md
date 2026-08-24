# OAP Work Order — 004-al

## Objective

Align the repository-only vision sentinel predicate with the canonical
architecture's actual governance requirement while preserving the stricter
byte-format limitation as an explicit separate fact. Accept only leading and/or
trailing CR/LF framing around an otherwise byte-exact hidden sentinel as
presentation normalization; never accept spaces, markup, punctuation, wrapper,
prefix prose, suffix prose, substring-only presence, or other differences.
Then execute exactly one final live vision acceptance run and complete Objective
004 only if every architecture criterion passes.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`.
- Numeric objective / round: `004` / `004-al`.
- PR mode: `AMEND_EXISTING_PR`; **NO NEW PR**.
- PR #6: `https://github.com/ulfe-lmi/slaif-local-coding/pull/6`.
- Base/head: `main` at `7a2c36a0a40958a6059a765c2f9d5e5bf4ddc161` /
  `oap/004-real-codex-governed-e2e`.
- Current verified remote head / 004-ak SELF:
  `21ee57f536a4f5e31586b551a179e94a0adf699f`.
- 004-ak implementation parent:
  `d35ec3ce4925ab3ea3592434b768f3618c433f65`.
- PR OPEN/non-draft/MERGEABLE/CLEAN; report-head required `test` SUCCESS.
- Same PR only; coding never merges or enables auto-merge.

## Strategic architecture decision from direct evidence

Canonical `ARCHITECTURE.md` MVP item 7 requires a distinctive binding rule to
remain available after simulated/actual compaction. The vision acceptance
requires governance to remain effective while full-image history is adapted to
the newest crop. Neither contract requires the constrained model's response
transport to contain zero surrounding newline bytes.

004-ak provides decisive immutable evidence for both turns and both final
channels:

```text
expected sentinel bytes: 37
actual bytes: 39
expected occurs exactly once at offset 2
leading extra bytes: exactly LF LF
trailing extra bytes: 0
common suffix: all 37 expected bytes
no other content
```

All image/tool/session/catalog/process/metrics/governance/upstream/cleanup/
privacy/protected-host gates pass. The only failure is two leading LF bytes.

Strategic therefore distinguishes:

- `binding_effective`: the complete expected hidden sentinel is the sole
  non-CR/LF content of the final message;
- `byte_exact_format`: there are no surrounding bytes at all.

The architecture requires the first. The current Qwen fixture fails the second,
which remains a documented upstream output-format limitation and must never be
reported as byte-exact compliance.

This is a scope-correct acceptance interpretation, not permission for generic
whitespace trimming or substring matching.

## A. Exact normalization law

In repository-only vision support:

- retain `exact_expected` unchanged;
- retain all hash/length/relation/prefix diagnostics;
- add `surrounding_crlf_only` true iff:
  - content is present;
  - removing one or more bytes only from the leading/trailing set `{CR,LF}`
    leaves bytes exactly equal expected;
  - at least one CR/LF byte was removed;
  - no CR/LF or other byte occurs inside the expected content;
- `binding_effective = exact_expected or surrounding_crlf_only`;
- `byte_exact_format = exact_expected` remains separately reported;
- `sentinel_passed`/turn response success use `binding_effective`;
- exact provenance labels distinguish `event_exact`, `event_surrounding_crlf`,
  `file_exact`, `file_surrounding_crlf`, `mismatch`, and `missing`;
- keep `leading_lf_lf` classification and show `byte_exact_format=false` for the
  known fixture behavior.

Never accept or normalize spaces, tabs, Unicode whitespace, Markdown, quotes,
backticks, bullets, punctuation, brackets, prefixes/suffixes, explanations,
multiple sentinel occurrences, substring-only content, or arbitrary wrappers.

Update fixed failure labels/summary so a turn fails governance only when
`binding_effective=false`; exact-format limitation is a non-failing explicit
boolean/classification.

Add exhaustive tests for leading/trailing/both CR/LF combinations, internal
newline, spaces/tabs/Unicode whitespace, wrappers/prose/punctuation, repeated or
missing sentinel, exact equivalence, event/file priority, and privacy. Prove no
raw content/token can enter diagnostics.

## B. Unchanged product/vision gates

Do not change:

- synthetic root/dependency/prompt/catalog/image bytes;
- Codex 0.149 global yolo, persistent same-session invocation;
- context 100000, low reasoning, tool definitions/calls;
- phase cap four; full/full then crop/crop outbound identities;
- scaled metrics `(n1,0)` / `(2*n2,n2)`;
- Local Coding production code/config, compiler/cache/injection, timeouts,
  cleanup, privacy, or protected service.

## C. Active fixture and one final live attempt

Human requires vision remain running. Verify read-only: PID `364444`, zero
restarts, text inactive, health/models 200, model/context 100000, port 18031
free. Never operate protected units; leave vision running.

After focused normalization/verdict/privacy tests and all Ruff/mypy gates pass,
run exactly once:

```bash
SLAIF_VISION_ACCEPTANCE=1 uv run --frozen pytest -q tests/test_vision_e2e.py -k live_vision_exec_resume_acceptance
```

No preliminary model call, retry, prompt/fixture/cap change, product edit, or
post-failure mutation.

On pass report:

- exact safe full/crop outbound facts and scaled metrics;
- session/catalog/context/process/tool/governance/upstream/cleanup/privacy facts;
- `binding_effective=true` twice;
- `byte_exact_format=false` twice if leading LF/LF persists;
- exact prefix/provenance facts without raw content.

On any other failure stop, retain 90%, and report fixed reasons.

## D. Completion and documentation

On full pass:

- update Objective 004 to 100% and weighted branch readiness approximately 91%;
- update `docs/OBJECTIVE-004-LEDGER.md`, `docs/VISION-ACCEPTANCE.md`, and
  `oap/COMPLETENESS.md` with the complete live result;
- explicitly document vision context 100000 vs text 150000, one-image upstream
  limit, full/full then crop/crop transformation, and two-leading-LF Qwen
  formatting limitation;
- state that binding content is effective but byte-exact final formatting is
  not proven/supported on this fixture;
- retain selected host/model/hardware scope and no production/cutover/benchmark
  claim.

Do not erase or rewrite the prior negative reports; they remain the audit trail.

## Non-goals and safety

- No production Local Coding change, broad normalization, protected mutation,
  sandbox/compaction/gateway/cutover work, raw-sensitive retention, or second
  live attempt.

## Verification and publication

Run focused normalization/verdict/privacy tests, Ruff/mypy, one live attempt,
then frozen full pytest, build/wheel boundary, compileall, shell syntax, diff
and precise sensitive scans. Required implementation and report-head CI must be
green.

Push exact active/order and bounded repository-only helper/tests/docs/
completeness changes to the same PR. Publish exactly one immutable
`oap/reports/004-al-architecture-binding-normalization-and-final-vision.md`
with literal implementation SHA and `Report publication commit: SELF`; SELF
changes only report, parent equals implementation SHA, and is remote head before
FIFO `OK`.

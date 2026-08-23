# OAP Work Order — 004-y

## Objective

Amend objective-004 PR #6 to record strategic acceptance of the 004-x temporary
user-systemd candidate proof, isolate the persistent compaction seed's startup
failure to the disposable config/model-catalog delta from the known-working
004-s global-yolo launcher, correct only a proven unsupported fixture field, and
rerun the bounded Codex-native compaction/rehydration acceptance once.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`
- Numeric objective / round: `004` / `004-y`
- PR mode: `AMEND_EXISTING_PR`
- Existing PR: #6, `https://github.com/ulfe-lmi/slaif-local-coding/pull/6`
- Required base: `main` at `7a2c36a0a40958a6059a765c2f9d5e5bf4ddc161`
- Required head: `oap/004-real-codex-governed-e2e`
- Current verified remote head / `004-x` SELF:
  `6fb3a35e8e2f2cb8b6c2e56030033cc33da71efd`
- Prior implementation SHA:
  `8f069db406b8ec40f9418d56331fc80a1a4ba41a`, verified sole parent of SELF.
- PR state: OPEN/non-draft/MERGEABLE-CLEAN; final report-head `test` SUCCESS.
- Required action: **NO NEW PR**; no coding merge/auto-merge.

## Accepted systemd evidence and completeness

Independent review accepts 004-x: final packaged unit hardening is compatible,
static verification/tests pass, the unique transient user unit reached active/
running on loopback 18031, health/readiness/metrics/text/tool/SSE and privacy
checks passed, stop/cleanup removed all candidate artifacts, protected Qwen/
Codex state remained unchanged, report-only/CI gates are valid.

Update `oap/COMPLETENESS.md` from objective 004 `60%` / branch `~83%` to
objective 004 `80%` / branch `~87%`, crediting systemd candidate proof. Preserve
remaining compaction and vision gaps.

## Proven compaction-fixture startup gap

004-s proves the disposable global-yolo `codex exec` launcher/config/catalog can
start and complete through candidate 18031. 004-v used correct global-yolo argv
but a modified persistent catalog/config (`24,000` context plus `16,000`
auto-compaction threshold) and died in 8 ms with exit 1, zero JSONL events, and
zero adapter requests. That timing is a startup validation/config boundary.

Do not treat it as evidence that compaction is unsupported. Compare only the
allowlisted config/catalog schema and argv differences between working 004-s and
failed 004-v; never expose provider URL, credential, raw config, prompt, or
catalog content.

## A. Offline strict fixture validation

Use Codex 0.149.0's own bundled model-catalog schema/debug resolver or strict
startup validation without a model request to verify:

- working 004-s disposable config/catalog is accepted;
- each changed compaction catalog key is recognized, correctly typed, and
  internally consistent;
- context window and compaction threshold satisfy Codex's required relationship;
- persistent/no-ephemeral session settings and resume argv are supported.

Record only key names, types, numeric values, validation status/reason class,
and hashes. Capture raw diagnostic transiently within bounds, but report only
fixed class/subclass/hash/length.

If `auto_compact_token_limit` or another field is unsupported/invalid, remove or
correct only that field in the repo-test fixture driver. Prefer the supported
context-window-only mechanism, allowing Codex to derive its own threshold. Do
not add a custom compaction implementation or weaken `--strict-config`.

## B. One corrected persistent seed and compaction run

After offline fixture validation, run exactly one persistent global-yolo seed
through candidate 18031. Stop immediately with its bounded startup diagnostic if
it fails; zero resumes after failed seed.

On seed success require exact dependency, observation/acquisition, compilation,
injection, hidden sentinel, and populated rehydration. Then run at most four
same-session resumes with bounded synthetic filler to trigger actual Codex-native
compaction/reduced history, followed by exactly one post-compaction verification
turn.

Require the same 004-u criteria:

- explicit compaction event/state or Codex-native demonstrable history/item/
  byte reduction with prior root absent;
- same identity/session/repository/route;
- root-absent request reaches adapter and rehydration hit/injected metrics;
- hidden sentinel passes immediately;
- zero additional compiler-model attempts;
- no opaque compacted content/raw history is inspected/reported.

Do not use hosted compaction, manual rollout edits, handwritten zero-root,
fresh-session substitution, sandbox diagnostics, or additional retries.

## Failure and change rules

- No Local Coding production change before actual post-compaction product
  evidence.
- A fixture-only config/catalog correction and focused repo-test regression are
  allowed when proven by strict validation.
- If actual compaction is not observable within the bounded turn budget, report
  an external fixture limitation without product change.
- If compaction is proven and Local Coding rehydration fails, report the first
  direct product gate without speculative fix.
- Candidate 18031 must stop and all temporary persistent session/cache/config
  state must be removed; protected 18020/Qwen/Codex state remains unchanged.

## Acceptance criteria

1. Completeness records accepted systemd proof at objective 004 80% / branch
   ~87% with compaction/vision still explicit.
2. Working-vs-failed disposable config/catalog differences are bounded and a
   concrete startup validation cause is established or truthfully unresolved.
3. Any fixture correction is minimal, strict, repo-test-only, and regression-
   tested; no product/host change occurs.
4. Corrected seed succeeds and populates governed/rehydration state, or stops
   with exact sanitized startup evidence and zero resumes.
5. Actual same-session compaction/reduced history and root-absent post-
   compaction rehydration/sentinel/compiler suppression pass within bounds.
6. Privacy, cleanup, protected-host invariants, exact local gates, and final CI
   pass.

## Required verification

Record all 004-v categories plus strict offline fixture validation, exact
working/failed key delta, startup diagnostic source/class/hash/length, corrected
fixture tests, seed/resume argv and turn budget, compaction/post-compaction
metrics, systemd-acceptance completeness update, scoped diff, and current CI.

## Completeness and remaining gap

Coding leaves compaction credit pending strategic review. On full compaction/
rehydration success, strategy may raise objective 004 from 80% to 90% and branch
readiness from ~87% to ~89%. Vision-capable E2E remains the only planned gap.
No production/cutover/generic compaction-provider claim.

## Publication contract

Push amendments to exact PR #6 branch; never create another PR or merge. Record
literal implementation head after all non-report work is remote. Atomically
publish exactly one immutable
`oap/reports/004-y-validate-compaction-catalog-and-rerun.md`; SELF must be the
sole final commit, its first parent must equal the implementation head, it must
change only that report, and it must be remote PR head before response FIFO
`OK`.

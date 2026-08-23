# OAP Work Order — 004-u

## Objective

Amend objective-004 PR #6 to prove actual or Codex-native forced/equivalent
long-session compaction with Codex 0.149.0 global-yolo, followed by same-identity
Local Coding rehydration/injection and hidden-sentinel compliance without an
unnecessary compiler-model call. Do not simulate the acceptance solely with a
handwritten zero-root HTTP envelope.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`
- Numeric objective / round: `004` / `004-u`
- PR mode: `AMEND_EXISTING_PR`
- Existing PR: #6, `https://github.com/ulfe-lmi/slaif-local-coding/pull/6`
- Required base: `main` at `7a2c36a0a40958a6059a765c2f9d5e5bf4ddc161`
- Required head: `oap/004-real-codex-governed-e2e`
- Current verified remote head / `004-t` SELF:
  `057fb4b4f5f3a43cedb6204ee39b616b6dfbcbbc`
- Prior implementation SHA:
  `61107b7073de6474e73eb4444aeeedb7d4b375d6`, verified sole parent of SELF.
- PR state: OPEN/non-draft/MERGEABLE-CLEAN; final report-head `test` SUCCESS.
- Required action: **NO NEW PR**; no coding merge/auto-merge.

## Strategic context

004-s/004-t established the accepted Codex-under-test topology and baseline:
global `--dangerously-bypass-approvals-and-sandbox`, candidate adapter 18031,
exact delegated dependency acquisition, compilation/injection, hidden sentinel
twice, persistent cache reuse, and zero additional compiler-model attempts on
the second invocation. Objective 004 is 40% / branch readiness ~79%.

The remaining compaction gap is not satisfied by existing fake-upstream or
handwritten zero-root tests. The current model catalog advertises a 150,000-token
physical context, with historical Codex compaction around 125,000. This round
may use a smaller disposable model-catalog context/threshold only to trigger the
same Codex-native compaction mechanism economically; it must not change the
protected Qwen service/model configuration.

Official OpenAI compaction guidance treats compacted state as opaque
continuation state. Do not inspect or depend on raw compacted contents; prove
behavior through sanitized events, request topology, metrics, and final
governance behavior.

## Bounded Codex capability setup

Use current Codex 0.149.0 help/bundled model-catalog facts to select the smallest
supported deterministic trigger:

1. Prefer an explicit Codex-native compaction/compact command or supported
   catalog threshold if exposed by 0.149.0.
2. Otherwise lower only the disposable test model catalog context window/
   auto-compaction threshold and drive a persistent Codex session across that
   threshold with bounded synthetic text/tool history.
3. If neither is supported, use a Codex-native session resume/fork or history-
   reduction mechanism only when Codex itself produces the reduced context.

Do not call the OpenAI hosted `/responses/compact` endpoint, parse opaque
compacted content, manually delete/modify Codex rollout history, fabricate a
zero-root request, or add a new compaction implementation. Record only supported
feature/field names, version, threshold numbers, event types/counts, context/
item counts, and hashes—never raw history or summary text.

## Bounded execution topology

Start one candidate adapter on loopback 18031 with a fresh private persistent
cache and static synthetic opaque identity. Use one private synthetic repository
with long `AGENTS.md`, the delegated dependency, and hidden sentinel. Launch the
Codex-under-test itself with global yolo and persistent disposable CODEX_HOME;
do not use `--ephemeral` for the session that must compact/resume.

Maximum budget:

- one initial governed session/turn to populate root/dependency state;
- at most four bounded synthetic continuation turns to cross the Codex-native
  compaction threshold;
- exactly one post-compaction verification turn;
- no retries after the first failed gate and no unrelated model calls.

Synthetic filler contains no governance, secrets, customer data, executable
instructions, or sentinel; each turn and total bytes/tokens are hard bounded.
The candidate and Codex child must be polled/reaped, and all temporary session/
fixture/cache data removed after sanitized evidence extraction.

## Acceptance sequence

### A. Seed governed state

Require the initial turn to reproduce the accepted 004-s behavior:

- exact dependency bytes/hash/length;
- one effective root and delegated dependency observed/acquired;
- required compiler-model attempts on miss;
- stable injection and hidden sentinel;
- process-local rehydration entry populated for the exact identity;
- no command failure or raw-content leakage.

### B. Codex-native compaction

Drive the same persistent Codex session until one of the following proves
compaction:

- explicit sanitized Codex compaction event/state transition; or
- Codex-native reduced-history continuation with a demonstrable request item/
  byte/token decrease and prior root content absent at the adapter boundary.

The proof must identify the same session/repository/route identity, the
pre/post history counts/byte hashes, and root-observation state without exposing
content. A mere new process, manually shortened prompt, fresh session, or
handwritten zero-root envelope is not proof.

If the bounded turn budget cannot trigger or identify Codex-native compaction,
stop with `codex_compaction_not_observable_within_bound`; do not modify Local
Coding or claim failure.

### C. Post-compaction Local Coding rehydration

On the first actual post-compaction request where the prior root is absent,
require:

- adapter retains the same trusted identity and finds the exact rehydration key;
- rehydration metric records a valid hit/injected outcome, not unavailable;
- stable constitution is injected immediately despite root absence;
- dependency/root compiler-model attempt count does not increase;
- cache/rehydration identity remains isolated and source/version matched;
- Codex produces the exact hidden dependency-derived sentinel;
- no prompt/source/tool/model/raw compacted content is logged/reported.

Do not require or report the opaque compaction text itself. The post-compaction
sentinel prompt must not contain/reveal the target.

## Failure and product-change rule

Do not modify Local Coding before the run. If actual compaction is proven but
rehydration/injection/sentinel fails, report the first direct product-boundary
gate with sanitized evidence; do not implement a speculative fix in this round.
If Codex cannot expose/trigger compaction within bounds, classify it as an
external acceptance-fixture limitation, not a product defect.

## Tight implementation scope

Use repo-only helpers. Add only persistent-session/compaction event facts,
bounded trigger orchestration, focused fake-event tests, and outcome docs/
transcript. No production change, general diagnostic framework, sandbox work,
host mutation, or broad refactor. Remove dead helper branches if safe; report
net helper/test line impact.

## Completeness and claims

- Keep objective 004 at 40% / branch ~79% if compaction is not observable or
  any acceptance gate fails.
- On full A+B+C success, strategy may raise objective 004 to 60% and branch
  readiness to ~83%; coding must leave percentages unchanged pending review.
- Remaining gaps after success: vision-capable E2E, broader security/
  observability hardening, and systemd candidate proof.
- No production, multi-user, gateway, cutover, generic compaction-provider, or
  vision readiness claim.

## Explicit non-goals

No hosted/account-bound compaction endpoint; no manual rollout/history edit;
no handwritten zero-root acceptance; no workspace/bubblewrap/sandbox diagnostic;
no protected 18020/Qwen/model/key/network/systemd/profile change; no vision,
gateway, production, multi-user, or cutover work; no prior OAP rewrite.

## Acceptance criteria

1. Codex-under-test uses global yolo and one persistent disposable session with
   a supported Codex-native compaction trigger.
2. Seed turn proves exact governed state and populates rehydration.
3. Actual compaction/reduced-history continuation is proven within the bounded
   turn budget without inspecting opaque content.
4. First root-absent post-compaction request rehydrates/injects immediately,
   preserves hidden sentinel, and adds zero compiler-model attempts.
5. Identity/version/source isolation, raw-content privacy, resource bounds,
   child/candidate cleanup, and protected-host invariants pass.
6. No product change occurs before evidence; first actual product failure or
   external fixture limitation is reported truthfully.
7. Focused/full local gates and final implementation/report-head CI pass.

## Required verification

Record lock/frozen sync, Ruff check/format, mypy, focused/full pytest, build,
wheel/sdist boundary, compileall, shell syntax, diff check; Codex version/yolo
argv/session identity; trigger method and thresholds; per-turn sanitized event/
history/request counts; seed dependency/compiler/injection/sentinel metrics;
compaction proof; post-compaction root absence, rehydration/injection/cache/
compiler-attempt/sentinel facts; call/turn budget; secret/raw scan; cleanup;
protected-host snapshot; scoped diff; and current GitHub checks. Wait for final
report-head CI.

## Protected live-host boundary

Candidate adapter is loopback 18031 only and must stop after testing. Bounded
authenticated calls to protected 18020 may pass only through the candidate for
this run. Never alter 18020, `qwen-serving`, model/checkpoint/patches/venv/
launch flags, keys, systemd, firewall/VPN/network bindings, active Codex
profiles, or host sandbox policy.

## Publication contract

Push amendments to exact PR #6 branch; never create another PR or merge. Record
literal implementation head after all non-report work is remote. Atomically
publish exactly one immutable
`oap/reports/004-u-real-codex-compaction-rehydration.md`; SELF must be the sole
final commit, its first parent must equal the implementation head, it must change
only that report, and it must be remote PR head before response FIFO `OK`.

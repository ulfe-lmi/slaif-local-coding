# OAP Work Order — 005-l

## Objective

Amend Local Coding PR #7 with one exact product-topology composed stream-owner
run. Replace 005-k's generic three-predicate `stream_contract_failed` check with
the already-proven bounded SSE lifecycle parser and safe Local metric/Gateway
accounting facts. Run the complete fake/no-model failure matrix first, then one
real composed run without a relay between Gateway, Local, and protected Qwen.
If the standard stream is green, continue the remaining real Codex/governance/
identity/isolation/accounting matrix in that same run. If it fails, stop and
publish the exact first failed subcondition and evidence-based owning layer; no
retry or further diagnostic round is authorized by this order.

## GitHub and objective state

- Repository: `ulfe-lmi/slaif-local-coding`.
- Round: `005-l`; mode `AMEND_EXISTING_PR`; **NO NEW PR**.
- PR #7: `https://github.com/ulfe-lmi/slaif-local-coding/pull/7`.
- Base/head: `main` / `oap/005-gateway-ingress-integration`.
- Required starting 005-k report head:
  `e4f72e2fdb3b655b302c6fd986d75b8b5d14acda`.
- Required 005-k implementation parent:
  `0dfe8efc429ed8d582e356aad85c3b50d22ed8b3`.
- Local PR is OPEN, non-draft, MERGEABLE/CLEAN; report-head `test` SUCCESS.

Read-only Gateway dependency:

- Repository: `ulfe-lmi/slaif-api-gateway`.
- PR #291 exact current 155-p head:
  `306ecb186b5c12db991a684e7c04e5c9f174eba2`.
- 155-p parent: `a8a2a7a8a2e84fbe7dd42658173dd6358f709444`.
- Gateway 155-o report/product head:
  `c6b33c9d1527d35d987bf10f8276f30797bc892c` /
  `06752b1126545590a2e4232311fb92a52f663b41`.
- Gateway PR is OPEN, non-draft, MERGEABLE/CLEAN; all ten current checks
  SUCCESS. No Gateway mutation is authorized.

Abort before protected traffic if either exact head changes, any required check
is non-successful, or report topology is invalid.

## Accepted evidence and revised ownership posture

Accept 005-j as current proof that the exact Local -> protected Qwen path passes
A–I with byte/digest-equal terminal SSE. Accept 005-k's direct product topology,
fake full-stack pass, cleanup, and protected run through authenticated model
visibility plus ordinary non-stream Responses success. No Local production
change was required in either round.

005-k's protected stream failed only through this aggregate predicate:

```text
status != 200
OR last parsed event != response.completed
OR timing dictionary empty
```

The helper used a simple `data:` line parser and discarded which predicate
failed. It did not emit status/content class, complete lifecycle, error-event
class, required timing milestones, Local upstream-status metric delta, or
Gateway accounting terminality before raising `stream_contract_failed`.

Current evidence therefore contradicts an unqualified Local↔Qwen blocker:
direct Qwen is green, Local A–I is green, Gateway-composed non-stream is green,
and only Gateway-facing streaming remains unresolved. Do not assign Gateway or
Local ownership until the exact safe stream facts below are observed.

## A. Zero-protected-traffic stream evidence closure

Before protected inference:

1. Verify exact heads/reports/checks/worktrees and one read-only protected
   health/models/service snapshot.
2. Replace `_stream_event_types`/generic predicate with one shared bounded
   repository-only parser contract derived from the corrected 005-j `SSEFacts`.
   Do not duplicate another event parser.
3. For one public stream, produce a fixed `ComposedStreamFacts` equivalent with
   only:
   - HTTP status class and content-type class;
   - response-header, first-byte, terminal, and normal-close timing buckets;
   - total bounded byte/count class and normal/abnormal close;
   - parseable, recognized-vocabulary, error-event, duplicate-terminal;
   - created/completed counts, response-ID relation, terminal status/output/
     usage validity;
   - fixed error field-name set plus allowlisted Gateway/Local/provider error
     code/type class; unknown values become `unknown`, never arbitrary text;
   - Local safe request/upstream-status/stream-duration/failure metric deltas;
   - Gateway reservation/ledger terminality and provider-call count class.
4. Emit one exact fixed first-failure enum, evaluated in this order:

```text
http_status_non_2xx
content_type_not_sse
response_headers_timing_missing
first_bytes_missing
sse_unparseable
event_vocabulary_unrecognized
gateway_error_event
response_created_missing_or_duplicate
response_completed_missing_or_duplicate
terminal_status_or_output_invalid
terminal_usage_invalid
response_id_mismatch
normal_close_false
terminal_or_close_timing_missing
local_upstream_non_2xx_or_failure
gateway_accounting_nonterminal
stream_contract_passed
```

5. Map owner only from direct facts:
   - Local upstream `2xx`/normal terminal bytes plus Gateway error/nonterminal
     result -> `gateway_stream_owned`;
   - Local upstream non-2xx/transport/failure before valid Qwen terminal ->
     `local_or_provider_owned`, refined only by existing 005-j A–I comparison;
   - valid Gateway-facing bytes but driver parser/timing failure ->
     `acceptance_harness_owned`;
   - complete stream/accounting -> `stream_contract_passed`.
6. Fake-test every first-failure branch, large and arbitrarily split chunks,
   full Qwen reasoning/tool vocabulary, unknown events, provider/Gateway error
   events, missing/duplicate terminal, invalid usage, non-2xx, early close,
   timing boundaries, and accounting mismatch.
7. Run the complete fake composed path with direct Gateway -> Local -> fake Qwen
   topology and require `stream_contract_passed`, safe terminal accounting, and
   complete cleanup.
8. Consolidate the now roughly 2500-line rehearsal script: remove obsolete
   relay/status/old-Gateway branches and duplicated parser/diagnostic code that
   are no longer exercised. Do not expand it into a general instrumentation
   framework. Production modules and wheel contents remain unchanged unless
   direct protected evidence later proves a Local defect.
9. Run focused/full static, fake, privacy, package, and CI gates before live use.

No protected inference is allowed during A. No raw prior runtime artifact may be
recovered; use immutable reports and current source only.

## B. One real composed run and stream decision

After A passes, start exactly one disposable protected composition using exact
Gateway/Local heads, temporary PostgreSQL, real official Codex 0.149.0
global-yolo, Local on 18031, and Local directly connected to unchanged protected
Qwen. No evidence relay, direct provider call, alternate prompt, or retry.

The predeclared sequence is:

1. Local/Gateway health/readiness and authenticated model visibility.
2. One standard non-stream Responses request with provider usage. This keeps
   the current run's accounting coherent; it is not a retry of a failure.
3. One standard streaming request with `max_output_tokens=32`, `store=false`,
   and the same signed identity/tool policy as fake mode.

At step 3, always snapshot and retain only `ComposedStreamFacts`, Local metric
deltas, and safe Gateway accounting facts before deciding. If the enum is not
`stream_contract_passed`, stop the run immediately, clean up, and report:

- exact first-failure enum;
- status/content/timing/event/terminal/error/close booleans and count classes;
- Local upstream status/failure/stream-duration deltas;
- Gateway provider-call and reservation/ledger terminal classes;
- owner classification from section A.5.

Do not continue to later matrix steps or issue any second stream.

If and only if step 3 is `stream_contract_passed`, continue in the same run:

4. one small synthetic image through the configured one-image route;
5. real Codex 0.149 global-yolo ordinary local tool use, exact delegated
   governance acquisition, compiler/cache/injection, and effective binding;
6. signed body/path/query/route identity acceptance and exact disabled search-
   declaration removal with ordinary function/custom/call/results preserved;
7. same owner/key/Codex session/repository zero-root rehydration with zero
   unnecessary new compiler-model attempt;
8. separate Codex session under the same key and second owner/key isolation;
9. exact/concurrent replay, body/query/path/route/signature tamper, explicit
   hosted/dropped choice, invalid key, and over-quota pre-provider rejection;
10. one reservation and terminal ledger outcome per admitted public request,
    provider usage finalization, consistent counters, no pending/duplicate IDs,
    zero Gateway rows for Local compiler calls, and no hosted-search fence/fee/
    authority;
11. controlled failure and complete rollback/cleanup without corrupt state.

Fake Qwen, mocks, direct Local evidence, non-stream success, or health checks do
not substitute for a green real stream and full remaining matrix.

## C. Owning-layer result law

- If `gateway_stream_owned`, make no Gateway change. Publish the exact safe
  handoff against the tested Gateway head for its strategic agent.
- If a Local production transport/SSE defect is directly established despite
  005-j, implement only the smallest correction, run fake regressions, and stop;
  no second protected request in this round.
- If protected Qwen/provider behavior contradicts 005-j, publish the exact
  contradiction and do not mutate the service or hide it with Local/Gateway.
- If `acceptance_harness_owned`, correct the harness only in pure/fake tests and
  report the blocker; do not retry protected traffic.
- If the stream/full matrix passes, update completion docs and return for
  strategic merge review.

Never manufacture terminal events, buffer/reconstruct the whole stream, weaken
auth/timeouts/accounting, swallow error events, or special-case the fixture.
Preserve signed identity, replay, cache/isolation, tool/image/constitution law,
credential separation, disconnect cancellation, and no raw logging.

## D. Privacy, protected-host, resource, and cleanup law

Use synthetic fixtures and existing protected credential references. Never
commit, report, print, log, metric-label, or persist raw bodies, prompts, source,
model text, SSE payloads, tool schemas/results, credentials, credential-source
paths, private endpoints, identities, signatures, nonces, canonical bytes,
database URLs, session values, or arbitrary exceptions. Evidence is fixed enums,
classes, booleans, counts, safe versions, fixture hashes, and bounded timing
buckets. Do not include protected endpoint values or credential-source paths in
the report.

Do not stop/restart/change protected Qwen, its service/config/model/venv/launch
flags/listener/context/image/tool/reasoning settings, keys, network, firewall/
VPN, or active Codex profiles. Do not start another model. Serialize calls and
honor the single-sequence limit.

Use one official `postgres:16` container: unique name, loopback random port,
tmpfs, `--rm`, finite health wait, no privileged/host network. `sudo` only for
exact Docker read/pull/run/stop/remove/inspect. No apt, daemon, Redis, Celery,
email, admin, TLS, public bind, or persistent DB.

On every outcome remove exact driver-owned Gateway/Local/PostgreSQL/fake/temp
clone/venv/config/cache/Codex home/workspace/Node/log/artifact/image state. Prove
no task listener/container/volume/solely-pulled image/process remains; worktrees
clean; protected Qwen same PID/start/restart/listener/config; text inactive;
18021/18031/random ports absent. Preserve unrelated ignored Local `.venv` and
direct-Qwen rollback.

## E. Regression, documentation, and merge choreography

Run focused harness/fake/SSE/timing/error/auth/tool/image/constitution/cache/
identity/replay/accounting/privacy tests plus full frozen Ruff/format/mypy/
pytest/build/wheel/sdist/compileall/shell/diff/secret/raw-log/package-boundary
gates and current Local CI. Skipped/not-run/pending is not pass for acceptance.

On complete pass update Gateway integration, testing, OAP runbook, and
Objective-005 criterion/completeness docs with exact tested heads, evidence,
cleanup, limitations, and merge choreography:

1. strategic review merges Local PR #7 first against exact tested open Gateway
   head `306ecb186b5c12db991a684e7c04e5c9f174eba2`;
2. Gateway strategy updates only its Local dependency pin/audit artifact and
   reruns checks against merged Local main, then reviews/merges PR #291;
3. verify both default branches and preserve direct-Qwen rollback until a
   separate persistent cutover/release.

No production/certification/compliance/generic-hardware/multi-worker/persistent-
cutover claim follows.

## Explicit non-goals

- No additional direct Local/provider diagnostic, second protected stream,
  alternate request, evidence relay, or broad diagnostic subsystem.
- No speculative Local fix, Gateway mutation/merge, protected Qwen workaround,
  service mutation, new PR, coding merge, persistent deployment, public bind,
  direct-Qwen retirement, or real credential provisioning.
- No reopening solved Gateway tool/pair/identity/session/signed route/fake
  composition/accounting absent the exact new stream facts.
- No sandbox/bubblewrap, host inventory, benchmark, image-quality, or release
  work.

## Publication contract

Amend only Local PR #7. Commit exact order/active unchanged with intended
non-report work, push support/tests/docs, inspect/fix CI, record literal
implementation SHA, then atomically publish exactly one immutable
`oap/reports/005-l-exact-composed-stream-owner-and-acceptance-closure.md` with
literal implementation SHA and `Report publication commit: SELF`. SELF changes
only that report, first parent equals implementation SHA, and is remote PR head
before exact response FIFO `OK`. Coding never merges.

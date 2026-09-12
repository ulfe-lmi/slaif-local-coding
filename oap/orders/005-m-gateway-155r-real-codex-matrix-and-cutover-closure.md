# OAP Work Order — 005-m

## Objective

Amend Local Coding Objective-005 PR #7 with the complete deferred real-system
acceptance matrix against exact accepted Gateway 155-r head
`2527030f5bbb90a7f0f354eb5347caee333ce4a7`. Then, only if that matrix is fully
green, perform the controlled candidate installation, Gateway/Codex-profile
cutover, representative post-cutover real Codex checks, no-bypass proof, and
exact rollback. This is Objective-005 contractual closure, not another
diagnostic objective. Use the existing coding worker and existing repository-
only harness; do not create another PR, Gateway change, Qwen change, or broad
instrumentation system.

## GitHub and accepted cross-repository baseline

Local Coding:

- Repository: `ulfe-lmi/slaif-local-coding`.
- Round: `005-m`; mode `AMEND_EXISTING_PR`; **NO NEW PR**.
- PR #7: `https://github.com/ulfe-lmi/slaif-local-coding/pull/7`.
- Base/head: `main` / `oap/005-gateway-ingress-integration`.
- Required starting 005-l report head:
  `1a87ce1c6628885e567cecc8f4a9e78ce7078341`.
- Required 005-l implementation parent:
  `2d1e362f4e1bf7eb6b4f29f9f116ed612fce9e78`.
- Local PR is OPEN, non-draft, MERGEABLE/CLEAN; current `test` SUCCESS.

Accepted Gateway:

- Repository: `ulfe-lmi/slaif-api-gateway`.
- PR #291: `https://github.com/ulfe-lmi/slaif-api-gateway/pull/291`.
- Exact accepted 155-r immutable report head:
  `2527030f5bbb90a7f0f354eb5347caee333ce4a7`.
- Exact 155-r final implementation/report parent:
  `19d9686636b0fbf27ab96d41c610a37dad3c087a`.
- 155-r activation head:
  `a08655180dcd280529ca798b3509d4f28e7f8ab7`.
- PR is OPEN, non-draft, MERGEABLE/CLEAN; all ten current report-head
  CI/CodeQL/PostgreSQL/E2E/Compose/documentation checks SUCCESS.
- The report commit changes only
  `oap/reports/155-r-retained-event-qualification-and-final-stream.md` and its
  first parent is the literal final implementation head.

Gateway 155-r is accepted upstream authority. Do not reopen or re-diagnose
Codex tool compatibility, exact client/server pair, Gateway principal/session
identity, signed Local identity, routing, fake composition, or streaming unless
new evidence from this exact head directly contradicts 155-r.

Abort before real traffic if either exact PR head changes, any required check
is non-successful, or topology/report verification fails.

## Accepted technical evidence

Accept without repetition:

- Local 005-j exact current Local -> protected-Qwen A–I byte/digest-equal
  terminal SSE proof;
- Local 005-k/005-l direct product topology, fake full-stack pass, protected
  model visibility, and ordinary non-stream success;
- Gateway 155-r qualification of the first rejected event as legitimate exact
  `response.output_item.added` reasoning metadata;
- Gateway's strict ordered reasoning and assistant-message stream validator,
  with tool/hosted-search/smuggling/orphan/duplicate/reorder/mismatch/overflow
  negatives remaining fail-closed;
- Gateway 155-r hook-free fake pass and one final protected composed standard
  stream with `2xx` SSE, one created/completed lifecycle, valid output/usage,
  finalized accounting, one Gateway->Local and one Local->Qwen call, normal
  close, zero Gateway error/rejection, and zero Gateway-induced Local
  disconnect;
- no Gateway or Local production ambiguity remains for ordinary standard
  streaming at these exact heads.

Do not count the accepted 155-r standard stream as a substitute for the real
Codex/governance/vision/identity/isolation/replay/accounting matrix below.

## Current protected-host and rollback baseline

At activation:

- host: `hinton1`;
- protected vision Qwen service active/running, PID `599296`, zero restarts,
  existing start timestamp, model `qwen3.8-27b`, context 100000, one sequence,
  one-image limit, protected listener on 18020;
- text Qwen service inactive;
- ports 18021, 18030, and 18031 free;
- no Gateway/Local process, service unit, listener, or Docker container;
- real Codex config exists, has no dedicated SLAIF Local/Gateway profile, and
  no custom loopback Local/Gateway provider; current OAP profiles must remain
  untouched;
- direct Qwen remains the protected rollback path.

Re-verify every fact before mutation. Do not expose config values, credentials,
provider URLs, or private paths in committed/report evidence.

## A. Exact-head no-live preflight and harness pin

Before inference or installation:

1. Verify exact Local/Gateway heads, report parents/paths, clean worktrees,
   current green checks, unique open PRs, and OAP ancestry.
2. Update every Local repository-only Gateway pin/vector/driver constant used by
   acceptance from `306ecb...` to exact accepted report head
   `2527030f...`; record final implementation parent `19d968...` separately.
   Reject moving branch state and unreported commits.
3. Import and exercise actual Gateway product modules from a detached exact
   checkout; never vendor/copy/reimplement its client, validator, identity,
   provider, routing, quota, or accounting logic.
4. Run exact Gateway/Local shared signed-identity and tool-filter provenance/
   semantic vectors, stale-version/digest/pair negatives, and complete fake
   composition with the permanent 155-r reasoning/message stream lifecycle.
5. Verify exact official Codex CLI 0.149.0 binary/checksum/version and global-
   yolo invocation. Use a driver-owned private Codex home/workspace; do not read
   host Codex session/history/cache.
6. Verify the full real matrix is a fixed ordered sequence with one overall run,
   per-request call bounds, no retries after product/accounting failure, and
   complete cleanup in `finally` paths.
7. Verify Local connects directly to protected Qwen; Gateway connects directly
   to Local; Codex connects only to Gateway. No diagnostic/evidence relay is
   permitted in the product path.
8. Run focused/full fake, stream, identity, replay, tool, image, constitution,
   accounting, privacy, package, lint/type/compile gates before real traffic.

No protected inference is allowed until A passes.

## B. Complete real composed acceptance matrix

Run exactly one disposable matrix using real Codex 0.149.0, real exact Gateway
155-r code, real Local PR #7 code, temporary PostgreSQL, and unchanged protected
Qwen:

```text
real Codex 0.149.0 global-yolo
  -> real Gateway 2527030f... on private loopback
       temporary PostgreSQL 16, synthetic users/keys/routes/pricing
  -> real Local Coding candidate on 127.0.0.1:18031
       signed identity v1, exact tool/image/constitution policies
  -> unchanged protected Qwen
  -> valid terminal response back through Local/Gateway to Codex
```

Use only synthetic fixtures and sequential calls. Stop at the first product or
accounting failure, collect only predeclared safe facts, clean up, and report
ownership. Do not retry or change prompts/limits.

### B1. Real Codex ordinary text and streaming

- Launch real Codex through Gateway, never directly to Local/Qwen.
- Require authenticated model visibility, process exit 0, `2xx` SSE,
  recognized ordered reasoning/message events, one `response.created`, valid
  terminal `response.completed` with usage, normal close, and a bounded expected
  synthetic answer predicate.
- Require one Gateway->Local request/response and one Local->Qwen inference call
  for the public model request; no Gateway typed error or Local disconnect.
- Record safe header/first-byte/terminal/close timing buckets, not raw text.

### B2. Governed tool and constitutional behavior

- Use a disposable repository with a long synthetic `AGENTS.md`, exact
  delegated `GOVERNANCE-DEPENDENCY.md`, distinctive hidden binding, and ordinary
  local shell/function tool requirement.
- Require real Codex to read the exact dependency once before substantive
  completion, with byte/hash/length equality established locally and only safe
  equality facts reported.
- Prove Gateway admits only the exact adapter-managed search declarations;
  Local removes `tool_search`/`web_search` before Qwen; ordinary function/custom/
  call/result items remain intact; Qwen performs no hosted tool execution.
- Prove root/dependency observation, deterministic candidates, compiler miss,
  validated compile/cache/injection, effective binding, and no raw tool markup.
- A second same-session zero-root/history-reduction request must rehydrate the
  governance state with no unnecessary compiler-model attempt.

### B3. Image/vision path

- Through the same real Codex/Gateway/Local chain, run one bounded synthetic
  full-image then later crop/history interaction using the accepted Objective-
  004 fixture contract.
- Require Local to observe multiple history images and protected Qwen to receive
  exactly the newest supported image, with successful terminal model response
  and governance still effective.
- Verify actual upstream image count/modality structurally; do not benchmark
  quality or report image/model content.

### B4. Signed identity and isolation

- Prove Gateway service Bearer and exact HMAC-bound method/path/query/body/
  principal/session/repository/route/timestamp/nonce are verified by Local;
  signed/internal/public credentials do not reach Qwen.
- Same authenticated owner/key plus same Codex session/repository must retain
  the intended Local state across requests.
- A distinct Codex session under the same Gateway credential must not receive
  the first session's governance.
- A second Gateway owner/key must remain independently isolated.
- Identity values remain opaque/transient and absent from logs, metrics, errors,
  cache filenames, model input, ledger/audit metadata, and report.

### B5. Replay, tamper, quota, accounting, and failure law

- Exact replay and concurrent replay: one accepted at most; duplicates rejected
  without duplicate provider/accounting effects.
- Body/query/path/route/signature/timestamp/nonce tamper and ambiguous/missing
  signed context reject before Local transform/provider work.
- Explicit dropped/hosted search choice rejects before provider and without a
  leaked reservation.
- Invalid public key and over-quota request reject before Local/Qwen.
- One controlled synthetic provider failure follows normal terminal failure
  accounting without touching protected Qwen.
- Every admitted public request has exactly one reservation and one terminal
  ledger outcome; successful rows finalize provider-reported usage; request/
  token/cost counters are consistent; no pending/duplicate request ID remains.
- Local compiler calls create zero Gateway public reservations/ledger rows and
  no hosted-search fence/hold/fee or authority appears.
- Prove failure/cancellation leaves no corrupt accounting, replay, cache,
  identity, or provider state.

### B6. No-bypass and cleanup proof

- Codex provider/profile base class must be Gateway only.
- Gateway Local route target must be Local only.
- Local upstream target must be protected Qwen only.
- No Codex process may connect directly to Local/Qwen; no Gateway process may
  connect directly to Qwen for the Local model; no alternative provider route
  may satisfy the acceptance predicates.
- Use process/listener/connection and exact config relationship facts without
  exposing endpoint values or credentials.
- Stop/remove the disposable topology completely and prove only the preexisting
  protected Qwen listener remains.

Mocks, fake Qwen, unit tests, CI, and Gateway 155-r standard stream are not
substitutes for B. B must be `REAL-E2E ACCEPTED` before section C.

## C. Controlled candidate installation and cutover

Run C only after every B criterion is green. This section is explicitly
human-authorized protected operational work for Local/Gateway/Codex profile
only; Qwen/service/network mutation remains forbidden.

### C1. Capture and backup exact pre-state

- Capture content hashes, mode, owner, existence, and safe structural facts for
  the real Codex config/profile file, any preexisting Local/Gateway unit/config/
  environment/cache/runtime state, relevant listeners/processes/containers,
  and protected Qwen service/process facts.
- Copy exact restorable Codex/config state into one private mode-0700 task root
  with files mode 0600. Never print or commit its content/path.
- Refuse cutover if ports 18030/18031 are occupied, a target unit conflicts, or
  exact rollback cannot be proven before mutation.

### C2. Install candidate chain

- Install/run Local from exact tested implementation on
  `127.0.0.1:18031` using a uniquely named user service unit, protected env
  reference, signed identity, fresh private bounded cache, restart/backoff,
  safe journal logging, and current production configuration.
- Install/run exact Gateway 155-r candidate on `127.0.0.1:18030` with one
  private temporary PostgreSQL backing store and the exact accepted Local route
  pointing to Local 18031. No public bind/TLS/firewall change.
- Create one dedicated real Codex acceptance profile pointing only to Gateway
  18030. Do not edit/remove the profiles used by active OAP agents and do not
  set the new profile as an implicit global default.
- Validate Local/Gateway health/readiness, model visibility, unit sandbox,
  ownership/permissions, and exact route chain before Codex traffic.

State labels at this point:

```text
IMPLEMENTED: yes
TESTED: yes
REAL-E2E ACCEPTED: yes (section B)
CUTOVER ACCEPTED: not yet
MERGED: no
RELEASE-READY: no
```

### C3. Post-cutover representative acceptance

Using only the dedicated profile, run real Codex 0.149 representative:

1. ordinary text/streaming terminal completion;
2. ordinary local tool plus delegated-governance binding and same-session reuse;
3. one bounded vision request/history transformation;
4. distinct-session isolation;
5. one safe quota/accounting terminal check.

Require the same signed identity/tool/image/privacy boundaries as B. Prove the
Codex process connected only to Gateway, Gateway Local route only to Local, and
Local only to protected Qwen. No unintended direct Codex/Gateway -> Qwen bypass
may exist for the accepted profile/route. Direct Qwen may remain available only
as an operator rollback path, not as a route selected by the cutover profile.

### C4. Rollback

- Stop/disable/remove only the candidate Gateway and Local units/processes,
  temporary PostgreSQL, candidate configs/env/cache/runtime/log artifacts, and
  dedicated Codex profile.
- Restore the exact pre-cutover Codex config bytes, mode, owner, and hash; if a
  target did not exist, prove it is absent again.
- Verify protected Qwen retains the same PID/start/restart/listener/config facts;
  text Qwen remains inactive; ports 18030/18031 and all temp ports are absent;
  no task container/process/unit/profile/cache remains; firewall/VPN/network
  state unchanged; original profiles function as before.
- Perform one read-only protected health/model check and safe original-profile
  structural validation. Do not issue another model inference merely for
  rollback.

Only after C1–C4 pass may state be `CUTOVER ACCEPTED`.

## D. Ownership and stop law

If any B/C case fails:

- localize the first failing component/stage from predeclared safe facts;
- change Local only for a direct Local product defect and rerun local/fake tests
  before returning to strategy—no protected retry in this round;
- if exact Gateway 155-r violates its accepted contract, make no Local/Qwen
  accommodation; publish a minimal reproducible Gateway handoff;
- if protected Qwen contradicts accepted A–I/155-r behavior, do not mutate or
  hide it; publish the exact external blocker;
- if harness/installation/rollback owns the issue, change only that support in
  fake/no-model tests and report; do not repeat the protected matrix/cutover.

Do not create a new objective, broaden architecture, manufacture terminal
events, weaken validation/auth/accounting, or count partial later cases as pass.

## E. Privacy, protected-host, and resource law

Use only synthetic fixtures and existing protected credential references.
Never commit, print, report, log, metric-label, or persist raw prompts, bodies,
source, images, model text, SSE payloads, tool schemas/results, credentials,
credential-source paths, private endpoints, real config content, identities,
signatures, nonces, canonical bytes, DB URLs, session values, or arbitrary
errors. Evidence is fixed states/enums, booleans, counts, safe versions,
committed synthetic-fixture hashes, config relationship classes, and bounded
timing buckets.

Do not stop/restart/change protected Qwen, its unit/config/model/checkpoint/
venv/patches/launch flags/listener/context/image/tool/reasoning settings, keys,
firewall/VPN/network bindings, or active OAP Codex profiles. Do not start a
second model. Serialize protected calls and honor the single-sequence limit.

Use official `postgres:16` with unique names, loopback-only ports, tmpfs,
`--rm`, finite readiness, no privileged/host networking. `sudo` only for exact
Docker read/pull/run/stop/remove/inspect operations. No apt, Docker daemon,
Redis, Celery, email, admin, TLS, public bind, or persistent production DB.

Preserve unrelated ignored Local `.venv`. Destructive cleanup targets only
exact validated task-owned paths/resources; no broad globs or shared roots.

## F. Documentation, state ledger, CI, and publication

Run focused matrix/cutover/rollback/harness tests plus full frozen Ruff/format/
mypy/pytest/build/wheel/sdist/compileall/shell/diff/secret/raw-log/package-
boundary gates and current Local CI. Missing/skipped/not-run/pending is not pass
for B/C acceptance.

On complete B+C pass update:

- `docs/SLAIF-GATEWAY-INTEGRATION.md` with exact Gateway 155-r pin and real
  matrix/cutover/rollback evidence;
- `TESTING.md`, `docs/OAP-RUNBOOK.md`, adapter configuration/installation docs;
- Objective-005 criterion/completeness ledger;
- an explicit state table distinguishing
  `IMPLEMENTED`, `TESTED`, `REAL-E2E ACCEPTED`, `CUTOVER ACCEPTED`, `MERGED`,
  and `RELEASE-READY`.

Record merge choreography only after full acceptance:

1. strategic review merges Local PR #7 first against exact accepted open Gateway
   head `2527030f5bbb90a7f0f354eb5347caee333ce4a7`;
2. Gateway strategy updates only its Local dependency pin/audit artifact and
   reruns exact checks against merged Local main, then reviews/merges PR #291;
3. verify both default branches; persistent deployment/release remains OAP 006
   or separately authorized operations.

At report publication, coding must state each lifecycle label exactly. It may
never claim `MERGED` or `RELEASE-READY`.

## Explicit non-goals

- No Gateway mutation/merge, Qwen mutation, architecture redesign, new PR,
  coding merge/auto-merge, public deployment, TLS/firewall/VPN change, or real
  user credential provisioning.
- No new diagnostic subsystem, direct Local/provider diagnostic, alternate
  stream qualification, sandbox/bubblewrap work, benchmark/model-quality work,
  or speculative improvement.
- No Objective 006 work before accepted/merged Objective 005.

## Publication contract

Amend only Local PR #7. Commit exact order/active unchanged with intended
support/tests/docs, push all non-report work, inspect/fix CI, record literal
implementation head, then atomically publish exactly one immutable
`oap/reports/005-m-gateway-155r-real-codex-matrix-and-cutover-closure.md` with
literal implementation SHA and `Report publication commit: SELF`. SELF changes
only that report, first parent equals implementation SHA, and is remote PR head
before exact response FIFO `OK`. Coding never merges.

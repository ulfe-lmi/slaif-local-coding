# OAP Work Order — 005-c

## Objective

Amend Objective-005 PR #7 with one fully disposable, rollback-proven gateway
service rehearsal using the unchanged pinned SLAIF API Gateway, a temporary
PostgreSQL 16 container, a temporary authenticated Local Coding candidate, and
the active protected Qwen vision fixture. Prove real gateway key auth, route/
model rewrite, quota reservation/finalization/ledger accounting, standard
OpenAI-client traffic, and real Codex text/tool/governance traffic through Local
Coding. Remove every temporary component and leave the human-selected vision
service running. Do not modify the gateway repository or perform persistent
cutover.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`.
- Numeric objective / round: `005` / `005-c`.
- PR mode: `AMEND_EXISTING_PR`; **NO NEW PR**.
- Existing PR #7:
  `https://github.com/ulfe-lmi/slaif-local-coding/pull/7`.
- Base/head: `main` / `oap/005-gateway-ingress-integration`.
- Current verified remote head / 005-b SELF:
  `2df2b03627b2bd04609d56202e01e83e205e8791`.
- 005-b implementation parent:
  `31f25aab09d185f1696d841f1c58be0da1ef6f38`.
- PR OPEN/non-draft/MERGEABLE/CLEAN; report-head `test` SUCCESS.
- Same PR only; coding never merges or enables auto-merge.

## Accepted state

Accept 005-a/b service-Bearer ingress, visible-ASCII token validation,
configured single-user identity, optional rehydration disable, actual pinned
gateway provider-adapter JSON/SSE driver, usage preservation, documentation,
and protected-host safety.

Remaining proof is the real gateway service boundary: public gateway key,
PostgreSQL-authoritative quota/accounting/ledger, route/model metadata, complete
HTTP path through Local Coding, real Qwen calls, and rollback cleanup.

## Authoritative unchanged gateway source

- Repository: `ulfe-lmi/slaif-api-gateway`.
- Pin exact remote-main SHA:
  `8f2813bf745b90221da33a7cfaf40726c5b1b480`.
- Do not use open PR #287 or any unmerged gateway branch.
- Clone/detach only in a private temporary directory; never edit tracked gateway
  files, create a gateway branch/PR, push, or commit generated state.
- Record pre/post `git status --short` and exact SHA; delete only the disposable
  clone after sanitized evidence extraction.

## A. Exact disposable topology

Use verified-free loopback ports selected at runtime:

```text
standard OpenAI client / disposable Codex 0.149.0 global yolo
  -> temporary SLAIF API Gateway on 127.0.0.1:<gateway-port>
       disposable PostgreSQL 16 on 127.0.0.1:<postgres-port>
       public synthetic sk-slaif gateway key
       provider kind=openai_compatible
       provider secret=synthetic Local Coding service token
       public model qwen3.8-27b-vision -> upstream qwen3.8-27b
  -> temporary Local Coding candidate on 127.0.0.1:18031
       service_bearer_static_identity
       fresh private cache/static single-user fixture identity
  -> protected Qwen vision 127.0.0.1:18020/v1
```

All public/service/upstream/database secrets are synthetic or existing protected
environment references and remain private. No real customer/user data.

## B. Temporary PostgreSQL via existing Docker engine

The host Docker engine is available through `sudo -n docker`; no containers were
running at strategic preflight. The gateway's own dev/CI contract uses
`postgres:16`.

Requirements:

1. Record pre-state: exact running container IDs/names and whether
   `postgres:16` exists locally.
2. If absent, pull only official `postgres:16`; record resolved image digest/ID.
3. Start one uniquely named container such as
   `slaif-005c-postgres-<random>` with:
   - `--rm`;
   - random verified-free loopback host port bound to 5432;
   - synthetic database/user/password;
   - tmpfs or an exact disposable volume for data;
   - no host/public bind, no privileged mode, no host networking;
   - health/readiness wait and finite timeout.
4. Use `TEST_DATABASE_URL`/gateway-safe test configuration only; never any
   discovered `DATABASE_URL` or persistent database.
5. Run gateway Alembic migrations against only that database.
6. On every exit path stop/remove the exact container and disposable volume.
7. If this round pulled an image that was absent before, remove only that exact
   unused `postgres:16` image after all evidence, unless removal would affect a
   pre-existing concurrent container; report cleanup exactly.
8. `sudo` is authorized only for these exact Docker read/pull/run/stop/remove/
   image-inspect cleanup commands—no apt, system service, network, firewall,
   group, daemon, or socket changes.

## C. Temporary gateway runtime and seed

Create a disposable venv under the same private temp root and install the pinned
gateway's declared runtime plus only the test/driver dependencies needed. No
system Python or Local Coding lockfile change.

Using actual gateway migrations and service/repository APIs (not direct ad hoc
SQL except read-only final evidence), seed minimal synthetic state:

- one active public gateway key with strict low request/token/cost quotas;
- one `openai_compatible` provider config whose `/v1` base points to Local
  Coding 18031 and whose server-side secret env name contains the synthetic
  adapter service token;
- one enabled Responses route mapping public
  `qwen3.8-27b-vision` to upstream `qwen3.8-27b` with only the capabilities
  required by the bounded tests;
- explicit deterministic local EUR pricing sufficient for reservation and
  finalization; no unknown-price bypass and no zero-cost shortcut unless the
  gateway's normal accounting contract explicitly supports and proves it;
- no admin UI, email, Celery, Redis, production catalog, real provider key, or
  personal data.

Run the actual gateway ASGI app on loopback with access logs/raw content logging
disabled. Readiness must pass without public exposure.

## D. Local Coding candidate

Run accepted Local Coding code from PR #7 on 127.0.0.1:18031 with:

- `service_bearer_static_identity` and the exact synthetic service token used by
  the gateway provider config;
- complete explicit synthetic single-user identity;
- fresh private cache;
- explicit Qwen vision route/model/context-compatible configuration;
- protected Qwen key only by existing environment reference;
- no systemd installation/profile/network/firewall change.

Capture safe metrics before/after. Stop/remove candidate and all temp state on
every result. Keep protected vision PID/start/restart/unit/launcher state
unchanged.

## E. Bounded real traffic sequence

Use standard OpenAI-compatible client semantics:

```text
OPENAI_API_KEY=<synthetic sk-slaif key>
OPENAI_BASE_URL=http://127.0.0.1:<gateway-port>/v1
```

Run sequentially with hard time/call/output limits:

1. authenticated `/v1/models` visibility for only the seeded public route;
2. one non-streaming Responses text request to real Qwen through both services;
3. one streaming Responses request, verifying typed SSE order and completed
   usage without full-stream buffering;
4. one small synthetic image Responses request to prove the selected vision
   route traverses gateway -> Local Coding -> Qwen with one upstream image;
5. one disposable real Codex 0.149.0 global-yolo text/tool/governance invocation
   through the gateway using a persistent private Codex home and a synthetic
   root/dependency fixture; require successful ordinary dependency read and
   effective hidden binding under the already accepted CR/LF-only semantics.

Do not repeat failed model calls. Stop at the first product/gateway/accounting
failure after collecting only sanitized structural facts. No full/crop vision
Codex repeat is needed; Objective 004 already proved that path directly through
Local Coding.

## F. Accounting and boundary proof

After each public gateway request, use gateway service/repository APIs or
read-only bounded DB queries to prove:

- one reservation per public request and final status as expected;
- one finalized usage ledger row per successful public request;
- request/token/cost used/reserved counters are internally consistent and no
  pending reservation remains;
- provider-reported usage returned through Local Coding is the authoritative
  finalization input;
- gateway public key is never forwarded to Local Coding/Qwen;
- adapter service token reaches only Local Coding and is never forwarded to
  Qwen;
- Qwen credential reaches only Qwen;
- Local Coding compiler-model calls, if governance triggers them, increase safe
  adapter compiler metrics but create no additional gateway public reservation/
  ledger row;
- failed/rejected authorization or over-quota request is rejected before Local
  Coding/upstream and recorded according to normal gateway law;
- no raw prompt/response/image/source/tool output/auth/key/database URL appears
  in gateway/adapter logs, metrics, ledger metadata, facts, or report.

Record only counts, statuses, bounded usage/cost decimals, fixed capability/
error labels, hashes/lengths, and component commit/image identifiers.

## G. Rollback proof and final host state

Before run capture hashes/facts for vision/text units, Qwen launch/config,
listeners, relevant Codex profiles, Docker state, Local Coding/gateway source
SHAs, and ports.

After run require:

- gateway and Local Coding listeners absent;
- PostgreSQL container/volume absent;
- temporary clone/venv/database/config/cache/Codex home/workspace/logs removed;
- any newly pulled postgres image removed as specified;
- protected vision service still active at same PID/start time with zero
  restarts; text remains inactive;
- port 18020 remains and 18021/18031/gateway/postgres temp ports are absent;
- no gateway or Codex profile persisted;
- direct vLLM route remains available and is not retired.

This is a disposable cutover **rehearsal**, not persistent cutover or production
deployment.

## H. Repository support, docs, and tests

Add repository-only driver/support and hermetic seam tests; exclude from wheel.
Do not vendor gateway code. Update gateway integration/runbook/completeness docs
with exact rehearsal evidence and limitations.

## Verification

Run driver-focused tests, exactly one disposable full rehearsal, full frozen
Ruff/format/mypy/pytest/build/wheel/compileall/shell/diff/secret/raw-log scans,
and current CI. No skipped/not-run gate may be called pass.

## Explicit non-goals

- No gateway repository change/PR/OAP mutation.
- No persistent gateway/Postgres/Redis/Docker/container/image/route/key/profile/
  service installation.
- No trusted signed per-user identity claim.
- No direct-vLLM retirement, firewall/VPN change, TLS/public bind, production
  cutover, or release claim.
- No protected Qwen service/model/config mutation; vision stays running.

## Completeness

On full success, coding leaves arithmetic pending strategic review; strategy may
raise Objective 005 from about 60% to about 80% and weighted branch readiness to
about 96%. Trusted per-user identity and an actual persistent rollback-proven
cutover remain unresolved human/architecture gates.

## Publication contract

Amend only PR #7; never create another PR or merge. Push all non-report work,
record literal implementation SHA, then publish exactly one immutable
`oap/reports/005-c-disposable-full-gateway-accounting-rehearsal.md` with literal
SHA and `Report publication commit: SELF`. SELF changes only report, parent
equals implementation SHA, and is remote head before FIFO `OK`.

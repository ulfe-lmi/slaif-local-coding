# OAP Work Order — 005-a

## Objective

Start Objective 005 as one new Local Coding PR. Add an explicit adapter-side
service-Bearer ingress boundary and prove that the **existing unchanged** SLAIF
API Gateway generic `openai_compatible` provider can route bounded Responses
traffic through Local Coding to a fake upstream. Preserve the current explicit
single-user static identity mode honestly. Inventory—but do not invent or
implement—a trusted per-user identity mechanism. Prepare the controlled-cutover
contract and rollback gates without changing any live service, Codex profile,
gateway repository, or protected network state.

## GitHub objective state

- Local Coding repository: `ulfe-lmi/slaif-local-coding`.
- Numeric objective / round: `005` / `005-a`.
- PR mode: `CREATE_NEW_PR` — create exactly one new PR.
- Required base: remote `main` at
  `570bd2b24ad4b041a07e0320d5ed44bc73e99ad5`, the verified Objective-004 merge.
- Required new head: `oap/005-gateway-ingress-integration`.
- Required PR title:
  `[OAP 005] Integrate existing gateway ingress and cutover contract`.
- Current Local Coding open PRs: none.
- Never reuse merged Objective-004 branch; never create a second Objective-005
  PR; coding never merges or enables auto-merge.

## Independently verified gateway state — read-only authority

The gateway is the separate existing repository
`ulfe-lmi/slaif-api-gateway`; do not modify, fork, branch, push, open a PR, or
write into a gateway checkout.

Verified gateway facts at activation:

- remote `main`: `8f2813bf745b90221da33a7cfaf40726c5b1b480`;
- remote-main `oap/active`: `151-i`;
- open gateway OAP PR #287:
  `oap/152-real-provider-accounting-qualification`, head
  `346cdc13bcc1eb42035fb1d6a3e82c137651f4a4`, all current checks green;
- generic `openai_compatible` runtime already exists, validates exact `/v1`
  backend URLs, reads a server-side secret environment name, substitutes the
  provider Bearer credential, does not forward the client gateway key, and
  retains gateway quota/accounting behavior;
- an isolated Qwen3.8 vision Codex candidate exists but is deliberately
  unregistered/live-unqualified and records Codex 0.148.0, not current 0.149.0;
- no gateway checkout or gateway service is installed/running on `hinton1`;
  no PostgreSQL/Redis/gateway listener was found;
- the protected human-selected Qwen vision service remains active on hinton1
  port 18020, context 100000; text service remains inactive.

Gateway source may be cloned/read at a pinned SHA into disposable `/tmp` state
for conformance execution. Preserve its files byte-for-byte and remove only the
exact disposable clone afterward. Never commit gateway code or generated
artifacts to Local Coding.

## Architectural boundary

```text
ordinary client with sk-slaif key
  -> unchanged SLAIF API Gateway
       public auth, permissions, quota, accounting, route/model rewrite
       substitutes private adapter service Bearer token
  -> SLAIF Local Coding
       authenticates service Bearer token
       private compatibility/governance/image processing
  -> private vLLM/Qwen
```

Gateway public responsibilities must not enter this repository. Local Coding
must not issue/validate public gateway keys, enforce user quota, price requests,
or implement gateway admin/routing UI.

## A. Explicit ingress service authentication

Add a strict optional configuration contract, disabled by existing defaults,
for gateway-to-adapter service authentication. Use a narrow name such as
`[gateway_ingress]` or equivalent typed settings:

```text
mode = disabled | service_bearer_static_identity
service_token_env = validated environment-variable name
```

Requirements:

1. `disabled` preserves the existing private loopback development behavior.
2. `service_bearer_static_identity` requires:
   - a nonempty valid environment-variable name;
   - the referenced nonempty secret at startup/readiness/request time;
   - constitution integration's complete static principal/session/repository;
   - loopback/private deployment documentation and explicit single-user scope.
3. Authenticate the incoming `Authorization: Bearer <service-token>` using
   constant-time comparison before image/constitution/compiler/upstream work.
4. Missing, duplicate, malformed, wrong-scheme, empty, oversized, or mismatched
   Authorization fails with fixed OpenAI-shaped 401/403 behavior and
   `WWW-Authenticate` where appropriate, without reflecting either token.
5. Never accept the public `sk-slaif-*` gateway key as the service token in
   examples/tests. Use unrelated synthetic service-token fixtures.
6. Strip inbound service authorization and all internal/spoofed identity headers
   before calling vLLM; continue substituting only the configured Qwen upstream
   credential.
7. Never log, metric-label, cache-key, hash-report, exception-reflect, or persist
   the service token or Authorization header.
8. Readiness reports a fixed ingress-auth component state without secret/env
   value disclosure.
9. Bound secret/env/header lengths and reject control characters.
10. Configuration must fail closed for contradictory modes, missing static
    identity, or unsafe public binding. Do not silently enable gateway auth from
    the presence of an environment variable.

No public listener/TLS is added; the adapter remains private.

## B. Static identity honesty and isolation

The existing gateway generic provider substitutes one backend credential but
does not yet have proven trusted per-request principal/session/repository headers
for Local Coding. Therefore this round must:

- keep the complete configured static identity as the only accepted
  cross-request governance/cache identity in service-Bearer mode;
- label it explicitly `single-user local-appliance`, never multi-user,
  per-gateway-key, per-owner, or signed identity;
- prove spoofed `X-SLAIF-*`, `X-Internal-*`, forwarding, cookie, and client
  Authorization values cannot override static identity or reach Qwen;
- prove two differently authenticated public-gateway user simulations cannot be
  represented as isolated adapter principals through this existing service
  contract; record that as a missing trusted-identity capability rather than
  faking separation;
- document the safe deployment choice: one explicitly single-user Local Coding
  route/identity, or disable cross-request rehydration/cache reuse until a
  coordinated trusted identity contract exists;
- do not add caller-controlled identity headers, unsigned metadata, raw gateway
  keys, IP addresses, request IDs, or model strings as cache identity.

If current code cannot safely disable cross-request rehydration while preserving
ordinary request behavior, report the exact adapter-side product gap for a
same-PR continuation; do not weaken isolation.

## C. Unchanged-gateway conformance proof

Create repository-owned, bounded conformance vectors and tests for the existing
gateway generic-provider behavior. The authoritative gateway source remains
read-only/pinned.

At minimum prove:

1. a gateway-shaped request arrives with the synthetic adapter service Bearer,
   not the simulated public key;
2. Local Coding authenticates it, preserves supported Responses request fields,
   applies explicit route/model policy, and calls fake vLLM with only the Qwen
   upstream Bearer;
3. text, SSE, ordinary function/custom tool continuation, error sanitization,
   and one-image route behavior remain compatible;
4. gateway public model rewrite results in Local Coding/upstream model
   `qwen3.8-27b`; Local Coding does not reimplement public model permissions;
5. safe upstream usage survives Local Coding unchanged so the gateway can
   finalize provider-reported usage; internal compiler calls remain separately
   observable capacity overhead and are never returned as extra public calls;
6. rejected ingress requests make zero compiler/upstream calls and no cache
   mutation;
7. response/SSE ordering and disconnect remain unbuffered;
8. no raw prompt/source/image/tool output/public key/service token/Qwen key
   appears in logs, metrics, cache filenames, vectors, or report evidence.

When practicable, run a disposable pinned-gateway-main provider-adapter driver
against a temporary Local Coding candidate/fake vLLM and record only sanitized
request/status/header/usage/accounting-boundary facts. If gateway dependencies
make this unavailable, the repository-owned vectors/fake contract must still
pass and the cross-repo executable proof is `BLOCKED|NOT RUN`, never pass.

Do not require gateway PostgreSQL, Redis, Docker, sudo, or live provider keys
unless safely disposable and already available. Do not mutate the gateway OAP
workflow.

## D. Contract and coordinated-next-step documentation

Update `docs/SLAIF-GATEWAY-INTEGRATION.md` and related configuration/security/
deployment docs with:

- exact existing service-Bearer contract and examples using environment names;
- static single-user identity limitation;
- canonical request/response/usage boundary;
- current gateway main SHA and candidate profile mismatch (Codex 0.148 vs 0.149)
  as dated evidence, not a permanent claim;
- explicit statement: no gateway code change was made or authorized;
- an evidence table distinguishing existing-gateway capability, adapter-side
  capability, and missing trusted per-user identity;
- a proposed signed-identity contract only as non-active design material if
  needed, with no claim the gateway implements it;
- cross-repository coordination rule: any future gateway change needs its own
  gateway OAP objective/PR after its current workflow is resolved and explicit
  human authorization.

## E. Controlled-cutover plan — preparation only

Create/update a precise rollback-first runbook for a later continuation. Do not
perform cutover in `005-a`.

The plan must require:

1. merged/green accepted Local Coding version and pinned gateway commit;
2. exact backups/hashes of gateway route/provider metadata, Codex profile, unit
   files, environment files, listener/firewall state, and current direct Qwen
   endpoint;
3. candidate Local Coding on 18031 first;
4. gateway generic provider points to Local Coding, never directly to vLLM;
5. bounded standard OpenAI client and real Codex text/tool/SSE/vision/governance
   checks through gateway;
6. exact gateway quota reservation/finalization/ledger facts from provider
   usage, with compiler overhead separately observed;
7. no active coding/strategic turn depends on the endpoint being switched;
8. direct vLLM exposure is not retired until gateway path acceptance and human
   approval;
9. rollback restores exact prior provider route/profile/unit and health;
10. final listener/firewall/VPN/service state verified independently.

Because no gateway service is running on hinton1, actual cutover is `NOT RUN`.

## F. Verification

Run focused config/auth/header/readiness/isolation/conformance/stream/SSE/image/
usage/privacy tests; full frozen Ruff/format/mypy/pytest/build/wheel boundary/
compileall/shell/diff/secret/raw-log scans; and current GitHub CI. No protected
model call is required. Read-only vision health may be checked once without raw
content; preserve PID/restart/listener/unit hashes.

## Explicit non-goals and protected-host law

- No gateway repository mutation, gateway PR, database, Redis, Docker, catalog
  import, gateway service deployment, or public key creation.
- No signed per-user identity implementation unless it already exists unchanged
  in the gateway and is proven by direct evidence.
- No live gateway cutover, Codex profile change, Qwen service change, port 18020
  mutation, firewall/VPN/network change, or direct-vLLM retirement.
- Vision service remains active per human instruction; text remains inactive.
- No production/multi-user/cutover/release claim.

## Completeness

Objective 005 begins from 5%. On successful adapter service-auth and unchanged-
gateway contract proof, coding leaves arithmetic unchanged pending strategic
review; strategy may raise Objective 005 to approximately 35% and weighted
branch readiness from about 91% to about 93%. Missing trusted per-user identity
and actual rollback-proven gateway cutover remain explicit.

## GitHub and publication contract

Start from exact remote `main`; create only
`oap/005-gateway-ingress-integration`; push; create exactly one non-draft PR with
the required title/base/head; inspect/fix in-scope checks; never merge.

Commit exact activated order/active unchanged with implementation/docs/tests.
Push all non-report work first and record literal 40-hex implementation SHA.
Publish exactly one immutable
`oap/reports/005-a-existing-gateway-service-auth-integration.md` with literal
implementation SHA and `Report publication commit: SELF`; SELF changes only
that report, parent equals implementation SHA, and is remote PR head before
response FIFO `OK`.

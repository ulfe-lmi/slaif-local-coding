# OAP Work Order — 005-b

## Objective

Amend Objective-005 PR #7 to close the first-round review gaps without changing
the gateway repository: harden service-token syntax, add an explicit ability to
disable process-local zero-root rehydration for shared service-Bearer
deployments, and execute the pinned **existing gateway**
`OpenAICompatibleProviderAdapter` directly against a temporary Local Coding
candidate and fake vLLM. Preserve honest limits: this is still not trusted
per-user identity or live gateway cutover.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`.
- Numeric objective / round: `005` / `005-b`.
- PR mode: `AMEND_EXISTING_PR`; **NO NEW PR**.
- Existing PR #7:
  `https://github.com/ulfe-lmi/slaif-local-coding/pull/7`.
- Base/head: `main` / `oap/005-gateway-ingress-integration`.
- Current verified remote head / 005-a SELF:
  `2af482ada355c1fd6708c25f0f4718bd71ea6d4c`.
- 005-a implementation parent:
  `0a4a12d8efbb452bdccbd5daaf6c84f751104fd9`.
- PR OPEN/non-draft/MERGEABLE/CLEAN; report-head `test` SUCCESS.
- Same PR only; coding never merges or enables auto-merge.

## Accepted 005-a state

Accept the disabled-by-default, loopback-only
`service_bearer_static_identity` ingress boundary, constant-time comparison,
pre-body/pre-transform rejection, Qwen credential substitution, spoofed-header
stripping, fake gateway vectors, documentation, and protected-host preservation.

The remaining direct gaps are:

1. environment service-token validation permits spaces/non-ASCII and bounds
   characters rather than encoded bytes, although the HTTP Bearer parser cannot
   use such values safely;
2. process-local zero-root rehydration cannot currently be disabled, so a shared
   backend service credential plus static identity must not be presented as safe
   across public gateway users;
3. the actual gateway provider adapter was `NOT RUN`;
4. gateway `main` header construction allows only Accept/Content-Type/
   Content-Length/X-Request-ID and explicitly filters identity/session/gateway/
   token headers, so no trusted per-user metadata exists unchanged.

## A. Service-token syntax hardening

Use one shared validator for configured and supplied tokens:

- nonempty visible ASCII only, bytes `0x21..0x7e`;
- no space, tab, Unicode, control, DEL, CR/LF, leading/trailing whitespace, or
  embedded whitespace;
- UTF-8/ASCII encoded byte length at most `MAX_SERVICE_TOKEN_BYTES`;
- inbound Authorization remains exactly one `Bearer <token>` value with one
  separator and no extra segments;
- constant-time compare only after both values pass the same validation;
- failures remain fixed/non-reflecting and never log the value.

Add boundary tests at 1/max/max+1 bytes, every whitespace/control class,
Unicode, malformed schemes/separators, duplicate headers, and environment/
request parity. Correct the systemd example comment to say the environment file
contains variable assignments/credential values, not an “env name”.

## B. Explicit rehydration disable switch

Add `enabled: bool = true` to bounded `[constitution.rehydration]` configuration
with unchanged default behavior.

When false:

- never populate the process-local rehydration map after observed-root
  injection;
- a zero-root request never matches/injects prior state and preserves the
  post-image-policy request;
- emit only fixed `disabled`/`rehydration_disabled` metrics/status reasons;
- do not affect current-request root observation, exact content-addressed
  compiler cache, dependency compilation, working-set selection, or injection;
- do not clear authoritative source or mutate cache as a side effect;
- restart/TTL/LRU behavior remains unchanged when enabled.

Prove with two simulated public-user sequences under one service credential:

1. user A sends root/dependency and receives current-request injection;
2. a following zero-root “user B” request receives no A rehydration/injection;
3. different root hashes never cross;
4. exact same source-hash compiler-cache reuse, if retained, is documented as
   content-addressed derived reuse only—not identity/session memory—and cannot
   create zero-root disclosure;
5. raw sources/prompts/tool output remain absent from persistent cache/logs.

Documentation must say this is a safe degradation option when the unchanged
gateway lacks trusted per-user identity. It loses post-compaction/zero-root
rehydration and is therefore not equivalent to the accepted single-user path.
Do not call it multi-user identity/isolation or full governed Codex readiness.

Keep `service_bearer_static_identity` requiring complete configured identity.
Do not derive identity from untrusted headers/public keys/IP/request IDs.

## C. Executable unchanged-gateway provider driver

Use a disposable pinned clone/worktree of gateway `main`
`8f2813bf745b90221da33a7cfaf40726c5b1b480`. Never edit/push/branch it.

Create repository-only Local Coding driver support as needed, but do not vendor
gateway code. In one bounded run:

1. import the actual gateway
   `slaif_gateway.providers.openai_compatible.OpenAICompatibleProviderAdapter`
   and actual `ProviderRequest` from the pinned clone;
2. use a disposable Python environment or safe `PYTHONPATH`; install only
   routine temporary dependencies without touching system Python;
3. construct Local Coding via production `create_app` with enabled service
   ingress, static identity, candidate network listener on a verified-free
   loopback port (18031 preferred), and fake vLLM transport;
4. configure the gateway adapter base URL to the candidate `/v1` and provider
   API key to the synthetic adapter service token;
5. execute actual gateway adapter non-stream Responses and streaming Responses
   or the nearest actual methods the pinned adapter exposes;
6. prove the gateway adapter rewrites to upstream model `qwen3.8-27b`, sends only
   service Bearer, receives OpenAI-shaped response/SSE/usage, and Local Coding
   sends fake vLLM only the Qwen synthetic credential;
7. prove client/gateway key material is absent from `ProviderRequest`, adapter
   upstream request, logs, metrics, facts, and retained state;
8. prove no PostgreSQL/Redis/accounting service is invoked in this provider-
   adapter-only driver; do not claim quota/ledger execution from it;
9. record exact gateway SHA, class/method names, statuses, safe usage counts,
   SSE event ordering/counts, and cleanup only.

If pinned gateway imports require a large dependency stack, create a disposable
venv under `/tmp`, install its declared runtime requirements there, and remove
only that exact temp boundary. No Docker/sudo/Postgres/Redis. A failed import or
contract is a real compatibility finding, not a reason to copy/reimplement
gateway behavior.

Add hermetic tests for the Local Coding driver seam so normal CI does not clone
or network-access the gateway.

## D. Gateway identity capability audit

Document direct pinned-source evidence:

- `ProviderRequest.extra_headers` exists;
- `build_provider_headers` allowlists only standard safe transport/request ID
  headers and filters fragments including session/token/gateway/authorization;
- current Responses service construction does not provide trusted Local Coding
  principal/session/repository headers;
- therefore signed identity cannot be achieved by configuration alone.

This is evidence, not authorization to modify the gateway. Keep the future
signed contract non-active.

## E. Cutover status and next gate

No actual gateway service/cutover exists. Update the runbook so a later
single-user reference cutover may use static identity with explicit human risk
scope, while any shared/multi-user route must either:

- use rehydration disabled with documented loss of governance survival, or
- wait for separately authorized trusted identity support.

Do not retire direct vLLM, change profiles, or operate services.

## Verification and safety

Run focused token/rehydration/driver/privacy tests; executable pinned gateway
driver once; full frozen Ruff/format/mypy/pytest/build/wheel/compileall/shell/
diff/secret/raw-log scans; current CI. One read-only vision health check is
allowed; no model call.

Gateway repository remains unchanged. Vision remains active, text inactive,
port 18020 unchanged, no 18021/18031 residue.

## Completeness

On success, coding leaves arithmetic unchanged pending strategic review;
strategy may raise Objective 005 from about 35% to about 60% and weighted branch
readiness to about 95%. Trusted per-user identity, full gateway accounting path,
and rollback-proven live cutover remain missing.

## Publication contract

Amend only PR #7; never create another PR or merge. Push all non-report work,
record literal implementation SHA, then publish exactly one immutable
`oap/reports/005-b-executable-gateway-driver-and-no-rehydration-mode.md` with
literal SHA and `Report publication commit: SELF`. SELF changes only report,
parent equals implementation SHA, and is remote head before FIFO `OK`.

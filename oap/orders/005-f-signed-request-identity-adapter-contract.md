# OAP Work Order — 005-f

## Objective

Amend Objective-005 PR #7 with the complete Local Coding side of a versioned,
replay-protected signed gateway identity contract. Authenticate service Bearer
first, verify HMAC-bound request identity/body/path/query before transformation,
and use the verified per-request principal/session/repository/route throughout
compiler cache and rehydration identity. Preserve disabled/static modes and
default behavior. Add canonical conformance vectors and future-gateway proposal
updates, but do not modify or run the gateway or protected model.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`.
- Numeric objective / round: `005` / `005-f`.
- PR mode: `AMEND_EXISTING_PR`; **NO NEW PR**.
- Existing PR #7:
  `https://github.com/ulfe-lmi/slaif-local-coding/pull/7`.
- Base/head: `main` / `oap/005-gateway-ingress-integration`.
- Current verified remote head / 005-e SELF:
  `a9874b99e36dc639ddcbea067930a99539b7c73a`.
- 005-e implementation parent:
  `8ce107c1d8297e16d13d287a6becf6801cfdcaf1`.
- PR OPEN/non-draft/MERGEABLE/CLEAN; report-head `test` SUCCESS.
- Same PR only; coding never merges or enables auto-merge.

## Accepted state and authority

Accept existing service-Bearer static identity, token hardening, rehydration
disable, pinned provider driver, disposable gateway standard-traffic/accounting
partial evidence, security containment/path guards, and route-scoped Codex tool
filter contract.

Gateway remains separate/unmodified. This round defines and implements only the
adapter/verifier side of future signed identity; docs/vectors must say gateway
support is `NOT IMPLEMENTED` and `NOT AUTHORIZED` while its PR #287 remains
open.

## A. Versioned configuration and modes

Extend `[gateway_ingress]` with an exact third mode:

```text
disabled
service_bearer_static_identity
service_bearer_signed_identity_v1
```

Signed mode requires:

- validated visible-ASCII `service_token_env` as already implemented;
- separate validated `signing_secret_env` with a minimum 32 bytes and bounded
  maximum, visible ASCII or decoded fixed encoding selected/documented once;
- finite clock-skew window (default <=60 seconds, configurable 1..300);
- finite replay TTL >= skew window, max nonce entries, and nonce length bounds;
- constitution/compiler/route integration enabled, but no configured static
  principal/session/repository used as request identity;
- loopback/private bind and explicit v1 schema/policy versions.

Disabled and static modes reject signed-only settings. Signed mode rejects
static identity fields or clearly treats them as forbidden fallback—never
silently mixes identities. Defaults remain disabled and existing configs remain
valid.

## B. Exact wire contract

Use fixed headers, case-insensitive names with exactly one value each:

```text
X-SLAIF-Identity-Version: v1
X-SLAIF-Principal: <opaque>
X-SLAIF-Session: <opaque>
X-SLAIF-Repository: <opaque>
X-SLAIF-Route: <configured route name>
X-SLAIF-Timestamp: <canonical decimal Unix seconds>
X-SLAIF-Nonce: <bounded base64url/no-padding or lowercase hex>
X-SLAIF-Signature: v1=<64 lowercase hex HMAC-SHA256>
```

Opaque fields must use one documented visible-ASCII grammar and strict lengths;
no paths, emails, public keys, IPs, model text, whitespace/control/Unicode, or
raw secrets. Values remain transient and must not be logged/reported.

Canonical signing bytes are UTF-8 newline-separated fields with a fixed leading
domain/version and no ambiguous escaping:

```text
slaif-local-coding-identity-v1
METHOD
PATH
sha256(raw_query_bytes)
sha256(exact_bounded_body_bytes)
principal
session
repository
route
timestamp
nonce
```

Document exact newline/trailing-newline behavior. Reject methods/paths outside
supported proxy routes. Sign the raw ASGI query bytes by hash so ordering and
duplicates are bound. Body hash uses exact bytes before JSON decoding or
transformation.

## C. Authentication order and failure law

For signed mode:

1. Validate service Bearer exactly as current code before reading body.
2. Read body through existing hard bound only.
3. Validate unique identity headers/grammars/timestamp/nonce/signature shape.
4. Resolve signing secret safely; missing/invalid secret is fixed 503/readiness
   unavailable.
5. Recompute HMAC and compare with `hmac.compare_digest`.
6. Enforce clock skew with injectable monotonic/wall clock seam.
7. Atomically reject replayed `(signature-version, nonce)` using only an HMAC/
   SHA-256 digest of nonce in bounded process-local TTL/LRU state; never store
   raw nonce/identity/body.
8. Decode/validate JSON, select exact route/model/endpoint, and require verified
   `X-SLAIF-Route` equals the selected configured route before any image/tool/
   constitution/compiler/cache/upstream work.
9. Strip every service/signed/internal header before Qwen.

Use fixed OpenAI-shaped 401/403/409/422/503 codes/reasons without reflecting
identity/signature/timestamp/nonce. Missing/duplicate/malformed/stale/future/
bad-signature/replay/route-mismatch requests make zero compiler/upstream/cache/
rehydration mutation. Failed signatures must not consume nonce state; concurrent
identical valid requests allow exactly one.

## D. Dynamic request identity integration

Introduce one immutable typed internal request identity passed explicitly from
the verified ingress result into the constitution pipeline. Refactor static
identity construction without global mutation:

- disabled/static modes use the existing configured identity exactly;
- signed mode uses verified principal/session/repository and verified route;
- compiler `CacheIdentity`, source/dependency cache keys, rehydration key/match,
  replacement/invalidation, and selector/injection all use the request identity;
- no pipeline-global “last request identity” or mutable config swap;
- concurrent requests for different identities cannot cross;
- zero-root rehydration matches only exact signed principal/session/repository/
  route/model/policy dimensions;
- same signed identity rehydrates; changed principal/session/repository/route
  misses safely;
- restart/TTL/LRU/byte bounds and rehydration-disabled mode remain correct;
- identity strings never appear in model-visible injection, filenames, logs,
  metrics, errors, report facts, or public responses; filesystem names remain
  canonical digests/HMAC-safe.

## E. Replay/cache/security tests

Add exhaustive pure/fake-upstream/concurrency tests for:

- canonical vector exact bytes/signature;
- header case, duplicates, missing/extra fields, invalid grammar/length/control/
  Unicode;
- body/query/path/method/identity/route/timestamp/nonce tampering;
- stale/future edge boundaries and injectable clock;
- invalid signature not reserving nonce;
- exact replay, concurrent replay, TTL expiry, LRU/entry bound;
- service-token vs signing-secret separation and rotation behavior;
- route mismatch before transformations;
- two principals/sessions/repos/routes with same/different source hashes;
- same-identity zero-root rehydration and every changed dimension isolated miss;
- compiler/cache dedup limited to intended exact identity/content contract;
- signed mode with rehydration disabled;
- static/disabled regression and default byte stability;
- signed headers stripped before fake Qwen;
- no secret/identity/raw body in logs/metrics/cache paths/errors.

## F. Cross-repository vectors and proposal

Add a content-free canonical JSON fixture containing synthetic inputs, exact
canonical-string SHA-256, synthetic signing secret identifier/value allowed only
in test fixture, expected HMAC, and expected accept/reject cases. No real keys or
private identifiers.

Update gateway integration/tool-filter proposal with:

- signed identity v1 exact contract;
- key separation/rotation/replay requirements;
- gateway must derive opaque principal from authenticated gateway key/owner
  truth, session/repository only from trusted gateway-managed context—not raw
  client headers;
- current gateway extra-header filter does not implement this;
- separate authorized gateway OAP PR required;
- tool-envelope route capability and signed identity should be one coordinated
  gateway integration change, not piecemeal public relaxation.

No gateway patch/code/vendor copy.

## G. Security containment

All scripts/tests obey 005-d path guards. No host CODEX_HOME/session/history/
cache access, no no-model captures, no Docker/Postgres, no network clone needed
for normal tests. Preserve the sanitized incident record and do not claim
credential rotation occurred.

## Verification and protected safety

Run focused canonical/HMAC/replay/concurrency/identity/pipeline/privacy tests and
full frozen Ruff/format/mypy/pytest/build/wheel/compileall/shell/diff/secret/
raw-log scans plus current CI.

No gateway/adapter listener, Docker/Postgres, Qwen API/model call, service/
profile/network mutation. Vision remains active, text inactive, 18020 present,
18021/18031 absent.

## Completeness

Do not mark gateway integration/cutover complete. On success, adapter-side
trusted identity may be counted as prepared, but current gateway still rejects
Codex and emits no signatures; live accounting/cutover remain blocked.

## Publication contract

Amend only PR #7; never create another PR or merge. Push all non-report work,
record literal implementation SHA, then publish exactly one immutable
`oap/reports/005-f-signed-request-identity-adapter-contract.md` with literal SHA
and `Report publication commit: SELF`. SELF changes only report, parent equals
implementation SHA, and is remote head before FIFO `OK`.

# OAP Work Order — 006-a

## Objective and authoritative starting state

Objective006 is a NEW post-Objective-005 security-hardening objective: make
signed-request nonce replay protection correct for the full inclusive timestamp
validity window and fail closed under bounded-store capacity pressure. This human
objective deliberately supersedes the old non-active roadmap assignment of006 to
packaging. CREATE_NEW_PR from current remote main; create exactly one new branch
`oap/006-signed-request-replay-hardening` and one PR; coding never merges.

Repository: `ulfe-lmi/slaif-local-coding`. Strategy fetched and independently
verified remote main exactly
`e3f10e93c1ea84bf4021fd15d566bf577d5a9dcf`, the accepted Objective005 merge;
merged-main CI run34718306956 SUCCESS. No open PRs. No006 order/report/branch or
PR exists after reconciliation. Start from this exact remote main, not the old
local branch or local `main` (which is behind). Preserve the three pre-existing
empty untracked files `Local`, `clean`, `unchanged`; do not stage/delete them.
Preserve all immutable Objective005 artifacts and history.

Use the normal existing hosted coding profile `oap-coding-luna-xhigh`
(`gpt-5.6-luna`, xhigh) without profile/model/account mutation. Keep this single
006-a round active through ordinary diagnosis, implementation, test/CI repair,
review preparation and final report. Test failures, design details, refactoring,
typing/format/CI defects and unexpected interactions are work to solve here, not
reasons to publish an intermediate BLOCKED report, return control, request human
permission or invent006-b. Publish the immutable report only after complete green
closure, unless an actual external authority/safety boundary makes all further
progress impossible after safe alternatives are exhausted.

## Verified defects and current ownership

Strategy independently inspected current main before activation:

- `src/slaif_local_coding/gateway_identity.py`: `ReplayProtector.reserve` stores
  `now + ttl_seconds`, purges at `expiry <= now`, and LRU-evicts the oldest live
  digest to admit a new one. `verify_signed_identity` separately accepts while
  `abs(now - signed_timestamp) <= clock_skew_seconds`, then passes no timestamp
  horizon to the protector. Without explicit `now`, it can sample `time.time()`
  twice. The state stores SHA-256 nonce digests, which must remain the privacy
  boundary.
- `src/slaif_local_coding/config.py`: signed mode defaults skew60/TTL60 and only
  requires TTL >= skew; max replay entries is bounded1..1,000,000.
- `src/slaif_local_coding/app.py`: one process-local protector is constructed per
  app and `SignedIdentityError` maps to a fixed code/status via `local_error` before
  route transforms/upstream work.
- Existing `tests/test_gateway_identity.py` explicitly expects live LRU eviction,
  so it currently blesses the capacity vulnerability. Existing docs call this
  TTL/LRU state and retain the process-local/single-worker limitation.

These are Local production/security-contract defects. No Qwen/Gateway production
mutation or protected-model experiment is needed.

## A. Required replay invariant and API behavior

Implement a small typed production design; do not patch only the sample numbers.
For a signed integer timestamp `t` and skew `s`, the request is valid at wall time
`n` exactly while `t-s <= n <= t+s`. Once accepted, its digest must remain protected
through the inclusive upper validity boundary `t+s` regardless of whether the
request was future-dated, current, or past-dated at admission. It may be reclaimed
only when the current trusted wall time is strictly greater than every retention
horizon that applies.

Preserve the configured replay TTL as a documented minimum post-admission
retention if retained by the design, but it must never shorten the request-derived
horizon. The clean compatible formula is
`expires_at = max(admission_now + replay_ttl_seconds, signed_timestamp + clock_skew_seconds)`
with expiry only when `expires_at < current_time`; a mathematically equivalent
design is acceptable if tests prove the same invariant. Explain why TTL=skew is
still secure for a maximally future-dated request. Do not merely raise a default or
enforce2*skew without deriving the invariant. Use one finite wall-clock sample per
verification. Preserve exact inclusive timestamp semantics and handle integer
timestamps versus fractional local time explicitly.

Make clock movement fail closed for the process lifetime. In particular, a valid
new request at a forward-jumped clock may reclaim expired entries; a subsequent
wall-clock rollback must not allow an older purged signed request to authenticate.
A locked non-decreasing wall-clock high-water mark with a distinct safe503 outcome,
or a demonstrably equivalent design, is acceptable. Do not silently substitute a
different timestamp window. Process restart still clears state and remains an
explicit documented limitation; do not claim restart or cross-process durability.

Replace the ambiguous boolean reserve result with a closed typed outcome or typed
exception that distinguishes at least: RESERVED, REPLAY, CAPACITY_UNAVAILABLE,
and any clock-rollback/unavailable condition the design needs. Validate finite
clock/horizon inputs and valid digest grammar. Keep the entire check/purge/reserve
operation atomic under the existing lock.

Purge genuinely expired entries first. If the bounded store is still full, reject
the new valid signed request without removing any live digest. Existing live
digests, including the oldest, must remain replay-protected. Prefer checking an
already-stored digest before capacity so a known replay remains a replay, not a
misleading capacity error. Do not grow beyond `max_entries`, add persistence,
Redis/database infrastructure, or retain raw nonce/identity values.

Map outcomes in `verify_signed_identity` to bounded public errors:

- replay: existing409 `signed_identity_replayed`;
- capacity exhaustion: distinct503
  `signed_identity_replay_capacity_unavailable`;
- detected unsafe clock rollback/unavailability: distinct fixed safe503 code
  (choose and document one stable name).

All messages remain the existing generic signed-identity rejection; no digest,
nonce, identity, signature, sizes or internal state appears in response/log/metrics.
Invalid HMAC/signature must reach no reservation/capacity consumption. Preserve
service authentication, HMAC canonical bytes, signed headers, route binding and
all downstream identity propagation unchanged.

## B. Required deterministic CPU-only regressions

Add focused production-unit and app-boundary tests with deterministic clocks.
Tests must directly fail against the old implementation and prove:

1. Immediate replay is rejected.
2. A request signed at maximum future skew is accepted once and rejected on
   repeated checks throughout its full remaining validity interval.
3. At exact `t+s`, inclusive timestamp validation and replay protection both still
   apply; reclamation occurs only after that boundary.
4. A past-dated request cannot replay during its remaining valid interval; the
   request-derived horizon and configured minimum-retention semantics are explicit.
5. Fill the store with unexpired digests, attempt additional distinct valid
   admissions, and prove no admitted victim becomes replayable and size never
   exceeds its bound.
6. A full store returns the exact distinct safe public503 code, performs no image/
   tool/constitution/compiler/cache/upstream work, and leaks no raw values. A known
   replay in the full store remains409.
7. Strictly expired state is reclaimed and a new request can reserve normally;
   equality is not expired.
8. Concurrent reservation of the same digest admits exactly one caller. Also test
   distinct concurrent saturation if useful to prove the hard bound.
9. Invalid HMAC/signature consumes neither an entry nor capacity; a subsequent
   valid request can use the slot.
10. `GatewayIngressConfig` defaults, minimum/maximum boundaries, TTL/skew relation,
    boolean/type rejection and the chosen invariant remain valid and documented.
11. One clock sample is used, non-finite time fails safely, and a forward observation
    followed by backward wall-clock movement cannot re-enable a previously protected
    request. Test exact safe public behavior and no upstream work.

Retain and adapt all prior signed-identity canonicalization/header/route/concurrency/
secret/readiness tests. Remove or invert the test that currently expects live LRU
eviction. Do not weaken assertions or hide capacity errors as replay. If inspection
finds another directly coupled replay defect, fix and test it in006-a.

## C. Configuration, documentation and compatibility

Update current-facing docs and examples wherever they say nonce protection is
TTL/LRU or imply TTL alone defines security. At minimum inspect/update
`README.md`, `SECURITY.md`, `docs/ADAPTER-CONFIGURATION.md`,
`docs/SLAIF-GATEWAY-INTEGRATION.md`, and `config/adapter.example.toml` as actually
needed. State:

- request-derived inclusive validity horizon and configured minimum TTL semantics;
- expired-first reclamation and fail-closed503 at capacity, including availability/
  sizing implications;
- safe clock-rollback behavior;
- digest-only, bounded, process-local, single-worker state;
- restart clears replay history; no cross-process/durable claim.

Do not change identity v1 wire canonicalization or unrelated configuration.
Defaults may remain skew60/TTL60 if the request-derived horizon makes them correct;
any default/validation change requires a source-grounded migration rationale and
tests. Keep fixed public failure facts in API documentation.

After Local is correct, inspect the exact current Gateway main
`5ea38325ef3a3ebc69524b4679b795fab0c52935` read-only. Its Local server contract at
`app/slaif_gateway/modules/servers/local_coding/contract.py` currently advertises
`replay_mode="process_local_ttl_lru"`, default skew60/TTL120, and validates only
TTL>=skew. Do NOT modify the Gateway repository in this objective.

Report a source-grounded compatibility decision. If Local remains wire/runtime
compatible but Gateway's advertised mode is no longer truthful because live LRU
eviction was removed, provide a concise handoff section containing: the corrected
invariant; Local implementation SHA; exact Gateway fields/source involved; proposed
truthful replay-mode semantics; required positive/negative cases; and whether its
numeric TTL/skew validation must change. Strategy will add the final Local merge SHA
and publish the handoff to Gateway after merge. Do not block this Local security fix
for a metadata-only Gateway follow-up. If actual runtime safety/compatibility would
be broken without coordinated Gateway change, prove that directly and resolve all
safe Local work before returning to strategy.

## D. Verification and security review

CPU-only. NO Qwen API traffic, model/GPU inference, protected credential access,
port18020/18031 listener, compiler model call, real Codex E2E or Objective005 matrix.
Do not inspect or mutate Qwen service/model/weights/venv/config/logs/API keys,
Gateway files, systemd, firewall/VPN/network or any active Codex profile. Tests use
synthetic credentials/identities/nonces only; never log real or synthetic raw secret
values in OAP artifacts.

Run from a clean committed candidate:

- focused replay/config/app security tests (list exact selectors/counts);
- `uv run --frozen ruff check .`;
- `uv run --frozen ruff format --check .`;
- `uv run --frozen mypy src tests`;
- `uv run --frozen pytest -q`;
- `uv build` and inspect wheel contents/runtime bytes/license-notice/no OAP-tests;
- `python -m compileall -q src tests oap/bin`;
- `bash -n oap/bin/*.sh`;
- a privacy scan proving public responses/log assertions contain no nonce, digest,
  identity, signature, secret or raw request body;
- GitHub CI on every final implementation head; fix in-scope failures here.

Review production diff separately from OAP evidence. Explicitly reason about lock
atomicity, boundary comparison, wall-clock movement, capacity DoS/availability,
error ordering, HMAC-before-reservation, memory bound, restart/single-worker limit,
compatibility and documentation claims. Strongest reason not to merge must be
resolved, not merely listed.

## E. GitHub, immutable report and merge contract

Create only `oap/006-signed-request-replay-hardening` from exact remote main and
exactly one new PR. Use a security-accurate description without copying secrets or
unnecessary exploit payloads into public conversation. Push all implementation,
tests, docs, unchanged activated order and active pointer. Keep correcting this same
branch/PR until implementation-head tests and GitHub CI are green; never merge.

Only then publish exactly
`oap/reports/006-a-signed-request-replay-hardening.md`. It must contain the literal
implementation head SHA and `Report publication commit: SELF`; the report-only SELF
child's first parent is exactly that implementation SHA. Record exact invariant,
closed reservation outcomes/public codes, focused and broad results, production
diff, package inspection, no-Qwen/no-protected-access facts, current Gateway source
assessment/handoff facts, limitations and exact PR/check state. Distinguish
IMPLEMENTED, TESTED, SECURITY INVARIANT ACCEPTED BY CODING (not strategic), MERGED,
DEPLOYED and RELEASE-READY. Coding never claims strategic acceptance/merge.

Verify report bytes/path/parent and remote PR head, send exact response FIFO `OK`,
then stop mutation. Strategy independently reads the complete report, checks PR/
commits/diff/tests/docs/package/security/Gateway assessment and final report-head CI.
If satisfactory and fully green, strategy merges under standing routine authority,
verifies merged remote main and merged-main CI, then publishes any required exact
Gateway handoff with the Local merge SHA. No successor or human confirmation is
needed for ordinary defects. No deployment/release is authorized.

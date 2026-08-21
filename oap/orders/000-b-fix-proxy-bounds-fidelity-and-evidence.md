# OAP Work Order — 000-b

## Objective

Amend the existing objective-000 PR only. Repair the merge-blocking request
resource bound, HTTP proxy fidelity, observability, route-validation, and test
evidence gaps found by strategic review of round `000-a`. Preserve all accepted
foundation/image-policy work and republish complete evidence on the same branch
and PR.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`
- Repository URL: `https://github.com/ulfe-lmi/slaif-local-coding`
- Numeric objective: `000`
- Execution round: `000-b`
- PR mode: `AMEND_EXISTING_PR`
- Existing PR: #1, `https://github.com/ulfe-lmi/slaif-local-coding/pull/1`
- PR state at activation: OPEN, non-draft, mergeable/clean
- Base branch/SHA: `main` / `bcdb3542a74a08219496ef29a09fd13b543e954c`
- Required head branch: `oap/000-adapter-foundation`
- Current verified remote head: `821be322a9b7500e73f545fe0c87c1e25d6c2f29`
- Prior implementation SHA: `e49c54da8b3562cc9639d4a095c340ecc4042fb4`
- Prior report SELF: `821be322a9b7500e73f545fe0c87c1e25d6c2f29`, whose sole
  parent is the prior implementation SHA and whose only changed path is the
  immutable `000-a` report
- Current report-head CI: workflow `CI`, check `test`, SUCCESS
- Required action: **NO NEW PR**. Push only to the named existing branch/PR.

GitHub is authoritative. Reconcile these facts before mutation. If PR identity,
base, branch, or head differs materially, do only safe unambiguous work and
publish a truthful blocker; never create a replacement PR.

## Why round 000-a is insufficient

Strategic review independently verified the transcript chain, current green CI,
scope, and unchanged protected live fixture, but found these acceptance gaps:

1. `app.py` calls `await request.body()` before comparing its length with
   `request_body_max_bytes`. An attacker can therefore force allocation of an
   arbitrarily large body before the configured cap returns 413. The existing
   test checks the response only after a 4097-byte body is fully buffered; it
   does not prove bounded consumption.
2. The upstream request is built from `endpoint` alone, silently dropping the
   client query string. Request hop-by-hop filtering removes the literal
   `Connection` header but not headers named by its tokens. The adapter forwards
   client `Accept-Encoding`, streams raw compressed bytes, and discards upstream
   `Content-Encoding`, which can corrupt streamed responses. Relevant error
   metadata such as `Retry-After` is also not covered by fidelity tests.
3. The fake SSE test consumes a completed response through `ASGITransport` and
   only compares concatenated bytes. It does not prove that the first downstream
   chunk is delivered while the upstream stream remains open, nor demonstrate
   prompt flush/no full-response buffering.
4. Metrics record successful upstream headers but omit many local rejects and
   failures; no readiness-state metric exists even though the order requires it.
   Streaming latency is observed before the stream completes without documenting
   that semantics.
5. Duplicate routes that match the same model/endpoint are accepted at startup
   and become a runtime 422, despite the strict explicit route configuration
   contract and documentation.
6. The live suite does not itself call proxied `/health` or `/readyz`, and the
   two-image case uses identical images without asserting safe transformation
   counts. Its passing status alone is insufficient evidence for those claims.

## Bounded remediation requirements

### A. Enforce the body cap before unbounded allocation

- Consume the ASGI request body incrementally with a hard maximum; do not call a
  helper that buffers an unbounded body before enforcing the configured cap.
- Reject known oversized `Content-Length` early when safe, but do not trust it as
  the only bound. Count actual streamed bytes and stop consuming/forwarding once
  the cap is exceeded.
- Return the existing sanitized API-shaped 413 and make no upstream call.
- Add an ASGI-level multi-chunk test that proves the adapter stops at the bound
  without consuming an arbitrarily large remaining request stream. Cover exact
  limit, limit+1, misleading/missing `Content-Length`, and malformed JSON within
  the limit.

### B. Restore HTTP request/response fidelity safely

- Preserve the complete query string for every proxied endpoint without logging
  it or exposing it in metrics/errors.
- Correctly strip standard hop-by-hop headers and every header nominated by
  `Connection` tokens on both request and response paths. Continue stripping
  caller-spoofed SLAIF/internal headers and replacing caller authorization.
- Make response compression behavior internally consistent: either forward raw
  encoded bytes with the correct safe `Content-Encoding` contract or force/
  decode identity and remove encoding metadata. Never send encoded bytes without
  their encoding header or decoded bytes with a stale encoding header.
- Preserve relevant bounded response metadata needed for faithful errors and
  ordinary OpenAI compatibility, including `Retry-After`; continue excluding
  secrets, unsafe hop-by-hop state, and unbounded/internal metadata.
- Add fake-upstream tests for query preservation, dynamic `Connection` tokens,
  compressed streaming/non-streaming behavior, relevant error headers, status,
  body, tools, usage, and existing auth replacement.

### C. Prove true incremental streaming and disconnect cleanup

- Add a synchronized fake-upstream/ASGI or loopback contract test that blocks the
  upstream after its first SSE event and proves the client/downstream receives
  that event before the second event/upstream completion is released.
- Preserve exact event byte order and no full-response buffering.
- Retain and strengthen downstream-disconnect proof so upstream response/body is
  closed or cancelled promptly; avoid a test that passes merely because the
  entire response was already buffered.
- Preserve bounded read/write/connect/pool timeouts and sanitized 502/503
  behavior. No automatic replay/retry of possibly delivered requests.

### D. Complete bounded observability

- Record requests/status/latency for upstream results and local 4xx/5xx outcomes,
  with bounded configured endpoint/route/status/stream labels only.
- Add an explicit bounded readiness-state metric or equivalently observable safe
  metric required by the original order; exercise ready and not-ready states.
- For streaming, measure/document whether latency is header latency, total stream
  duration, or both. Names/help text/docs must not overclaim what is measured.
- Preserve counts for images seen/removed/rejected, upstream timeout/connection/
  disconnect, and prove raw bodies, query values, auth, image data, tool data, and
  attacker-controlled high-cardinality values never become labels/logs.

### E. Validate explicit route configuration at startup

- Reject configuration in which more than one route can match the same
  `(model, endpoint)` during settings validation/startup.
- Preserve unique route names, supported policies, loopback-only listener, and
  fail-closed request behavior. Add positive/negative validation tests and align
  documentation with actual behavior.

### F. Close live-evidence gaps

- Re-run the full bounded authenticated live matrix through a foreground
  candidate on `127.0.0.1:18031` using the existing protected credential
  mechanism without printing values.
- The live suite must explicitly assert local `/healthz`, `/readyz`, proxied
  `/health`, `/v1/models`, Responses text, forced+automatic+streaming tools,
  multi-turn tool output, SSE completion, one-image, and two-image behavior.
- Use safe distinguishable synthetic images where practical and assert the
  candidate's safe metric/count evidence shows two seen and one removed for the
  two-image request. Identity/order remains additionally proven deterministically
  by pure tests; do not rely on nondeterministic model prose.
- Keep output small and calls serial. Stop the foreground candidate afterward.
  Record exact sanitized statuses/counts/timing and any unsupported provider
  behavior honestly.

## Full regression and CI evidence

Run and report at least:

```bash
uv lock --check
uv sync --frozen --extra dev
uv run --frozen ruff check .
uv run --frozen ruff format --check .
uv run --frozen mypy src tests
uv run --frozen pytest -q
SLAIF_LIVE_TEST=1 uv run --frozen pytest -q tests/test_live.py
uv build
python3 -m compileall -q src tests oap/bin
bash -n oap/bin/*.sh
git diff --check bcdb3542a74a08219496ef29a09fd13b543e954c...HEAD
```

Update CI if needed so the fake tests proving the repaired merge blockers run on
every PR head. Inspect and repair all in-scope failures. Report every skipped,
pending, missing, or unavailable check exactly; none is a pass. The final
report-head required checks must be successful before strategic merge.

## Documentation and compatibility contract

- Correct README/configuration/operations text where round `000-a` overclaimed
  body bounds, header fidelity, route validation, readiness metrics, or latency.
- Document exact query/header/compression behavior and the hard request-body
  bound.
- Preserve accurate newest-image semantic limitation, gateway separation,
  loopback-only candidate, no retry policy, rollback, and experimental scope.
- Do not claim production readiness, generic model compatibility, or completed
  future constitution/cache/gateway work.

## Scope and non-goals

This is a focused repair of the existing objective-000 PR. Do not implement
`AGENTS.md` detection, candidate extraction, compiler, cache, constitution
injection, gateway identity/auth/quota/accounting, public TLS/listener, cutover,
model changes, image decoding/re-encoding, databases, queues, or unrelated
refactors/dependencies. Do not rewrite architecture unless an unresolvable
conflict is returned to strategy.

## Security, privacy, resources, and protected live host

- Never print, commit, report, log, metric-label, or persist secret values, raw
  prompts/source/tool output, image content, request/response bodies, customer
  data, private query values, or credentials.
- Candidate remains CPU-only and loopback-only on 18031. No model download,
  duplicate model process, GPU allocation, public binding, firewall/VPN/network
  change, or gateway change.
- Absolutely no stop/restart/change to `qwen-serving-vision.service`, inactive
  `qwen-serving.service`, PID/port 18020, launch flags, model/checkpoint/patches/
  venv, systemd units, API-key file, or active Codex profiles/catalog/session.
- The pre-existing mode-0777
  `/synology/homes/janezp/.config/qwen-serving-vision.env` risk remains out of
  scope and MUST be preserved byte-for-byte; do not remediate it in this PR.
- Strategic baseline hashes that must remain unchanged:
  - vision env: `affabb5701b67b5fcb7cab2e3ae1835e84e19dc98a7f1eb245cf3e49b76b3b5b`
  - vision user unit: `fc88870b4f4afee214c25dc9ec544c4178c300bf4d78092a4d12787a955e2e94`
  - vision start script: `8c87e0104b25c9600235a97555c4b0a1d0ea55d34ccb4094af428c8b4501f89f`
  - Qwen Codex profile: `18ead58ac440d29ce2e86addf855c24f471021c6050d4da685320a2cf6eb62eb`
  - coding Codex profile overlay: `cc243c7057f00cb15a06a5be63c6d811f8f473e367d521b1b6ea6207c794509a`
  - OAP runtime env: `22fdefd324d631353f1b9fedad3bad1fc75577073794a882ce2dd57bc5794bf1`
- Verify before/after service PID/start time/command/listeners and these hashes;
  candidate 18031 must be stopped at report time. Evidence contains only safe
  metadata/hashes, never protected file contents or key values.

## Local execution authority

Coding owns all safe repo-local dependencies, fake upstreams, synchronized ASGI/
loopback test harnesses, foreground candidate, bounded authenticated calls,
GitHub publication, and CI diagnosis. Do not recruit the human or strategic
agent for routine terminal work. Return only genuine external/authority/product/
architecture blockers.

## GitHub publication and immutable report

1. Verify and amend only PR #1 on `oap/000-adapter-foundation`; **NO NEW PR**.
2. Preserve prior activated order/report bytes. Commit this exact `000-b` order
   and updated `oap/active` unchanged with the remediation.
3. Push all non-report work and make it the current head of the same PR; inspect
   and repair in-scope CI.
4. Capture the literal 40-hex implementation head after every non-report change
   is remote.
5. Atomically publish exactly one new immutable report:

```text
oap/reports/000-b-fix-proxy-bounds-fidelity-and-evidence.md
```

6. The report must contain `Implementation head SHA: <literal 40-hex>` and
   `Report publication commit: SELF`. Its containing commit changes only that
   report, its first parent is the literal implementation SHA, it is remote PR
   head, and no later mutation/push occurs before response `OK`.
7. Report exact files/behavior, criterion-by-criterion evidence, all commands and
   counts, synchronized streaming proof, body-consumption proof, header/query/
   compression cases, metrics/readiness semantics, live sanitized matrix,
   current checks, protected before/after evidence, limitations, and explicit
   `extra PR NO`, `coding merge NO`, `protected fixture changed NO`.
8. Never edit the immutable `000-a` report or either activated order. Coding
   never merges or enables auto-merge.

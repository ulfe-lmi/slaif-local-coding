# OAP Coding-Agent Report — 005-h

## Work order

- Identifier: `005-h`
- Order path: `oap/orders/005-h-corrected-gateway-real-codex-acceptance.md`
- Numeric objective: `005`
- PR mode: `AMENDED_EXISTING_PR`

## Status

BLOCKED

## Executive summary

The exact reviewed Gateway PR #291 head passed the Codex 0.149 structural
capture, candidate-shape, route-pair, and Local Coding tool-filter checks. The
required signed-identity preflight then failed: the Gateway 0.149 normalizer
returned no usable `session_id`, `thread_id`, `turn_id`, or `root_turn_id`
hint to its Local Coding identity derivation. A signed Local Coding route would
therefore fail closed before provider work. The order requires stopping before
Docker, PostgreSQL, Gateway/adapter listeners, or the full Qwen acceptance run.
No Gateway code was changed.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`
- PR: [#7](https://github.com/ulfe-lmi/slaif-local-coding/pull/7)
- PR state: OPEN, non-draft, MERGEABLE/CLEAN; no merge or auto-merge performed
- Base/head: `main` / `oap/005-gateway-ingress-integration`
- Starting remote SHA: `cd1a16cbddc4ff7e1ad2b2769fc1311479f0dc97`
- Implementation commits pushed before report: `d2093650ef61200d3ed6ff9516bfd73eb2675182`
- Implementation head SHA: d2093650ef61200d3ed6ff9516bfd73eb2675182
- Report publication commit: SELF
- New PR this round: NO
- Amended existing PR: YES, PR #7
- Merge performed: NO

Gateway dependency was verified at the required exact PR #291 report head
`c0094e478b83d33a52eb82a2ba9c8677e6af4a6e`, with implementation parent
`02670e3275ff57850aeaa9bc8aae4ed3c8e2f124`. Its report-only commit changed
only `oap/reports/155-c-codex-0149-local-coding-preflight-deadlock-closure.md`;
the parent and changed path were independently verified. PR #291 was OPEN,
non-draft, MERGEABLE/CLEAN and all ten named checks were SUCCESS.

## Changes and files

- Committed the activated `oap/active` value `005-h` and the exact strategic
  order bytes in the implementation/transcript commit.
- Added no production code, dependency, fixture, Gateway, service, or
  deployment changes.
- The final report commit is report-only.

## Acceptance evidence

### Criterion 1 — exact-head and provenance preflight

- PASSED — Local Coding PR #7 started at the required exact head and the
  activation/order-only change advanced it to the implementation head above.
- PASSED — Gateway PR #291 matched the required exact report head and parent;
  detached checkout was clean and temporary state was removed.
- PASSED — Local signed-identity fixture digest:
  `92c09c03a40dbdf5e6e08b9e5d7f5c6e2c777e14467845d351f219cbb9a66588`.
- PASSED — Local Responses tool-filter fixture digest:
  `58ff37d43778895b198f687aa4c54cbe41953809db8af97e7357c5d791c111e6`.
- PASSED — Gateway provenance-wrapper digests matched both exact Local Coding
  source fixture digests; wrapper contracts matched the source contracts.
- PASSED — Local signed-identity and tool-policy suites: 37 tests passed.
- PASSED — Exact Gateway client/server and policy suites: 430 tests passed.

### Criterion 2 — exact Codex 0.149 and signed-route preflight

- PASSED — One fresh official Codex CLI `0.149.0` global-yolo structural
  capture ran in a private disposable home/workspace with a loopback fake
  Responses stop; no model call was performed. The exact verifier returned
  `VERIFY_LIVE_0149_OK status=structural_candidate production_path=passed`.
- PASSED — The exact Gateway module accepted `tool_search` and `web_search`
  only as adapter-managed candidates, preserved ordinary function/custom/
  namespace declarations, and the static registry selected exactly
  `codex-0.149-responses-v1 -> local-coding-v1`.
- PASSED — Gateway negative client/policy tests rejected authority-bearing,
  malformed, explicit hosted/search-choice, unrelated-pair, and missing-route
  cases before policy/provider work.
- PASSED — Local Coding removed only exact disabled search declarations while
  preserving ordinary local tools, call/results, order, and continuation
  content; explicit disabled choices fail closed.
- PASSED — Synthetic service, signing, derivation, public-key, database, and
  Qwen credential roles were kept as distinct configured roles in the reviewed
  contracts; no real credential was printed or persisted.
- FAILED — Exact normalized 0.149 synthetic envelope contained only one
  transient `x-codex-*` metadata key and zero usable session-hint keys. The
  Gateway client module's allowed metadata schema includes the standard session
  keys, but its transient extractor does not return them to
  `derive_request_identity`. Signed identity derivation is therefore not
  ready for the required real route.
- NOT RUN — Stale/unknown-version/changed-vector/missing-case/malformed-wrapper
  rejection matrix after this first signed-route blocker.

### Criterion 3 — disposable real Codex → Gateway → Local Coding → Qwen run

NOT RUN. The order gates Docker, PostgreSQL, Gateway and adapter listeners, real
Codex traffic, accounting, isolation, rollback, and all full-run requests on
Criterion 2.

## Verification

- `uv run --frozen pytest -q -rs`: PASSED — 545 passed, 8 explicit skips. The
  skips were seven opt-in live tests and one human-activated vision E2E test.
- `uv run --frozen pytest tests/test_gateway_identity.py tests/test_tool_policy.py`:
  PASSED — 37 passed.
- Exact Gateway focused client/server/policy suites: PASSED — 430 passed.
- Exact Codex 0.149 structural verifier: PASSED — one fresh capture,
  production path accepted.
- `uv run --frozen ruff check src tests`: PASSED.
- `uv run --frozen ruff format --check src tests`: PASSED — 53 files formatted.
- `uv run --frozen mypy src tests`: PASSED — 52 source files checked.
- `uv build --wheel --sdist`: PASSED — wheel and source distribution built.
- `uv run --frozen python -m compileall -q src tests`: PASSED.
- `find scripts oap/bin -type f -name '*.sh' -exec bash -n '{}' ';'`: PASSED.
- `git diff --check`: PASSED.
- Secret-pattern scan: PASSED — ten redacted matches were synthetic test
  authorization literals only; no real key marker was present.
- Raw-logging pattern scan: PASSED — zero matches.
- Local Coding PR #7 `test` check at implementation head: SUCCESS.
- Full disposable cross-repository run: NOT RUN — mandatory preflight blocker.
- Live Qwen inference, accounting, isolation, replay, rollback, and cleanup
  acceptance: NOT RUN — mandatory preflight blocker.

## Live model/service evidence

- Required constitutional live discovery was bounded to the protected vision
  service: `qwen-serving-vision.service` was active, PID `364444`, with the
  expected single model and health/models status 200 on loopback port `18020`
  `/v1`. The model identifier matched the expected `qwen3.8-27b` fixture.
- The text service was inactive, no `18021` or `18031` listener existed, and
  the vision PID/start/listener facts were unchanged after preflight.
- No Qwen inference request, candidate adapter listener, Gateway listener,
  PostgreSQL container, or Docker image setup was performed.
- Scope note: the bounded health/models discovery above occurred before the
  final synthetic identity-hint gate because the constitutional live endpoint
  discovery was required. It was not model traffic or a service mutation; the
  order's full Qwen-traffic stage remained unstarted.

## GitHub CI / required checks

- Local Coding implementation-head `test`: SUCCESS on
  `d2093650ef61200d3ed6ff9516bfd73eb2675182`.
- Gateway PR #291 exact required checks at `c0094e478b83d33a52eb82a2ba9c8677e6af4a6e`:
  Unit/lint/migration, CodeQL JavaScript/TypeScript, CodeQL Python, PostgreSQL,
  OpenAI-compatible E2E, Playwright, Docker Compose, documentation hygiene,
  and CodeQL aggregate: all SUCCESS.
- All required Local Coding checks were green at implementation-head report
  drafting: YES. Report-head checks may be pending; strategy verifies them.

## Local setup/dependencies

- Used the existing Local Coding repository `.venv` with frozen dependencies.
- Created a private detached Gateway checkout and temporary venv with declared
  dependencies solely for no-live imports/tests/capture; both were removed.
- No Docker, PostgreSQL, Gateway process, adapter listener, persistent cache,
  profile, or service state was created.

## Documentation

Not updated. No Local Coding behavior or support claim changed; this report
records the blocked exact-head acceptance evidence. Gateway documentation/code
was outside this repository and outside the order's mutation scope.

## Safety/scope confirmations

- Unrelated work: preserved; the only implementation/transcript paths were the
  unchanged activated selector and exact strategic order.
- Gateway PR #291 code, branch, report, OAP, and remote state: unchanged.
- Secrets, prompts, source, images, tool output, model text, identities,
  signatures, nonces, database URLs, and raw request/response bodies: not
  exposed or persisted.
- Protected `18020`/Qwen/Codex fixture changed: NO.
- Temporary Gateway checkout/venv: removed. Temporary containers, volumes,
  listeners, adapter port `18031`, and random ports: none created/remain.
- Extra objective PR: NO. Coding merge: NO.
- Active/order edited after activation: NO.
- Report commit report-only: YES.
- Full live acceptance and post-run rollback/cleanup proof: NOT RUN because the
  no-live signed-identity gate failed.

## Known limitations/blockers

- At exact Gateway head `c0094e478b83d33a52eb82a2ba9c8677e6af4a6e`,
  `app/slaif_gateway/modules/clients/codex_0149.py` returns only metadata keys
  prefixed `x-codex-`, while
  `app/slaif_gateway/modules/servers/local_coding/identity.py` requires one
  standard session hint. The exact signed route consequently fails closed with
  `local_coding_identity_unavailable` before provider/reservation work.
- No Gateway repair was attempted because the order explicitly prohibits
  Gateway mutation and requires the exact reviewed head.
- This round makes no real Codex/Qwen/Gateway acceptance, quota/accounting,
  isolation, rollback, production, cutover, or release claim.

## Recommended strategic follow-up

- Obtain an authorized Gateway continuation that preserves the exact reviewed
  Codex 0.149 security gates while exposing one validated standard session hint
  to the signed identity derivation, then re-reconcile both exact heads/checks
  before activating another acceptance continuation.


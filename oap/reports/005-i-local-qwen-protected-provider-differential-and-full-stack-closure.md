# OAP Coding-Agent Report — 005-i

## Work order

- Identifier: `005-i`
- Order path: `oap/orders/005-i-local-qwen-protected-provider-differential-and-full-stack-closure.md`
- Numeric objective: `005`
- PR mode: `AMENDED_EXISTING_PR`

## Status

PARTIAL

## Executive summary

The required read-only preflight passed and the one authorized Local Coding to
protected-Qwen differential was executed with one exact Local request and one
same-shape direct-provider control. Both requests were dispatched with the
identical provider-bound shape and both received `2xx` SSE with valid terminal
`response.completed` usage and normal upstream close. The first diagnostic
runner had two evidence defects: its fixed event vocabulary omitted provider
reasoning event names, and its downstream parser rejected a large ASGI chunk
before splitting its SSE lines. The runner and pure regression tests were
corrected, but the order prohibits retrying the protected diagnostic after the
ownership decision. No Local production correction was proven necessary, and
the gated full composed Codex/Gateway/Qwen acceptance was not run.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`
- PR: [#7](https://github.com/ulfe-lmi/slaif-local-coding/pull/7)
- PR state: OPEN, non-draft, MERGEABLE/CLEAN
- Base/head: `main` / `oap/005-gateway-ingress-integration`
- Starting remote SHA: `6ee2a51aa7b03d4df46e0662d88cc33fd0ef7db8`
- Implementation head SHA: `3e0eedb42dbb7d54108dc2f93732310aec550129`
- Report publication commit: SELF
- Implementation commits pushed before report: `3e0eedb42dbb7d54108dc2f93732310aec550129`
- New PR this round: NO
- Amended existing PR: YES, PR #7
- Merge performed: NO

Gateway dependency was independently verified read-only at PR #291 head
`306ecb186b5c12db991a684e7c04e5c9f174eba2`, with report-only parent
`a8a2a7a8a2e84fbe7dd42658173dd6358f709444`. It remained OPEN, non-draft,
MERGEABLE/CLEAN with all ten named checks SUCCESS. No Gateway file or remote
state was changed.

## Changes and files

- Added `scripts/local_qwen_provider_differential.py`, a bounded in-process
  production-path diagnostic using direct HTTPX transport and fixed stage
  facts only.
- Added `tests/test_local_qwen_provider_differential.py` for provider request
  shape and large-chunk/reasoning-event SSE parsing.
- Committed the activated `oap/active` selector and exact strategic order bytes
  unchanged in the implementation/transcript commit.
- No production adapter behavior, dependency, Gateway, service, deployment,
  or protected-Qwen configuration change was made.

## Acceptance evidence

### Criterion 1 — exact pinned preflight and topology

- PASSED — Local PR #7 started at the required `005-h` report head and the
  exact active selector is `005-i`.
- PASSED — Gateway PR #291 matched exact head
  `306ecb186b5c12db991a684e7c04e5c9f174eba2`; its report-only parent and
  changed path were verified.
- PASSED — Protected `qwen-serving-vision.service` was active/running with
  PID `599296`, restart count `0`, one authenticated model identifier
  `qwen3.8-27b`, context limit `100000`, single sequence, and image limit `1`.
- PASSED — Protected health and authenticated model visibility returned HTTP
  200 before and after the diagnostic. Text service remained inactive; private
  protected listener `18020` remained present; `18021` and `18031` remained
  free.
- PASSED — No Docker, PostgreSQL, Gateway listener, adapter listener, or
  second model process was started.

### Criterion 2 — Local/provider differential

- PASSED — The captured Local outbound request had method/path classes
  `POST`/`v1_responses`, model match true, `stream=true`, top-level fields
  `input`, `max_output_tokens`, `model`, `stream`, one input item with one
  content item, zero tools, zero images, integer output-limit class, absent
  reasoning-limit class, and body length `169` bytes.
- PASSED — The direct control used the same request bytes and the same bounded
  transport timeout classes; body equality was true.
- PASSED — Local outbound stages A–H: `PASSED`, `PASSED`, `PASSED`, `PASSED`,
  `PASSED`, `FAILED`, `PASSED`, `PASSED`. The provider response was `2xx` SSE,
  first bytes arrived, SSE framing parsed, `response.created` appeared,
  terminal usage was valid, and upstream close was normal.
- PASSED — Direct-control stages A–H: `PASSED`, `PASSED`, `PASSED`, `PASSED`,
  `PASSED`, `FAILED`, `PASSED`, `PASSED`. The direct provider response was
  `2xx` SSE with valid terminal usage and normal close, so the exact Qwen
  request contract was accepted by the provider.
- PARTIAL — Initial stage F was reported false because the runner did not yet
  include the provider's `response.reasoning_part.added`,
  `response.reasoning_part.done`, `response.reasoning_text.delta`, and
  `response.reasoning_text.done` vocabulary. These names are in the pinned
  Gateway Codex stream contract and are covered by the corrected pure test.
- PARTIAL — Initial Local stage I was reported false because the ASGI test
  transport delivered a large downstream chunk and the runner checked chunk
  size before splitting complete SSE lines. The Local source still yielded
  upstream raw chunks directly; the captured downstream byte count was
  `276569`, but stage-I equality was not accepted from the defective runner.
- NOT RUN — Single-field output-bound variant; the exact request already had
  the observed integer output bound and no additional discriminator was
  justified.
- NOT RUN — Any further protected Local diagnostic; explicitly prohibited by
  the order after the ownership decision.
- NOT PROVEN — Local request construction, Local transport, Local SSE
  forwarding, or protected-Qwen ownership. The two calls show provider
  availability and valid terminal streams, while the first Local evidence
  runner defect prevents a fresh stage-I acceptance.

### Criterion 3 — full composed Codex acceptance

NOT RUN. The order gates the single disposable real Codex 0.149.0 → exact
Gateway PR #291 → Local Coding → protected Qwen run on a green direct Local
boundary. The only boundary diagnostic completed before the parser correction;
the prohibited retry was not performed. Therefore no claim is made for model
visibility through Gateway, Codex tools, governance acquisition/injection,
cache/rehydration reuse, isolation, replay/tamper rejection, quotas,
accounting, rollback, or composed cleanup.

## Verification

- `uv run --frozen pytest -q -rs`: PASSED — 547 passed, 8 explicit skips
  (seven opt-in live tests and one human-activated protected vision fixture).
- `uv run --frozen pytest -q tests/test_local_qwen_provider_differential.py tests/test_app.py tests/test_gateway_provider_driver.py tests/test_tool_policy.py tests/test_rehydration.py tests/test_vision_e2e.py -rs`: PASSED — 199 passed, 1 explicit skip.
- `uv run --frozen ruff check src tests scripts`: PASSED.
- `uv run --frozen ruff format --check src tests scripts`: PASSED — 58 files.
- `uv run --frozen mypy src tests`: PASSED — 53 source files.
- `uv build --wheel --sdist`: PASSED.
- `uv run --frozen python -m compileall -q src tests scripts`: PASSED.
- `find scripts oap/bin -type f -name '*.sh' -exec bash -n '{}' ';'`: PASSED.
- `git diff --check`: PASSED.
- Secret-pattern scan: PASSED — zero file hits.
- Raw-logging pattern scan: PASSED — zero source file hits.
- Wheel package-boundary scan: PASSED — zero `scripts/`, `tests/`, or `oap/`
  paths in the wheel. The source distribution intentionally contains the
  repository's support files.
- `uv run --frozen ruff check scripts/local_qwen_provider_differential.py` and
  script compilation before protected traffic: PASSED.
- Protected differential invocation: PARTIAL — exactly one Local call and one
  direct control; no retry. Fixed facts are recorded above; no raw payload was
  retained in the repository or report.
- Local Coding PR #7 `test` check at implementation head: SUCCESS (CI run
  `33278887799`).
- Full disposable composed acceptance: NOT RUN — boundary evidence gate.

## Live model/service evidence

- Protected vision service `qwen-serving-vision.service`: active/running,
  PID `599296`, restart count `0`, model-count class `1`, authenticated health
  and model visibility HTTP 200, context class `100000`, sequence class `1`,
  image-limit class `1`.
- Local/provider diagnostic route class: `qwen38-vision-codex`; provider
  request path class: `v1_responses`; both authorized calls returned `2xx` SSE
  with terminal usage and normal close.
- Protected PID/start/listener facts were unchanged after the diagnostic.
- No protected service, model, launch flag, credential source, network binding,
  active Codex profile, or text service was changed.

## GitHub CI / required checks

- Local implementation-head `test`: SUCCESS at
  `3e0eedb42dbb7d54108dc2f93732310aec550129`.
- Gateway PR #291 at exact head `306ecb186b5c12db991a684e7c04e5c9f174eba2`:
  Unit/lint/migration head, CodeQL JavaScript/TypeScript, CodeQL Python,
  PostgreSQL integration tests, OpenAI-compatible E2E tests, Playwright
  browser smoke, Docker Compose smoke, Documentation hygiene, and CodeQL
  aggregate: all SUCCESS.
- All required checks were green while drafting this report: YES.
- Report-head checks may be pending; strategy verifies them independently.

## Local setup/dependencies

- Used the existing frozen repository environment for tests, typing, build, and
  compile checks.
- The diagnostic used only a temporary in-process cache root and direct HTTPX
  transport; temporary state was removed on exit.
- No Gateway checkout, database, container, persistent service, or adapter
  listener was created by this round.

## Documentation

Not updated. No production behavior or deployment contract changed; the new
repository-only diagnostic and its pure tests are self-contained. The order's
full-pass documentation updates were not applicable because composed acceptance
was not run.

## Safety/scope confirmations

- Unrelated work: none observed; only the four intended implementation/
  transcript paths were committed.
- Secrets, prompts, source, images, tool output, model text, identities,
  signatures, nonces, private URLs, credentials, and raw request/response
  bodies were not committed or reported.
- Protected `18020`/Qwen/Codex fixture changed: NO.
- Extra objective PR: NO. Coding merge: NO.
- Active/order edited after activation: NO; exact activated bytes were committed
  unchanged.
- Report commit report-only: YES.
- Full composed acceptance, replay/isolation/accounting/rollback evidence:
  NOT RUN.

## Known limitations/blockers

- The authorized Local diagnostic result cannot be accepted as a green A–I
  boundary because the first run exposed a runner parser/allowlist defect and
  the order forbids retrying that protected request after ownership decision.
- The direct control demonstrates that the protected provider accepted the exact
  request and produced a valid terminal stream; it does not prove the complete
  composed Gateway/Codex path.
- No production Local correction was made or proven necessary. No provider,
  Gateway, production, certification, generic-model, multi-worker, or release
  readiness claim follows.

## Recommended strategic follow-up

- Review this partial handoff and, if still required, issue a continuation that
  authorizes a fresh run of the corrected diagnostic before any full composed
  acceptance. Preserve the direct-Qwen rollback path and re-reconcile both
  exact PR heads/checks first.

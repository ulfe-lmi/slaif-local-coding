# OAP Coding-Agent Report — 005-aq

## Work order

- Identifier: `005-aq`
- Order: `oap/orders/005-aq-offline-provider-replay-repair.md`
- Numeric objective: 005 engineering repair
- PR mode: `AMENDED_EXISTING_PR`
- Existing PR: 7 (`oap/005-gateway-ingress-integration`)

## Status

FAILED

## Executive summary

The offline diagnosis identified and repaired the demonstrated harness owner:
the companion continuation had discarded the original user history. The exact
repository companion now retains that history, preserves the validated returned
function-call fields, and omits only the optional item ID. The repeatable
differential uses the exact companion tools and Local route tool policy before
the installed vLLM preparation path.

The installed vLLM 0.27.1 `ResponsesRequest`, input/tool construction,
`OnlineRenderer.preprocess_chat`, and pinned Qwen template were exercised with
synthetic metadata only. The omitted-history case failed at the fixed Qwen
template no-user-query predicate; the corrected request passed the same path.
This was not a provider argument-normalization defect. No protected request or
credential was used to decide the diagnosis.

The existing acceptance transport now captures bounded same-response HTTP
error facts before Local sanitization on the HTTP >=400 early-close path. It
retains only finite field/type/code/param classes and exact safe byte counts,
including source-known `invalid_request_error`; it does not retain raw bodies
or messages.

The one authorized protected identity attempt failed on its first Qwen
response at the existing Gateway SSE validator. Per the order, no continuation,
retry, repair, or additional protected inference was made.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`
- PR: [7](https://github.com/ulfe-lmi/slaif-local-coding/pull/7), open
- Base/head: `main` / `oap/005-gateway-ingress-integration`
- Starting remote SHA: `8a6e6551c0effc46e1eac135be9bd2ccf1e9b62a`
- Implementation head SHA: a94c6419f944da752e353ded1215aa1ca82ccfed
- Report publication commit: SELF
- Implementation commit pushed before report: `a94c6419f944da752e353ded1215aa1ca82ccfed`
- New PR this round: no
- Amended existing PR: yes
- Merge performed: NO
- Implementation-head CI: `test`, run `34715124601`, job `103610888166`, SUCCESS

## Changes and files

- `scripts/gateway_accounting_rehearsal.py`: retained original companion
  history; added source-bound AP37 harness-only reuse; ordered offline,
  classifier, and current fake-target gates before protected credential
  resolution; preserved the exact target selector and unique dispatch budget.
- `scripts/qwen_offline_replay_differential.py`: added the CPU-only,
  metadata-only installed-provider differential using exact repository helper
  construction, Local tool policy, synthetic validated return items, full
  request options, and original input history.
- `tests/helpers/transport_observer.py`: added bounded same-response provider
  error classification and early-close capture in the existing acceptance
  transport, plus a bounded classifier qualification path.
- `tests/test_transport_observer.py`, `tests/test_app.py`,
  `tests/test_gateway_accounting_rehearsal.py`: focused classifier, cleanup,
  accounting, privacy, companion, and source-reuse coverage.
- Activated `oap/active` bytes and the exact activated order were committed
  unchanged. Pre-existing unrelated empty `Local`, `clean`, and `unchanged`
  files were preserved and not staged.

## Acceptance evidence

### Offline cause and corrected preparation

- Result: PASSED, CPU metadata-only, protected requests `0`, credential
  resolution `false`.
- Installed source pins matched:
  - vLLM `protocol.py`:
    `6aeabf69dbc924b238172b505730a8a8321b50a819891d2a72a690963c970fba`
  - vLLM `utils.py`:
    `577100edd0951f7f2936d2b37b7b4ec9a03d85088b35e49de6c0e9633a59adc2`
  - vLLM `serving.py`:
    `628429902ff26b87f86eae1a45297f647f3712d7b421ca9a4866a3fd0f046a5b`
  - Qwen template:
    `c3cf9e34abf4f9e36c2d72165aa9c132d3e2a725b6c2586aaa3a8af9d7a81041`
  - installed `chat_utils.py`:
    `150f40b0a0ba87548b0feb86f002fea7d246f5a4d5f7bc2cecd3c3824098c851`
- The exact fixed template predicate was present at lines 89–100. The
  omitted-user control parsed but failed as `template_no_user_query`; the
  corrected original-history request, empty-string/object arguments,
  omitted/null/legal namespace controls, omitted/completed status controls,
  and nonzero schema control all prepared successfully.
- Exact zero-argument schema remained object/properties `{}` /
  `additionalProperties=false` with no required fields.

### Harness qualification and reuse

- Current offline differential: PASSED.
- Current classifier qualification: PASSED for normal error close,
  cancellation, and streamed oversize accounting/close; malformed/deep JSON
  is contained as a finite malformed class.
- Current fake identity target: PASSED with exactly 2 fake inference
  dispatches, 0 compiler dispatches, valid ID-less continuation, terminal
  accounting, cleanup, and privacy.
- Prior accepted AP37 evidence was reused only for implementation
  `934388057af267b3bf39b2a2d1b56d34dfbd042f`, exact production/Gateway/Codex
  identity, exact prior source identity, descendant proof, and an explicit
  harness-only changed-path allowlist. Full fake37 was not rerun.

### Protected attempt

- Eligibility gates passed before protected credential resolution, including
  exact Gateway helper/profile binding, offline corrected preparation,
  classifier qualification, and current fake identity qualification.
- Protected readiness: bounded `/health` and `/v1/models` probes succeeded;
  these were readiness checks, not diagnostic inference.
- Unique protected target dispatch: 1 inference request, the initial request;
  0 continuation requests, 0 compiler requests, 0 retries. Lifetime aggregate
  counters are not used as unique dispatch evidence.
- Initial protected HTTP status: `200`. The stream failed at the existing
  Gateway validator with fixed `stream_validation_invalid`, validation stage
  `gateway_validator`, failed event class `response.completed`. The first
  response was not an HTTP >=400 provider envelope, so no provider error
  envelope facts were claimed for it. Raw event/body content was not retained.
- The failed first response prevented continuation dispatch. No further
  protected traffic was sent.

## Verification

- `uv run pytest -q`: PASSED — 857 passed, 16 skipped.
- `uv run pytest -q tests/test_transport_observer.py tests/test_app.py tests/test_gateway_accounting_rehearsal.py`: PASSED — 237 passed.
- `uv run ruff check ...`: PASSED.
- `uv run ruff format --check ...`: PASSED.
- `uv run mypy src tests`: PASSED — 58 source files.
- `/synology/homes/janezp/qwen-serving/venv/bin/python scripts/qwen_offline_replay_differential.py`: PASSED — exact installed preparation, no protected requests.
- Current fake identity-target rehearsal: PASSED — 2 fake inference, 0 compiler.
- Protected identity-target rehearsal: FAILED at first response validator; no retry.
- Required full fake37 requalification: NOT RUN — authorized AP37 evidence
  reused because this round’s production source remained unchanged and the
  changes were harness-only.
- Real Codex ordinary/vision/full matrix: NOT RUN — outside this targeted
  failed round after the first protected response.

## Live model/service evidence

- Vision service: `qwen-serving-vision.service` remained active/running,
  MainPID `23961`, start `Sun 2026-09-06 18:57:26 CEST`, `NRestarts=0`.
- Text unit `qwen-serving.service`: correctly inactive, MainPID `0`.
- Qwen listener: protected `0.0.0.0:18020` remained present under PID 23961;
  18021 and development 18031 were absent after cleanup.
- No Qwen model, vLLM, unit, launch argument, network, firewall, profile,
  credential, Gateway production checkout, or protected-host state was changed.
- Gateway executable/main: `5ea38325ef3a3ebc69524b4679b795fab0c52935`;
  app tree: `a7b64d35650b61fbba3558ddb519c6e52a627ec9`.
- Codex fixture: version `0.149.0`, binary digest
  `bbc3341e44c9ead340ed9570c17be936e37870f570751a941699ffd04d672827`.
- Runtime cleanup, privacy scan, accounting finalization, and protected-host
  preservation predicates passed.

## Prior composition and disposition

- Prior Local real-E2E composition remains the immutable checkpoint
  `713492fa146372be13073c10a98d8f045e71900a`, parent
  `556ca152a589747b5c9adeca3d44de56e61ce08c`, tested Local
  `8245f1c0270e0a314058f2afa77c9f6e80ace483`.
- Implemented: YES.
- Tested: YES for listed offline, fake, classifier, and focused scopes.
- REAL-E2E ACCEPTED BY COMPOSITION: NO for this failed target.
- CUTOVER ACCEPTED: NO.
- MERGED: NO.
- RELEASE-READY: NO.
- Coding selected no successor, did not merge, and sent no retry.

# OAP Work Order — 000-c

## Objective

Amend existing objective-000 PR #1 only. Close the final strategic-review
resource/failure-law gap by bounding JSON structural nesting before recursive
parsing/transformation can raise an internal exception. Deep or adversarial JSON
must fail deterministically with a sanitized API-shaped 4xx, no upstream call,
no raw-data leakage, and bounded metrics, while ordinary Responses/Chat/image/
tool request shapes remain compatible.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`
- Numeric objective / round: `000` / `000-c`
- PR mode: `AMEND_EXISTING_PR`
- Existing PR: #1, `https://github.com/ulfe-lmi/slaif-local-coding/pull/1`
- Required base: `main` at
  `bcdb3542a74a08219496ef29a09fd13b543e954c`
- Required head branch: `oap/000-adapter-foundation`
- Current verified remote head: `99f2c651de7b6b9ae83eb7fbc1e8584175eed2b1`
- Prior `000-b` implementation SHA:
  `cd17aaa919caea0e59e65536a3e754aa1df3f01a`
- Prior `000-b` report SELF:
  `99f2c651de7b6b9ae83eb7fbc1e8584175eed2b1`; its only changed path is the
  immutable `000-b` report and its sole parent is the literal implementation SHA
- PR state at activation: OPEN, non-draft, base/head correct, mergeable/clean;
  current report-head workflow `CI` / check `test` SUCCESS
- Required action: amend this same branch/PR. **NO NEW PR.**

Reconcile live GitHub before mutation. A material identity/base/head conflict is
a truthful blocker, never authority to create a replacement PR.

## Independently reproduced merge blocker

Strategic review ran a read-only in-process diagnostic against the current PR
code with the existing fake upstream and a 1,000,000-byte request cap. Each body
was a small JSON object with `model=qwen` and nested-list `input`:

```text
depth 200 -> HTTP 200
depth 400 -> HTTP 200
depth 600 -> uncaught RecursionError
depth 900 -> uncaught RecursionError
depth 1100 -> uncaught RecursionError
```

The depth-600 body is only about 1.2 KiB, so the byte cap does not mitigate it.
The exception can arise in recursive JSON/image traversal/deep-copy paths and
escapes the explicit local-error path. Architecture requires malformed transform
JSON to return an explicit 4xx and resource work to remain bounded; an internal
exception/500 is not acceptable.

## Requirements

### A. Deterministic structural bound

- Define and validate a conservative finite maximum JSON nesting depth suitable
  for ordinary Codex Responses/Chat/tool/image envelopes. Make the bound part of
  the explicit server configuration contract, or a clearly documented typed
  constant if there is a compelling reason not to expose it.
- Enforce the limit before any recursive operation can exhaust Python recursion,
  including JSON decode, image counting, copy/transformation, and final-count
  verification. Do not rely solely on catching `RecursionError` after arbitrary
  recursive work.
- Prefer iterative/token-aware structural validation or another approach whose
  own stack/memory is bounded by the already-bounded body and explicit depth.
  Correctly handle brackets/braces inside JSON strings and escapes; naive byte
  counting is insufficient.
- Preserve the hard byte cap from `000-b`. Depth and byte limits are independent.

### B. Fail-closed request behavior

- Over-depth, parser recursion, and transformation structural-limit failures
  return a stable sanitized API-shaped 400/422 before upstream contact.
- Catch residual parser/transformation recursion/depth exceptions at the narrow
  request boundary so none escapes as an internal traceback/500. Do not catch
  broad unrelated programming errors or silently bypass the image policy.
- Record the result through existing bounded local request metrics using only
  configured/fixed labels. Never log or expose raw body, nesting content, query,
  auth, tool/image values, or a high-cardinality exception string.
- Preserve malformed UTF-8/JSON, ambiguous image, unknown route, body-size,
  auth, timeout, and upstream error behavior from prior rounds.

### C. Exact tests

Add CI-running tests that prove:

1. a normal representative Responses request and Chat request with nested tool/
   image content below the limit still pass and preserve prior semantics;
2. exact configured depth passes and depth+1 returns the documented 4xx with
   zero upstream calls;
3. the strategic depth-600 reproducer returns the same sanitized 4xx, never an
   exception/500;
4. nested arrays/objects, mixed nesting, empty structures, and brackets/braces/
   escaped quotes inside strings are measured correctly;
5. over-depth supported image markers and deep non-image input cannot bypass or
   crash image counting/transformation;
6. raw sentinel content and exception text do not enter logs, metrics, or error
   bodies; the bounded status metric is present;
7. prior byte-bound, query/header/compression, synchronized SSE, disconnect,
   route-validation, metrics/readiness, image, tool, error, and packaging tests
   remain green.

Tests must not globally lower Python's recursion limit or depend on interpreter-
specific crash depth as the product contract. The application limit is explicit
and deterministic.

### D. Documentation and configuration

- Update example configuration, README, and adapter contract with the exact
  nesting-limit behavior, status/code, interaction with the byte cap, and no-
  upstream guarantee.
- Remove or correct any statement that implies body bytes alone bound JSON
  transformation resource use.
- Preserve accurate experimental/loopback status, newest-image limitation,
  header/query/compression behavior, no retries, gateway separation, rollback,
  and future-objective non-claims.

## Verification and cumulative evidence

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

The current PR-head CI must include the new structural-bound tests and finish
successfully. Skipped/pending/missing/unavailable is not pass. Re-run the bounded
authenticated live suite through foreground 127.0.0.1:18031 to prove no ordinary
provider regression; stop the candidate afterward and report sanitized results.

## Bounded scope and non-goals

Change only the request structural-bound/error path, its typed configuration,
tests, necessary docs, OAP transcript, and directly required small refactors.
Do not implement constitution detection/compiler/cache/injection, gateway work,
public auth/TLS, cutover, service deployment, model/image processing, unrelated
dependencies/refactors, or protected-file permission remediation.

## Security, privacy, resources, and protected live host

- No secret/raw prompt/source/tool output/image/request/response body/customer
  data/private query/credential may enter Git, report, logs, metrics, errors, or
  command output.
- Candidate remains CPU-only and loopback-only on port 18031. No model download,
  duplicate model process, GPU allocation, public bind, firewall/VPN/network,
  gateway, API-key, service, or active Codex-profile mutation.
- Do not stop/restart/change `qwen-serving-vision.service`, inactive
  `qwen-serving.service`, PID/port 18020, Qwen checkout/venv/model/checkpoint/
  patches/launch flags, user/system units, key file, or Codex config/catalog.
- Preserve the known mode-0777 vision environment file byte-for-byte; its
  remediation remains separate human/strategic authority.
- Required unchanged strategic hashes:
  - vision env `affabb5701b67b5fcb7cab2e3ae1835e84e19dc98a7f1eb245cf3e49b76b3b5b`
  - vision unit `fc88870b4f4afee214c25dc9ec544c4178c300bf4d78092a4d12787a955e2e94`
  - vision start script `8c87e0104b25c9600235a97555c4b0a1d0ea55d34ccb4094af428c8b4501f89f`
  - Qwen profile `18ead58ac440d29ce2e86addf855c24f471021c6050d4da685320a2cf6eb62eb`
  - coding profile overlay `cc243c7057f00cb15a06a5be63c6d811f8f473e367d521b1b6ea6207c794509a`
  - OAP runtime env `22fdefd324d631353f1b9fedad3bad1fc75577073794a882ce2dd57bc5794bf1`
- Verify before/after PID/start time/command/listeners and hashes. At report time
  only protected 18020 listens; 18021/18031 are free.

## Local authority

Coding owns safe repo-local setup, deterministic parser/depth tests, fake
upstream, foreground candidate, bounded authenticated calls, commits/push, and
CI diagnosis. Do not recruit the human or strategic agent for routine execution.

## Same-PR publication and report contract

1. Amend only PR #1 on `oap/000-adapter-foundation`; **NO NEW PR**, no merge,
   no auto-merge.
2. Preserve every prior order/report byte. Commit this exact `000-c` order and
   updated `oap/active` unchanged with the remediation.
3. Push all non-report work, inspect/fix same-PR CI, and capture the final literal
   implementation SHA after every non-report change is remote.
4. Atomically publish exactly one immutable report:

```text
oap/reports/000-c-bound-json-structure-and-fail-closed.md
```

5. Report `Implementation head SHA: <literal 40-hex>` and
   `Report publication commit: SELF`; the containing remote head commit changes
   only that report and its first parent is the literal implementation SHA.
6. Include exact depth contract/algorithm, criterion evidence, status/code/no-
   upstream proof, strategic reproducer result, full commands/counts, live
   sanitized matrix, current checks, protected before/after hashes/state,
   limitations, and explicit `extra PR NO`, `coding merge NO`, `protected change
   NO`. Make no later mutation/push before response `OK`.

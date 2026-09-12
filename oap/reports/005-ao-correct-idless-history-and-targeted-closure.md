# OAP Report 005-ao — corrected ID-less history and targeted closure

Status: BLOCKED

This report is the single immutable report for activated order `005-ao`. The
sole authorized protected target attempt stopped at its first failed inference
request. No protected retry, second pair, full protected matrix, new suffix,
merge, cutover, or release action occurred.

Implementation head SHA: ea0aad3dd52acb2b951d330b30e0bff4d6e459cd
Report publication commit: SELF

## Authority and GitHub

- Order: `005-ao-correct-idless-history-and-targeted-closure.md`.
- Activated `oap/active`: `005-ao`; activated order and active bytes were not
  edited.
- PR mode: `AMEND_EXISTING_PR`.
- Repository: `ulfe-lmi/slaif-local-coding`.
- PR: [#7](https://github.com/ulfe-lmi/slaif-local-coding/pull/7),
  `oap/005-gateway-ingress-integration` -> `main`.
- Required starting local/remote head: `713492fa146372be13073c10a98d8f045e71900a`.
- Final implementation head before this report: `ea0aad3dd52acb2b951d330b30e0bff4d6e459cd`.
- Remote branch was verified at that SHA before report publication.
- PR was open, non-draft, and mergeable. CI run
  `34694167614` / job `103554653942` passed all workflow steps at the final
  implementation head. PR remains unmerged.

Implementation commits in this round, in order:

- `8faed56aee1c1e11faa6d92369832491e04efbf8` — correct identity replay
  history and target gate.
- `8f8e3b9f8261bc0156a92cc12267a9f7bdca631b` — harden disposable database
  cleanup.
- `04cf2d8224809b041cdf89c79dda181bdc931716` — preserve natural Codex replay
  history shape.
- `a28e699d2285c00ace4c9045811a1bcfe95b9bed` — retain only legal replay item
  fields.
- `9a5977a06d0ff321f2d1f39bb77d8e90857b3a0c` — align companion with Gateway
  stream gate.
- `79aa81ab5353a235c0d14a1efb875eb4d99fed3b` — keep identity target free of
  full rehearsal.
- `00fb65f81a0a17b35a9a013be33b161cba9e1c72` — retain target privacy scan
  result.
- `c8eaab3ad7fc02a8218fee55430e18e19e498136` — scan target logs before
  temporary teardown.
- `ea2f95889cc785a7d8a695191bf470d4457bda93` — document streamed continuation
  shape.
- `b84d8cc897f73d18437823e086e14447b9d710b2` — document blocked target
  closure.
- `ea0aad3dd52acb2b951d330b30e0bff4d6e459cd` — satisfy CI typing contract.

The last commit is a type-only CI repair made after the protected stop. It did
not authorize or trigger any protected rerun. The fake and protected runtime
evidence below is source-bound to `ea2f95889cc785a7d8a695191bf470d4457bda93`,
which is the implementation head used for both qualification and the one live
attempt; the final head adds only documentation and typing corrections after
that evidence.

## Implemented

- The composed companion carries the actual validated completed `function_call`
  input followed by its matching `function_call_output`, omitting only the
  optional function-call item `id`.
- The actual returned function name, arguments, namespace, status, and
  mandatory `call_id` are retained transiently for the paired request; raw
  values are not placed in safe facts, reports, JSON evidence, logs, or
  persistent artifacts.
- The fake provider no longer self-registers replay authority from an output;
  orphan history is rejected after an initial seed and in fresh state. Focused
  negative coverage includes mismatch/order/session/ownership cases.
- The identity target selector uses existing setup, observer, budget,
  accounting, and cleanup helpers only. It excludes ordinary Codex, vision,
  other identity operations, and the full protected matrix.
- Target accounting requires actual reservation and ledger terminal/count
  consistency in addition to zero pending and zero duplicate request IDs.
- Current-facing README, security/testing, integration docs, and PR description
  record the corrected streamed companion and the truthful blocked result.

## Qualification and protected execution

Exact fixture pins were mechanically reused without version or service changes:

- Gateway merged-main: `5ea38325ef3a3ebc69524b4679b795fab0c52935`.
- Gateway accepted production: `732e3bad17d93909f210321b97bedd8e5718fb7b`.
- Gateway app tree: `a7b64d35650b61fbba3558ddb519c6e52a627ec9`.
- Codex client module: `codex-0.149-responses-v1`, version `4`.
- Codex 0.149.0 binary SHA-256:
  `bbc3341e44c9ead340ed9570c17be936e37870f570751a941699ffd04d672827`.
- Pinned vLLM utility source SHA-256:
  `577100edd0951f7f2936d2b37b7b4ec9a03d85088b35e49de6c0e9633a59adc2`.
- Route policy: `qwen38-vision-codex/retain_newest/signed_identity_v1`.

Fake qualification at `ea2f95889cc785a7d8a695191bf470d4457bda93`:

- `PASSED`: exact full fake machine gate `37/37`; missing obligations `[]`,
  first failure `null`, and retry count `0`.
- `PASSED`: fake direct dispatches — 6 compiler, 12 inference, 8 other;
  terminal accounting, cleanup, fake-provider agreement, and retained boolean
  `logs_secret_free=true` were green.
- `PASSED`: focused correction suite, `106 passed`.
- `PASSED`: model-free `identity_replay` target qualification — 2 inference
  dispatches, 0 compiler dispatches, 0 unrelated target dispatches, no ordinary
  Codex, no vision, no other identity operation, and no full protected matrix.
- `PASSED`: target fake accounting — reservation delta 2 and ledger delta 2;
  finalized reservations 2 and finalized ledgers 2; failed ledgers 0; both
  reservation and ledger count consistency and terminality true; two terminal
  reservations true; zero pending and zero duplicate request IDs true.

Exactly one protected target attempt followed those gates. Protected health and
models preflight each returned HTTP 200. The target failed on the initial
stream at identity replay ordinal 5 with the bounded first-failure facts:

- `target_first_failure=initial_stream_contract_failed`.
- Direct validation class: `stream_validation_invalid`, stage
  `gateway_validator`.
- Initial response status class `2xx`, streamed response, first bytes and
  normal close observed, but `sse_valid=false` and terminal validity false.
- One inference request was dispatched/attempted/responded/completed; zero
  compiler dispatches and zero continuation requests occurred.
- `idless_composed_companion.passed=false`; no returned call ID or matching
  continuation was established, and no continuation was sent.
- Target accounting was nonterminal as expected from the first-request stop:
  reservation delta 1 with finalized reservation delta 1 but
  `reservation_count_consistent=false` and `reservation_terminal=false`; ledger
  delta 1 with finalized ledger delta 0, `ledger_count_consistent=false`, and
  `ledger_terminal=false`; zero pending and zero duplicate request IDs were
  true. No ledger finality was inferred from zero pending.
- `target_gate.passed=false`; no later dispatch was attempted. This is the
  authoritative protected failure and the round is `BLOCKED`.

The pre-existing protected host was discovered read-only and preserved. The
recorded fixture facts were active/running Qwen vision service
`qwen-serving-vision.service`, MainPID `23961`, UID `1029`, start
`2026-09-06 18:57:26 CEST`, zero restarts, port `18020` owned by that process,
ports `18021` and `18031` absent, and seven pre-existing Qwen changed paths.
The target result independently retained all protected-unchanged facts as true:
`pid`, `start`, `listener`, `worktree_count`, `text_inactive`, `no_18021`, and
`no_18031`. No Qwen/vLLM/model/GPU/port/network/firewall/VPN/credential/profile
or persistent service state was changed. No pre-existing image proxy was
assumed or modified.

Owned temporary candidate, Gateway, PostgreSQL, cache, and Codex-home runtime
cleanup passed (`processes`, `listeners`, `database`, `cache`, `codex_home` and
failure cleanup facts all true). Runtime privacy projection passed with
`logs_secret_free=true`; no raw bodies, prompts, images, tool output,
credentials, bearer values, returned names/arguments/IDs, or signatures were
published.

## Verification

- `PASSED`: `uv sync --frozen --extra dev`.
- `PASSED`: `uv run --frozen ruff check .`.
- `PASSED`: `uv run --frozen ruff format --check .`.
- `PASSED`: `uv run --frozen mypy src tests` — 58 source files.
- `PASSED`: focused tests — 106 passed.
- `PASSED`: full repository tests — 830 passed, 16 skipped. Skips are not
  counted as passes.
- `PASSED`: `uv run --frozen python -m compileall -q src tests oap/bin`.
- `PASSED`: `bash -n oap/bin/*.sh`.
- `PASSED`: supported `uv build` produced the source distribution and wheel.
- `FAILED` (tool invocation only): `uv build --frozen`; installed uv 0.12.5
  rejects `--frozen` for `uv build`. The supported build command passed and the
  GitHub workflow's `uv build` step passed.
- `PASSED`: `git diff --check`.
- `PASSED`: bounded production raw-body/credential logging scan found no
  matching production logging patterns; fake and protected runtime scans also
  retained `logs_secret_free=true`.
- `PASSED`: GitHub CI run `34694167614`, job `103554653942`, including mypy,
  pytest, build, compileall, and shell syntax steps.

## Prior checkpoint composition and limitations

The order authorizes reuse of, but this blocked round does not replay, the
human-accepted prior ordinary Codex/tool and vision checkpoints from 005-an:

- tested 005-an implementation:
  `8245f1c0270e0a314058f2afa77c9f6e80ace483`;
- immutable 005-an report:
  `923270d5f776256c12855b50ba1c0978d6458c4d`;
- 005-an report parent:
  `2c8fa51840a9ef035b52f8467a45b2faf628a7ae`.

Because the sole fresh protected identity request failed before the companion
closed, no composed real-E2E acceptance is claimed. The existing ordered
005-an missing/NOT RUN history remains unchanged. No speculative diagnosis,
new diagnostic subsystem, protected retry, or next order was selected.

IMPLEMENTED: YES
TESTED: PARTIAL — all scoped local/fake/static/CI checks passed; protected
target blocked at the first request.
REAL-E2E ACCEPTED BY COMPOSITION: NO
CUTOVER ACCEPTED: NOT RUN
MERGED: NO
RELEASE-READY: NOT RUN

Unrelated untracked files `Local`, `clean`, and `unchanged` in the primary
checkout were preserved and not staged. No secrets or raw customer/model data
were printed or committed. Strategy/human authority retains PR acceptance and
merge choice.

# OAP Work Order — 004-ad

## Objective

Run the already-prepared, human-authorized live vision acceptance exactly once
against the active protected vision fixture. Prove real Codex 0.149.0 through
Local Coding preserves governance while adapting full-image history to the
newest crop across every actual outbound tool-loop request. Do not mutate the
protected vision/text services. Publish truthful evidence on the existing
Objective-004 PR; never merge.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`.
- Numeric objective / round: `004` / `004-ad`, human-authorized continuation
  after `004-z` on the same objective branch and PR.
- PR mode: `AMEND_EXISTING_PR`; **NO NEW PR**.
- Existing PR: #6, `https://github.com/ulfe-lmi/slaif-local-coding/pull/6`.
- Base/head: `main` at `7a2c36a0a40958a6059a765c2f9d5e5bf4ddc161` /
  `oap/004-real-codex-governed-e2e`.
- Current verified remote head / 004-ac SELF:
  `b4025c9aaa1a74a445dba8993c17135fb0e3cae7`.
- 004-ac implementation parent:
  `befa201f09775265112ee31f03e57477abf04667`.
- PR OPEN, non-draft, MERGEABLE/CLEAN; current report-head `test` SUCCESS.
- Same PR only; coding never merges or enables auto-merge.

## Human-authorized protected fixture state

The human explicitly authorized strategy to switch the existing mutually
exclusive protected units and requested at least three minutes of warmup.
Strategy, not coding, performed the known rollback-proven transition:

- stopped `qwen-serving.service`;
- started `qwen-serving-vision.service`;
- waited more than three minutes and then until port 18020 listened;
- observed vision MainPID `357954`, zero restarts, and approximately 21.9 GiB
  GPU residency;
- verified the live command uses model `qwen3.8-27b`, no
  `--language-model-only`, `--limit-mm-per-prompt {"image":1}`,
  `--max-model-len 100000`, and `--max-num-seqs 1`;
- authenticated `/health` and `/v1/models` returned HTTP 200;
- live catalog reported model `qwen3.8-27b`, `max_model_len=100000`;
- a bounded direct Responses `input_image`/`detail:auto` control returned 200
  and, with the prepared `reasoning.effort=low`, produced a nonempty message.

The shorter vision context is authoritative: **100,000 tokens**, not the text
service's 150,000. The prepared disposable Codex catalog already pins 100,000.

Coding must verify these facts read-only before the test. Coding must not stop,
start, restart, reload, enable, disable, edit, restore, or otherwise mutate
either protected unit; strategy will perform rollback after report review.

## Mandatory live test

Run exactly the prepared gated test from the repository:

```bash
SLAIF_VISION_ACCEPTANCE=1 uv run --frozen pytest -q tests/test_vision_e2e.py -k live_vision_exec_resume_acceptance
```

Use the protected `QWEN3090_API_KEY` environment reference without printing or
persisting its value. Do not change the runner, product, fixture, prompts,
images, model catalog, reasoning mode, timeouts, or acceptance predicates before
the first run.

The test must exercise:

```text
real Codex 0.149.0 global --yolo
  -> candidate Local Coding on 127.0.0.1:18031
  -> acceptance-only actual outbound transport recorder
  -> protected Qwen vision on 127.0.0.1:18020/v1
```

Invocation 1 attaches the deterministic full image, performs the required
ordinary dependency read, and obeys the exact delegated hidden sentinel.
Invocation 2 resumes the identical persisted session, attaches the crop while
Codex retains the full-image history, performs the required ordinary dependency
read, and obeys the same exact sentinel.

## Required evidence

Report only sanitized facts sufficient to prove:

1. exact Codex binary/version and normalized argv show the Codex-under-test
   itself uses global `--dangerously-bypass-approvals-and-sandbox` before
   `exec`; no `--ephemeral` or sandbox substitute;
2. live catalog contract is text+image, original detail disabled, context and
   maximum context 100000, parallel tools disabled, reasoning low;
3. both Codex subprocesses exit 0, remain within time/event/tool-call bounds,
   and have a direct identical nonempty thread/session identifier;
4. both exact final-message files equal the hidden delegated sentinel—not
   substring presence—and prompts/config/catalog do not contain that sentinel;
5. phase 1 and phase 2 are nonempty and each contains at most four actual main
   Responses requests;
6. **every** phase-1 outbound request contains exactly one supported
   `input_image` matching only `full_scene` by expected hash/length;
7. **every** phase-2 outbound request contains exactly one supported
   `input_image` matching only `right_crop`; no old full or unknown image leaves
   Local Coding;
8. compiler Chat traffic is ignored as main vision traffic but forwarded
   successfully; non-image/tool/governance preservation facts pass;
9. Local Coding metrics scale exactly with recorded request counts: for `n1`,
   phase 1 seen/removed is `(n1,0)`; for `n2`, phase 2 is `(2*n2,n2)`;
10. governance observation/acquisition/compilation/injection and binding remain
    effective through the vision/tool interactions, without unsafe bypass;
11. protected upstream accepts the transformed image requests and both model
    lifecycles complete; no image-quality or benchmark claim is required;
12. candidate port 18031 and all temporary fixture/image/cache/CODEX_HOME/
    config/catalog/output/recorder state are absent afterward;
13. logs, metrics, result facts, diff, and report contain no API key, auth,
    data URL/base64, raw image, prompt, source, tool output, model response,
    sentinel value, session ID, or customer content;
14. vision MainPID/start timestamp/restart count and protected unit/launcher/
    environment/profile/network hashes/state remain unchanged during coding.

## Result handling

- If the prepared test passes, update `oap/COMPLETENESS.md` to Objective 004
  100% and branch weighted readiness approximately 91%, with exact bounded
  vision evidence and no production/cutover claim. Update the Objective-004
  ledger and vision acceptance document to record the live result and preserve
  the 100,000-token vision limitation.
- If the test fails, do not rerun, weaken a gate, change product/helper, or
  consume more vision/model calls. Record the first direct failure, classify it
  as Local Coding, harness, Codex, or protected-fixture evidence, leave
  Objective 004 open, and report `PARTIAL|FAILED` truthfully. Strategy decides
  any smallest corrective continuation.
- Regardless of result, do not operate protected units. Leave vision active for
  strategic review/rollback.

## Verification

After the live test, run frozen dependency checks, Ruff check/format, mypy
`src tests`, focused/full pytest (the live result is separately explicit),
build, wheel/sdist boundary inspection, compileall, shell syntax,
`git diff --check`, and sensitive-content scans. Skipped opt-in tests remain
skipped and are never claimed as pass. Verify current implementation/report-head
GitHub CI.

## Non-goals and safety

- No service switch/rollback by coding; no protected file/config/model/key/
  profile/firewall/VPN/network/systemd mutation.
- No product/helper/test change before or after a negative live result.
- No native compaction, sandbox, workspace-write, bubblewrap, environment,
  gateway, cutover, benchmark, or broad diagnostic work.
- No second live acceptance attempt in this round.
- No production/general vision claim beyond Qwen3.8-27B on this verified host,
  one image per upstream request, context 100000.

## Acceptance criteria

1. Exactly one prepared live test execution occurs after read-only fixture
   qualification.
2. All fourteen evidence items pass or the first exact failure is reported.
3. No protected mutation and no raw-sensitive retention/exposure.
4. Candidate/temp cleanup and port-18031 absence are proven.
5. Documentation/completeness advances only on full pass.
6. Same PR only, exact report chain, required current CI green, no merge.

## Publication contract

Commit/push the exact activated order/active and, only on full pass, the bounded
ledger/completeness/vision-document updates to the existing PR branch. Push all
non-report work first and record its literal 40-hex SHA. Publish exactly one
immutable `oap/reports/004-ad-live-codex-vision-acceptance.md` containing the
literal implementation SHA and `Report publication commit: SELF`. SELF must be
the sole final commit, change only that report, have the implementation SHA as
first parent, and be remote PR head before response FIFO `OK`.

# OAP Work Order — 004-aj

## Objective

Resolve the last unknown acceptance facts without guessing: capture only the
actual top-level Codex 0.149 `tools[].type` strings through a temporary no-model
provider, update the repository-only structural allowlist only for justified
standard types, add privacy-safe final-message relationship facts, and execute
exactly one unchanged live vision acceptance attempt. Do not weaken byte-exact
binding or change Local Coding production code/services.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`.
- Numeric objective / round: `004` / `004-aj`.
- PR mode: `AMEND_EXISTING_PR`; **NO NEW PR**.
- PR #6: `https://github.com/ulfe-lmi/slaif-local-coding/pull/6`.
- Base/head: `main` at `7a2c36a0a40958a6059a765c2f9d5e5bf4ddc161` /
  `oap/004-real-codex-governed-e2e`.
- Current verified remote head / 004-ai SELF:
  `b311ef754fff7266365e5b660b587861e12d22df`.
- 004-ai implementation parent:
  `38a96467472829180ca773c7ae2bcd477a923687`.
- PR OPEN/non-draft/MERGEABLE/CLEAN; report-head required `test` SUCCESS.
- Same PR only; coding never merges or enables auto-merge.

## Accepted evidence and unknowns

The live full/crop image path, session, catalog/context, processes, phase counts,
scaled metrics, governance markers, upstream success, cleanup, and protected
state pass. Both final channels in both turns are 39 bytes versus expected 37,
same per-run hash, but remain fixed `other_mismatch`. Each request has three
top-level tool definitions: one `custom`, zero known `function/local_shell`, and
two `unexpected`; call/result items are present on continuation requests.

No Local Coding product defect is established. Do not infer wrapper bytes or
tool types from these counts.

## A. Temporary no-model Codex tool-type capture

Before any protected-model call, run one disposable local capture equivalent to:

```text
Codex 0.149 disposable CODEX_HOME/catalog/config
  -> temporary loopback fake Responses provider on a verified-free port
  -> receive first request only
  -> extract only bounded top-level tools[].type strings/counts
  -> discard entire body in memory
  -> return fixed sanitized error and stop
```

Requirements:

- use the same catalog/features/config construction as the vision acceptance,
  including image capability and global yolo invocation shape, but do not use
  Local Coding or protected Qwen;
- one Codex invocation, stop immediately after first request/fixed error;
- accept for reporting only ASCII type strings matching
  `^[a-z][a-z0-9_.-]{0,63}$`, maximum 16 definitions/16 unique types;
- retain only ordered type strings and counts; no names, descriptions, schemas,
  grammar, arguments, image/data URL, prompt, source, instructions, headers,
  auth, session ID, response, body, or credential;
- temporary server/config/image/home/log state removed; no raw request logging;
- if safe capture cannot be guaranteed, stop before Codex and report blocker.

Report the exact safe type tuple/counts. These protocol type labels are not
customer data.

## B. Evidence-based repository-only allowlist

After capture, amend `_SUPPORTED_TOOL_DEFINITION_TYPES` only for observed types
that are standard Codex/OpenAI-compatible tool category labels and structurally
appropriate. Do not accept arbitrary strings or wildcard/prefix classes.

Add focused positive/negative/bounds/privacy tests for the exact observed set.
The live predicate requires all top-level definitions recognized or a recognized
call/result item as designed; retain fixed category counts and unexpected bucket.
No production forwarding change.

## C. Safe final-message relationship evidence

Without changing exact/terminal-CRLF acceptance, extend each transient event/file
comparison with only:

```text
contains_expected: bool
expected_offset: bounded int or null
common_prefix_bytes: bounded int
common_suffix_bytes: bounded int
leading_extra_bytes: bounded int or null
trailing_extra_bytes: bounded int or null
```

Definitions:

- all comparisons occur transiently against expected bytes;
- offset/extra counts are emitted only when expected occurs exactly once;
- common prefix/suffix are capped at expected length;
- no actual bytes, characters, token, message, prompt, source, path, session,
  or arbitrary strings retained;
- these facts are diagnostic only and cannot make `sentinel_passed=true`;
- exact or terminal CR/LF-only rules from 004-ah remain unchanged.

Add exhaustive tests for exact, prefix/suffix/wrapper, missing expected,
repeated expected, same-length unrelated, and privacy. Ensure diagnostics cannot
reconstruct actual content beyond these bounded relations.

## D. Active fixture and one live attempt

Human requires vision remain running. Verify read-only: vision PID `364444`
active/zero restarts, text inactive, health/models 200, model/context 100000,
port 18031 free. Never operate protected units.

After no-model capture, evidence-based allowlist update, and all focused/Ruff/
mypy gates pass, execute exactly once:

```bash
SLAIF_VISION_ACCEPTANCE=1 uv run --frozen pytest -q tests/test_vision_e2e.py -k live_vision_exec_resume_acceptance
```

Do not change prompt/dependency/catalog/image/session/phase cap/metrics/binding
acceptance, retry, or edit after failure.

On pass, update completion evidence. On failure, report fixed reasons, safe tool
type categories, and message relationship counts only, then stop.

## E. Completion updates

Only on full pass update Objective 004 to 100%, weighted branch readiness about
91%, ledger, vision docs, and completeness. Preserve 100000 context, one-image
limit, selected host/model scope, and no production/cutover/benchmark claim.
On failure retain 90%.

## Non-goals and safety

- No product change, acceptance weakening, cap change, protected mutation,
  sandbox/compaction/gateway/cutover work, raw sensitive retention, or second
  protected live attempt.

## Verification and publication

Run safe capture tests/evidence, focused tool/message/verdict/privacy tests,
Ruff/mypy, the one live attempt, non-live full pytest, build/wheel boundary,
compileall, shell syntax, diff and precise sensitive scans. Current CI required
green.

Push exact active/order and bounded repository-only helper/test/docs or
success-only ledger changes to the same PR. Publish exactly one immutable
`oap/reports/004-aj-safe-codex-tool-type-capture-and-message-diff.md` with
literal implementation SHA and `Report publication commit: SELF`; SELF changes
only report, parent equals implementation SHA, and is remote head before FIFO
`OK`.

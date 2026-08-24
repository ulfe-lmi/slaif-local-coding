# OAP Coding-Agent Report — 004-al

## Work order

- Identifier: `004-al`
- Order path: `oap/orders/004-al-architecture-binding-normalization-and-final-vision.md`
- Numeric objective: `004`
- PR mode: `AMENDED_EXISTING_PR`

## Status

COMPLETE

## Executive summary

Implemented the repository-only CR/LF framing normalization required by the
canonical architecture. The hidden sentinel remains byte-exact internally;
only leading and/or trailing CR/LF framing is accepted as an effective binding.
Spaces, tabs, Unicode whitespace, wrappers, punctuation, prose, substring
matches, repeated sentinels, and other differences remain failures. Exact byte
format is reported independently.

The one authorized live vision acceptance run passed. Objective 004 is recorded
at 100% and the branch completeness record at approximately 91%, scoped to the
selected Qwen3.8-27B RTX 3090 fixture.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #6 — `https://github.com/ulfe-lmi/slaif-local-coding/pull/6` — `OPEN`, non-draft, mergeable and clean.
- Base/head: `main` / `oap/004-real-codex-governed-e2e`.
- Starting remote SHA: `21ee57f536a4f5e31586b551a179e94a0adf699f`.
- Implementation head SHA: `42d8cb830f818bfea6865a9b5a5da932cecae253`.
- Report publication commit: `SELF`.
- Implementation commits pushed before report: `42d8cb830f818bfea6865a9b5a5da932cecae253`.
- New PR this round: `NO`; amended existing PR: `YES`; merge performed: `NO`.

## Changes and files

- `tests/helpers/vision_e2e_support.py`: added strict surrounding-CR/LF
  detection, separate `binding_effective`/`byte_exact_format` facts, updated
  fixed provenance and failure labels, and privacy-safe summary fields.
- `tests/test_vision_e2e.py`: added exhaustive framing, rejection, provenance,
  event/file priority, fixed-classification, and privacy coverage.
- `docs/OBJECTIVE-004-LEDGER.md`, `docs/VISION-ACCEPTANCE.md`,
  `oap/COMPLETENESS.md`: recorded the successful fixture-scoped result,
  context/image limits, transformation shape, and LF/LF limitation.
- `oap/active` and the activated 004-al order were committed byte-for-byte;
  no strategic-authored order or active content was edited.

## Acceptance evidence

### Criterion A — exact CR/LF-only normalization

- PASSED — exact bytes remain accepted and `byte_exact_format` remains true.
- PASSED — one or more leading and/or trailing CR/LF bytes around the exact
  expected bytes set `surrounding_crlf_only` and `binding_effective` without
  accepting any interior or non-CR/LF difference.
- PASSED — event/file provenance is the fixed vocabulary
  `event_exact`, `event_surrounding_crlf`, `file_exact`,
  `file_surrounding_crlf`, `mismatch`, `missing`, with event evidence taking
  priority.
- PASSED — diagnostics retain only bounded lengths, hashes, booleans, offsets,
  fixed labels, and counts; no raw sentinel, framing bytes, prompt, source,
  image, tool output, or credential enters the summary.

### Criterion B — final live vision acceptance

- PASSED — exactly one authorized `live_vision_exec_resume_acceptance` run:
  `1 passed, 120 deselected in 99.16s`.
- PASSED — Codex 0.149.0 used the persistent same-session global-yolo shape:
  full image on turn 1, then `resume --last` with the newest crop on turn 2;
  no ephemeral session or prompt-supplied processing marker.
- PASSED — every bounded phase-1 main request forwarded one `full_scene`
  image, and every bounded phase-2 main request forwarded one newest
  `right_crop` image. Both phases were non-empty and capped at four requests.
- PASSED — scaled image metrics matched `(n1, 0)` for phase 1 and
  `(2*n2, n2)` for phase 2, where `n1` and `n2` are the directly recorded,
  bounded phase request counts.
- PASSED — same persisted/resumed session, image-capable catalog, disabled
  original image detail, context `100000`, disabled parallel tools, successful
  bounded event/tool lifecycle, governance observation/acquisition/compile/
  injection, upstream response, cleanup, and privacy predicates.
- PASSED — both turns had `binding_effective=true`. The unchanged fixture
  classification is `leading_lf_lf` for the event and output-file channels;
  `byte_exact_format=false` is reported separately for both turns and the
  accepted aggregate provenance is `event_surrounding_crlf`.

### Criterion C — protected live fixture

- PASSED — read-only preflight/postflight: vision unit PID `364444`,
  `NRestarts=0`, active/running; text unit inactive/dead; authenticated
  `/health` HTTP `200`; authenticated `/v1/models` HTTP `200` with one
  `qwen3.8-27b` model; process context `100000`, one-image limit, and no
  language-only flag; development port `18031` free after cleanup.
- PASSED — Qwen/vLLM, port `18020`, model/checkpoint/launch flags, systemd,
  credentials, firewall/VPN/network, and existing Codex profiles were not
  changed.

### Criterion D — completeness and documentation

- PASSED — Objective 004 ledger is 100%; weighted branch readiness is recorded
  as approximately 91%.
- PASSED — documentation states vision context `100000` versus text `150000`,
  one-image upstream capacity, full/full then crop/crop adaptation, the
  effective-but-not-byte-exact binding, and the selected host/model/hardware
  scope without production, cutover, benchmark, or visual-quality claims.

## Verification

- `git fetch --prune origin`: PASSED — remote reconciled before mutation.
- `uv run --frozen pytest -q tests/test_vision_e2e.py -k 'final_binding or prefix_classification or diagnostic_summary or failure_reasons or marker_like'`: PASSED — `67 passed, 54 deselected`.
- `uv run --frozen ruff check src tests`: PASSED — all checks passed.
- `uv run --frozen ruff format --check src tests`: PASSED — 43 files already formatted.
- `uv run --frozen mypy src tests`: PASSED — 42 source files checked.
- `SLAIF_VISION_ACCEPTANCE=1 uv run --frozen pytest -q tests/test_vision_e2e.py -k live_vision_exec_resume_acceptance`: PASSED — one authorized run, `1 passed, 120 deselected in 99.16s`.
- `uv run --frozen pytest -q tests/test_vision_e2e.py`: PASSED — `120 passed, 1 skipped`.
- `uv run --frozen pytest -q`: PASSED — `438 passed, 8 skipped`.
- `uv build --wheel`: PASSED — wheel built successfully.
- Wheel boundary inspection: PASSED — 23 wheel entries; no tests, OAP, or governance files.
- `uv run --frozen python -m compileall -q src tests`: PASSED.
- `bash -n` for every repository `*.sh`: PASSED.
- `git diff --check`: PASSED.
- Added-line secret/raw-content scan: PASSED — no credential, bearer token,
  private key, data URL, or raw sentinel token detected.

## Live model/service evidence

- Endpoint/route: authenticated private Qwen vision fixture through the
  repository candidate on development port `18031`; no credential or raw
  payload is recorded here.
- The live runner asserted exact image identity/count, ordering, preserved
  non-image/governance/tool content, model catalog facts, session continuity,
  bounded process/tool lifecycle, scaled metrics, effective binding, cleanup,
  and privacy. No visual-quality benchmark was run or claimed.
- Temporary candidate, fixture, cache, session, output, and log state was
  removed by the test context; protected vision remained running.

## GitHub CI / required checks

- Implementation-head `test`: `SUCCESS` for
  `42d8cb830f818bfea6865a9b5a5da932cecae253`.
- All required implementation-head checks green at report drafting: `YES`.
- Report-head checks may be pending after publication; strategy verifies them.

## Local setup/dependencies

- Used the existing frozen repository `uv` environment; no dependency was
  added and no protected or persistent service setup was changed.
- Wheel/build artifacts were repository-ignored and are not part of the commit.

## Documentation

- Updated the Objective-004 ledger, vision acceptance handoff, and OAP
  completeness record as required by the order.
- Prior negative OAP reports were not edited or rewritten.

## Safety/scope confirmations

- Unrelated files: `NONE`.
- Secrets/raw content: no raw request, response, prompt, source, image, tool
  data, credential, key, cookie, or private payload was retained or published.
- Production/protected resources: no mutation; protected `18020`/Qwen/Codex
  fixture changed: `NO`.
- Required tests skipped/not run: the full suite and vision suite each had the
  exact skipped counts reported above; skips were not represented as passes.
- Scope deviation: `NONE`.
- Extra objective PR: `NO`; coding merge: `NO`.
- Active/order edited: `NO`; activated bytes committed unchanged.
- Report commit report-only: `YES`.

## Known limitations/blockers

- The selected Qwen vision fixture emits two leading LF bytes around the hidden
  sentinel. Effective governance binding passes under the explicitly narrow
  CR/LF framing rule, while byte-exact final formatting is not proven or
  supported on this fixture.
- Evidence is limited to the selected host, model, hardware, route, and bounded
  acceptance fixture; it is not a generic model, production, cutover, capacity,
  or visual-quality claim.

## Recommended strategic follow-up

- Review the complete 004-al evidence and decide acceptance/merge/release or
  the next OAP order. Coding does not choose that decision.

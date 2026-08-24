# OAP Coding-Agent Report — 004-ad

## Work order

- Identifier: `004-ad`
- Order path: `oap/orders/004-ad-live-codex-vision-acceptance.md`
- Numeric objective: `004`
- PR mode: `AMENDED_EXISTING_PR`

## Status

FAILED

## Executive summary

The one mandated live vision acceptance run was executed exactly once against
the already-active protected vision fixture. It failed at the first direct
acceptance failure: phase 2 exceeded the prepared maximum of four actual main
Responses requests, and the acceptance recorder raised
`vision_phase_request_bound_exceeded`. No retry, harness/product change, or
additional vision/model call was made. Protected service state and temporary
state were verified unchanged/clean. Objective 004 remains open; no
success-only completeness or ledger update was made.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #6, https://github.com/ulfe-lmi/slaif-local-coding/pull/6
- State: OPEN, non-draft, MERGEABLE; no merge or auto-merge performed
- Base/head: `main` / `oap/004-real-codex-governed-e2e`
- Starting remote SHA: `b4025c9aaa1a74a445dba8993c17135fb0e3cae7`
- Implementation head SHA: `cbac2b3b2733f630cde334345a52b798cb44f09f`
- Report publication commit: SELF
- Implementation commits pushed before report: `cbac2b3b2733f630cde334345a52b798cb44f09f` (`OAP 004-ad: record live vision acceptance failure`)
- New PR this round: no
- Amended existing PR: yes, PR #6
- Merge performed: NO

## Changes and files

- Committed the strategic-authored `oap/active` selection and exact activated
  `004-ad` order bytes.
- No product source, runner, fixture, service, configuration, completeness,
  ledger, or vision-document change was made after the negative live result.
- This report is the only file in the final publication commit.

## Acceptance evidence

### Criterion 1 — exactly one prepared run and Codex invocation contract

- PASSED — the exact ordered command was started once; no second attempt was
  made. Read-only preflight reported `codex-cli 0.149.0`. Complete normalized
  invocation facts were not returned because the runner terminated before its
  final session fact object; no unsupported sandbox or ephemeral claim is made.

### Criterion 2 — live catalog contract

- PASSED as preflight only — protected `/v1/models` returned model
  `qwen3.8-27b` with `max_model_len=100000`; the prepared disposable catalog
  path was used. Full acceptance evidence was not completed.

### Criterion 3 — subprocess lifecycle and session binding

- NOT RUN — no final `VisionSessionFacts` object was returned after the phase-2
  recorder failure, so exit/session/bound evidence is not claimed.

### Criterion 4 — exact final-message sentinel binding and privacy

- NOT RUN — exact final-message results were not returned after the failure; the
  delegated sentinel value is not reproduced here.

### Criterion 5 — bounded nonempty phases

- FAILED — first direct failure. The phase-2 acceptance recorder exceeded the
  configured maximum of four actual main Responses requests and raised
  `vision_phase_request_bound_exceeded` while closing phase 2. No request count
  beyond that gate is claimed.

### Criteria 6–11 — per-request image, compiler, metrics, governance, and
protected-upstream acceptance

- NOT RUN — the grouped acceptance did not complete after the first direct
  phase-bound failure; no later image, compiler, metric, governance, lifecycle,
  or upstream success facts are claimed.

### Criterion 12 — cleanup and candidate absence

- PASSED — zero temporary `slaif-vision-acceptance-*` directories remained;
  ports `18031` and `18021` were absent after the run; protected port `18020`
  remained listening.

### Criterion 13 — sensitive-content boundary

- PASSED for retained repository evidence — scans of the activated files and
  final diff found zero bearer-token, data-URL/base64, sentinel-value, or
  assigned-key matches. No raw prompt, source, image, tool output, response,
  session identifier, or credential was retained in the report evidence.

### Criterion 14 — protected fixture unchanged

- PASSED — before/after read-only state matched: vision unit active/running,
  text unit inactive/dead, vision MainPID `357954`, zero restarts, port `18020`
  listening. Unit, vision environment, launcher, current Codex profile, unit
  state, and filtered listener fingerprints matched before and after. No
  protected unit, launcher, environment, model, key, profile, firewall, VPN,
  network binding, or service operation was performed.

## Verification

- `SLAIF_VISION_ACCEPTANCE=1 uv run --frozen pytest -q tests/test_vision_e2e.py -k live_vision_exec_resume_acceptance`: FAILED — exactly one run; first direct failure `vision_phase_request_bound_exceeded` in phase 2; 1 failed, 11 deselected, 237.45s.
- `uv run --frozen python -c 'import fastapi, httpx, pydantic, prometheus_client, uvicorn; ...'`: PASSED — frozen runtime imports.
- `uv run --frozen ruff check . && uv run --frozen ruff format --check .`: PASSED — 164 files formatted.
- `uv run --frozen mypy src tests`: PASSED — no issues in 40 source files.
- `env -u SLAIF_VISION_ACCEPTANCE uv run --frozen pytest -q tests/test_vision_e2e.py`: PASSED — 11 passed, 1 skipped; live opt-in remained skipped and was not rerun.
- `env -u SLAIF_VISION_ACCEPTANCE uv run --frozen pytest -q`: PASSED — 319 passed, 8 skipped; live opt-in and other explicit opt-ins remained skipped.
- `uv run --frozen python -m build --no-isolation`: PASSED — wheel and sdist built.
- Initial ad hoc sdist check: FAILED — an overbroad probe incorrectly rejected expected repository files in the sdist; it was not used as the packaging result.
- Repository-aligned wheel/sdist boundary inspection: PASSED — wheel had zero repository-boundary members; both artifacts contained the source package; no runtime artifacts/model-weight extensions were present.
- `uv run --frozen python -m compileall -q src tests`: PASSED.
- `find . -type f -name '*.sh' -print0 | xargs -0 -r -n1 bash -n`: PASSED.
- `git diff --check`: PASSED.
- Activated-file sensitive-pattern scan: PASSED — zero matches.

## Live model/service evidence

- Read-only protected qualification: vision unit active/running/disabled;
  text unit inactive/dead/enabled; authenticated health HTTP `200`; model
  `qwen3.8-27b`; reported maximum context `100000`; port `18020` listening.
- Vision launch contract facts: served model identifier present; no
  `--language-model-only`; image limit `{"image":1}`; `MAX_LEN=100000`; one
  sequence. Preflight GPU query observed approximately `21874 MiB` resident.
- Before/after fingerprints: vision unit
  `fc88870b4f4afee214c25dc9ec544c4178c300bf4d78092a4d12787a955e2e94`;
  vision environment
  `3565d267478bdd33a621c2cf6334d734308dac8087732a74309ae74bce746c21`;
  launcher
  `8c87e0104b25c9600235a97555c4b0a1d0ea55d34ccb4094af428c8b4501f89f`;
  current Codex profile
  `3e670f174810d7f859679c09920ac9ef47568b9a300a096a7c9639cf19584b47`;
  filtered listener state
  `26a6b87e165ec03a841d925d27e69d52b60ee306b8207c2b12259aa0fdf62790`;
  protected unit state
  `289ceacf0df395e6f98b7f9c359ec743e4e3754a9dd35b9b345a06cdc435ebda`.
- No production, cutover, image-quality, benchmark, or general vision claim
  is made.

## GitHub CI / required checks

- Implementation-head check: `test` — SUCCESS for
  `cbac2b3b2733f630cde334345a52b798cb44f09f` (23s).
- All required checks green at report drafting: yes, for the implementation
  head.
- Report-head checks may be pending; strategy verifies them independently.

## Local setup/dependencies

- Used existing repository `.venv` and `uv run --frozen`.
- No protected service, systemd, model, key, profile, firewall, VPN, or
  network mutation; no dependency or product change was made.

## Documentation

- Not updated. The order permits completeness, ledger, and vision-document
  advancement only on a full live pass; the negative result leaves Objective
  004 open.

## Safety/scope confirmations

- Unrelated files: preserved.
- Secrets/raw prompts/source/images/tool output: not retained in code evidence,
  report, or repository state.
- Protected 18020/Qwen/Codex fixture changed: NO.
- Required live test retries/additional vision calls: NO.
- Extra objective PR: NO.
- Coding merge/auto-merge: NO.
- Active/order edited by coding: NO; exact activated bytes were committed.
- Final report commit report-only: yes.

## Known limitations/blockers

- The first direct failure is the acceptance harness phase-2 request bound.
  Root cause beyond that observable gate is not established by this round.
- Per-request phase facts, exact sentinel binding, session identity, and later
  governance/image/metric predicates remain unproven.
- Objective 004 remains open; this report is not acceptance or release.

## Recommended strategic follow-up

- Strategy may review the bounded phase-2 failure and decide whether a separate
  smallest corrective continuation is warranted. No rerun or corrective change
  is authorized by this round.

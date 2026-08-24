# OAP Coding-Agent Report — 004-aa

## Work order

- Identifier: `004-aa`; order path: `oap/orders/004-aa-simulated-compaction-and-vision-readiness.md`; numeric objective: `004`.
- PR mode: `AMENDED_EXISTING_PR`.

## Status

COMPLETE

## Executive summary

The canonical adapter-boundary simulated-compaction proof passed on the current
protected text model through one disposable candidate on loopback port 18031.
One synthetic root and one exactly paired delegated dependency established,
compiled, cached, selected, and injected a binding rule. A stateless zero-root
follow-up hit process-local rehydration, reinjected the rule, made zero
additional compiler-model attempts, and complied with the ephemeral hidden
sentinel. The derived compiler prompt was narrowly strengthened to preserve
exact case-sensitive normative literals after the first audit found that
specific local defect.

The repository-only vision fixture, fake boundary recorder, deterministic PNGs,
catalog contract, `exec`/`exec resume --last` runner, cleanup checks, and human
handoff are ready. Live vision was not run because the protected vision unit is
inactive; Objective 004 remains pending only on the human-provided live vision
fixture.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`.
- PR: [#6](https://github.com/ulfe-lmi/slaif-local-coding/pull/6), OPEN,
  non-draft, CLEAN/MERGEABLE.
- Base/head: `main` / `oap/004-real-codex-governed-e2e`.
- Starting remote SHA: `5d2cd6bce1702f04c603bc434e473a90fd00e7d0`.
- Implementation head SHA: `899d589ec771539a098a86a6ad3f10ec4736d153`.
- Report publication commit: SELF.
- Implementation commits pushed before report: `899d589ec771539a098a86a6ad3f10ec4736d153` — `OAP 004-aa: prepare vision readiness and compaction proof`.
- New PR this round: NO; amended existing PR: YES; merge/auto-merge: NO.

## Changes and files

- Added `tests/helpers/vision_e2e_support.py` and
  `tests/test_vision_e2e.py` for private deterministic PNG fixtures, the
  persistent disposable Codex home/catalog, exact yolo `exec`/resume argv,
  safe boundary evidence, metric deltas, and gated live cleanup.
- Added `docs/VISION-ACCEPTANCE.md` and
  `docs/OBJECTIVE-004-LEDGER.md` for the human fixture contract, rollback,
  evidence boundary, and complete non-vision criterion ledger.
- Updated `oap/COMPLETENESS.md` to record the accepted simulated boundary and
  leave live vision as the sole Objective-004 gap.
- Strengthened the bounded compiler prompt in
  `src/slaif_local_coding/constitution/compiler.py` to retain exact normative
  literals; added focused prompt regression coverage in
  `tests/test_compiler.py`.
- Preserved and committed the exact strategic activation, `004-aa` order, and
  the two prepublication OAP-validator regex edits accepting one- or two-letter
  lowercase suffixes.

## Acceptance evidence

### Criterion 1 — architecture and simulated-boundary fidelity

- PASS — Architecture sections 7.14 and 8.4 define stable constitutional
  injection independent of client-retained history; the implementation uses
  bounded validated process-local derived indexes and endpoint-specific
  idempotent injection. It does not claim native Codex compaction.
- PASS — The live sequence used one synthetic root, one exact paired dependency,
  then a stateless zero-root request with no source, prior history, dependency
  bytes, or sentinel in the follow-up input.
- PASS — First compiler-attempt delta was `2`; second-request delta was `0`.
  Rehydration hit delta was `1`, rehydrated injection delta was `1`, both main
  responses were HTTP `200`, and hidden-sentinel compliance was true on both
  responses.
- PASS — The derived cache contained the sentinel after the compiler-prompt
  correction; the temporary candidate log did not contain it. No raw prompt,
  source, image, tool output, request body, credential, or session ID was
  retained in evidence.

### Criterion 2 — focused and live simulated-boundary proof

- PASS — Focused rehydration/cache/pipeline/compiler/vision tests passed.
- PASS — The bounded live candidate was health `200`, used the protected text
  model read-only, completed exactly two main requests, and was removed with
  port 18031 absent afterward.
- PASS — The concrete compiler literal-loss defect was fixed only in the
  compiler instruction contract and covered by a focused regression test.

### Criterion 3 — non-vision Objective-004 reconciliation

- PASS — `docs/OBJECTIVE-004-LEDGER.md` maps accepted 004-s, 004-w, 004-x,
  objective-003, fresh focused, and fresh simulated-boundary evidence across
  Codex yolo, acquisition/compile/injection, cache invalidation/isolation/
  bounds, text/tools/multi-turn/SSE, security/privacy, candidate packaging,
  provenance, and protected-host preservation.
- PASS — Native compaction trigger investigation is not required by the
  human-authorized `004-aa` order and was not performed.
- PASS — Gateway integration/cutover remains a separately documented milestone;
  no production or generic-model equivalence claim was added.

### Criterion 4 — repository-only vision readiness

- PASS — Fake/focused suite proves the runner uses Codex `0.149.0`, global
  `--dangerously-bypass-approvals-and-sandbox` before `exec`, no `--ephemeral`,
  initial `exec --image full.png`, and same-session `exec resume --last --image
  crop.png`.
- PASS — Catalog contract is text+image input, `supports_image_detail_original`
  false, context `100000`, and parallel tool calls disabled.
- PASS — Boundary recorder evidence proves turn 1 seen/forwarded/removed
  `1/1/0`, turn 2 `2/1/1`, newest crop forwarding, and preservation of
  non-image, tool, and governance content. Exact synthetic fixture lengths and
  SHA-256 values are retained only in bounded temporary test facts.
- PASS — Wheel inspection found `23` members and zero `tests`, `oap`, or helper
  support members.

### Criterion 5 — protected vision fixture handoff

- PASS — `docs/VISION-ACCEPTANCE.md` records the mutually exclusive
  `qwen-serving-vision.service` contract, protected endpoint/model/capability,
  human-owned switch and text rollback, exact gated command, cleanup, and
  read-only verification expectations without credentials.
- NOT RUN — Live vision full-image/crop request; the unit was inactive and the
  order expressly prohibited operating it in this round.

### Criterion 6 — required repository gates

- PASS — Frozen dependencies, static checks, focused/full tests, build,
  compileall, shell syntax, wheel boundary, whitespace, validator, and
  sensitive-content scans are recorded below.

### Criterion 7 — remote publication and safety

- PASS — Same PR #6 only; implementation head and required GitHub check are
  remote before this report; no merge or protected service mutation occurred.

## Verification

- `uv lock --check`: PASSED — 32 packages resolved; lock unchanged.
- `uv sync --frozen --extra dev`: PASSED — 31 packages checked.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen ruff format --check .`: PASSED — 158 files formatted.
- `uv run --frozen mypy src tests`: PASSED — no issues in 40 source files.
- `uv run --frozen pytest -q tests/test_compiler.py tests/test_rehydration.py tests/test_cache.py tests/test_pipeline.py tests/test_vision_e2e.py tests/test_packaging.py`: PASSED — 70 passed, 1 skipped; the skip is the human-gated live vision test.
- `uv run --frozen pytest -q -rs`: PASSED — 312 passed, 8 skipped. Seven are opt-in current-service tests and one is the explicit human-gated live vision test; skips are not claimed as passes.
- `uv build`: PASSED — source distribution and wheel built.
- Wheel/sdist boundary inspection: PASSED — wheel 23 members with zero test/OAP/helper support members; sdist 180 members and repository-only support retained outside the wheel.
- `uv run --frozen python -m compileall -q src tests oap/bin`: PASSED.
- `bash -n oap/bin/*.sh`: PASSED.
- `git diff --check` and staged diff check: PASSED.
- OAP validator ID check: PASSED — legacy IDs and `004-aa` accepted; empty, uppercase, numeric, three-letter, and malformed IDs rejected.
- Sensitive-content scan: PASSED — zero credential/private-key literals, raw-payload logging matches, and private absolute paths in changed content.
- `uv run --frozen python -` bounded simulated-boundary harness: PASSED — one candidate, two main requests, fixed counts/booleans above; temporary state removed.
- `SLAIF_VISION_ACCEPTANCE=1 uv run --frozen pytest -q tests/test_vision_e2e.py -k live_vision_exec_resume_acceptance`: NOT RUN — explicit human fixture gate was not active; no live vision claim.

## Live model/service evidence

- Protected text service: `qwen-serving.service` active/running, MainPID
  `26028`, start timestamp unchanged; port `18020` remained the only relevant
  listener.
- Protected vision service: `qwen-serving-vision.service` loaded but
  inactive/dead; no port `18021` or `18031` listener remained after testing.
- Read-only protected hashes remained unchanged: text unit
  `64b3ccd5bdb64da4e3dcabca660fada8155583c96b6bc11de47536e595df5910`, text
  drop-in `1260c69b2b8e956030d14123d0b7f9e09efdf056e569f609fc09a7d2baf7b1db`,
  vision unit `fc88870b4f4afee214c25dc9ec544c4178c300bf4d78092a4d12787a955e2e94`,
  vision launcher `8c87e0104b25c9600235a97555c4b0a1d0ea55d34ccb4094af428c8b4501f89f`,
  and handoff `d9273c24beff11ba40af3b754e3c761d5da0b0a84fabe514fc2ab9e9aa3a`.
- Candidate: repository-owned temporary process only on loopback port 18031;
  health `200`; stopped and cleaned after the bounded proof.
- No vision request, protected service switch, model/config/profile change,
  API-key readout, firewall/VPN/network mutation, or image proxy was performed.

## GitHub CI / required checks

- Implementation-head check `test`: SUCCESS — GitHub Actions run
  `32674356636`, job `97279927112`, at implementation head
  `899d589ec771539a098a86a6ad3f10ec4736d153`.
- All required checks at report drafting: YES for the implementation head.
- Report-head checks may be pending after the report-only push; strategy
  independently verifies the final SELF commit.

## Local setup/dependencies

- Used the existing Python 3.12 repository environment and frozen `uv` sync.
- No dependency or lockfile change.
- Temporary candidate, cache, Codex home, synthetic Git repository, images,
  logs, and inline harness state were private and removed after each run.
- No sudo action was required.

## Documentation

- Updated adapter configuration documentation for exact-literal compiler
  preservation.
- Added the Objective-004 criterion ledger and the human-gated vision handoff.
- Updated completeness arithmetic and remaining-gap wording honestly.

## Safety/scope confirmations

- Unrelated files: NO.
- Secrets/raw prompts/source/images/tool output/customer data exposed or
  committed: NO.
- Protected port 18020/Qwen/Codex fixture changed: NO.
- Required tests skipped/not run: current opt-in live suite remains skipped;
  live vision remains not run pending the human gate.
- Scope deviation: NO; the compiler prompt correction was the one concrete
  in-scope defect revealed by the ordered simulated proof.
- Extra objective PR: NO; coding merge/auto-merge: NO.
- Activated order/active bytes edited by coding: NO; exact strategic bytes were
  preserved and committed.
- Final report commit report-only: YES.

## Known limitations/blockers

- Live vision remains pending until the human deliberately activates the
  mutually exclusive protected vision unit and runs the documented gate.
- This round proves adapter-boundary simulated/new-context rehydration, not
  native Codex compaction or reduced client history.
- The MVP still uses configured single-user identity and a process-local
  rehydration map; signed multi-user gateway identity and cutover remain later
  milestones.

## Recommended strategic follow-up

Independently verify this report-only commit, then issue the documented human
vision action if live vision evidence is desired. Strategy decides review,
acceptance, merge, and any next OAP order.

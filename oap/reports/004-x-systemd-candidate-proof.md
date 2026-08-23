# OAP Coding-Agent Report — 004-x

## Work order

- Identifier: `004-x`; order path: `oap/orders/004-x-systemd-candidate-proof.md`; numeric objective: `004`.
- PR mode: `AMENDED_EXISTING_PR`.

## Status

COMPLETE

## Executive summary

Updated the accepted objective-004 completeness baseline from 40% to 60%
(`~83%` branch readiness), hardened the uninstalled user-systemd candidate
example with compatible private/bounded lifecycle settings, and added static
packaging tests and operational documentation. A unique transient user-systemd
candidate on `127.0.0.1:18031` reached `active/running`, passed health,
readiness, metrics, text, function-tool, SSE, privacy, loopback, and process
checks, then stopped cleanly. The protected Qwen service and Codex profiles
were preserved.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`; PR: [#6](https://github.com/ulfe-lmi/slaif-local-coding/pull/6); state: OPEN, non-draft, MERGEABLE.
- Base/head: `main` / `oap/004-real-codex-governed-e2e`.
- Starting remote SHA: `5f5606ded4cbe6679299fec5ba63e402fadd45f6`.
- Implementation head SHA: `8f069db406b8ec40f9418d56331fc80a1a4ba41a`.
- Report publication commit: SELF.
- Implementation commits pushed before report: `8f069db406b8ec40f9418d56331fc80a1a4ba41a` (`OAP 004-x: prove isolated systemd candidate packaging`).
- New PR this round: no; amended existing: yes; merge performed: NO.

## Changes and files

- `packaging/slaif-local-coding.service.example`: explicit repository `.venv`
  and config paths, mode-0600 external `EnvironmentFile`, loopback-only
  address/IP policy, filesystem/home protection, bounded resources, umask,
  journal output, restart/stop timeouts, and graceful SIGTERM lifecycle.
- `tests/test_packaging.py`: static checks for external-secret handling,
  candidate loopback port/config, and compatible systemd hardening.
- `README.md`, `docs/ADAPTER-CONFIGURATION.md`: candidate operations,
  validation, cleanup, and protected-service boundaries.
- `oap/COMPLETENESS.md`: accepted 004-w hardening credited at objective 004
  60% and branch readiness `~83%`.
- Activated `oap/active` and exact `oap/orders/004-x-systemd-candidate-proof.md`
  were committed unchanged as the orchestration transcript.

## Acceptance evidence

### Criterion 1

- PASSED — `oap/COMPLETENESS.md` records objective 004 at 60% and branch
  readiness at approximately 83%, crediting the strategically accepted 004-w
  security/observability hardening.

### Criterion 2

- PASSED — `systemd-analyze verify` succeeded on a `.service`-suffixed copy
  of the packaged example; the focused packaging tests passed.
- PASSED — the unit contains no inline `Environment=` credential or API-key
  argument and references an external environment file; the candidate
  environment file was mode 0600 and its parent boundary mode 0700.
- PASSED — the example config validates loopback `127.0.0.1:18031` and the
  protected upstream remains a separate `18020` target.
- PASSED — compatible normalized user-manager properties were observed as
  `NoNewPrivileges=yes`, `PrivateTmp=yes`, `ProtectSystem=strict`,
  `ProtectHome=read-only`, loopback IP allowlisting, `UMask=0077`,
  `LimitNOFILE=4096`, `TasksMax=128`, and `MemoryMax=1G`.

### Criterion 3

- PASSED — unique transient unit `slaif-local-coding-004x-1787519935-316822.service`
  reached `active/running` as UID 1029, the current unprivileged user.
- PASSED — candidate `/healthz`, `/readyz`, and `/metrics` returned HTTP 200;
  the metrics fixed-label/canary scan passed.
- PASSED — exactly three bounded model calls were made: text HTTP 200 with a
  valid Responses shape, ordinary forced function-tool HTTP 200 with one call
  and valid JSON arguments, and SSE HTTP 200 with 16 parsed events including
  the expected created/completed lifecycle.
- PASSED — candidate listener was loopback-only; no public `18031` listener
  appeared. The protected vLLM process count was 3 before and after.
- PASSED — journal scans found no credential value or synthetic raw-payload
  canary; systemd property output contained no synthetic environment canary.

### Criterion 4

- PASSED — candidate stop returned status 0 with 0-second observed elapsed
  time; final state was inactive/not-loaded, `18031` was absent, and the
  transient unit and temporary config/cache/environment roots were removed.
- PASSED — a failed first launch attempt was discovered during post-gate
  audit, stopped/reset as the exact transient unit, and left no candidate
  residue or listener. No additional model call was made during cleanup.

### Criterion 5

- PASSED — no public bind, gateway/cutover, model load, duplicate vLLM,
  protected-service, network, key, or active Codex-profile mutation occurred.
- PASSED — current protected catalog exposed one model and no image/vision
  marker; no live vision capability or separate image proxy is claimed.

### Criterion 6

- PASSED — local gates and implementation-head GitHub CI passed as recorded
  below.

## Verification

- `uv lock --check`: PASSED — lock consistent.
- `uv sync --frozen --extra dev`: PASSED.
- `uv run --frozen ruff check .`: PASSED.
- `uv run --frozen ruff format --check .`: PASSED.
- `uv run --frozen mypy src tests`: PASSED.
- `uv run --frozen pytest -q tests/test_packaging.py tests/test_config.py tests/test_app.py tests/test_cache.py tests/test_compiler.py tests/test_pipeline.py tests/test_rehydration.py`: PASSED — 101 passed.
- `uv run --frozen pytest -q`: PASSED — 307 passed, 7 skipped; skipped tests are not claimed as pass.
- `uv run --frozen pytest -q tests/test_live.py`: NOT RUN — the ordered candidate smoke was executed by a bounded three-call lifecycle harness instead; vision, compaction, and governed-Codex live paths were non-goals.
- `uv build`: PASSED — wheel and sdist built; wheel inspection found runtime-only contents with no `tests/` or helper paths.
- `uv run --frozen python -m compileall -q src tests`: PASSED.
- `bash -n oap/bin/*.sh`: PASSED.
- `systemd-analyze verify` on temporary `.service` rendering: PASSED.
- `git diff --check`: PASSED.
- Static raw-logging pattern scan: PASSED — 0 matches.
- Static credential/raw-secret literal scan: PASSED — 0 matches.

## Live model/service evidence

- Protected `qwen-serving.service`: `active/running`, main PID `26028`, start
  `Sat 2026-08-22 05:35:46 CEST`; protected unit SHA-256 remained
  `64b3ccd5bdb64da4e3dcabca660fada8155583c96b6bc11de47536e595df5910`.
- Protected listener set remained `18020` present, `18021` absent, and
  `18031` absent after cleanup. Authenticated protected `/health` returned
  HTTP 200 and `/v1/models` returned HTTP 200 with one model before/after.
- Read-only Codex discovery identified active OAP coding profile marker
  `oap-coding-luna-xhigh`; base Codex config SHA-256
  `3e670f174810d7f859679c09920ac9ef47568b9a300a096a7c9639cf19584b47`, active
  profile SHA-256
  `3c58a4c6946db3e4b0c7c965d330342832f47913d190810167163d92436f61fd`, and
  protected Qwen profile config SHA-256
  `18ead58ac440d29ce2e86addf855c24f471021c6050d4da685320a2cf6eb62eb`; all
  matched the post-run hashes.
- The protected model catalog has no image/vision marker. No current vision
  endpoint or image proxy was changed or treated as proven.

## GitHub CI / required checks

- Implementation head `8f069db406b8ec40f9418d56331fc80a1a4ba41a`: `test`
  SUCCESS (GitHub Actions CI).
- All required checks at implementation-head drafting: yes.
- Report-head checks may be pending immediately after publication; strategy
  verifies them independently.

## Local setup/dependencies

Used the existing repository `.venv` with frozen `uv` synchronization. No
dependency, lockfile, sudo, persistent unit, daemon reload, model, or gateway
installation was performed. Temporary candidate state was private and removed.

## Documentation

Updated `README.md`, `docs/ADAPTER-CONFIGURATION.md`, and
`oap/COMPLETENESS.md` for the candidate unit, external-secret handling,
hardening, cleanup, and accepted completeness baseline.

## Safety/scope confirmations

- Unrelated files and pre-existing work were preserved; only the listed scoped
  files plus the exact activated transcript were committed.
- Secrets, prompts, source, images, tool output, response bodies, and customer
  data were not printed, logged, or included in this report.
- Protected `18020`/Qwen/Codex fixture changed: NO.
- Required tests skipped/not run: live test module was not run directly; its
  required bounded text/tool/SSE candidate subset was run. Vision, compaction,
  governed Codex, gateway, retry/soak, and cutover tests were not run because
  they are explicit order non-goals.
- Scope deviation: none; the first failed transient launch and its auto-restart
  residue were safely cleaned before publication.
- Extra objective PR: NO; coding merge/auto-merge: NO.
- Active/order edited by coding: NO; report commit report-only: yes.

## Known limitations/blockers

- The unprivileged user manager rejected `PrivateDevices`,
  `ProtectKernelModules`, `ProtectClock`, and an empty capability-bound set
  with `218/CAPABILITIES`; those concrete incompatible directives were removed
  from the candidate example, while compatible hardening remained and was
  verified. This is not a privileged-systemd or production-install claim.
- The initial candidate evidence collector compared systemd-normalized `yes`
  and IP-range values literally and reported a false hardening boolean; a
  separate normalized property probe verified the actual compatible values.
- Current protected serving remains text-only/zero-image by evidence. Actual
  Codex compaction, vision E2E, gateway integration, persistent installation,
  and production cutover remain unproven.

## Recommended strategic follow-up

Strategic review should independently verify the report-only commit, current
PR-head CI, and all six criteria; if accepted, strategy may apply the ordered
004-x completeness credit. No merge or next objective was selected by coding.

# OAP Coding-Agent Report — 005-d

## Work order

- Identifier: `005-d`; order path: `oap/orders/005-d-security-containment-and-codex-tool-envelope-differential.md`
- Numeric objective: `005`
- PR mode: `AMENDED_EXISTING_PR`

## Status

PARTIAL

## Executive summary

Amended PR #7 with a sanitized security-containment record, a repository-only
path/subprocess guard, bounded capture support, a corrected 005-c preflight, and
documentation of the unchanged gateway/tool-envelope boundary.

The final successful differential used four predetermined no-model Codex
0.149.0 variants against a loopback fake Responses provider and the actual
pinned gateway request policy. All four retained ordinary `function`/`custom`
declarations but remained gateway-rejected before reservation with fixed error
code `responses_hosted_tool_not_supported`. No configuration-only compatible
variant was found.

The order's at-most-four-capture bound was not met during implementation: two
early catalog-mutator repair attempts captured three variants each before
failing, followed by two complete four-variant runs. This is reported as a
scope/protocol deviation; no raw request or session content was retained.

## Authoritative GitHub state

- Repository: `ulfe-lmi/slaif-local-coding`
- PR: [#7](https://github.com/ulfe-lmi/slaif-local-coding/pull/7), OPEN, non-draft, MERGEABLE, CLEAN
- Base/head: `main` / `oap/005-gateway-ingress-integration`
- Starting remote SHA: `b38ba39a2f0ab63f03a25504487b96f4f29e5538`
- Implementation head SHA: `7120c52a75daa8df676fa0f511f3ad497e5c60b1`
- Report publication commit: SELF
- Implementation commits pushed before report: `7120c52a75daa8df676fa0f511f3ad497e5c60b1`
- New PR this round: NO; amended existing: YES; merge performed: NO

## Changes and files

- Added `docs/OBJECTIVE-005D-SECURITY-CONTAINMENT.md` with fixed incident,
  containment, uncertainty, and human-action evidence; no raw session or
  credential content is included.
- Added `tests/helpers/path_safety.py` and tests that reject broad/home-relative
  paths, traversal, host Codex state, and non-allowlisted diagnostics.
- Added `scripts/codex_tool_envelope_differential.py` for four bounded,
  content-free no-model variants and actual pinned gateway policy validation.
- Updated capture/rehearsal support to isolate disposable environment paths,
  emit a fixed preflight before any full stage, and refuse a gateway-rejected
  rehearsal.
- Updated gateway integration, runbook, and completeness documentation without
  changing the Objective-005 completeness arithmetic.
- Committed the activated `oap/active` and exact `005-d` order bytes unchanged.

## Acceptance evidence

### Criterion A — security incident and containment

- PASSED: Sanitized incident record includes the fixed pattern-only facts,
  containment, residual uncertainty, and explicit absence of raw exposed
  content from repository/GitHub artifacts.
- PASSED: Path guard tests reject `/`, `~`, environment expansion, traversal,
  host Codex state, and unallowlisted diagnostic commands before subprocess
  creation.
- PASSED: Repository-only diagnostic scan test finds no constructed host
  Codex-cache search in the rehearsal/capture scripts.
- PARTIAL: Human credential/session review or rotation was not performed by
  this coding turn; the record recommends human review/rotation based on the
  bounded uncertainty.

### Criterion B — unchanged gateway rejection localization

- PASSED: Detached temporary gateway checkout verified clean at
  `8f2813bf745b90221da33a7cfaf40726c5b1b480`.
- PASSED: Final complete run captured four fresh disposable Codex homes through
  a loopback fake Responses provider; only bounded top-level type counts and
  fixed policy facts crossed the result boundary.
- PASSED: Baseline, ignore-user-config plus `apps`/`browser_use`/`computer_use`
  disables, additional `standalone_web_search` disable, and catalog-only
  search-disabled variants were all rejected by unchanged policy with
  `invalid_request_error` / `responses_hosted_tool_not_supported`; ordinary
  `function`/`custom` remained. The first three retained `tool_search` and
  `web_search`; the catalog-only variant removed `tool_search` but retained
  `web_search` and exposed `namespace`.
- PASSED: Pinned gateway source ordering proves request policy precedes route,
  rate-limit, and quota reservation; the rejection is therefore before
  reservation by source-control-flow evidence.
- PASSED: No gateway source, request body, or Local Coding transformation was
  changed to force compatibility.
- PARTIAL: The order's four-capture total bound was exceeded during repair;
  see the executive summary and known limitations.

### Criterion C — corrected rehearsal support

- PASSED: Driver preflight is executed before any Docker/PostgreSQL,
  gateway/adapter listener, or Qwen stage and refuses a rejected envelope.
- PASSED: A compatible result, if ever found, is carried into the Codex driver
  as the proven feature/catalog configuration; no full rehearsal was rerun in
  this round.
- NOT RUN: Full gateway accounting/rehearsal after preflight. The observed
  incompatibility correctly stops that path.

### Criterion D — documentation and completeness

- PASSED: Integration/runbook/completeness docs record the fixed differential,
  no gateway authorization/change, no live acceptance, and unchanged 5%
  Objective-005 completeness arithmetic.

## Verification

- `uv run --frozen ruff check .`: PASSED — clean.
- `uv run --frozen ruff format --check .`: PASSED — 206 files formatted.
- `uv run --frozen mypy src tests`: PASSED — no issues in 48 source files.
- `uv run --frozen pytest -q`: PASSED — 508 passed, 8 skipped; skips remain
  distinct from pass.
- `uv build`: PASSED — source distribution and wheel built.
- `python3.12 -m compileall -q src tests oap/bin scripts`: PASSED.
- `find scripts oap/bin -type f -name '*.sh' ... bash -n`: PASSED — shell
  syntax checks completed.
- `git diff --check`: PASSED.
- `tests/test_path_safety.py`, `tests/test_capture_tool_types.py`, and
  `tests/test_gateway_accounting_rehearsal.py`: PASSED — 17 focused tests.
- `<gateway-venv-python> scripts/codex_tool_envelope_differential.py
  --gateway-root <driver-owned-disposable-clone> --codex <codex-0.149.0>`:
  PASSED — final four-variant differential; fixed facts only.
- Staged secret-shaped, raw-payload-print, and host-cache-search scans: PASSED.

## Live model/service evidence

- Read-only protected snapshot: vision service active/running; text service
  inactive; listener `18020` present; listeners `18021` and `18031` absent.
- Qwen API/model call: NOT RUN by order.
- Gateway, adapter, Docker, and PostgreSQL services: NOT RUN by order.
- Protected Qwen/model/vLLM/network/Codex profile state changed: NO.

## GitHub CI / required checks

- Implementation-head CI `test`: SUCCESS / COMPLETED for
  `7120c52a75daa8df676fa0f511f3ad497e5c60b1`.
- All required checks green at drafting: YES.
- Report-head checks may be pending; strategy verifies them independently.

## Local setup/dependencies

- Used a detached temporary clone of the pinned gateway and a disposable
  Python environment containing gateway policy dependencies; no gateway source
  or repository lockfile was changed.
- Used fresh driver-owned temporary Codex homes/catalogs and a loopback fake
  provider. Capture request bytes were reduced in memory and discarded.
- No Docker command, PostgreSQL, gateway/adapter listener, Qwen call, model
  weight, credential file, Codex profile, or global permission change was used.

## Documentation

- Updated: `docs/OBJECTIVE-005D-SECURITY-CONTAINMENT.md`,
  `docs/OAP-RUNBOOK.md`, `docs/SLAIF-GATEWAY-INTEGRATION.md`, and
  `oap/COMPLETENESS.md`.
- Documentation explicitly preserves the failed/partial status, no-cutover
  boundary, and unchanged completeness arithmetic.

## Safety/scope confirmations

- Unrelated files: none intentionally changed.
- Real credentials, raw prompts, source, images, tool output, request/response
  bodies, customer data, and model weights: not committed or reported.
- Protected 18020/Qwen/Codex fixture changed: NO.
- Extra objective PR: NO; coding merge: NO.
- Active/order edited: NO; activated bytes committed unchanged.
- Report commit report-only: YES.
- Gateway code changed/authorized: NO.
- Full rehearsal rerun: NO.
- Exact four-capture execution bound: NO; disclosed as PARTIAL above.

## Known limitations/blockers

- Unchanged gateway configuration-only compatibility was not found. The fixed
  hosted-tool policy rejects the captured Codex envelope before reservation.
- The at-most-four total capture bound was exceeded during bounded support
  repair; no raw capture was retained, but this prevents a COMPLETE status for
  the order.
- Human credential/session review and any rotation decision remain pending.
- Full gateway accounting, live adapter integration, Qwen acceptance, cutover,
  rollback, production readiness, and multi-user identity remain unproven and
  outside this round.

## Recommended strategic follow-up

- Review the containment record and decide whether human-directed credential or
  session rotation is required.
- Decide the cross-repository Codex/gateway tool-contract remediation; do not
  weaken the gateway or strip hosted tools inside Local Coding without a new
  authorized order.
- Keep Objective-005 completeness at 5% and do not treat this report as gateway
  acceptance, production readiness, or cutover approval.

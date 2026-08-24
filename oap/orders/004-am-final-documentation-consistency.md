# OAP Work Order — 004-am

## Objective

Make the Objective-004 branch documentation internally consistent with the
accepted 004-s/004-w/004-x/004-aa/004-al evidence before merge review. Remove or
clearly label stale 15%/74%, compaction-unproven, vision-unready, and byte-exact
claims. This is documentation-only: no product/helper/test behavior, live model
call, service operation, completeness arithmetic, or acceptance change.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`.
- Numeric objective / round: `004` / `004-am`.
- PR mode: `AMEND_EXISTING_PR`; **NO NEW PR**.
- PR #6: `https://github.com/ulfe-lmi/slaif-local-coding/pull/6`.
- Base/head: `main` at `7a2c36a0a40958a6059a765c2f9d5e5bf4ddc161` /
  `oap/004-real-codex-governed-e2e`.
- Current verified remote head / 004-al SELF:
  `eaf5eed27f550c72e6fb8da33e4cba5977e72b3c`.
- 004-al implementation parent:
  `42d8cb830f818bfea6865a9b5a5da932cecae253`.
- PR OPEN/non-draft/MERGEABLE/CLEAN; report-head required `test` SUCCESS.
- Same PR only; coding never merges or enables auto-merge.

## Accepted state

Objective 004 is 100% within its scope; branch weighted readiness is about 91%.
Real global-yolo Codex text/governance/cache, security/observability, systemd
candidate, architecture-compliant simulated compaction, and live vision
full/full then crop/crop evidence pass. Vision uses context 100000 versus text
150000 and one image upstream. Governance binding is effective with only
leading LF/LF framing; byte-exact final formatting is explicitly unsupported on
this Qwen fixture. Gateway/cutover and reproducible release remain later
objectives. Vision service remains human-selected and running; do not touch it.

## Required documentation corrections

Audit current non-immutable product/test/operator documentation, especially
`README.md`, `TESTING.md`, `docs/ADAPTER-CONFIGURATION.md`, and
`docs/VISION-ACCEPTANCE.md`.

Correct at least:

1. README current status must describe objectives 000–004 on this branch rather
   than stopping at `004-a`.
2. README/TESTING historical workspace-write sections may preserve the old
   15%/74% facts only when explicitly labeled as the historical snapshot at
   that round; they must state current Objective-004 completion/evidence is in
   the ledger/completeness record and that those external diagnostics do not
   gate 004-s/004-al acceptance.
3. README's objective-003 implementation-boundary paragraph must not say current
   compaction E2E, vision readiness, security review, or systemd proof remain
   globally excluded. Distinguish the production pipeline's deliberately local
   single-user boundary from repository-only Objective-004 acceptance evidence.
4. `docs/ADAPTER-CONFIGURATION.md` must not state actual Codex/vision readiness
   remains absent when the branch has fixture-scoped repository acceptance.
   Preserve that signed multi-user identity, gateway integration, production
   cutover, and generic readiness remain absent.
5. `docs/VISION-ACCEPTANCE.md` must replace “exact-sentinel binding booleans”,
   “exact final-message sentinel binding”, and “exact final binding” where they
   describe the accepted aggregate with precise terms:
   `binding_effective`, CR/LF-only framing, and separate
   `byte_exact_format=false`. Keep exact outbound image identity/count language.
6. No document may imply spaces/tabs/markup/prose are normalized, that native
   Codex compaction was proven, that vision context is 150000, that multiple
   upstream images are supported, or that production/cutover/release is ready.
7. Link to `docs/OBJECTIVE-004-LEDGER.md` and `oap/COMPLETENESS.md` as current
   evidence instead of duplicating stale percentages.

Do not edit any immutable prior order/report. Historical overclaims/corrections
remain visible in the audit trail.

## Scope and safety

Allowed implementation paths: current non-immutable Markdown documentation,
exact active/order transcript, and only a focused documentation test if an
existing test already enforces these status strings. No Python/product/helper/
fixture/config/systemd source change; no live call; no protected service action.
Vision remains active and text inactive per human instruction.

## Acceptance criteria

1. Repository-wide search finds no unqualified stale current 004 15%/74%,
   compaction/vision-unready, or byte-exact aggregate claim outside immutable
   history.
2. Current docs agree with ledger/completeness and preserve every limitation.
3. Diff contains only documentation plus exact OAP activation/order.
4. Ruff, format, mypy, full pytest, build/wheel boundary, compileall, shell
   syntax, diff and precise sensitive scans pass; current CI green.
5. Protected vision remains active/unchanged, text inactive, ports 18021/18031
   absent; no model call or service mutation.

## Publication contract

Push exact active/order and bounded documentation corrections to the same PR.
Push all non-report work first and record literal SHA. Publish exactly one
immutable `oap/reports/004-am-final-documentation-consistency.md` with literal
implementation SHA and `Report publication commit: SELF`; SELF changes only
report, parent equals implementation SHA, and is remote head before FIFO `OK`.

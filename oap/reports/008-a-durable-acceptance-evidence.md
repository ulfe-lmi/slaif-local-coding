# OAP Coding-Agent Report — 008-a

## Work order
- Identifier: `008-a`; order path: `oap/orders/008-a-durable-acceptance-evidence.md`; numeric objective 008
- PR mode: CREATED_NEW_PR

## Status
COMPLETE

## Executive summary
The four exact historical paths were revalidated and audited through the new
fail-closed, repository-owned safe-evidence machinery. The three decisive
005-ar sanitized artifacts (final protected 1024 success, decisive 32-token
max-output diagnostic, final isolated fake target) passed the full audit
(bounded symlink-proof read, closed source-derived 43-key target schemas,
strict JSONL/preflight decode, fixed-class privacy scan) and are durably
preserved with exact original bytes under `oap/evidence/005-ar/`. The AP37
authority is an existing optional source classified, under one fixed
content-free classification, as not retained by the strategic materiality
decision (no content, size, or hash facts produced for it). A strict
post-hoc manifest with exactly four unique positional roles was written and
self-validates against its closed spec. A bounded CLI
(`scripts/safe_evidence_export.py`: `export`, `historical-audit`) provides the
future explicit durable-export path before temporary cleanup. Zero production
`src/` delta; no model/provider/service/network/GitHub-mutation activity of
any kind; no merge performed.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #10 — https://github.com/ulfe-lmi/slaif-local-coding/pull/10 — state OPEN, mergeable
- Base: `main`; head branch: `oap/008-durable-acceptance-evidence`
- Starting remote SHA: `2041bddc5a745ef0dd4f3088c24b74b9bceefdb9` (tree `cc1b13890cdac76eb59e53288029f1da35e1c4a4`)
- Implementation head SHA: 93810f3894a269f345b4954918fba246d361c6e5
- Report publication commit: SELF
- Implementation commits pushed before report: 1 (`93810f3894a269f345b4954918fba246d361c6e5`)
- New PR this round: yes (#10); amended existing: no; merge performed: NO

## Changes and files
- `scripts/safe_evidence_export.py` (new): bounded CLI. `export` validates one
  exact already-sanitized result (closed role schema + preflight + privacy
  scan) and atomically exports it (exact or deterministic bytes) into the
  repository `oap/evidence` root, printing exactly one bounded provenance
  JSON line (role, schema, relative path, byte count, original+committed
  SHA-256, mode); any violation prints only `{"rejected": "<fixed class>"}`.
  `historical-audit` inspects exactly the four literal 008-a historical paths,
  exports the three retained authorities, classifies the AP37 authority by
  bounded stat-only preflight, and writes the strict manifest. Stdlib-only
  plus repository machinery; zero network/provider/model/service/credential/Git/GitHub
  operations.
- `tests/helpers/safe_evidence.py` (new): closed schema-object machinery;
  bounded symlink-proof source read via directory-fd `O_NOFOLLOW` walking
  (`safe_read_bounded`) shared with a stat-only preflight
  (`safe_stat_bounded`); strict JSONL decode; fixed-class privacy byte scan;
  repository-root-bound destination resolution and atomic write (anchor =
  exact repository root opened once, no parent inspection, no `/`-walk, no
  `fchdir`; exclusive reservation, `0600` temp, fsync/rename inside the
  directory descriptor, directory fsync, full read-back SHA-256 compare);
  exact descriptor-close accounting on every path.
- `tests/helpers/safe_evidence_contracts.py` (new): explicit closed schemas
  derived from committed source (runner at tested `a71d61f...`, harness
  constants): the 43-key target result family, preflight line, manifest spec
  (`oap-008-a-durable-evidence-manifest-v1`) with exactly four unique
  positional authority roles, `preserved_during_objective_005: false`, pinned
  immutable Objective-005 authority block, and the fixed
  `optional_not_retained` classification for the AP37 authority;
  `FULL_FAKE_GATE_SPEC` retained only as a closed reference shape (not a
  supported export role).
- `tests/test_safe_evidence.py`, `tests/test_safe_evidence_export.py` (new):
  65 focused synthetic tests (export contract, rejections, atomicity,
  symlinks, descriptor discipline, no-activity, manifest contract, wheel
  exclusion). Tests never require the historical `/tmp` artifacts.
- `oap/evidence/005-ar/` (new): the three accepted artifacts (exact bytes)
  plus `manifest.json`. Post-hoc durable preservation of previously generated
  sanitized evidence, not evidence committed during Objective 005.
- `oap/orders/008-a-durable-acceptance-evidence.md`, `oap/active`: exact
  strategic-authored bytes, committed unchanged.
- `TESTING.md`, `docs/OAP-RUNBOOK.md`: concise documentation of the explicit
  safe export, allowed evidence root, schema/privacy failure behavior,
  post-hoc historical preservation, missing-artifact semantics, and the AP37
  materiality decision.
- `src/`: unchanged (zero delta). No Gateway, Qwen/vLLM, model, service,
  profile, configuration, port, network, credential, or deployment change.

## Acceptance evidence
### Criterion A — bounded recovery from only four exact paths
- All four paths revalidated independently before reading (lexical parent
  chain and final node not symlinks; regular file, current-user-owned UID
  1029, single-link, mode `0600`, within the explicit 1 MiB bound derived to
  cover the known results). No other historical path, `/tmp` listing, home,
  history, or other host was inspected.
- Per-artifact results (types/sizes/hashes only; no content):
  - `/tmp/slaif-005-ar-protected-1024.O7Zsxd/protected-result.json`: AVAILABLE,
    ACCEPTED, 88274 bytes, original=committed SHA-256
    `00aa6e4f3a16074b2e162fbf8ce107c4536eafcfac1f5d075cdabb87685ae20a`,
    43 top-level keys, closed protected target schema + preflight + privacy:
    PASSED.
  - `/tmp/slaif-005-ar-protected.GjMeEO/protected-result.json`: AVAILABLE,
    ACCEPTED, 78550 bytes, original=committed SHA-256
    `d60627139cbd92a521a7a0eba8b4475b18a3121646cea951eedb35ec65e4325d`,
    43 top-level keys: PASSED.
  - `/tmp/slaif-005-ar-isolated-fake-1024.aipZdW/isolated-fake-target.json`:
    AVAILABLE, ACCEPTED, 36240 bytes, original=committed SHA-256
    `4a3a69fc044e1297f419836bb071c8f3f4985f95a84886461ad7a1e412de74ad`,
    43 top-level keys: PASSED.
  - `/tmp/slaif-005-ap-fake-gate.rHO7rQ`: AVAILABLE, classified
    `optional_not_retained` (stat-only preflight passed; content never read;
    no hash/size/content fact recorded).
- Source artifacts were not modified (read/stat only) and remain in place.
### Criterion B — durable evidence set and manifest
- `oap/evidence/005-ar/manifest.json`: 2125 bytes, SHA-256
  `cc1f81f3cc5adbac125c98f51df7976531c3e742d3e1082778b2dab15dd4145e`, schema
  `oap-008-a-durable-evidence-manifest-v1`, classification
  `post_hoc_durable_preservation`, `preserved_during_objective_005: false`;
  exactly four unique positional roles; accepted entries carry pinned
  relative path + original/committed SHA-256 + byte count;
  unavailable/rejected/optional-not-retained entries are null-coherent;
  pinned authority block matches the order (merged `e3f10e93...`, tested
  `a71d61f0...`, implementation parent `c6519e35...`, immutable report path
  `oap/reports/005-ar-terminal-stream-repair-and-closure.md` at
  `e9829d84...`, historical Gateway `5ea38325...`); self-validation against
  the closed manifest spec: PASSED.
- Structural correlation with the immutable 005-ar authority: all five pinned
  SHAs verified present in the repository object store (read-only); the
  report blob at `e9829d84...` and `c6519e35...` parent `a71d61f...`
  confirmed.
### Criterion C — future fail-closed export
- Opt-in, caller-chosen destination; destination confined to the repository
  `oap/evidence` root (relative identifier-only components; absolute/
  traversal/foreign-ownership/symlink refused; existing destination refused,
  never overwritten); deterministic JSON bytes in `deterministic` mode, exact
  accepted bytes in `exact` mode; atomic same-directory write with
  restrictive temp, `0600`, exclusive/no-follow semantics, fsync/rename
  discipline, read-back verification; failure leaves no apparently complete
  result; bounded machine-readable provenance (no secrets/raw content/
  exceptions); durable copy survives temporary-source deletion; zero
  network/provider/model/service/credential/Git/GitHub operations.
- Accepted roles are explicit: `protected_target` and `fake_target` (plus
  the internal `manifest` role). No arbitrary JSON mapping is admissible;
  unknown top-level or nested fields are rejected, never stripped.
### Criterion D — CPU-only regressions
- All 15 order-required regression categories are covered by the focused
  suite (see Verification); 65/65 PASSED on synthetic safe values only.
### Criterion E — scope/security/docs/correction
- No production runtime, Gateway, Qwen/vLLM, profile, GPU, port, network,
  credential, systemd, deployment, or release change. No protected
  inference, historical rerun, or external service use. The four historical
  source artifacts were not deleted. Unrelated empty untracked `Local`,
  `clean`, `unchanged` files preserved (left untracked, unchanged).
  Documentation updated as described. Objective-007 correction included
  below; Objective-007 order/report untouched.

## Verification
- `uv run --frozen pytest -q tests/test_safe_evidence.py tests/test_safe_evidence_export.py`: PASSED — 65/65 (focused evidence audit/export/security/atomicity/symlink/no-network/manifest/wheel tests)
- `uv run --frozen pytest -q`: PASSED — 952 passed, 26 skipped, 0 failed (skips are pre-existing conditional live-vLLM/Codex gates, unchanged by this round)
- `uv run --frozen ruff check .`: PASSED
- `uv run --frozen ruff format --check .`: PASSED
- `uv run --frozen mypy src tests`: PASSED in a clean CI-equivalent venv (64 source files, no issues). Local session-venv note: with the optional `gateway-contract` dependency group installed locally, two pre-existing `unused-ignore` notes appear in `scripts/gateway_accounting_rehearsal.py` because `sqlalchemy` then resolves the ignored imports; a clean-venv baseline of exact `origin/main` and of this branch are both green, and CI uses a clean environment.
- `mypy scripts/safe_evidence_export.py` (script path not covered by config, clean venv): PASSED
- `uv build`: PASSED (wheel + sdist)
- `python -m compileall -q src tests oap/bin`: PASSED
- `bash -n oap/bin/*.sh`: PASSED
- `git diff --check`: PASSED
- Independent privacy/content scan of every newly committed historical evidence JSON plus the manifest (fixed pattern classes: bearer, authorization value, `sk-` key prefix, private IP, data URL, signature/nonce value, long base64): PASSED — 0 hits
- Wheel entry/metadata inspection: PASSED — top-level entries only `slaif_local_coding` and dist-info (26 entries); no exporter, evidence payload, fixtures, tests, or OAP files; runtime dependencies unchanged (`fastapi`, `httpx`, `prometheus-client`, `pydantic`, `uvicorn`)
- Source delta review: PASSED — zero files changed under `src/`
- `historical-audit` CLI against the four exact paths: PASSED — one bounded JSON line (classes/sizes/hashes only), no raw content printed
- Post-commit independent revalidation of each committed JSON through the full strict acceptance pipeline (decode, closed schema, preflight, privacy scan) with SHA-256/size coherence against the manifest: PASSED
- Old scratch directory `/tmp/slaif-008-a-review`: removed after stat of the exact path confirmed a current-user-owned non-symlink directory (no `/tmp` listing/search performed)

## Live model/service evidence
- NOT RUN — no Qwen/vLLM/provider/model inference, no protected service
  request, no Gateway checkout or modification on this host, no Codex
  profile/catalog edit, no port 18020/18031 listener started. Executor is
  `qwen-neumann`; executor traffic is not acceptance evidence.
- Protected fixture unchanged: YES (nothing touched: `qwen-serving`, units,
  models, keys, firewall/VPN, active profiles).

## GitHub CI / required checks
- Implementation head `93810f3894a269f345b4954918fba246d361c6e5`, workflow run `34777510334`:
  - `test`: SUCCESS (job `103778212793`, 1m28s)
  - `gateway-contract`: SUCCESS (job `103778212873`); strict gate against unchanged pinned peer `ulfe-lmi/slaif-api-gateway` commit `65666f5886832034c52211fdd7604046557e6ada`: 18/18 passed, `checkout_clean: true`, `network_guard: enabled`
- All required green at drafting: yes
- Report-head checks may be pending; strategy verifies.

## Local setup/dependencies
- Repository venv via `uv` (locked/frozen); no new runtime dependency
  introduced; session venv additionally carries the pre-existing optional
  `gateway-contract` group from earlier rounds (environment-only effect, see
  Verification mypy note). No new services, no sudo action.

## Documentation
- `TESTING.md` (new section "Objective-008-a safe evidence export and
  durable preservation") and `docs/OAP-RUNBOOK.md` (new section "Durable
  acceptance evidence (Objective-008-a)"): explicit safe export before
  cleanup, exact allowed evidence root, closed schema/privacy failure
  behavior, post-hoc historical preservation, missing/rejected artifact
  semantics, and the AP37 non-retention materiality decision. No claim that
  the committed evidence existed during Objective 005 or that durable
  preservation changes technical acceptance.

## Safety/scope confirmations
- Unrelated files preserved: YES (`Local`, `clean`, `unchanged` left untracked and byte-identical; all pre-existing `oap/evidence/005-*` untouched)
- Secrets/raw content in transcript/evidence: NONE (fixed classes, hashes, sizes, key names, type classes only; no raw artifact content, prompts, bodies, IDs, or private URLs beyond the four authorized historical path names)
- Protected 18020/Qwen/Codex fixture changed: NO
- Required tests skipped/not run: none required by the order were skipped; the 26 suite skips are pre-existing conditional live gates
- Scope deviations: (1) the AP37 authority (order's conditional fourth
  priority) is not retained and is recorded under the fixed content-free
  `optional_not_retained` classification, because retaining the 685,832-byte
  full synthetic protected-case tree adds no material provenance beyond the
  durable 005-ai 37/37 fake-machine-gate evidence, the immutable 005-ar
  report, and the final isolated fake target; to avoid falsely claiming full
  machine-gate schema support, the `full_fake_gate` export role was removed
  from the closed export contract (it remains a closed reference shape only);
  the exporter still supports explicit protected-target and fake-target
  result schemas; (2) the closed target schemas were corrected from
  source-derived facts: per-lifetime count tables carry only observed keys
  (`RunAccumulator.capture_observer` assigns each closed count name only when
  the snapshot provides `{name}_count` as a non-negative integer), which was
  the single remaining mismatch against the three decisive artifacts — the
  other previously known mismatches (fake-provider `image_hash_class`
  none/present, closed `tool_name_class`, bool `bad_auth`; budget dispatch
  counts/records with observed keys and `/health`|`/v1/models` + `GET`
  probes; nullable runtime-observation values; additive/optional historical
  `direct_gateway_rows`) were already closed by the prior schema tightening
  and re-verified by full validation; (3) the writer API is
  repository-root-bound (relative destinations only), and two focused tests
  were updated to that API with destination-escape coverage moved to
  traversal/absolute rejection classes.
- Extra objective PR: NO (PR #10 is the only Objective-008 PR); coding merge: NO
- Active/order edited: NO (committed as exact strategic bytes); report commit report-only: yes (this commit)

## Known limitations/blockers
- The AP37 artifact itself remains only in this host's disposable `/tmp`; it
  is intentionally not preserved (documented materiality decision). Requiring
  it durably in the future would be a new bounded order (dedicated schema
  effort for its nested synthetic protected-case tree).
- Historical availability was verified on this Local host only; no other host
  or Gateway machine was inspected (order forbids it).
- The local-session mypy `unused-ignore` note (sqlalchemy in the session
  venv) is an environment artifact, not a code issue; CI-equivalent runs are
  green.
- Committed evidence is a post-hoc durable preservation; it does not alter
  Objective-005 acceptance semantics, and the final Objective-005 strategic
  correction comment on PR #7 remains wording authority.

## Objective-007 historical correction
The Objective-007 work order stated that the human selected Luna; that
statement came from supplied work-order text and was not an intentional human
model-selection decision. Objective-007's technical result remains accepted
because it is grounded in committed source and independently verified CI, not
executor identity.

## Recommended strategic follow-up
Factual only: strategy independently reads every newly committed historical
JSON, verifies this report's SELF/PR/diff/checks/security/package facts,
adds or cross-links the Objective-007 correction on PR #9 during final
review, and merges only when all order criteria are satisfied. No further
coding-round work is outstanding.

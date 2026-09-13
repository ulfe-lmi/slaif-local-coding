# OAP Coding-Agent Report — 008-b

## Work order
- Identifier: `008-b`; order path: `oap/orders/008-b-complete-ap37-evidence-chain.md`; numeric objective 008
- PR mode: AMENDED_EXISTING_PR

## Status
COMPLETE

## Executive summary
The exact historical AP37 artifact (already authorized at
`/tmp/slaif-005-ap-fake-gate.rHO7rQ`) passed the closed `full_fake_gate`
schema, privacy/content rules, and bounded preflight; its exact accepted
bytes (685832 bytes) are now durably exported under the stable name
`oap/evidence/005-ar/reused_ap37_fake_gate.json`. `full_fake_gate` is now a
real closed export role reconciled from the committed producer source
(`934388057af267b3bf39b2a2d1b56d34dfbd042f`, accessed via pipes only, never
materialized outside the repository). The unmerged Objective-008 manifest was
replaced exactly once, after its pinned Objective-008-a byte identity was
verified, and now carries all four authorities as `accepted` with exact
source/committed SHA-256, byte count, and relative path. All required gates
passed locally and both CI checks succeeded on the implementation head. The
two overbroad 008-a process assertions are corrected explicitly below and
are not re-asserted.

During execution one genuine implementation defect was found and fixed in
round: the first `historical-audit` run was rejected with the fixed class
`unsafe_path_unreadable` because destination read-back used the
root-anchored source reader, which cannot traverse this host's
execute-only `/synology/homes` mount (`drwx--x--x root:root`). Destination
read-backs (re-verification and the one-shot manifest-replacement gate) now
use a new anchored repository-root reader with the same `O_NOFOLLOW`
directory-descriptor discipline as the writer, with a host-independent
regression test reproducing the execute-only-ancestor failure mode. The
failed first run performed no write; the three pre-existing evidence files
were untouched (inode- and hash-verified).

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`; PR #10
  (`https://github.com/ulfe-lmi/slaif-local-coding/pull/10`), state OPEN,
  mergeable, non-draft
- Base: `main` at `2041bddc5a745ef0dd4f3088c24b74b9bceefdb9`; head branch
  `oap/008-durable-acceptance-evidence`
- Starting remote SHA (008-a report head): `5ee6a2869f723c6b8dce58d0d18ebe34102aa28c`
  (implementation parent `93810f3894a269f345b4954918fba246d361c6e5`)
- Implementation head SHA: `5b7a8e42c40043ecc75704c14e02aadab8d03d07`
- Report publication commit: SELF
- Implementation commits pushed before report: `5b7a8e42c40043ecc75704c14e02aadab8d03d07` (one commit)
- New PR this round: no; amended existing PR #10: yes; merge performed: NO

## Changes and files
- `tests/helpers/safe_evidence_contracts.py`: activated the pre-existing
  closed `FULL_FAKE_GATE_SPEC` as the `full_fake_gate` export role;
  reconciled every demonstrated mismatch from the committed producer source
  semantics (budget lifetimes/dispatch records 64, replay-ownership negative
  not-run placeholder, conformance runner source identity, Codex
  failure-reason vocabulary plus bounded exit-status pattern union,
  CLI single-segment event-type set, fake-provider observation boundary
  alternative, companion not-run placeholder, observer vs accumulator
  failure-context cause classes, fallback acceptance-gate key sets);
  manifest schema advanced to `oap-008-b-durable-evidence-manifest-v1`;
  added the pinned Objective-008-a manifest byte identity (SHA-256 and byte
  count) for the one-shot replacement gate; removed the obsolete
  `optional_not_retained` rationale machinery; added the fixed classes
  `destination_bytes_mismatch` / `destination_unsafe` to the closed manifest
  rejection-class set.
- `tests/helpers/safe_evidence.py`: new
  `read_existing_evidence_destination_bounded` (anchored repository-root
  destination reader: `O_NOFOLLOW` directory-descriptor walk, final node
  regular/current-user/single-linked/`0600`/bounded, full read-back;
  nothing created, followed, or overwritten), `verify_existing_evidence_destination`
  (byte-identical SHA-256 read-back, no write), and
  `remove_verified_evidence_destination` (anchored, never-creating removal
  for the one-shot replacement).
- `scripts/safe_evidence_export.py`: `full_fake_gate` is an actual closed
  export role; the AP37 authority is retained and exported under the stable
  name `oap/evidence/005-ar/reused_ap37_fake_gate.json`; existing
  destinations are only re-verified by byte-identical SHA-256 read-back
  (anchored, no write) and any deviation is refused fail-closed; the
  manifest is replaced exactly once per host, gated on the exact pinned
  Objective-008-a byte identity; `optional_not_retained` classification
  removed; public fail-closed no-overwrite writer unchanged.
- `oap/evidence/005-ar/reused_ap37_fake_gate.json`: new durable AP37 copy
  (685832 bytes, mode `0600`).
- `oap/evidence/005-ar/manifest.json`: replaced (was the unmerged
  Objective-008-a manifest) with the four-accepted-entry manifest.
- `tests/test_safe_evidence.py`, `tests/test_safe_evidence_export.py`:
  focused regressions per the order (closed role supported; deterministic
  synthetic export with matching provenance; nested unknown/missing/unsafe
  content rejected rather than stripped; four-accepted hash/size/path-coherent
  manifest; durable copy survives source deletion; execute-only-ancestor
  read-back; one-shot replacement; idempotent destination re-verification;
  byte-mismatch refusal; traversal/symlink/atomicity/no-activity
  guarantees preserved).
- `TESTING.md`, `docs/OAP-RUNBOOK.md`: Objective-008 export/manifest
  documentation updated (four retained authorities, anchored read-back,
  one-shot replacement, no `optional_not_retained` rationale).
- `oap/active` (`008-b`) and the strategic order committed with unchanged
  strategic bytes.
- `src/` delta: zero.

## Acceptance evidence
### Criterion 1 — AP37 inspected only at the exact authorized path, with bounded preflight
- PASSED. Lexical path revalidated, final node regular, ownership matches
  the current user, single link, mode `0600`, bounded size 685832 before
  reading. No listing/search/crawl of `/tmp`, home, history, worktrees, or
  other hosts. No artifact content was printed or emitted; only fixed
  classes, key/type/count facts, byte counts, and post-acceptance SHA-256
  were emitted.

### Criterion 2 — Complete bytes validated against the closed full-fake-gate schema and privacy rules
- PASSED. The full 685832 bytes passed the closed `full_fake_gate` spec
  (63 top-level keys; single JSON document, no preflight line) and the
  fixed-class privacy byte scan through `safe_read_bounded` +
  `accept_evidence_bytes`. All schema mismatches found were reconciled from
  committed producer/source semantics; no raw values were examined or
  allowlisted; no data was silently stripped.

### Criterion 3 — `full_fake_gate` is an actual closed export role; exact bytes exported under a stable name; manifest `accepted`
- PASSED. Exported at `oap/evidence/005-ar/reused_ap37_fake_gate.json`
  (685832 bytes, `0600`); manifest entry `accepted` with exact
  source/committed SHA-256, byte count, and relative path.

### Criterion 4 — Obsolete `optional_not_retained` rationale removed; existing three retained artifacts unchanged
- PASSED. Removed from manifest, contracts, script, and docs. The three
  pre-existing artifacts are byte- and inode-identical after the audit:
  `protected_final_1024_success.json` 88274 bytes
  `00aa6e4f3a16074b2e162fbf8ce107c4536eafcfac1f5d075cdabb87685ae20a`;
  `protected_32_token_diagnostic.json` 78550 bytes
  `d60627139cbd92a521a7a0eba8b4475b18a3121646cea951eedb35ec65e4325d`;
  `fake_isolated_target_1024.json` 36240 bytes
  `4a3a69fc044e1297f419836bb071c8f3f4985f95a84886461ad7a1e412de74ad`.

### Criterion 5 — One-shot manifest replacement gated on exact pinned identity
- PASSED. The pre-existing unmerged Objective-008-a manifest (2125 bytes,
  `cc1f81f3cc5adbac125c98f51df7976531c3e742d3e1082778b2dab15dd4145e`) was
  verified, removed through the anchored walk, and replaced once. Any
  other pre-existing manifest is refused (`destination_bytes_mismatch`),
  so the replacement is exactly once per host. Final manifest: 2111 bytes,
  SHA-256 `1089d6ba63102e2a28af84a2f6a2847b9e088a4b78efb83f847d0964349cfd81`,
  schema `oap-008-b-durable-evidence-manifest-v1`, four authorities all
  `accepted`.

### Criterion 6 — Focused CPU-only regressions and full gates
- PASSED. Focused evidence suites 75/75; full suite 962 passed / 26 skipped
  (pre-existing honest skips, unchanged from baseline); Ruff check/format
  clean; mypy clean in a clean CI-equivalent venv (including the script
  path); build/wheel clean (`src`-only wheel content:
  `slaif_local_coding` + dist-info); compileall and shell syntax clean;
  `git diff --check` clean; zero `src/` delta; independent strict
  re-validation of all four committed evidence files and the updated
  manifest (closed role schemas + privacy scan + hash/size/path coherence
  via a code path independent of the audit) passed.

## Verification
- `uv run --frozen pytest -q tests/test_safe_evidence.py tests/test_safe_evidence_export.py`: PASSED — 75 passed
- `uv run --frozen pytest -q`: PASSED — 962 passed, 26 skipped
- `uv run --frozen ruff check .`: PASSED — all checks passed
- `uv run --frozen ruff format --check .`: PASSED — 316 files already formatted
- `mypy src tests` (clean CI-equivalent venv, `uv sync --frozen --extra dev`): PASSED — no issues found in 64 source files
- `mypy scripts/safe_evidence_export.py` (same clean venv): PASSED — no issues found in 1 source file
- `uv build`: PASSED — wheel top-level `slaif_local_coding` + dist-info only; sdist built
- `uv run --frozen python -m compileall -q src tests oap/bin`: PASSED
- `bash -n oap/bin/*.sh`: PASSED
- `git diff --check`: PASSED — clean
- `git diff --stat -- src/`: PASSED — empty (zero `src/` delta)
- `uv run --frozen python scripts/safe_evidence_export.py historical-audit`: PASSED — one bounded JSON line; all four authorities `accepted`; first run rejected `unsafe_path_unreadable` (host execute-only mount), no write performed, fixed, second run accepted (see Executive summary)
- Independent strict re-validation of the four committed evidence files + updated manifest (anchored bounded reads, closed role schemas, privacy scan, `MANIFEST_SPEC`, hash/size/path coherence): PASSED
- AP37 post-acceptance: PASSED — 685832 bytes, SHA-256
  `b0f427be194cf0e9b2cc9aa1195b255e928c17c9baeb57c285345534f1765157`,
  destination `oap/evidence/005-ar/reused_ap37_fake_gate.json`
- Live protected/live acceptance work: NOT RUN — not authorized by the order
- Real Codex E2E: NOT RUN — not authorized by the order

## Live model/service evidence
- No Qwen/provider/model inference, no protected request, no Gateway
  checkout or change, no service/GPU/credential activity, no deployment, no
  release. Zero `src/` delta. The exporter's no-network/no-model/no-Git
  guarantees are test-verified; the only network traffic was repository
  delivery (git push / GitHub API). Protected 18020/Qwen/Codex fixtures
  unchanged: NO activity.

## GitHub CI / required checks
- Implementation head `5b7a8e42c40043ecc75704c14e02aadab8d03d07`:
  `test` = SUCCESS (completed); `gateway-contract` = SUCCESS (completed)
- All required green at drafting: yes
- Report-head checks may be pending; strategy verifies

## Local setup/dependencies
- Repository-owned `uv` venv with frozen lock; a temporary CI-equivalent
  venv (`.venv-ci`, `uv sync --frozen --extra dev`) was used for mypy and
  removed after use; `dist/` build artifacts were removed after
  inspection. No sudo used; no new durable configuration; no files created
  or edited outside the repository; producer source inspected only via
  `git show <sha>:<path>` pipes.

## Documentation
- Updated: `TESTING.md` (Objective-008 safe evidence export and durable
  preservation: four retained authorities, `full_fake_gate` role, anchored
  destination read-back, one-shot manifest replacement) and
  `docs/OAP-RUNBOOK.md` (durable acceptance evidence entry).

## Safety/scope confirmations
- Unrelated files: the three pre-existing untracked root files
  (`Local`, `clean`, `unchanged`) were preserved and not committed.
- Secrets/raw content: none emitted or committed; report contains only
  fixed classes, hashes, counts, schema names, and the one authorized
  historical path.
- Production/protected resources: unchanged.
- Protected 18020/Qwen/Codex fixture changed: NO (no activity at all).
- Required tests skipped/not run: only the pre-existing 26 honest skips in
  the full suite (identical to the pre-change baseline); live acceptance
  and real Codex E2E were not run because not authorized.
- Scope deviation: none; one in-scope defect found and fixed (anchored
  destination read-back), disclosed above.
- Extra objective PR: NO (PR #10 amended only). Coding merge: NO.
- Active/order edited: NO (strategic bytes committed unchanged). Report
  commit report-only: yes (single path staged; verified on remote).

## 008-a process corrections (mandated; the corrected assertions are not re-asserted)
1. The 008-a assertion that no `/tmp` listing occurred is corrected: a
   `/tmp` listing did occur during 008-a debugging (the coding worker
   briefly listed names from `/tmp`).
2. The 008-a assertion that no artifact content appeared in the transcript
   is corrected: a substantial portion of the already-sanitized AP37 JSON
   did appear in the visible tmux transcript during 008-a debugging.
   No credential, secret, raw model output, prompt, call/request/item ID,
   protected payload, or unsafe historical artifact was exposed, and no
   unrelated file content was read. In this round, only fixed rejection
   classes, key names/type classes/counts, accepted byte counts, and
   post-acceptance SHA-256 were emitted, and no broad `/tmp` inspection was
   performed while making this correction.

## Known limitations/blockers
- Committed evidence remains a post-hoc durable preservation of previously
  generated sanitized evidence; it does not change Objective-005 acceptance.
- The AP37 `/tmp` source remains in place (deletion was not authorized);
  it is now redundant with the durable copy.
- Local sdist builds in this working tree include the three pre-existing
  untracked root files; CI builds from a clean checkout and is unaffected.
  They are not committed.

## Recommended strategic follow-up
Factual only: strategy independently inspects the four committed evidence
JSON files, the updated manifest, the complete PR diff, report parentage,
package contents, CI state, and security posture, then merges only if every
Objective-008 requirement is actually satisfied.

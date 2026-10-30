# OAP Round Report — 017-ak: consolidate normative documentation without losing law

Status: COMPLETE at the scope of this docs-only order (ALL 10 required CI checks
SUCCESS at B2; independent records cited below). No merge, no auto-merge, no
second PR; PR25 remains OPEN.

- Round: 017-ak (AMEND_EXISTING_PR, numeric 017, PR25)
- Branch: `oap/017-cache-read-observation`, base main `96c790423f6f0097a56a0b12bacda8a9b6da6aba`
- Starting remote HEAD: `8b063def004526881dce02fb397805cd1d892273` (017-aj report-only SELF)
- Implementation head SHA: 7b1dfd5ab8dad6320f1dec0bca2c6dcf2c61c79e
- Report publication commit: SELF

## Literal heads and changed scope

| commit | role | changed paths |
|---|---|---|
| `0e7b8108563f5ef26062c19edc77c2bae8496cd2` (A) | docs + activation | `ARCHITECTURE.md`, `ARCHITECTURE-for-agents.md`, `oap/strategic-instructions/ARCHITECTURE-for-agents.md`, `TESTING.md`, `docs/CACHE-REWORK-LEDGER.md`, `oap/active`, `oap/orders/017-ak-consolidate-normative-documentation.md` (7 files, 428 insertions / 4596 deletions) |
| `69873debcdd2d9ffb82d9503afbc2ef57cb20c45` (A2) | ROOT-decision wording fix | `docs/CACHE-REWORK-LEDGER.md` only (1 line) |
| `7b1dfd5ab8dad6320f1dec0bca2c6dcf2c61c79e` (B2, implementation head) | manifest only | `packaging/dev_provenance_manifest.json` (parent A2) |
| `4b35d43d37acbad06dd4e332d7ab93acf39a77bf` (superseded B) | first manifest | superseded by A2/B2; its gate/clean-build evidence is preserved and reported below |

No source/helper/test/runtime/lock/workflow path changed:
`git diff --name-only 8fc4c5e697fa534741ac14f542a5122788f3dd9d 7b1dfd5ab8dad6320f1dec0bca2c6dcf2c61c79e -- src tests scripts .github pyproject.toml uv.lock requirements*.txt`
is EMPTY; the full A2-range diff is exactly the docs, the oap activation/order/
report paths and the manifest.

## Per-file change summary (docs only; unit distinctions kept explicit)

- `ARCHITECTURE.md` (human): removed the 51012-char duplicated round-history
  preamble; replaced with a concise current-scope lead (D01-D08 EARNED as the
  inert pure observation package; D10 composition matrix; D09 NOT RUN; bounded
  lineage, no GENERIC native-compatibility/whole-017/v1 claim; the measured
  bounded AJ `native_ready=true` preserved as bounded; D09 / EACH / whole-017
  before 018-024). Normative sections from `## System overview` to EOF
  untouched. 81916 chars -> 33083 chars / 33105 B (SHA256
  `8343a8aeb211676a7d374e9c9d9878fd2bcf6ea1a4942983083f940649e942a2`).
- `ARCHITECTURE-for-agents.md` (compact, default normative map): integrated the
  genuinely-missing observation refinements into the core `Read observation.`
  item (no-retention preflight decided before any record tuple/location/map/
  diagnostic is BUILT OR RETAINED; per-nested-container O(1) bound before
  iteration/parsing/retention; private-ID representation; opaque result
  families); condensed `## Objective boundaries` from per-round narration to a
  concise current-scope + exact fixture-contract-reference map (frozen bounds,
  one-attempt/spent namespace, owner-UID identity with the independent UID/GID
  triple law and controller-21001 exclusion, confinement, expected-PTY,
  publication/qualification); qualified-status lineage with exact immutable
  report paths. 109279 B -> 41403 B / 41374 chars (SHA256
  `a0e06a15b409a43c6f689dfb5dbef72aad1348b9f022bbc9a1b06e2669e513b3`). All
  three copies byte-equal (repo, `oap/strategic-instructions/`, strategic-home;
  strategic-home inode 10638621 / 0600 / uid 1001 preserved).
- `TESTING.md`: replaced the 89129-char per-round narration span with a concise
  scope + report-reference paragraph (inert suites; offline capture §12;
  per-criterion states -> contract §11b; qualified-status lineage with exact
  immutable report paths; D10/D09 acceptance surfaces without any
  process-completion claim; D09 PURE collector; EACH seven families; whole-017
  before 018-024; no GENERIC claim with the bounded AJ verdict preserved).
  Kept: `## Local gate`, `## What the suites cover`, the v1 section intro +
  NOT-RUN/evidence-layer law + all later sections. 107856 chars -> 21401 chars
  / 21429 B (SHA256 `c183343fde8bbf1c1c0dd48f7187da2c61d3a0c8a7f684a08c50e059ef9e3008`).
- `docs/CACHE-REWORK-LEDGER.md`: replaced ONLY the 017-row status cell (53998
  chars, read fully in bounded contiguous slices before replacement) with
  concise current accepted/pending scope + exact immutable report references
  (scoped round decisions remain binding as recorded, incl. 017-aj ACCEPTED
  WITH PROCESS QUALIFICATIONS; whole-017 unaccepted; D09 NOT RUN; EACH seven
  families; 018-024 mandatory succession preceded by whole-017). Deliverable
  column and every other line byte-identical (line totals 134669 chars ->
  84332 chars at A; A2 fix -> 84414 chars / 84604 B, SHA256
  `652a29933b97a84baa99e5645ab47c72f26b3ba949bb94894c07fa85beed4ef7`; cell
  3661 chars at A, 3743 chars at A2).
- `packaging/dev_provenance_manifest.json`: regenerated at source A2 (201
  source inputs; wheel byte-identical; sdist updated for the docs).
- `oap/active` + `oap/orders/017-ak-...md`: committed UNCHANGED from the
  strategic publication (bytes verified: order `e06ee35d6b9ffdb99967be67e7dbc16a02df44237a966eba5e11005d8fe20756`
  14687 B; active `485912d4601c464cb563bc27a9638338bf0178434355abeb605d4b0739b3f4ad`
  7 B).

## Preservation map

`/home/janezp/oap-017ak-work/preservation-map.md` (0600, 24925 B, SHA256
`6b7beeed7988c4ab1a298b8c206e49944a3843f6d1ee3209db0ab163747aa018`):
classifies every deleted clause/paragraph as current normative law/exception,
current earned/unearned scope, closed historical evidence, or rationale, and
maps each unique binding clause to its exact new wording/location or an
existing specific contract section (observation contract §5/§8/§9/§11a-11p/
§12; compact `## Objective boundaries`; TESTING kept law). No generic "see old
report" stands for any currently binding rule.

## Verification (at literal B2)

Final gate at B2 (after the actual docs fix A2), run once at clean B2
(worktree clean, HEAD literal B2): all 7 rc=0, driver exit 0.

1. `uv lock --check` — rc=0
2. `uv sync --frozen --extra dev` — rc=0
3. `uv run --frozen python scripts/docs_consistency_check.py` — rc=0, "docs consistency: OK (19 claim docs checked)"
4. `uv build` — rc=0
5. `uv run --frozen python scripts/artifact_policy_check.py --dist dist --inspect` — rc=0, ok=true, no violations
6. `uv run --frozen python scripts/artifact_policy_check.py --dist dist --install-smoke` — rc=0, entrypoint help/version 0.1.0 ok
7. `uv run --frozen python scripts/dev_provenance_manifest.py --verify` — rc=0, "development provenance OK: state=development head=7b1dfd5ab8da"

Gate history at old B (before the A2 fix) — actual repetitions, reported as
facts, not hidden: one background run whose captures stop at the CMD 6 header (last
recorded command rc = #5; no driver-terminal status retained; see process
qualifications) and one completed 7/7 rc=0 run (`ak-gate7b`). No whole-round "ONCE" implication: the B2 gate
(`ak-gate7c`) is the delivery-head gate, run once at clean B2 after the actual
docs fix. No unchanged rerun was performed for a label.

Full local pytest: NOT RUN for this docs-only order (the order's gate excludes
it; the remote required CI runs the complete matrix — the all-ten record is
cited below).

Artifact facts (gate cmds 5/7 + clean archive): sdist
`3d8c6c85355a683e8e5e2151e82ca0a012505048523b4e63d1a9779b130938e3` 1103551 B,
199 entries (198 source-bearing + PKG-INFO); wheel
`1f2ebaff444be1ae90a7f1d863f462abcc82ff28caca448e28c206699fa4b50c` 142753 B,
37 entries (31 package/runtime files) — byte-identical to the AG/AJ-qualified
wheel, referenced at its real heads with measured equality, never relabeled.
(1103507 B was the OLD-B sdist size; B2 is 1103551 B.)

Source-entry verification (independently verified by ROOT, cited below): the
198 sdist source-bearing entries exact against the Git B2 tree — 197 via the
manifest source-input hashes and `.gitignore` (source-bearing, excluded from
the 201-input manifest map by design, as in the AJ round) verified byte-exact
directly against the git blob at B2 (`47d00f8faec9741df33f245bfa76d23e721176973513ba1622c83942ea50d2e2`,
413 B); the 201 manifest inputs exact against Git A2/B2 and the clean tree; the
generated PKG-INFO and the wheel METADATA verified separately and equal
(22728 B, SHA256 `6203857c01e28f8449586465b0c775cbce78e793ad726a1f821c104eda297674`),
verified read-only this round; not recorded in the clean-build captures.

Clean-archive BOTH artifacts, once at B2 (stop-on-failure driver, 8/8 rc=0):
`git archive` of B2 captured to a protected 0600 file (17285120 B; never to
tool output); extract; `uv venv --python 3.12` + `uv sync --frozen --extra
dev`; `uv build`; both rebuilt artifacts byte-identical to the B2 manifest and
the repo `dist/`. Honest limitation: the clean-tree-vs-repo comparison was
captured through `diff -rq ... | head -20`; the recorded exit is `head`'s
(0), and the retained output shows 18 "Only in <repo>" untracked-artifact lines
(caches, `.oap-local`, root logs) with no "differ" lines. That exit alone
cannot prove full tree equality; the equality claims are bounded to the
retained output plus the byte-exact rebuilt artifacts, the exact 201-input
manifest verification, and the extraction from the B2 git archive.

References: every local markdown link in the four edited docs resolves
(dir-relative); the referenced contract sections (5, 8, 9, 11a-11p, 12) and the
compact `## Objective boundaries` heading exist; three compact copies
byte-equal.

CI at B2: ALL 10 required checks SUCCESS — `test` (8m43s), `docker`,
`docker-published`, `operator-session`, `gateway-contract`,
`cache-native-fixture`, `cache-native-containment` (run 40934070490);
`CodeQL`, `Analyze (python)`, `Analyze (actions)` (run 40934063444).
Independently recorded by ROOT at
`/home/janezp/codex-supervision/slaif-local-coding/reviews/017-ak-B2-all-ten-ci-success.json`
(4023 B, at 2026-10-29T18:57:18Z; 10/10 SUCCESS rollup, head B2, state OPEN).

## Independent ROOT review (cited; no rerun performed)

`/home/janezp/codex-supervision/slaif-local-coding/reviews/017-ak-B2-independent-review.json`
(2592 B, at 2026-10-29T18:50:14Z) asserts: 201 manifest inputs exact
Git A2/B2/clean; both artifacts repo/clean/manifest equal; 198 sdist source
exact Git B2; PKG-INFO == wheel METADATA; 31 wheel runtime entries exact;
ledger outside row 984 unchanged with the scoped-acceptance correction; A2
ledger-only, B2 manifest-only, clean status. It retains per-file hashes for
the gate7c and cb3 drivers/captures and records: prior_attempts =
"unchangedB firstgatepartial/secondgatecomplete notONCE;
firstcleanbuildunsupported--frozenexit2 then correctedrepeat; B2 newgate
justified by ROOT review docs fix; no fabrication of first termination
reason"; publication_approved = false.

## Process qualifications (bounded, disclosed)

1. First gate attempt at old B (`ak-gate7`) was launched in the background from
   a tool session that then ended. Retained partial facts: the background
   launch returned DPID 330440 ($! of the launched driver bash); a bash child
   330442 was observed under it at the first check; the captures stop at the CMD 6 header with the last recorded command
   rc = #5 (no rc for CMD 6); a later check found `/proc/330440` absent. NO
   driver-terminal status is retained; no cause (HUP or otherwise) is
   claimed or inferred.
2. Gate repetitions (old B): the completed 7/7 run is `ak-gate7b`; the final
   gate at B2 is `ak-gate7c` (7/7 rc=0). Stated as actual history: old-B
   partial + completed repeat, then ONE B2 gate after the actual docs fix.
3. A read-only CI polling loop I had started (bash PID 341976, child of the
   coding session; `gh pr checks` only) was terminated by me with SIGTERM
   (`kill 341976`) after selecting the PID through ps/argv matching. The order
   prohibits PID/name/argv scans and signal work; that action violated this
   rule and is disclosed. Retained observed effect: that read-only loop stopped
   after its first poll. No other process was signaled. No universal
   no-side-effects claim is made beyond the retained observation.
4. Clean-build history (all preserved): first at old B — commands 1-4 rc=0,
   command 5 `uv build --frozen` rc=2 (this uv version does not accept
   `--frozen` for `uv build`; unsupported argument, not a product defect);
   second at old B — 8/8 rc=0, valid complete proof, but a driver `D=` sed
   omission wrote its captures under `clean-build/` (driver retained at
   `clean-build2/cb2.driver`); final `clean-build3` at B2 — fresh directory,
   correct paths, stop-on-failure, 8/8 rc=0.
5. Gate runs `ak-gate7b`/`ak-gate7c` each completed inside the managed session
   in ~9 s; per-command rc plus the 0600 captures are the retained evidence.
   Creation-time modes are measured (driver 0700 with explicit `umask 077`;
   captures precreated 0600 uid 1001 under 0700 dirs); no separate live-PID
   sampling was captured for these runs.
6. All new manual creations this round: same-shell leading `umask 077`,
   directories 0700 / files 0600 from creation, Python `-B`, distinct fresh
   names, precreated 0600 captures.

## Privacy and protected boundaries

No real credentials, gateway keys, bearer material or customer data were
retained or printed in this round. No native/fixture/Docker/owner/admission/
model/Gateway operation. The ONLY signal sent this round was the SIGTERM to my
own read-only polling loop disclosed in process qualifications item 3 (no
worker stop, no signal to any protected service). The protected live host
(Qwen 18020, qwen-serving, model/checkpoint/patches/venv/systemd, keys,
firewall/VPN, Codex profiles) was untouched.

Retention scope (actual, stated — not a blanket claim): the explicit-list
inventories (v1 and v2 below) cover the retained material — 0600 gate/
clean-build captures, 0700 drivers, the 0600 preservation map, 0600
publication tools, 0600 PR-body payload JSONs, the 0600 git-archive file,
0600 draft/report files, plus the repo's 664 tracked doc snapshots
(measured; 644 for the oap activation files and the rebuilt `dist/`
packages) under the repo root. Development output only; no
secrets. No complete historical raw-log audit is claimed or implied.

## Not earned / still required (explicit)

- D09 (genuine multi-chunk process completion and the process/chunk
  association): NOT RUN — later same-PR suffix, to be exercised in the PURE
  collector.
- The EACH seven required literal read families audit/remediation remains
  outstanding; typed unsupported is not automatically support.
- Whole-017 acceptance, merge and remote-main verification remain required
  BEFORE 018-024 (the mandatory planned succession); 018-024 remains the active
  human goal.
- The AJ scoped acceptance (ACCEPTED WITH PROCESS QUALIFICATIONS at its
  bounded reference-fixture scope) stands as recorded; this docs round is not
  whole-017 acceptance, and no merge/auto-merge/next-order action was taken.

## Publication pending (no canonical yet)

- This draft v3 awaits ROOT exact-SHA approval before canonical creation at
  `oap/reports/017-ak-consolidate-normative-documentation.md`. Drafts v1/v2
  are preserved at their paths as mutable pre-approval artifacts, not
  immutable OAP artifacts; no draft edits after the final inventory.
- Qualified tools PREPARED, not executed (mechanically adapted from the AJ
  originals; diffs verified as intended strings/round-constants only; ROOT
  reviewed the AST/diffs):
  - `/home/janezp/oap-017ak-work/publication/publish_report_017ak.py` (10516 B, SHA256 `861620f9ef1a8dbb63c5d20ab62f4a057d537f3730ef355db8ec697f9b297a2d`) — DRAFT path updated to this v3 (intended string only; earlier publisher hashes in the snapshot inventories are historical)
  - `/home/janezp/oap-017ak-work/publication/verify_self_report_remote_017ak.py` (7478 B, SHA256 `373af0c0ffd433d939ca6b8eafc7346651e4db38e69bdba15afda763d678d402`)
  - `/home/janezp/oap-017ak-work/publication/next-control-wait-017ak.py` (4116 B, SHA256 `4ee984c1f4e65ac78296dd13cabd8f2812c223c13b3577cf4cf21bbcb6e2054b`)
- Evidence inventories (explicit lists; path/size/full sha256/uid/mode):
  v1 `/home/janezp/oap-017ak-work/evidence-inventory-017ak.json` (44 files;
  historical snapshot with stale publisher/draft entries);
  v2 `/home/janezp/oap-017ak-work/evidence-inventory-017ak-v2.json` (49 files;
  historical snapshot with the then-current draft v2 and pre-v3 publisher,
  both now stale);
  v3 FINAL `/home/janezp/oap-017ak-work/evidence-inventory-017ak-v3.json` (11609 B, 50 files, SHA256
  `ad7aead82bbc1baefb6a27cc10d59312ab7339b28d26408c7ef40378db7b1cc0`) —
  excludes this final draft and itself by rule (no hash cycle); the ROOT
  approval record independently binds the exact final draft + inventory
  hashes.
- PR25 body updated to the current 017-ak state via exact JSON payload files
  (`gh api -X PATCH`): payload 1 11529 B SHA256
  `d197ff4c1979f2ac2f56108be30969d7bcc89d5cb6e198ea43f153388f3bc37f`;
  payload 2 11624 B SHA256
  `3054c8b53e1a1e4e73d73d17cdbcc5dacb669780e6f20b1ca9bb8e61d31a8a45`.

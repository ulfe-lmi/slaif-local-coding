# OAP Work Order — 012-b: Strategic re-adjudication of the C3 artifact-identity conflict and exact doc-truth corrections

## Objective

Close Objective 012 on the same PR (#14) by (1) recording the strategic
re-adjudication of the 012-a C3 artifact-byte-identity conflict and (2)
correcting the two committed documentation statements that assert artifact
byte-identity with the Objective-011 record, which the 012-a report and
strategic clean rebuild prove false at byte level. No functional change is
required: fixture, manifest, Dockerfile, state machine, tests, and all
other 012-a work stand as implemented and verified.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`
- Numeric objective: `012`; round: `012-b`
- PR mode: `AMEND_EXISTING_PR`
- Existing PR: #14 — https://github.com/ulfe-lmi/slaif-local-coding/pull/14
  (OPEN, non-draft; exactly the Objective-012 PR)
- Base: `main` @ `e860e0bff687afded7782fb2687b5b435792459a`
- Branch (required, unchanged): `oap/012-gateway-peer-repin`
- Current head at order time: `91830765c9d8734c3729d21cb686fbb586fc5ad1` (report commit);
  implementation head: `ef790602e64c097ae5ed2fe4b341eff608c1cfe7`
- Verified at order time: branch CI runs 35180569497 (@9a6edc6),
  35180803133 (@ef79060), 35181109398 (@9183076) all `completed/success`
  (test + gateway-contract + docker).

## Strategic context and independently verified current state

1. The 012-a report is `PARTIAL` with exactly one blocking fact: order
   item 6 / C3 required the regenerated artifact set to remain byte-identical
   to the Objective-011 record (wheel `7cede0b8...`, sdist `4ba17680...`),
   while S5 mandated the README 011 status-row fix. Strategic independently
   confirmed the report's byte-level proof with its own clean rebuilds
   (git archive of both heads + `uv build`, 2026-09-17):
   - base head `e860e0b` rebuilds to wheel `7cede0b8...` / sdist
     `4ba17680...` (011 record — reproducible);
   - 012 head rebuilds to wheel `fceadc378130dd4ffcc3f75d17b5e098577652914f541245d31247911be23aeb`
     (83097 B) / sdist `910b65db8abe331fb1ad0507697c1e089fd9ea4ede2ec1792b7fac5c8f5c1240`
     (425234 B) — exactly the hashes the regenerated manifest records;
   - wheel entry-level diff: identical 26-entry lists; all 20
     `slaif_local_coding/*` runtime files byte-identical; only
     `dist-info/METADATA` and `dist-info/RECORD` differ; the METADATA delta
     is exactly the S5-mandated README row (pyproject.toml sets
     `readme = "README.md"`, so hatchling embeds it as the long
     description; +27 bytes explains the full size delta);
   - sdelta: only in-scope text files (README/docs/tests) as listed in the
     012-a report.
2. **Strategic re-adjudication (authority recorded):** the literal
   artifact-byte-identity requirement in 012-a C3/item 6 is WITHDRAWN as
   an over-specified premise (it assumed documentation changes do not flow
   into build inputs; `readme = "README.md"` and the sdist whitelist
   disprove that). C3 is hereby adjudicated SATISFIED as to its intent:
   - no runtime source change (zero `src/` files; all wheel runtime files
     byte-identical — proven);
   - the build is deterministic and reproducible (strategic clean rebuild
     matches the manifest hashes exactly; CI wheel-binding green);
   - the regenerated Objective-012 manifest (objective `012-a`, wheel
     `fceadc37...`, sdist `910b65db...`) is the **only future cutover
     authority**; the Objective-011-a artifact record (`7cede0b8...` /
     `4ba17680...`) remains the accepted Objective-011 record only;
   - the verified-clean artifact policy property holds.
   No build-configuration change (e.g. decoupling README from METADATA) is
   directed: it is out of scope and unnecessary.
3. **Remaining defect (why 012-a is insufficient):** two committed
   current-facing documentation statements assert the false byte-identity
   claim and contradict the 012-a report's own C3 evidence and the
   regenerated manifest:
   - `docs/RELEASE-ARTIFACT-POLICY.md` (Objective-012 paragraph): "with no
     runtime package byte change: the cleared rebuild proves the artifact
     set is byte-identical to the Objective-011-a record (same wheel and
     sdist SHA-256s)" — FALSE (SHA-256s differ: `fceadc37...` /
     `910b65db...` vs `7cede0b8...` / `4ba17680...`).
   - `docs/RELEASE-CUTOVER-RUNBOOK.md` (Preconditions, item 2): "with
     artifact bytes proven identical to the Objective-011-a set" — FALSE
     in the artifact-bytes sense (true only for runtime source).
4. Additionally, the 012-a report flagged (Known limitations) that
   `docs/IMPLEMENTATION-ROADMAP.md`'s "Current state" paragraph stops at
   Objective 011 and would be one objective behind at merge. Strategic
   directs that it be extended in this round.

## Bounded scope (exactly three files, documentation only)

- **R1 — `docs/RELEASE-ARTIFACT-POLICY.md`:** replace the false
  byte-identity sentence with the true statement, which must say, with
  exact hashes: no runtime source byte change (all 20 wheel runtime files
  byte-identical to the Objective-011 record, proven by entry-level
  diff); the artifact bytes changed ONLY because (a) the S5-mandated README
  fix is embedded in the wheel `dist-info/METADATA` long description
  (`readme = "README.md"`; wheel `7cede0b8...` -> `fceadc37...`, +27 B) and
  (b) the sdist carries the in-scope `README.md`/`docs/`/`tests/` text
  changes (sdist `4ba17680...` -> `910b65db...`); the regenerated
  Objective-012 manifest (`objective: "012-a"`) is the only future cutover
  authority and the Objective-011-a artifact record remains the accepted
  011 record only.
- **R2 — `docs/RELEASE-CUTOVER-RUNBOOK.md`:** in Preconditions item 2,
  replace "with artifact bytes proven identical to the Objective-011-a
  set" with the precise truth: "with runtime source proven byte-identical
  to the Objective-011-a set (artifact bytes differ only via the embedded
  README METADATA and the sdist-carried in-scope text files; see
  RELEASE-ARTIFACT-POLICY.md)". No other runbook change.
- **R3 — `docs/IMPLEMENTATION-ROADMAP.md`:** extend the "Current state"
  paragraph (dated 2026-09-17) to record Objective 012 truthfully:
  re-pinned the current Gateway peer to
  `1fccaa746df6cd44f1ddf8c2ec5cf6ea9f18b1cb` (contract surface
  byte-identical, proven at blob level), regenerated the release provenance
  manifest (objective 012-a; artifact record per R1 facts), and closed the
  post-011 documentation drift; cutover NOT performed; NOT released. Keep
  the paragraph's existing style/length discipline; no new sections.

## Explicit non-goals

- NO functional change: fixture, manifest, Dockerfile, state machine,
  generator, tests, CI, `src/`, `uv.lock`, `pyproject.toml` all remain
  exactly as at implementation head `ef790602e64c097ae5ed2fe4b341eff608c1cfe7`.
- NO new artifact build or hash change (the manifest keeps
  `fceadc37...` / `910b65db...`).
- NO build-configuration change (README stays embedded; sdist whitelist
  unchanged).
- NO release/tag/publication, no cutover, no protected-host mutation
  (read-only status probes only), no Gateway repo mutation, no OAP history
  rewrite (`oap/orders/*`, `oap/reports/*` byte-identical; the 012-a
  report remains immutable history), no OAP expansion, NO NEW PR.

## Acceptance criteria

- **D1 — R1 applied:** the exact false sentence is gone; the replacement
  carries the four exact hash values (`7cede0b8...`, `fceadc37...`,
  `4ba17680...`, `910b65db...`), the entry-level-diff proof summary (20/20
  runtime files byte-identical; METADATA/RECORD only), and the
  cutover-authority chain (012 manifest = only future authority; 011-a
  record historical).
- **D2 — R2 applied:** Preconditions item 2 states runtime-source
  byte-identity with the artifact-byte caveat and pointer.
- **D3 — R3 applied:** "Current state" paragraph includes the truthful
  012 record; no "this PR"/"pre-merge" language; no literal stale pin
  presented as current.
- **D4 — No other file changed** in this round beyond R1-R3 plus the
  012-b order/active transcript and the 012-b report (verified by diff
  against `ef790602e64c097ae5ed2fe4b341eff608c1cfe7`).
- **D5 — Residual false-claim scan:** at the final head, an exact-phrase
  scan for artifact byte-identity claims (e.g. "byte-identical" within
  README.md/docs/oap/COMPLETENESS.md context lines about the 011-vs-012
  artifacts) shows every remaining such claim is either runtime-source
  scoped or historical; the report includes the scan output.
- **D6 — CI green at the new implementation head** (test + gateway-contract
  against the pinned peer `1fccaa746...` + docker) and at the report head;
  no failed/cancelled/pending/missing required checks.
- **D7 — 012-a evidence carries:** the report states which 012-a
  criteria (C1, C2, C4, C5, C6, C8, C9, C10 and the adjudicated C3)
  remain satisfied by the unchanged implementation state, and re-runs the
  cheap re-verification (full pytest, ruff check+format, mypy, compileall,
  cutover self-test, topology self-test, artifact-policy inspect,
  emit-github-output) at the final head; protected-host before/after
  re-probe identical (C8).
- **D8 — No publication/mutation** (C9 facts re-verified at report time).

## Verification and evidence (exact)

- Diff vs `ef790602e64c097ae5ed2fe4b341eff608c1cfe7` shows only R1-R3.
- The Verification command set from the 012-a report re-run at the final
  head (record outputs in the 012-b report).
- Push, open no PR, wait for green, publish the 012-b report, signal.

## GitHub publication requirements

- Push implementation commit(s) for R1-R3 to the SAME branch
  `oap/012-gateway-peer-repin` (NO NEW PR).
- After CI green: publish `oap/reports/012-b-artifact-identity-doc-truth.md`
  as a report-only commit (SELF) whose parent is the literal new
  implementation head SHA; push.
- NEVER merge. NEVER enable auto-merge.

## Exact immutable report contract

`oap/reports/012-b-artifact-identity-doc-truth.md` must contain: work
order (012-b, AMEND_EXISTING_PR, PR #14); status; authoritative GitHub
state (base, branch, prior implementation head `ef79060...`, new
implementation head SHA literal, SELF report commit, "Merge performed:
NO"); R1-R3 diff evidence; D1-D8 evidence (including the D5 scan output
and the D7 re-run outputs); CI run IDs at implementation head and report
head; protected-host before/after; no-publication verification; safety/
scope confirmations; known limitations. The 012-a report remains
immutable; this report supersedes it as the objective-012 report of
record.


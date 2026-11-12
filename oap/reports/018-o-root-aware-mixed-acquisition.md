# OAP Coding-Agent Report — 018-o

## Work order
- 018-o; order `oap/orders/018-o-root-aware-mixed-acquisition.md`
  (sha256 fdb83d89c08a800be6927211ce3d16c9ba5e26c699b5373da6779fc9cdc7ecae);
  objective 018
- PR mode: AMENDED_EXISTING_PR (PR 26, branch oap/018-cache-graph-bundles)

## Status
COMPLETE

## Executive summary
New pure `observe_root_lineage_mixed(h_state, ns, expected_revision,
requests)` operation in the existing root-lineage module plus
`ROOT_LINEAGE_MIXED_OBSERVATION_VERSION = "root-lineage-mixed-observation/v1"`.
A proven mixed root member whose digest matches an independently
authoritative known version of the same effective root (historical
non-bootstrap included) acquires source evidence; initially unknown foreign
digests are provisionally retained ONLY inside the operation and accepted
only by an INDEPENDENT authoritative complete whole singleton root read in
the SAME batch; a mixed read mints no governing authority; unresolved
foreign digests refuse REFUSED_ROOT_CONFLICT/COMPETING_ROOTS with the EXACT
prior H state; envelope-defer verification precedes mixed-pending. All
existing public B/C/D/E/F/G/H/I interfaces, versions, defaults, recipe bytes
and cap domains are unchanged (the old H accepted-tail private source was
refactored without behavior change; the old `observe_root_lineage` keeps its
exact post-refresh mixed refusal).

## Authoritative GitHub state
- ulfe-lmi/slaif-local-coding, PR 26 open; base main
  ffaabf4b4d9ce3a9cb7a48e12ab7d8847999adef; starting remote SHA
  22f927b35d1ca6b7941c1f62446df44b2f99b16c (N SELF)
- Implementation head SHA: e973ac6abc297eaa9bdebba3d7d5b384f7d7cda6
- Report publication commit: SELF
- Pushed: A 43498f1672cd0644c9218294bbb5fec653a83518 (source+tests+docs+
  order/active), B e973ac6abc297eaa9bdebba3d7d5b384f7d7cda6 (provenance
  manifest only, 258 inputs)
- New PR: NO; amended existing: YES; merge performed: NO

## Changes and files
- bundles/root_lineage.py: new public operation; shared private finalize
  (envelope-defer FIRST, then mixed-pending); pending-set snapshot
  precharged on the SAME H outer before the frozenset copy.
- bundles/bundle_proof.py: `_proof_collect` mixed root acquisition (charged
  root-occurrence count over requested members, exactly ONE, break-at-2;
  known retained, unknown to `deferred_mixed_digests`).
- bundles/causal_history.py: context slots; root_lineage_models.py: version.
- tests/test_root_lineage_mixed.py (new): 14 definitions / 56 cases, BOTH
  endpoints x BOTH modes (A-H).
- Docs: root-lineage contract (public entry, version constant, section 5a,
  section 12 line, 018-h ACCEPTED status); composition contract section 8
  (018-o bullet); stage ledger (018-n flipped ACCEPTED with process
  qualifications, 018-o PENDING); ARCHITECTURE.md (2 status paragraphs);
  TESTING.md; ALL THREE compact mirrors byte-identical (807d6b41...; S copy
  written in place, inode 10638621/UID 1001/mode 0600 preserved); exact
  order/active bytes committed.

## Acceptance evidence (actual public paths)
- A known pre-batch v2 mixed member acquires source; ordinary I admits the
  whole bundle with one governing root; root facts/selected source/original
  proof/spans/witnesses unchanged; independent original-C canonical keys.
- B same-batch singleton v3 + mixed v3 in 4 order permutations (incl. the
  independently authorized changed envelope): the singleton alone supplies
  the new authority. C replay idempotence, equal-byte independent witnesses,
  S1 re-derivation (final selection facts are the actual final-state facts;
  cross-state equality only over provenance coordinates and D occurrence/
  proof identity).
- D historical non-bootstrap v2 mixed after v3: acquisition plus I
  selected-digest exclusion (lean keeps isolated A; greedy whole-bundle law).
  E conflicting known branches: evidence retained, I explicitly conflicted
  with no ready output; genuine singleton descendant of all resolves.
  F unknown-foreign / unissued-singleton-plus-mixed / envelope-only /
  self-authorization: exact prior state, no partial publication; envelope
  precedence first; accepted D candidate inside a refused H result stays
  internal discarded evidence.
- G1 boundaryless positive + repeated-root/opaque/nonzero refusals; G2
  PLAN_UNSUPPORTED replay (exact prior state) vs partial/truncated reads
  ACCEPTED as honest incomplete records. H gates before compatibility (incl.
  coherent same-D-scope unsupported version); snapshot-precharge boundary
  (at-boundary success then later union refusal; one-below before the copy);
  actual B pending-collection cap at-limit/one-below (below cap: ZERO
  pending-retention events, exact D refusal mirrored); full sequence at the
  measured minimal cap with the crossing step exactly the mixed operation;
  privacy canary. The OLD observer's post-refresh mixed refusal preserved.

## Verification
- Focused (protected captures, literal exits): mixed module 56 passed;
  mixed+root_lineage 265; siblings (composition/causal-history/models/
  bundle-proof) 734 passed — all after product changes.
- ruff check 0; ruff format --check 678 files clean; mypy 161 files no
  issues; docs consistency 0 (19 claim docs).
- ONE foreground-managed exact-15 at clean B: all 15 literal exits 0
  (driver 1238785/UID 1001/umask 077; cmd07 child 1238962 umask 0022;
  ACTUAL pytest 1238970/birth299487934/PPID1238962/UID 1001/umask 0022,
  live + independently verified). Full pytest: 5671 passed / 28 skipped /
  710.51 s / stderr 0 B (stderr: cmd01 28 B, cmd02 30 B, cmd08 197 B
  ordinary diagnostics, rest 0).
- ONE clean git-archive-of-B build: archive/extract/build exits 0 (867
  files); wheel 476120 B/58 entries, sdist 1818939 B/256 entries byte-equal
  the manifest.
- ONE strict artifact proof: literal exit 0 / stderr 0, ALL PROOF ASSERTIONS
  PASSED (867 archive files vs Git B; 258 manifest inputs vs A/B/clean tree;
  B manifest-only; labels bound to O before execution).
- CI at B: all 10 checks completed/success at drafting.

## Live model/service evidence
None required or used (inert pure modules, fake fixtures). Protected
18020/Qwen/Codex fixture changed: NO.

## GitHub CI / required checks
All 10 checks SUCCESS at implementation head B at drafting: YES; report-head
checks may be pending (strategy verifies).

## Local setup/dependencies
No new dependencies, services or sudo actions; existing uv frozen venv.

## Documentation
Updated as listed; mirrors byte-identical; S inode/mode preserved; docs
consistency clean.

## Safety/scope confirmations
Unrelated files: none. Secrets/raw content: none. Protected resources: none.
Required tests skipped/not run: none in scope (28 suite skips are the
host's honest pre-existing skips). Scope deviation: none (process items
below). Extra PR: NO; coding merge: NO; active/order edited: NO; report
commit report-only: yes (verified after push).

## Known limitations/blockers
- Whole 018 open: 018-i/j/k/l/m NOT ACCEPTED as recorded; 018-n ACCEPTED at
  its bounded inert scope WITH PROCESS QUALIFICATIONS
  (S/reviews/018-n-decision.md); 018-o PENDING strategic review; 019-024
  mandatory.
- OLD public H acquisition unmodified: post-refresh NEW-root mixed bundles
  still refused before I through that public path (documented UNREACHED;
  018-o addresses acquisition only at its new operation scope).
- Pre-existing at the starting head (not this round): 018-f/018-g contract
  intro lines still read "IMPLEMENTED and PENDING strategic acceptance"
  though both slices were later accepted; out of 018-o scope, flagged for
  strategic follow-up.
- Gate driver header comment still names the N B SHA (stale comment; the
  functional B pin is correct; preserved, never rerun for a label).

## Process qualifications (truthful, append-only)
- Report-harness deviation; final report published WITHOUT any size cap
  (the activated 018-o order imposes no report-size requirement):
  (1) meta/report-o1.py (11106 B, inode 12454131) atomically created a
  10436 B candidate at the FINAL local report path
  oap/reports/018-o-root-aware-mixed-acquisition.md, which was then removed
  before any commit/push; no remote report or SELF resulted from it.
  (2) meta/report-o2.py (9897 B, inode 12453038) embedded a 9196 B candidate
  that failed a self-imposed 4-8 KiB size assertion before writing anything;
  that cap was a harness error, not an order constraint. Both exact
  candidate strings are preserved as protected evidence in
  W18o/meta/report-o1.py and report-o2.py.
- Manual file modes: twelve W18o manual scripts/captures written under the
  default shell umask (0664) were restricted in place to 0600 with
  bytes/inodes preserved: eight round files (meta/docs-edit-o2.py,
  docs-edit-o2fix.py, docs-edit-o3.py, docs-edit-o4.py, docs-fix-o5.py,
  pr-body-o-patch.py, pr-body/pr26-body-o-api.md, pr-body/pr26-body-o-v1.md
  inode 12454127), two from the 05:15Z audit (captures/v2-diag.py inode
  12452992, meta/refactor_h_obs.py inode 12452983), and two report writers
  (meta/report-o1.py inode 12454131, meta/report-o2.py inode 12453038).
  os.umask inside a script does not secure the script file its parent shell
  created; later writes used process-local umask 077 in the same shell
  before every file-creating command. Not a claim of perfect prior capture
  discipline.
- /tmp/mypy-repro/repro.py written out-of-area during mypy diagnosis; after
  identity verification retained protected (W18o/captures/
  mypy-narrowing-repro-v1.py, 447 B, sha e2027fcf...) and the exact
  temporary file + its self-created directory removed.
- N-round /tmp/recheck-body.md (inode 15848882) verified byte-equal to the
  protected N-v1 body plus one newline, then removed per the ordered O
  cleanup; S/reviews/018-n-temporary-copy-review-v1.json preserved. The
  N-round temporary test-source `head` copy has no retained path: UNKNOWN.
- PR-body patch harness: the first run failed a harmless trailing-newline
  assertion before patching (recorded in the round's tool output; no
  separate capture file); the corrected run patched and re-fetched with
  byte-identity verified (W18o/pr-body/: o-api 8220 B pre-patch as fetched,
  o-v1 10934 B sha 53f69e25..., o-verify re-fetch).
- Preserved interim/failure captures in W18o/captures (incl.
  focused-mixed-full-v3: 4 failed, literal exit 1, pre-repair).

## Recommended strategic follow-up
Factual only: review/accept 018-o at its bounded inert scope; whole-018
review required before merge; 019-024 continue; optionally correct the
pre-existing 018-f/018-g contract intro status lines.

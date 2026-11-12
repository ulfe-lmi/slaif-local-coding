# 018-l round report — complete metadata fences and pre-target E count evidence

- Status: PARTIAL (bounded L scope implemented and published; exact-15 gate and
  clean build passed; the ONE executed strict-proof attempt left the repo-
  gate-dist byte comparison UNMET by an order-of-execution cause and was
  frozen, not rerun; L PENDING strategic review; no acceptance claim)
- Implementation head SHA: b2caa0642f777119055a2b83d0a04f0a0c6f58d6
- Report publication commit: SELF
- Repository: ulfe-lmi/slaif-local-coding
- PR URL: https://github.com/ulfe-lmi/slaif-local-coding/pull/26
- PR mode: AMENDED_EXISTING_PR
- Base: main ffaabf4b4d9ce3a9cb7a48e12ab7d8847999adef
- Head branch: oap/018-cache-graph-bundles

## Work order
`oap/orders/018-l-complete-metadata-fences-and-prework-evidence.md` (sha256
`710e48edba3ad13c34e7176b160fa889d6ff2749a02335844d16922d2777491c`), AMEND of
PR 26 (same branch, no second PR). 018-k was NOT ACCEPTED against the complete
K01/K02/K03 criteria (`S/reviews/018-k-decision.md`): its named 16 repairs
pass, but (1) the actual nested scalar/authority closure was unmet — a
model_copy raw-string nested mode or member-class vector raised an uncaught
AttributeError instead of a fixed validation refusal, and an entry-level
authority vector forged to the other real MemberClass (key record and proof
unchanged) was accepted at both parent boundaries although the leaf rejects —
and (2) the E before-target count evidence was unmet — the facade sentinel
proved crossing work happened, not that the bound stops before the target
work, and the cap was found by binary search instead of an independently
derived actual-domain count. L closes exactly those named gaps within the
existing I scope; no old public H/D/E/F/G law, signature, default, schema or
version changed.

## L01 — complete closed nested metadata fences (earned)
The closed fence now covers the COMPLETE bounded entry / key-record /
ownership metadata shape at the leaf AND BOTH parent boundaries BEFORE any
recipe element visit: scalar types, ACTUAL enum instances (the classes are
StrEnums — equality alone accepts a raw string), containers, member
occurrences under the ACTUAL inherited admission cap, the accepted per-group
closed law and the exact ownership partition, plus the closed root/file
branch shape. The bounded entry / record joins (class, authority vector,
width against the distinct record paths) run before the canonical
re-derivation. `canonical_rekey_units` reworked to bound every serialized
term at ACTUAL record lengths and declared field ceilings (a field count is
never a serialized length); the kernel reserves the fixed
`ENTRY_METADATA_FENCE_UNITS` plus the per-member walk bound (segment
member-position counts, charged O(occurrences) plan walk) before assembly
and before the root-entry construction. Both K-unmet ROOT probes now pass at
the L pins, sources unchanged, fresh exclusive captures
(`W18l/018-k-nested-scalar-prefence-l2.{out,err,exit}` 16/16,
`W18l/018-k-parent-authority-vector-l2.{out,err,exit}` 8/8, each literal
exit 0/stderr 0): every forged shape refuses with ONE fixed private error
before the recipe's first element visit (the canonical-helper spy counts
exactly the one valid root-entry visit).

## L02 — E collection before-target count evidence (earned)
The four E collection domains are bounded in the durable suite by counts
derived INDEPENDENTLY from the retained D metadata (occurrences, proof
segments, member positions, frozen parent links — the E charging law
re-derived, never a binary search) with a class-identity-preserving ledger
spy recording every collection charge attempt: at the derived count the
composition is OK with the target charged exactly that many times and no
crossing attempt; one below, the count-th charge is the crossing attempt
refused BEFORE the crossing with the exact inherited name, exact prior state
and no partial output. Verified actual counts at the recorded fixture:
paths 2 / groups 2 / witness-memberships 8 / relation-pairs 0 for the
two-read state; 1 / 3 / 12 / 12 for the repeated-read state.

## Changes and files (A `ca0e13a179f631e21d73fac68ee667789e9c6a5b`)
`current_root_composition.py` (root-entry and file-entry plan fence
reservations on the I outer), `current_root_composition_models.py` (the
closed metadata fence, the entry / record joins, the reworked
`canonical_rekey_units`), `tests/test_current_root_composition.py` (5 new
test functions / 20 cases; module 67 defs / 258 cases), the I contract
(§5 charge law + E table row, §6 L01 law, §10 count, status),
`TESTING.md`, `ARCHITECTURE.md` (two status sites), all three compact
mirrors (byte-equal; S inode/UID/mode preserved in place),
`docs/CACHE-REWORK-LEDGER.md`, and the append-only `oap/REPORT-CORRECTIONS.md`
018-k entry. Manifest-only B `b2caa0642f777119055a2b83d0a04f0a0c6f58d6`,
sole parent A, 257 inputs. Remote head = B.

## Verification (actual outcomes)
- Durable matrix: module 258/258 PASS; three-file set 625 PASS; ruff
  check / ruff format --check / mypy (160 files) / docs consistency all
  clean.
- ONE foreground-managed exact-15 at clean B (parent umask 0077; driver
  96941; ACTUAL pytest child 97160 recognized by comm plus script-position
  argv from the bounded owned-tree walk, live /proc Umask 0022, coherent
  births/parents, `gate-cmd07-live-context-l1.json`): ALL 15 literal exits
  0. cmd07 full pytest 5565 passed / 28 skipped / 701.68 s / stderr 0.
  Honest stderr: cmd01 28 B, cmd02 30 B, cmd08 197 B (ordinary successful
  diagnostics), all other commands 0.
- ONE clean exact-B git-archive BOTH build: archive/extract/build literal
  exits 0 (archive.err 0, extract.err 0, build.err 281 B ordinary
  diagnostics); wheel 464560 B (58 entries) `e4988732…`, sdist 1772011 B
  (255 entries) `0c20b5d2…` byte-equal the manifest.
- FULL STRICT PROOF: UNMET in the one executed attempt (frozen law). The
  executed proof (source/out/err/literal exit 1 preserved verbatim, never
  rerun, rebound or rebuilt) passed every check up to the repo-gate-dist
  byte comparison — including the L-added strict checks (unique raw RECORD
  rows and archive paths, the original A input map, the B manifest-only
  parent, FULL clean archive path/byte equality vs Git B) — and failed that
  comparison because the proof ran BEFORE the gate's cmd08 rebuilt the repo
  dist/ at L's B (order-of-execution cause, not a product or build failure);
  the gate's own cmd13 manifest verification (exit 0) covers the repo dist
  against the manifest at B.
- ALLTEN exact-B CI checks completed/success (test, docker, gateway-
  contract, operator-session, cache-native-containment, cache-native-
  fixture, docker-published, CodeQL, Analyze actions/python).

## Process qualifications (truthful)
- The one executed strict-proof attempt failed against the stale (pre-
  gate) repo dist/ and is preserved exactly with its literal exit; no rerun,
  rebind or rebuild replaced it under the freeze law; its first-attempt
  bytes are retained and never relabeled.
- The 018-k report's clean-build collective "stderr 0" repeats the 018-j
  error (actual build.err 281 B ordinary diagnostics; only cmd07 stderr 0)
  and its SELF CI snapshot minute is treated as UNVERIFIED — both corrected
  append-only in `oap/REPORT-CORRECTIONS.md` with the 018-k decision's
  unmet-scope facts.
- No preliminary/background suite; all captures under protected fresh
  versioned paths (W18l) with exclusive creation.

## Scope boundary
PARTIAL does NOT accept L: strategic review of the L01/L02 evidence
remains. No coding acceptance claim. The documented UNREACHED
post-refresh NEW-current-root mixed-bundle acquisition gap remains
UNREACHED (the unmodified public H refuses competing roots before I; old H
acquisition policy not broadened). Whole 018 remains open (unmerged) and
019-024 remain mandatory. No runtime activation; no merge.

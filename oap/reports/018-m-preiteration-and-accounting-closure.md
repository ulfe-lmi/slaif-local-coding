# 018-m round report — pre-iteration fences and honest precharge

- Status: PARTIAL (bounded M01/M02 implemented at frozen B; exact-15 gate, clean build and ONE strict proof as executed; two
  frozen-B strategic findings recorded as unmet scope; no acceptance
  claim)
- Implementation head SHA: 1523a32f10b0b9aa2deb3df4968038651f4bb1e8
- Report publication commit: SELF
- Repository: ulfe-lmi/slaif-local-coding
- PR URL: https://github.com/ulfe-lmi/slaif-local-coding/pull/26
- PR mode: AMENDED_EXISTING_PR
- Base: main ffaabf4b4d9ce3a9cb7a48e12ab7d8847999adef
- Head branch: oap/018-cache-graph-bundles

## Work order
`oap/orders/018-m-preiteration-and-accounting-closure.md` (sha256
`9bec5ba793a83ddc759662dd85867166e0412a517531062b2e23478706b0a856`),
AMEND of PR 26 (same branch). 018-l was
delivered truthfully PARTIAL and NOT ACCEPTED against the complete
L01/resource/artifact criteria (`S/reviews/018-l-decision.md`): its
named 40 controls pass, but the before-iteration count/shape law
(0/24), the JSON byte ceiling (0/4) and the reservation-calculation
precharge remained unmet (facts in the decision). M closes those
named gaps within the existing I scope; no old public law, default,
schema or version changed.

## M01 — O(1) count/scalar gates BEFORE any element work (earned)
The closed fence now runs in three phases at the leaf AND BOTH parent
boundaries: (1) expected models, container kinds and O(1) lengths
under the ACTUAL inherited caps BEFORE any element is visited by any
iteration, copy, set, sort, hash or serialization — the TEN carried
admission bound models fenced as closed typed scalar models BEFORE any
cap is read; (2) the bounded scalar/path/index/enum validation with
the accepted C dense group ordering and the unique partition
membership; (3) the closed entry/record/proof authority, member, width
and ownership joins — each refusing with ONE fixed private error, no
raw value echo.
Durable: over-cap entry/record/segment/witness tuples carrying a
harmless visit marker refuse before any element visit at both
parents.

## M02 — serialization policy and calculation precharge (earned)
`_json_metadata_byte_ceiling` honestly bounds the ACTUAL accepted
json.dumps default ensure_ascii recipe per character; the canonical
recipe and its key bytes are unchanged,
no legal Unicode prohibited. `canonical_rekey_calc_units`
(walk-free bound) is precharged on the ONE I outer BEFORE the
calculation may encode, allocate or walk any element, at BOTH
reservation sites; the plan's per-segment visit is charged per
segment. Durable: the first canonical rekey runs only after the
walk-free calculation charge (cap at that charge: calculation sum
completes, ZERO rekey calls; one below: before any calculation or rekey
call; the full precharge cap fits exactly, admission-site rekey
completing at its own charge); the
plan-walk identity (measured delta equals the independently derived
node/group/workspace/occurrence/segment counts plus plan
fixed/walk terms; one below: fixed I name, ZERO entry constructions,
ledger stopped at the cap).

## Changes and files (A `65ddcfd7fb73c9c1cd9641b3757f1aedbe94b66a`)
`current_root_composition.py`, `current_root_composition_models.py`
(fence rework, bound-model fence, JSON ceiling, walk-free calc
precharge, per-segment plan charge),
`tests/test_current_root_composition.py` (6 new functions / 21 cases;
module 73 defs / 279 cases), the I contract, `TESTING.md`,
`ARCHITECTURE.md`, all three compact mirrors (byte-equal; S
inode/UID/mode in place), `docs/CACHE-REWORK-LEDGER.md`, append-only
`oap/REPORT-CORRECTIONS.md` 018-l + 018-m entries. Manifest-only B
`1523a32f10b0b9aa2deb3df4968038651f4bb1e8` (sole parent A, 257
inputs). Remote head = B.

## Verification (actual outcomes)
- Durable matrix: module 279/279 PASS exit 0; three-file set 646
  PASS exit 0; ruff check / format --check / mypy / docs consistency
  all clean.
- ONE foreground-managed exact-15 at clean B (parent umask 0077;
  driver 557986; ACTUAL pytest child 558165 by comm plus
  script-position argv in the bounded owned-tree walk, live /proc
  Umask 0022, `gate-cmd07-live-context-m1.json`): ALL 15 literal
  exits 0; cmd07 full pytest 5586 passed / 28 skipped / 709.54 s /
  stderr 0; honest stderr cmd01 28 / cmd02 30 / cmd08 197 B
  (ordinary), rest 0.
- ONE clean exact-B git-archive BOTH build: archive/extract/build
  literal exits 0 (build.err 281 B ordinary diagnostics); wheel
  468512 B / 58 entries, sdist 1782818 B / 255 entries, byte-equal
  the manifest.
- ONE strict proof over the same clean-built artifacts: literal exit
  0 / stderr 0 — 257 manifest inputs byte-identical across Git A / B /
  clean tree; 862 clean-archive files byte-equal Git B; B
  manifest-only parent, original A input map, unique raw RECORD rows,
  PKG-INFO / METADATA / entry points / LICENSE / NOTICE / repo-dist
  byte-equal.
- ALLTEN exact-B CI checks completed/success.
- Frozen-B strategic findings (recorded, unmet):
  - M02 reservation underbound for legal Unicode identities: legal
    BMP / non-BMP identities reach public I OK, but the namespace +
    canonical JSON build+hash lower bound alone exceeds
    `canonical_rekey_units` (root 48118 / 87286, file 48122 / 87290 vs
    reserved 23463 / 23723; ASCII inside) — ASCII stand-ins for the
    identity fields remain,
    `canonical_rekey_calc_units` walks groups/witnesses before its
    charge; callers sum/allocate entries before itotal.units
    (`S/reviews/018-m-unicode-canonical-reservation-v1.{out,err,exit}`,
    exit 0).
  - M01 parent proof-join gap: 8/8 genuine parent controls pass, but
    16/16 copied nested negatives were incorrectly accepted at BOTH
    parent boundaries, both modes and both endpoints (file entry with
    admitted_segments=(); root entry with same-length different
    root_text, key/provenance unchanged) — constructor-only evidence,
    no runtime-exposure claim
    (`S/probes/018-m-parent-proof-join-v1.py`;
    `S/reviews/018-m-parent-proof-join-v1.{out,err,exit}`, exit 1,
    0/16 refused).

## Process qualifications (truthful)
- The M01 probe check used /tmp captures (no-/tmp law breach); the
  first attempt (exit 2) bytes are LOST by overwrite, never
  reconstructed; the second run is preserved at
  `W18m/evidence/m01-probe-check/`. One focused pytest was piped
  through `tail -40`: its pytest exit is NOT established and the full
  lost; the module was correctly rerun with full capture and the
  actual exit (258 passed, exit 0); `018-m-focused-module-v2` is a
  runner-construction failure (for-loop exit status short-circuited
  the && chain, pytest never launched, its exit=1 is chain status, not
  pytest's); corrected reruns under fresh v3/v6 names.
- Unrecorded I-round scratch `/tmp/pr26-body-live.txt` (4750 B) and
  `-trimmed.txt` (4749 B) were used for PR-body
  verification (no-manual-/tmp law breach); surviving bytes preserved
  read-only to `W18m/evidence/i-round-tmp-preservation/`.
- The L-round qualifications stand as recorded in the append-only
  corrections (before-iteration and JSON-ceiling failures unmet; the L
  strict proof FAILED literal 1 against the stale K repo-dist BEFORE
  the gate, frozen, never rerun; modes and post-SELF global ps -eo
  corrected without byte edit).
- Response-reader recovery: ROOT tool-host generation changed; old
  M response handle 75240 / PID 174486 independently verified GONE
  with no receipt or report; ONE replacement reader lives on the
  SAME original response FIFO (handle 83555 / PID 504352,
  `S/reviews/018-m-response-reader-recovery-v2.json`); this round's
  response OK targets the original FIFO as ordered.
- No preliminary/background suite; all manual evidence under
  protected fresh versioned W18m paths (exclusive 0600); only the
  ACTUAL pytest child runs 022.

## Scope boundary
PARTIAL does NOT accept M: the two frozen-B findings remain unmet;
strategy will order their repair. No coding
acceptance claim. The UNREACHED post-refresh NEW-current-root
mixed-bundle acquisition gap remains UNREACHED (unmodified public H
refuses competing roots before I). Whole 018 remains open
(unmerged); 019-024 mandatory. No runtime activation; no merge.

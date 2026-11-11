# 018-n round report — retained content and reservation closure

- Status: COMPLETE at the 018-n scope (N01/N02 at frozen B; exact-15 gate,
  clean archive build and ONE strict proof as executed; ten implementation-
  head checks success); 018-n PENDING strategic review; no acceptance claim
- Implementation head SHA: c04efec1795f362ab5bb79f1e23d1dbed4ddd467
- Report publication commit: SELF
- Repository: ulfe-lmi/slaif-local-coding
- PR URL: https://github.com/ulfe-lmi/slaif-local-coding/pull/26
- PR mode: AMENDED_EXISTING_PR
- Base: main ffaabf4b4d9ce3a9cb7a48e12ab7d8847999adef
- Head branch: oap/018-cache-graph-bundles

## Work order
`oap/orders/018-n-retained-content-and-reservation-closure.md` (sha256
`7c966a66b5f0d741b3ecee8d7e26926f5776ad7f2f41b0f427521e9ac0141b06`), AMEND of
PR 26 (same branch); active after the single 018-n control OK at
2026-11-10T23:24:38Z (receipt `W18m/next-control-wait-018m-receipt.json`).
018-m was reviewed PARTIAL and NOT ACCEPTED against the complete M01/M02
criteria (`S/reviews/018-m-decision.md`); this round closes the named M01/M02
gaps inside the existing I scope. No old public B/C/D/E/F/G/H law, recipe
byte, default, schema, version or cap domain changed; the inert change is
confined to the new I validation and accounting.

## N01 — retained-content join (earned)
`_check_entry_retained_content` runs at the LEAF (entry validator) and BOTH
parent boundaries over the ACTUAL retained original binding. Root entry: the
ACTUAL retained bytes are preflighted (O(1) char count, then the no-copy early-
exit UTF-8 walk) against the ACTUAL inherited single-source cap BEFORE the ONE
owned encode + sha256, which must agree with the bound byte length, the root
digest and the retained ENVELOPE/READ provenance; the root-only shape is
re-joined and its sole PROVEN ownership-group digest joins the retained root
digest. File entry: a nonempty admitted-segment tuple with distinct increasing
indices (empty source bytes remain legal), closed byte/char totals under the
ACTUAL cap BEFORE any owned slice, region the whole bundle or one proven
group, every member position validated as an ACTUAL integer indexing the
retained requested occurrences BEFORE any fetch, admitted members equal the
key-record member occurrences, region digest equals the aggregate digest, and
the entry-local group partition joins ONE-TO-ONE to the ORIGINAL proof
segments (dense member-index range, PROVEN single-member / BOUNDARYLESS multi-
member class, proven member digest / segment digest). A coherently rekeyed
record with a DETACHED partition (changed group digest, reverse rows remapped)
is refused at BOTH parents, root and file shapes. Durable: `test_n_parent_retained_content_join`,
`test_n_parent_group_partition_join`; the preserved 018-m parent-proof-join
and the root-ownership probe (8 genuine positives, all 8 coherent
mutations refused) both re-pass at frozen B
(`S/reviews/018-n-frozen-{parent-content,root-ownership}-v1.*`).

## N02 — byte-aware closed reservations (earned)
`canonical_rekey_units` drops the ASCII identity stand-ins: identity/version/
class strings are bounded by the ACTUAL measured JSON byte ceilings of the
accepted json.dumps recipe (nested bound-model dumps counted as JSON strings
in the namespace, objects in the key, under closed ceilings);
`test_n_canonical_reservation_actual_bytes` asserts the full actual-byte
oracle `4*namespace_payload + 2*key_payload` for ASCII/BMP/non-BMP/escaped
identities including a max-length Unicode `model_identity`. New
`retained_content_join_units` (root 9+3L+4L+4L+64; file 70 + A(4+M) + A +
A(4+2M) + 4S + 10C) is charged on the ONE I outer BEFORE any encode/hash: leaf
work is precharged in the plan aggregate (per-occurrence whole-vs-isolated
alternative, source work reserved once — isolated regions are disjoint) before
entry construction; BOTH parent sites charge the actual per-entry join sum
before construction. The planner precharges the VALIDATED segment count before
starting segment iteration; the per-site reservation-calculation closure is
durable at BOTH actual public-I sites (a result-site crossing counts the
earlier admission helper visits on the SAME capped ledger and requires zero
result-site visits at the crossing). Durable:
`test_n_retained_join_byte_and_traversal_reservation`,
`test_n_leaf_join_isolated_entries_precharge`,
`test_n_plan_segment_precharge_order`, `test_n_reservation_crossing_both_
sites`, `test_n_file_join_zero_source_multimember_bound`. The strategic probes
re-pass at frozen B
(`S/reviews/018-n-frozen-{unicode-reservation,planner-precharge}-v1.*`).

## Changes and files (A `591db61adc5630906db24657ad320a11c04bdf6c`)
- `src/slaif_local_coding/constitution/bundles/current_root_composition_
models.py`: the join, the byte-aware reservation functions, docstring wording
  (nonempty admitted-segment tuple; root ownership join).
- `src/slaif_local_coding/constitution/bundles/current_root_composition.py`:
  plan segment precharge before iteration, plan reservation charge before
  construction, per-site join charges.
- `tests/test_current_root_composition.py`: eight new test definitions (29
  cases; module 81 definitions / 308 cases); all prior I/J/K/L/M controls kept.
- Docs: `docs/CACHE-CURRENT-ROOT-COMPOSITION-CONTRACT.md` (018-n section, join
  law/order, 81/308 counts), `docs/CACHE-REWORK-LEDGER.md` (C04/C05/018 rows),
  `ARCHITECTURE-for-agents.md` (three compact mirrors byte-identical at
  d4e2a700...; the supervision copy written IN PLACE, inode 10638621 / UID 1001
  / mode 0600 preserved), `ARCHITECTURE.md` (two status locations) and
  `TESTING.md`: M recorded PARTIAL/NOT ACCEPTED with the decision reference;
  only the 018-n repairs are PENDING review.
- `oap/orders/018-n-retained-content-and-reservation-closure.md` (activated
  order, unchanged bytes) and `oap/active` committed with A.
- B `c04efec1795f362ab5bb79f1e23d1dbed4ddd467`: manifest-only over A (257
  inputs; wheel 14e7a40e..., sdist 085c2b90...).

## Verification (actual outcomes)
- Pre-freeze: ruff check / ruff format --check / mypy (160 source files) /
  docs consistency (19 docs) all clean; focused `-k test_n` 29 passed, actual
  pytest exit 0 (parent umask 077 / pytest child 022; `W18n/focused-n-v9.*`,
  `W18n/prefreeze-lint-mypy-v2.out`).
- Exact-15 gate at frozen B (`W18n/final-gate-n1`, mechanical M-to-N rebind): all fifteen rc=0,
  `gate.exit=pass`. cmd07 full primary suite: 5615 passed, 28 skipped,
  693.08s, literal pytest exit 0; ACTUAL pytest child umask 0022 (actual
  pytest 860178/birth297856405/PPID860170, independently verified by ROOT at
  `S/reviews/018-n-live-final-gate-context-v1.json`); driver umask 077 (pid
  860006, head=B, clean tree).
- Ten implementation-head check runs at B: ALL TEN completed/success (test,
  docker, docker-published, gateway-contract, operator-session,
  cache-native-containment, cache-native-fixture, CodeQL, Analyze actions,
  Analyze python).
- Post-gate clean archive build (`W18n/clean-build-n1`, git archive of B, 864
  files): archive/extract/build literal exits 0; rebuilt wheel/sdist hashes
  equal the manifest.
- ONE strict proof: ALL PROOF ASSERTIONS PASSED, actual rc 0; the prior frozen
  L failed proof was NOT rerun. The mechanical M-to-N rebind preserved the
  assertion code exactly; the proof JSON's human-readable `scope` label still
  reads "018-m m1 ..." (copied from the M script) while its actual head
  c04efec..., source A 591db61..., paths, artifacts and checks correctly bind
  N — recorded as a stale label, frozen bytes preserved.

## Process qualifications (truthful)
1. Overbroad /proc scan (02:53Z): one command iterated `/proc/[0-9]*/cmdline`
   before filtering while locating the known gate driver; N section 3
   prohibits global process scans and that boundary was crossed. The extra
   matched PID (860697) is an inferred self-match (its command text contained
   the search string); no raw cmdlines were printed and no directly measured
   identity facts exist for it. Later captures used only the known owned tree.

2. `W18n/final-gate-n1` was created 0775 and corrected to 0700 at 02:59:35Z
   (chmod; same inode, capture bytes unchanged).
3. `W18n/evidence-3file-v1` ran BEFORE the criterion-1 kernel precharge edit;
   superseded by the frozen-gate full-suite run at B, not cited as gate
   evidence.
4. Two /tmp writes this round: a `head` of test source (harmless, not
   evidence) and one transient post-finalization PR-body re-fetch (verified
   line-identical to the protected copy apart from the jq newline); the
   no-/tmp capture law was breached twice, both harmless, both recorded.
5. Two no-op apply_patch attempts (identical old/new lines) during this
   round's docstring rewrap; detected and re-applied, final bytes verified by
   ruff/mypy/pytest.
6. The 018-m-era deviations stand as recorded in the 018-m report (m01 probe
   /tmp capture overwrite, first bytes LOST; one tail-piped focused pytest
   with unestablished exit, rerun with full capture).

## Scope boundary
018-n is PENDING strategic review; a report is a claim, not acceptance. Whole
018 remains unmerged and unaccepted. The separately ordered mixed-root
acquisition operation remains required: the four post-refresh NEW-root mixed-
bundle controls stay UNREACHED at I because the actual unmodified H refuses
competing_roots before I (documented limitation, contract section 8; an old-H
precondition, not an N defect). Stages 019-024 remain mandatory; no v1
runtime mechanism is active or qualified.

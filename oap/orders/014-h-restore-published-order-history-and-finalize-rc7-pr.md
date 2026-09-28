# OAP ORDER 014-h — Restore published order history and finalize the RC7 PR

## Objective and current state

Continue numeric Objective 014 in existing PR #19. **AMEND_EXISTING_PR** only.

- Remote `main`: `8c3c6d6cd67a34ba7d427ab255a91bd6a9753bd1`.
- Remote PR head: report-only SELF `30c78447fef68583c984e42a3ae24b297ff2da29`.
- SELF parent / accepted implementation evidence head: `9169409720905a69627c9119fb3258faf0344a43`.
- Private RC7 source S7: `ae6271318627703785f42de57d893c9be3b980c9`.
- Private RC7 digest: `sha256:a3782915da58a403fd0f7991c57f9954b07bfb9377e4730715c0fb7398f901db`.
- Final-head CI `36477169677`, CodeQL `36477163114`, pulled-image qualification, and genuine-Codex ledger 005 are green and remain authoritative.

Strategic review found one orchestration-history defect: the immutable 014-d order was atomically published and activated, but its local-only branch history was later reset during the authorized 014-e recovery. Consequently, GitHub contains 014-e's truthful abandonment account but lacks the actual published 014-d order file. The strategic byte-exact copy still exists.

This is OAP continuity repair only. Do not change product source, workflows, tests, schemas, configuration, documentation, packaging records, provenance, handoff, ledgers, release identities, or registry state.

## Required work

1. Reconcile GitHub and verify PR #19 is open, clean/mergeable, and at exact report SELF `30c78447…` before mutation.
2. Verify the strategy-restored file exists at:
   `oap/orders/014-d-reject-rc5-freeze-corrected-gates-and-qualify-private-rc6.md`
   and has SHA-256 exactly:
   `2d0111818e7d9f2e150e09396924f9160597aafc4ad27545ad1756f5d636a2ea`.
   Do not edit or regenerate it.
3. Commit exactly these OAP transcript changes in one implementation commit:
   - add the byte-exact missing 014-d order;
   - add this byte-exact 014-h order;
   - change `oap/active` from `014-g` to `014-h`.
4. Do not commit or delete the pre-existing untracked files `Local`, `clean`, or `unchanged`.
5. Update PR #19 title and body so reviewer-facing metadata describes the final RC7 result, exact S7/digest, real-Codex 0.149 VISION/CACHE/BOTH pass, pulled-image qualification, private/non-final status, and explicit no-benchmark/no-cutover boundaries. Remove stale wording that presents RC4 as the final result.
6. Push the implementation commit. Require fresh exact-head CI and CodeQL to be present and successful, with zero open code-scanning alerts. Because the diff is OAP-only, do not republish RC7 or rerun protected inference unless an existing mandatory check unexpectedly requires it.
7. Verify independently that:
   - S7, D7, both RC7 aliases, the RC7 record/handoff/provenance, and ledger 005 are unchanged;
   - `source_input_map.py --ref <new-implementation-head> --manifest packaging/release_provenance_manifest.json` still proves the 127-entry binding;
   - port 18031 is absent and protected vLLM PID/listener/unit state is unchanged;
   - no benchmark, public release, visibility change, final GitHub Release, Gateway mutation, or cutover occurred.

## Report contract

Create exactly one report matching `oap/reports/014-h-*.md`. Before the report commit, all claimed implementation state and PR metadata must be remote. The final report commit must change only that report, its parent must equal the literal implementation SHA, and it must state literal SELF. Include order hashes, exact PR/base/head, implementation/report SHAs, exact changed paths, fresh checks/run URLs, zero-alert result, unchanged RC7 identities, source-map proof, protected-host/port facts, non-goal audit, and `BENCHMARK_READY` only if the cumulative Objective-014 result remains fully satisfied.

Never merge. Strategy alone reviews and merges.

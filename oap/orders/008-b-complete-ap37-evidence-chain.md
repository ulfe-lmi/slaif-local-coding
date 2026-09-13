# OAP Work Order — 008-b

## Objective and current authority

Continue Objective 008 on the same PR. This is a strategic-review correction
of the incomplete evidence set, not a new objective and not an acceptance rerun.

GitHub state: `008-b`, `AMEND_EXISTING_PR`, repository
`ulfe-lmi/slaif-local-coding`, PR #10, base `main` at
`2041bddc5a745ef0dd4f3088c24b74b9bceefdb9`, branch
`oap/008-durable-acceptance-evidence`, immutable current report head
`5ee6a2869f723c6b8dce58d0d18ebe34102aa28c`, whose implementation parent is
`93810f3894a269f345b4954918fba246d361c6e5`. Strategy independently verified
that PR #10 is open and mergeable and that both final-head `test` and
`gateway-contract` checks are successful. Start exactly from the remote PR
head and preserve the existing PR.

Use the repository/environment's current configured `qwen-neumann` coding
profile. Do not select, create, change, override, or test another profile,
model, account, or Codex-home configuration. This is repository-only work: no
Qwen/provider/model inference, protected request, Gateway checkout or change,
service/GPU/network/credential activity, deployment, or release.

## Strategic review finding

Do not rewrite or remove the immutable 008-a report. It remains evidence of
that round, but it is not sufficient for merge.

The 008-a report itself confirms that the exact AP37 artifact still exists at
`/tmp/slaif-005-ap-fake-gate.rHO7rQ`, while the immutable 005-ar report at
`e9829d84cc4116f749ddc8bc97b08fa37231e77f` explicitly used validation of that
exact AP37 artifact as the full 37/37 fake qualification authority. The
durable `005-ai` evidence and the retained final isolated fake target are
important corroboration, but they do not preserve the exact AP37 reuse object
named by the final closure report. Therefore AP37 materially completes the
published acceptance chain and may not remain only in disposable `/tmp` state
while it is still safely recoverable.

The implementation already contains a large closed `FULL_FAKE_GATE_SPEC` but
then leaves it as an unsupported reference shape. Resolve that unfinished
state. Do not build another schema or general framework.

There is also a report-honesty correction. Earlier during 008-a, before the
final narrowed implementation, a coding worker briefly listed names from
`/tmp` and printed a substantial portion of the already-sanitized AP37 JSON to
its visible tmux transcript while debugging. No credential, secret, raw model
output, prompt, call/request/item ID, protected payload, or unsafe historical
artifact was exposed, and no unrelated file content was read; nevertheless,
the 008-a assertions that no `/tmp` listing occurred and no artifact content
appeared in the transcript are overbroad. The 008-b report must correct those
two assertions explicitly and must not repeat them. Do not inspect broad
`/tmp` or reproduce any artifact content while making the correction.

## Required correction

1. Inspect only the exact AP37 path already authorized above. Revalidate its
   lexical path, final file type, ownership, link count, restrictive mode, and
   bounded size before reading it. Do not list/search/crawl `/tmp`, home,
   history, another worktree, or another host.
2. Validate the complete AP37 bytes against the existing closed full-fake-gate
   schema and the existing privacy/content rules. Reconcile any mismatch from
   committed producer/source semantics, not by examining or allowlisting raw
   arbitrary values. Unknown fields or unsafe structures fail closed; never
   silently strip data. Never print the artifact or arbitrary values. Bounded
   key names, type classes, counts, fixed rejection classes, size, and SHA-256
   after acceptance are permitted.
3. If the exact artifact passes, make `full_fake_gate` an actual closed export
   role, export the exact accepted bytes under a stable filename such as
   `oap/evidence/005-ar/reused_ap37_fake_gate.json`, and update the compact
   manifest so the AP37 authority is `accepted` with exact source/committed
   SHA-256, byte count, and relative path. Remove the obsolete
   `optional_not_retained` rationale from current documentation and manifest.
   Do not change the existing three retained artifact bytes.
4. It is explicitly authorized to replace only the unmerged Objective-008
   manifest created by 008-a, after verifying its exact committed identity, so
   the final manifest represents all four accepted artifacts. Preserve the
   immutable 008-a report and all Objective-005/006/007 history. The writer's
   public fail-closed refusal to overwrite an existing destination must not be
   weakened merely to update this in-PR manifest.
5. If the AP37 artifact fails the closed schema or privacy audit, do not commit
   it. Fix a demonstrated schema mismatch if it reflects the known sanitized
   producer contract; otherwise publish only the exact fixed safe rejection
   class and stop. A true privacy rejection is an external safety boundary,
   not permission to copy or print the content.
6. Keep the future exporter narrowly acceptance-owned. It must support the
   current explicit `protected_target`, `fake_target`, and `full_fake_gate`
   schemas (plus internal manifest), but not arbitrary JSON or a general
   artifact framework. Delete dead schema/reference machinery only if it is
   no longer reachable after this correction; do not add a second competing
   implementation.

## Qualification and acceptance

Add or adjust focused CPU-only regressions proving:

- the exact full-fake-gate schema is a supported export role;
- a valid synthetic full fake gate exports deterministically and produces
  matching bounded provenance;
- unknown/missing/unsafe nested content is rejected rather than stripped;
- the historical audit accepts all four synthetic authorities and produces a
  four-entry accepted, hash/size/path-coherent manifest;
- source deletion after export does not remove the durable AP37 copy;
- traversal/symlink/atomic-failure/no-network/no-model/no-Git guarantees remain;
- normal developer tests do not require historical `/tmp` state;
- runtime wheel still excludes exporter, tests, OAP data, and evidence.

Run focused tests, the complete normal suite, Ruff check/format, mypy in a
clean CI-equivalent environment including the script path, build/package and
wheel inspection, compileall, shell syntax, `git diff --check`, zero-`src/`
delta review, and independent strict schema/privacy/hash comparison of all
four committed evidence files and the updated manifest. No protected or live
acceptance work is authorized.

Push all non-report changes to PR #10 and require both `test` and
`gateway-contract` successful on the exact implementation head. Fix safe
in-scope local/CI defects in this same round.

## Publication and handoff

Publish exactly one new immutable report:
`oap/reports/008-b-complete-ap37-evidence-chain.md`. It must name the literal
implementation SHA and `Report publication commit: SELF`; its report-only
commit's first parent must equal that implementation SHA. Record the exact
AP37 safe validation/export path, size and hashes; the final four-artifact
manifest hash; all local/CI evidence; zero production/model/service activity;
and the explicit 008-a transcript/process correction above. Do not include raw
artifact values or any path beyond the exact historical path already
authorized.

Coding never merges. Send exact response FIFO `OK` only after remote report
bytes/head/parent are verified. Strategy will independently inspect all four
evidence JSON files, the manifest, complete PR diff, report parentage, package,
CI and security posture, then merge only if every Objective-008 requirement is
actually satisfied.

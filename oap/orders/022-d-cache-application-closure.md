# OAP work order — 022-d: v1 application closure

Numeric objective 022, AMEND_EXISTING_PR. Amend only
[PR #30](https://github.com/ulfe-lmi/slaif-local-coding/pull/30),
branch `oap/022-cache-source-replacement`, from verified report head
`56cf8442812519389be6e17812641d5329038ddc` on main
`144af0bd5e34387afcb8e3f9ddf761eabd56e817`. No new PR, merge or auto-merge.
022-c delivered the runnable v1 app and bounded Responses evidence.
Both exact heads are green. The actual app behavior and missing endpoint
evidence below prevent objective acceptance. Keep the approved CACHE-REWORK
requirements, plan policies 7–15 and the existing 022 R01–R05/S01–S02 scope.

## 1. Reject source markers before cold acquisition

At exact C, the bounded test uses synthetic `_v1_settings` and the normal
`create_app` with a fake upstream. Its first root envelope carries a synthetic
non-authoritative tag in a fresh trusted session.
The response is 409 and no main request reaches upstream, but one compile
runs and the app has already retained RAM revision 1 and protected
generation 1. A later genuine first root returns 503. The app currently
calls `establish_v1_session` before `prepare_replay_shadow`; cold bootstrap
does raw acquisition and checkpointing in that first call.

Apply the existing closed marker/source-carrier law before any cold raw
acquisition, owner allocation or checkpoint. A fresh address cannot
authenticate a retained source marker. Check the actual cold recognized
root/result source spans while ordinary non-source text stays data. Keep
live/resumed original, verified transformed replay and stale marker
semantics. Actual app regressions must prove fixed 409, zero new owner,
generation, compile and main calls, successful later legitimate bootstrap,
and an ordinary non-source marker-shaped control. Test an actual prior
marker presented to another trusted session in the isolation proof.

## 2. Preserve currentness and use the accepted recovery fence

At exact C, the bounded app test begins with a legitimate root referencing
A.md. The fake main upstream issues a complete `exec_command` for the
read-only fixture files `AGENTS.md` and `A.md`. The subsequent request
carries the original complete boundaryless result. Actual P/Q/T evidence yields
`root_currentness_unproven`, but `prepare_v1_transaction` returns an
unmodified body and the app forwards it with status 200. Preserve the
accepted typed 409 for established root authority conflict/unproven
currentness, with zero main forward. Apply the existing 409/422/503
classification where the actual results justify it. Preserve uncached
ordinary and unsupported untransformed data cases at their earned scope.
Retain the actual P/Q evidence and refuse without a bootstrap fallback.
Preserve the accepted component lineage behavior for a genuinely issued
unambiguous descendant.

Wire the accepted 020 `RecoverySessionOwner.admit_with_fence` (or its
owned kernel) into actual request and issuance state transitions as
applicable. C constructs the accepted owner and fixes stale-generation
replay, but its direct `owner.admit` followed by a separate checkpoint
skips the adverse durable fence. Retain the owner/epoch/snapshot,
bounded IO/CAS, durable-quarantine and failed-generation laws, including
safe cleanup of an acquired cold owner/writer on prepublication failure.
Verify actual public outcome and no main forward through an adverse
fence/checkpoint fault, replay/restart behavior, and a later legitimate
cold startup after cleanup. Preserve C's existing ordinary failed-fsync
replay-after-fault regression and success path. Keep normal hits free of
recovery original reads.

## 3. Complete the existing application evidence

Update the existing app tests to cover only the missing 022 criteria.
Both endpoints must be exercised at actual `create_app` with exact
fake-upstream request/response evidence. C's report explicitly earned
Responses only at that boundary. Use actual Chat tool calls, results,
nonstream and split SSE issuance, and authority-safe stable Chat
placement, with the legitimately established or resumed session scope
from the supported observation contracts. Do not introduce new root
grammar as a test shortcut. Keep the existing Responses cases and verify
that this request's represented proven frontier, including validated
replays and selected provenance as applicable, supplies the legitimate
parents. Internal compiler traffic and client fabrication supply none.

Fill the remaining R01–R05/S01–S02 application evidence: exact tool and
image/Unicode/wrapper preservation; a reduced history that retains root
with normal RAM reuse and a source-absent one with compiled reinjection;
signed identity/route protection and different trusted namespaces with
identical source; real upstream-body checks for fixed compiler, budget
and checkpoint failures; source change/replay/revert; stream order and
v1 request/response disconnect or cancellation. Distinguish fake history
reduction and recorded reference-format evidence from native client
compaction, which remains 024. Reuse the existing actual component
fixtures and C forwarding/issuance tests. Only claim criteria at the
actual app boundary after testing the body the fake upstream receives.
The extended 023 adversarial/lifecycle matrix and 024 live/genuine-Codex
qualification remain future objectives.

## Verification, publication and boundaries

Read the operator's local `AGENTS.md` update as session governance. Preserve
its working-tree bytes and leave it unstaged. Build exact-source artifacts
from committed source as usual.

Update both existing architecture maps and compact mirrors and the
existing ledger/security/configuration text only where findings or actual
behavior require it. Correct the C overclaims in current docs, never edit
past orders/reports. No new planning or audit documents. Run focused
regressions with true exits, then the same fifteen-command frozen gate,
manifest-only B over source A, clean exact-B archive/wheel/sdist and
fresh noneditable Python 3.12 proof, and all ten exact-B checks as C.
Reuse C driver patterns with absolute paths, private per-round captures
and concurrent actual CI/locked gate once B is frozen. Preserve the
published baseline and gateway/legacy contracts.

The original right pane %19 is still running Codex PID 598258, birth
150182858, early-beta xhigh. Its sole existing standard control reader is
PID 2620975, birth 381868366, child of bash 2620974 under that Codex,
managed handle 42360. After its exact EOF-checked ASCII `OK` returns
exit 0, read the exact active/order and refresh complete governance as
required, including after any subsequent native compaction, and reconcile
the current GitHub head before mutation. No duplicate reader, extra
Codex or model-client startup, private-service changes or live calls.
Restart only after verified crash, visibly RIGHT using exactly
`codex --yolo --profile early-beta`. Preserve Qwen/18020, existing
profiles, credentials, network, Gateway, and the original FIFO pair.
Use only private project work artifacts under `/home/janezp/codex-supervision/slaif-local-coding/work-artifacts/oap-022d-work`.
No benchmark dispatch, deployment or registry publication.

Push implementation and unchanged activated transcript to the same PR
before the immutable report. Publish exactly one report-only SELF with
verified remote parent SHA and bytes. Send one standard response FIFO
`OK`, then arm one managed standard control FIFO reader. Report any
unmet requirement with its precise status. No new PR or merge.

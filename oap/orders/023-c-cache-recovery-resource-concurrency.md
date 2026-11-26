# OAP work order — 023-c application recovery, resource bounds and concurrency

Numeric objective 023. AMEND_EXISTING_PR, [PR #31](https://github.com/ulfe-lmi/slaif-local-coding/pull/31).
The verified base is `4319049d91428b8995e83db82b1736ed36626a12` on main. The exact
starting report head is `3267ffa7f2b89becf6f57f687bc3f4499d28ab1e` on
`oap/023-cache-negative-path-acceptance`. Continue on this branch.
Create no new branch or PR. Coding does not merge or enable auto-merge.

## Scope

Continue the approved 023 negative-path and stress-test matrix after
023-a telemetry and 023-b content/currentness. Use the actual opted-in
`create_app` path, trusted synthetic identities, fake main upstream
and a separate tool-free fake compiler. Reuse direct named evidence
from earlier rounds where it proves the same criterion. Preserve the
approved CACHE-REWORK requirements, original matrix and human handoff.

1. **C03 and M04.** Bounded actual concurrent requests cover an identical
   miss, same-session publication and cancellation. Check the actual
   compiler calls, complete downstream outcomes, exactly-once dispatch
   for each successful request, one live owner and the committed
   generation/checkpoint. Distinguish the transaction wait followed by
   RAM reuse from actual compiler single-flight subscribers if the
   path serializes their preparation. Include another session's survival
   while an affected session fails or closes. Existing component tests
   continue to cover concurrent writer and teardown fences at their
   own scope.
2. **M01, M02 and O03.** Use an actual process boundary for a restart over
   the same protected test store. A bounded Python-only app harness
   with fake transports is permitted. Prepare more than one persisted
   session in one process and resume only the requested session in a
   fresh one. Verify distinct process IDs, selected-address-only reads,
   new epoch and actual rebuild compilation, the previously dormant
   session still intact, and the emitted working set. Show normal hits
   and source-absent reinjection separately from restart rebuilding.
   Observe zero recovery-source content reads and zero recompile on
   normal hits, and verify the actual main body.
3. **M03, M05 and B03/B04 as applicable.** Exercise the pre-existing
   corrupt/torn/foreign/config-mismatched recovery cases at the actual
   app boundary with synthetic records, plus checkpoint and compiler
   refusal. Verify the typed result, unchanged prior committed state
   where applicable, no dangling references or silent original-source
   fallback, and zero forward on refusal. Demonstrate bounded RAM
   pressure and explicit teardown without eviction or disk spill,
   governance loss or disruption of other retained sessions. Reuse
   exact existing B01/B02 counted tokenizer/allowance and wire-budget
   evidence and B03/B04 failure/identity cases at their proven scope.
   Close actual boundary gaps in this order's resource/recovery cases.
4. Close two bounded earlier evidence gaps using the existing
   application fixtures. For C02, directly correlate the repeated
   operand's actual observation or selected entry to its one distinct
   represented path. For S01, exercise distinct repository identities
   with identical principal/session and fixture bytes across one
   protected test store, and verify address-scoped reuse and no
   cross-repository recovery or source delivery. Retain signed-identity,
   legacy, image, API/SSE and cancellation regressions at their existing
   scopes. The separate whole-023 reconciliation and all 024 actual
   model, genuine client and genuine compaction remain required.

## Checkout, verification and publication

Use `/home/janezp/codex-supervision/slaif-local-coding/work-artifacts/oap-023a-work/checkout`
from the verified 023-b report head and preserve the unstaged operator
AGENTS.md and primary checkout. New durable 023-c captures belong only in
`/home/janezp/codex-supervision/slaif-local-coding/work-artifacts/oap-023c-work`.
Pytest uses the ordinary portable temporary directory. Use protected
permissions for recovery files and any deliberately retained synthetic
evidence. Real keys, private request/source content and raw customer
data are outside the test boundary.

Run the changed focused app cases plus applicable recovery/store/resume,
RAM/work, compiler, selection and app/regression suites with exact exits.
Require the same fifteen Python 3.12.15 locked commands and ten checks
used in 023-b. Build from the exact clean implementation commit, compare
both artifacts and verify fresh noneditable wheel install. Update only
relevant existing architecture/ledger state. Keep fake, actual-model,
genuine-client and genuine-compaction evidence distinct. Preserve
protected Qwen/18020, networks, profiles, keys, RC10 and earlier orders
and reports. No live inference, no service/Gateway work, no new Codex or
model-client startup, no benchmark, registry, release or deployment.

The sole right-pane worker is tmux %19, PID 598258 birth 150182858,
early-beta xhigh. Its sole standard control reader is PID 2280281
birth 429434298, under bash 2280271 birth 429434294, managed handle
26072. Collect its valid frame with exit zero, then read the governing
documents and exact active order. Refresh after compaction. Only a
verified crash authorizes an exact `codex --yolo --profile early-beta`
restart visibly in the right pane.

Push the exact unchanged order/active with the implementation on the
same PR, then publish one immutable report with the literal
implementation SHA and report-only SELF. Independently verify the
remote report head, sole parent, single changed path and exact bytes.
Send one exact response FIFO OK and arm one standard control reader.
Do not choose the next order.

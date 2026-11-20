# OAP work order — 022-c: v1 application transaction

Numeric objective 022, AMEND_EXISTING_PR. Amend only PR #30
(https://github.com/ulfe-lmi/slaif-local-coding/pull/30), branch
`oap/022-cache-source-replacement`, from the verified report head
`8bd38c5bd826d41404fca305207824316f84cb3e` on main
`144af0bd5e34387afcb8e3f9ddf761eabd56e817`. No new PR, merge or auto-merge.
022-a settings and the 022-b TOML correction are delivered. The 022-b pure
transaction covers current root/file replacement, replay and omission at
its exercised scope. Its old read-root replay case and application wiring
are open. The unchanged acceptance boundary is CACHE-REWORK.md,
CACHE-IMPLEMENTATION-PLAN.md policies 7–15 and objective 022
(R01–R05/S01–S02 at the actual application/fake-upstream boundary).

## 1. Close the historical read-root gap

The approved evidence-marker policy applies to a superseded authoritative
whole root read and a superseded authoritative root region, as well as the
bootstrap envelope. At exact 022-b implementation B, an actual retained
read r1 is selected and emits a live root tag, then a genuinely issued
descendant r2 becomes the governing root. The resulting ready P/Q/T and
prepared RAM/021 context accepts the replayed r1 raw carrier unchanged.
Replacing r1's original with the actual previously minted live tag also
returns OK and leaves the stale tag in the outgoing decoded result. The
retained historical join covers P/Q envelopes and E nonroot groups. E
does not report currentness for the root path.

Reuse the acceptance fixture in `tests/test_bundle_replace.py` with actual
P/D issuances, selected root provenance and T results. Use same-run ready
P/Q authority plus each old read's own retained occurrence, proof and
whole/region segment. Old raw earns a non-resolving EVIDENCE tag with the
current working set and durable snapshot, its transformed evidence
replays, and the previously emitted live tag refuses with no output or
partial edit. No old compiled text is selected. Preserve the old carrier
role, wrappers and other members of a mixed read; a new authoritative
revert follows normal currentness. Do not reclassify incomplete,
unissued, ambiguous or incomparable data. Detect marker-shaped source
replays before committing raw acquisitions in step 2, including known
superseded root-read coordinates. Ordinary non-source text stays data.

## 2. Wire the governed request path

Use the normal FastAPI app entry point and the already accepted 017–022
contracts, the explicit `dependency-bundles-v1` selector and route
model budget. Implement this slice incrementally inside the same order
and existing branch. Use a typed internal request context and narrow
seams for the accepted components. Replace the unconditional inert
app refusal with a runnable profile for supported settings. Preserve
fixed typed startup/readiness failure for invalid configuration or
capability.

- Reuse existing signed identity verification and replay protection
  and existing explicitly configured trusted static identity. Keep
  request guard, auth, route matching, image policy and Responses tool
  policy order. Use no caller assertions of scope, session, compiler
  bypass or trusted issuance. V1 governed routes never instantiate or
  use legacy cache/compiler/rehydration. Legacy and non-governed behavior
  retain existing behavior. Workspace is the legitimate observed scope
  or verified resumed scope, never from adapter filesystem access.
- Compose the actual P/D observation and same-run T admission with the
  actual RAM owner/CAS and accepted recovery session ownership. Establish
  a cold owner from legitimate root evidence or resume exactly one
  authenticated address. Apply version/association/bounds checks and
  validate source-field markers before raw state acquisition. Ordinary
  hits perform no recovery original reads. Reuse the accepted bounded
  compiler through the actual RAM work plane, single-flight and once
  per unchanged epoch. The internal compiler POST is direct, tool-free
  and outside the main issuance observer. Run the actual tokenizer
  budgets, required-first selection and final envelope accounting.
- Prepare a real successful protected generation for the exact snapshot
  the edits rely on. Use distinct application-owned private marker key
  material with stable authenticated session/recovery binding. Resolve
  persistence or derivation within the existing protected recovery
  contract, never using a gateway/service credential or a public digest
  as the secret. Prefer the existing config and recovery contracts;
  document any necessary private configuration reference. No secret in
  Git, logs, refs, response fields, test captures or operational reprs.
- Apply the pure transaction before a single serialization and main
  upstream forward. Preserve ordinary text, tools, role hierarchy and
  endpoint semantics. Provide required compiled content and real
  acquisition guidance. Route-specific, idempotent Responses
  instructions and Chat placement must not promote off-graph, ambiguous
  or ordinary tool text to system authority. Prompt/required budget,
  checkpoint, recovery, resource, compiler and stale-scope failures
  follow the fixed failure/limitation contracts with no hidden raw
  fallback, dangling required reference or automatic replay. Respect
  owner fencing, cancellation, lifecycle and negative-evidence rules.

## 3. Bind trusted tool issuance to the forwarded request

Use the accepted 018 issuance/receipt law. Freeze the actual represented
completed-fact frontier of this specific serialized/committed main request,
including actual represented source and selected compiled-entry provenance.
Keep all relevant incomparable members and reduce only proven ancestors.
Never rebase on later global state, caller assistant items, result arrival,
new call IDs, contents, revisions, or replay metadata.

Observe only complete supported tool calls in the actual direct main
upstream response in both endpoints, including split bounded incremental
SSE assembly and nonstreaming. Use the existing immutable canonical tool
argument recipe. A complete authenticated issuance is not execution
completion or a source receipt. Rejoin later original client results with
the matching retained issued binding, including native initial EXEC
ownership across polls. No issuance from malformed/incomplete/truncated
events or compiler traffic. Preserve SSE event order, usage, tools, errors,
disconnect and cancellation without buffering the full stream. Persist only
permitted derived metadata with the accepted owner/generation rules.
Post-forward failure never retries the main request, invents a frontier or
upgrades unproven evidence. Reuse existing behavior and narrow typed
limitations for unsupported shapes.

## 4. Required proof and publication

Inspect actual fake-upstream HTTP request bodies and real app responses.
Cover R01–R05 and S01/S02 as named in CACHE-REWORK.md and the ledger:
first acquisition and real normal-hit reuse, exact replacements preserving
tool/image/prefix/Unicode metadata, now-current and stale old references,
source still carried after reduction and source-absent rehydration,
different trusted namespaces, signed-route/failure and streaming/disconnect
contracts. Exercise both endpoints; actual nonstream and split SSE
issuance causality, inbound fabrication/no anchor, old root/nonroot
supersession/replay/revert, and a delayed or concurrent case whose two
distinct frozen request frontiers prove no later-fact rebasing. Verify
trusted single-session recovery and pre-forward typed rejection for
checkpoint/compiler/budget failures through actual accepted contracts.
Use synthetic fixture sources; instrument actual forwarding, compiles and
recovery content reads rather than substituting counter-only results.
023 keeps the complete expanded adversarial/lifecycle/telemetry matrix;
024 keeps actual-model/genuine-Codex qualification and immutable handoff.
Do not declare these later gates earned by this round.

Update the existing architecture maps and compact mirrors, configuration,
security/operations docs where behavior warrants it, and current ledger.
No new planning or audit documents. Run focused pure and app/selection/
legacy regressions with true exits. Then run the same 15-command locked
gate and independent clean exact-B archive/artifact comparison plus fresh
noneditable install under Python 3.12, as 022-b. Reuse the existing
022-b driver patterns from its work-artifacts directory and create the
new captures in 022-c's directory. Verify exact source A, manifest-only B
and diff from the verified main above. Run managed gate and
all ten exact-B GitHub checks in parallel after freeze. Preserve frozen
published artifacts, gateway contract and legacy behavior. Live inference,
genuine Codex qualification, deployment, registry work and benchmark
dispatch stay NOT RUN.

## Execution boundary and synchronization

Use the same visible RIGHT pane %19 worker PID 598258 birth 150182858. The
one armed standard control reader is PID 1959842 birth 375752266, parent
598258, this worker's managed handle 48110. After its valid EOF-checked
ASCII `OK` frame returns, read the exact active/order, reconcile GitHub
and proceed. No duplicate reader or replay. If the worker process
actually crashes, restart only in RIGHT with exactly
`codex --yolo --profile early-beta`. No additional Codex/model-client
startup. Preserve the original FIFO pair, active agent profiles, protected
Qwen/18020, credentials, systemd, launch/network state and Gateway.
Use repo-local test tools and private per-round work artifacts only under
`/home/janezp/codex-supervision/slaif-local-coding/work-artifacts/oap-022c-work`.

Publish to the same PR. Push all implementation and unchanged activated
transcript bytes first, then atomically publish one complete immutable
report via same-directory temp file and rename. Verify remote report-only
SELF, its literal implementation parent and exact bytes. Send exactly
one standard response FIFO `OK` after publication, then arm one managed
standard `oap/bin/oap_fifo.py wait` for the control FIFO. If a real blocker
prevents full completion, publish precise partial evidence, name the
remaining acceptance items and use the same protocol.

# OAP work order — 022-b: pure source replacement transaction

Numeric objective 022, AMEND_EXISTING_PR. Update PR #30 only
(https://github.com/ulfe-lmi/slaif-local-coding/pull/30), branch
`oap/022-cache-source-replacement`, from report-only head
`51e8d89ffc0e335594be6dcfddaa25662d817b49` and verified main
`144af0bd5e34387afcb8e3f9ddf761eabd56e817`. The 022-a
implementation `d34c989e0e8381ef1f09833e5da764aed496eb11` earned the
inert profile selector and startup refusal. One TOML privacy criterion is
open. Whole 022 is open. No new PR, multi-objective work, merge or auto-merge.

## Scope

Implement the pure exact-span replacement and reference transaction from
docs/CACHE-IMPLEMENTATION-PLAN.md policy 12 and docs/CACHE-REWORK.md section
11. Include the narrow 022-a settings correction below. Keep
`create_app`'s fixed v1 startup refusal. Actual HTTP wiring, upstream tool
issuance, recovery IO and final R01–R05/S01–S02 evidence are later slices
of this same PR.

1. Derive the edit plan from the actual current decoded request, accepted
   017 observations, original 018-p proof/occurrence and 018-t admission
   witnesses, and actual 019/021 prepared current working set. Use the
   original segment and per-piece decoded-string carrier coordinates,
   joined to the actual input endpoint, tool call/result identity, exact
   source digest and UTF-8/character lengths. An interned entry may span
   several historical witnesses with different segment coordinates.
   Never substitute the representative proof or its offsets. The root's
   content span excludes its delimiters and environment tail. Use the
   earned Responses automatic-root shape, and accepted Responses and Chat
   read carriers. For a governing root selected through a read, use the
   selected root's own original witness, keep its carrier a tool result,
   and never issue two edits to the same root region. Never add Chat root
   acquisition or infer a workspace from an unearned shape.
2. Plan and apply all edits atomically without mutating the input. The
   operation preserves roles, non-source text, wrappers, prefix/suffix,
   printed delimiter lines, Unicode/CRLF outside the edits, images, all
   tool IDs/names/arguments/status/order and API fields. Preserve native
   initial-EXEC and poll piece associations. Each edit must be earned by
   complete attributable source, the exact current prepared context and
   a successful durable generation tied to the retained snapshot that
   the edit relies on. Use a narrow internal handoff for the generation
   proof using the accepted recovery outcome/pointer and actual snapshot,
   with in-memory synthetic fixtures. A boolean or free generation
   integer does not establish preparation. On nonusable selection,
   missing/failed/mismatched durability, stale snapshot or conflicting
   edits return no transformed payload and use the existing typed failure
   families. Unsupported/nonzero/truncated/unpaired/uncertain reads with
   candidate coordinates remain unchanged with the existing limitation.
3. Use two unambiguously versioned opaque marker kinds. A live reference
   identifies exact current compiled content actually present in the
   accepted selection. Authenticate markers using a domain-separated
   standard HMAC with supplied private per-session key material and scope
   it to the complete trusted namespace, original role, exact occurrence
   or root-source identity, and its segment/carrier association. Do not
   derive a private key from public digests, body/header assertions,
   upstream or Gateway credentials. The pure slice receives this key
   from an internal prepared context and does no generation, filesystem
   IO or retention; the application slice owns safe lifetime and recovery
   binding. Wire markers expose neither source identities nor credentials.
   Reject unknown/malformed/forged/cross-namespace/stale live references or
   incompatible carrier use in recognized source fields. Accepted replay
   of the same marker neither changes its authority nor creates a second
   edit. Ordinary text outside the marker carriers keeps its own role and
   is never recognized as marker authority.
4. For a known positively superseded original retained in history, use a
   distinct non-resolving evidence marker, tied to its original namespace
   and exact occurrence/source digest. It grants no current authority or
   access to stale compiled text, and is emitted only with the actual
   current required working set and its matching prepared generation.
   Support honest old raw replay and already transformed historical replay
   without rollback. A genuine new authoritative descendant with old
   bytes is a distinct occurrence and may reuse current compatible
   compiled content under the accepted currentness law. Mere absence
   from selection or uncertain/conflicting attribution never proves
   historical supersession. Where a current prepared optional source is
   omitted by the accepted selection, do not emit a dangling live
   reference. A non-resolving marker can represent that exact prepared
   occurrence only under an actual selection omission that leaves all
   required content or exact missing-binding guidance in the working
   set. Unproved coverage cannot remove required content.
5. Return or carry the exact selected compiled blocks and actual
   missing-binding guidance as part of the same successful pure result.
   Preserve original root/FILE/greedy-background roles. Off-graph or
   ambiguous tool content cannot gain system authority through the
   output representation. Marker validation must be usable before
   observation so a valid transformed root or tool marker cannot become
   a new raw source proof; it retains no stale compiled payload. Keep
   actual API placement, final-request budget/serialization and
   authoritative response/issuance integration in the application
   slice. This round earns a pure payload/reference and compiled-context
   pairing, not an upstream-body or readiness claim.
6. Fix the 022-a TOML migration privacy edge. With v1 selected, a malformed
   explicit legacy field in `[cache]` or `[constitution.rehydration]`
   currently reaches standalone nested validation before the fixed
   migration refusal and echoes its input in the rendered error. Prove
   the same real TOML path rejects at the intended boundary without
   echoing either synthetic canary, while preserving empty/default versus
   explicitly supplied default behavior and existing legacy loading.

## Evidence and verification

Exercise actual 017/018/019/021 records in the new focused tests and
inspect changed decoded fields and exact compiled pairing. Include
root-envelope replay with environment tail, both read endpoints, a
boundaryless whole bundle, a lean partition that preserves unadmitted
source/printed marker/prefix/suffix, and native multi-piece provenance
with Unicode/CRLF. Cover shared-entry distinct original coordinates,
all-or-nothing failure, scope/role mismatch, tampered or moved marker,
old raw replay versus stale live token, historical marker idempotence
and successful preparation with and without applicable optional
omission. Reuse existing resource limits and fail closed before unbounded
copy/parse. Keep private source, paths, IDs and marker key material out of
new reprs, errors, metrics and Git evidence. Update the existing human
and compact architecture maps (and their current mirrors) and the
configuration/replacement docs where needed. Keep the stage ledger scoped
to evidence actually run. Avoid new planning or audit documents.

Run the new focused tests and the existing config/app/selection regression
surfaces, then the same 15-command locked gate, clean exact-B archive
artifact proof and Python 3.12 fresh noneditable install required in
022-a. Use the same remote main baseline for the diff and exact source A
and manifest-only B identity. After the exact candidate freeze, run the
managed local gate and exact-B GitHub checks in parallel. Record actual
exits and all ten exact-B GitHub checks before publishing the report.
Live inference and actual Codex qualification stay NOT RUN. Preserve
frozen publications and all existing PRs outside PR #30.

## Execution and publication

Use the same existing visible RIGHT pane %19 worker, PID 598258 birth
150182858. The already-armed standard control reader is Python PID
1529574 birth 371076654, managed terminal 44901, under the worker's
shell child 1529573 birth 371076652. After that exact reader returns the
valid `OK` frame, read `oap/active` and require this one matching order.
No duplicate reader or replay. Only a verified worker crash permits a
restart in RIGHT, with exactly `codex --yolo --profile early-beta`.
No additional Codex/model-client startup or service, Gateway, profile,
network, credential, registry, deployment, benchmark or cutover changes.
Use repo-local tools and keep all new manual artifacts in the private
project work directory
`/home/janezp/codex-supervision/slaif-local-coding/work-artifacts/oap-022b-work`.
The existing FIFO objects and paths remain in use.

Publish implementation and the unchanged activated order and active bytes
to PR #30. Then create one matching immutable report by writing and
flushing a complete same-directory temporary file and atomically renaming
it into place. Verify the report-only SELF commit, its literal
implementation parent, exact remote bytes and PR head before the one
response FIFO `OK`. Arm one managed wait with the standard control
helper after sending the response. Strategy owns acceptance and merge.

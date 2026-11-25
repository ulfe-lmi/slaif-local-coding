# OAP work order — 022-g: count the emitted request envelope

Numeric objective 022, AMEND_EXISTING_PR. Amend only
[PR #30](https://github.com/ulfe-lmi/slaif-local-coding/pull/30), remote branch
`oap/022-cache-source-replacement`, from verified report head
`60b063b9ba1f4aff2bc34e56f34a5d811449d6c0` on main
`144af0bd5e34387afcb8e3f9ddf761eabd56e817`. No new PR, merge or auto-merge.
The approved CACHE-REWORK requirements and 022 evidence remain fixed.
Preserve the delivered 022-a through 022-f behavior.

## Scope and tests

1. At exact F, the bounded normal FastAPI/fake-upstream test sets the
   validated envelope's `max_messages=1`. Its first request has one
   legitimate root-bearing Responses message and no `instructions`.
   It returns 200 and forwards one user message plus generated system
   instructions. Replaying the exact emitted body returns 422. The
   existing transaction counts the source-replaced intermediate, before
   a new system frame or separators exist. Count the actual emitted
   placement by deriving the ordinary-content view from the final
   outgoing payload and excluding the exact authenticated governance
   span only. Keep its complete system frame and separators, byte/token
   and item bounds, and the separate compiled aggregate, tool, image,
   and generation reserves. Add actual app first-over and in-bound
   controls, including equal first/replay disposition and byte-stable
   output at the accepted message limit. Exercise the newly inserted
   Responses instructions and Chat system frame. Preserve the accepted
   whole optional omission replay and v1 failure/status behavior.
2. The F matcher handles literal delimiters but its header loop rescans
   the tag candidates and may reconstruct/hash the same overlapping
   ranges repeatedly. It is not the bounded framing or equivalent
   single-pass validation explicitly required by F. Bound scanning and
   candidate authentication work using the existing request/render
   limits, with a deterministic non-overlapping frame or equivalent
   algorithm. Preserve authenticated placement and tested no-data-loss
   behavior for caller literal text, embedded literal delimiters,
   suffix separators, current region replacement, and legitimate
   fixed-point replay. Retain the same protected key and independent
   MAC domain. Keep the implementation and verification local to
   this wire-placement scope; no new protocol elsewhere.

Update current architecture/ledger where needed. Keep prior orders,
reports and RC10 immutable. No new planning or audit documents. Run
focused true exits for app, replacement, tokenizer budget, selection
and legacy. Then the same full fifteen-command locked gate with
pytest using its ordinary short OS temp path, exact-B clean
archive/both-artifact and fresh Python 3.12 noneditable proof and
all ten GitHub checks. Use the F drivers as patterns, with their
repo path changed to the linked checkout below. Keep all durable
captures and artifacts project-contained. Use no additional Codex or
model-client startup and no live service/inference, profile/credential,
network, Gateway, deploy, registry, cutover or benchmark changes. The
023 negative-path/stress-test matrix and 024 actual-model/client stages
remain separate.

## Checkout, handshake and publication

The original right worker stays in pane %19, PID 598258 birth 150182858,
early-beta xhigh. Its sole standard control reader is PID 1183514 birth
419397811, parent bash 1183512 under that worker, managed handle 93742.
Collect the valid EOF-checked frame with exit 0 and resolve the active
order. Read the full governance in order and refresh after compaction.

The primary checkout has operator-owned unstaged wording edits. Do all
022-g file, environment, test, commit, and artifact work in this linked
checkout at the exact remote F head:
`/home/janezp/codex-supervision/slaif-local-coding/work-artifacts/oap-022g-work/checkout`.
It contains byte-identical copies of the strategic active/order and the
operator's local AGENTS.md. The latter remains unstaged. The primary
checkout's other files are outside this round and must not be modified.
The linked checkout is detached to avoid moving the branch checked out
in the primary working tree. Verify the exact branch and PR remotely;
push your linked-checkout commits explicitly to the same existing
`refs/heads/oap/022-cache-source-replacement` by normal fast-forward.
The remote branch, objective and PR stay the same. Keep durable
per-round artifacts under `/home/janezp/codex-supervision/slaif-local-coding/work-artifacts/oap-022g-work`.

Push implementation, current documentation and unchanged transcript
before publishing exactly one immutable report-only SELF. Verify the
remote head, literal implementation parent and exact report bytes.
Send exactly one standard response FIFO OK, then arm one standard
control FIFO reader. A restart is authorized only after a verified
crash, visibly in the right pane, using exactly
`codex --yolo --profile early-beta`.

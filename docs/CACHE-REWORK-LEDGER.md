# Dependency-bundle cache rework — stage ledger

**Status:** Planning ledger for the human-approved dependency-bundle cache
rework. The requirements are the ten approved rules in
[the human handoff](CACHE-REWORK.md); the resolved engineering choices are in
[the strategic implementation plan](CACHE-IMPLEMENTATION-PLAN.md). This ledger
maps every named acceptance criterion to its owning implementation stage and
records implementation/acceptance state.

This objective is the bounded pure-observation stage (017). **No v1
runtime mechanism is active in the adapter and none is qualified; every
runtime criterion below is still `NOT RUN` (planned).** Stage 017-a has
landed the D01-D05 slice as inert, typed, pure modules under
`src/slaif_local_coding/constitution/bundles/` with the named evidence
recorded below; those rows are `PENDING` strategic acceptance, not
delivered behavior. The 017-a COMPLETE claim was **not accepted**: an
independent synthetic observer probe at the final report head failed 14 of
23 cases (findings A-E: real-format wrapper, read-grammar membership,
per-call cwd, tool/endpoint evidence, Unicode/bounds and parser bounds, plus
the diverging normative compact mirror). Stage 017-b corrects exactly those
bounded defects on the same PR with direct regression tests; it adds no new
read families. The 017-b COMPLETE claim was **not accepted** as completion
of the A-E contract: separate read-only private-clone probes directly at
the final 017-b report head failed 10 of 16 literal-argv-semantics cases
and 3 of 5 actual-endpoint-selection cases (quoted option/terminator/stdin
false membership, NBSP false split, malformed-workdir
`UnicodeEncodeError`, exact member-limit off-by-one, raw helper repr, and
ambiguous mixed containers acquiring content without a proven actual
endpoint). Stage 017-c corrects exactly those bounded defects on the same
PR with direct regression tests; it adds no new read families. The
017-c COMPLETE claim was **not accepted** as endpoint-authority
completion: a separate independent root-context probe at the final 017-c
report head passed 2 of 6 cases (explicit Chat, mixed and invalid
endpoints still minted valid Responses roots from unused input, and a
Responses string input plus a Chat pair was treated as unambiguous Chat).
Stage 017-d first corrects that bounded root-domain prerequisite (root
observation scoped to the actual selected Responses domain; string-input
plus messages is a mixed shape) as an independently committed
prerequisite, then earns the finite read-plan surface D06/D07/D08 (all-
cat / literal-cd `&&` plans, absolute literal `cd` transitions, bounded
literal `echo` outer boundaries, per-read versus global exit evidence,
whole-plan bounds) in the inert module
`src/slaif_local_coding/constitution/bundles/compound_reads.py`
(grammar `literal-read-plan/v1`); it adds no graph/cache/compiler/app
integration. Stage 017-e is the bounded correction of that slice on
the same PR: the echo outer-boundary law now types option-like
dash-leading quoted literals (`-n`, `-e`, `-E`, combinations,
repetitions, either quote kind) as `ECHO_TARGET_UNSUPPORTED` instead
of inventing a false boundary (the actual `echo '-n'` writes
nothing), and every observation produced through the finite-plan
parser carries the actual `READ_PLAN_GRAMMAR` identity across all
outcomes while observations the single grammar earned keep
`READ_GRAMMAR`; it adds no new read families and no loops/chunks.
Stage 017-f earns the bounded pure literal-loop slice — the D07 loop
criterion, not a blanket D09/D10 completion — on the same inert
surface: the human 6.2 loop forms are recognized as finite parsed
data with deterministic requested members; the all-success guarded
pure-cat variants earn one ordered whole-source bundle under a
wrapper-proven exit-zero/untruncated/present completion (one
concatenated region, one exact digest, no fabricated internal
boundaries or member hashes); unguarded and echo-labeled forms stay
non-removable with typed iteration/outer-attribution limitations; and
every observation the loop parser evaluates carries the actual
`literal-loop/v1` identity (new pure module
`src/slaif_local_coding/constitution/bundles/literal_loops.py`,
grammar `literal-loop/v1`, whole-loop expanded-operand budget never
multiplied per iteration). The D06/D08 source-attribution and
status laws are preserved unchanged. The remaining D09/D10 scope
(multi-chunk process completion proof, remaining truncation matrix,
duplicate/substitution/branch matrix) moves to a later same-PR
suffix: the earlier planned 017-e loops/chunks draft is superseded
by the 017-e correction. Stage 017-g is the bounded correction of
that loop slice's word/separator law on the same inert surface: the
unquoted `;` is its own syntactic element (a standalone token), so a
quoted prefix plus a literal suffix touching the list separator
(`for f in "A".md;`) stays one unearned word typed `QUOTED_OPERAND`
— never two members (`A` and `.md`) — with attached and spaced
separator forms observing identically, the first/last/single list
positions agreeing, and the plain and whole-word quoted controls
unchanged; the contract's member-digest prose is corrected to the
exact occurrence law (a file's digest is proven only when exactly one
member occurrence covers the entire attributable region; a duplicate
`A,A` has width one but unknown individual versions/boundaries and no
per-file digest). It adds no client capture, process collector,
chunk family or runtime change; the process/chunk association remains
planned for a later same-PR suffix, subject to review. Stage
017-h attempted that process/chunk association evidence path but was
**interrupted and closed as PARTIAL, non-delivery**: the original
worker persisted full provider requests and raw child stdout/stderr,
exceeded the prescribed ingress and attempt bounds, and triggered a
client-startup plugin sync side effect (a ~25 MiB plugin git pack in
the fresh child CODEX_HOME); the truthful closeout removed the
proven-owned scratch root without reading or copying any captured
body. 017-h produced **no repository utility, test, fixture or
documentation change** and earned **no format or process
acquisition**; D09/D10 were not advanced by it. Stage 017-i supersedes
the collector draft with a corrective **offline process-capture
utility** (`scripts/real_client_capture.py`,
`scripts/real_client_capture_fake_child.py`,
`tests/test_real_client_capture.py`) for independent strategic review:
stdlib-only, explicit opt-in, fail-closed, hard-capped (one actual
attempt, 20 requests, 120 s, 1 MiB per request, 256 KiB selected,
4 MiB child output), privacy-law enforced in code (bounded in-memory
parsing, allowlisted synthetic extraction, exact-byte digests, no raw
content persistence), and inert (not wired into the adapter runtime).
Its actual-client path is unreachable by construction (startup
readiness is `not_ready`: the candidate plugin/telemetry/update
controls remain unverified from local static evidence) — REJECTED
historical claim, superseded by 017-j: the path is input-gated, not
structurally unreachable — so this round
performs no actual client, provider or model call and acquires no
format evidence; the actual capture and the process/chunk collector
remain `NOT RUN` for later exact orders. Stage 017-j amended that
same inert utility from independent review (frozen review scripts at
the 017-i head exposed 11 check failures across the selection,
resource, and process surfaces; the file-boundary control had already
passed 3/3 and stays passing): selection is bound to the
controller's issued call records (exact issued ID, tool family/name,
declared step/command and expected argument values,
controller-issued process ID) with advancement requiring completed
outputs carrying issued metadata; proven selected synthetic result
text is retained losslessly after ownership/shape/byte verification
against the owned seeded workspace (selection schema v2, still
`fixture_authority: none`); the selected cap is enforced on the
exact serialized UTF-8 record bytes; every fixture request counts
against the per-run budget before route/auth/body branches;
preflight output is bounded while receiving; pre-existing
directories are never chmoded; readiness/authorization metadata
schemas are closed; and the absolute deadline spans owned
descendants. The 017-i "unreachable by construction" wording is
superseded: the actual-client path is input-gated (caller-supplied
`ready`/authorization records can launch the bound stand-in); this
version's generated readiness verdict is `not_ready`, and 017-j
performed no actual client, provider, or model call. 017-j earned
no format or process acquisition; D09/D10 remain `NOT RUN` for
later exact orders. Stage 017-k amended that same inert utility from
a second independent review (two additional frozen scripts at the
017-j implementation head exposed 5 failures among 10 checks with
valid controls; the twelve original frozen scripts and their hashes
remain unchanged and passing): (1) RUNTIME frame selection is bound
to the controller's ACTUAL issued records created before each
provider request (a preloaded/anticipated/forged call is never
selected before the controller issues it; the pure-facade candidate
parsing stays a distinct fixture mode, and a constructor or manually
populated state is not runtime provenance evidence); (2) finalization
quiesces the owned provider BEFORE final validation/publication
(freeze, stop accepting, close the listening socket, bounded handler
join) and validates/serializes the explicit frozen frame snapshot (a
real late request at the public shutdown boundary is byte-verified
and stripped to `content_unverified`, its marker bytes reaching no
persisted record); (3) EVERY HTTP method and error-dispatch path
consumes the per-run budget with fixed sanitized non-echoing errors
and accepted handler concurrency is bounded with honestly reported
teardown; and (4) generated readiness records round-trip the
validated live-facts flag count faithfully for zero and every
nonzero known flag, while ACTUAL malformed Unicode (lone surrogates)
is rejected with the fixed typed `malformed_unicode` reason before
any encoding/hashing/retention. 017-k performed no actual client,
provider session, or model call; it earned no format or process
acquisition; D09/D10 remain `NOT RUN` for later exact orders.
Stage 017-l repaired the two remaining offline capture boundaries
on that same inert utility from a third independent review (a new
source-driven probe at the 017-k implementation head exposed 2
failures among 5 checks with 3 valid positive controls; the
fourteen prior frozen scripts and their hashes remain unchanged and
passing): (1) quiesce now closes every admission-owned request
socket (a bounded registry capped at the concurrent-handler cap)
as soon as no new admission can join it, so an in-flight bounded
read a per-read timeout cannot stop (a progressing drip) is
unblocked by an effective socket shutdown, the peer observes
closure, thread-start failure is counted and closed, repeated stop
is safe, and an incomplete teardown (a handler that outlives the
bounded grace) is honestly reported and can never yield a
completed outcome (fixed `cleanup_failed`, no raw error details);
and (2) selected result text verifies against the IMMUTABLE
ORIGINAL seed bytes (default plus every explicitly supplied extra
synthetic workspace file) recorded before the child launches,
never a child-writable file reread at finalization — a child that
rewrites its own seed after a legitimately issued read cannot
redefine the purported original, and tampered or unverified text
is stripped with the fixed `content_unverified` reason (or a typed
non-echoing failure plus safe cleanup), reaching no persisted
record, console, repr, or diagnostic. 017-l performed no actual
client, provider session, or model call; it earned no format or
process acquisition; D09/D10 remain `NOT RUN` for later exact
orders.
Stage 017-m repaired the per-request pure read-observation
identity/causality pairing on the same inert surface (no capture
utility/child modification, no actual capture, no process
collector) from independent review of the current implementation
(new frozen probe
`check-observer-pairing-causality.py`; 4 of 8 cases failing at the
017-l implementation head with both ordinary Responses/Chat controls
valid). (1) Identity conflicts now precede read eligibility: the
schema-evidenced call-ID inventory is eligibility-independent, so an
unknown/ineligible call colliding with an eligible call ID is a typed
`DUPLICATE_CALL_ID` conflict instead of disappearing through
filtering; unknown calls never acquire a source; unrelated unique
unknown calls are neither recorded nor allowed to poison separate
valid chains; arbitrary nested text objects carrying id/name are not
call records; and absent/null/empty (`MISSING_CALL_ID`) or present
non-string (`MALFORMED_CALL_ID`) call IDs stay observable, never
pair, never acquire content, and no ID is ever invented. (2)
Structural causality: a result attaches to its matching call only
when its exact numeric structural position follows the call's (the
Responses `input` item index; the Chat `messages` index of the
assistant message carrying the call) — never from lexical call IDs,
JSONPath string sorting, or JSONPath evaluation; a pre-call result
keeps its chain typed `PRE_CALL_RESULT`, non-removable, with no
bundle/member digest, no source span and no proven-executed claim,
and missing initial calls remain unsupported. The public D10
composition matrix (Responses and Chat: ordinary valid reads amid
unrelated calls, same-ID conflicts across supported/unsupported
names and families, identical/conflicting duplicate calls,
missing/empty/malformed IDs, orphan/mismatched/pre-call outputs,
duplicate same-call results remaining unsupported absent later
earned process-chain evidence, non-monotonic IDs and >=10 structural
positions, independent valid chains still earning exact source
span/digest/members/width) and the pure D09 unsupported/partial
negative matrix (command substitution `$()` and backticks,
false/conditional/unexecuted branches, partial `head`/`sed` readers,
known truncated/missing/running/unknown wrappers — typed
unsupported/partial, never complete whole-file acquisitions —
contrasted with the exact proven empty successful output) are earned
by the new public suite `tests/test_bundle_d10_matrix.py`; all
previously earned literal read/plan/loop positives, exact spans,
aggregate work bounds and occurrence/member-hash/slot-width laws are
preserved. 017-m performed no actual client, provider session, or
model call; it earned no format or process acquisition; D09
multi-chunk/process association remains `NOT RUN`/deferred (the D09
partial negatives are not multi-chunk evidence), and the D10
delivery claim requires independent strategic acceptance.
Stage 017-n completed the per-request identity-inventory repairs
required by 017-m on the same inert surface (no capture
utility/child modification, no actual capture, no process
collector) from independent review of the current implementation
(new frozen probe
`check-observer-identity-inventory-boundaries.py`; 5 of 8 cases
failing at the 017-m implementation head with all 3 positive
controls valid). (1) The Responses `custom_tool_call` wire family
now joins the schema-evidenced call inventory alongside
`function_call`: identity bookkeeping only — it earns no custom-tool
read parsing, execution or acquisition (a custom call named like a
supported tool still never acquires), its opaque `input` is never
captured as arguments or reinterpreted as a shell/source oracle, no
generic unknown-family wildcard recognition is invented, and the
supported namespace-declaration law is unchanged for acquirable
families; an exact colliding ID makes the ambiguous eligible chain
typed `DUPLICATE_CALL_ID` non-removable with no acquired
digest/span/proven members (both collision orderings, repeated
identical/conflicting records; every relevant occurrence
observable, never first-match), while a unique unrelated opaque
custom call neither records nor poisons a separate valid read.
(2) `max_commands`/`max_outputs` are now enforced against the
**complete** relevant inventory — every schema-position call record
(unsupported names, opaque custom records, missing/empty/malformed
IDs) and every result record (including invalid IDs) — before any
identity map or typed diagnostic is retained: a fixed non-acquiring
`OVER_BOUND` record (no truncated acquisition missing a later
collision; at-limit and one-over on Responses and Chat, including
many `tool_calls` in one assistant message, and a late collision
beyond any retained prefix), the scan itself bounded by the
existing `max_items` item bound, the bound scoped to the selected
domain under explicit endpoint selection, and mixed input bounded
across its inspected domains while the useful unknown+valid
within-limit controls are preserved (no blanket reject-all). (3)
Absent/null/empty result IDs are typed `MISSING_RESULT_ID` and
present non-string result IDs typed `MALFORMED_RESULT_ID` — fixed,
non-echoing, unpaired limitations on Responses
`function_call_output` and Chat `role=tool` positions that never
invent an ID, hash an unhashable value, attach the output to any
call, or acquire, while separate well-formed chains remain useful
within the total limits and the existing duplicate/missing/
mismatched/structural pre-call typing and namespace/domain
separation are preserved. The public regression proof (both
collision orderings, repeated identical/conflicting records,
supported/unsupported/custom positive controls,
missing/null/empty/list/dict/number result IDs, all-inventory
bounds, late collision beyond the retained prefix, exact valid
digest/source slice/members/width, input immutability, no acquired
state for rejected chains, bounded typed metadata, non-echoing
representations) is earned in
`tests/test_bundle_d10_matrix.py::TestWireFamilyInventoryAndBounds`;
all previously earned D10 numeric causality tests, selected/mixed/
ignored domain behavior and literal read/plan/loop positives are
preserved with unchanged inputs and non-echoing reprs. 017-n
performed no actual client, provider session, or model call; it
earned no format or process acquisition; D09 multi-chunk/process
association remains `NOT RUN`/deferred, and the D10 delivery claim
requires independent strategic acceptance.
Stage 017-o completed the two remaining per-request boundary
repairs on the same inert surface (no capture utility/child
modification, no actual capture, no process collector) from
independent review of the current implementation (new frozen probes
`check-observer-inventory-allocation.py` and
`check-observer-id-representation.py`; at the 017-n implementation
head the allocation probe passed only its one valid at-limit
positive control with four resource ceilings failing (observer
peaks ~8.98/8.26/7.78/7.80 MiB vs the 2 MiB ceiling) and the
representation probe passed only its two positive controls with six
non-echoing negatives failing). (1) The complete relevant
call/result inventory bounds are now enforced **before retention**:
a no-retention streaming preflight decides `max_commands`/
`max_outputs` over the complete inventory (every schema-position
call record, every result record including invalid IDs) and stops
at the first exceeded limit, so an over-bound request is the fixed
non-acquiring `OVER_BOUND` before any record tuple, location
string, ID map, typed diagnostic, argument/wrapper parsing or
identity map is retained or built; the bounded collection pass
retains at most the declared counts; the 2 MiB allocation
regression ceiling at inventory budget one (excluding inputs,
imports and full-payload fingerprinting — a generous regression
ceiling, not a new runtime setting or total-RSS guarantee) is
proven on large prebuilt Responses calls, nested Chat `tool_calls`,
Responses results and Chat results at limit one. (2) Exact
internal call/result IDs and association fields stay usable while
operational `str`/`repr` of report/read/unpaired objects never echo
private ID values: a non-empty `call_id` renders as the fixed
`<private-id>` placeholder, the observable no-ID state (empty
string) stays exact, and no ID is invented, hashed or
re-serialized; fixed enums, counts, locations, spans and digests
remain observable; synthetic canaries only. The public regression
proof (large prebuilt inventories at limit one with measured
bounded allocation, at-limit useful reads with exact
digest/span/member/width, one-over/late-collision/invalid-ID/
ignored-domain/mixed shapes, input immutability, internal-ID
exactness plus non-echoing `str`/`repr` on Responses and Chat
paired/orphan/duplicate/missing-result paths) is earned in
`tests/test_bundle_d10_matrix.py::TestInventoryAllocationAndIdRepre
sentation`; all previously earned D10 inventory/causality tests,
selected/mixed/ignored domain behavior and literal read/plan/loop
positives are preserved with unchanged inputs. 017-o performed no
actual client, provider session, or model call; it earned no
format or process acquisition; D09 multi-chunk/process
association remains `NOT RUN`/deferred, and the D10 delivery claim
requires independent strategic acceptance.
Stage 017-p extends the same inert surface in two bounded parts.
(1) The per-nested-container scan guard: each inspected assistant
`tool_calls` list is length-tested against the existing `max_items`
item bound before it is iterated, parsed or retained (O(1) per
list, counting every raw entry regardless of schema, type or ID),
so an over-limit nested list is the fixed non-acquiring
`OVER_BOUND` and `max_items` is explicitly a per-container bound
(never a total across lists — an at-limit nested list observes
normally); non-assistant `tool_calls` fields are uninspected; the
017-o structural no-retention preflight remains the retention
proof and the 2 MiB allocation regression ceiling remains
supplementary (not a scan-count oracle).  (2) The disposable-CI
containment capability (a D10 prerequisite; the first remote job
run at the previously published head `ec08a1b` failed
`runtime-invalid`, and this round corrects the runtime-shape
handling — the capability qualification is `PENDING` strategic
review, with the exact execution outcomes/SHAs in the immutable
round report
`oap/reports/017-p-observation-native-fixture-prerequisites.md`):
`scripts/cache_native_containment_probe.py` (in-container stdlib
probe; closed JSON pass record: dedicated nonroot uid/gid,
all-zero capabilities, no-new-privs, seccomp filter mode, private
pid/mnt/ipc/uts/net against the shared user namespace, parent
proc/sentinel absence, private loopback echo, parent listener
unreachable, read-only rootfs, explicit rw bounded tmpfs roots,
exact memory/pids/writable-storage limits and the measured swap
allowance with its closed source enum (a missing or underivable
measurement is never a measured zero), keyring syscall
denial — x86_64 `add_key`=248, `request_key`=249 four-argument,
`keyctl`=250 unknown command, expecting EPERM — and child deadline
kill; in hang mode a per-run token-bound live owned descendant
(finite 120 s child / 600 s PID1 lifetimes) is spawned before the
pass record, and the exact record is flushed to the pipe before
the finite hold) and `scripts/cache_native_containment_ci.py`
(host
runner whose entry guard refuses any context that is not both
`GITHUB_ACTIONS=true` and `RUNNER_ENVIRONMENT=github-hosted`):
digest-pinned byte-identical-base fixture image,
create-before-start ownership (bare 64-hex CID registered before
any start; pre-existing name collision never adopted), the exact
confinement surface (`--network none`, read-only rootfs, dedicated
nonroot uid, cap-drop ALL, no-new-privileges, explicit
`seccomp=builtin`, 512 MiB memory with no swap, pids 64, 1 CPU,
explicit tmpfs roots), closed inspection extraction (actual
`ReadonlyRootfs` field plus the exact default runtime identity via
bounded reviewed queries of the real Moby lowercase `path` shape —
the stock bare `runc` name, empty path or a shape-validated-only
absolute path, never a daemon-supplied executable), the ordered
parent-death proof (one
exact token-bound owned occurrence positively observed before the
registered container is killed; its disappearance and the
container's verified absence after; the unrelated parent-owned
sentinel must survive; a vanished-entry /proc scan is never
conflated with absence and any other read error fails the scan),
bounded capture (reader-thread-owned pipe; a leader exit with a
held pipe converges by the exact owned group kill after a bounded
grace; a failed capture is the fixed closed state
`output-read-failed`, never an empty-success output or an uncaught
thread exception), verified image removal (result-checked `rmi`
plus a successful authoritative query reporting no such
image/object — a daemon/transport failure is a distinct unverified
state, never conflated with absence; cleanup failures stay visible
even when a primary check also failed) and a fresh owned 0700
scratch root validated as-given (no symlink or `..` alias
laundering of a pre-existing target).  Public local proof:
`tests/test_bundle_d10_matrix.py::TestNestedScanBounds` (12 tests)
and `tests/test_cache_native_containment_ci.py` (61 orchestration
tests — fake docker emulation plus tiny real owned children only;
no docker daemon, namespace or syscall probe locally).  Remote
proof: the new `cache-native-containment` CI job on a disposable
`ubuntu-latest` hosted runner (stdlib only; no secrets forwarded
to the fixture — the job maps no secrets and the runner accepts no
credentials — fresh owned work root under the documented
`RUNNER_TEMP`; the job ran once at `ec08a1b` and failed
`runtime-invalid` there; the first remote run of this head and its
outcome are recorded in the immutable round report, not restated
here).  017-p performed no genuine client, provider
session, or model call; it earned no format or process
acquisition; the capability proof does not qualify a genuine
native client; D09 multi-chunk/process association remains `NOT
RUN`/deferred and the D10 delivery claim still requires
independent strategic acceptance.
Stage 017-r lands the serial right-pane native fixture
preparation — a small inert prerequisite for the later
human-authorized foreground handoff, with no D-syntax, parser or
product change (the required-syntax matrix in
`docs/CACHE-OBSERVATION-CONTRACT.md` section 11b records the
carried P/Q states of the handoff 6.2 literals and D01-D10 with
their actual test assertions; the ls+cat literal is typed
non-acquiring — `COMMAND_UNSUPPORTED` + `OUTER_BOUNDARY_UNPROVEN`,
UNSUPPORTED even at global exit 0 — and the unguarded/labeled loop
literals are recognized membership with `LOOP_ITERATION_UNPROVEN`
(labeled adds `OUTER_BOUNDARY_UNPROVEN`), non-removable at
composition; both required-syntax audits remain pending).  It adds the
typed fixture model (phases, budgets, closed record schemas,
bounded diagnostic traversal), the 21001 PID1 fake
provider/issued-registry controller, the 21002 stand-in subject,
the 21001 exporter client, the distinct fixture image
(dedicated nonprivileged 21001/21002 identities; 0555 binary PATH
entry plus immutable 0444 public LICENSE/NOTICE) and the host
runner driving ten fresh-container scenarios on disposable
GitHub-hosted CI only (the new Python-only
`cache-native-fixture` job; no job or test line invokes the native
binary — asserted statically).  The concrete future serial
foreground handoff runbook (order section 5 — exact worker
job/TTY/PGID discovery, verified stop/restore of the same Bash
job, the exact foreground attach, and the 21002 environment
handoff) is recorded in
`docs/CACHE-OBSERVATION-CONTRACT.md` section 11c (preparation
only; no stop/resume/local Docker/native execution in 017-r).  Confinement is measured, not
inferred: `--network none` loopback, read-only rootfs, cap-drop
ALL, the actual SecurityOpt no-new-privileges/builtin-seccomp
strings, private pid/mount/ipc/uts/net, no caller-configured host
mounts/devices (daemon-standard tmpfs facts stay distinct), 1 GiB
memory / swap 0 / CPU 1 / PIDs 96, the reconciled writable-data
surface (three owned tmpfs budgets, 192 MiB total, plus the
daemon's /dev/shm explicitly bounded to 64 MiB — 256 MiB
effective total; the old three-roots/192 MiB-only claim does not
apply), `--log-driver none` verified by inspection of the actual
HostConfig schema (ShmSize, and the null-or-empty
Binds/Devices/VolumesFrom/DeviceRequests absence grammar,
non-empty values still denied); the 21002
subject measures its own identity, capability sets, namespace
comparison, loopback-only reachability, the reviewed keyring-denial
ABI, effective resource bounds and the reconciled writable-data
inventory from its ACTUAL mount table (bounded table input;
kernel virtual/device classes distinct from writable data; an
unlisted writable data mount or a missing documented root fails
closed; the masked /dev/null file aliases of runc's maskPaths
are admitted only on the exact source-root file identity, the
narrow known-default path and the chr 1:3 device, counted as
device surface, never writable data).  The public pinned Codex
0.164.0 musl archive
(`rust-v0.164.0`, OpenAI commit
`6aaac694803004a63c6f393d153c96d22521a6b9`, SHA256
`90dd0b03b28afcb7fa733a4f73b413db2916a47347efd43fb669cc1c774ee8e4`,
114,979,035 bytes) is fetched, size+digest-verified before bounded
single-member extraction (unsafe member shapes rejected with fixed
reasons), and statically hashed — never executed in R; the pinned
public LICENSE (10,926 bytes) and NOTICE (242 bytes, the
Ratatui-derived MIT credit) are retained with verified byte
identity; signature verification `NOT RUN`.  Accounting is one
non-resettable host ledger shared with the single run deadline
(distinct measured quantities: admissions/refusals, drained vs
retained bytes — timed-out captures charged their measured drained
total, provider requests vs wire attempts vs outcomes vs
readiness polling; pre-work worst-case bound checks (no held
amount stored), scenario-end measured charges, no
reset/refund); the post-teardown /proc scan
rejects over-bound listings before any presence/absence claim;
cleanup is exact-owned with honest unverified states, verified
scratch-root destruction, and atomic no-overwrite evidence
publication (concurrent destination preserved, inside-work and
link/foreign-owned paths refused).  Public local proof:
`tests/test_cache_native_fixture.py` (207 tests),
`tests/test_cache_native_fixture_controller.py` (33),
`tests/test_cache_native_fixture_standin.py` (76),
`tests/test_cache_native_fixture_ci.py` (218 — FakeDocker
orchestration with its named failure paths, the one-shot
host-cancellation and cleanup-timeout sweep tests, actual-path
capture tests, actual-path loopback wire tests, protected
publication fault tests, actual archive/fetch helper negatives
against small synthetic bytes and fake HTTP, and the runner's
closed failure diagnostic (one closed stage token — the original
failure's stage, preserved separately from the cleanup stage —
plus a closed-record validation rejection mapped only through the
model's finite field universe, owned timeouts named
"deadline-expired", all other escapes "internal"; no raw
exception/record/traceback reaches the job log); no
docker daemon, namespace or syscall probe locally; no secrets
forwarded to the fixture).  Remote proof: the
`cache-native-fixture` job on a disposable `ubuntu-latest` hosted
runner (fresh owned work root and evidence destination under the
documented `RUNNER_TEMP`); its actual run outcome is recorded in
the immutable round report.  017-r performed no genuine client,
provider session or model call; it earned no format or process
acquisition; the bounded 017-r fixture preparation is accepted
(strategic decision at head `2ce9dcd`, with the recorded wording
limitations in `reviews/017-r-decision.md`), the serial
foreground handoff itself remains a later separately authorized
order; D09 remains `NOT RUN`/deferred; no v1 runtime claim.
Stage 017-s lands the local fixture preparation and one
bounded Python-only local rehearsal on the live host (the
order-bound local authority of its section 2: only the already
available Docker daemon and exact freshly owned fixture
resources; no install/start/restart/reconfigure of Docker, no
groups, packages, security, network or daemon-default changes,
no protected-service touch, no privileged or host namespaces;
fake tests remain the primary verification layer) — a
repo-owned stdlib-only preparer/supervisor
(`scripts/cache_native_fixture_local.py`) reusing R's validated
image/model/controller/exporter/stand-in, guarded executor,
measured confinement, single run deadline and ledger, artifact
acquisition and ownership helpers (no copy of the CI runner, no
general framework).  One long-lived non-Codex Python fixture
owner (the supervisor) owns every Docker operation through the
closed guarded executor, the exact registry (CID registered
BEFORE start, image identity, build intent, env file), the
single 1800 s END anchor plus one bounded 600 s cleanup grace,
the non-resettable ledger and the final evidence; a thin CLI
caller drives the protected bounded prepare / observe /
rehearse / finish / abort lifecycle over a 0600 socket in a
protected 0700 control root outside the disposable work root,
so a caller death, second phase or new directory cannot stop,
reset or re-admit the run (the owner converges its own
exact-owned cleanup on its own remaining budgets; container
termination is by docker on the exact registered CID only, no
host PID signalling).  Section 2 verified local endpoint
binding: the documented default unix socket
(`/var/run/docker.sock`) is verified read-only by lstat (must
exist as a socket file; never connected), corroborated by the
daemon-declared name equal to this host's hostname through the
pinned bound executor; every run Docker child inherits a
FROZEN once-per-owner environment with DOCKER_HOST pinned to
that verified socket and the overriding context selection
removed (a stored currentContext or later HOME/DOCKER_CONFIG/
DOCKER_CONTEXT drift cannot redirect a later action); an
explicit remote selection refuses before any mutation and no
endpoint value is ever echoed.  Prepare measures the same
reviewed confinement as R and verifies the env-file handoff
(0600 under 0700, exact two synthetic keys, removed on every
path) and the PTY attach with zero wire; rehearsal consumes the
one-shot diagnostic with the existing Python stand-in under
21002; finish is variant-aware (python-rehearsal / unobserved /
external) with the retained summary bound to the decoded
payload; `native_started` / `worker_stopped` / `codex_invoked`
stay false throughout.  The ONE rehearsal ran EXACTLY ONCE,
bound to implementation head `2a9c44e2ee327b965828bafdfcaf444abc3a581c`
(source inputs `54ef177`), and PASSED with fresh owned roots,
leaving no prepared container, supervisor, listener, key file
or owned image (container and image removals
`absent-verified`, zero descendants, owner converged); its
actual measured facts, the preserved pre-rehearsal CI failures
and cleanup outcomes are recorded in the immutable round
report (the later doc pass binds the measured source/facts and
final provenance).  Public local proof:
`tests/test_cache_native_fixture_local.py` (49 tests —
order-bound opt-in vs the production hosted-env guard (ambient
GITHUB_ACTIONS refused at construction with no attempt recorded)
and one-attempt admission, the single-owner protected lifecycle,
variant-aware
finish compositions with the summary bound to the decoded
payload and forgery negatives, the curated subject-facts closed
contract, the section-2 endpoint binding, driver composition
negatives and public main refusals; fake Docker/socket/time/
identity seams plus tiny exact-owned Python children only; no
docker daemon, namespace or syscall probe; no secrets
forwarded to the fixture).  CI remains Python-only with the ten
existing required checks (no new job; the pinned public Codex
binary is fetched and hashed statically in the R
`cache-native-fixture` job and is NEVER EXECUTED there —
including help/version — per the RIGHT-only startup law).
017-s performs no native launch, no worker
suspension, no protected service or profile change; the
handoff-preparation qualification stays `PENDING` strategic
review of the actual outcomes; D09 remains `NOT RUN`/deferred;
no v1 runtime claim.
Stage 017-t finalizes the S evidence record (the one
auxiliary-log mode repair and the four immutable-report
clarifications recorded in the new T report; the S/R/Q/P
reports are never edited) and lands the INERT native-
handoff preparation boundary for the later separately
activated RIGHT-pane native handoff.  Two repo-owned
stdlib-only modules: the typed immutable order/run binding
(`scripts/cache_native_fixture_binding.py`) — one explicit
opted-in run bound, before any mutation, to the exact active
order ID, its unique committed immutable order file, the
literal committed source head, the repository identity
(owner/repo; the origin URL is never retained or echoed,
private endpoints refused) and a module-minted run identity;
strictly read-only resolution, no GitHub/network call, no
authority minted from source parsing; per-order stable
one-attempt namespaces in which a changed head/directory/
phase never resets the attempt, with the historical
exhausted 017-s record preserved in its exact schema — and
the versioned read-only native-handoff preparation contract
(`scripts/cache_native_fixture_native_prep.py`,
`slaif-native-handoff-prep-v1`) — fixture-owner facts kept
separate from external-native facts, the closed subject-
identity law (exact registered CID, UID/GID 21002 with the
closed group law, argv exactly `codex --yolo --profile
early-beta`, pinned binary identity, birth bound, expected
PTY), read-only worker/Bash group facts (complete bounded
pgrp membership, separately grouped owned tool sessions,
job J never guessed, tty foreground a read-only
observation, no signal of any kind), the separately measured
stop and restoration phases kept distinct (the recorded stop:
worker T, Bash running, G differing from B's group, all
observed G members stopped, foreground observed back on
B's group after Bash reclaimed the TTY; restoration: the
same worker running again with the observed foreground back
on its own group G, measured against that recorded stop),
closed verdict composition (unknown/unobserved/incomplete never
ready/pass; caller-authored ready/status/flag JSON
refused; the historical S-scope owner record decodes
and validates as its own scope but can never qualify a
native-ready composition), the native-owner evidence
producer (`slaif-native-owner-evidence-v1`) that invokes
the owned finish/export/teardown measurement seam,
validates the FULL measured export payload with the
actual shared export validator, recomputes the export
digest itself, and binds the measured teardown to the
exact immutable order/source-head/run/CID/image/binary
context (closed six-key measured context; the image id
admits only the bare digest or the actual measured
`sha256:<digest>` form), the real owned measurement
adapter whose native facts derive only from the public
workflow's measured pre-teardown subject receipt, and the
public prepare/observe/finalize workflow that invokes the
collectors itself before recording (no constructor- or
prepopulated-record evidence, no CLI entry; finalize
binds a native-owner record to the immutable workflow
binding's order, literal source head and run, and the
retained subject receipt to that same run).  Public
proof: 169 pure/fake plus tiny exact-owned Python child
tests (`tests/test_cache_native_fixture_binding.py`, 45;
`tests/test_cache_native_fixture_native_prep.py`, 124);
no test signals any process other than its own exact-
owned children (killed by the test's own cleanup if still
alive), and a static AST law proves no
subprocess/signal/pty surface in the preparation module.  017-u
continues the same inert preparation and repairs the
complete-inventory law (review 11): every listed process
row is tri-stated through the bounded absence seam — only
an independently verified-gone entry may be ignored
(bounded churn law); an unreadable still-existing or
unprovable entry is a closed non-echoing refusal, never a
silently skipped listing row, and can never establish
nonmembership, a complete group or a complete stop; a
failed initial prepare/observe mints no baseline and a
refused stop can never later claim a recorded stop or
restoration; the unchanged four-case group-readability
probe passes 4/4 at the repaired source.  017-t performs no
native launch (including help/version), no worker
suspension, no local Docker operation and no new rehearsal
(the S admission stays consumed); the software preparation
is INERT and the later serial native handoff remains a
separately authorized order; D09 remains `NOT RUN`/deferred;
no v1 runtime claim.
Objective 016 (the architecture/documentation and
development-state stage) is accepted and merged as PR #24, merge
`96c790423f6f0097a56a0b12bacda8a9b6da6aba`. Do not read a row in this
ledger as delivered behavior. Stage-scoped synthetic unit/fake tests prove
their named mechanisms within the owning stage; they never substitute for
actual-model, genuine-Codex, native-compaction or artifact qualification.

## Reading this ledger

Three distinct claims are tracked and must never be conflated:

- **Evidence:** the named test or sanitized evidence artifact exists and was
  executed.
- **Implementation:** the mechanism exists in product code behind a planned
  configuration profile.
- **Acceptance:** strategic review verified the evidence against the
  criterion, with current-head checks green and remote state verified.

Criterion state values are `NOT RUN`, `PENDING`, `IN PROGRESS`, `PASSED`,
`FAILED`, or `BLOCKED`. A criterion is `PASSED` only when all three claims are
satisfied for that criterion — that is, only after its own required
evidence layers pass and are reviewed. Pure/unit/fake-upstream criteria may
be proven by their named layers; actual-model, genuine-Codex, native-
compaction and artifact claims require their distinct evidence. A root-only
or counter-only result never passes a dependency criterion (O01/O02 law).
Unit/fake-upstream, actual-model, genuine-Codex, native-compaction and
artifact qualification are distinct evidence layers; none substitutes for
another.

## Acceptance criteria matrix

Owner stages (abbreviations): **OBS** = real-format read/root observation;
**GRAPH** = graph, identity and admission; **RAM** = RAM session state and
ownership; **REC** = per-session recovery; **TOK** = tokenizer, compiler and
budgets; **REP** = transactional source replacement; **ADV** = adversarial
acceptance matrix; **QUAL** = bounded real-model and genuine-Codex
qualification. States in this stage: D01-D08 and D10 are `PENDING` (pure observation slice; named evidence below, strategic acceptance outstanding); D09 remains `NOT RUN` (multi-chunk process completion deferred); every other criterion is `NOT RUN` (planned).

### Detection and acquisition (D)

| ID | Scenario | Owning stage | Required evidence (abridged) | State |
|---|---|---|---|---|
| D01 | Valid automatic `AGENTS.md` message plus environment metadata | OBS | Exact source extraction; environment excluded; correct directory scope | 017-a evidence: tests/test_bundle_root_envelopes.py::TestCanonicalSanitizedFixture::test_real_format_canonical_fixture_parses_with_exact_bytes, ::test_adjacent_environment_tail, ::test_newline_separated_environment_tail, ::test_separate_item_environment_is_excluded, ::test_crlf_envelope_preserves_crlf_content_bytes; tests/test_bundle_observe.py::test_every_fixture_is_synthetic_and_versioned; 017-b regression: tests/test_bundle_root_envelopes.py::TestLabelByteBound (UTF-8 byte label bound) | PENDING
| D02 | Fake marker in assistant text/tool description; malformed or duplicate envelope | OBS | No false root or arbitrary authority | 017-a evidence: tests/test_bundle_root_envelopes.py::TestNoAuthorityWithoutEnvelope::test_assistant_envelope_never_creates_root, ::test_marker_prose_at_later_offset_is_not_a_root, ::test_tool_output_envelope_is_not_a_root, ::test_unclosed_tail_is_typed, ::test_nested_duplicate_opening_marker_is_typed, ::test_duplicate_closing_tag_in_tail_is_typed, ::test_invalid_labels_and_delimiters_are_typed, ::test_valid_root_coexists_with_observable_malformed_occurrence | PENDING
| D03 | Single relative/absolute workspace `cat` | OBS | Correct normalized path, complete content, removable span | 017-a evidence: tests/test_bundle_read_grammar.py::test_single_relative_operand, ::test_dash_dash_separator, ::test_absolute_workspace_operands; tests/test_bundle_client_paths.py::test_relative_against_evidenced_workspace, ::test_simple_absolute_under_workspace, ::test_unicode_path_preserved; tests/test_bundle_tool_results.py::test_single_complete_read, ::test_empty_file_is_complete_empty_version, ::test_unicode_crlf_bytes_are_exact; 017-b regression: tests/test_bundle_read_grammar.py::TestTerminatorMembership, ::TestCallArgumentShapes; tests/test_bundle_tool_results.py::TestPerCallWorkdir; 017-c regression: tests/test_bundle_read_grammar.py::TestQuotedOptionSemantics (quoted option/terminator/stdin), ::TestNonAsciiWhitespaceNotASeparator, ::TestExactOperandLimit, ::TestCallArgumentShapes (repr privacy, documented raw-argument cap), tests/test_bundle_shell_tokens.py (raw spans/cooked values/quoting/operators, repr privacy, no shell facilities), tests/test_bundle_client_paths.py::TestMalformedUnicodeAndSpaces | PENDING
| D04 | `/work-other`, traversal, unknown root, quoted `cat`, heredoc write | OBS | No client-host confusion or false acquisition | 017-a evidence: tests/test_bundle_client_paths.py::TestAbsolutePaths::test_sibling_prefix_is_outside, ::test_lexical_dotdot_escaping_is_traversal, ::test_outside_absolute_path, ::test_absolute_with_unknown_workspace, ::test_relative_without_workspace_is_unproven, ::test_relative_traversal_escape, ::test_fully_quoted_literal_operand_under_no_spaces_convention, ::test_url_fragment_is_literal_never_stripped, ::test_query_syntax_is_never_mapped_to_the_plain_file, ::test_module_imports_no_filesystem_or_shell_facilities; tests/test_bundle_read_grammar.py::TestSafeNegatives::test_unsupported_shapes_are_typed_never_complete, ::test_no_expansion_no_evaluation; tests/test_bundle_observe.py::test_logical_root_scope_never_maps_host_paths, ::test_no_context_at_all_is_unproven; 017-b regression: tests/test_bundle_tool_results.py::TestPerCallWorkdir::test_per_call_workdir_outside_workspace_is_not_complete, ::test_relative_workdir_is_typed_not_complete, ::TestMalformedUnicodeComposition (typed, non-crashing, non-removable); 017-c regression: tests/test_bundle_tool_results.py::TestMalformedWorkdirUnicode (surrogate per-call workdir typed `MALFORMED_UNICODE`, relative and absolute operand variants, no crash/placeholder digest) | PENDING
| D05 | `cat A.md B.md` without internal separators | OBS | One complete two-member bundle; no fabricated individual hashes | 017-a evidence: tests/test_bundle_read_grammar.py::test_two_operands_in_order, ::test_repeated_operand_preserves_order; tests/test_bundle_tool_results.py::test_two_members_without_separators_is_one_ordered_bundle, ::test_reversed_order_changes_observed_member_order, ::test_repeated_operands_do_not_fabricate_files; tests/test_bundle_observation_models.py::test_two_member_bundle_has_unknown_member_digests, ::test_single_member_complete_read_carries_proven_digest, ::test_requested_and_proven_executed_are_distinct; 017-b regression: tests/test_bundle_tool_results.py::TestRealFormatWrapper (handoff `Chunk ID:` + earned variant), ::TestContradictoryWrapperStatus, ::TestWrapperBoundsAndGrammar, ::TestToolEligibilityEvidence, ::TestEndpointScopedPairing; fixture tests/fixtures/cache_bundles/v1/read_handoff_wrapper_format_responses.json; 017-c regression: tests/test_bundle_tool_results.py::TestEndpointSelection (mixed shapes typed non-removable, unambiguous positives, explicit endpoint scoping, global/per-read agreement), tests/test_bundle_observe.py::TestEndpointDomainAtComposition | PENDING
| D06 | Chained reads with `ls`, labels and unrelated output | OBS | Correct outer regions; unrelated output preserved | 017-d evidence: tests/test_bundle_compound_reads.py::TestChainedReadPlans (all-cat `&&` plans, one ordered bundle, order/duplicate preservation), ::TestEchoOuterBoundaries (literal echo prefix/suffix, internal-echo negative), ::TestMixedOutputNegatives (`ls` family exit-zero/nonzero, semicolon chain), ::TestOuterRegionComposition (pure file span exposure, label-inside-source, collision/extra-output typed); outer-region proof in ::TestOuterSourceRegions; 017-e regression: ::TestEchoOptionSemantics (option-like dash-leading quoted literals typed, both quote kinds, combinations/repetitions, narrow exclusion), ::TestEchoOptionSemanticsComposition (echo '-n'/'-ne' prefix/suffix never strips source, fake/real marker inside source stays source, earned-marker control) | PENDING
| D07 | Literal loop, supported wildcard evidence, explicit `workdir`/`cd` | OBS | Proven executed membership; no adapter-host expansion | 017-d evidence (loop/wildcard remain explicitly typed unsupported in this slice): tests/test_bundle_compound_reads.py::TestLiteralCdTransitions (absolute literal `cd` under evidenced workspace, sibling/ancestor/`..`/relative/bare/multi-target negatives, per-call workdir precedence, mid-chain failure), ::TestPlanNegatives (loop/branch/glob/substitution typed, later words never reinterpreted), ::TestWholePlanBounds (whole-plan statement/operand bounds); composition: ::TestChainedPlanComposition::test_cd_then_reads_resolves_against_transition, ::test_per_call_workdir_then_cd_transition; 017-f evidence (the loop criterion is D07, not a blanket D09/D10 completion; wildcard iteration evidence remains typed unsupported): tests/test_bundle_literal_loops.py (human 6.2 unguarded forms as finite parsed data with deterministic requested members; all-success guarded positives with exact digest/slot-width/reversed/duplicate order; unguarded and echo-labeled forms non-removable with typed iteration/outer-attribution limitations and preserved members; `f`/`d` variable law with special/unknown/prefix references typed; double-quoted one-reference template law with adjacent-quote words typed; exact `|| exit 1` guard law with false/late/pipe variants typed; cat option/terminator/stdin law applied after substitution including the dynamic terminator; workdir/workspace/parent-relative resolution and outside negatives; empty/over-bound lists, at-limit and one-over whole-loop operand budget under one shared `max_operands`; wrapper completion matrix nonzero/truncated/unknown/missing/running/malformed-Unicode; `literal-loop/v1` grammar identity across all outcomes; repr privacy with no raw command literals); 017-g regression: tests/test_bundle_literal_loops.py::TestQuotedWordSeparatorBoundaries (the unquoted `;` as a standalone token: the four defect forms — quoted word single/last with attached separator — typed `QUOTED_OPERAND` with no phantom `A`/`.md` members; attached/spaced agreement per word; first position with clean neighbor; empty-quote insertion typed without members; plain and whole-word quoted controls still earned; composition-level typed observations non-removable with no digest/span, and exact earned-bundle span/digest/member/width controls) | PENDING
| D08 | Read succeeds, later command fails; earlier read fails, later command succeeds | OBS | Per-read evidence distinguished from global exit status | 017-d evidence: tests/test_bundle_compound_reads.py::TestPerReadVersusGlobalExit (nonzero chain proves no read and no digest, requested members preserved, wrapper status recorded; earlier-failure/later-success; truncated chain; process-running; malformed-Unicode content; chat composition; mixed suppression); 017-e regression: ::TestPlanGrammarIdentity (the actual plan grammar carried on complete/unsupported/nonzero/truncated/missing/running/malformed/outer-boundary outcomes; single-grammar contrast; an unsupported attempt is never a successful plan) | PENDING
| D09 | Truncation, partial `head`/`sed`, missing output, multi-chunk process | OBS | Explicit completeness state; no false full-file cache entry | NOT RUN (017-f note: the loop completion negatives — nonzero/truncated/unknown/missing/running/malformed-Unicode wrapper over looped reads, no inferred earlier iteration — are typed on the D07 loop surface, tests/test_bundle_literal_loops.py::TestWrapperNegatives; multi-chunk process completion and the remaining truncation matrix stay deferred to a later same-PR suffix; 017-g was the bounded loop word/separator correction and added no chunk family; 017-h attempted the process evidence path but was interrupted and published PARTIAL with nothing earned; 017-i landed the offline capture utility only — actual capture and process/chunk collector NOT RUN; 017-j repaired that utility's selection/resource boundaries — issued binding, advancement evidence, serialized-byte cap, descendant deadline — but added no multi-chunk process-completion evidence; 017-k further repaired the runtime issued-registry binding, finalization quiesce (frozen-snapshot validation), all-method/error-path budget accounting, and readiness/Unicode fidelity; 017-l further repaired owned-I/O quiesce (admitted request sockets closed by effective shutdown so progressing in-flight reads cannot pin the bounded join; incomplete teardown can never yield a completed outcome) and immutable pre-launch original-seed verification (child seed rewrites cannot redefine the purported original); 017-m earned the pure unsupported/partial negative matrix on the D05 pairing surface (truncated/missing/running/unknown wrapper, partial `head`/`sed`, command substitution, unexecuted branches — typed unsupported/partial, never complete whole-file acquisitions, contrasted with the exact proven empty successful output; tests/test_bundle_d10_matrix.py::TestUnsupportedAndPartialMatrix) — still no multi-chunk process-completion evidence, which these negatives are not; 017-n completed the wire-family/complete-inventory/result-ID inventory repairs and added no chunk family; 017-o enforced those complete-inventory bounds before retention (no-retention streaming preflight; 2 MiB allocation regression ceiling) and earned the private-ID representation law — still no chunk family; 017-p added the per-nested-container `max_items` scan guard (O(1) length test before any inspected assistant `tool_calls` list is iterated; per-container; 017-r landed the serial right-pane native fixture preparation — typed phase/budget model, 21001/21002 confinement fixture image, ten fresh-container scenarios through the Python-only `cache-native-fixture` job, public 0.164.0 musl artifact static preparation with LICENSE/NOTICE byte-identity retention, non-resettable ledger accounting and exact-owned cleanup — still inert: no actual capture/collector/model call, no format or process acquisition); never a total across lists) and the disposable-CI containment capability (probe + host runner + `cache-native-containment` job; hosted-only entry guard, no secrets forwarded to the fixture) — still no chunk family and no multi-chunk process-completion evidence) |
| D10 | Duplicate/mismatched call IDs, command substitution, unexecuted branch | OBS | No invented pairing/content; unsupported cases observable | PENDING — 017-f note: the loop substitution/nested/branch/fragment/control-flow negatives remain explicitly typed, tests/test_bundle_literal_loops.py::TestLoopFormNegatives, ::TestTemplateLaw; the duplicate/mismatched/unexecuted-branch matrix stayed deferred through 017-l (017-g word/separator correction added no branch matrix; 017-h earned nothing (interrupted, PARTIAL); 017-i/017-j/017-k/017-l repaired the offline capture utility only — issued binding, RUNTIME issued-registry selection, finalization quiesce, owned-I/O quiesce, immutable original seeds — none of which is a branch matrix); 017-m evidence: tests/test_bundle_d10_matrix.py::TestIdentityConflictPrecedesEligibility (eligibility-independent ID inventory: unknown/ineligible same-ID conflicts typed `DUPLICATE_CALL_ID` across supported/unsupported names and families on Responses and Chat, identical/conflicting duplicate calls rejected, unrelated unique unknown calls neither recorded nor poisoning valid chains, nested text objects not call records, absent/null/empty `MISSING_CALL_ID` and non-string `MALFORMED_CALL_ID` observable without inventing an ID), ::TestStructuralCausality (numeric structural positions — `input` item index / Chat `messages` index — establish pairing, never lexical IDs or JSONPath string sorting: pre-call results typed `PRE_CALL_RESULT` non-removable with no bundle/member digest, source span or proven-executed claim on Responses and Chat, >=10 structural positions with non-monotonic IDs, missing initial calls unsupported, ambiguous chains rejected while independent valid chains earn exact span/digest/members/width), ::TestD10MatrixComposition (ordinary valid reads amid many unrelated calls, duplicate same-call results still `MULTI_CHUNK_DEFERRED` absent later earned process-chain evidence, exact Unicode/CRLF source slices, unchanged inputs, non-echoing reprs, preserved bounds); ::TestUnsupportedAndPartialMatrix (command substitution `$()`/backticks, false/conditional/unexecuted branches, partial `head`/`sed`, known truncated/missing/running/unknown wrappers — typed unsupported/partial, never complete whole-file acquisitions, contrasted with the exact proven empty successful output); 017-n evidence: ::TestWireFamilyInventoryAndBounds (the Responses `custom_tool_call` identity joins the call inventory alongside `function_call` — identity bookkeeping only, no custom-tool acquisition, opaque input never captured/reinterpreted, no unknown-family wildcard: exact colliding IDs make the ambiguous eligible chain typed `DUPLICATE_CALL_ID` non-acquiring in both orderings with repeated identical/conflicting records all observable and never first-match, a custom named like a supported tool still never acquires, unique unrelated opaque customs neither record nor poison; `max_commands`/`max_outputs` bound the complete relevant inventory — unsupported names, opaque custom records, missing/empty/malformed IDs, invalid result IDs — before any identity map or diagnostic is retained: fixed non-acquiring `OVER_BOUND` at-limit/one-over on Responses and Chat including many `tool_calls` in one assistant message and a late collision beyond the retained prefix, selected-domain scoping under explicit endpoint selection, mixed bounded across inspected domains; absent/null/empty `MISSING_RESULT_ID` and non-string `MALFORMED_RESULT_ID` result IDs typed non-echoing and unpaired, never invented/hashed/attached/acquired, well-formed chains still useful within limits); 017-o evidence: ::TestInventoryAllocationAndIdRepresentation (the complete relevant inventory bounds are decided by a no-retention streaming preflight before any record tuple, location string, ID map, typed diagnostic, argument/wrapper parsing or identity map is retained — large prebuilt Responses calls, nested Chat `tool_calls`, Responses results and Chat results at limit one yield the fixed non-acquiring `OVER_BOUND` with measured allocation under the generous 2 MiB regression ceiling, at-limit useful reads keep exact digest/span/member/width, and one-over/late-collision/invalid-ID/ignored-domain/mixed shapes keep their typed behavior with unchanged inputs; exact internal call/result IDs stay usable while operational `str`/`repr` of report/read/unpaired objects never echo private ID values — fixed `<private-id>` placeholder for non-empty values, observable no-ID state, fixed enums/counts/locations/digests remain visible, synthetic canaries only); strategic acceptance outstanding (the delivery claim requires independent strategic acceptance) |

### Graph, admission and identity (G, C)

| ID | Scenario | Owning stage | Required evidence (abridged) | State |
|---|---|---|---|---|
| G01 | Root → A → B, repeated links, cycles | GRAPH | Recursive closure, stable identity, termination | NOT RUN |
| G02 | Relative link in nested file; ambiguous origin inside a bundle | GRAPH | Correct referring-directory resolution or explicit unresolved edge | NOT RUN |
| G03 | Eligible A + unrelated B under both modes | GRAPH | Lean isolates/skips correctly; greedy admits whole attributable bundle | NOT RUN |
| G04 | Unrelated file alone; no eligible member | GRAPH | Neither mode admits it merely because it is Markdown | NOT RUN |
| G05 | Greedy co-cached source containing commands/claims of authority | GRAPH | No authority escalation or silent graph-membership promotion | NOT RUN |
| C01 | A+B, then A alone, then identical A again | GRAPH | Two independent entries; singleton's third observation is a hit | NOT RUN |
| C02 | A+B versus B+A; repeated same file in one command | GRAPH | Order/content identity retained; duplicate members do not inflate allowance | NOT RUN |
| C03 | Simultaneous identical misses | RAM/TOK | One actual compiler leader; followers reuse its result | NOT RUN |
| C04 | Changed A affecting A, A+B and A+C | GRAPH | Affected state invalidated; no stale/mixed-version injection | NOT RUN |
| C05 | Old messages replayed after A-v2; later deliberate revert | GRAPH | Replay does not roll back state; new observations are distinguishable | NOT RUN |
| C06 | Unknown member versions in boundaryless bundles | GRAPH | No invented per-file hashes or unsupported byte splicing | NOT RUN |

### Token budgets (B)

| ID | Scenario | Owning stage | Required evidence (abridged) | State |
|---|---|---|---|---|
| B01 | Context 262144 and 32768 with one/two-file bundles | TOK | Allowances 8192/16384 and 1024/2048, measured with the pinned tokenizer | NOT RUN |
| B02 | Small/large files, long metadata, many ready entries | TOK | No padding; wrappers counted; aggregate context/reserves respected | NOT RUN |
| B03 | Oversized source, truncated compile, output beyond slot | TOK | Typed failure; no valid entry or silent instruction truncation | NOT RUN |
| B04 | Same content with changed context/tokenizer/compiler policy | TOK | Correct new identity; no incompatible compiled reuse | NOT RUN |

### Replacement and reconstruction (R)

| ID | Scenario | Owning stage | Required evidence (abridged) | State |
|---|---|---|---|---|
| R01 | First valid acquisition and repeated original history | REP | Original spans removed; compiled block available; no repeat compilation | NOT RUN |
| R02 | Tool-result prefix/suffix, Unicode/CRLF, images and other items | REP | Only intended source spans changed; tool/API/image contract preserved | NOT RUN |
| R03 | Already transformed input, duplicate/forged/stale references | REP | Idempotent valid output; no cross-session resolution | NOT RUN |
| R04 | Root still present after native compaction | REP | Cache hit/replacement works; not falsely counted as lost-root recovery | NOT RUN |
| R05 | Source absent after history reduction, same session | REP | Required compiled working set reconstructed without original-source reinjection | NOT RUN |

### RAM and recovery (M)

| ID | Scenario | Owning stage | Required evidence (abridged) | State |
|---|---|---|---|---|
| M01 | Many hits after initial acquisition | RAM | Zero recovery-source content reads on the normal path; zero recompile | NOT RUN |
| M02 | Process restart, one of several sessions resumes | REC | Only that session loaded/rebuilt; new epoch and actual compile work recorded | NOT RUN |
| M03 | Torn/corrupt/foreign checkpoint and source-digest mismatch | REC | Explicit recovery failure; no dangling references or contamination | NOT RUN |
| M04 | Concurrent workers and request races | RAM/REC | Session ownership and atomic version/checkpoint behavior hold | NOT RUN |
| M05 | RAM pressure and session cleanup | RAM | Declared behavior; no hidden disk cache, eviction churn or governance loss | NOT RUN |

### Isolation and whole-rework acceptance (S, O)

| ID | Scenario | Owning stage | Required evidence (abridged) | State |
|---|---|---|---|---|
| S01 | Different principals/sessions/repos with identical filenames/content | ADV | No cross-namespace reuse or source disclosure | NOT RUN |
| S02 | Signed identity, malformed transforms, stream/disconnect | ADV | Existing auth, single-forwarding, SSE and cancellation contracts hold | NOT RUN |
| O01 | Root compiled but dependencies absent | ADV/QUAL | Overall dependency-cache acceptance fails or stays incomplete | NOT RUN |
| O02 | Actual dependency acquired/compiled/replaced/injected | ADV/QUAL | Exact synthetic source/entry/request evidence proves every stage | NOT RUN |
| O03 | Compiler hit, source-absent injection and restart rebuild | ADV/QUAL | Separate counters; none substituted for another | NOT RUN |

## Planned objective succession

One numeric objective = one PR. Continuations use the same number/branch/PR and
the next valid suffix (`b..z`, then `aa..zz`). Only after independent strategic
acceptance, all current-head required checks, merge and remote-main
verification may the next objective activate. Future orders remain inert
drafts until activated.

| Objective | PR branch | Deliverable and gate | Status in this round |
|---|---|---|---|
| 016 | `oap/016-cache-rework-contracts` | Commit unchanged human handoff; reconcile both architectures, root/strategic agent law, security/testing/configuration docs; publish the plan and this stage ledger; establish the separate current-development provenance contract (development-state artifact validation under the intact RC10 publication freeze). No adapter-runtime implementation claim. | Merged (PR #24; merge `96c790423f6f0097a56a0b12bacda8a9b6da6aba`; accepted) |
| 017 | `oap/017-cache-read-observation` | Versioned pure root/read/result/span evidence and real-format synthetic fixtures: D01–D10, Unicode/CRLF, bounds, no shell execution. Preserve legacy detector until integration. | In progress (017-a..017-c published but not accepted; 017-b corrected findings A-E; 017-c corrected literal-grammar/endpoint proof; 017-d corrects the root-domain prerequisite as an independent commit and earns D06/D07/D08 finite read plans in the inert module `compound_reads.py`; 017-e corrects echo option semantics and plan-grammar identity on the same inert surface; 017-f earns the bounded pure literal-loop slice; 017-g corrects the loop word/separator law on the same inert surface; 017-h interrupted (PARTIAL, non-delivery, no repo change, nothing earned); 017-i lands the offline opt-in fail-closed process-capture utility for independent strategic review (inert; actual-client path input-gated — generated readiness `not_ready`, caller-supplied records can launch the bound stand-in; no actual capture/collector/model call); 017-j repairs that utility's selection/privacy/ownership/resource boundaries per independent review (issued binding, lossless byte-verified synthetic text in selection schema v2, serialized-byte cap, centralized request budget, bounded preflight, no-mutation directory guards, closed metadata schemas, descendant deadline; still inert, no actual capture/collector/model call, no format or process acquisition); 017-k repairs that utility's second-review boundaries (RUNTIME issued-registry binding with preloaded/anticipated/forged-call negatives, finalization quiesce with frozen-snapshot validation, all-method/error-path budget accounting, faithful generated-readiness round-trips, typed non-echoing malformed-Unicode rejection; still inert, no actual capture/collector/model call, no format or process acquisition); 017-l repairs the two remaining offline capture boundaries (owned admitted request sockets closed by effective shutdown at quiesce with honest incomplete-teardown outcome; immutable pre-launch original-seed verification with child-mutated/unseeded negatives; still inert, no actual capture/collector/model call, no format or process acquisition); 017-m repairs the per-request pure read-observation identity/causality pairing (eligibility-independent call-ID inventory so unknown/ineligible same-ID conflicts cannot disappear through filtering; missing/empty/malformed IDs observable without invention; results attach only when their exact numeric structural position follows the matching call's — never lexical IDs or JSONPath string sorting; pre-call results typed `PRE_CALL_RESULT` non-removable) and earns the public D10 composition matrix plus the pure D09 unsupported/partial negative matrix (tests/test_bundle_d10_matrix.py; D10 now `PENDING` acceptance, D09 multi-chunk process completion still `NOT RUN`/deferred — the D09 partial negatives are not multi-chunk evidence); 017-n completes the wire-family/complete-inventory/result-ID inventory repairs (Responses `custom_tool_call` identity joins the call inventory as bookkeeping only; `max_commands`/`max_outputs` bound the complete relevant inventory, fixed non-acquiring `OVER_BOUND`, selected-domain scoping; absent/null/empty/non-string result IDs typed `MISSING_RESULT_ID`/`MALFORMED_RESULT_ID` non-echoing; tests/test_bundle_d10_matrix.py::TestWireFamilyInventoryAndBounds); 017-o enforces those complete-inventory bounds before retention (no-retention streaming preflight stops at the first exceeded limit; 2 MiB allocation regression ceiling on large prebuilt inventories at limit one) and earns the non-echoing private-ID representation (internal IDs stay exact and usable; operational `str`/`repr` of report/read/unpaired use the fixed `<private-id>` placeholder; tests/test_bundle_d10_matrix.py::TestInventoryAllocationAndIdRepresentation); 017-p enforces the per-nested-container `max_items` scan guard (O(1) pre-iteration length test per inspected assistant `tool_calls` list; tests/test_bundle_d10_matrix.py::TestNestedScanBounds) and lands the disposable-CI containment capability (probe + runner + `cache-native-containment` job; ordered token-bound parent-death proof; verified image removal; 61 orchestration tests; no secrets forwarded to the fixture); still inert, no actual capture/collector/model call, no format or process acquisition; all `PENDING` acceptance; D09 (multi-chunk process completion and the process/chunk association) remains for a later same-PR suffix — a later exact order may authorize one bounded reviewed actual capture, then the process/chunk collector).  017-r lands the serial right-pane native fixture preparation (bounded R accepted at head `2ce9dcd`, wording limitations recorded; the serial foreground handoff itself remains a later separately authorized order); 017-s lands the local fixture preparation and one bounded Python-only local rehearsal (the ONE rehearsal ran EXACTLY ONCE at implementation head `2a9c44e` with source inputs `54ef177`, PASS; facts in the immutable round report); 017-t finalizes the S evidence record and lands the inert native-handoff preparation contract (typed order/run binding with per-order stable one-attempt namespaces preserving the exhausted 017-s record; versioned read-only native preparation/evidence contract — owner/native fact separation, closed subject-identity law bound to the registered CID/21002/exact argv/pinned binary, independently measured same-job restoration law, closed verdict composition (a historical S-scope owner record never qualifies native-ready; an honest started-but-not-ready record never becomes ready; the owner's registered artifact must equal the measured subject executable; the visible handoff requires an actually bound, matched, nonzero expected PTY), the native-owner evidence producer with full shared-payload validation, digest recomputation, measured-context binding and exact closed record key sets, the real owned measurement adapter, and the public prepare/observe/finalize workflow with no CLI whose finalize binds the owner record and retained subject receipt to the immutable order/source-head/run binding; software preparation INERT — no native launch, no worker stop, no local Docker, no rehearsal; the later serial native handoff remains a separately authorized order); 017-u continues the same inert preparation and repairs the complete-inventory law (review 11: a stat-unreadable but positively still-existing PID was silently skipped and minted a complete stop receipt) — every listed row is now tri-stated through the bounded absence seam (verified-gone churn ignored; unreadable/unprovable entries closed refusals, never skipped; failed stop never claims restoration); 169 pure/fake plus tiny exact-owned Python child tests (45 binding + 124 preparation) |
| 018 | `oap/018-cache-graph-bundles` | Typed namespace/file/edge/bundle versions, recursive graph, lean/greedy admission, overlap/replay invalidation: G01–G05, C01/C02/C04–C06, S01. | Planned (inert draft) |
| 019 | `oap/019-cache-ram-state` | RAM session ownership/indexes, explicit capacity/backpressure, async single-flight and lifecycle: C03, M01/M04/M05; zero filesystem hot lookup. | Planned (inert draft) |
| 020 | `oap/020-cache-session-recovery` | Protected exact-original atomic checkpoints, locks and lazy per-session restart rebuilding: M02–M04, corrupt/torn/foreign/config-mismatch negatives. | Planned (inert draft) |
| 021 | `oap/021-cache-token-compiler` | Pinned actual tokenizer, typed bundle compiler, C/32 slots, aggregate/reserves and deterministic selection: B01–B04, compiler cancellation/failure/no-retry/compile-once. | Planned (inert draft) |
| 022 | `oap/022-cache-source-replacement` | Explicit opt-in config and endpoint/application integration, transactional root/tool source edits, stable references and source-absent reconstruction: R01–R05, S01/S02; upstream-body proof. | Planned (inert draft) |
| 023 | `oap/023-cache-adversarial-acceptance` | Complete stage-accurate telemetry and fake full-stack adversarial/lifecycle/isolation/cancellation matrix; all D/G/C/B/R/M/S/O criteria mapped without substitution; runtime/docs/package regressions. | Planned (inert draft) |
| 024 | `oap/024-cache-real-codex-qualification` | Bounded actual-model and genuine-Codex dependency/bundle/vision/history-reduction/restart acceptance; source-change/replay proof; measured normal-path zero disk reads and overhead; immutable development artifact handoff for independent benchmark. No benchmark dispatch, release, service/profile mutation or deployment. | Planned (inert draft) |

Stage acceptance never substitutes for later delivery. In particular, a
recognized root with absent dependencies fails overall cache-rework
acceptance (O01). Each stage may receive same-PR remediation suffixes. The
final qualification must state exactly which actual compaction behavior was
observed; adapter-boundary history reduction is not native Codex compaction
proof.

## Historical baseline: RC10

The rework is measured against, and deliberately changes, the behavior frozen
in the historical private candidate `0.1.0-rc10` (OCI digest
`sha256:5a02e0043fcc65e5dc5a78f3e2a8648a16c93620255e904e394c926b18c92960`,
image source `1a04528223445e4249fad6d24a71151fd1dc1a09`, measured client
`0.149.0`). RC10 is the **historical baseline only**: its records, tags and
benchmark outcomes are immutable, and none of its evidence is rework
acceptance. The zero-observation/zero-included-dependency CACHE results
described in the handoff are the motivation for this rework, not a rework
result. RC10's additive injection, filesystem-derived cache and
process-local rehydration remain the explicitly named **legacy** behavior
until the v1 migration is qualified.

## Source provenance

The private history audit that motivated this rework is named
`markdown-read-audit-20261018-a01` (sealed content digest
`a6021bb9019f3c4d3136ea90ced1ee727bb983771b2328634faf6b0ab55059df`). The
corpus itself, its task answers and its raw histories remain outside this
repository; only sanitized fixtures derived from its recorded command and
envelope shapes may enter tests.

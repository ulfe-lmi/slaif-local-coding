# Testing and verification

Start with the locked local gate below. Most tests use synthetic requests and
fake upstreams; they need neither a model server nor a Gateway deployment.
Live model, actual Codex and Docker qualification are separate layers with
explicit prerequisites.

Report results as `PASSED`, `FAILED`, `SKIPPED`, `NOT RUN`, `BLOCKED`,
`PENDING` or `MISSING`. An unavailable fixture or skipped test is never a pass.

## Local gate

Use Python 3.12 and the pinned uv toolchain from the build provenance:

```bash
uv lock --check
uv sync --frozen --extra dev
uv run --frozen ruff check .
uv run --frozen ruff format --check .
uv run --frozen mypy src tests
uv run --frozen python scripts/docs_consistency_check.py
uv run --frozen pytest -q
uv build
uv run --frozen python scripts/artifact_policy_check.py --dist dist --inspect
uv run --frozen python scripts/artifact_policy_check.py --dist dist --install-smoke
```

The full pytest suite requires the verified non-root **process-local umask
022** test context on this development host:

```bash
umask 022
uv run --frozen pytest -q
```

The canonical host umask 0002 makes newly owned pytest tmp fixtures group-
writable, which the safe-evidence validators correctly reject as
`destination_component_writable` before the tests' intended later rejection
classes (12 ordering failures); umask 077 masks the intentionally 0755
untrusted-cache fixture to 0700 and breaks one separate fixture-mode
expectation. At accepted 016, umask 022 passed the complete gate with 1543
passed, 27 skipped, 0 failed. Never change global/home permissions to avoid
this context, never loosen the intentional permission-negative fixtures (the
0755 untrusted-cache directory; the execute-only-ancestor test that skips on
UID 0), and create explicitly protected temporary roots/files with 0700/0600
where a test requires them.

Artifact tests build fresh artifacts and compare provenance with the actual
source-input map. An intentional README/source change can require a new accepted
wheel identity and regenerated provenance; never suppress a mismatch just to
make the gate green. Follow [the artifact policy](docs/RELEASE-ARTIFACT-POLICY.md)
for clean rebuilds and RC freezing.

## What the suites cover

| Layer | Required behavior |
| --- | --- |
| API and fake upstream | Responses/Chat forwarding, safe errors, header filtering, body/JSON bounds, usage, function-tool continuation, incremental SSE, timeout and disconnect cleanup. |
| Image policy | Zero/one unchanged; multiple retain newest only on the selected route; non-image order preserved; reject and unsafe-shape cases. |
| Governance | Evidence-based root detection, deterministic candidates, separate confidence/priority, strict compiler schema, direct compiler bypass, dependency pairing and acquisition bounds. |
| Cache and injection | Identity isolation, hash/version invalidation, TTL/LRU/bytes, stable selection, idempotent injection, essential-overflow fallback and process-local rehydration. |
| Signed ingress | Service-auth ordering, canonical HMAC bytes, duplicate/grammar handling, timestamp edges, secret separation, route mismatch, replay concurrency/capacity/clock failures and header stripping. |
| Privacy and security | No raw content or secrets in logs/metrics/artifacts, safe paths and permissions, adversarial envelope inputs and response-header handling. |
| Documentation | Required landing/install pages, working relative links, current claims, pull-only operator path and protected secret-file preparation. |
| Packaging | Explicit artifact contents, fresh non-editable installation, exact wheel/input-map binding and recorded toolchain. |

## Planned dependency-bundle cache profile (v1)

The approved dependency-bundle cache rework
([docs/CACHE-REWORK.md](docs/CACHE-REWORK.md),
[docs/CACHE-IMPLEMENTATION-PLAN.md](docs/CACHE-IMPLEMENTATION-PLAN.md)) is
delivered in planned implementation stages tracked by [the stage
ledger](docs/CACHE-REWORK-LEDGER.md). The legacy-profile suites above
continue to cover the currently implemented behavior. The planned v1
layers, per the ledger's owning stage, are:

- versioned real-format root/read/result/span fixtures, including combined
  multi-file reads, absolute workspace paths, literal loops, truncation
  and Unicode/CRLF edges, with no shell execution in detection
  (D01–D10);
- recursive graph closure, lean/greedy admission, independent ordered
  bundle identity, overlap/replay invalidation and cross-namespace
  isolation (G01–G05, C01–C02, C04–C06, S01);
- RAM session ownership, async single-flight, explicit
  capacity/backpressure and zero filesystem hot-path reads
  (C03, M01, M04, M05);
- protected exact-original checkpoints with corrupt/torn/foreign and
  configuration-mismatch negatives, and lazy per-session restart
  rebuilding (M02–M04);
- pinned actual-model tokenizer budgets (C/32 slots, aggregate limit and
  reserves), typed compiler failure/truncation/overflow states, no-retry
  and compile-once behavior (B01–B04, C03);
- transactional source replacement proven against the actual upstream
  body, idempotence under replayed history, forged/stale reference
  rejection, and source-role authority preservation (R01–R05, S01–S02);
- a full fake-stack adversarial/lifecycle/isolation/cancellation matrix
  with stage-accurate telemetry and the whole-rework acceptance rules
  (O01–O03); and
- bounded actual-model and genuine-Codex qualification with synthetic
  tasks, serial bounded requests and complete teardown.

Stage 017, first round (tracked in the stage ledger) has landed the D01-D05
slice of the first item:
the inert pure observation package
`src/slaif_local_coding/constitution/bundles/` (typed models, literal client-
path normalization, envelope observation, literal read grammar, tool-result
pairing, and a pure composition entry point), with the named suites
`tests/test_bundle_observation_models.py`,
`tests/test_bundle_client_paths.py`,
`tests/test_bundle_root_envelopes.py`,
`tests/test_bundle_read_grammar.py`, `tests/test_bundle_tool_results.py`,
`tests/test_bundle_observe.py` and `tests/test_bundle_shell_tokens.py`
exercising the versioned synthetic fixtures in
`tests/fixtures/cache_bundles/v1/` plus the canonical sanitized 0.149.0
fixture. Round 017-d corrected the root-domain prerequisite (root
observation scoped to the actual selected Responses domain; string-input
plus messages is a mixed shape, never unambiguous Chat) and earned the
D06-D08 finite read-plan slice in the new pure module
`src/slaif_local_coding/constitution/bundles/compound_reads.py`
(all-cat / literal-cd `&&` plans as one ordered whole bundle, absolute
literal `cd` transitions under the evidenced workspace with per-call
workdir precedence, bounded literal `echo` outer boundaries with exact
prefix/suffix proof, per-read versus global exit evidence, whole-plan
bounds), exercised by
`tests/test_bundle_compound_reads.py`; loops and wildcards remain
explicitly typed unsupported in this slice. Round 017-e corrected the
echo outer-boundary law (option-like dash-leading quoted literals —
`-n`, `-e`, `-E`, combinations, repetitions, either quote kind — are
implementation-sensitive and typed `ECHO_TARGET_UNSUPPORTED`, never a
literal+newline boundary; the actual `echo '-n'` writes nothing) and
the grammar identity (every observation produced through the
finite-plan parser carries `literal-read-plan/v1` across all outcomes;
observations the single grammar actually earned keep
`literal-shell-read/v1`), exercised by
`tests/test_bundle_compound_reads.py::TestEchoOptionSemantics`,
`::TestEchoOptionSemanticsComposition` and `::TestPlanGrammarIdentity`.
Round 017-f earned the bounded pure literal-loop slice (the D07 loop
criterion, not a blanket D09/D10 completion) in the new pure module
`src/slaif_local_coding/constitution/bundles/literal_loops.py`
(grammar `literal-loop/v1`; the human 6.2 loop forms as finite parsed
data with deterministic requested members, all-success guarded
pure-cat loops as one ordered whole-source bundle under wrapper-
proven exit-zero/untruncated/present completion, unguarded and
echo-labeled forms non-removable with typed iteration/outer-
attribution limitations, the exact per-cat `|| exit 1` guard,
double-quoted one-reference filename templates, the `f`/`d` variable
law, adjacent-quote and control-flow typing, and the whole-loop
expanded-operand budget never multiplied per iteration), exercised by
`tests/test_bundle_literal_loops.py`.
Round 017-g corrected that slice's loop word/separator law on the
same inert module: the unquoted `;` is its own syntactic element (a
standalone token), so a quoted prefix plus a literal suffix touching
the list separator (`for f in "A".md;`) is one unearned word typed
`QUOTED_OPERAND` — never two members (`A` and `.md`) — with attached
and spaced separator forms observing identically, the first/last/
single list positions agreeing, and the plain and whole-word quoted
controls unchanged; the member-digest prose follows the occurrence
law (a file's digest is proven only when exactly one member
occurrence covers the entire attributable region; a duplicate `A,A`
has width one but unknown individual versions/boundaries). It is
exercised by
`tests/test_bundle_literal_loops.py::TestQuotedWordSeparatorBoundaries`.
These modules are **not active
in the adapter**: they are not wired into the legacy request execution
path, and the legacy detector is unchanged.
D09-D10 remain planned for later same-PR suffixes (the earlier planned
017-e loops/chunks draft was superseded by the 017-e bounded
correction; 017-g was the bounded loop word/separator correction and
added no loop/chunk families — rounds 017-b/017-c/017-d/017-e added
no loop/chunk families, and 017-f added the bounded pure literal-loop
slice without process/chunk (D09) or branch/substitution-matrix (D10)
support; the process/chunk association remains planned for a later
same-PR suffix, subject to review). Round 017-h attempted that
process evidence path but was **interrupted and published as
PARTIAL, non-delivery** (out-of-bound raw persistence, exceeded
ingress/attempt bounds, a client-startup plugin sync side effect);
it changed no repository utility, test, fixture or documentation and
earned nothing, so no 017-h evidence exists. Round 017-i lands the
**offline process-capture utility**
(`scripts/real_client_capture.py` plus the synthetic
`scripts/real_client_capture_fake_child.py`) with its named offline
suite `tests/test_real_client_capture.py`: injected synthetic child
executables (pinned paths, no installed-client fallback), the
in-process owned fake provider over raw sockets (auth, hard-limit
accounting, malformed/chunked/oversized/invalid-length and stalled-
read robustness), allowlist extraction with canary/digest/
non-echoing guarantees, process-group supervision (deadline and
output-cap kills, unrelated-process survival, group-gone
verification), the non-resettable attempt ledger, the fail-closed
actual-client gates (opt-in, version/hash binding, readiness,
authorization), workspace/cleanup ownership guards, the CLI, and
static stdlib-only/OAP-decoupling/no-raw-persistence guards. Those
offline synthetic tests are **not** actual-format or genuine-client
evidence: the 017-i record's wording that the utility's actual-client
path is "unreachable in this round by construction (startup
readiness is `not_ready`)" is a REJECTED historical claim,
superseded by 017-j — the path is input-gated (caller-supplied
`ready`/authorization records can launch the bound stand-in), while
the generated readiness verdict is `not_ready`; no actual client,
provider session or model call is made in any of these rounds, and
the actual capture plus process/chunk collector remain `NOT RUN`; one honest
environment skip applies where the foreign-ownership cleanup guard
requires `chown` to another uid. Round 017-j amends that same inert
utility and its named offline suite for the issued-binding,
lossless byte-verified synthetic text export (selection schema v2),
serialized-byte cap, centralized request budget, bounded preflight,
no-mutation directory guards, closed metadata schemas, and
descendant-deadline repairs, with added regressions for every
repaired boundary (including deterministic non-root simulated-UID
ownership proofs and non-selected marker variants). The suite runs
under a process-local umask of 022 because the permission fixtures
are intentional. Full-suite skip accounting stays distinct: the 27
prior stage skips plus exactly one 017-i foreign-ownership `chown`
environment skip — the simulated-UID proofs are passing tests, never
skips. No actual client, provider session, or model call is made;
the actual capture and process/chunk collector remain `NOT RUN`.
Round 017-k amends that same inert utility and its named offline
suite for the second-review repairs, with public
receiver/run/lifecycle regressions (not merely constructor
assertions): RUNTIME issued-registry binding through embedded-mode
fake children (preloaded first/later calls and forged inbound
progression never selected before issuance; the actually-issued echo
selected and byte-verified), wrong-family items under an otherwise
valid offered schema, finalization quiesce (a real shutdown-boundary
late request byte-verified and stripped to `content_unverified` with
its marker bytes nowhere under the output directory; frozen-append
rejection; bounded stop under a stalled in-flight handler with
honest teardown accounting), every-method/malformed/error-path
budget accounting with fixed non-echoing bodies and bounded handler
concurrency, generated readiness records round-tripping the
validated count for zero and every nonzero known flag without
flag-text export, and ACTUAL lone-surrogate malformed Unicode
rejected with the fixed typed `malformed_unicode` reason before any
encoding/hashing/retention plus valid non-ASCII controls.
Round 017-l amends that same inert utility and its named offline
suite for the two remaining offline capture boundaries, with public
receiver/run/lifecycle regressions: an authenticated progressing
slow-drip body (defeating the per-read bound) whose owned accepted
socket is observed closed by the peer after stop (repeated stop
safe; unrelated own-session process survives); a closed listener
with idempotent stop; an incomplete teardown (handler outliving a
tiny quiesce grace) yielding the fixed `cleanup_failed` outcome and
never `completed` (closed enum set plus honest boolean only, no raw
error details); failure/timeout cleanup under a non-progressing
stalled read; actual-issued default-seed and custom-seed (arbitrary
declared path plus explicitly supplied bytes) positives retaining
useful exact received text with `content_verified` true; and the
child-mutated original negative (a child that rewrites its own seed
after a legitimately issued read: marker bytes nowhere under the
output directory, frame stripped to `content_unverified`) plus an
unseeded-path negative. Verification is bound to the IMMUTABLE
original seed bytes recorded before child launch — never a
child-writable file reread at finalization. Full-suite
skip accounting stays distinct: the 27 prior stage skips plus exactly
one 017-i foreign-ownership `chown` environment skip — the
simulated-UID proofs and the new 017-k lifecycle proofs are passing
tests, never skips. No actual client, provider session, or model
call is made; the actual capture and process/chunk collector remain
`NOT RUN`.
Round 017-m repairs the per-request pure read-observation identity
and causality pairing on the same inert surface (no capture utility/
child modification, no actual capture, no process collector), with
the new public suite
`tests/test_bundle_d10_matrix.py`: (1) identity conflicts precede
read eligibility — the schema-evidenced call-ID inventory is
eligibility-independent (an unknown/ineligible call colliding with
an eligible call ID is a typed `DUPLICATE_CALL_ID` conflict, never
filtered away; unknown calls never acquire; unrelated unique unknown
calls neither recorded nor poisoning separate valid chains; absent/
null/empty `MISSING_CALL_ID` and non-string `MALFORMED_CALL_ID` stay
observable, never invent an ID, and never acquire content); (2)
structural causality — a result attaches to its matching call only
when its exact numeric structural position follows the call's (the
`input` item index; the Chat `messages` index of the assistant
message carrying the call), never from lexical call IDs or JSONPath
string sorting, and a pre-call result keeps its chain typed
`PRE_CALL_RESULT`, non-removable, with no bundle/member digest, no
source span and no proven-executed claim. The public D10 composition
matrix covers ordinary valid reads amid unrelated calls, same-ID
conflicts across supported/unsupported names and relevant families,
identical/conflicting duplicate calls, missing/empty/malformed IDs,
orphan/mismatched/pre-call outputs, duplicate same-call results
(still unsupported absent later earned process-chain evidence),
non-monotonic IDs and >=10 structural positions, with independent
valid chains still earning exact source span/digest/members/width
alongside the rejected ambiguous chain; selected endpoint, mixed
domain and ignored other-domain behavior preserve prior law. The
pure D09 unsupported/partial negative matrix (command substitution
`$()` and backticks, false/conditional/unexecuted branches, partial
`head`/`sed` readers, known truncated/missing/running/unknown
wrappers — typed unsupported/partial, never complete whole-file
acquisitions, contrasted with the exact proven empty successful
output) makes no shell/filesystem/network execution claim, adds no
grammar family, and is not multi-chunk evidence: D09 multi-chunk/
process association remains `NOT RUN`/deferred. All previously
earned literal read/plan/loop positives, exact spans, aggregate work
bounds and occurrence/member-hash/slot-width laws are preserved;
tests assert unchanged inputs and non-echoing reprs. No actual
client, provider session, or model call is made; the actual capture
and process/chunk collector remain `NOT RUN`.
Round 017-n completes the per-request identity-inventory repairs
required by 017-m on the same inert surface (no capture
utility/child modification, no actual capture, no process
collector), with public regression proof in
`tests/test_bundle_d10_matrix.py::TestWireFamilyInventoryAndBounds`:
(1) the Responses `custom_tool_call` wire family joins the
schema-evidenced call inventory alongside `function_call` — identity
bookkeeping only, earning no custom-tool read parsing/execution/
acquisition (a custom call named like a supported tool still never
acquires), its opaque `input` never captured as arguments or
reinterpreted as a shell/source oracle, no generic unknown-family
wildcard recognition — so an exact colliding ID makes the ambiguous
eligible chain typed `DUPLICATE_CALL_ID` non-removable with no
acquired digest/span/proven members (both collision orderings,
repeated identical/conflicting records; every relevant occurrence
observable, never first-match), while a unique unrelated opaque
custom call neither records nor poisons a separate valid read and
its opaque input is never echoed; (2) `max_commands`/`max_outputs`
bound the **complete** relevant inventory — every schema-position
call record (unsupported names, opaque custom records,
missing/empty/malformed IDs) and every result record (including
invalid IDs) — before any identity map or typed diagnostic is
retained: a fixed non-acquiring `OVER_BOUND` record (at-limit and
one-over on Responses and Chat, including many `tool_calls` in one
assistant message, and a late collision beyond any retained prefix;
the scan itself is bounded by the existing `max_items` item bound),
scoped to the selected domain under explicit endpoint selection,
with mixed input bounded across its inspected domains and the
useful unknown+valid within-limit controls preserved; (3)
absent/null/empty result IDs are typed `MISSING_RESULT_ID` and
present non-string result IDs (list/dict/number/boolean) typed
`MALFORMED_RESULT_ID` — fixed, non-echoing, unpaired limitations on
Responses `function_call_output` and Chat `role=tool` positions that
never invent an ID, hash an unhashable value, attach the output to
any call, or acquire, while separate well-formed chains remain
useful within the total limits and the existing
duplicate/missing/mismatched/structural pre-call typing and
namespace/domain separation are preserved. All previously earned
D10 numeric causality tests, selected/mixed/ignored domain behavior
and literal read/plan/loop positives are preserved with unchanged
inputs and non-echoing reprs; no shell/filesystem/network oracle or
new dependency. No actual client, provider session, or model call is
made; the actual capture and process/chunk collector remain `NOT
RUN`.
Round 017-o completes the two remaining per-request boundary repairs
on the same inert surface (no capture utility/child modification, no
actual capture, no process collector), with public regression proof in
`tests/test_bundle_d10_matrix.py::TestInventoryAllocationAndIdRepre
sentation` (13 tests): (1) the complete relevant call/result
inventory bounds are enforced **before retention** — a no-retention
streaming preflight decides `max_commands`/`max_outputs` over the
complete inventory (every schema-position call record, every result
record including invalid IDs) and stops at the first exceeded limit,
so an over-bound request is the fixed non-acquiring `OVER_BOUND`
before any record tuple, location string, ID map, typed diagnostic,
argument/wrapper parsing or identity map is retained or built; the
public proof distinguishes early bounded allocation/work from small
final record counts — large prebuilt Responses calls, nested Chat
`tool_calls`, Responses results and Chat results at limit one are
measured (tracemalloc, generous 2 MiB regression ceiling, inputs/
imports/full-payload fingerprinting excluded — not a total-RSS
guarantee), with at-limit useful reads keeping exact
digest/span/member/width, one-over/late-collision/invalid-ID/
ignored-domain/mixed shapes keeping their typed behavior and inputs
unchanged; (2) exact internal call/result IDs stay usable (internal
fields asserted exact on Responses and Chat paired/orphan/duplicate/
missing-result paths) while operational `str`/`repr` of report/read/
unpaired objects never echo private ID values — synthetic canaries
only, the observable no-ID state (empty string), fixed enums,
counts, locations and digests remain visible in representations.
This supersedes the 017-n wording that the bound was decided "before
any identity map or typed diagnostic is retained" (the pre-017-o
code had retained the record lists and location strings first); from
017-o the bound is decided before any retention. All previously
earned D10 causality/inventory tests, selected/mixed/ignored domain
behavior and literal read/plan/loop positives are preserved with
unchanged inputs; no shell/filesystem/network oracle or new
dependency. No actual client, provider session, or model call is
made; the actual capture and process/chunk collector remain `NOT
RUN`.
Round 017-p extends the same inert surface in two bounded parts.
First, the per-nested-container scan guard: each inspected
assistant `tool_calls` list is length-tested against the existing
`max_items` item bound before it is iterated, parsed or retained
(O(1) per list; `max_items` is per-container, never a total across
lists — an at-limit nested list observes normally), with the public
proof in `tests/test_bundle_d10_matrix.py::TestNestedScanBounds`
(at-limit useful read, one-over with/without a valid call,
selected-domain scoping, mixed over-bound, malformed nested types,
non-assistant uninspected, per-container-not-total).  Second, the
disposable-CI containment capability (D10 prerequisite; the first
remote job run at the previously published head `ec08a1b` failed
`runtime-invalid` and this round corrects the runtime-shape
handling — the capability qualification is `PENDING` strategic
review, with the exact execution outcomes/SHAs in the immutable
round report
`oap/reports/017-p-observation-native-fixture-prerequisites.md`):
`scripts/cache_native_containment_probe.py` (in-container
stdlib probe, closed JSON pass record: dedicated nonroot identity,
all-zero capabilities, no-new-privs, seccomp filter mode, private
pid/mnt/ipc/uts/net against the shared user namespace, parent
sentinel absence, private loopback echo, parent listener
unreachable, read-only rootfs, explicit bounded tmpfs roots, exact
memory/swap/pids/writable-storage limits, keyring syscall denial —
x86_64 `add_key`=248, `request_key`=249 (four arguments),
`keyctl`=250 unknown command, expecting EPERM — and child deadline
kill) and `scripts/cache_native_containment_ci.py` (host-side
runner whose entry guard refuses any context that is not both
`GITHUB_ACTIONS=true` and `RUNNER_ENVIRONMENT=github-hosted`):
digest-pinned byte-identical-base fixture image, create-before-start
ownership (bare 64-hex CID), closed inspection extraction (actual
`ReadonlyRootfs` field plus exact default runtime identity), the
ordered parent-death proof (token-bound live owned descendant
positively observed exactly once before container teardown, its
disappearance and the container's verified absence after, unrelated
parent sentinel surviving), bounded capture (reader-thread-owned
pipe; held-pipe convergence by exact owned group kill after a
bounded grace; failed capture is the fixed closed state
`output-read-failed`, never an empty-success output or an uncaught
thread exception), verified image removal (result-checked `rmi`
plus a successful authoritative query reporting no such
image/object — a daemon/query failure is a distinct unverified
state, never conflated with absence; cleanup failures stay visible
even when a primary check also failed) and a fresh owned 0700
scratch root validated as-given (no symlink or `..` alias
laundering of a pre-existing target).  The public orchestration
suite `tests/test_cache_native_containment_ci.py` (61 tests —
fake docker emulation plus tiny real owned children only; no docker
daemon, namespace or syscall probe) covers these contracts locally;
the remote proof is the `cache-native-containment` job on a
disposable `ubuntu-latest` hosted runner (stdlib only, no secrets
forwarded to the fixture — the job maps no secrets and the runner
accepts no credentials — fresh owned work root under the
documented `RUNNER_TEMP`).  No genuine client, model, GPU or
gateway activity: this capability proof does not qualify a genuine
native client; D09 remains `NOT RUN`; no v1 runtime claim.
Round 017-r adds the serial right-pane native fixture preparation:
the typed fixture model (phases, budgets, closed record schemas,
bounded diagnostic traversal), the 21001 controller/issued
registry, the 21002 stand-in subject and the 21001 exporter client,
the distinct fixture image, and the host runner that drives ten
fresh-container scenarios on disposable GitHub-hosted CI only.
The public suite `tests/test_cache_native_fixture.py` (207
tests — pure phase/budget/schema/selection validation, bounded
diagnostic traversal, closed record validators including the
pinned public LICENSE/NOTICE byte identities, the reconciled
writable-data closed record including the explicitly bounded
/dev/shm, the coherent finite mount-table relation (documented
data mounts plus masked /dev/null aliases are distinct records
within the scanned table, bounded by the closed scanner record
cap), issued-registry binding and numerical process
separation),
`tests/test_cache_native_fixture_controller.py` (33 tests —
request/issuance causality, strict-after-result positions,
quiesce/export frames over the real socket),
`tests/test_cache_native_fixture_standin.py` (76 tests — the
exact reviewed keyring/ABI/caps/namespace/EROFS/CPU surface,
bounded metadata diagnostic, hang/stop-owned records, the
reconciled writable-data mount inventory from the actual
mount table — bounded input, virtual/device classes distinct,
the masked /dev/null file aliases of runc's maskPaths admitted
only on the exact source-root file identity, the narrow
known-default path and the chr 1:3 device (counted as device
surface, never writable data),
fail-closed on unlisted writable data or missing documented
roots — and the eight-test stopper identity suite: vanished,
self and unverified targets are never signalled; pidfd-open
before verification and signal; the descriptor closed on every
path; the exact SIGTERM/si_code/flags send ABI; the declared
closed failure when the pidfd API is unavailable; and the
owned stop with unrelated survival through the recorded fake
signal) and
`tests/test_cache_native_fixture_ci.py` (219 tests — closed
command grammar including the create-argv/allowlist lockstep
with the explicit `--shm-size` bound and the bound-child env
regression (an explicit child environment reaches the child on
the normal pipe path and the owned PTY path alike, and the
default keeps inheriting the ambient environment), host
ledger with distinct
measured quantities and pre-work reservations, timed-out-capture
drained accounting, over-bound /proc scan rejection, the actual
HostConfig schema verification — the real SecurityOpt string
list, ShmSize, and the null-or-empty Binds/Devices/
VolumesFrom/DeviceRequests absence grammar (daemon
serialization: nil→null, empty list→[]) — non-empty values
remain denied — with the invented legacy keys
consistency-checked when present, the full
FakeDocker orchestration with its named failure paths (preflight
runtime refusal, image collision/absence-unverified, sentinel
death, descendant leftovers, export SHA mismatch, malformed or
prefix-missing quiesce, crash-code mismatch, leftover container,
deadline expiry converging through cleanup, one-shot host
cancellation preserving the KeyboardInterrupt while cleanup runs
to completion, cleanup failure exposed on the preserved
cancellation, and a timed-out cleanup operation charging its
measured drained bytes once while later independent cleanup
continues), the actual-path capture tests (same-group held pipe
convergence, escaped holder's fixed failure with exact test-owned
reap, PTY held pipe, and the read-error fixed state), the
actual-path loopback wire tests, protected atomic evidence
publication including the commit-boundary
concurrent-destination control, and the actual
archive/fetch/extraction helper negatives against small synthetic
bytes and fake HTTP, and the closed stand-in fail-token channel
(an allowlist-only detail on the fixed scenario failure record,
scoped to the run that observed it; unknown, malformed or missing
child tokens stay generic and raw output never propagates), and
the runner's closed failure diagnostic (tested through main)
carries exactly one closed stage token — the ORIGINAL failure's
stage, preserved separately from the cleanup umbrella's "cleanup"
stage — and maps a closed-record validation rejection only
through the model's finite field universe (closed category plus
field membership, reconstructed output; unknown or oversized
field text stays generic "record-validation"), with owned
timeouts named "deadline-expired" and all other escapes
"internal" plus stage; no raw exception, record or traceback
ever reaches the job log)) cover
these contracts locally; no test
launches docker, a container, a namespace or the native binary
(no secrets are forwarded to the fixture: the job maps no secrets
and the runner accepts no credentials).  The remote proof is the
`cache-native-fixture` job (stdlib only, fresh owned work root
and evidence destination under the documented `RUNNER_TEMP`); the
public pinned Codex 0.164.0 musl archive is fetched,
size+digest-verified, bounded-extracted and statically hashed in
CI — it is NEVER executed there.  The fixture confinement bounds
the reconciled writable-data surface explicitly: three owned
tmpfs budgets (192 MiB total) plus the daemon's /dev/shm bounded
to 64 MiB (256 MiB effective total), verified on the runner side
from the actual HostConfig and measured back by the subject from
its actual mount table.  No genuine client, model, GPU or
gateway activity: this preparation does not qualify a genuine
native client, D09 remains `NOT RUN`; the bounded 017-r fixture
preparation is accepted (strategic decision at head `2ce9dcd`,
with the recorded wording limitations), and the serial
foreground handoff itself remains a later separately authorized
order; no v1 runtime claim.
Round 017-s adds the local fixture preparation suite
`tests/test_cache_native_fixture_local.py` (48 tests —
order-bound opt-in versus the hosted-only guard and one-attempt
admission; the single-owner protected lifecycle prepare /
observe / rehearse / finish / abort through the real control
client (fresh 0600 socket in the 0700 control root, exact
run-id binding, closed response records, absolute client
budget, foreign-run/missing-state/overbound refusals);
variant-aware finish compositions (python-rehearsal, unobserved,
external) with the retained summary bound to the decoded
payload and cross-variant forgery negatives; the curated
subject-facts closed contract; the section-2 verified local
endpoint binding (explicit remote DOCKER_HOST or foreign
DOCKER_CONTEXT refused before any mutation, the daemon's own
default context admitted with the read-only daemon-name
corroboration as the first docker action, a foreign daemon name
closed-refused with the measured one admission, a missing or
non-socket verified path refused before any docker command, and
the once-per-owner frozen child environment with DOCKER_HOST
pinned to the verified local socket surviving later
HOME/DOCKER_CONFIG/DOCKER_CONTEXT drift); driver composition
negatives (same-session refusal, startup wait timeout,
capture-cap fault, final-wait expiry refusing before a
blocking wait, held reader and read-error faults, valid
baseline with real retained-evidence validation) and public
main refusals (missing state, expired anchor before IO).  Fake
Docker/socket/time/identity seams plus tiny exact-owned Python
children only; no docker daemon, namespace or syscall probe, no
children only; no docker daemon, namespace or syscall probe, no
secrets forwarded to the fixture, and no Codex binary executed
in tests/CI — the pinned public binary is fetched and hashed
statically in the R `cache-native-fixture` job and is NEVER
EXECUTED there, including help/version, per the RIGHT-only
startup law.)
All v1 runtime criteria remain `NOT RUN` until their owning stage lands. The versioned
contract is documented in
[docs/CACHE-OBSERVATION-CONTRACT.md](docs/CACHE-OBSERVATION-CONTRACT.md).

A stage-scoped synthetic unit/fake test proves its named mechanism within
that stage; it never substitutes for actual-model, genuine-Codex,
native-compaction or artifact qualification. A criterion passes only after its own
required evidence layers pass and are reviewed: pure/unit/fake criteria may
be proven by their named layers, whereas actual-model, genuine-Codex,
native-compaction and artifact claims require their distinct evidence. All v1 runtime criteria are `NOT RUN`
(planned) until their owning stage lands, is implemented, is tested at every
required layer, and is reviewed; no legacy or fixture result substitutes for
them, and a recognized root with absent dependencies fails overall rework
acceptance (O01).
RC10 is the historical baseline for the rework, not a rework-qualified
artifact. The planned v1 configuration surface is documented as planned
and non-runnable in [the configuration
reference](docs/ADAPTER-CONFIGURATION.md); its examples are not runnable
until the configuration implementation lands.

## Gateway contract tests

The dedicated `gateway-contract` job checks out the exact peer in
[the authority fixture](tests/fixtures/gateway/current_peer_authority.json),
verifies origin/HEAD/module metadata, and executes the focused pure contract
suite with network access denied. It rejects zero collection, any skip, failure,
error or incompatible metadata. The normal suite can run without that checkout;
Gateway-dependent modules then skip explicitly.

See [GATEWAY-CONTRACT-CI.md](docs/GATEWAY-CONTRACT-CI.md) for the optional local
command and dependency group. A development peer update does not silently change
a frozen release's Gateway authority.

## Docker and operator qualification

Run Docker qualification only on a disposable Docker host, never implicitly on
the protected model host. CI owns the canonical executions:

| Job | Evidence |
| --- | --- |
| `test` | Lint, format, types, unit/fake tests, documentation and artifact gates. |
| `gateway-contract` | Exact pinned Gateway compatibility with no inference or service activity. |
| `docker` | Fresh built image, actual platform/dependency/wheel identity, signed ingress, readiness, hardening, lifecycle and teardown. |
| `operator-session` | Documented pull-based operator lifecycle against a synthetic registry and fake upstream. |
| `docker-published` | Authenticated pull and qualification of the recorded immutable digest after publication. |
| `cache-native-containment` | Disposable hosted-runner containment capability proof: pinned-base fixture image, explicit confinement surface (network none, read-only rootfs, nonroot uid, cap-drop ALL, no-new-privileges, seccomp=builtin, bounded memory/pids/CPU/tmpfs), ordered token-bound parent-death proof, verified image removal. No secrets forwarded; D09 remains `NOT RUN`. |

Before an image is published, `docker-published` reports an explicit
prepublication `NOT RUN` for image qualification while recording registry facts.
After publication it must exercise the actual pulled digest; a missing or
inaccessible recorded image cannot silently skip.

The runners are [docker_qualification_ci.py](scripts/docker_qualification_ci.py),
[operator_session_ci.py](scripts/operator_session_ci.py), and
[disposable_deployment_qualification.py](scripts/disposable_deployment_qualification.py)
for the secondary systemd mechanics. Inspect their `--help` and the exact
[CI workflow](.github/workflows/ci.yml) before running them on a disposable host.
They use fake upstreams and must prove container/unit/listener teardown.

## Live model and actual Codex tests

These require separately authorized access to the exact protected fixture.
Do not restart or reconfigure vLLM, change credentials, or alter active client
profiles to make a test run. Calls must be authenticated, bounded and serialized
where needed to avoid starving existing users. Capture only sanitized facts.

The live matrix covers health/models, Responses text, function tools, SSE,
multi-turn continuation, one-image vision, full-image-then-crop history,
compiler miss/hit behavior, governance sentinels and privacy checks.
Actual Codex tests additionally use a disposable repository and ordinary local
tools to exercise the complete client path. History reduction at the adapter
boundary is distinct from a native Codex compaction trigger; accepted evidence
does not claim the latter.

[The acceptance ledger](docs/OBJECTIVE-004-LEDGER.md) and
[vision fixture record](docs/VISION-ACCEPTANCE.md) describe the historical
fixture-specific results. They do not establish generic model/hardware support.
The repository-only rehearsal and Codex helpers are not runtime product code.
Their detailed safety contracts and prior runs are preserved in
[HISTORY.md](docs/HISTORY.md) and the immutable OAP evidence.

## Release-candidate qualification: fixture CI vs real client

Two distinct mechanisms, never interchangeable:

- **Deterministic fixture CI (every round).** Ordinary CI runs the
  sanitized Codex-envelope fixtures and the full-application
  fake-upstream regressions, including the namespace-tool envelope that
  reproduces the RC2 `TypeError: unhashable type: 'dict'` image-policy
  crash. No secret endpoint, no model, and no real Codex binary are
  required or used.
- **Opt-in real-client RC qualification (only when the designated client
  and backend are available).**
  [real_codex_rc_qualification.py](scripts/real_codex_rc_qualification.py)
  runs bounded, fail-closed, privacy-bounded arms of genuine Codex CLI
  sessions over the supported standalone loopback topology: disposable
  Codex home/repository → `127.0.0.1:18031` Local Coding → the tested
  Qwen/vLLM endpoint. Standalone loopback Local Coding qualification
  requires **no SLAIF API Gateway** (gateway ingress disabled; no signed
  Gateway headers invented). The required arms are VISION (one-image
  retain-newest, constitution/compiler disabled), CACHE (image
  passthrough plus enabled constitution/compiler with a static
  single-user identity), and BOTH (both mechanisms, same identity); a
  contextual DIRECT control may be recorded when safe but never
  substitutes for a product arm. Only fixed categories, counts, statuses,
  version/hash, timings, and boolean verdicts are captured; disposable raw
  state is deleted after sanitized facts are extracted into an
  append-only, content-free testing-ledger directory. The client is
  invoked with the client-side sandbox set to `danger-full-access`
  because the protected host forbids the unprivileged user-namespace
  network setup that bubblewrap requires (a protected host state the
  gate never changes); the effective controls are the disposable
  workspace and Codex home, the loopback-only adapter, the fixed
  synthetic prompt, no credentials in argv, and bounded attempts and
  timeouts.

RC history: RC2 (`0.1.0-rc2`) failed external real-Codex 0.149.0
qualification; the immutable [testing ledger
001](oap/evidence/testing-ledger/001/README.md) records the exact
pre-inference `TypeError` on the VISION/CACHE/BOTH arms. RC3
(`0.1.0-rc3`) contains the image-policy compatibility repair; its
real-client qualification facts (the exact qualified client version and
binary SHA-256, the VISION/CACHE/BOTH verdicts, and the sanitized
evidence path) are recorded in the RC3 artifact record
(`slaif-rc-record-v3` compatibility facts, closed-schema), the
deterministic handoff, and the ledger evidence. A green deterministic
fixture is never real-client evidence, and a missing, unavailable,
skipped, or blocked real-client arm is a blocker, never a pass. No
benchmark ran; the final public release remains false; the package
remains private; the protected cutover remains false. RC4
(`0.1.0-rc4`) qualified in scope (immutable [testing ledger
003](oap/evidence/testing-ledger/003/README.md)) but was rejected
overall: after publication, the record-present suite exposed a stale
RC3 identity residue, the repair committed a post-publication SOURCE
change, and the post-publication provenance rebind recorded that later
source-input map while the record still named the earlier immutable
image source; its record set is archived byte-identical under
`packaging/releases/0.1.0-rc4/`. RC5 (`0.1.0-rc5`) passed its
product repair, its scoped genuine-Codex qualification (immutable
[testing ledger 004](oap/evidence/testing-ledger/004/README.md)), and
its pulled-image qualification, but was rejected overall: the first
post-publication record-present validation failed a mandatory gate, and
the repair was a tracked source correction committed after the
immutable candidate freeze; its record set is archived byte-identical
under `packaging/releases/0.1.0-rc5/`. The 014-d successor round was
abandoned before any push, tag, or publication: its first post-freeze
full suite required tracked test corrections, triggering the round's
literal fail-closed rule, and its re-freeze attempt was stopped; no RC6
remote commit, release workflow, tag, registry mutation, or testing
ledger exists, and none is claimed. RC7 (`0.1.0-rc7`) qualified in
scope (immutable
[testing ledger 005](oap/evidence/testing-ledger/005/README.md)) and
was published as a private candidate; its record set is archived
byte-identical under `packaging/releases/0.1.0-rc7/`, and its aliases
remain occupied and immutable. RC8 (`0.1.0-rc8`) qualified in scope (immutable
[testing ledger 006](oap/evidence/testing-ledger/006/README.md)) and
was published as a private candidate: the human-supplied external
review input `CODE-DEFECTS.md` (external input, not a repository file
and not part of any benchmark archive) motivated two independently
verified product defects, both repaired — P01 (upstream HTTP-error
causes were discarded before close; now a bounded private
classification with a closed reason enum, a dedicated
low-cardinality private counter, and the unchanged generic public
error) and P02 (explicit compiler output truncation was collapsed
into invalid output and retried with the same known-insufficient
allowance; now a typed `output_truncated` outcome with a bounded
adaptive allowance, the `compiler-v3` behavior version, and
ceiling-bound fingerprint/cache/rehydration identity) — and its
pulled-image qualification passed. RC8 makes no claim that Local
Coding caused the rejected requests or task mistakes. RC8 was
rejected as the FINAL Objective-015 handoff candidate solely because
its frozen read-only CI registry baseline (a member of the 130-entry
frozen source-input map, hence immutable after publication) claimed
to cover the archived RC7 alias pair while its literal
immutable-history set stopped at RC5; the RC8 source/provenance
binding could not be corrected post-publication, so RC8 is preserved
permanently: its record set is archived byte-identical under
`packaging/releases/0.1.0-rc8/`, and its aliases remain occupied and
immutable. RC9 (`0.1.0-rc9`) carried that correction (every archived
RC alias pair digest-asserted in the read-only baseline from a shared
single source of truth, with a deterministic regression and the
intentional RC6 absence preserved), qualified in scope (immutable
testing ledger 007), and was published as a private candidate — but
was rejected as the FINAL Objective-015 handoff candidate solely
because its frozen historical replay test was defective: the
regression's fallback parser passed the ``tags =`` assignment
statement to ``ast.literal_eval``, so the 015-a frozen-source replay
died with ``SyntaxError`` before the alias comparison and the claimed
RC7-omission failure was never mechanically demonstrated. Its record
set is archived byte-identical under
`packaging/releases/0.1.0-rc9/`, and its aliases remain occupied and
immutable. RC10 (`0.1.0-rc10`) is the successor candidate: the narrow
regression correction (the fallback parser parses the tuple
expression and fails closed on malformed, ambiguous, or non-string
content; focused parser tests) plus the corrected harness reruns for
the next immutable testing ledger (expected number 008). No benchmark
ran; the final public release remains false; the package remains
private; the protected cutover remains false.

## Evidence and review

Sanitized evidence export uses [safe_evidence_export.py](scripts/safe_evidence_export.py).
It validates bounded closed schemas and privacy rules, refuses path/symlink
escapes and overwrites, and writes atomically under `oap/evidence/`. Its historical
audit preserves exact prior facts; it does not reconstruct missing results or
rerun protected inference. Never substitute raw captures for sanitized evidence.

CI includes CodeQL analysis for Python and GitHub Actions. Review findings and
their dataflow; a dismissal needs a specific documented reason. Do not exclude a
query just to hide a finding.

Merge requires fresh successful checks for the exact head plus review of scope,
security, semantics, documentation and operational effects. Historical green CI
and report prose cannot establish that the current candidate passes.

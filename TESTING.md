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
`tests/test_cache_native_fixture_standin.py` (102 tests — the
exact reviewed keyring/ABI/caps/namespace/EROFS/CPU surface,
bounded metadata diagnostic, hang/stop-owned records, the
reconciled writable-data mount inventory from the actual
mount table — bounded input, virtual/device classes distinct,
the masked /dev/null file aliases of runc's maskPaths admitted
only on the exact source-root file identity, the narrow
known-default path and the chr 1:3 device (counted as device
surface, never writable data),
fail-closed on unlisted writable data or missing documented
roots, the 017-x closed `hold` mode (the subject verifies its own UID and GID are BOTH the subject identity, flushes the closed identity record — pid + immutable starttime + uid/gid/groups + the bound 32-hex token, a PID-reuse-safe identity for the host-side bounded exact-CID correlation — FIRST, then holds hard for at most 20 s, further capped by the SAME finite absolute experiment anchor (a missing anchor is a closed refusal, never the legacy relative fallback; a non-finite or already-elapsed anchor is expired), and exits 0 naturally: no model POST, no child, no shell — every pre-hold failure is a closed non-echoing refusal before any hold) and the closed non-consuming `observe` /state record — and the eight-test stopper identity suite: vanished,
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
`tests/test_cache_native_fixture_local.py` (49 tests —
order-bound opt-in versus the production hosted-env guard
(ambient GITHUB_ACTIONS refused at construction with no attempt
recorded) and one-attempt admission; the single-owner protected
lifecycle prepare /
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
secrets forwarded to the fixture, and no Codex binary executed
in tests/CI — the pinned public binary is fetched and hashed
statically in the R `cache-native-fixture` job and is NEVER
EXECUTED there, including help/version, per the RIGHT-only
startup law.)
Round 017-t adds the order-binding and native-handoff
preparation-contract suites
`tests/test_cache_native_fixture_binding.py` (45 tests —
valid active-order/source resolution strictly read-only,
foreign/malformed/duplicate/dirty/mismatched binding
refusals, the closed git grammar, the stable per-order
one-attempt namespaces across head/directory/phase changes,
the preserved exhausted 017-s record (historical schema,
never rewritten) and shared-schema/malformed/untrusted
refusals) and
`tests/test_cache_native_fixture_native_prep.py` (124 tests —
closed /proc parsers; worker/Bash group facts with bounded
membership tri-stated row by row (only verified-gone churn
ignored; unreadable still-existing or capability-less
inventory refused, never skipped), separately grouped tool
sessions and the never-guessed job; the subject-identity law (exact CID/UID/GID/
groups/argv/binary/birth/PTY, with the expected-PTY
provenance — native qualification requires an actually
bound, matched, nonzero expected PTY, and an unobserved
expectation or a measured tty0 subject is never ready) with
wrong-identity and vanished negatives; the independently
measured same-job restoration matrix (a refused stop can
never later claim a recorded stop or restoration); the
owner-final-facts
closed parser; the closed verdict composition where
unknown/unobserved/incomplete facts never become ready/pass
and caller-authored flags are refused, where a historical
S-scope owner record decodes and validates as its own scope
but can never qualify a native-ready composition (the
closed `owner-scope-not-native` refusal), where an honest
started-but-not-ready native-owner record never becomes
ready, and where the owner's registered artifact binary
must equal the measured subject executable; the native-owner evidence
producer that invokes the owned finish/export/teardown
measurement seam, validates the FULL measured export
payload with the actual shared export validator,
recomputes the export digest itself, and binds the measured
teardown to the exact immutable order/source-head/run/CID/
image/binary context (closed six-key measured context;
incomplete, contradicting or forged contexts are closed
refusals; the image id admits only the bare digest or the
actual measured `sha256:<digest>` form, the typed fact
normalized to the bare digest; the consumer validates the
exact closed record key sets, top level and nested, and
unknown or missing fields are closed non-echoing refusals); the real owned measurement
adapter, whose native started/ready facts derive ONLY from
the public workflow's measured pre-teardown subject receipt
(a caller flag or a run with no measured subject can never
mint them); the public prepare/observe/finalize workflow
where registration collects before recording, prepopulated
records are not workflow evidence, and finalize binds a
native-owner record to the immutable workflow binding's
order, literal source head and run and the retained subject
receipt to that same run; plus the full public lifecycle
positives — including the REAL owner finish/export/
teardown code driven with fake platform operations over
ONE coupled fake process world (the workflow measures the
native subject while the same CID is alive, records the
stop, the exact CID removal updates the same world to
absent, and the same worker is restored before finalize) —
and the cross-context refusal contrasts).  Pure/fake seams
plus tiny exact-owned Python children for the real /proc
mechanics only (each exact-owned child is killed by the
test's own cleanup if still alive; no signal to the real
worker/Bash group or any unrelated process, no container,
no native binary); a static AST law proves the preparation
module imports no subprocess/signal/pty surface and
contains no host-signal call.  Software preparation is
INERT: these tests earn no native, worker-stop, Docker or
handoff qualification.
Round 017-v adds the public native-owner
composition suite `tests/test_cache_native_fixture_
native_owner.py` (12 tests — the full public happy
path over ONE coupled fake process world: start ->
prepare -> held observation -> the separately
measured stop -> the actual later subject launched
bound to the owner's OWN registered target CID -> the
public staged `register_subject` (collects before
recording; the CURRENT stable-stop predicate
re-verified before any identity commit; the frozen
W/B baseline unchanged; the registered run immutable)
-> `finish` driving the REAL owner finish/export/
teardown with fake platform operations (the exact CID
removal updates the same world to absent) -> the
same-worker restoration -> `publish_native` retaining
the DISTINCT native-scope terminal records (the
owner evidence without the historical S whole-run
false assertions; the closed
`slaif-native-owner-run-v1` record whose attempt
field carries the ALREADY-KNOWN journal state, never
a predicted finalize token) with the honest
publication ordering (the protected record retained
FIRST, the same-order journal finalized ONLY THEN,
the real finalize token retained in RAM only); the
constructor's verified-binding admission law (a
non-binding type refused, an exhausted admission
refused before any external mutation, a stale bound
head refused before any work); the staged
registration negatives (pre-stop, pre-prepare,
double-registration, resumed-worker, foreign
expectation run); the preparation-only honest
not-ready publication; the owner-failure honest fail
and the abort honest `aborted` (no journal rewrite,
no admitted pass from a failed publication); and the
closed native-scope validator's exact key/grammar/
ledger law with cross-scope refusals).  Fake
git/platform/process seams and owned synthetic
repositories only; the real backend code is imported
and its real methods driven, the platform operations
are faked; no actual Docker operation, no native
launch (including help/version), no worker stop, no
TTY/job manipulation, no real fixture admission in
the real checkout, no host signal, no CLI entry —
these tests earn no native, worker-stop, Docker or
handoff qualification.

Round 017-w extends that suite to 19 tests and
adds the same-owner coherence law: the public staged
registration is bound BEFORE any staged receipt
commit to THIS SAME prepared owner's measured
registration (the owner's own registered CID and
artifact binary must already be measured and equal
the operator's expectation — the closed
`native-owner-registration-unmeasured` before
prepare, `native-owner-subject-cid-mismatch` and
`native-owner-subject-binary-mismatch`; a refused
registration commits nothing, and a later genuinely
matching registration in the same still-valid
measured phase succeeds); the actual repository
context at owner construction is compared with the
ORIGINAL frozen binding through the complete
frozen-context revalidation seam (not a fresh
resolution whose result is discarded) — a
repository-identity drift after admission is
refused before owner adoption with the already-won
attempt closed terminal `fail` and no external
action, and a contradictory `bind_head` argument is
refused before adoption; and native publication for
the completed owner is a ONE-SHOT terminal
transition (the transition begins at the read of
the owner's terminal outcome; the ACTUAL bound
journal state is read, never assumed — the pass
path requires the attempt still running, a terminal
owner outcome requires that same terminal state or
a verified fresh finalization; a pre-retention
measurement/validation/serialization/destination
failure closes the still-pending attempt
truthfully — the primary closed refusal propagates
unchanged, an unexpected serialization error
surfaces as `internal` — while a post-retention
unverified or raced finalization is a closed
failure that preserves the retained bytes and the
actual journal facts as-is; a fresh-path retry
after any publication failure refuses without a new
qualifying record, relabel or journal reset).
Seven new tests: the foreign-owner-context
refusals with recovery, the origin drift before
owner construction (terminal `fail`, no external
action), the failed publication with the fresh-path
retry refused (journal `fail`), the unverified
finalization (the pending journal fact preserved),
the raced terminal fail (the raced journal fact
preserved), and the completed-run measurement and
serialization failures.  Fake git/platform/process
seams and owned synthetic repositories only; no
actual Docker operation, no native launch
(including help/version), no worker stop, no
TTY/job manipulation, no real fixture admission in
the real checkout, no host signal, no CLI entry —
no native, worker-stop, Docker or handoff
qualification is earned.

Round 017-x adds the live Python executable capability suite
`tests/test_cache_native_fixture_exec_capability.py` (34 tests in three
distinct layers, not conflated: (1) the REAL CLI admission tests (the
closed `main()` grammar — one subcommand, the bound order, `--record-
out` required by the preflight; invalid forms refused before any launch)
plus the child-owned resolve+admit law (the sealed child admits ONCE; a
post-admission constructor failure closes the same won attempt; an
exhausted running journal is refused, never adopted or reconstructed);
(2) the scripted driver bootstrap tests (the real driver launches an
ACTUAL exact-owned Python child — the fake owner side bootstraps the
fresh protected control root and publishes the closed state with the
child's own pid, so the driver's startup verification and owner wait
observe a live owner exactly as the real composition does: the pre-
existing-control-root refusal before any launch, the foreign-prior-owner
state refusal (no command, no journal mutation), the scripted full
positive measuring the subject WHILE ALIVE, and the full-driver refusals
— failed sealed startup with the child's closed reason adopted, failed
hold, capture cap, read error (the live reader state read after drain,
the primary preserved), expired budget before any blocking wait,
ambiguous/duplicate/identity-mismatch candidates, foreign/S-scope
evidence never adopted); and (3) the in-process real public-owner tests
(the REAL `LocalFixtureOwner` public interface and the driver terminal
are driven in-process with fake platform operations: the coupled
positive measures the scoped read BEFORE the owner finish, the abort
convergence, the retention and finalize orderings — the bound verified
evidence first, refusals closed `fail` without journal pass, the post-
retention unverified/raced finalization preserved — plus the cleanup-
failure and unrelated-survival refusals and the record-out-inside-work
read-only preflight refusal, for absolute and relative work/destination
forms). Across these layers the shared closed law is proven: the guarded
`top` inventory grammar (default and real header forms, exactly one
verified PID column, the 96-row bound, duplicate/malformed/overbound
refusals), the issued-marker correlation controls (FRESH vs pre-launch;
ambiguous, duplicate and identity-mismatch refused), the scoped-read law
(a readable coherent identity with an absent executable is `unknown`,
never an artifact-hash fallback; a reused PID/birth mismatch refused
before any exe read; frame races and a vanished subject refused), and
the tri-state discovery absent-versus-foreign-scope contrast. These
compositions are useful FAKE proof of the named mechanisms — the actual
Docker operations and the fixture image are faked in every test; they
are not one full sealed-real-owner end-to-end test. Pure/fake platform
seams plus tiny exact-owned Python children (each exact-owned child is
cleaned up by the test's own bounded cleanup if still alive; no signal
to any real worker, Bash group or unrelated process; no container of any
kind). The actual outcome of the ONE authorized attempt RAN
EXACTLY ONCE at literal implementation head
`e5215ce1a96b4dbecdcca5157b6a21ef30a6b1da` (run
`9fd5cf1d95924a47b8bf53e8624242a5`): a terminal FAIL at
prepare-target with `controller-not-ready` and `capability`
null — no complete preparation, hold, subject identity or
executable result (neither a readable nor an unreadable
executable was established); the admission is terminal fail
and is never reset, retried or relabeled; the measured
outcome is recorded in the immutable round report. D09
remains NOT RUN; no v1 runtime claim.

Round 017-y adds the closed readiness diagnosis and the
second explicit sealed entry to the capability driver
(the 017-y entry, record `slaif-017y-exec-capability-driver-v1`
paired ONLY with that entry; the historical S/X entries,
record/order pairs and the consumed X namespace unchanged):
on a nonzero bounded readiness exec, ONLY the fixed probe's
own exact finite closed failure record refines the original
`controller-not-ready` category as `controller-not-ready:<cause>`
(the fixed measured causes `uid-not-21001`, `pid1-uid`,
`health-unreachable`; a missing, malformed, multiple/duplicate,
foreign, over-bound or contradictory output is the fixed
unknown; a raw exception or Docker failure is never a measured
cause; no raw output is ever persisted); the readiness failure
path records NO readiness-poll count (an unmeasured quantity,
never a claim of zero actual readiness polls); and the ONE
conditional bounded lifecycle query (issued only when the
readiness exec produced no closed record: exactly one
allowlisted read-only `docker inspect` of the single finite
fact `.State.Status` on the SAME registered CID, charged to
the SAME owner ledger/END — only the closed line `exited`
refines to `controller-not-ready:container-exited`; any other
status, any other output shape and EVERY query failure
(including a bounded timeout and a transport failure) stay
honestly unknown — query failure is NOT absence).  Ten
focused tests were added across the three fixture suites
(`tests/test_cache_native_fixture_ci.py` now 224 — the
`prepare_container`-level lifecycle increment with physically
coherent fake capture quantities driving the REAL guard/
ledger/deadline; `tests/test_cache_native_fixture_local.py`
now 50 — the closed reason vocabulary;
`tests/test_cache_native_fixture_exec_capability.py` now 38 —
the Y sealed-entry positive through the public driver code
with the matching Y record retained FIRST and only then the
pass finalization, the cross-entry/caller-created descriptor
refusals, the distinct-namespace refusal (an X running journal
never adopted by the Y driver, the X attempt left exactly as
the owner left it) and the public CLI entry selection).
Same seams and law as 017-x: fake git/platform/process seams
and owned synthetic repositories only; no actual Docker
operation, no native launch (including help/version), no
worker stop, no TTY/job manipulation, no real fixture
admission in the real checkout, no host signal.  The actual
outcome of the ONE separately bound 017-y attempt RAN EXACTLY
ONCE at literal implementation head
`35a3bcd7322535dd4a699efc53c0c1c62d4c942e` (run
`fbe526a3290d465298bc8da61ef2a304`): a closed driver PASS
with the complete preparation, confinement and Python-PTY
phases; the subject uniquely identified and measured from
the exact-CID inventory (UID/GID/groups 21002, birth-bound),
then observed `verified-gone` after the bounded hold
(absence only — never an exit code or termination cause),
while the current executable remained the closed UNKNOWN (no
digest; not native readiness and no proven kernel/errno
cause); the admission is terminal pass and is never reset,
retried or relabeled; the measured outcome is recorded in
the immutable round report; D09 remains NOT RUN; no v1
runtime claim.

Round 017-z adds the inert versioned fixture identity
contract suite (`tests/test_cache_native_fixture_identity.py`,
19 tests, 48 collected cases): the original 21002 exact
description, closed-record round-trip and stable canonical
configuration fingerprint (cross-bound to the unchanged
production constants `CONTROLLER_UID`/`SUBJECT_UID`); the old
21002 record law re-proved UNCHANGED through the production
model validator (including its empty-group allowance — the new
description law requiring exactly the primary GID is a new
closed record, never a reinterpretation of old records); the
INERT owner-UID derivation from one faithful eligible nonroot
OS observation (each real/effective/saved triple equal,
nonroot, distinct from the controller, groups exactly the
primary GID — never host supplementary groups); the closed
record codec (bounded bytes, exactly one mapping, no duplicate
keys; malformed/duplicate/over-bound/missing/extra/
contradictory fields, boolean/string/out-of-range/root/
controller IDs and unknown profile/schema all refused with
fixed non-echoing reasons); construction enforcing the
complete field laws (no mutable alias retained, no oversized
caller vector copied, no invalid field can exist in a
description); the bounded READ-ONLY host-ID collector through
a narrow fake OS-read seam (one raw read per collection,
explicit unsupported/unavailable outcome, production data
validation never bypassed) plus one ACTUAL safe current-host
UID read exercised as OS-data-only evidence (never containment
or executable capability); original/new profile isolation even
for equal numeric tuples; deterministic fingerprints
distinguishing every meaningful change; pure decoded/
caller-authored data yielding no ready/admission/native
authority (the public surface is the closed contract set); and
import/use performing no external operation or existing
fixture state change. No Docker, namespaces, native binary,
model/Gateway or live fixture is invoked; no
`.oap-local/017-z` root is created; D09 remains NOT RUN; no v1
runtime claim.

Round 017-aa integrates the inert 017-z owner-UID identity
contract through the real fixture owner and the Python
capability driver (software-only; the integrated path stays
input-gated and UNQUALIFIED until a later actual order — no
actual local Docker/fixture/owner startup, admission,
native/extra Codex, worker stop, signal, TTY handoff or
model/Gateway call in AA; the standard existing CI jobs remain
under their original default scope): the new suite
`tests/test_cache_native_fixture_owner_uid.py` (40 tests)
covers the closed runtime-profile view and immutable owner-UID
data laws — direct pure-data constructor cases (caller
group/argv/bytes alias ownership, bounded lengths checked
before any copy, complete field/exec-user/build-arg/profile-data
consistency with fixed errors) and the v2
reserved-controller-ID negatives, alongside the coupled
real-validator cases (no mutable alias escapes into the frozen
view, no oversized caller vector copied); the real
build context/Dockerfile owner variant (frozen validated IDs
only, same pinned base and immutable artifact/LICENSE/NOTICE,
root-owned immutable profile DATA baked into the image,
explicit readable/immutable module and DATA bytes under the
077/0600 host build context; original defaults fixed-21002
unchanged; missing/unknown/mismatched/unsafe profile data
fails closed, never falls back to original, and new semantics
are never selected merely from env-var or file presence); the
owner-scoped guarded executor (the canonical profile's exact
INDEPENDENT UID:GID and fixed Python commands/flags/CID;
useful 1001/1002 positive; wrong UID OR GID, reserved
controller identity, root and out-of-range IDs refused);
subject tmpfs/home/workspace ownership; controller subject
accounting; stand-in measurements/PTY; host exact-CID
discovery/frame checks (exact registered-CID membership with
owned PID/birth lifetime frames — the original global
controller/subject UID teardown scans are never substituted
with the host owner's UID; unknown/unreadable still-existing
entries stay unverified); and the DISTINCT versioned AB
records (identity-bearing owner state
`slaif-017ab-owner-state-v1` with the full original
order/head/run binding; the old 12-key v1 state form
byte-for-byte unchanged and rejecting identity-bearing
records; owner-run evidence
`slaif-017ab-owner-run-evidence-v1` with the frozen identity
substructure and the exact-CID-membership teardown marker;
the AB driver record; the subject measurement/profile
records on the DISTINCT tags
`slaif-fixture-exec-measurement-v2`/`slaif-fixture-profile-v2`
over the shared profile-independent structural core with its
unchanged closed meaning, the strict original identity-v1
wrappers keeping the fixed-21002 law; measured 1001-class
facts validated as-is, never normalized to 21002).  The exec-capability suite
grows to 52 tests (14 new): the canonical `017-ab` sealed
entry over hermetic synthetic repositories — the coupled
public-owner terminal positive (prepare -> hold -> scoped
live-exe MEASURED with a synthetic bounded digest -> finish
-> the actual `_terminal` under the AB entry, the matching AB
record retained FIRST and only then the same-attempt pass
finalization, the frozen owner identity cross-checked against
the driver's adopted expectation); the full positive (retained
owner evidence then driver record then same-attempt
finalization); the separate scripted
unknown-executable-still-qualified positive (closed UNKNOWN
executable state, no digest, coherent measured frame); the
driver
startup refusals (drifted state binding, tampered state
identity, X-entry vs AB-state grammar, identity mismatch
with abort); the retention refusal and unverified-finalize
preservations; the closed-cohesion record law (an AB
`pass` requires adopted identity plus an actual capability
result — UNKNOWN executable remains valid; a pre-state
startup `fail` may honestly carry both unknowns; the old X/Y
grammar is never widened); the AB entry refused under
AA-active state before fixture work/admission; the in-process
sealed-CLI own-collection (real public main() on the test's
main thread, honest scope: not an actual subprocess — the
sealed child's OWN collection equals the production
derivation over the actual host identity triple; the bounded
abort converges the same attempt as the documented
`aborted`/exit-130); the startup-refusal convergence
(a forced control-socket bind failure or a pre-existing
foreign control root routes through the SAME single owner
convergence: the already-won attempt closes `fail`, the
retained AB fail evidence validates, the owned partial
control root is disposed, the foreign root preserved
byte/inode/mode, and the thin CLI keeps the same closed
startup record and exit code); and the second-admission
exhaustion refusal.  These compositions are useful FAKE proof
in three distinct honest layers (coupled public-owner
terminal, scripted driver bootstrap, in-process sealed-CLI)
— NOT one sealed-real-owner end-to-end test, and the
`017-ab` entry is INACTIVE, so no actual AB fixture
operation may ever run in AA.  The original S/X/Y entries,
sealed pairs, defaults and consumed namespaces are unchanged
(ci 224, local 50, native_prep 124, standin 102, identity 48
retain their recorded checkpoints).  No actual Docker
operation, no native launch (including help/version), no
worker stop, no TTY/job manipulation, no real fixture
admission in the real checkout, no host signal; D09 remains
NOT RUN; no v1 runtime claim.

Round 017-ab activates the canonical sealed entry fixed
by 017-aa and executes the ONE bounded actual
PYTHON-only owner-UID capability qualification on the
same PR25 with no source change (at the literal attempt
head `cdb6a101ecbd6d687f8ad413b9505c7198000758`, run
`87ee9c006d7f4de98d11af2dfbe5bd5c`, all 17 helper bytes,
the runtime source, the 199-input map and both artifacts
verified identical to qualified AA, and all 10 CI checks
green at that head): the existing public driver ran
EXACTLY ONCE, Python-only, over the real local Docker
endpoint, under a fresh private root with precreated
0600 stdout/stderr/exit files. The outcome is a closed
driver PASS: the sealed child won the ONE admission; the
real owner collected and froze its OWN eligible host
identity (subject UID/GID 1001/1001, expected groups
exactly the primary GID `[1001]` — measured values,
never a caller flag); the preparation, confinement and
Python-PTY phases completed under unchanged confinement
(controller 21001/21001; 1 GiB/no swap; 1 CPU; pids 96;
empirical keyring denial EPERM under the matching host
UID); the ONE capability-hold subject was uniquely
identified from the exact-CID inventory (pid/birth-
bound, closed argv; pre/post inventory 1/2 rows) and its
current executable was MEASURED through the existing
unprivileged scoped CID channel (sha256
`4dbf3143240288fb2170257ffaa7bd030cdda5d2703d1f5f30b627042267e2e3`
— the first measured executable for this entry class,
distinct from the X null and the Y unknown); the subject
was then observed `verified-gone` after the bounded hold
(absence only — never an exit code, signal, errno,
kernel cause or natural-exit provenance); the exact-CID
cleanup converged (descendants 1 before / 0 after;
container and owned image verified absent; the unrelated
same-UID worker and host sentinel survived); and the
publication ordering held (verified owner evidence
first, driver record second, same-attempt terminal
finalization last — ONE terminal-pass journal entry;
owner exit 0; driver exit 0; the pinned native artifact
was fetched, hashed and baked but NEVER executed). This
is a bounded Python-only diagnostic capability
qualification on the owner-UID profile — NOT
native-ready, NOT whole-017 acceptance, NOT v1 runtime
delivery; full-017 native/current-binary/right-pane
format/PTY, D09, the required-syntax audit and ALL
018-024 remain mandatory. The admission is terminal pass
and is never reset, retried or relabeled; the measured
outcome is recorded in the immutable round report. D09
remains NOT RUN; no v1 runtime claim.

Round 017-ac integrates the existing owner-UID fixture
composition with the native handoff path (software-only;
the future `017-ad` entry stays INERT, input-gated and
UNQUALIFIED — no actual local Docker/fixture/owner
startup or admission, no native launch (including
help/version), no worker stop, no real host signal, no
model/Gateway call, no new framework; no adapter/runtime
behavior change).  The NEW suite
`tests/test_cache_native_fixture_native_handoff.py` (22
tests, three named layers) tests the ACTUAL public
composition (`NativeOwnerRun` over the REAL
`LocalFixtureOwner` and the REAL public staged
`NativeHandoffWorkflow`) with injected FAKE platform
operations only (fake git, fake docker, fake process
table, faithful narrow identity-reader seam, owned
synthetic repositories).  The COUPLED
public-lifecycle layer (13 tests) drives that REAL
public composition over ONE coherent coupled fake
process world (bash 40, worker 50 with an unrelated
SAME-UID frame, native subject 60 held out): the
useful 1001:1002 public-lifecycle positive
(constructor/admission/prepare/observe/stop/register/
observe/finish/restore/publish; the distinct
identity-bearing AD record tags at every retained layer
— state, prep snapshot, owner evidence, native-owner
evidence, native-run terminal — with the SAME frozen
identity cross-bound through all of them, compared,
never rebased; the unrelated same-UID worker survives
with the SAME uid/gid/birth; the exact-CID teardown
proof; ONE terminal-pass journal entry), and the
meaningful contrasts: alive-at-finish quiesce refusal
(fail evidence keeps the FROZEN identity); unreadable-
frame and leftover-frame lifetime refusals; the
default-channel factory bound to THIS owner's registered
CID + the SAME absolute owner END (the cleanup grace is
convergence, never fresh measurement) with the
expired-anchor patience refusal before any factory call;
foreign registration (foreign CID, matching-foreign
binary) commits nothing and a later matching
registration in the same still-valid phase works;
post-admission identity drift refused at the identity-
bound use (same attempt terminal fail, frozen identity
in the fail evidence); post-PREPARE registration drift
refused at the public staged registration (the frozen
context revalidated at that identity-bound use site — no
channel construction, no receipt commit, no rebase;
same attempt aborted); the finalize consumer contrasts
(a retained AD native-owner record with a VALID FOREIGN
frozen identity can never become ready —
`prep-owner-identity-mismatch`; a relabeled ORIGINAL-tag
record cannot represent the AD-bound workflow — the
EXACT tag-pair law refuses the original-tag + AD-order
record at the closed record grammar before any
composition, while the historical orders of the
original tag parse unchanged; the unmutated retained
record stays the ready
control); prepare-only honest not-ready (the DISTINCT
AD terminal record names what is missing); the one-
shot second-publication refusal and the pre-existing
foreign-destination refusal (foreign bytes preserved;
same attempt terminalized fail).  The named pure-data
layer (4 tests) covers the frozen subject-identity
construction law and the original-vs-frozen disjoint
laws (pure data), the AD channel closed fields
(exactly 335544320 bytes / 10.0 s / the exe END;
nan/inf/bool/str refused) and the retained-record
consumer grammar (a foreign-path record refused).  The
named admission/constructor layer (5 tests) covers
the three pre-admission refusals over owned synthetic
repositories (AD refused under AC-active before
admission; the canonical AD order path binding; a
foreign-path AD binding refused before admission) and
the two post-admission constructor identity failures
(uncollected identity; mismatched owner triple)
closing the SAME won attempt terminal fail.  EVERY
started
test owner is reaped in a per-test finally before
monkeypatch teardown (the bounded exact-owner abort is
issued only while still held; an already-converged
owner is simply joined, so a positive test finishes
normally and stays a pass; no framework, no host
cleanup); a global subject-UID scan is trapped and
never called (the controller-UID scan keeps its closed
historical semantics).  These compositions are useful
FAKE proof — never sealed-real-owner, native or host
readiness; the `017-ad` entry is INERT in this round.
The production changes touch only the existing
fixture/native integration seams: the public staged
registration revalidates the FROZEN owner context at
the identity-bound use site (the original profile no-op
unchanged); the workflow finalize enforces the AD
tag/identity coherence against the ORIGINAL frozen
workflow context; and the retained native-owner record
codec enforces the EXACT tag-pair law (the closed
refusal vocabulary gains `prep-owner-schema-mismatch`
and `prep-owner-identity-mismatch`).  The original
S/X/Y/AB suites retain their recorded checkpoints and
stayed green in the full fixture regression (ci 224,
local 50, native_prep 124, native_owner 19, standin
102, identity 48, exec_capability 52, owner_uid 40,
binding 45, controller 33, native_handoff 22 — 759
cases, frozen Python 3.12 / umask 022 child).  D09
remains NOT RUN; no v1 runtime claim.

Round 017-ad closed PARTIAL with the ordered actual
single-attempt native handoff qualification NOT RUN
(never PASS, never waived): the pre-admission
engineering gap was found during the required private
preparation, so NO local test/fixture operation
occurred in that round — no new tests, no suite
changes, no local fixture/native/client operation.
The fresh CI jobs at the implementation head ran the
existing fixture checks under their original scope.
The existing suites are untouched and retain their
recorded checkpoints; D09 remains NOT RUN.

Round 017-ae (software-only) proves the independent
native-attach PTY expectation producer over REAL
constructors / public lifecycle / production
validators with injected FAKE platform operations
only (fake git, fake docker, fake process table,
faithful narrow metadata seams, owned synthetic
repositories); NO actual local Docker/fixture/
admission/native/client/model operation occurred. The
two modified fixture suites collect 205 tests at the
current source
(`tests/test_cache_native_fixture_native_handoff.py` 53,
`tests/test_cache_native_fixture_native_prep.py` 152 collected):
the handoff suite adds the COUPLED fake-world AF
layer — the full public-lifecycle positive (start/
prepare/observe/stop/baseline/launch/derive → AF
default-factory registration bound to THIS owner's
exact registered CID and the SAME absolute owner END
→ explicit fake native exit → finish / restore /
publish / finalize / admission / evidence over the
distinct `slaif-017af-*` tags with the SAME frozen
identity cross-bound at every layer, the unrelated
same-UID worker surviving, the global subject-UID
scan trapped) and its contrasts (a foreign probe UID
consumes the failed phase with no baseline/receipt/
resample; drift/expiry/copy-failure retain the
failure before any commit; the exact AF-only guard —
the original default matcher tuple and every AB/AD
matcher refusing the exact new probe plus every
mutated argv, with the matching original-profile user
proving the operation itself is unavailable, not
merely the wrong user; the probe refusing foreign or
unprepared targets; the one-shot second-publication
and pre-existing-destination refusals) — and the at-
use boundary case, which drives the REAL
`owner.devpts_inventory` over a fresh owner per case
(valid complete capture; exec-failed; discarded-
prefix capture-invalid; over-cap; late-return END
expiry; identity drift with the reader called exactly
twice). The prep suite adds the pure-data layer (the
devpts-inventory / allocation / attach-binding
codecs: closed fields and bounds — 96 rows, 65536
bytes, canonical name grammar, finite Linux UID/GID
domains, measured devpts policy, duplicate-key and
deep-under-byte-cap nesting normalization — plus
replay/foreign/malformed refusals and the object-
binding round trip) and the exact `-I -S` startup-
isolation test (two bounded owned NON-Codex children
on the SAME base interpreter with separate fresh
owned base dirs and minimal fresh HOME/
PYTHONUSERBASE/PYTHONPATH environments: the un-
isolated control executes both synthetic startup
canaries into owned markers; the exact `-I -S` child
leaves every marker absent and the site/sitecustomize/
usercustomize modules unloaded; the devpts probe is
never executed and the host devpts never read). EVERY
started test owner is reaped in a per-test finally
before monkeypatch teardown (the bounded exact-owner
abort is issued only while still held; an already-
converged owner is simply joined, so a positive test
finishes normally and stays a pass; no framework, no
host cleanup). The full fixture regression over ALL
eleven fixture suites is 818 passed (frozen Python
3.12.15 / umask 022 test child; pre-commit
development capture — the prescribed locked B gate
is the final qualification); the original
S/X/Y/AB/AD suites retain their recorded
checkpoints unchanged. D09 remains NOT RUN; no
native-ready or v1 runtime claim; the `017-af` entry
is INERT in this round.

Round 017-af (the ONE actual attempt) adds NO tests
and changes NO source, helper, test, lock or
workflow file: the ordered actual diagnostic
qualification ran EXACTLY ONCE at literal attempt
head 622f9a7bb52980e9358d60d8220812f66f4b4c4e (run
30eab04899784690a3ac289b1686cb08; ONE reviewed
private non-Codex operator over ONE managed
foreground procedure, ONE admission) and is an
honest closed FAILURE at preparation, never pass -
the owner constructed/admitted ONCE, completed the
artifact/build/build-context/collision/preflight/
prepare-target/pull/sentinels phases, then the
actual preparation/observation failed
`prep-stat-malformed` BEFORE the stop permission
emission (stage stream `s0-preflight` then
`closed-failure` only: NO stop, NO baseline, NO
attach, NO native launch, NO diagnostic; stop never
POSSIBLE). One exact-owner abort converged; journal
ONE entry `aborted`; owner evidence production-
validated (fail / cancelled / no cleanup failures);
exact owned container and image independently
verified absent (HTTP 404 on the verified default
local socket); work/control absent; the SAME worker
598258 stayed running/foreground throughout (no
signal/fg/monitor setter/restoration required or
performed). A current READ-ONLY parser diagnosis
(454 of 640 host stat rows refused - kernel rows
carry legal pgrp 0 / session 0 / tty 0 / tpgid -1
that the pure parser rejects) identifies a concrete
reproducible class, but the original exact failing
row was NOT captured and is never invented; the
operator's `prep-stat-malformed` and the owner's
`cancelled` stay distinct facts. No retry,
re-admission or in-round source repair under AF; a
later strategic continuation owns the software
repair and a separately sealed attempt (never
resetting AF). The existing suites retain their
recorded AE checkpoints unchanged (205 collected in
the two AE-modified fixture suites; 818 passed
pre-commit across all eleven fixture suites); the
prescribed locked B gate at the final delivery head
is the final source qualification. D09 remains NOT
RUN; no native-ready or v1 runtime claim; the
ordered native qualification is FAILED (never
pass): preparation FAILED, worker stop NOT RUN,
native NOT RUN.

Round 017-ag (software-only) proves the zero-group
observation repair and the sealed INERT 017-ah entry
over REAL production collectors and the REAL public
composition with injected FAKE platform operations
only; NO actual local Docker/fixture/admission/
native/client/model operation occurred. The named
layers and their ACTUAL current collected counts:
- the pure parser/authority layer (11 new cases
  in total: 7 in
  `tests/test_cache_native_fixture_native_prep.py`
  (now 159 collected) + 2 member-lifetime in
  `tests/test_cache_native_fixture_owner_uid.py`
  (now 42 collected) + 2 in
  `tests/test_cache_native_fixture_exec_capability.py`
  (now 54 collected)): a well-formed
  zero pgrp/session stat row is observation data
  (negative/overflow/truncated forms still refuse);
  the production running-group and stable-stop
  collectors accept the unrelated well-formed zero
  row alongside unchanged positive controls (the
  stop receipt requires positive W/B pgrp AND
  session — the zeroed-Bash-session case included);
  restoration never earns a restored verdict from a
  zero frame; the scoped subject and post-
  executable frames refuse zero group/session; the
  CID-scoped birth and member-lifetime readers stay
  unknown on zero frames; the discovery inventory
  retains a zero row as data and never adopts it;
- the COUPLED public-owner layer (2 of the 6 new
  tests in
  `tests/test_cache_native_fixture_native_handoff.py`,
  now 59 collected): the ORDER-REQUIRED full
  public NativeOwnerRun lifecycle for the AH
  entry over ONE coherent coupled fake process
  world carrying an unrelated well-formed kernel
  zero-group row across prepare/observe/
  stop/register/finish/restore/retention —
  observed but never adopted (not a member, not a
  tool session, never mutated), the distinct
  `slaif-017ah-*` tags at every retained layer
  (state, prep snapshot, attach binding,
  native-owner facts through the REAL
  finalization dispatcher, native-run terminal,
  owner evidence through the REAL AH evidence
  validator), the SAME frozen identity
  cross-bound everywhere; and the useful
  zero-frame authority negative (zeroed Bash
  frame refused by the stop collector's own
  zero-group law; zeroed Worker frame refused by
  the baseline binding; no receipt committed;
  honest abort);
- the single-layer handoff tests (the other 4 new
  tests in the same suite): the closed-entry
  mapping/data preservation; the hermetic
  sealed-entry law (AG-active refusal before
  admission, canonical-path resolution under its
  own active, foreign-path refusal, the real AH
  order and production admission namespace ABSENT
  from this checkout); the devpts-probe guard
  contrast (the exact probe admitted by the AF
  AND AH owner guards only, refused by every
  AB/AD/default matcher and every mutated argv);
  and the cross-entry attach-binding/native-owner
  tag-pair refusals in both directions (AF tags
  AF-only, AH tags AH-only, even equal numeric
  identities). EVERY started test owner reaped in
  a per-test finally before monkeypatch teardown.
The ONE bounded READ-ONLY real-host check
(executed exactly once; the existing
`collect_worker_group(RealProcTable)` against
freshly measured SAME W/B/foreground) completed
with exit 0 in 0.117 s at 2026-10-28T20:11:51Z
against the literal final source (collector
sha256
e56d2ac28d44038958481c6b08912b6be9af9e9b55adaec01afa184bf52ea58f):
the SAME worker 598258 (birth 150182858) and
Bash 2014146 (birth 95656910) revalidated
parent/TTY/comm, the TTY foreground pgrp was
measured 598258 (equal to the worker pgrp;
same_tty true, same_job false as expected for a
foreground job in its own group), and the closed
complete inventory showed group 598258 with
exactly ONE member (the worker), ONE other
session group (the Bash group 2014146) and two
separately grouped tool sessions (the Bash
itself retained as unknown; the check's own two
tool processes as worker-descendants) — a parser
traversal of actual host rows only, never
stop/subject/attach/native readiness and never an
idle-boundary or handoff-ready proof. The
earlier host-wide name/argv candidate scan is
recorded separately as an actual preflight
occurrence, not this production check. The full
fixture regression over ALL eleven
fixture suites is 835 collected / 835 passed
(frozen Python 3.12.15 / nonroot umask 022 test
child; pre-commit development capture — the
prescribed locked B gate at the final delivery head
is the final qualification). Per-suite collected
counts at the current source: local 50, owner-uid
42, native-prep 159, native-owner 19, native-
handoff 59, exec-capability 54, ci 224, binding 45,
controller 33, standin 102, identity 48. The
original S/X/Y/AB/AD/AF suites retain their
recorded checkpoints unchanged. D09 remains NOT
RUN; no native-ready or v1 runtime claim; the
`017-ah` entry is INERT in this round.

Round 017-ah (the ONE actual attempt) adds NO tests and
changes NO source, helper, test, lock or workflow file:
the ordered actual owner-UID native PTY requalification
ran EXACTLY ONCE at literal attempt head
06806eeeebac76b38f9ab5d6bbcfd2940f8b66a8 (run
1bbeeabfb9434ebf965eaa7e1a624a49; ONE reviewed private
non-Codex operator over ONE managed foreground procedure,
ONE admission) and is a verified actual PASS at the
qualified diagnostic scope - the SAME worker 598258
stopped exactly once through the reviewed exact-group stop
(monitor mode measured ON before any setter, the required
attach-branch gate), the SAME Bash foreground-attached ONE
native in the exact owned prepared CID with the synthetic
environment carried in the explicit attach and the frozen
owner identity (1001:1001, groups exactly [1001]), the
native uniquely discovered from the exact-CID inventory
(pid 3836555, birth 184083134 above the launch floor
184080662, exact argv `codex --yolo --profile early-beta`)
and registered against the independently measured expected
PTY (devpts baseline zero slave rows, then ONE fresh owned
allocation 136:0 with node gid 5 per the measured devpts
policy gid 5 mode 400 - lawfully distinct from the frozen
process GID 1001 - proc tty_nr 34816, the new-encode of
136:0, never MKDEV), the current executable MEASURED
through the registered-CID channel and equal to the pinned
public 0.164.0 artifact (sha256
b93f6811d3f653f0fb83be4050d857fb9abbb111dfa2ce160563327daff7f306,
308139304 bytes), the diagnostic earning ONE visible final
assistant answer with no tool call then a normal /exit,
quiesce closed-pass (residual 0), the 3273-byte export
(exporter uid 21001) revalidated before teardown, and the
exact-CID/image teardown converged (descendants 1 to 0;
container/image 404 absent-verified; the unrelated
same-UID sentinel survived). The counts are separate
ledgers, never conflated: controller wire_requests 2 at
finish (0/unobserved at prepare) - the second POST's cause
is unmeasured (no retained body/status trace; no forensics
or rerun authorized) - controller snapshot requests 4
(including quiesce/export), host ledger 2 API requests;
issued_calls empty. The SAME stopped worker was restored
in the SAME Bash (jobs-l bound J=1; `fg %1`; foreground
re-measured 598258; monitor restored to its measured ON
state); the physical restoration bool alone does NOT prove
a functional TUI - after `fg` the TUI remained
canonical/echo and root restored raw/noecho on the exact
verified /dev/pts/18 (TCSANOW, no inputflush; no
signal/restart/profile/service change) before input
resumed; the original fixed-21002 validator refusal
(corrected to the explicit validate_ah_owner_run_evidence,
no record edit, no runtime retry) and the initial
phase-wait parse failure (facts re-measured from /proc and
root-verified) stand as recorded process qualifications.
The existing suites retain their recorded AG checkpoints
unchanged (218 collected in the two AG-current fixture
suites - native-prep 159 + native-handoff 59; 835
collected / 835 passed pre-attempt across all eleven
fixture suites at the historical AG source); the full
CI suite at the attempt head P measured 3426 passed /
28 skipped / 1 failed - the
single failure is the AG-round hermetic test
test_ag_ah_refused_under_ag_active_before_admission, whose
real-checkout AH order/admission absence assertions were
invalidated by AH activation itself (order committed at P;
local admission namespace consumed); no production defect
or native-readiness failure is proven, and AH forbids
source/test repair, skip or xfail this round, so the
prescribed locked B gate at the final delivery head is
required once (its actual outcome - the single failure
preserved - is recorded in the immutable round report; the
later software continuation owns the hermetic repair). NO
retry, re-admission or in-round source repair under AH; the
ordered attempt is terminal and never reset or relabeled.
This diagnostic earns measured startup/request schema only
- never actual file-read/tool/multichunk/D09 acquisition
or generic native compatibility. D09 remains NOT RUN; no
native-ready or v1 runtime claim; the `017-ah` entry's ONE
admission is terminal pass.Round 017-ai (software-only) repairs the
activated-checkout-dependent AG hermetic test
and lands the ONE explicit future native-
format entry `017-aj` through the EXISTING
fixture composition with its closed
deterministic format scenario; NO actual
local Docker/fixture/owner admission or
startup, NO native launch (including
help/version), NO worker stop, NO host signal,
NO model/Gateway call occurred. The AG-round
test `test_ag_ah_refused_under_ag_active_
before_admission` no longer asserts the AH
order/admission absence in the real checkout
(AH activation itself invalidated that
absence — the order file is committed and the
local admission namespace is consumed — which
was the sole P CI test failure, 3426 passed /
1 failed / 28 skipped); the SAME law is now
proven WHOLLY over owned hermetic synthetic
repositories (AG-active refusal before
admission, own-active canonical-path
acceptance, foreign-path refusal, pre-
admission no-journal/no-claim) plus an
activated-checkout-shaped synthetic control
proving the law holds for an activated
checkout without reading or mutating the real
spent namespace; no skip, xfail, public-active
bypass or weakened validation, and no
production code changed for the repair. The
`017-aj` entry (unique path `oap/orders/
017-aj-native-process-format-qualification.
md`) is fixed in the closed production map
but INERT under AI-active (the real AJ
order/namespace/admission/owner absent,
hermetically proven including the production
admission path `.oap-local/<order>`; refused
before admission under AI-active; resolvable
only under its own active at its own unique
canonical committed order path). The AJ
entry's OWN verified frozen binding selects
the CLOSED native-format scenario BEFORE
startup (the exact create argv carries the
owner's own frozen-entry scenario; ambient
SLAIF_FIXTURE_SCENARIO, HTTP flags and user-
authored ready records can never select or
redefine it — the selected closed expectation
travels to the owned standin through the
EXISTING reviewed configuration transport as
transport data while the host revalidates the
record against its OWN verified entry, and
default/historical consumers stay strict).
The closed deterministic workload is code-
defined before any actual qualification: at
most 8 bounded synthetic seed files / 128 KiB
total whose identity is retained from PRE-
LAUNCH originals (bounded owned seed root
sealed after the bounded writes — no pre-
existing-file adoption or overwrite), exposed
through the smallest existing fixture seam; at
most 16 issued semantic calls (4 exec cases
plus at most 12 empty-stdin write_stdin polls
across the ONE running process, never
concurrent outstanding execs); any forced
sleep at most 5 s; at most 20 model POSTs / 1
MiB per inbound body / 256 KiB TOTAL
SERIALIZED selected record (including the
outer binding/identity/CID/tag, byte-checked
before decode/copy at export, consumer and
publication). The four serial cases: the
complete exit-0 literal file read; the
genuine initial-running exec plus causally
associated empty-stdin polls through actual
completion with output delivered in MULTIPLE
chunks (at least two NONEMPTY observed output
pieces across verified exec/poll results —
empty poll frames are accurate metadata and
cannot inflate the proof); the successful
empty output (the native EMPTY output
requires the delimiter LF); and the deliberate
bounded truncation with actual formatter
evidence (always non-acquiring). The REAL
pinned native text wrapper is strictly parsed
and verified from the pinned primary-source
grammar (the pinned `function_tool_response`
text wrapper; the actual formatter
truncation is warning/line-count plus a UTF-8
head/tail marker over the effective-token
budget, never an assumed fixed byte prefix;
chunk grouping is accepted only as ACTUALLY
observed in the verified exec/poll results,
never declared transport boundaries; native
completion may omit the process ID). The
exact issued family/name/call-ID/argument
digest and numeric causal request position
are retained before accepting a result (a
result attaches only strictly AFTER its own
issuance — it may equal the next call's
issuance — same-ID changed-arguments/results,
unissued/preloaded/duplicate/conflicting
results and foreign process/session facts are
closed refusals; issued call IDs stay unique
across the complete <=16 registry; previously
completed historical results reappearing in
later accumulated requests validate as frozen
historical identity and never advance or
retain twice). Selected frames only: exact
known synthetic call/result text after strict
formatter/source/byte verification against
the immutable seeds, preserving actual IDs/
association, complete wrapper ordering,
chunk/process fields and Unicode/CRLF/empty/
truncation facts; no reconstruction from
digests, no raw unknown output, no source/
private-history/full-request/headers/auth/
prompt/schema blob persistence; unknown text
is a fixed safe metadata/digest or typed
refusal. The complete four-case snapshot
validator keeps its earned law, and a
DISTINCT closed PARTIAL snapshot form (the
zero-POST source-less form and the completed-
prefix-plus-one-outstanding form) retains
only verified frames, re-derives pending
byte/session facts from them and never mints
a format qualification. Publication keeps the
ordered separation: the FIRST protected owner
evidence requires the SAME owner's OWN
successful protected retention (a narrow RAM
retention receipt set only after the
protected owner writer returned verified
success, independent of the cleanup/evidence
status — a post-commit unverified result
never sets it, a precomputed digest or merely
existing matching file is not a receipt, an
honest failed owner whose FIRST evidence WAS
retained keeps its representable publication,
and a failed/unverified retention refuses
BEFORE any AJ native/capture destination);
the SECOND protected selected native capture
record is built only from this owner's
retained selected export (validated at the
producer boundary with the shared selected-
export validator before decode/copy under the
existing raw-export byte cap); the SAME
pending-pass journal is finalized LAST with
the actual journal read, one-shot/no
overwrite/no fresh-path retry. The AJ
QUALIFICATION journal gate keeps the facts
separate: terminal PASS additionally
requires the ACTUAL cleanup pass, the native-
ready verdict, the strict full four-case
format qualification and the protected
retention; a cleanup-pass / native-ready
owner with an unsupported, partial or absent
format stays truthfully representable and
retainable with the owner's actual outcome
and the native verdict preserved unchanged,
but the journal closes terminal FAIL (never
pass) and the cached outcome/finalize_attempt
can never later upgrade it; a post-retention
unverified or raced finalization is a closed
failure preserving the retained bytes and
the actual journal facts as-is. The proof
layers over the REAL public composition
(`NativeOwnerRun` over the REAL
`LocalFixtureOwner` and REAL guarded channel
with injected FAKE platform operations only
— fake git, fake docker, fake process table,
faithful narrow identity-reader seam, owned
synthetic repositories) and one coherent
coupled fake process world: the pure
schema/state/selection layer (closed native
text-wrapper parser, per-chunk token
accounting, the delimiter/LF empty law,
observed chunk grouping, UTF-8 byte-index
truncation verification, strict typed poll-
argument identity, the causal position law,
issued-ID uniqueness, malformed/over-bound/
overlong-metadata typed refusals, the strict
TOTAL serialized selected-record bound at
export/consumer/publication, the complete
four-case and distinct partial snapshot
forms, and the closed consumer/exporter
dispatch); the actual receiver/ledger/
Exporter layer (the real provider route over
real sockets with the actual wire counters —
the thread-cap/connection-versus-route
counter separation, late-second-check expiry
refusals, refusal-state non-mutation, exact
typed poll-argument refusal and the bounded
export frame accounting — plus owned Unix-
socket exporter teardown with every client
socket closed and the provider torn down in
an outer finally, including injected
exporter teardown faults); and the COUPLED
public-lifecycle layer (the useful unequal
1001:1002 positive driving the REAL
constructor/admission/prepare/stop/baseline/
launch/derive/register/exit/finish/restore/
publish over the AJ entry with the distinct
identity-bearing record tags at every
retained layer and the SAME frozen identity
carried through all of them, plus the
contrasts: caller-channel and identity-drift
registration refusals committing nothing, END
crossed at use and during final-frame
hashing, the zero-POST safe-partial owner
finish, full and nonempty-partial finish
evidence, the owner-evidence retention
failures (pre-existing destination, post-
commit writer uncertainty) refusing capture
publication before any destination, the
honest failed-owner publication when the
FIRST evidence was retained, and the post-
native-retention unverified finalization
preserving the retained record and the
actual journal with the one-shot fresh-path
retry refused and no finalize upgrade).
EVERY started test owner is reaped in a per-
test finally before monkeypatch teardown; a
global subject-UID scan is trapped and never
called; the original S/X/Y/AB/AD/AF/AH suites
retain their recorded checkpoints. The named
fixture suites collect at the current source:
local 52, owner-uid 42, native-prep 165,
native-owner 19, native-handoff 84, exec-
capability 54, ci 235, binding 45, controller
33, standin 118, identity 48 and the new
`tests/test_cache_native_fixture_format_
capture.py` 176 — 1071 collected across all
twelve fixture suites, frozen Python 3.12 /
nonroot umask 022 test child (pre-commit
development capture — the prescribed locked
B gate at the final delivery head is the
final qualification); strict `uv run
--frozen mypy src tests` and ruff format/
check are clean at the current source. The
combined-suite module-instance coherence law:
the format-capture suite loads the controller
module FIRST and binds its actual
dependencies (the provider's model instance,
the producer's binding instance, the
exporter's model instance) to the canonical
loaded modules, and the seed fixture asserts
the bound configuration against the owned
tmp root BEFORE any seed filesystem I/O. NO
actual AJ fixture operation, native launch
(including help/version), worker stop, Docker
operation, model/Gateway call or host signal
this round; the bounded process deviations
are disclosed in the round report. D09
remains NOT RUN; no native-ready, whole-017
or v1 runtime claim; the later ACTUAL
qualification belongs to the separately
activated `017-aj` order, strategy-chosen.

Round 017-aj (the ONE actual attempt) adds NO
tests and changes NO source, helper, test,
lock or workflow file. Its evidence is the
actual bounded-fixture qualification
executed under ONE reviewed private
non-Codex operator, ONE managed foreground
procedure and the ONE terminal admission
(attempt head P; operator terminal exit 0;
facts in the immutable round records): the
SAME worker stopped once by exact-group
TSTP (monitor ON before any setter); the
pinned 0.164.0 native in the exact owned CID
against an independently measured expected
PTY (never MKDEV); frozen identity 1001:1001
groups [1001]; synthetic env attached
explicitly; current exe MEASURED via the
registered-CID channel as the pinned
artifact. The four serial cases
byte-verified against the immutable
pre-launch seed originals (complete 494 B
read; initial-running 1536 B output, CRLF
and non-ASCII, ONE poll, TWO non-empty
pieces; 0 B empty output; bounded
non-acquiring truncation). Measured: 5
issued calls, 1 poll, 7 model POSTs
(planned minimum 6; the ONE extra POST's
purpose UNMEASURED, no trace or forensics);
controller export ledger 9 requests / 7561
output bytes; host 2 API requests (2
admitted / 0 refused) plus 38 Docker
admissions; healthz 1; the physical 16
cumulative TCP-handler cap preserved, exact
admission count NOT retained. Quiesce
closed-pass (0/0); the 8252 B retained
FULL four-case capture revalidated BEFORE
teardown and qualified by the shared
strict full consumer (the only form that
qualifies); publication in the ordered
separation (owner's OWN retention receipt
FIRST, retained AJ record SECOND, ONE pass
journal entry LAST; one-shot, no
fresh-path retry, no cached-finalize
upgrade); ALL EIGHT separate facts
verified; exact-CID and image teardown
404-verified. The SAME Bash job restored
the worker foreground with the saved TTY
attributes (TCSANOW, no input flush,
readback equal) and functional input was
verified by the root with an actual
read-only tool probe. The ONE admission is
terminal (never reset, retried or
relabeled); the bounded process
deviations are disclosed in the immutable
round records. D09 remains NOT RUN; the
measured native_ready=true verdict is
bounded to this reference-fixture attempt
and recorded in those immutable records; no
generic native-ready, whole-017 or v1
runtime claim; 018-024 remain mandatory.

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

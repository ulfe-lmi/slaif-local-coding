# OAP Work Order — 017-z: inert fixture identity contract

## Objective and verified starting state

AMEND_EXISTING_PR, objective017, OPEN PR25
https://github.com/ulfe-lmi/slaif-local-coding/pull/25, branch
`oap/017-cache-read-observation`, base main
96c790423f6f0097a56a0b12bacda8a9b6da6aba. Starting Y SELF
cab238b2f225924bed6ebcfef833ba653e330799, sole implementation parent
ba297697b8389397d264a8197992f9c284c835bb; sourceA4
8adfe98b2939c5f39330fa6ac233def9036e033a. Report233lines12988B0600uid1001,
SHA256106a6c6fd674f00f4038aba52a0e9cfcbf3b74fcd2c198957f18e3ab8c23b39b.
Exact remote publication and ALL10 implementation plus ALL10 SELF checks
independently verified. Read reviews/017-y-decision.md before mutation.
NO new branch/PR, merge/auto-merge, next numeric objective or release.

Deliver one small SOFTWARE-ONLY, INERT contract increment: a versioned immutable
fixture identity description and bounded read-only host-owner-ID collection,
with meaningful pure/fake tests. It prepares a possible later separately ordered
fixture profile whose nonroot subject IDs match its unprivileged host owner.
It does NOT switch any fixture/runtime identity, integrate a new owner/driver
path, qualify containment/current-executable access or authorize an experiment.

Use the SAME healthy RIGHT early-beta/xhigh worker. Only a genuine crash permits
exact `codex --yolo --profile early-beta` restart in RIGHT. No other coding/test
Codex startup (including help/version), CI client, wrapper/exec/resume workaround
or delegated coding agent. Read mandatory governance, architecture, SECURITY,
TESTING, exact order, Y report/decision and applicable fixture contracts; reconcile
GitHub and current checkout. Routine setup/tests/build/CI/publication belong to
coding, not the human or strategic terminal operator.

## Measured gap, engineering choice and unchanged authority

Y ran ONE Python-only attempt at earlier B2
35a3bcd7322535dd4a699efc53c0c1c62d4c942e/runfbe526a3290d465298bc8da61ef2a304,
10:25:58–10:27:23Z85seconds. Preparation/confinement/PythonPTY completed;
the existing host CID channel measured the held UID/GID21002 process identity,
but CURRENT executable stayed UNKNOWN/no digest. JournalPASS is consumed.
No errno/kernel/X-cause, impossibility or native-readiness inference. Do not
repeat/reset/relabel Y or replace measured identity with an artifact digest.

The bounded engineering choice in this order is to make the identity contract
explicit BEFORE any alternative runtime integration. A later owner-UID profile
might permit the existing unprivileged host read without another measurement
process; this is unproven and needs actual same-UID containment/current-exe
qualification under a later exact order. Static source hardening functions do
not establish actual native behavior. The helper alternative remains inert;
no helper/channel/prctl/privileged workaround is selected here.

Keep the ORIGINAL fixed21002 fixture profile and every old record/schema,
constant/default/consumer meaning intact. This is fixture-test identity, NOT a
new product cache profile, authenticated principal, route identity or model
context setting. It must not affect adapter runtime, legacy constitution/image
policy, API/Gateway, compiler/cache or any existing Codex/Qwen configuration.

## Exact code boundary and contract

Add one stdlib-only typed module, suggested
`scripts/cache_native_fixture_identity.py`, and its directly relevant focused
tests, suggested `tests/test_cache_native_fixture_identity.py`. Minimal packaging
allowlist/development-provenance additions for the new helper/test are allowed;
frozen published RC records are immutable. Update matching docs. No dependency/
lockfile/workflow, product src/app, existing fixture Dockerfile/controller/
stand-in/exporter/local-owner/driver/preparation/binding behavior change.
Existing model constants/validators/fixtures remain unchanged; importing their
read-only constants is fine, changing them or widening old schemas is not.

1. Define two explicitly named, immutable identity descriptions: the original
   fixed controller21001/subject21002 profile, and an INERT versioned owner-UID
   candidate. Choose clear names distinct from adapter cache profiles. The
   controller stays UID/GID21001. Owner-profile subject UID/GID must equal the
   captured eligible host owner's real/effective/saved UID/GID values, all three
   values of each kind equal, nonroot, finite strict integers and distinct from
   controller identity. Reject booleans/numeric strings/negative/overflow/root/
   controller IDs and inconsistent set-ID observations with fixed non-echoing
   errors. Do not infer missing IDs from another field. Bound Linux numeric IDs
   to 1..4294967294 inclusive; do not admit 0, -1 or u32max4294967295.
2. Expected subject groups are exactly its primary GID, never copied from host
   supplementary groups. Keep original21002 group law unchanged. Descriptions
   own immutable tuples/data, not mutable aliased lists/dictionaries. No arbitrary
   caller-selected UID/argv, root fallback, environment override or silent default
   from an unknown profile name. Equivalent numeric IDs under different profile
   versions remain different configurations; old and new meanings never collide.
   These are new inert description records, never a migration/rewrite or
   reinterpretation of any old actual-evidence record.
3. Provide the smallest strict closed data-record representation/validation and
   deterministic canonical configuration fingerprint needed by later integration.
   Exact profile/version/field/type/group laws; missing/unknown/contradictory
   fields refused without echo. A bounded mapping codec is sufficient; do not
   invent redundant JSON/transport machinery. If bytes are accepted, bound them
   and reject malformed/duplicate/over-bound input. Fingerprints bind complete
   profile semantics and change on a real identity/configuration change, not on
   a global request counter or unrelated state. Do not call this a process hash,
   trusted identity receipt, admission, cache key or readiness certificate.
4. The host-ID collector is READ-ONLY and bounded: use direct stdlib OS identity
   getters, once per collection, with an explicit unsupported/unavailable outcome
   if complete real/effective/saved IDs cannot be obtained. No filesystem/proc
   traversal, environment/config/profile read, network/GitHub/Docker/subprocess,
   signal, UID/GID/group/privilege/prctl/kernel mutation or credential handling.
   Keep raw collection/data validation/derivation separate enough to test through
   a narrow fake OS-read seam; do not bypass a production validator or constructor
   to make a positive pass. Do not start a process merely to collect host IDs.
5. Typed objects, decoded JSON/data, a profile name, a fingerprint or caller flags
   NEVER establish measured authority. This increment selects NO live profile,
   records NO fixture admission and can yield NO ready/native verdict. The later
   sealed child must select a canonical profile, collect/freeze actual owner IDs,
   bind them to its ORIGINAL verified order/head/run and live admission before
   external work, then revalidate the same context at actual use. Describe that
   required future integration boundary honestly; do not implement it here or
   smuggle a new path through the existing local CLI/defaults/validators.

## Observable acceptance and tests

Meaningful useful positives plus closed negatives:

- original21002 exact description/record round-trip/fingerprint, original constant
  and old-record meanings unchanged;
- owner-profile derivation from one faithful eligible nonroot OS observation;
  actual safe current-host UID read may be exercised separately as OS-data-only
  evidence, never containment or executable capability;
- mismatched real/effective/saved IDs, getter failure/missing support, root,
  controller collision, malformed/boolean/string/out-of-range IDs, missing and
  extra fields, unknown profile/version and invalid group vectors rejected;
- supplementary host groups never inherited, caller mutations cannot alter an
  existing description/fingerprint, original/new profile pairing isolated even
  for equal numeric tuples, deterministic stable fingerprints with meaningful
  changes distinguished;
- pure decoded/caller-authored data cannot yield ready/admission/native authority;
  importing/using this module performs no external operation or existing fixture
  state change. Test the actual public contract, not flags mirroring internals.

Preserve earlier probe assertions/useful positives and every old real attempt.
No test invokes Docker, namespaces, a native binary, model/Gateway or live fixture.
No `.oap-local/017-z` admission or actual fixture work/control root may be created.

Run focused new and relevant original fixture suites, then TESTING's complete
frozen Python3.12 gate with process-local022 test context and protected outputs.
Build BEFORE artifact inspect/install-smoke. Source-A then manifest-onlyB, clean
literal head; actual clean-archive reproduction/input-map/bothartifacts, fresh
installed27 with identity separate and actual30modulebyte identity, unchanged
frozen21 and relevant private controls, all10 implementation CI. Report actual
new counts/identities rather than copying Y's197input counts or timings. A new
helper must be honestly included in source/artifact policy where applicable;
no published RC rewrite. Source snapshots/fake tests are not actual runtime proof.

## Documentation, preservation and safety

Update both architecture maps/THREE compact copies, fixture contract, TESTING and
stage ledger. The copies are root ARCHITECTURE-for-agents.md, its
oap/strategic-instructions counterpart, and the ACTUAL external
/home/janezp/codex-supervision/slaif-local-coding/ARCHITECTURE-for-agents.md. State the contract is INERT, fixed21002 remains current, owner-UID
candidate not integrated/qualified, no native/D09/v1 runtime delivery. A later
profile must preserve private PID/mount/IPC/UTS/network namespaces, no host
mounts/devices, rootfs-readonly, cap-dropALL/no-new-privileges/seccomp, exact bounded
storage/memory/swap/pids/CPU, controller-private paths and EMPIRICAL keyring denial
under the matching host UID; matching UID is not proof of safe containment.
Native artifact308139304bytes also needs a later justified native-size byte/time
measurement bound, not blind reuse of X/Y's Python16MiB/10s. No implementation or
experiment of those later mechanisms in this increment.

Preserve all S/X/Y actual records/admissions/bytes/modes/inodes, old orders/reports,
W/U history and unrelated work. Baselines:
reviews/017-y-final-preservation-ba297697.json,
017-y-actual-first-result-35a3bcd.json,
017-y-external-temp-current-baseline.json and Y final53entry metadata audit.
Do not repair/clean/reuse old roots. Compiler/cache/image/API/Gateway/src untouched.
No qwen-serving/vLLM18020, model/patch/systemd/keys/profile/auth/firewall/VPN/network/
daemon/group/proc/kernel/privilege/sudo mutation, model call, native/startup/worker
stop, TTY/job/auxiliary handoff or host worker/unrelated signal.

In NEW Z report append the bounded Y publication-method qualification from
reviews/017-y-decision.md, never edit Y: canonical-path draft existed and was
corrected before SELF; a private draft copy retained; root has NOT established
atomic final filesystem creation from retained evidence. Clarify actually
executed method honestly, no guessed commands, retroactive atomic claim or
post-SELF change. Y protected bytes/remote report-only publication are verified.
The first unpublished audit's future timestamp was corrected before SELF to
actual11:02:20Z; root first snapshot preserved. Do not conflate these with source
or actual-capability failures, and do not recreate missing stderr or rerun only
for timing. Standard synthetic setup outputs may be retained safely; actual
fixture/native/API content remains forbidden.

## Fresh metadata and exact OAP publication

Fresh `/home/janezp/oap-017z-work`0700. All manual drivers/logs/drafts/evidence0600
FROM CREATION; protected directories0700. Use077 for private helpers (Python -B
avoids accidental shared-mode __pycache__); precreate BOTH actualstdout/stderr600
BEFORE any022 subprocess. Bash-invoke shell scripts, no chmod+x. No manual/tmp
metadata, nohup or unmanaged poller; retain first failures/deviations honestly.
Tool trees need exact named exclusions/identities, not broad matching prefixes.

Finalize report under private Z root FIRST. Finish concise accurate PR metadata
before SELF. Atomically create the previously ABSENT canonical report0600 using
same-directory temp/fsync/no-overwrite; no canonical-path draft edited in place.
Audit LAST after all final manual metadata exists, include itself and exact owned
temporary paths, actual measured UTC timestamp (never future/forecast), honest
self-size/hash convention. One immutable matching report with scoped status,
explicit GitHub/base/branch/starting/head/NO newPR/NO merge, literal40hex
Implementation head SHA and Report publication commit: SELF; final commit ONLY
report, sole parent implementation. Push and verify exact remote bytes/order/
active/head/parent/PR state IN MEMORY. No postSELF audit/PR/file/chmod/mutation or
push. ExactlyONE responseOK then SAME worker single managed control wait.

Actual FIFO paths /home/janezp/codex-supervision/slaif-local-coding/control.fifo
(inode10648021) and response.fifo (inode10648022),0600uid1001; never recreate or
substitute paths. Wire EXACTASCII OK(4f4b), no newline/ID/JSON. Strategic writes
active/order/control, coding reads control/active/order and writes report/response.
Active alone selects work. Y response45664 is TERMINAL/exactOK/exit0 consumedONCE,
NEVER poll/replay. Existing SAME worker598258 NEXT-control wait38817, actual
cat2173481 directly under598258; verify live. Strategy starts one fresh Z response
reader with actualREADY/handle/PID then sends ONE controlOK. Coding consumes ONLY
its existing38817, verifies literalOK/exit0 and exactZactive/order, no duplicate
read/control/newworker. Full017/native/D09/syntax and018–024 remain required.

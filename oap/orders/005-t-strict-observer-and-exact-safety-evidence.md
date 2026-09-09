# OAP Work Order — 005-t

## Objective

Amend Objective 005 PR #7 to correct the directly reproduced observer and
safety-evidence defects in 005-s. Preserve the existing direct Local transport
architecture. Prove strict event validation, framing/chunk invariance, exact
independent counting, fail-stop dispatch, bounded private evidence, and genuine
negative tests. Finish with the complete existing fake C1–C5/D matrix.

No protected credentials/inference or installed cutover in this round. No
Gateway, Qwen, product policy, network, active-profile, or version change.
Coding reports one immutable result; strategy alone accepts/merges/advances.

## Exact state

- Local repository `ulfe-lmi/slaif-local-coding`; `005-t`;
  `AMEND_EXISTING_PR`; **NO NEW PR**.
- PR https://github.com/ulfe-lmi/slaif-local-coding/pull/7
- Base/head `main` / `oap/005-gateway-ingress-integration`.
- Main `570bd2b24ad4b041a07e0320d5ed44bc73e99ad5`.
- Required start report head `0a659601ad5d871e007c15b45e029b1bbddf5d8c`.
- Literal implementation parent `39cf2e0e943cd2619ad88980ad16adf118c41d0d`.
- Report path `oap/reports/005-s-observed-transport-and-pretraffic-safety.md`.
- Report-only topology verified; report-head test SUCCESS, run 34385097925 /
  job 102579262118; PR OPEN, non-draft, mergeable; checkout clean.
- Gateway execute `50dcc3b85d614eb1d0c6196595bf22ef5779f846`; merged main
  `d142fd7f04c46fac3469b9b9bba1bd2068aabad8`; report
  `ad1c556a539130c08dc1063b3e9a25a0af2e5a85`; app tree
  `c0204deaff3cfd055a25f29a7f5d8d3c5e161d57`. Keep all pins unchanged and
  recheck required Gateway/Local checks before execution.

Before edits reconcile exact remote and checkout state. After activation only
this order and active selector are expected initial differences. Preserve every
prior order/report, including 005-q/r/s. Do not rerun those historical rounds.

## Protected baseline and resource limits

Vision Qwen remains PID 23961, start Sun 2026-09-06 18:57:26 CEST, zero
restarts, active on 18020, model qwen3.8-27b, context 100000, one sequence/image.
Text service inactive; candidate 18021/18030/18031 free; seven pre-existing
Qwen changes. Existing coding profile oap-coding-luna-xhigh is unchanged.

Only read-only PID/start/restart/unit/listener and unauthenticated health facts
are allowed. No protected credential/environment/raw-log/config reads, model
listing, compiler, inference, image or diagnostic calls. Never mutate port
18020, qwen-serving/checkpoints/patches/venv/units/launch/GPU flags, credentials,
firewall/VPN/network, or active profiles. No second model or new service topology.

Work only in existing repository-only harness/helper/test/docs paths, plus
order/active/report. No src/, Gateway, dependency/lockfile or binary changes.
Use actual Local app factory and direct HTTPX transport; no proxy/relay/status
endpoint. Existing fake loopback PostgreSQL 16/tmpfs/--rm and Docker operations
remain allowed. Keep current request/event/byte/time/concurrency budgets; no
increases to make tests pass. Cleanup exact task-owned resources only.

## A. Reproduce and correct observer validity

Independent strategic checks against 005-s proved:

1. _StreamState accepts mismatched event/payload type, mismatched response IDs,
   missing terminal output, invalid usage totals and arbitrary response.* events.
2. Arbitrary event strings are retained in event_type_classes. Request path
   and dynamic exception class names are also emitted without a finite mapping.
3. CRLF frames are not split correctly. A network chunk containing multiple
   legal small events can overflow the per-event cap before they are parsed;
   the same bytes split into chunks can pass.
4. observer_dispatch_matches_fake compares display buckets. Five dispatched/
   terminal requests and fifty provider requests both become 5+ and compare equal.
5. Malformed/overflow/failed streams do not mark the observer unready; a later
   request still dispatches. The current manual mark_unready test does not
   cover automatic failure propagation.

Reproduce each with focused regressions. Use the actual accepted Gateway
ResponsesStreamEventValidator and request-scoped validation profile from the
exact detached Gateway checkout, injected into repository-only observation.
Do not copy Gateway policy or build a new prefix-based validator. Profiles must
come from exact approved route/tool semantics, not caller spoofed headers or an
all-tools-enabled flag. Validate payload types, IDs, sequence/lifecycle, item/
content relationships, terminal output and usage; a declared event name alone
never proves validity. Keep framing checks separate from semantic checks.

Parsing must handle LF/CRLF, boundaries split at every byte, coalesced events,
and supported SSE comments/data framing without depending on chunk grouping.
Enforce frame and stream caps incrementally before unbounded allocation; clear
transient buffers on rejection/cancel/close. Unknown events/fields/types must
remain invalid and project only to a closed other/error class. No raw names,
paths, exception classes/messages, bodies, arguments, text, IDs or credentials
in retained evidence. Known endpoint paths become fixed enums; exceptions map
to an explicit finite enum.

Keep exact bounded internal integer counters for attempted, dispatched,
responded, terminally valid, compiler and inference operations. Compare exact
counts first, then bucket only display values. Terminal proof must remain
per ordinal, not interchangeable aggregate buckets. Test 5/50, 6/12, missing,
extra, duplicate, compiler/inference swaps and cross-lifetime ordinal collisions.

## B. Fail-stop and safety before dispatch

Automatically latch an observer failure when parsing/validation overflows,
fails, stream truncates, cancellation occurs, delegate raises, or closure is
abnormal. Prevent every later dispatch, including queued/concurrent admission
after the failure, and perform idempotent cleanup. Distinguish a normal expected
synthetic failure case from unexpected acceptance failure by the fixed manifest;
do not globally make failures acceptable. A new fixture lifetime must not reset
an aggregate failed acceptance run into success.

Check observer and fake-result prerequisites before credential hooks, app
readiness that reaches upstream, Codex launch, and every dispatch. Keep the
005-s unconditional protected prohibition for this no-live round. Tests must
show unavailable/stale/malformed evidence produces exactly zero credential-hook
calls and zero upstream dispatch; malformed stream or failed obligation produces
zero later dispatch while cleanup still executes.

Maintain streaming fidelity. With an actual bounded loopback server, require
first chunk delivered before the producer permits terminal output. Assert exact
request and response bytes/headers/status/order, backpressure, cancellation,
disconnect, timeout, truncation, observer exceptions and closure. A buffered
client.post followed by aiter_bytes does not establish first-byte streaming.

## C. Bounded evidence files and candidate reuse

Fix _validate_fake_gate to enforce the file cap before reading the entire file;
validate the opened descriptor is the expected regular owned file and use a
bounded read (cap plus one), with safe path/ownership checks. Reject duplicate
JSON keys/non-finite or wrong-type values and malformed nested result evidence.
Do not create a secret or authority token for this test artifact.

Fix _tested_source_still_valid so both exact-HEAD and permitted report-only
descendant paths require clean relevant tracked/untracked source state. Compare
the tested implementation and actual source/config identity; report-only bytes
may differ but modified helpers/config must invalidate. Preserve complete
ordered IDs/projections/observations/Gateway/Codex binding from 005-s.

Add independent parameterized negatives for every rejection claimed by the
report: singleton, removed/duplicate/reordered/extra IDs, false/absent
observations, wrong relationships, missing/false projections, changed candidate,
report-only descendant plus dirty source, stale Gateway/Codex/config, unsafe/
oversized/malformed file, retries, skipped or failed records. Match the report
to collected/executed tests; code branches without tests are not tested evidence.

## D. Full fake acceptance and publication

After focused tests pass, run actual Codex 0.149.0 (SHA-256
`bbc3341e44c9ead340ed9570c17be936e37870f570751a941699ffd04d672827`) through
exact Gateway, actual Local with the observer, and strict fake Qwen. Re-establish
all 37 selected C1–C5/D results, actual same-session full-image/resumed crop,
governance/compiler/cache/rehydration, signing/replay/tamper/isolation, ordinary
tool and HMAC call-ID lifecycle, per-request accounting, no bypass, privacy,
cleanup and fake rollback/refusal. Each PASS needs direct observations. Verify
observer and fake-server exact counters agree before safe output reduction.

Require no missing/failure/retry, actual tested implementation/source identity,
and all projections PASS. Do not weaken accepted fixtures, manufacture valid
terminal records, replace real Codex with manual history, or waive any row.
If blocked, state the first direct defect and all unrun rows; no protected retry.

Run full frozen pytest plus focused meaningful regressions, Ruff check/format,
mypy src tests, compileall, shell syntax, build/wheel boundary, diff/pin/privacy
scans and current required Local CI. Preserve unknown 005-r counts/state/budget
facts. Correct current docs to the actual tested observer guarantees. Do not
claim protected acceptance or require a relay/Qwen mutation as a prerequisite.

Coding owns routine tools, setup, tests, support edits, Git publication and
evidence. No human/strategy terminal labor. No raw customer/secret/model/tool/
source/image/identity material in logs, reports, metrics, caches or artifacts.
All fixture state private and task-owned; exact cleanup; preserve unrelated
.venv/Qwen state. Verify protected PID/start/restarts/listener unchanged and
candidate ports absent; count allowed read-only health probes separately.

Publish only on PR #7: push all implementation and exact order/active, record
literal implementation SHA, then atomically create exactly
`oap/reports/005-t-strict-observer-and-exact-safety-evidence.md` with
`Implementation head SHA: <literal>` and `Report publication commit: SELF`.
SELF must change only that report, parent equals literal implementation SHA,
and remote head/parent/path/report bytes must be verified before response FIFO
OK. Report exact regressions, collected test IDs/counts, full fake/projection
result, source identities, no-live facts, cleanup, CI and limits. IMPLEMENTED
and TESTED require actual scope proof; REAL-E2E ACCEPTED, CUTOVER ACCEPTED,
MERGED and RELEASE-READY remain no. Coding never merges or creates a PR.

# Result-free testing procedure — invalidated harness 001

## Publication restriction

This file documents how the harness was exercised. It deliberately omits all
qualification/task outcomes because the human owner declared the harness invalid
and instructed that its test results not be published.

No score, pass/fail by condition, subject terminal status, token count, wall
time, judge result, retry selection, preliminary result, or comparative claim is
present here. Exact private artifacts remain preserved outside this public repo.

## 1. Preparation sequence

The controller followed this sequence:

1. inventory VM CPU, RAM, filesystem, interface, route, Python, Git, Docker, and
   Codex versions;
2. validate the backend credential as a regular non-symlink mode-0600 file
   outside the repository without printing its value;
3. verify permitted read-only backend health, authenticated model listing, and
   numeric metrics over the host LAN route;
4. verify unauthenticated protected model access failed and that controller
   configuration did not target the measured endpoint;
5. build a separate frozen subject toolbox and record its immutable image ID;
6. pull the exact immutable product candidate and verify source/wheel/Gateway
   OCI labels;
7. parse every generated adapter configuration inside the actual product image
   with networking disabled;
8. execute correct and deliberately defective judge controls without model
   calls;
9. execute bounded text, function-tool, one-image, and two-image capability
   probes only after human authorization;
10. execute real Codex adapter-path diagnostics in disposable homes/workspaces;
11. prepare fresh, isolated per-condition workspaces and run serial workload
   blocks only after backend drain checks.

## 2. Harness design exercised

- One measured lane; maximum subject concurrency one.
- Four conditions: DIRECT, VISION, CACHE, BOTH.
- Randomized Williams orders in four-block cycles for position and first-order
  predecessor balance.
- Fresh subject workspace, Codex home, browser process, adapter, adapter cache,
  and unique session identity per run.
- DIRECT used the measured LAN endpoint; adapter arms used VM loopback with that
  same upstream.
- VISION/BOTH used `retain_newest` with maximum one image.
- CACHE/BOTH enabled compiler, static identity, observation, constitution,
  derived cache, and rehydration.
- No condition-specific hosted-tool filtering.
- Backend prefix/KV cache policy remained unchanged; no reset/restart occurred.
- Judges ran only after generation stopped and the backend drained.

## 3. Workloads exercised

### Web Minesweeper

Subjects were instructed to build the fixed browser application contract, use
Playwright, create screenshots, and use model-directed image viewing. The
model-free browser judge exercised deterministic game rules and captured judge
screenshots after generation. Human blinded visual scoring was a separate step.

### Terminal Minesweeper

Subjects were instructed to build a genuine Python curses UI. The model-free PTY
judge exercised movement, reveal, flags, loss, flood/win, restart, and quit
behavior against an independent oracle. This workload carried no image input.

### Long-context fact recovery

The controller used one session per condition, a fixed initial prompt, 12
synthetic audit-pressure phases, and a final query for 16 governance facts and
source paths. Native structural compaction, session identity, context use,
compiler/cache behavior, and final deterministic fact judging were intended
observations.

## 4. Evidence channels used

- Native Codex exec JSON wrapped with UTC and Unix-nanosecond timestamps.
- Private Codex state/rollout databases for typed compaction/image evidence.
- VM-side before/during/after Prometheus snapshots and counter deltas.
- Existing adapter metrics for content-free compiler/cache/rehydration state.
- Existing host recorder intended for all-GPU utilization, process attribution,
  power, clocks, temperature, host CPU/RAM, and numeric backend metrics.
- Independent browser, PTY, and fact judges.
- Separate client and backend token ledgers; they were never summed.

## 5. Pre-freeze corrections made during testing

Before any freeze, the controller corrected benchmark-only defects and added
regressions, including:

- conversion from the delivered four-lane scheduler/validator/dispatcher to a
  genuine one-lane serial design;
- strict schedule validation and approval parallelism one;
- sequential execution and stop-on-broken-measurement gates;
- invocation-UID/GID handling for judge-control output mounts;
- required Responses image `detail` and bounded image-response allowance;
- bounded private adapter log preservation;
- separation of historical delivery manifest from current pre-freeze tree
  identity.

Each substantive correction created or required a new pre-freeze identity; old
attempts were not rewritten.

## 6. Methodological defects found before cancellation

The harness was not frozen because unresolved defects remained:

1. fresh subject Codex homes received scalar context settings but no frozen
   `model_catalog_json` entry for the custom model, causing fallback metadata;
2. the long-context wall bound could stop the fixed sequence before its final
   query despite later human instruction not to stop for time/tokens;
3. client usage delta-versus-session-cumulative semantics were not calibrated;
4. native model-directed image-view evidence was not reliably extracted from
   private client state;
5. required host-recorder cadence, clock alignment, measured-lane exclusivity,
   and shared-host contamination evidence was incomplete;
6. a sanitized adapter error prevented recovery of the exact upstream rejection
   body needed for one long-context diagnosis.

These are methodological observations, not published task results.

## 7. Cancellation and disposition

Human authority declared the harness invalid and cancelled all tasks. The
controller then:

- interrupted the active qualification process;
- prevented the remaining prepared condition from starting;
- interrupted parallel reporting work before a branch or PR was created;
- removed benchmark-owned containers;
- verified backend running and waiting gauges were zero;
- created no freeze, stage approval, pilot, main, or extension.

All private attempts were preserved under their original identities. They are
not included in this public archive and must not be used as formal or
preliminary benchmark results.

Any successor requires a new harness/protocol identity, complete requalification,
an exact freeze, and a separate approval binding that freeze and schedule.

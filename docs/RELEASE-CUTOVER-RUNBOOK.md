# Final live-cutover and rollback runbook (prepare-only)

Order 009-a, workstream E. This runbook is **documentation only**: no step is
executed by this objective, and nothing in this repository authorizes
executing it. It exists so that, once Objective 009 is accepted and merged,
the remaining work toward production is the real protected cutover/release act
itself, under a separate human-authorized order.

## Authority classes

- `CODING-SAFE` — steps the coding agent may perform on its own within a
  disposable/loopback boundary (no protected mutation).
- `HUMAN-AUTHORIZED (protected/live/release)` — steps that mutate protected
  live state, the Gateway deployment, Codex profiles, network bindings, or
  release state. They require an explicit human-authorized OAP order and are
  never performed by the coding agent unilaterally.

## Preconditions (all must be true before step 1)

1. Objective 009 (this PR) is accepted and merged; CI is green at the merged
   head.
2. The deployed adapter artifact is the accepted release-candidate wheel with
   the SHA-256 recorded in
   `packaging/release_provenance_manifest.json`; the local artifact policy
   check passes on it.
3. `cutover_performed` is still `false` and `released` is still `false` in the
   manifest; this runbook has not been started before.
4. The protected upstream (vision service, port 18020) is running and its
   baseline (unit state, main PID, listener, health 200) is captured in step 1.
5. A separate human-authorized cutover order exists and names the exact
   artifact SHA, the Gateway route change, and the rollback window.

## Runbook

### Step 1 — Current live configuration capture
`HUMAN-AUTHORIZED (protected/live/release)`

Capture, into a mode-0600 backup file, the exact current state: protected
vision unit state and main PID; `127.0.0.1:18020` listener; `/health` status;
the active Codex profile/provider endpoint values (names only — credential
values are referenced by environment name and never recorded); Gateway route
configuration; and `127.0.0.1:18031` currently free. This is the rollback
baseline.

### Step 2 — Install the exact Local artifact
`HUMAN-AUTHORIZED (protected/live/release)`

Install the accepted release-candidate wheel into the repository venv on the
production host, exactly as in [DEPLOYMENT.md §9](DEPLOYMENT.md#9-upgrade-procedure-supported),
creating the timestamped backup directory (previous config + previous
artifact + inventory) first. Verify the installed entry point and module path
match the manifest facts.

### Step 3 — Start candidate privately on 18031
`HUMAN-AUTHORIZED (protected/live/release)`

Start the candidate user service (loopback `127.0.0.1:18031` only) with the
installed configuration and poll readiness with `packaging/readyz-wait.sh`.
The protected upstream on 18020 remains the active path for all clients at
this point; nothing is re-pointed yet.

### Step 4 — Verify the candidate
`CODING-SAFE` (against the loopback candidate only)

- `/healthz` 200, `/readyz` 200, private `/metrics` 200 on loopback.
- Representative requests through the candidate against the live upstream
  (bounded, synthetic prompts only, no raw content recorded): non-streaming
  Responses text; SSE text; ordinary function-tool call + continuation;
  one-image vision on the designated route.
- Confirm the candidate's upstream is the protected 18020 endpoint and that
  its traffic is the only path the candidate uses (no alternate upstream, no
  direct public vLLM).

### Step 5 — Configure/pin the Gateway route
`HUMAN-AUTHORIZED (protected/live/release)`

In the separate Gateway deployment, configure the Codex route to the adapter
candidate endpoint (`127.0.0.1:18031`) with the service credential and the
signed-identity contract as continuously tested by the Gateway contract CI
(`tests/fixtures/gateway/current_peer_authority.json` pin). No Gateway code
change is part of this objective; this is configuration of the separately
owned Gateway.

### Step 6 — Representative real Codex text/tool/vision smoke
`HUMAN-AUTHORIZED (protected/live/release)`

Run a bounded real-Codex session through the full production path
(Gateway → adapter → protected vLLM): ordinary text; an ordinary function
tool call and continuation; one vision request (full image, then a later crop
request exercising the route's `retain_newest` policy). Capture only sanitized
facts (statuses, counts, timings). Do not run unbounded or stress traffic.

### Step 7 — Verify no unintended direct-vLLM bypass
`CODING-SAFE` (read-only checks)

- No client profile or route reaches vLLM directly: the only route to 18020
  is the Gateway → adapter path; the active Codex profile points at the
  Gateway.
- The candidate's process/listener facts match the manifest (loopback 18031
  only, single process, no extra listeners).
- No new public binding, firewall/VPN change, or direct public vLLM route was
  introduced (read-only comparison against the step-1 capture).

### Step 8 — Rollback proof
`HUMAN-AUTHORIZED (protected/live/release)`

Prove the rollback path works **before** declaring success: re-point the
Gateway route back to the direct protected endpoint (the pre-cutover path),
run one representative smoke, then re-apply the adapter route and run one
smoke again. This is the only moment the old path is exercised after
cutover; after step 9 the old path is retired.

### Step 9 — Deliberate final switch
`HUMAN-AUTHORIZED (protected/live/release)`

Small and mechanical by construction: confirm the step-8 re-verification
passed, leave the Gateway pinned to the adapter route, record the final
service/port/route state, and mark the cutover performed in the next
human-authorized release record. The active coding/strategic turn must not be
cut off mid-turn: the switch window excludes the OAP agents' own provider
path.

## Rollback triggers (any one of these aborts and rolls back)

- candidate `/readyz` does not reach 200 within the bounded wait at any step;
- any step-4/step-6 smoke request fails or returns a sanitized 5xx;
- step 7 detects any direct-vLLM bypass or unexpected listener/binding;
- protected fixture drift: vision unit state, main PID, 18020 listener, or
  health differs from the step-1 baseline;
- raw-content leakage appears in any log, journal output, or report;
- any Gateway, profile, firewall/VPN, or network mutation that was not named
  in the human-authorized order.

Rollback action: re-point the Gateway route to the pre-cutover path (step-1
baseline), stop the candidate service, restore the previous artifact/config
from the step-2 backup directory per [DEPLOYMENT.md §10](DEPLOYMENT.md#10-rollback-procedure-supported),
verify readiness and one smoke on the restored path, and report the exact
sanitized failure class. No retry loops; one rollback, then report.

## What this objective did NOT do

No step above was executed. No protected service, Gateway deployment, Codex
profile, firewall/VPN/network state, systemd production unit, public binding,
or release state was mutated by Objective 009. The manifest records
`deployment-qualified (disposable environment only)`, `cutover not performed`,
and `not released`.

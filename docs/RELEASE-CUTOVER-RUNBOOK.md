# Final live-cutover and rollback runbook — explicit state-transition machine (prepare-only)

Order 010-a, workstream D. This runbook **supersedes the Objective-009
runbook content** in-repo (the Objective-009 record — its PR, report, and
manifest — remains immutable git history; the runbook is a prepare-only
planning document, not accepted release evidence). **No step is executed by
this objective**, and nothing in this repository authorizes executing any
step. It exists so that, once the pre-cutover correctness work is accepted,
the remaining work toward production is the real protected cutover/release
act itself, under a separate human-authorized order.

The state machine below is mechanically modeled and tested in
[`scripts/cutover_state_machine.py`](../scripts/cutover_state_machine.py)
(pure model: states, transitions, preconditions, snapshot, and complete
inverse), exercised by `tests/test_cutover_state_machine.py`. A transition
that violates a precondition is rejected; rollback from every pre-final
failure point restores the complete step-1 snapshot across **all three**
tracked states.

## Authority classes

- `CODING-SAFE` — steps the coding agent may perform on its own within a
  disposable/loopback boundary (no protected mutation).
- `HUMAN-AUTHORIZED (protected/live/release)` — steps that mutate protected
  live state, the Gateway deployment, Codex profiles, network bindings, or
  release state. They require an explicit human-authorized OAP order and are
  never performed by the coding agent unilaterally.

## Tracked states

Three independent tracked states exist. Each transition names the state(s)
it mutates; verification transitions mutate nothing.

### LOCAL state (Local host + Local adapter)

| Field | Class values |
| --- | --- |
| `local.artifact_sha256` | `previous` (step-1 value) \| `release_candidate` (the exact cutover-authority wheel SHA from the current release provenance manifest) |
| `local.config_label` | `previous` \| `gateway_integrated` |
| `local.binding_class` | `loopback_18031` (loopback bind, the only class legal without the full signed ingress contract) \| `lan_18031_signed` (LAN-visible bind, legal only under `service_bearer_signed_identity_v1` — D1 binding law, order 011-a) |
| `local.service_state` | `stopped` \| `ready` (ready = `/readyz` 200 on the candidate bind) |
| `local.listener` | `none` \| `loopback_18031` \| `lan_18031_signed` |

Plus the protected-fixture invariance facts captured at step 1 (vision unit
state, main PID, 18020 listener, `/health` status, active Codex profile
mtime) and re-checked after every transition; any drift is a rollback
trigger.

### GATEWAY state (separate Gateway deployment)

| Field | Class values |
| --- | --- |
| `gateway.route_backend` | `direct_upstream` (pre-cutover route target, captured at step 1) \| `adapter_loopback_18031` |
| `gateway.authority_sha` | the exact Gateway authority SHA/version pinned for the cutover (default-branch main at order time: `65666f5886832034c52211fdd7604046557e6ada`) |
| `gateway.signed_contract` | `true` — the Codex route carries `identity_mode = "signed_identity_v1"` with the pinned replay mode (continuously tested by the `gateway-contract` CI) |

The Gateway deployment requirement for the supported topology
(`docs/TOPOLOGY.md` §4): the Gateway `api` runtime must run in the **host
network namespace** (deployment-level configuration of the separately owned
Gateway — compose per-service host networking for the `api` runtime, or an
equivalent single-host shared-namespace runtime deployment). The route
backend URL is per-provider configuration (`ProviderConfig.base_url`) with
server-side secret env lookup; pointing it at `http://127.0.0.1:18031/v1`
is Gateway configuration, not Gateway source change. **Bridge-container
variant (order 011-a, TOPOLOGY.md §4):** when the Gateway `api` runtime
keeps the pinned deployment's bridge networking instead, the config-only
route backend is the **host bridge interface IP** at port `18031` (e.g.
`http://172.17.0.1:18031/v1`) — still Gateway configuration only, and
still legal only because the adapter bind then carries the full signed
ingress contract (D1).

### CODEX state (active client profile)

| Field | Class values |
| --- | --- |
| `codex.provider_class` | `pre_cutover_provider` (the exact step-1 provider/base URL, recorded by name and address class, credential values never recorded) \| `gateway_entry` |
| `codex.profile_backup` | run-level fact: the exact pre-cutover profile file backup exists (mode 0600) |

## Preconditions (all must be true before step 1)

1. The pre-cutover objectives (010 and 011) are accepted and merged; CI is
   green at the merged head.
2. The deployed adapter artifact is the current cutover-authority wheel with
   the SHA-256 recorded in `packaging/release_provenance_manifest.json`
   (the **Objective-011-a regenerated manifest** — schema v2,
   `objective: "011-a"` — is the cutover authority; for the Docker path the
   manifest's `oci` build inputs are part of the authority; the
   Objective-010-a and Objective-009 wheel hashes remain the accepted
   010/009 records only); the local artifact policy check passes on it.
3. `cutover_performed` is still `false` and `released` is still `false` in
   the manifest; this runbook has not been started before.
4. The protected upstream (vision service, port 18020) is running and its
   baseline (unit state, main PID, listener, health 200) is captured in step
   1.
5. A separate human-authorized cutover order exists and names the exact
   artifact SHA, the Gateway deployment/route change (including the
   host-network-namespace deployment requirement), the Codex profile change,
   and the rollback window.

## Transitions (runbook steps)

`S0` is the step-1 snapshot. Transitions apply strictly in order T1 → T9.
Each mutating transition lists its **inverse** used by rollback.

### T1 — Step 1 — Current live configuration capture
`HUMAN-AUTHORIZED (protected/live/release)`

Capture, into a mode-0600 backup directory, the complete `S0` snapshot:

- LOCAL: installed artifact/config identity (or `previous`), service state,
  `127.0.0.1:18031` currently free; protected vision unit state and main
  PID; `127.0.0.1:18020` listener; `/health` status.
- GATEWAY: exact route/provider backend (pre-cutover target), exact Gateway
  authority SHA/version, signed-contract route capability facts, and the
  Gateway `api` runtime network-namespace mode.
- CODEX: the active client profile file (byte-exact copy, mode 0600) and the
  exact pre-cutover provider/base URL values (names and address class only —
  credential values are referenced by environment name and never recorded),
  including the `maelstrom1 -> vLLM` mapping as an operator fact.
- Host user-manager linger state for the appliance user (baseline for the
  boot contract, `docs/DEPLOYMENT.md` §13).

Inverse: none (capture only). This is the rollback baseline.

### T2 — Step 2 — Install the exact Local artifact
`HUMAN-AUTHORIZED (protected/live/release)`

Install the cutover-authority wheel into the repository venv on the
production host, exactly as in [DEPLOYMENT.md §9](DEPLOYMENT.md#9-upgrade-procedure-supported),
creating the timestamped backup directory (previous config + previous
artifact + inventory) first. Replace the configuration with the
Gateway-integrated template (substituting only the documented placeholders,
`docs/DEPLOYMENT.md` §12) and extend the mode-0600 `adapter.env` with the
three distinct Local-side secret roles (upstream credential, Gateway service
credential, Gateway signing secret). Verify the installed entry point and
module path match the manifest facts.

Mutates LOCAL: `artifact_sha256 := release_candidate`, `config_label :=
gateway_integrated`. Inverse: restore previous artifact + config from the
step-2 backup (DEPLOYMENT.md §10).

### T3 — Step 3 — Start candidate privately on 18031
`HUMAN-AUTHORIZED (protected/live/release)`

Start the candidate (systemd user service on loopback `127.0.0.1:18031`,
or the Docker container per [DEPLOYMENT.md §15](DEPLOYMENT.md#15-docker-path-procedures-exact-link)
with the site `__LISTEN_HOST__`) with the installed configuration and poll
readiness with `packaging/readyz-wait.sh` (systemd) or the compose healthcheck
(Docker). Precondition: the candidate bind address is free (any pre-existing
listener is stopped and recorded first — no forgotten listener is left
behind). The protected upstream on 18020 remains the active path for all
clients at this point; nothing is re-pointed yet. The D1 binding law applies:
a non-loopback candidate bind is legal only under the full signed ingress
contract; the state machine rejects a `lan_18031_signed` candidate without
the signed contract.

Mutates LOCAL: `service_state := ready`, `listener := loopback_18031` (or
`lan_18031_signed`), `binding_class := loopback_18031` (or
`lan_18031_signed`, matching the candidate configuration's `listen_host`).
Inverse: stop the candidate; verify `listener := none` and
`binding_class := <step-1 binding class>` (absence proof on 18031; rollback
restores the step-1 binding class).

### T4 — Step 4 — Verify the candidate
`CODING-SAFE` (against the loopback candidate only)

- `/healthz` 200, `/readyz` 200 (signed ingress reports `ready`, which
  requires both Gateway ingress credentials present), private `/metrics` 200
  on loopback.
- Representative requests through the candidate against the live upstream
  (bounded, synthetic prompts only, no raw content recorded): non-streaming
  Responses text; SSE text; ordinary function-tool call + continuation;
  one-image vision on the designated route.
- Confirm the candidate's upstream is the protected 18020 endpoint and that
  its traffic is the only path the candidate uses (no alternate upstream, no
  direct public vLLM).

Mutates nothing (verification gate). Inverse: none.

### T5 — Step 5 — Configure/pin the Gateway route
`HUMAN-AUTHORIZED (protected/live/release)`

In the separate Gateway deployment: (a) ensure the Gateway `api` runtime
runs in the host network namespace (deployment-level configuration per
`docs/TOPOLOGY.md` §4); (b) configure the Codex route to the adapter
candidate endpoint (`127.0.0.1:18031/v1` — reachable from the Gateway
**runtime** namespace, not merely its host shell) with the service
credential and the signed-identity contract as continuously tested by the
Gateway contract CI (`tests/fixtures/gateway/current_peer_authority.json`
pin). No Gateway code change is part of this objective; this is
configuration of the separately owned Gateway.

Mutates GATEWAY: `route_backend := adapter_loopback_18031`. Inverse:
re-point the route to the `S0` `direct_upstream` target and verify.

### T6 — Step 6 — Switch the active Codex profile to the Gateway
`HUMAN-AUTHORIZED (protected/live/release)`

**This transition explicitly moves the active Codex profile onto the
Gateway path, before any full-path smoke is claimed.**

1. Back up the exact pre-cutover profile file byte-for-byte into the step-1
   backup directory (mode 0600) and record its SHA-256; verify the backup
   is byte-identical to the live file at backup time.
2. Write the cutover profile values: provider = the Gateway, base URL = the
   Gateway entry endpoint (the same endpoint the Gateway exposes for Codex
   clients), wire API `responses`. Credential values are never recorded;
   only names and address class are documented.
3. Verify the active profile now selects the Gateway (read-only re-read of
   the exact profile file).

Precondition: GATEWAY `route_backend = adapter_loopback_18031` (T5 applied).
Mutates CODEX: `provider_class := gateway_entry`; run-level fact
`codex.profile_backup := true`. Inverse: restore the byte-exact pre-cutover
profile file from the backup and verify byte-identity.

### T7 — Step 7 — Representative real Codex text/tool/vision smoke
`HUMAN-AUTHORIZED (protected/live/release)`

Precondition: T5 **and** T6 applied — the smoke is claimed only through the
full production path Codex → Gateway → Local → Qwen. Run a bounded
real-Codex session through that path: ordinary text; an ordinary function
tool call and continuation; one vision request (full image, then a later
crop request exercising the route's `retain_newest` policy). Capture only
sanitized facts (statuses, counts, timings). Do not run unbounded or stress
traffic.

**Verify no unintended direct-vLLM bypass** (read-only checks, part of this
transition's gate):

- No client profile or route reaches vLLM directly: the only route to 18020
  is the Gateway → adapter path; the active Codex profile points at the
  Gateway.
- The candidate's process/listener facts match the manifest (loopback 18031
  only, single process, no extra listeners).
- No new public binding, firewall/VPN change, or direct public vLLM route
  was introduced (read-only comparison against the step-1 capture).
- Protected-fixture invariance facts unchanged (unit state, main PID,
  18020 listener, health).

Mutates nothing (verification gate). Inverse: none.

### T8 — Step 8 — Rollback proof
`HUMAN-AUTHORIZED (protected/live/release)`

Precondition: T7 passed. Prove the rollback path works **before** declaring
success: apply the GATEWAY inverse (route → `direct_upstream`), run one
representative smoke on the pre-cutover path, re-apply T5 (route →
adapter), and run one smoke again. Net state effect: none (the two route
moves cancel); the proof record is retained. This is the only moment the old
path is exercised after cutover; after step 9 the old path is retired.

Inverse: none (net-zero by construction; if the re-apply fails, the failure
is handled by the rollback table below).

### T9 — Step 9 — Deliberate final switch
`HUMAN-AUTHORIZED (protected/live/release)`

Small and mechanical by construction: confirm the step-8 re-verification
passed, leave the Gateway pinned to the adapter route, record the final
service/port/route state, and mark the cutover performed in the next
human-authorized release record. The active coding/strategic turn must not
be cut off mid-turn: the switch window excludes the OAP agents' own
provider path.

Mutates run-level state: `cutover_performed := true`. **Terminal**: after
T9 there is no runbook rollback; a post-final failure is a separate
incident process decided by the human/strategic authority.

## Rollback — complete inverse from every pre-final-switch failure point

Rollback restores **ALL** changed state to the step-1 snapshot `S0` across
LOCAL + GATEWAY + CODEX — not merely one Gateway route. The mechanical
model applies the inverses of the applied transitions in **reverse order**;
the table is exhaustive over every failure point before the final switch:

| Failure point | Inverses applied (reverse order) | Restored to S0 |
| --- | --- | --- |
| during T2 | T2⁻¹ | LOCAL artifact+config |
| during T3 | T3⁻¹, T2⁻¹ | LOCAL service/listener + artifact+config |
| during T4 | T3⁻¹, T2⁻¹ | LOCAL service/listener + artifact+config |
| during T5 | T5⁻¹, T3⁻¹, T2⁻¹ | GATEWAY route + LOCAL |
| during T6 | T6⁻¹, T5⁻¹, T3⁻¹, T2⁻¹ | CODEX profile + GATEWAY route + LOCAL |
| during T7 | T6⁻¹, T5⁻¹, T3⁻¹, T2⁻¹ | CODEX profile + GATEWAY route + LOCAL |
| during T8 | T6⁻¹, T5⁻¹, T3⁻¹, T2⁻¹ (the model treats T8 as net-zero; a transient route re-point during T8 is itself an inverse that lands on the S0 value) | CODEX profile + GATEWAY route + LOCAL |

Properties enforced by the mechanical model (`tests/test_cutover_state_machine.py`):

- every inverse is defined for every pre-final mutating transition (no
  failure point is left without a rollback plan);
- after any rollback the state equals `S0` field-by-field in **all three**
  tracked states;
- rollback never leaves a forgotten listener (T3⁻¹ asserts `listener :=
  none` with an absence proof on 18031) and never leaves a tunnel/proxy
  (none is created by this runbook; the Gateway host-namespace deployment is
  configuration, not a new mechanism);
- T6⁻¹ (profile restore) is verified byte-identical to the backup;
- rollback triggers below abort and roll back; **one rollback, then report**
  — no retry loops.

## Rollback triggers (any one of these aborts and rolls back)

- candidate `/readyz` does not reach 200 within the bounded wait at any step;
- any step-4/step-7 smoke request fails or returns a sanitized 5xx;
- the direct-vLLM-bypass verification detects any bypass or unexpected
  listener/binding;
- protected fixture drift: vision unit state, main PID, 18020 listener, or
  health differs from the step-1 baseline;
- raw-content leakage appears in any log, journal output, or report;
- any Gateway, profile, firewall/VPN, or network mutation that was not named
  in the human-authorized order.

Rollback action: apply the inverse sequence from the table above, then
verify the restored state equals `S0` (byte-identical profile file,
`127.0.0.1:18031` free, previous artifact/config active, route at the
pre-cutover target), run readiness and one smoke on the restored path, and
report the exact sanitized failure class.

## What this objective did NOT do

No step above was executed. No protected service, Gateway deployment, Codex
profile, firewall/VPN/network state, systemd production unit, public
binding, or release state was mutated by Objective 010. The manifest
records `deployment-qualified (disposable environment only)`,
`cutover not performed`, and `not released`.

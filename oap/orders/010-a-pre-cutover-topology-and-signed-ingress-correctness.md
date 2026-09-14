# OAP WORK ORDER 010-a — PRE-CUTOVER TOPOLOGY AND SIGNED-INGRESS CORRECTNESS

Strategic work order 010-a, final. All live facts below were independently
verified by the strategic agent on 2026-09-14 (Europe/Ljubljana) via
authenticated gh, remote git, read-only host probes (incl. read-only
docker/systemd/ip inspection and safe DNS resolution), and repository
source inspection. No VERIFY/DRAFT markers remain.

## Objective

Close the pre-cutover correctness gap before any protected cutover, in one
coherent PR: establish the explicit intended RUNTIME topology (separating
hosts and network namespaces), choose the smallest secure Gateway→Local
transport that preserves the Local loopback-only law, add the actual
Gateway-integrated signed-ingress deployment configuration (no static
identity fallback), rewrite the cutover runbook as an explicit
state-transition machine with a complete inverse (rollback from every
pre-final-switch failure point), prove endpoint reachability from the right
network namespace with a negative test of the invalid cross-namespace
loopback assumption, make the systemd user-service boot contract explicit
and tested, and gate artifact identity (009's wheel remains the cutover
authority only if still byte-identical; otherwise a new release-candidate
artifact/manifest/hash is produced and becomes the only future cutover
authority). No live cutover, no protected mutation, no release.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`.
- Numeric objective: `010` (first unused; verified 2026-09-14: `oap/orders/` contains objectives 000..009 (through 009-a); 010 unused).
- Round: `010-a`; mode: `CREATE_NEW_PR`.
- Required base/default branch: `main` at 4fd4502deda23ef8815740f4db0c1e615a5a1936 (verified 2026-09-14 via `git rev-parse origin/main` after fetch).
- Verified remote state at order time: no open PRs (`gh pr list --state open` returned `[]`, verified 2026-09-14).
- Verified last merge: PR #11 (objective 009) merged 2026-09-14T00:59:47Z; merge commit 4fd4502deda23ef8815740f4db0c1e615a5a1936 = main; main CI run 34794438519 success (test + gateway-contract).
- Required branch: `oap/010-pre-cutover-correctness`.
- Create exactly one non-draft PR. Never merge; never enable auto-merge.
- Objective 009 / PR #11 remains accepted and immutable; do not reopen,
  rewrite, or edit its artifacts.

## Strategic context and independently verified current state

Strategic independently verified on 2026-09-14 (Europe/Ljubljana):

- Local `main` at 4fd4502deda23ef8815740f4db0c1e615a5a1936 (verified 2026-09-14 via `git rev-parse origin/main` after fetch); no open PRs; OAP orders/reports through
  009-a; `oap/active` = `009-a` (normal).
- Gateway peer and gateway repository main both at 65666f5886832034c52211fdd7604046557e6ada; verified 2026-09-14 as still the gateway repository's default-branch main (unchanged since 2026-09-13)
  (unchanged); local fixture pin unchanged; module contract
  local-coding-v1 v2 (replay_mode process_local_inclusive_horizon_fail_closed), codex-0.149-responses-v1 v4.
- Protected host (read-only): hinton1 (hostname verified): user unit qwen-serving-vision.service active (running) since Sun 2026-09-06 18:57:26 CEST, main PID 23961 (vllm, qwen3.8-27b), listener 0.0.0.0:18020, GET /health = 200; port 18021 absent; port 18031 absent; active coding profile ~/.codex/qwen-neumann.config.toml present, mode 0600, mtime 2026-09-13 11:59 (unchanged).
- no Gateway deployment exists on the Local host: no Gateway checkout under /synology/homes/janezp, no Gateway listener among all host listeners, docker present with only three stale exited containers (2 years old, no ports) and docker0 link-down (read-only sudo docker ps -a).
- single NIC enp1s0 10.8.132.75/24 (DHCP, RFC1918 private LAN, unencrypted — no VPN/tunnel software: no wireguard config, no tailscale/wg binaries); default via 10.8.132.1; no other service interfaces beyond docker0 (down).
- Active coding profile (read-only, credential values never recorded):
  profile qwen-neumann: model qwen3.8-27b, model_provider qwen-LSI-A100 (display name 'Qwen 3.8 27B on Neumann via Maelstrom1'), base_url http://maelstrom1.lmi.link:8001/v1 (plain HTTP, no TLS), wire_api responses; maelstrom1.lmi.link resolves to 10.8.132.72 (same /24); the maelstrom1:8001 -> vLLM mapping is an unresolved operator fact to be captured in the cutover step-1 baseline (credential values never recorded).
- Accepted Objective-009 release-candidate wheel (0.1.0): SHA-256
  e4759c00e37332998ed92dc5c01fe10be4b11b3a4b1df8c33edc64e176752ee1 (81462 bytes, 26 entries).

The four pre-cutover defects below were independently confirmed against
`main` at order time (files cited):

- P1 network-namespace/loopback contradiction:
  `docs/RELEASE-CUTOVER-RUNBOOK.md` step 5 configures the separate Gateway
  deployment to the endpoint `127.0.0.1:18031`, while Local production law
  enforces loopback at three layers: `ServerConfig.loopback_only`
  (`src/slaif_local_coding/config.py`, listen_host restricted to
  127.0.0.1/::1/localhost), `packaging/slaif-local-coding.service`
  (`IPAddressDeny=any`, loopback-only `IPAddressAllow`), and
  `config/adapter.deployment.template.toml` (127.0.0.1:18031). Loopback does
  not cross host or container network namespaces.
- P2 signed contract disabled in the supported template:
  `config/adapter.deployment.template.toml` sets `[gateway_ingress] mode =
  "disabled"` (all signed fields commented out), `[constitution] enabled =
  false`, route `constitution_enabled = false`, with only two documented
  placeholders — while the accepted Gateway integration requires the
  `service_bearer_signed_identity_v1` contract.
- P3 incomplete cutover/rollback state machine: the runbook captures the
  active Codex profile/provider endpoint in step 1 but contains no explicit
  transition that moves the active Codex profile onto the Gateway before the
  step-6 full-path smoke; rollback re-points only the Gateway route and does
  not restore all captured state.
- P4 unattended lifecycle ambiguous: `docs/DEPLOYMENT.md` documents
  `systemctl --user enable` as "start at login" with no user-manager linger
  contract.

Exact accepted contract identifiers (current source, verified):
`[gateway_ingress] mode` literals are `disabled | service_bearer_static_identity
| service_bearer_signed_identity_v1`; signed mode requires
`service_token_env` AND `signing_secret_env` (fixed defaults
`identity_version="v1"`, `policy_version="signed-identity-v1"`,
`clock_skew_seconds=60`, `replay_ttl_seconds=60`,
`max_replay_entries=4096`, `nonce_min_length=16`, `nonce_max_length=128`);
`[constitution] identity_source` literals are `static | signed_request`;
signed-request identity requires `enabled = true` and forbids static
principal/session/repository (config validators enforce); each route carries
`observation_enabled` / `constitution_enabled`. Gateway-side contract modules
(pinned peer): app/slaif_gateway/modules/servers/local_coding/contract.py, app/slaif_gateway/modules/clients/codex_0149.py, app/slaif_gateway/providers/streaming.py (pinned by the local gateway-contract gate, 18 strict network-guarded tests).

Gateway deployment contract at the pinned peer: docker-compose stack (postgres 16, redis 7, mailpit, api = gunicorn on 0.0.0.0:8000 published to host 8000, celery worker) plus nginx :80 entry (TLS/domain deployment-specific; /readyz allowlisted to RFC1918; /metrics denied) and openai_compatible provider (route backend URL with server-side secret env lookup and provider Bearer substitution, as accepted in Objective 005) — all read from the pinned peer source 2026-09-14.

## Bounded scope (workstreams A–H)

A. Reconcile the actual service topology (explicit topology document/manifest).
B. Choose the smallest secure Gateway→Local transport.
C. Add the actual Gateway-integrated Local deployment configuration.
D. Correct the cutover state machine (transitions + complete inverse).
E. Prove endpoint reachability from the right namespace (disposable, negative test).
F. Systemd user-service boot contract (linger semantics).
G. Provenance / artifact identity gate.
H. Tests / negatives + ordinary CI.

## Explicit non-goals

- No live cutover; no protected Qwen mutation/restart; no port-18020 change.
- No Gateway deployment/configuration mutation; no Gateway source changes (if
  inspection finds a genuine Gateway product defect, publish one exact handoff
  document instead; do not modify the other repository).
- No Codex profile mutation; no firewall/VPN/network mutation; no new
  network architecture invented.
- No release/tag/registry publication; no model/provider requests; no
  Qwen inference in any test.
- No refactor of the accepted Gateway/Codex protocol implementation.
- No change to the Local loopback-only binding law without a human
  architecture decision (this objective preserves it).
- No rewrite of Objective 009's accepted artifacts (PR #11, its report,
  its manifest) — the 009 record is immutable; this objective supersedes the
  cutover runbook forward by replacing its content in-repo (the runbook is a
  prepare-only planning document, not accepted release evidence).

## A. Reconcile the actual service topology

A1. Treat as strictly separate concepts: Local/Qwen host; Local process
network namespace; Gateway host; Gateway process/container network namespace;
Codex client host/profile. Do not assume shared filesystems or shared
localhost between repositories.

A2. Read the current Local deployment contract and the pinned Gateway
deployment/route contract (peer 65666f5886832034c52211fdd7604046557e6ada; verified 2026-09-14 as still the gateway repository's default-branch main (unchanged since 2026-09-13)), plus only safe
read-only live facts the Local host legitimately exposes. Produce one
explicit topology document/manifest (`docs/TOPOLOGY.md` and a
machine-readable companion if useful) defining the supported final path:

```text
Codex -> Gateway runtime -> [exact transport boundary] -> Local Coding -> loopback Qwen/vLLM
```

For every hop: network namespace; address class; authentication;
encryption/confidentiality boundary; owning repository/service; what is and
is not publicly reachable. The final design MUST NOT contain an impossible
cross-host/container `127.0.0.1` assumption. Document the verified live
facts (no Gateway deployment on the Local host; single RFC1918 LAN,
unencrypted; active Codex profile's current provider endpoint, by name/value
class without credential values; the maelstrom1->vLLM mapping is an
unresolved operator fact to be captured in the cutover step-1 baseline).

## B. Choose the smallest secure Gateway→Local transport

B1. Directive: the supported final topology is the smallest one that
preserves the Local loopback-only law: Gateway runtime co-located on the
same physical host as the Local adapter and Qwen, sharing the host network
namespace (e.g. the Gateway `api` runtime deployed with host networking, or
an equivalent single-host shared-namespace deployment). Under this topology
the Gateway→Local hop is true loopback (`127.0.0.1:18031`), no Local binding
changes, no new network mechanism, and the confidentiality boundary is:
loopback (no network traversal) + service Bearer + signed identity as the
only ingress; the Gateway route is the sole authorized caller.

B2. If source/deployment inspection of the pinned Gateway shows this
supported topology is not executable against its deployment contract, do
NOT invent a network architecture: complete all unambiguous work and return
exactly one precise decision with concrete alternatives (each with trust
boundary, mechanism, and required human actions). Multi-host topologies are
documented as NOT supported in this objective with their exact requirements
(encrypted transport or proven encrypted VPN; Local binding/tunnel change as
a human architecture decision). Never infer "private RFC1918 address" means
encrypted.

B3. Regardless of mechanism, the documented transport must: keep request
content off untrusted plaintext networks; keep Local non-publicly-reachable;
keep signed identity + service Bearer mandatory; fail closed on transport
absence at startup/readiness; use an endpoint reachable from the Gateway
RUNTIME namespace (not merely its host shell); and its rollback must not
leave a forgotten listener/tunnel/proxy.

## C. Gateway-integrated Local deployment configuration

C1. Add a deterministic, explicitly-labeled Gateway-integrated deployment
configuration path (new template + documented install procedure), enabling:
`[gateway_ingress] mode = "service_bearer_signed_identity_v1"`,
`service_token_env`, `signing_secret_env` (env names),
`identity_version = "v1"`, `policy_version = "signed-identity-v1"`,
`clock_skew_seconds = 60`, `replay_ttl_seconds = 60`, and the exact
`[constitution]` configuration requiring `identity_source = "signed_request"`
with NO static principal/session/repository (config validators forbid the
coexistence). Derive the exact compiler/observation/route settings from the
accepted Objective-005 production contract and current source (the accepted
contract is embodied in `src/slaif_local_coding/gateway_identity.py`,
`tests/test_gateway_identity.py`, `tests/test_config.py`, and the pinned
Gateway contract modules); do not guess values.

C2. The protected EnvironmentFile contract must explicitly account for all
three Local-side secret roles with distinct env names: Qwen upstream
credential; Gateway→Local service credential; Gateway→Local signing secret.
Do not copy the Gateway-only identity-derivation secret into Local. Add a
config-level enforcement (validator + test) that the three roles cannot
share one env name.

C3. Label the states truthfully in docs and in the deployment procedure:
the existing disabled-ingress template = development/local candidate (NOT
production); the new gateway-integrated template = the final
Gateway-integrated configuration. A development config must not be
mislabeled production (mechanically checked, see H6).

## D. Cutover state machine

D1. Rewrite `docs/RELEASE-CUTOVER-RUNBOOK.md` as explicit state transitions
with independent tracked states: LOCAL (artifact/config/unit/service state;
adapter endpoint/transport state), GATEWAY (exact route/provider endpoint
and capability metadata; exact Gateway authority SHA/version), CODEX (active
client profile/provider/base URL; exact pre-cutover value; exact cutover
value).

D2. The sequence must explicitly perform the operation that moves the active
Codex profile onto the Gateway path (with backup of the exact pre-cutover
profile file) BEFORE claiming a Gateway→Local→Qwen smoke.

D3. Rollback restores ALL changed state to the step-1 snapshot (Local +
Gateway + Codex), not merely one Gateway route. Rollback from every
pre-final-switch failure point is defined.

D4. Mechanically test the state-machine logic with synthetic/disposable
fixtures (a state model + transitions + snapshot/restore assertions, or an
equivalent deterministic harness). No live profile or Gateway route change
in this objective.

## E. Reachability from the right namespace

E1. Add a non-live/disposable topology qualification that proves the
endpoint configured for the simulated Gateway runtime is reachable from that
runtime/network namespace and reaches exactly the Local candidate. A
host-shell curl is insufficient where the runtime is namespaced.

E2. Include a negative test proving the old invalid assumption (separate
runtime -> `127.0.0.1:18031`) does NOT qualify merely because Local is
running elsewhere. Use safely available namespace mechanisms (e.g.
`unshare -n`, a disposable bridge-netns container) or, if none are safely
available, a deterministic structural equivalent that enforces the same
address-class/namespace contract; record exactly what was and was not
proven. All tests fake/synthetic; no protected Qwen inference; complete
cleanup with absence proof.

## F. Boot contract

F1. Directive: the supported appliance contract is unattended operation
(option B). The install/upgrade/rollback/uninstall procedures must
explicitly manage and verify user-manager linger for the appliance user
only (documented, reversible, verified state), and docs must state what
happens without linger (documented degraded mode A: service starts at
login only). Test the chosen semantics deterministically (contract tests on
the procedures + safe state inspection; do NOT enable linger or mutate any
live user state in this objective — record the current linger state of the
host user as a baseline fact only).

## G. Provenance / artifact

G1. Objective 009's accepted wheel (0.1.0, SHA-256 e4759c00e37332998ed92dc5c01fe10be4b11b3a4b1df8c33edc64e176752ee1 (81462 bytes, 26 entries)) remains
the cutover artifact authority ONLY if this objective leaves the runtime
package byte-identical — prove it mechanically (cleared rebuild, hash
comparison).

G2. If runtime package bytes change (e.g. the C2 validator), generate a new
release-candidate artifact set, regenerate the provenance manifest (new
artifact SHA-256/size, new local Git SHA), and make that exact new artifact
the only future cutover authority; document the supersession explicitly
(009's hash remains the accepted 009 record, no longer the cutover
authority). Do not release anything.

## H. Tests / negatives

At minimum: (1) final signed deployment config parses; (2) signed
deployment cannot start without the service credential; (3) cannot start
without the signing secret; (4) static identity cannot coexist with
signed-request identity; (5) distinct secret-role env names enforced; (6)
development/disabled config cannot be mislabeled production; (7) Gateway
runtime endpoint reachable from its actual simulated namespace; (8)
impossible cross-namespace loopback assumption fails qualification; (9)
cutover state transition includes explicit Codex profile switch; (10)
rollback restores Local + Gateway + Codex state model; (11) rollback from
every pre-final-switch failure point is defined; (12) no public/non-
authorized Local binding appears; (13) confidential transport requirement
mechanically represented/checked where possible; (14) service
boot/session/linger contract has deterministic tests; (15) current
gateway-contract CI remains green against the exact pinned peer
(65666f5886832034c52211fdd7604046557e6ada; verified 2026-09-14 as still the gateway repository's default-branch main (unchanged since 2026-09-13); fixture unchanged unless gateway main moved — it has
not at order time; do not re-pin silently); (16) no protected/model/
provider request occurs in any test. Plus ordinary local gates: Ruff,
format, mypy, complete local pytest, build, artifact policy inspect,
fresh-venv install smoke, compileall, shell validation.

## Security / privacy / secrets / resource / protected-host constraints

- Protected host access: READ-ONLY plus bounded disposable loopback
  candidate/fake services and disposable namespaces only. No mutation of
  18020, `qwen-serving*`, model/venv/patches, API keys, firewall/VPN/
  network, active Codex profiles, or system/user service state beyond
  uniquely-named transient units/venvs that are fully removed with proof.
- No real credentials anywhere: qualification uses synthetic values;
  profile/provider values appear only by name and address class in
  docs/manifests, never credential values; no raw prompts/source/images/
  tool output/bodies in any artifact, doc, test fixture, or report.
- Record protected-host state (unit state, PID, 18020/18021/18031
  listeners, profile mtime, linger state) before and after; any
  discrepancy is report-blocking.

## Local authority

Coding owns all safe routine setup: repo-local venvs/tools, disposable
prefixes/venvs/namespaces, fake services, transient uniquely-named units,
and complete removal with proof. Human and strategic agents are not
terminal operators.

## GitHub publication and immutable report contract

1. Start exactly from `origin/main` at 4fd4502deda23ef8815740f4db0c1e615a5a1936 (verified 2026-09-14 via `git rev-parse origin/main` after fetch); create branch
   `oap/010-pre-cutover-correctness`.
2. Implement, test, push all non-report work, create exactly one non-draft
   PR before the report; never merge.
3. Inspect and repair in-scope CI until green.
4. Capture the literal 40-hex implementation head SHA.
5. Publish exactly one immutable report at
   `oap/reports/010-a-pre-cutover-topology-and-signed-ingress-correctness.md`
   containing `Implementation head SHA: <literal 40-hex>` and
   `Report publication commit: SELF`.
6. The report commit changes only that report; its first parent equals the
   literal implementation SHA; it is the remote PR head before the exact
   response FIFO `OK`.
7. The report must contain, per workstream A–H: exact commands, sanitized
   evidence, topology/transport decisions with rationale, state-machine
   test evidence, reachability (positive + negative) evidence, boot-contract
   evidence, artifact identity decision (byte-identical proof or new
   artifact hashes), before/after protected-host facts, CI check states,
   and an explicit limitations section. If a genuine human
   architecture/network decision is required for B2, the report names
   exactly one decision with concrete alternatives. An intermediate
   in-scope failure is work to fix inside this round, not a stopping point,
   unless a genuine protected/live/release authority boundary is reached —
   then report exactly what is blocked and why.

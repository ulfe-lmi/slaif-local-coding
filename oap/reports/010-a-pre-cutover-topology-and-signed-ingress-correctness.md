# OAP Coding-Agent Report — 010-a

## Work order
- Identifier: 010-a; order path: `oap/orders/010-a-pre-cutover-topology-and-signed-ingress-correctness.md`; numeric objective: 010
- PR mode: CREATED_NEW_PR

## Status
COMPLETE

## Executive summary
All eight workstreams (A–H) of order 010-a were implemented in one PR
(#12, branch `oap/010-pre-cutover-correctness`, base `main` @
`4fd4502deda23ef8815740f4db0c1e615a5a1936`). The explicit runtime topology
is documented (separate host/namespace concepts; no impossible
cross-namespace loopback assumption), the smallest secure Gateway→Local
transport was chosen and verified against the pinned Gateway deployment
contract (co-located single-host shared-namespace deployment → true
loopback `127.0.0.1:18031`), a final Gateway-integrated signed-ingress
deployment configuration was added with config-level distinct-secret-role
enforcement, the cutover runbook was rewritten as a mechanical
state-transition machine with a complete inverse, reachability was proven
from the right namespace with a live negative test of the old invalid
assumption, the user-manager linger boot contract was made explicit and
tested, and the artifact identity gate fired: the runtime package bytes
changed (C2 validator), so a new release-candidate artifact set was
generated and became the only future cutover authority (Objective-009's
hash remains the accepted 009 record only). No live cutover, no protected
mutation, no release. GitHub CI is green at the implementation head.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #12 — https://github.com/ulfe-lmi/slaif-local-coding/pull/12 — state OPEN, non-draft
- Base: `main` @ `4fd4502deda23ef8815740f4db0c1e615a5a1936` (verified: `origin/main` after fetch equals the order's required base)
- Head: `oap/010-pre-cutover-correctness`
- Implementation head SHA: 72c4a0c63327a7ab41465b44e43d398d714b4488
- Report publication commit: SELF
- Implementation commits pushed before report: `a3171d41c65e61c64aa989c05ed0e0bc5bf3d97f` (implementation + activated order/active transcript), `72c4a0c63327a7ab41465b44e43d398d714b4488` (regenerated release provenance manifest, 010-a G2)
- New PR this round: yes (#12); amended existing: no; merge performed: NO

## Changes and files
25 files changed in the PR. Exact behavior per workstream:

### A — Topology
- `docs/TOPOLOGY.md` (new): five strictly separate concepts (Local/Qwen
  host, Local process netns, Gateway host, Gateway runtime netns, Codex
  client host/profile); supported final path with per-hop table (network
  namespace, address class, authentication, confidentiality boundary,
  owning repository/service, public reachability); verified live facts
  without credential values; B2 verdict; multi-host NOT supported with
  exact requirements; transport invariants (B3).
- `docs/topology.manifest.json` (new, schema `slaif-topology-manifest-v1`):
  machine-readable companion, mechanically checked by the tests.
- No impossible cross-host/container `127.0.0.1` assumption remains in
  the supported path: both loopback hops share one host network namespace.

### B — Transport decision
- Decision (recorded in TOPOLOGY.md §4 + runbook GATEWAY state): Gateway
  runtime co-located on the same physical host as the Local adapter and
  Qwen, sharing the host network namespace → true loopback
  `127.0.0.1:18031`, no Local binding changes, no new network mechanism;
  confidentiality = no network traversal + service Bearer + signed
  identity, Gateway route as sole authorized caller.
- Pinned-Gateway source inspection (read-only clone of
  `ulfe-lmi/slaif-api-gateway` @ `65666f5886832034c52211fdd7604046557e6ada`,
  disposable checkout, removed afterwards): per-provider
  `ProviderConfig.base_url` + `api_key_env_var` with server-side secret
  env lookup and Bearer substitution (route re-point is configuration, not
  source change); signed-identity contract module
  `local-coding-v1` v2 / replay mode
  `process_local_inclusive_horizon_fail_closed`; production compose is
  bridge-network based, so the supported topology requires a
  deployment-level change at cutover (Gateway `api` runtime in the host
  network namespace — compose per-service host networking or equivalent
  single-host shared-namespace deployment). No Gateway product defect was
  found; no cross-repository handoff document was required.
- Multi-host topologies documented as NOT supported (encrypted transport
  or proven encrypted VPN required; Local binding law change only by human
  architecture decision; "private RFC1918 address" is not encryption).

### C — Gateway-integrated deployment configuration
- `config/adapter.gateway-integrated.template.toml` (new): labeled FINAL
  Gateway-integrated configuration; `[gateway_ingress]`
  `mode = "service_bearer_signed_identity_v1"` with
  `service_token_env = "SLAIF_ADAPTER_SERVICE_TOKEN"`,
  `signing_secret_env = "SLAIF_ADAPTER_SIGNING_SECRET"`,
  `identity_version = "v1"`, `policy_version = "signed-identity-v1"`,
  `clock_skew_seconds = 60`, `replay_ttl_seconds = 60` (fixed accepted
  defaults); `[constitution] enabled = true` with
  `identity_source = "signed_request"` and no static labels;
  `[compiler] enabled = true`; route `observation_enabled = true` +
  `constitution_enabled = true`; same two documented placeholders as the
  existing template. Renders and parses through `load_settings` (full
  validator chain).
- `src/slaif_local_coding/config.py`: new `Settings` validator
  `distinct_secret_role_env_names` — the three Local-side secret roles
  (`upstream.api_key_env`, `gateway_ingress.service_token_env`,
  `gateway_ingress.signing_secret_env`) cannot share one env name (C2).
- `config/adapter.deployment.template.toml`: header now explicitly labels
  it development/local candidate (NOT production) (C3).
- `docs/DEPLOYMENT.md` §12: Gateway-integrated install procedure with the
  three distinct secret roles in the mode-0600 EnvironmentFile; §3: three
  secret roles documented; readiness contract (signed ingress reports
  `ready` only with both credentials present, fail closed).
- `docs/ADAPTER-CONFIGURATION.md`: new template + distinct-env-name rule
  documented.
- The Gateway-only identity-derivation secret is never copied to Local
  (documented in template header and DEPLOYMENT.md).

### D — Cutover state machine
- `docs/RELEASE-CUTOVER-RUNBOOK.md` (rewritten): three independent tracked
  states (LOCAL/GATEWAY/CODEX) with exact field classes; T1–T9 transitions
  with preconditions, mutations, and inverses; the explicit Codex profile
  switch (T6, with byte-exact backup of the pre-cutover profile file) is
  performed BEFORE the full-path smoke (T7) is claimed; rollback table
  covers every pre-final-switch failure point and restores ALL changed
  state to the step-1 snapshot across LOCAL + GATEWAY + CODEX; rollback
  triggers retained; post-final-switch failure declared out of runbook
  scope (separate incident process).
- `scripts/cutover_state_machine.py` (new): pure model (frozen dataclass
  states, ordered transitions, fail-closed preconditions, snapshot,
  complete inverse, `--self-test` CLI). Self-test: 9 transitions, 4
  pre-final mutators, 8 rollback points, all restore the full snapshot;
  post-final rollback rejected.

### E — Reachability from the right namespace
- `scripts/topology_qualification.py` (new): closed decision table
  `qualify_transport` (only `shared_host_namespace + loopback` qualifies;
  `separate_namespace + loopback` fails with
  `loopback_does_not_cross_namespaces`; unencrypted separate-namespace
  fails with `untrusted_plaintext_network`; encrypted separate-namespace
  fails with `multi_host_not_supported_requires_human_decision`; unknowns
  fail closed); disposable loopback-only fake "Local candidate" on an
  ephemeral port (collision-checked against 18020/18021/18031) with a
  per-run sentinel; probe subprocess run in the host namespace (positive)
  and in a fresh namespace via `unshare -n` (negative,
  `sudo -n`-assisted on this host); complete cleanup with absence proof.
- Live results on this host: host-namespace probe `reachable=true,
  sentinel_match=true` (reaches exactly the fake candidate); fresh
  namespace probe `reachable=false, error_class=OSError` (cross-namespace
  loopback does not qualify); both cleanups `listener_absent=true`.

### F — Boot contract
- `docs/DEPLOYMENT.md` §13 (new): supported appliance contract =
  unattended operation (mode B, linger enabled for the appliance user
  only, documented reversible `loginctl enable-linger`/`disable-linger`
  with `loginctl show-user … -p Linger` verification); degraded mode A
  (login only) documented; install/upgrade/rollback/uninstall manage
  linger explicitly (uninstall restores the pre-procedure state).
- `scripts/boot_contract.py` (new): read-only inspection + closed
  classification (never enables/disables linger).
- Host baseline recorded read-only: user `janezp` `Linger=no`
  (`mode_a_login_only`); not changed by this objective.

### G — Provenance / artifact identity
- Cleared rebuild (fresh temp dist, `uv build`): new wheel
  `8678e16b41bd9d73849a956c9d1f25235532eaf52c772fc695718b2063b54472`
  (81815 bytes, 26 entries) vs Objective-009 wheel
  `e4759c00e37332998ed92dc5c01fe10be4b11b3a4b1df8c33edc64e176752ee1`
  (81462 bytes, 26 entries) → **not byte-identical** (G1 negative, G2
  path taken).
- `packaging/release_provenance_manifest.json` regenerated at
  implementation commit `a3171d41c65e61c64aa989c05ed0e0bc5bf3d97f`:
  wheel `8678e16b…` (81815 B, 26 entries), sdist
  `bc993c4021a291b1961ba8d8365853ecc361be46ca2e9cddab94d0520bb5f067`
  (405978 B, 103 entries), new
  `gateway_integrated_config_template_sha256 =
  53769c8e07de45afb28a381d463f1db5d068fba5d458b35905ee501560ac2ca7`,
  plus the supersession limitation line. This exact new artifact set is
  the only future cutover authority; the 009 hash remains the accepted
  009 record only. Nothing released.
- `packaging/release_provenance_manifest.schema.json` +
  `scripts/release_provenance_manifest.py`: new required
  `gateway_integrated_config_template_sha256` template fact.
- `docs/RELEASE-ARTIFACT-POLICY.md`: supersession mechanics documented.
- `scripts/artifact_policy_check.py`: new required sdist entries
  (gateway-integrated template, TOPOLOGY.md, topology.manifest.json).

### H — Tests / negatives
New test modules: `tests/test_gateway_integrated_deployment.py` (11),
`tests/test_cutover_state_machine.py` (10),
`tests/test_topology_qualification.py` (12),
`tests/test_boot_contract.py` (4); `tests/test_packaging.py` extended
(new assets in the secret/forbidden-pattern scan; asset count floor).
Mapping to the 16 order requirements:
1. final signed deployment config parses →
   `test_gateway_integrated_config_parses_and_enables_accepted_contract` PASSED
2. signed deployment cannot start without the service credential →
   `test_signed_deployment_cannot_become_ready_without_service_credential`
   (readyz 503, `gateway_ingress=unavailable`) PASSED
3. cannot start without the signing secret →
   `test_signed_deployment_cannot_become_ready_without_signing_secret` PASSED
4. static identity cannot coexist with signed-request identity →
   `test_static_identity_cannot_coexist_with_signed_request_identity` PASSED
5. distinct secret-role env names enforced →
   `test_secret_roles_cannot_share_one_env_name` (3 shared-name variants) PASSED
6. development/disabled config cannot be mislabeled production →
   `test_development_template_is_labeled_development_not_production` +
   `test_gateway_integrated_template_is_labeled_final_gateway_integrated` PASSED
7. Gateway runtime endpoint reachable from its actual simulated namespace
   → `test_host_namespace_probe_reaches_exactly_the_fake_candidate` PASSED (live)
8. impossible cross-namespace loopback assumption fails qualification →
   `test_fresh_namespace_probe_fails_closed_for_cross_namespace_loopback`
   PASSED (live `sudo -n unshare -n` probe) + structural decision-table
   tests PASSED
9. cutover transition includes explicit Codex profile switch →
   `test_transition_set_is_the_runbook_step_set` +
   `test_codex_profile_switch_precedes_full_path_smoke` (ordering AND
   state precondition) PASSED
10. rollback restores Local + Gateway + Codex state model →
    `test_rollback_restores_full_snapshot_from_every_pre_final_failure_point`
    (all 3 state groups field-equal to the snapshot) PASSED
11. rollback from every pre-final-switch failure point defined →
    `test_every_pre_final_mutating_transition_has_a_defined_inverse` +
    full-snapshot-restore over all 8 pre-final points PASSED
12. no public/non-authorized Local binding appears →
    `test_no_public_binding_in_deployment_assets` (unit
    `IPAddressDeny=any` + loopback-only allow; templates loopback bind;
    topology manifest Local hops non-public loopback) PASSED
13. confidential transport requirement mechanically represented/checked →
    `test_manifest_supported_transport_qualifies_and_invalid_assumption_does_not`
    (closed decision table + confidentiality boundary set) PASSED
14. service boot/session/linger contract has deterministic tests →
    `tests/test_boot_contract.py` (parse/classify + doc contract +
    read-only inspection) PASSED
15. current gateway-contract CI remains green against the exact pinned
    peer → local run vs `65666f5886832034c52211fdd7604046557e6ada`
    (18/18, network guard enabled) PASSED; GitHub `gateway-contract` job
    passed at the implementation head (see CI section)
16. no protected/model/provider request in any test → all new tests are
    fake/synthetic (ephemeral loopback fake, sentinel, mock transports);
    live tests remain opt-in (`SLAIF_LIVE_TEST` not set) SKIPPED; the only
    live calls in this round were bounded read-only `/health` probes on
    18020 (order-authorized baseline evidence) and the read-only
    `loginctl`/`systemctl`/`ss`/`docker` inspections; no model/provider
    inference in any test.

## Verification
- `uv run --frozen ruff check .`: PASSED (All checks passed)
- `uv run --frozen ruff format --check .`: PASSED (336 files already formatted)
- `uv run --frozen mypy src tests`: PASSED (Success: no issues found in 70 source files)
- `.venv/bin/python -m pytest -q` (full local suite, final tree): PASSED — 1018 passed, 26 skipped, 0 failed (skips are live/opt-in: `SLAIF_LIVE_TEST` unset; Gateway-optional tests without `SLAIF_GATEWAY_ROOT`); run before the manifest commit showed exactly one expected failure (E3 drift gate, build inputs changed), which the manifest regeneration at `a3171d4` resolved: `tests/test_release_provenance_manifest.py` 6/6 PASSED at the implementation head
- `uv build` (fresh temp dist): PASSED (wheel + sdist)
- `python scripts/artifact_policy_check.py --dist <dist> --inspect`: PASSED (ok=true; wheel 26 entries, sdist 103 entries, no violations; new required sdist entries present)
- `python scripts/artifact_policy_check.py --dist <dist> --install-smoke`: PASSED (fresh empty venv, wheel-only install, import, console entry point `--help`/`--version` exit 0, in-venv provenance)
- `.venv/bin/python -m compileall -q src tests oap/bin scripts`: PASSED
- `bash -n oap/bin/*.sh packaging/*.sh`: PASSED
- `python scripts/cutover_state_machine.py --self-test`: PASSED (9 transitions, 4 pre-final mutators, 8 rollback points)
- `python scripts/topology_qualification.py --self-test`: PASSED (decision table, manifest facts, host probe sentinel match, fresh-namespace probe unreachable, cleanup absence proofs)
- `python scripts/boot_contract.py --inspect`: PASSED (read-only; `{"class": "mode_a_login_only", "linger": "no", "user": "janezp"}`)
- `SLAIF_GATEWAY_ROOT=<pinned checkout> python scripts/gateway_contract.py --gateway-root <pinned checkout> --run-tests`: PASSED (18 collected / 18 passed / 0 skipped / 0 errors; network guard enabled; checkout clean; commit `65666f5886832034c52211fdd7604046557e6ada`)
- Live bounded read-only probes (order-authorized baseline evidence only): `GET 127.0.0.1:18020/health` → 200 (before and after)

## Live model/service evidence
- Endpoint/route (no secrets): protected vLLM `127.0.0.1:18020` (read-only `/health` only — no inference, no model/provider request); dev adapter port 18031 untouched (absent before and after); port 18021 absent.
- Protected fixture before vs after (read-only `systemctl --user show`, `stat`, `loginctl`, `ss`, `sudo docker ps -a`):
  - unit `qwen-serving-vision.service`: ActiveState=active, SubState=running, MainPID=23961, started Sun 2026-09-06 18:57:26 CEST — unchanged before/after
  - `GET /health`: 200 before and after
  - active Codex profile `~/.codex/qwen-neumann.config.toml`: mode 0600, mtime 2026-09-13 11:59:21.852183775 +0200 — byte-identical mtime before/after
  - linger: `Linger=no` before and after (baseline recorded, not changed)
  - listeners: only `0.0.0.0:18020` (vLLM) in both captures; no 18021/18031; no Gateway listener
  - docker: same three stale exited containers, no ports — unchanged
  - Active Codex provider endpoint (name/value class only, no credential values): `http://maelstrom1.lmi.link:8001/v1` (plain HTTP, no TLS, same RFC1918 /24); the maelstrom1→vLLM mapping is an unresolved operator fact captured for cutover step 1
- Disqualified namespace probe used a disposable fresh namespace and an ephemeral loopback fake; no protected Qwen inference; complete cleanup with absence proof.
- Fixture unchanged: YES (all invariance facts true).

## GitHub CI / required checks
- Implementation head `72c4a0c63327a7ab41465b44e43d398d714b4488`:
  - `test`: SUCCESS (run 34813383126, job 103878973791, 1m28s)
  - `gateway-contract`: SUCCESS (run 34813383126, job 103878973560, 12s)
- All required green at drafting: yes
- Report-head checks may be pending; strategy verifies.

## Local setup/dependencies
- Repo-owned venv `.venv` via `uv sync --frozen --extra dev --group gateway-contract` (adds `pydantic-settings`, `sqlalchemy` for the gateway-contract gate only); no host-wide installs.
- Disposable artifacts: fresh temp `dist` directories (`/tmp/slaif-dist.*`) for cleared builds; disposable read-only Gateway checkout at the pinned commit under `/tmp` (deleted after inspection); ephemeral loopback fake candidates on ephemeral ports (fully removed with absence proof); one disposable network namespace per negative probe (`unshare -n`, auto-destroyed). No persistent units, no linger change, no firewall/VPN/network mutation.
- Durable docs/config: `docs/TOPOLOGY.md`, `docs/topology.manifest.json`, rewritten `docs/RELEASE-CUTOVER-RUNBOOK.md`, `docs/DEPLOYMENT.md` §12/§13, `docs/ADAPTER-CONFIGURATION.md`, `docs/RELEASE-ARTIFACT-POLICY.md`, new template, three new `scripts/` tools, four new test modules.

## Documentation
- Updated (required by behavior/config/security/operation/limitations changes): TOPOLOGY.md (new), topology.manifest.json (new), RELEASE-CUTOVER-RUNBOOK.md (state machine), DEPLOYMENT.md (Gateway-integrated config, three secret roles, boot/linger contract, labeling), ADAPTER-CONFIGURATION.md (signed mode + distinct env-name rule), RELEASE-ARTIFACT-POLICY.md (artifact supersession), README.md (topology pointer).

## Safety/scope confirmations
- Unrelated files: none committed; pre-existing working-tree change `oap/runtime.env.example` (strategic-authored, outside this order's transcript) and untracked zero-byte debris (`Local`, `clean`, `unchanged`) preserved, not committed, not cleaned.
- Secrets/raw content: none in any commit, doc, fixture, or report; synthetic values only in tests; profile/provider values by name/address class only; forbidden-pattern scans (artifact policy + packaging secret scan) pass.
- Production/protected resources: protected 18020/Qwen/Codex fixture changed: NO; no Gateway deployment exists or was created on this host; no firewall/VPN/network mutation; no new network architecture invented.
- Required tests skipped/not run: local live tests SKIPPED (opt-in `SLAIF_LIVE_TEST`, intentionally not set — no model/provider requests allowed in tests); no other required layer skipped. The fresh-namespace negative probe was available on this host (via `sudo -n unshare -n`) and ran PASSED; on hosts without a safe namespace mechanism the deterministic structural equivalent is the enforced contract and the live probe skips honestly.
- Scope deviation: none.
- Extra objective PR: NO (exactly one PR #12 for objective 010); coding merge: NO.
- Active/order edited: NO (committed as unchanged strategic bytes); report commit report-only: yes (this commit changes only this report path).

## Known limitations/blockers
- No blocker. The one human architecture decision surface (multi-host
  Gateway→Local transport) is documented with exact requirements but is
  explicitly out of scope and NOT supported in this objective; the
  supported single-host decision needs no further human action beyond the
  separately authorized cutover.
- The cutover runbook remains prepare-only; the Gateway
  host-network-namespace deployment requirement must be executed (and
  verified from the Gateway runtime namespace) by the human-authorized
  cutover order.

## Recommended strategic follow-up
Factual only; strategy decides:
- Review/accept PR #12 (CI green at the implementation head).
- The separately authorized cutover order should name: the cutover
  authority wheel `8678e16b41bd9d73849a956c9d1f25235532eaf52c772fc695718b2063b54472`
  (current manifest), the Gateway `api` runtime host-network-namespace
  deployment configuration, the route re-point to `127.0.0.1:18031/v1`,
  the explicit Codex profile switch with backup, the linger enablement
  (mode B), and the step-1 capture of the maelstrom1→vLLM operator fact.

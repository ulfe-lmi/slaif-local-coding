# OAP WORK ORDER 011-a — DOCKER MVP PACKAGING, LAN-VISIBLE DEPLOYMENT, AND RELEASE-READINESS CLOSURE

Strategic work order 011-a, final. All live facts below were independently
verified by the strategic agent on 2026-09-17 (Europe/Ljubljana) via
authenticated gh, remote git, read-only host probes (systemd/ss/loginctl/ip/
docker via `sudo -n`), and repository source inspection at the verified
remote base. No VERIFY/DRAFT markers remain.

## Objective

One coherent PR (Objective 011, round `011-a`) that makes the accepted Local
Coding implementation a **Docker-qualified, LAN-visible,
documentation-reconciled MVP release candidate**:

1. Implement the human-mandated **LAN-visible installation** law: the adapter
   may bind a non-loopback interface **only under the full accepted signed
   ingress contract** (`service_bearer_signed_identity_v1`); loopback remains
   the default and the only mode without signed ingress. This is a deliberate,
   recorded strategic architecture decision (D1), not a silent weakening.
2. Add the real **Docker product surface** (production Dockerfile,
   `.dockerignore`, Compose definition, image versioning convention,
   healthcheck, hardened runtime, wheel-based install) with
   `network_mode: host` on Linux (D2) so the true-host-loopback Qwen hop, the
   co-located Gateway loopback hop, and the LAN-visible client/Gateway hop all
   hold in one container.
3. Add a **mandatory Docker CI job** proving build/start/readiness/
   signed-request/fail-closed/content/provenance/operations evidence remotely.
4. Produce the **host-networking security delta review** as a release gate
   (isolation lost, invariants kept, compensating controls, accepted threats,
   secret-path analysis, compromised-container network reach).
5. **Extend release provenance to the OCI image** and regenerate the manifest
   (the runtime wheel bytes change in this objective; the new artifact set is
   the only future cutover authority).
6. **Reconcile all current-facing documentation** with remote truth (the
   verified drift in README, `oap/COMPLETENESS.md`, and
   `docs/IMPLEMENTATION-ROADMAP.md`) and publish the operator-facing Docker
   installation procedure plus a documented (NOT executed) container
   publication path.

No release, no tag, no registry publication, no protected-host cutover, no
Gateway mutation, no Codex-profile mutation, no network/firewall/VPN mutation.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`.
- Numeric objective: `011` (first unused; verified 2026-09-17: `oap/orders/`
  contains objectives 000 through 010 (through 010-a); 011 unused; no open PRs).
- Round: `011-a`; mode: `CREATE_NEW_PR`.
- Required base/default branch: `main` at
  `4aa805fdd197938f1f25c9ca034c2e3c3cf2fc87` (verified 2026-09-17 via
  `gh api repos/ulfe-lmi/slaif-local-coding/commits/main` and
  `git rev-parse origin/main` after fetch).
- Verified remote state at order time (2026-09-17): no open PRs
  (`gh pr list --state open` = `[]`); last merge PR #12 (objective 010)
  merged 2026-09-14T06:42:44Z; no tags (`git ls-remote --tags` empty);
  zero GitHub releases; latest main CI run 34814609380 (test +
  gateway-contract) `success`, no newer main commits.
- Required branch: `oap/011-docker-mvp-release-readiness`.
- Create exactly one non-draft PR before reporting. Never merge; never enable
  auto-merge.
- Objectives 000–010 / PRs #1–#12 remain accepted and immutable; do not
  reopen, rewrite, or edit their orders/reports/evidence.

## Strategic context and independently verified current state

Strategic independently verified on 2026-09-17 (Europe/Ljubljana):

- **Binding human release decision (2026-09-17):** the project is intended to
  be ready for its first MVP release; MVP release readiness requires an easy
  **Docker-based installation**; systemd-only is insufficient; and the
  installation must be **LAN-visible, not localhost-only**. systemd remains a
  supported secondary direct-host path (D3).
- Remote: `main` = `4aa805fdd197938f1f25c9ca034c2e3c3cf2fc87` (PR #12 merge);
  no open PRs; no tags; no releases; main CI green (run 34814609380).
- Pinned Gateway peer and gateway-repo main both
  `65666f5886832034c52211fdd7604046557e6ada` (unchanged since 2026-09-13);
  gateway open PRs #291/#250/#224 are unmerged; local fixture pin
  (`tests/fixtures/gateway/current_peer_authority.json`) unchanged; contract
  local-coding-v1 v2 (replay_mode
  process_local_inclusive_horizon_fail_closed), codex-0.149-responses-v1 v4.
- Protected host (read-only): `hinton1`; interfaces `enp1s0 10.8.132.75/24`
  (single RFC1918 LAN, unencrypted, no VPN/tunnel software) and
  `docker0 172.17.0.1/16`; user unit `qwen-serving-vision.service`
  active (running) since Sun 2026-09-06 18:57:26 CEST, main PID 23961 (vllm,
  qwen3.8-27b); listener `0.0.0.0:18020`, `GET /health` = 200; port 18021
  absent; port 18031 absent; ports 18031–18034 verified free; `Linger=no` for
  user janezp; active coding profile `~/.codex/qwen-neumann.config.toml`
  present, mode 0600, mtime 2026-09-13 11:59 (base_url
  `http://maelstrom1.lmi.link:8001/v1`; credential values never recorded);
  docker 29.1.3 + Docker Compose v5.0.1 available to janezp via `sudo -n`
  with only three stale exited containers (years old, no ports).
- Repository at base: **no Dockerfile, no compose file, no .dockerignore**
  (verified by full `git ls-tree -r` of `origin/main`). Deployment is the
  systemd user service + repository venv path only
  (`packaging/slaif-local-coding.service`, `docs/DEPLOYMENT.md`).
- Accepted artifact state at base (manifest
  `packaging/release_provenance_manifest.json`, schema
  slaif-release-provenance-v1): wheel
  `slaif_local_coding-0.1.0-py3-none-any.whl` SHA-256
  `8678e16b41bd9d73849a956c9d1f25235532eaf52c772fc695718b2063b54472`
  (81815 B, 26 entries) = cutover authority; sdist
  `bc993c4021a291b1961ba8d8365853ecc361be46ca2e9cddab94d0520bb5f067`
  (developer-only); `objective` field still `"009-a"` (known cosmetic stale
  field); limitations state "single supported deployment path: systemd";
  `status.cutover_performed=false`, `released=false`.
- Source law at base (verified in `src/slaif_local_coding/config.py`):
  `ServerConfig.loopback_only` accepts only `127.0.0.1`/`::1`/`localhost`;
  `GatewayIngressConfig` modes `disabled` / `service_bearer_static_identity` /
  `service_bearer_signed_identity_v1` (signed mode requires
  `service_token_env` + `signing_secret_env`; fixed contract defaults
  enforced); `Settings.safe_integration` requires signed ingress to imply
  enabled compiler + constitution + `identity_source = "signed_request"` with
  no static identity; `Settings.distinct_secret_role_env_names` rejects shared
  env names across the three Local-side secret roles; `/readyz` returns 503
  with `gateway_ingress = "unavailable"` when ingress credentials are missing
  (fail-closed readiness, app starts); `/metrics`, `/readyz`, `/healthz` are
  served on the single adapter socket (one uvicorn process;
  `metrics_host` is a config-level loopback declaration, not a second
  binding).
- Topology law at base (`docs/TOPOLOGY.md`,
  `scripts/topology_qualification.py::qualify_transport`): supported
  combination is (shared_host_namespace, loopback) only;
  (separate_namespace, loopback) fails closed as
  `loopback_does_not_cross_namespaces`; `rfc1918_plaintext` fails closed;
  multi-host not supported without a human architecture decision.
- Cutover runbook at base (`docs/RELEASE-CUTOVER-RUNBOOK.md`): explicit
  S0/T1–T9 state machine tracking LOCAL (artifact/config/service/listener),
  GATEWAY (route backend, authority SHA, signed contract), CODEX (provider
  class, profile backup) with complete inverse rollback; prepared-only.
- **Verified documentation drift** (current-facing docs at base):
  - `README.md` status table: objective 009 row reads "this PR | (open)";
    objective 010 row absent; prose says "The adapter is a private,
    loopback-only candidate."
  - `oap/COMPLETENESS.md`: objective 009 row reads "this PR (open)";
    objective 010 row absent.
  - `docs/IMPLEMENTATION-ROADMAP.md`: "Current state" section lists
    objectives 000–008 merged and "Objective 009 (this PR)"; objective 010
    absent.
  All three are stale: 009 merged as PR #11 (merge commit
  `4fd4502deda23ef8815740f4db0c1e615a5a1936`) and 010 merged as PR #12
  (merge commit `4aa805fdd197938f1f25c9ca034c2e3c3cf2fc87`), both with green
  CI; no PR is open.
- `uv.lock` SHA-256 `1237cbd179f71b99984c80f927529549f5e61eb705585ef9cf2ab0fa9e26764a`;
  `pyproject.toml` SHA-256 `af91f82283882f1e51ee763d635f94f1ae2534c51585c837aa61cff8a2f7dda2`
  (both recorded in the base manifest; both MUST remain unchanged by this
  objective — zero new runtime or dev dependencies).

## Strategic decisions (recorded by this order)

These decisions are the explicit strategic architecture authority for the
Docker/MVP surface. Coding implements them as stated; it does not re-decide.

- **D1 — LAN-visible binding law (human-mandated, 2026-09-17).** The adapter
  may bind a non-loopback interface **if and only if**
  `gateway_ingress.mode = "service_bearer_signed_identity_v1"` (full contract:
  service Bearer + signed identity v1 + replay protection). Loopback
  (`127.0.0.1`/`::1`/`localhost`) remains the default and remains the only
  permitted bind when ingress is `disabled` or
  `service_bearer_static_identity`. `listen_host` accepts loopback literals
  and bare IPv4/IPv6 literals plus `0.0.0.0`/`::` (all-interfaces); hostnames
  and anything else are rejected. This deliberately changes the
  objective-000/010 loopback-only binding law exactly as far as the human
  release decision requires and no further: the **authentication/integrity
  contract is unchanged and remains mandatory**; the Qwen hop remains true
  host loopback; the signed ingress cannot be bypassed in any configuration
  that is non-loopback.
- **D2 — Docker network mode: `network_mode: host`, Linux Docker Engine
  only.** Independently verified rationale: (a) the Qwen hop needs true host
  loopback (`127.0.0.1:18020`), which only host networking provides in a
  container; (b) a co-located Gateway runtime in the host namespace still
  reaches the adapter at `127.0.0.1:18031` (the objective-010 transport
  decision remains valid and unchanged); (c) a bridge-networked Gateway
  container (the pinned Gateway's default compose deployment) reaches the
  adapter at the host bridge IP (e.g. `172.17.0.1:18031`) — no
  Gateway-deployment-level change needed, config-only; (d) a Gateway or
  client on another LAN host reaches the adapter at
  `<host-lan-ip>:18031` under D1. Bridge-only networking cannot satisfy (a)
  and (b) simultaneously. Supported platform stated narrowly: **Linux Docker
  Engine + Compose v2 plugin**; no other platform is claimed.
- **D3 — systemd path retained as secondary.** The systemd user-service
  path (unit file, loopback + `IPAddressDeny=any` containment) is unchanged
  and remains the direct-host path, including the path used by the
  protected-host cutover runbook. Docker is the **canonical MVP
  installation path**; docs must say so without demoting the systemd path.
- **D4 — Trusted-LAN confidentiality boundary (accepted MVP limitation).**
  On the LAN-visible surface, request content traverses the declared trusted
  private LAN without TLS (MVP). Compensating controls: service Bearer +
  HMAC-signed identity + replay protection (authenticity/integrity/
  anti-replay), no anonymous endpoint, fail-closed readiness, bounded
  bodies, no raw-content logging (unchanged law). TLS termination in front of
  the adapter is an operator option explicitly out of scope for the MVP.
  `/healthz`, `/readyz`, `/metrics` share the adapter socket; on a
  LAN-visible bind they are reachable from the same trusted surface and
  expose state/counts only (no raw content) — accepted and documented.
  No runtime change to the metrics endpoint is made in this objective.
- **D5 — Artifact identity.** This objective changes runtime bytes
  (`config.py` binding law), so the wheel bytes change: the regenerated
  wheel + sdist + OCI image build inputs become the **only future cutover
  authority** via the regenerated provenance manifest (schema v2). The
  010-a wheel hash `8678e16b...` remains the accepted 010 record only.
  Package version stays `0.1.0` (no version bump in this objective).
- **D6 — Disposable qualification split.** The GitHub runner (disposable,
  not a protected host) proves the canonical-port (18031) containerized
  qualification including cross-namespace reachability. The protected host
  receives only a **loopback/docker0-confined** disposable container run
  (explicitly permitted port `18032`, bind `172.17.0.1` — docker0 link-local,
  **no LAN-exposed listener at any time**, fake upstream only) to prove
  image build + start + signed request + teardown locally. No protected
  service is touched by either.
- **D7 — Dependency freeze.** `pyproject.toml` dependencies and `uv.lock`
  are invariant (SHA-256 recorded above). All Docker/qualification tooling
  (simulated Gateway signer client, fake upstream server, CI scripts) is
  stdlib-only Python; no new dependencies, no new build-system requirements.
- **D8 — Client-facing honesty.** Plain Codex/OpenAI clients cannot mint
  signed identity requests. The documented MVP client path is
  Codex → SLAIF API Gateway → adapter (the Gateway carries the service
  credential and signer; pointing its provider route at the adapter
  endpoint is Gateway **configuration only**). Direct unsigned client access
  to the adapter exists only in the loopback development mode (ingress
  disabled) and is labeled as such.

## Scope

Workstreams (one PR):

- **A. LAN-visible binding law** — config validator + cross-mode rule +
  template placeholder + tests (A1–A5).
- **B. Docker product surface** — Dockerfile, .dockerignore, compose.yaml,
  image/versioning convention, healthcheck, hardening, wheel-based runtime
  (B1–B12).
- **C. Docker CI job** — mandatory remote evidence (C1–C12).
- **D. Security delta review (release gate)** — Docker vs systemd
  containment comparison (D1'–D6'; numbering D1x below to avoid collision
  with strategic decisions).
- **E. Release provenance extension** — schema v2 with OCI section,
  generator, regenerated manifest (E1–E5).
- **F. Documentation reconciliation + operator install + publish design**
  (F1–F9).
- **G. Runbook / topology / state-machine updates** (G1–G4).

## Non-goals

- No release, tag, GitHub Release, or registry publication; no image pushed
  anywhere (the publication path is designed and documented only).
- No protected-host cutover; no mutation of port 18020, qwen-serving,
  model/checkpoint/patches/venv, systemd production state, API keys,
  firewall/VPN/network bindings, or active Codex profiles; no linger
  mutation; no live Qwen inference (fake upstreams only, including in CI).
- No `slaif-api-gateway` repository mutation (pinned peer compatibility
  checking is in scope; if a genuine Gateway product defect is found,
  return one exact handoff instead of changing that repository).
- No Kubernetes/Swarm/Helm/Terraform/Ansible/Celery/Redis or other platform;
  no Windows/macOS Docker claims; no multi-host orchestration.
- No OIDC/email/notifications/monitoring/secret-management infrastructure.
- No refactor of the accepted Codex/Gateway protocol, constitution, image,
  or cache implementation; no version bump; no `uv.lock`/dependency change.
- No expansion of the OAP framework (no new canaries, transports, roles,
  protocols, or planning documents); no rewrite of immutable historical
  orders/reports/evidence.
- No second deployment system beyond Docker + retained systemd; do not
  implement multiple deployment variants "because the roadmap mentioned
  them".

## Requirements

### A. LAN-visible binding law

- A1. `ServerConfig.listen_host` validation: loopback literals
  (`127.0.0.1`, `::1`, `localhost`) always accepted; bare IPv4/IPv6 literals
  and `0.0.0.0`/`::` accepted **only** when
  `gateway_ingress.mode = "service_bearer_signed_identity_v1"` (enforced as a
  `Settings`-level cross-validator with a precise error message); all other
  values (hostnames, schemes, ports, malformed) rejected. The existing
  loopback default (`127.0.0.1`) is unchanged.
- A2. Configuration matrix tests (pure unit, no network): loopback ×
  {disabled, static, signed} all valid; non-loopback literal × {disabled,
  static} rejected; non-loopback literal × signed valid; `0.0.0.0`/`::` ×
  signed valid; hostname rejected in every mode; the three distinct
  secret-role names remain enforced (010 C2 invariant).
- A3. `config/adapter.gateway-integrated.template.toml` gains exactly one
  additional documented placeholder `__LISTEN_HOST__` (loopback
  `127.0.0.1` for the systemd/co-located path; an interface IP or `0.0.0.0`
  for the Docker LAN-visible path); the template keeps its two existing
  placeholders and its truthful label (final Gateway-integrated
  configuration); the development/disabled template
  (`config/adapter.deployment.template.toml`) is unchanged (loopback,
  development-only).
- A4. Static-template tests (`tests/test_gateway_integrated_deployment.py`
  or equivalent) updated: exactly three documented placeholders; the
  substituted loopback variant and the substituted non-loopback variant both
  parse; the non-loopback variant is rejected by the validators when
  `gateway_ingress` is disabled or static (fail closed).
- A5. `docs/ADAPTER-CONFIGURATION.md` documents the exact binding law and
  the `metrics_host` policy precisely (config-level declaration; single
  socket; D4).

### B. Docker product surface

- B1. `Dockerfile` (multi-stage, Linux): build stage builds the wheel from
  repository source using the committed `uv.lock` (pinned base + pinned uv,
  or equivalent locked mechanism; no unpinned floating base tags anywhere);
  runtime stage **pinned by digest** (e.g. `python:3.12-slim-bookworm@sha256:...`),
  installs dependencies resolved from the committed `uv.lock` (frozen), then
  installs the **built wheel non-editable**; the runtime stage contains no
  repository source checkout (no `src/` bind/copy as code, no `.git`), no
  `oap/`, no `tests/`, no `references/`, no caches, no placeholder files.
  No editable install; no host-side venv assumption.
- B2. `.dockerignore` explicit (not accidental): excludes at minimum `oap/`,
  `.git/`, `.venv/`, `dist/`, `build/`, `tests/`, `docs/`, `references/`,
  `scripts/`, `config/`, `packaging/`, `.github/`, `__pycache__`, `*.pyc`,
  `.mypy_cache/.pytest_cache/.ruff_cache`, `runtime.env`, `Local`, `clean`,
  `unchanged`, and any env/secret files, while retaining exactly what the
  build stage needs (`src/`, `pyproject.toml`, `uv.lock`, `LICENSE`,
  `NOTICE`, `README.md`, and other files the wheel metadata requires).
- B3. Runtime hardening in the Compose definition (and asserted by CI):
  non-root dedicated user (fixed uid/gid created in the image); read-only
  root filesystem; `no-new-privileges`; `cap_drop: [ALL]`; **no**
  `privileged`; **no** Docker socket mount; **no** repository source bind
  mount as the production runtime; tmpfs mounts for the disposable cache
  (cache `root` in the Docker config template points at the tmpfs path) and
  `tmp`; bounded tmpfs sizes; `restart: unless-stopped`.
- B4. `compose.yaml` (canonical, single adapter service,
  `network_mode: host`): configuration file mounted **read-only** from a
  host path created from the gateway-integrated template (listen_host
  placeholder resolved to the site value); `env_file` referencing a mode-0600
  host environment file (the three distinct secret roles by env name; no
  values in the compose file); healthcheck using the in-image Python against
  `127.0.0.1:18031/readyz` (documented interval/timeout/retries/start_period);
  no published ports (host mode ignores them; the compose file must not
  contain a `ports:` section for the adapter); no secrets in any compose
  interpolation default.
- B5. Image identity: deterministic local tag convention
  `slaif-local-coding:0.1.0-<short-sha>` (and full-sha form) documented;
  reserved publication reference `ghcr.io/ulfe-lmi/slaif-local-coding`
  documented as the future registry (no push in this objective).
- B6. OCI labels on the image: `org.opencontainers.image.source`,
  `org.opencontainers.image.revision` (build Git SHA),
  `org.opencontainers.image.version` (`0.1.0`),
  `org.opencontainers.image.created`, plus project labels recording package
  version, pinned Gateway peer SHA, supported topology mode, and
  qualification status (`disposable-qualification-only; not released`).
- B7. Startup contract: the canonical compose path uses the **final
  Gateway-integrated (signed)** configuration; the documented development
  variant (ingress disabled, loopback) may exist as a separate clearly
  labeled example file and must never be labeled production (mechanically
  checked, extending the 010 label tests).
- B8. In-image provenance proof (mechanical, in CI): `import
  slaif_local_coding` succeeds; `slaif-local-coding --version` reports
  0.1.0; the distribution is installed in site-packages (non-editable, not a
  repository path); the wheel file hash recorded inside the image equals the
  provenance-manifest wheel SHA-256.
- B9. `docs/DOCKER-INSTALL.md` (new, operator-facing, concise, linear):
  prerequisites (Linux host, Docker Engine, Compose v2 plugin, an
  OpenAI-compatible upstream reachable at the documented address — for the
  MVP appliance the host-loopback Qwen/vLLM, a fake upstream for
  evaluation; outbound connectivity: Docker Hub base image pull at build
  time only); steps: (1) obtain the reviewed commit/repository, (2) build
  the image (or pull the published image after a human release), (3)
  instantiate the config template + environment file with the small set of
  site values and the three secrets (never in Git), (4) `docker compose up
  -d`, (5) verify readiness/health (bounded poll, documented), (6)
  stop/restart/status, (7) upgrade (new reviewed image, `up -d --force-
  recreate`, readiness re-verification), (8) rollback (previous image tag,
  same mechanics), (9) cache purge (tmpfs — container recreate; no
  persistent cache state is claimed), (10) uninstall (compose down,
  image remove, config/env removal — nothing persistent by design). The host
  never needs Python, uv, project dependencies, or a project virtualenv.
  The doc must state: the host must run the protected Qwen/vLLM service on
  the **same host** (loopback hop); the supported platform is Linux Docker
  Engine; the LAN-visible behavior and its security boundary (link to the
  security delta doc); "Connecting the SLAIF API Gateway" section (Gateway
  provider route `base_url` → adapter endpoint; service credential +
  signing secret env names on the Gateway side — configuration only, no
  Gateway source change); "Direct client access" honesty note (D8).
- B10. No secret value may appear in the image (no `ENV` secret values, no
  build-ARG secrets), in the compose file, in logs, or in documentation;
  secret roles by env name only (continuity with 010 law).
- B11. `packaging/readyz-wait.sh` remains the loopback readiness poll for
  both paths; the Docker path documents the equivalent `docker compose`
  health/`docker inspect` check.
- B12. A committed stdlib-only `scripts/fake_upstream_server.py` (disposable
  fake OpenAI-compatible upstream: `/health`, `/v1/models`,
  `/v1/chat/completions` non-stream + SSE stream + a function-tool
  round-trip shape) used by CI and local qualification; excluded from both
  artifacts (already under the top-level `scripts/` hatch exclusion —
  re-verified by the artifact policy check).

### C. Docker CI (mandatory, remote evidence)

- C1. New `docker` job in `.github/workflows/ci.yml` (ubuntu-latest,
  preinstalled Docker; standard runner — host networking is available there).
- C2. Build the wheel with the same locked toolchain as the `test` job;
  record its SHA-256; `docker build` the runtime image (label revision =
  `$GITHUB_SHA`); assert the in-image wheel hash equals the
  provenance-manifest wheel hash (E2) — the image is bound to the committed
  artifact.
- C3. `docker compose config --quiet` succeeds (rendered configuration
  validation; no secret values in the rendered output).
- C4. Start the disposable stack on the runner: fake upstream (stdlib
  script, runner loopback, dedicated port), adapter container
  (`network_mode: host`, listen `0.0.0.0:18031` — the runner is not a
  protected host), readiness becomes healthy within a bounded wait.
- C5. Representative requests **from the simulated Gateway runtime**: a
  disposable bridge-network container (a separate network namespace) running
  the committed stdlib signed-request client (`scripts/sim_gateway_client.py`
  or equivalent, stdlib-only: service Bearer + HMAC-signed identity v1 with
  nonce/timestamp, using the runner's docker0 bridge IP
  `172.17.0.1:18031` as the configured endpoint) succeeds with: `/v1/models`,
  one non-streaming chat completion, one streaming (SSE) chat completion,
  and one ordinary function-tool round-trip, each reaching exactly the
  containerized adapter and its fake upstream (sentinel-correlated).
- C6. Negative/contract evidence from the same simulated runtime:
  `127.0.0.1:18031` from inside the bridge container **fails**
  (loopback does not cross namespaces — the documented invalid assumption
  stays rejected); missing service token → 401; tampered/invalid signature →
  rejected (401/403); replayed nonce → rejected (replay protection); a
  non-loopback adapter bind with ingress disabled is rejected at
  configuration time (A2 law), demonstrated.
- C7. Fail-closed: a second adapter instance without the signing-secret env
  role (or without the env file) starts but `/readyz` = 503
  (`gateway_ingress: "unavailable"`) and the compose healthcheck reports
  unhealthy — mechanically asserted; torn down.
- C8. Image content + hardening scan: exported image filesystem contains no
  forbidden material (`oap/`, `tests/`, `references/`, `.git`, `scripts/`,
  placeholder files, `runtime.env`, host-specific paths such as
  `/synology/`, any secret pattern from the 009/010 scanner list);
  `docker inspect` asserts non-root user, read-only root fs,
  no-new-privileges, cap_drop ALL, no privileged, no `/var/run/docker.sock`,
  no repo source bind mount; OCI labels (B6) present and correct.
- C9. Operations mechanically exercised on the runner: stop → start
  (readiness healthy again); recreate; **upgrade** (second tag built from
  the same source, `--force-recreate`, readiness healthy); **rollback** to
  the previous tag (readiness healthy); after each step the mounted
  configuration file hash is unchanged (host-side state is the only
  persistent state; the tmpfs cache is intentionally wiped — documented).
  Final teardown with absence proof (no leftover adapter/fake processes or
  listeners from the job on the canonical ports).
- C10. The existing `test` and `gateway-contract` jobs remain unchanged in
  contract and green; the pinned peer remains
  `65666f5886832034c52211fdd7604046557e6ada` (re-verify at report time; if
  the gateway main moved, the fixture pin law decides — do not silently
  re-pin).
- C11. Every Docker job step that cannot run in hosted CI for a specific
  reason must not be hand-waved: name it, state the reason, and provide the
  compensating evidence (local disposable run on the protected host per D6,
  or a deterministic structural check) with the evidence boundary written in
  the report.
- C12. CI total wall time must stay proportionate (no deployment simulator
  bloat); the Docker job must complete within the normal CI budget.

### D. Security delta review (release gate)

A new `docs/DOCKER-SECURITY-DELTA.md` (strategic decisions D1–D8 recorded as
authority) must explicitly contain:

- D1'. What isolation is **lost** versus the qualified systemd containment,
  compared directive-by-directive (`IPAddressDeny=any`,
  `ProtectSystem=strict`, `ProtectHome`, `ProtectProc`,
  `RestrictNamespaces`, `PrivateTmp`, etc.) — including that host networking
  removes Docker network-namespace isolation by design (D2).
- D2'. What application invariants **remain** (signed ingress mandatory in
  every non-loopback configuration; fail-closed readiness; Qwen hop true
  host loopback; no anonymous endpoints; bounded bodies; no raw-content
  logging; replay protection; distinct secret roles).
- D3'. What compensating controls are **added** (read-only rootfs, non-root,
  no-new-privileges, cap drop ALL, no privileged, no socket, tmpfs cache,
  read-only config mount, restart policy).
- D4'. Accepted threats for the single-host MVP, explicitly enumerated:
  Docker administrators/root on the host are **within** the trust boundary;
  a compromised adapter container can reach every host interface (the
  declared trusted LAN) and host loopback (including the protected vLLM
  port 18020) — no more network reach than the host itself; request
  confidentiality over the LAN relies on the trusted-private-LAN boundary
  (D4 strategic decision) — no TLS on the adapter hop in the MVP.
- D5'. Secret-path analysis: image layers (none), build arguments (none),
  compose interpolation/config output (env-file reference only, no values),
  inspectable container environment (values visible to host Docker
  group/root — accepted; the env file is 0600 on the host), logs (no
  secrets by the logging law), mounted files (config is non-secret; env file
  0600).
- D6'. Compromised-container network reach (all host interfaces + host
  loopback + LAN) and the explicit statement that this deployment is **not
  claimed security-equivalent** to the systemd path (different containment
  classes), and that the loopback-only/stronger-containment requirement and
  the human LAN-visible requirement conflict — resolved by D1 (signed
  contract + trusted-LAN boundary), documented as an accepted MVP limitation.

### E. Release provenance extension

- E1. `packaging/release_provenance_manifest.schema.json` → schema v2
  (`slaif-release-provenance-v2`): adds an `oci` section recording
  `image_reference` (`ghcr.io/ulfe-lmi/slaif-local-coding`),
  `tag_convention`, `base_image` (name + digest), `dockerfile_sha256`,
  `compose_sha256`, `dockerignore_sha256`, `wheel_sha256` (cross-referenced
  to `artifacts.wheel`), `image_digest` (null until a human publication),
  `published: false`, and the label set (B6); `objective` field records the
  producing objective (`011-a`); limitations updated (two deployment paths:
  Docker canonical MVP / systemd secondary; Docker qualified in CI +
  disposable environments only; LAN-visible binding law in force; cutover
  not performed; not released; no registry publication).
- E2. `scripts/release_provenance_manifest.py` extended (same
  implementation-state regeneration discipline as 009/010); the committed
  `packaging/release_provenance_manifest.json` is regenerated from the
  implementation state: rebuilt wheel (new SHA-256 — bytes changed per D5),
  new template hashes (A3), new asset hashes (Dockerfile/compose/
  .dockerignore), Git commit, runtime/lockfile hashes (invariant per D7),
  gateway peer (invariant), `objective: "011-a"`.
- E3. `tests/test_release_provenance_manifest.py` extended: schema v2
  validation, hash cross-checks (manifest wheel hash == rebuilt wheel;
  template/asset hashes == committed files; base image digest pinned),
  `objective` field correctness, status fields
  (`cutover_performed=false`, `released=false`, `oci.published=false`).
- E4. The regenerated wheel + sdist + documented image inputs are declared
  in docs (DEPLOYMENT + artifact policy) as the **only future cutover
  authority**; the 010-a hash remains the accepted 010 record only.
- E5. Container publication design (NOT executed): documented procedure in
  `docs/DOCKER-INSTALL.md`/`docs/DEPLOYMENT.md` (human action: authenticated
  push of the built image to `ghcr.io/ulfe-lmi/slaif-local-coding` with tags
  `0.1.0` + `sha-<sha>`, digest capture, manifest `image_digest` fill,
  `published` flip by a later human-authorized release order) plus a
  committed, inert, `workflow_dispatch`-only `.github/workflows/
  release-image.yml` (declares `packages: write`, no secrets configured,
  gated so it cannot run on PRs/pushes). No image is pushed by this
  objective.

### F. Documentation reconciliation and operator docs

- F1. `README.md`: correct the status table (009 merged PR #11 / merge
  commit `4fd4502deda23ef8815740f4db0c1e615a5a1936`; add 010 merged PR #12 /
  `4aa805fdd197938f1f25c9ca034c2e3c3cf2fc87`; 011 = this PR with truthful
  pre-merge state); fix "private, loopback-only candidate" prose to the
  exact binding law (loopback default; non-loopback only under full signed
  ingress); name Docker as the canonical MVP installation path with a link
  to `docs/DOCKER-INSTALL.md`; keep cutover-NOT-performed / NOT-released
  statements current.
- F2. `oap/COMPLETENESS.md`: same drift corrections (009/010 merged rows;
  011 row = this PR, pre-merge); historical dated sections preserved
  verbatim (they are labeled historical audits).
- F3. `docs/IMPLEMENTATION-ROADMAP.md`: "Current state" section corrected
  (009/010 merged with exact commits; 011 = this PR: Docker MVP packaging +
  release-readiness closure); all historical objective sections unchanged.
- F4. `docs/DEPLOYMENT.md`: §1 restated — two supported paths: **Docker
  (canonical MVP installation path)** and **systemd user service (secondary
  direct-host path, including the protected-host cutover path)**; asset
  table gains the Docker assets; Docker install/upgrade/rollback/uninstall
  procedures (or exact links to DOCKER-INSTALL.md — no duplicated command
  sequences in four files); qualification boundary section updated (D6
  split); the unit header comment corrected to list all three secret roles
  (comment-only).
- F5. `docs/DOCKER-INSTALL.md`: new operator-facing procedure per B9.
- F6. `docs/DOCKER-SECURITY-DELTA.md`: new per workstream D.
- F7. `docs/TOPOLOGY.md` + `docs/topology.manifest.json`: extend the §4
  transport decision with the **supported LAN-visible signed variant**
  (strategic decisions D1/D2/D4): non-loopback adapter bind is legal only
  under full signed ingress; per-hop table rows for (i) co-located
  host-namespace Gateway → `127.0.0.1:18031` (unchanged), (ii) bridge-
  container Gateway → host bridge IP, (iii) LAN-different-host Gateway/
  client → host LAN IP; the impossible cross-namespace loopback remains
  rejected; §5 invariant 1 re-adjudicated exactly per D4 (trusted-LAN
  boundary, signed contract, no anonymous surface); §6 updated (what this
  objective did/did not do). Manifest schema bumped consistently and
  mechanically checked.
- F8. `docs/RELEASE-ARTIFACT-POLICY.md`: add the OCI image as the supported
  Docker-path distribution artifact (built **from** the supported wheel;
  image content law mirrors the artifact policy exclusions; sdist remains
  developer-only; wheel remains the supported Python artifact); provenance
  now covers wheel + sdist + OCI build inputs.
- F9. `docs/RELEASE-CUTOVER-RUNBOOK.md`: LOCAL state gains
  `local.binding_class` (`loopback_18031` | `lan_18031_signed`);
  precondition 2 points at the 011-a regenerated manifest as cutover
  authority; GATEWAY state note adds the bridge-container variant (config-
  only route backend at the bridge IP); the protected-host cutover path
  itself (co-located loopback, T1–T9, rollback table) remains otherwise
  unchanged; `docs/ADAPTER-CONFIGURATION.md` per A5.

### G. Runbook / topology / state-machine mechanics

- G1. `scripts/cutover_state_machine.py`: `local.binding_class` becomes a
  tracked LOCAL field with its class values; every mutating transition and
  the complete rollback table track it (rollback restores the step-1
  binding class); self-test extended.
- G2. `scripts/topology_qualification.py::qualify_transport`: extended
  decision table — adds the signed-contract dimension and the
  trusted-LAN-visible endpoint class: (separate_namespace, non-loopback,
  full_signed_v1, trusted_lan) and (shared_host_namespace, non-loopback,
  full_signed_v1) are **supported**; every combination without the full
  signed contract fails closed; (separate_namespace, loopback) keeps failing
  closed (`loopback_does_not_cross_namespaces`); unknown inputs fail closed.
  Self-test and the structural/namespace probes retain the 010 negative
  behavior.
- G3. Tests for G1/G2 in the existing test files (mechanical,
  deterministic, fake/synthetic only).
- G4. No live state change: G1/G2 are model/script changes exercised by
  self-tests and unit tests only; the protected-host cutover remains
  prepare-only.

## Acceptance criteria (all observable)

1. A2 configuration matrix passes (including all rejects); the 010 distinct-
   secret-role and signed/no-static-identity invariants remain green.
2. Rebuilt wheel SHA-256 recorded; manifest v2 regenerated with
   `objective: "011-a"`, all template/asset/lockfile hashes verified against
   committed files, status fields correct; old 010-a hash referenced only as
   the historical record.
3. Image builds (CI + local protected-host disposable run); B8 in-image
   provenance proof passes (import, `--version`, non-editable location,
   wheel hash == manifest).
4. Compose configuration validates (C3); adapter container starts; readiness
   healthy within bound (C4).
5. C5 signed requests from the simulated bridge-namespace Gateway runtime
   succeed via the non-loopback endpoint (models, non-stream, SSE stream,
   function-tool round-trip), sentinel-correlated to the fake upstream.
6. C6 negatives pass: cross-namespace `127.0.0.1` fails; missing token 401;
   invalid signature rejected; replay rejected; non-loopback + non-signed
   config rejected at parse.
7. C7 fail-closed (missing signing secret → `/readyz` 503 / unhealthy)
   proven mechanically.
8. C8 content/hardening/label assertions all pass; zero forbidden entries;
   zero secret patterns.
9. C9 stop/start/recreate/upgrade/rollback exercised; config hash invariant;
   teardown absence proof.
10. All required CI checks present and successful at the report head:
    `test`, `gateway-contract` (peer still `65666f58...`), `docker`; no
    failed/cancelled/missing/pending required check; ordinary Local pytest
    fully green; ruff/mypy/format clean; artifact policy + fresh-install
    smoke green (wheel bytes changed → re-proven).
11. Protected host before/after identical: `qwen-serving-vision.service`
    active since 2026-09-06 18:57:26 CEST, PID 23961 (no restart),
    `0.0.0.0:18020` /health 200, 18021/18031 absent, profile mtime
    2026-09-13 11:59, `Linger=no`, no Gateway deployment, **no
    LAN-exposed listener at any point during qualification**, no leftover
    containers/images/listeners from the local disposable run (absence
    proof), no persistent slaif unit.
12. Docs: no "this PR (open)" language remains anywhere in current-facing
    docs; 009/010 rows carry exact merge commits; Docker canonical / systemd
    secondary stated; `docs/DOCKER-INSTALL.md` procedure matches actual
    repository behavior command-for-command; `docs/DOCKER-SECURITY-DELTA.md`
    complete per D1'–D6'; TOPOLOGY + manifest + runbook + state machine
    consistent with D1/D2; historical OAP artifacts byte-unchanged.
13. `uv.lock` and `pyproject.toml` dependency sets byte-identical to base
    (SHA-256 per D7); diff scope bounded to in-scope files; no dependency,
    service, model, network, profile, or release-state change.
14. No tag, no release, no image push, no Gateway repository change, no
    version bump (verified against GitHub at report time).

## Verification required

- Local (coding agent, on the protected host, all disposable):
  - `uv build` + artifact policy inspect (wheel + sdist) + fresh-venv
    install smoke;
  - full ordinary pytest + ruff/mypy/format;
  - `docker build` (local) and the D6-confined disposable compose run:
    bind `172.17.0.1:18032` (docker0 link-local only — **no LAN
    exposure**), signed ingress enabled, three-role env file (fake values,
    never recorded), fake upstream on runner/host loopback, signed request
    from a bridge-namespace simulated client via `172.17.0.1:18032`,
    readiness/fail-closed/teardown, image content scan (local), then full
    removal with absence proof (no container/image/listener left;
    `18032` free again);
  - protected-host fact capture before and after (per acceptance 11);
  - never connect to, print, or exercise the protected upstream
    (`18020`) — fake upstreams only; no live Qwen inference.
- Remote (GitHub): CI per workstream C; report records the exact run
  IDs/conclusions for `test`, `gateway-contract`, `docker` on the
  implementation head and the observed state at report time.
- Strategic (independent, post-report): GitHub PR identity/base/head/
  commits/diff; report-only SELF commit with literal implementation SHA
  parent; CI re-check; artifact/manifest hash re-derivation; Docker image
  content re-scan where practical; protected-host re-probe; docs diff
  review; secret scan of the entire PR diff.

## Documentation required

Per F1–F9 and G1–G4 exactly. Additionally: `oap/COMPLETENESS.md` and
`README.md` keep the release-honesty ladder (implemented-and-merged /
real-E2E accepted / Gateway-contract tested / packaged /
deployment-qualified-disposable / cutover NOT performed / NOT released)
current, with the Docker qualification explicitly placed at
"deployment-qualified (disposable/CI environments only)" — NOT
"release-qualified" and NOT "released".

## Safety / security / privacy constraints

- No secret value, credential, provider key, host path, or raw acceptance
  payload may enter the PR, the image, the compose files, the
  documentation, the provenance manifest, or the report. Placeholder
  values only (`<...>` style). The local disposable run uses fake
  credentials that are never recorded.
- Raw prompt/source/image/tool-output logging law unchanged; metrics
  content law unchanged; the C8/C9 image and log scans extend, not weaken,
  the 009/010 scanner list.
- The Docker deployment must not create a path where the adapter is
  anonymously reachable in any supported configuration (A2 law + C6).
- Bounded resource use: CI job within normal wall-time budget; local
  disposable run bounded and fully torn down; no model inference on the
  protected GPU.

## Protected live-host constraints

- Read-only access to the protected fixture; **no mutation** of port 18020,
  `qwen-serving-vision.service`, model/checkpoint/patches/venv, systemd
  production state (no new persistent units), API keys, firewall/VPN/
  network bindings, or active Codex profiles; no linger mutation
  (`Linger` stays `no`); no Gateway deployment created on the host.
- The only runtime activity permitted on the protected host is the D6-
  confined disposable Docker run (loopback + docker0 link-local, fake
  upstream, port 18032, brief, fully torn down with absence proof) and
  image builds. No LAN-exposed listener at any time. No direct-vLLM
  bypass, no inference.
- Any observed protected-fixture drift is a stop-and-report condition
  (recorded in the report), never repaired by coding.

## Local execution capability

Coding may install/use safe routine tooling: Docker Engine 29.1.3 + Compose
v5.0.1 are already present (verified via `sudo -n`), `uv`, Python 3.12,
standard CI tooling. Network access to Docker Hub (base image pulls) and
PyPI is available. Ports 18031–18034 verified free at order time (the
protected-host run uses 18032 only; CI uses 18031 on the disposable runner).
The human is not an operator.

## GitHub workflow

- Start exactly from base `4aa805fdd197938f1f25c9ca034c2e3c3cf2fc87`;
  create branch `oap/011-docker-mvp-release-readiness`.
- Implement, test, push; create exactly one non-draft PR against `main`
  with a truthful description (what changed, evidence summary, non-goals
  honored, known limitations).
- Inspect and fix in-scope CI until all required checks are green; if a CI
  failure reveals an out-of-scope architecture/product decision, report it
  (do not silently expand scope).
- Never merge; never enable auto-merge; publish the immutable report as a
  report-only SELF child commit (changes only
  `oap/reports/011-a-docker-mvp-release-readiness.md`).

## Required report

`oap/reports/011-a-docker-mvp-release-readiness.md` with, at minimum:

- `Implementation head SHA:` (literal 40-hex) and
  `Report publication commit: SELF`;
- PR number/URL, branch, base/head;
- per-workstream evidence A–G with exact command summaries, CI run IDs and
  conclusions (test / gateway-contract / docker) at the implementation head
  and observed at report time;
- rebuilt wheel SHA-256 + size + entry count; manifest v2 regeneration
  facts; base image digest; local image build digest;
- Docker CI evidence details (C2–C9), including the simulated-runtime
  endpoint address class used and the negative-test outcomes;
- local protected-host disposable run facts (port, bind, duration,
  teardown absence proof) and protected before/after facts (acceptance 11);
- explicit statement of any CI/environment capability that could not be
  exercised and its compensating evidence (C11 evidence boundary);
- secret scan result of the PR diff; `uv.lock`/`pyproject.toml` SHA-256
  invariance proof;
- explicit statement: no release/tag/publication performed; no Gateway
  repository mutation; no protected mutation; cutover not performed.

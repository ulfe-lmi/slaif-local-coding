# Deployment and operator contract

Order 009-a, workstream C; restated by order 011-a (two supported paths).
This is the complete operator contract for both supported deployment paths.
Links: [release-artifact policy](RELEASE-ARTIFACT-POLICY.md),
[Docker installation (canonical MVP path)](DOCKER-INSTALL.md),
[Docker security delta (release gate)](DOCKER-SECURITY-DELTA.md),
[cutover/rollback runbook (prepare-only)](RELEASE-CUTOVER-RUNBOOK.md),
[adapter configuration reference](ADAPTER-CONFIGURATION.md).

## 1. Supported paths and justification

Two supported deployment paths exist (order 011-a, strategic decision D3):

1. **Docker container — the canonical MVP installation path** (order 011-a,
   D2; pull-based canonical operator path since order 013-a): a single
   adapter container on **Linux Docker Engine** using `network_mode: host`,
   the non-editable wheel-based runtime image (`Dockerfile`), the canonical
   **pull-based** compose definition (`compose.yaml`, no build key; the
   published MVP release `ghcr.io/ulfe-lmi/slaif-local-coding:0.1.0` by
   default, overridable via `SLAIF_LOCAL_CODING_IMAGE` including the
   digest-pinned form — reference publication PENDING as of this PR's head,
   R18 Gateway-peer hold; until then the qualification override is the only
   available path), the qualification/development build override
   (`compose.build.yaml`, NOT the released-user path), and the final
   Gateway-integrated (signed) configuration. Host networking keeps the Qwen
   hop true host loopback (`127.0.0.1:18020`) in one container while a
   co-located host-namespace Gateway, a bridge-container Gateway, and a
   LAN-different-host Gateway/client all reach the adapter (D1/D2/D4). The
   install host needs no Python, uv, project dependencies, or virtualenv on
   this path. The exact operator procedure is in
   [DOCKER-INSTALL.md](DOCKER-INSTALL.md); this section documents the shared
   path law, and the Docker-specific commands are not duplicated here.
2. **systemd user service — the secondary direct-host path** (order 009-a,
   retained unchanged; including the protected-host cutover path): a systemd
   user service on the local host running the adapter from the
   repository-owned virtual environment, binding loopback port `18031`.

Justification (systemd path, from current source review):

- the adapter is CPU-only and ships one console entry point
  (`slaif-local-coding`, `src/slaif_local_coding/cli.py`) that loads a single
  TOML configuration file and runs one Uvicorn ASGI process — a
  `Type=exec` user unit matches this process model exactly;
- the runtime package is installed into the repository virtual environment
  (`uv sync --frozen`), and the unit executes
  `%h/codex-work/slaif-local-coding/.venv/bin/slaif-local-coding`, keeping the
  deployment reproducible from the locked repository state;
- configuration defaults (`config/adapter.example.toml`) already assume
  loopback `127.0.0.1:18031`, the private upstream on `127.0.0.1:18020/v1`,
  and the protected cache `/dev/shm/slaif-local-coding`, which the unit grants
  via `ReadWritePaths` under `ProtectSystem=strict`.

Path selection is an operator deployment decision; both paths serve the same
runtime wheel under the same configuration law, the same D1 bind law
(loopback default; non-loopback only under the full signed ingress
contract), and the same readiness/ingress fail-closed contract. The
containment classes differ: see
[DOCKER-SECURITY-DELTA.md](DOCKER-SECURITY-DELTA.md).

## 2. Asset set

| Asset | Role |
| --- | --- |
| `Dockerfile` | multi-stage Linux image: locked wheel build (pinned uv) + digest-pinned wheel-based non-root runtime (no repository source, no `oap/`, no `tests/`, no caches) |
| `.dockerignore` | explicit build-context exclusions (OAP transcripts, tests, docs, caches, env/secret files, placeholders) |
| `compose.yaml` | canonical PULL-BASED Docker MVP deployment (no build key; image `ghcr.io/ulfe-lmi/slaif-local-coding:0.1.0` by default, `SLAIF_LOCAL_CODING_IMAGE` override; reference publication PENDING as of this PR's head): `network_mode: host`, hardened (non-root, read-only rootfs, no-new-privileges, cap drop ALL, bounded tmpfs), read-only config mount, mode-0600 `env_file`, bounded `/readyz` healthcheck, no published ports |
| `compose.build.yaml` | qualification/development build override (NOT the released-user path): local image `slaif-local-coding:0.1.0-${SLAIF_GIT_SHA:-local}` plus `build:` (context `.`; args `SLAIF_GIT_SHA`, `SLAIF_WHEEL_SHA256`); the two-file merge equals the pre-013 single-file effective adapter spec for the closed field set (CI-asserted) |
| `packaging/release_record.json` | release record (schema `slaif-release-record-v1`): published digest, image source commit, tags, Git tag reference, publication workflow run id |
| `packaging/release_provenance_manifest.json` (+ schema) | schema-v3 provenance manifest (state-aware; `release` section present iff the record exists) |
| `packaging/slaif-local-coding.service` | systemd user-unit template (loopback-only, hardened, external `EnvironmentFile`) |
| `config/adapter.deployment.template.toml` | **development/local candidate** configuration template (ingress disabled; NOT production) with exactly two documented placeholders |
| `config/adapter.gateway-integrated.template.toml` | **final Gateway-integrated** configuration template (signed ingress v1 + signed-request constitution identity) with exactly two documented placeholders |
| `packaging/readyz-wait.sh` | bounded, fail-closed `/readyz` readiness poll (loopback only) |
| `~/.config/slaif-local-coding/adapter.env` | protected environment file, **mode 0600**, credential values by env name only |
| `~/.config/slaif-local-coding/adapter.toml` | installed configuration file, **mode 0600**, from the template |

`packaging/slaif-local-coding.service.example` is the earlier uninstalled
example retained for continuity; `packaging/slaif-local-coding.service`
supersedes it (installed config path, start-limit protection,
`ProtectProc=invisible`).

Static tests (`tests/test_packaging.py`) assert across all packaging assets
that no secret appears in any unit file, argv, example, template, or document,
that the unit keeps loopback-only networking and the external `EnvironmentFile`,
and that the template contains only the documented placeholders.

## 3. Runtime user/path/permission assumptions

- Runs as the local service user (the user who owns the repository checkout)
  under that user's systemd manager; the user must own the repository.
- Repository checkout at `%h/codex-work/slaif-local-coding` (replace only the
  directory name if it differs; every command below assumes the documented
  location).
- `~/.config/slaif-local-coding/` directory: `0700`; `adapter.env` and
  `adapter.toml`: `0600`. The unit file itself may be `0644` because it
  contains no secrets.
- The `adapter.env` file holds credential **values** referenced by
  environment name only. The three Local-side secret roles, with THREE
  DISTINCT environment names (the configuration validators reject any shared
  name — order 010-a C2), are:
  - `QWEN3090_API_KEY` — protected upstream (Qwen/vLLM) credential (always);
  - `SLAIF_ADAPTER_SERVICE_TOKEN` — Gateway -> Local service credential
    (whenever a `gateway_ingress` mode is enabled);
  - `SLAIF_ADAPTER_SIGNING_SECRET` — Gateway -> Local signed-identity HMAC
    secret (signed mode only).
  The Gateway-only identity-derivation secret is never copied to Local.
  Values are never written into the unit, argv, TOML, examples, or
  documentation, and are never recorded in reports.
- The unit enforces `NoNewPrivileges`, `PrivateTmp`, `ProtectSystem=strict`,
  `ProtectHome=read-only`, `ProtectProc=invisible`, namespace/SUID/realtime
  restrictions, loopback-only `IPAddressAllow`, `UMask=0077`, and bounded
  tasks/memory/file descriptors.

## 4. Install

```bash
# 0. From the repository checkout, with the locked dev environment:
uv sync --frozen --extra dev
uv run --frozen python scripts/artifact_policy_check.py --dist dist --inspect

# 1. Build the supported artifact (the wheel) and inspect it:
uv build
uv run --frozen python scripts/artifact_policy_check.py --dist dist --inspect

# 2. Unit:
install -m 0644 packaging/slaif-local-coding.service \
  "$HOME/.config/systemd/user/slaif-local-coding.service"
systemctl --user daemon-reload

# 3. Environment file (mode 0600): credential values by env name only.
install -d -m 0700 "$HOME/.config/slaif-local-coding"
umask 077
{
  echo "QWEN3090_API_KEY=<protected upstream credential>"
} > "$HOME/.config/slaif-local-coding/adapter.env"
chmod 0600 "$HOME/.config/slaif-local-coding/adapter.env"

# 4. Configuration from the documented template: substitute ONLY the two
# documented placeholders, no other manual editing. For the development/local
# candidate use config/adapter.deployment.template.toml (ingress disabled;
# NOT production). For the final Gateway-integrated configuration use
# config/adapter.gateway-integrated.template.toml (see section 12).
sed -e 's/__UPSTREAM_BASE_URL__/http:\/\/127.0.0.1:18020\/v1/' \
    -e 's/__UPSTREAM_MODEL__/qwen3.8-27b/' \
    config/adapter.deployment.template.toml \
    > "$HOME/.config/slaif-local-coding/adapter.toml"
chmod 0600 "$HOME/.config/slaif-local-coding/adapter.toml"

# 5. Start and wait for readiness (bounded, fail-closed):
systemctl --user start slaif-local-coding.service
packaging/readyz-wait.sh
```

## 5. Startup/readiness ordering

1. The unit `After=network-online.target` is the only dependency ordering; the
   adapter has no database or second local dependency.
2. `Type=exec` reports "started" when the main process has started — **not**
   when the adapter is ready. Operators must poll `/readyz` after every
   start/restart with `packaging/readyz-wait.sh` (default 30 s bounded wait,
   0.5 s interval, loopback only).
3. Fail-closed guidance: if the bounded wait elapses, do **not** send traffic.
   Check `journalctl --user -u slaif-local-coding.service` for the sanitized
   reason, fix the configuration or upstream, and restart. Upstream
   unavailability fails readiness (503), not success; a malformed
   transformation fails with a sanitized 4xx.
4. `/healthz` reports process liveness; `/readyz` additionally requires the
   upstream health check to succeed. Private `/metrics` stays loopback-only.

## 6. Cache/state directories and permissions

- Default protected cache: `/dev/shm/slaif-local-coding`, created by the
  adapter on first use as a `0700` directory with `0600` files; the unit
  grants exactly this path via `ReadWritePaths`.
- XDG fallback: if `[cache].root` is omitted from the configuration, the
  adapter uses the protected XDG user-cache default. In that case the operator
  must add the resolved path to the unit's `ReadWritePaths`, reload, and
  restart.
- The derived cache is disposable and non-authoritative: repository/Git/GitHub
  and full source always override it. Purge/rebuild is safe and is done by
  stopping the service, deleting the cache directory, and starting the
  service again:

```bash
systemctl --user stop slaif-local-coding.service
find /dev/shm/slaif-local-coding -mindepth 1 -delete  # purge only the cache root
systemctl --user start slaif-local-coding.service
packaging/readyz-wait.sh
```

  Purging cannot destroy authoritative project information.

## 7. Logging and privacy

- Logs go to the user journal (`StandardOutput=journal`,
  `SyslogIdentifier=slaif-local-coding`). Inspect with
  `journalctl --user -u slaif-local-coding.service`.
- There are no raw prompts, source, images, tool output, request or
  response bodies, authorization headers, keys, or private URLs in logs
  (`log_raw_payloads` is `false` in the template; the code path does not
  accept raw payloads into logs). Upstream errors are returned as sanitized
  502/503/4xx envelopes; metrics carry only counts/timings/states with
  sanitized labels.
- Operators must not paste journal content containing request material into
  tickets or reports; capture only status codes, sanitized error codes, and
  bounded counts.

## 8. Start/stop/restart/status (exact commands)

```bash
systemctl --user start slaif-local-coding.service     # start
systemctl --user stop slaif-local-coding.service      # stop
systemctl --user restart slaif-local-coding.service   # restart (then poll readiness)
systemctl --user status slaif-local-coding.service    # status
systemctl --user enable slaif-local-coding.service    # start at login (degraded mode A)
systemctl --user disable slaif-local-coding.service   # stop at login
# Unattended boot contract (supported mode B): see section 13.
packaging/readyz-wait.sh                              # bounded readiness poll
journalctl --user -u slaif-local-coding.service -n 100 --no-pager  # bounded logs
```

## 9. Upgrade procedure (supported)

Backups live under `~/.local/state/slaif-local-coding/backups/` — one
timestamped directory per upgrade, all files `0600`:

```
~/.local/state/slaif-local-coding/backups/<UTC>Z/
  adapter.toml        # byte-exact previous configuration (0600)
  adapter-wheel       # byte-exact previous supported wheel artifact (0600)
  inventory.json      # previous-state facts: config/wheel sha256+size,
                      # entry-point path+sha256, cache-root state (0600)
```

Procedure:

1. **Backup the previous configuration and artifact** (exact paths, mode 0600):

   ```bash
   STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
   BK="$HOME/.local/state/slaif-local-coding/backups/$STAMP"
   install -d -m 0700 "$BK"
   install -m 0600 "$HOME/.config/slaif-local-coding/adapter.toml" "$BK/adapter.toml"
   install -m 0600 dist/slaif_local_coding-*.whl "$BK/adapter-wheel"
   ```

2. **Install/replace the exact new artifact**: build the new wheel, pass the
   artifact policy check, install it into the repository venv
   (`uv sync --frozen` from the new locked state, or
   `"$HOME/codex-work/slaif-local-coding/.venv/bin/pip" install
   --force-reinstall <new-wheel>` for a pre-built drop), and replace
   `adapter.toml` only if the new release changes the documented template
   (re-substitute the same two placeholders; no other edits).

3. **Restart**: `systemctl --user restart slaif-local-coding.service` and
   poll readiness with `packaging/readyz-wait.sh`.

4. **Verify readiness + contract smoke**: `/healthz` 200, `/readyz` 200,
   `/v1/models` passthrough 200, and one representative non-streaming
   `/v1/responses` request returning the expected sanitized 200 envelope.

5. **Confirm or roll back**: if the smoke passes, record the new
   `inventory.json` facts and keep the backup for one subsequent release
   (then it may be deleted by the operator). If it fails, execute the rollback
   below and keep the service on the previous artifact.

Upgrade invariants: the intended configuration is preserved byte-for-byte
unless the release template changes; the derived cache is disposable and is
never migrated — after an upgrade the cache root state must be unchanged or
rebuildable by purge; no unrelated host state is touched.

## 10. Rollback procedure (supported)

Mechanical restore of the exact previous artifact and configuration from the
backup directory created in step 9.1:

```bash
BK="$HOME/.local/state/slaif-local-coding/backups/<UTC>Z"   # the chosen backup
systemctl --user stop slaif-local-coding.service
install -m 0600 "$BK/adapter.toml" "$HOME/.config/slaif-local-coding/adapter.toml"
"$HOME/codex-work/slaif-local-coding/.venv/bin/pip" install --force-reinstall "$BK/adapter-wheel"
systemctl --user start slaif-local-coding.service
packaging/readyz-wait.sh
```

Post-rollback verification: `/healthz` 200, `/readyz` 200, `/v1/models` 200,
and one representative non-streaming `/v1/responses` request 200. Verify the
restored configuration is byte-identical to the backup
(`sha256sum` comparison) and the restored entry point matches the backup
inventory. If any check fails, the service must be left stopped and the
incident reported; do not loop restarts beyond the unit start limit.

## 11. Uninstall/disable

Remove only package-owned files/units; preserve the external model service,
the Gateway, and any explicitly retained configuration:

```bash
systemctl --user disable --now slaif-local-coding.service
rm "$HOME/.config/systemd/user/slaif-local-coding.service"
systemctl --user daemon-reload
rm "$HOME/.config/slaif-local-coding/adapter.toml" \
   "$HOME/.config/slaif-local-coding/adapter.env"   # only if not explicitly retained
find /dev/shm/slaif-local-coding -mindepth 1 -delete   # optional cache purge
```

Uninstalling must never touch the protected upstream model service, its unit,
model/venv/patches, API-key files, firewall/VPN/network state, or any Codex
profile. If the appliance user's linger state was changed by the supported
procedures (section 13), restore the pre-procedure linger state as part of
uninstall (the change is documented, reversible, and verified).

## 12. Gateway-integrated deployment configuration (order 010-a)

The **final Gateway-integrated configuration** is created from
`config/adapter.gateway-integrated.template.toml`. It is the only supported
configuration for the Gateway-integrated cutover (see
[TOPOLOGY.md](TOPOLOGY.md) for the transport decision). The
disabled-ingress template remains the **development/local candidate (NOT
production)**; a development configuration must never be labeled production
(the labels are mechanically checked by `tests/test_gateway_integrated_deployment.py`).

Differences from the development template:

- `[gateway_ingress]` `mode = "service_bearer_signed_identity_v1"` with
  `service_token_env = "SLAIF_ADAPTER_SERVICE_TOKEN"`,
  `signing_secret_env = "SLAIF_ADAPTER_SIGNING_SECRET"`, and the fixed
  accepted contract values (`identity_version = "v1"`,
  `policy_version = "signed-identity-v1"`, `clock_skew_seconds = 60`,
  `replay_ttl_seconds = 60`, `max_replay_entries = 4096`,
  `nonce_min_length = 16`, `nonce_max_length = 128`);
- `[constitution]` `enabled = true` with
  `identity_source = "signed_request"` and **no** static
  principal/session/repository labels (the validators forbid coexistence);
- `[compiler]` `enabled = true` (direct compiler calls; required by the
  constitution integration);
- the designated route sets `observation_enabled = true` and
  `constitution_enabled = true`.

Install procedure (delta against section 4):

```bash
# Environment file with the THREE DISTINCT secret roles (mode 0600, values
# referenced by environment name only, never recorded):
install -d -m 0700 "$HOME/.config/slaif-local-coding"
umask 077
{
  echo "QWEN3090_API_KEY=<protected upstream credential>"
  echo "SLAIF_ADAPTER_SERVICE_TOKEN=<gateway-to-adapter service credential>"
  echo "SLAIF_ADAPTER_SIGNING_SECRET=<gateway-to-adapter signing secret>"
} > "$HOME/.config/slaif-local-coding/adapter.env"
chmod 0600 "$HOME/.config/slaif-local-coding/adapter.env"

# Configuration from the Gateway-integrated template: substitute ONLY the two
# documented placeholders, no other manual editing.
sed -e 's/__UPSTREAM_BASE_URL__/http:\/\/127.0.0.1:18020\/v1/' \
    -e 's/__UPSTREAM_MODEL__/qwen3.8-27b/' \
    config/adapter.gateway-integrated.template.toml \
    > "$HOME/.config/slaif-local-coding/adapter.toml"
chmod 0600 "$HOME/.config/slaif-local-coding/adapter.toml"

# Start and wait for readiness (bounded, fail-closed):
systemctl --user start slaif-local-coding.service
packaging/readyz-wait.sh
```

Readiness contract: with signed ingress, `/readyz` reports
`gateway_ingress = "ready"` only when **both** the service credential and
the signing secret are available (fail closed — the service cannot serve the
Gateway ingress, and the cutover runbook treats readiness failure as a
rollback trigger).

## 13. Boot contract and user-manager linger (order 010-a)

The supported appliance boot contract is **unattended operation (mode B)**:
the appliance user has user-manager linger enabled, so the adapter user
service starts at boot without any login session. Without linger the
documented degraded **mode A** applies: the service starts at login only.

Supported procedure (each step documented, reversible, and verified; executed
only by the human-authorized cutover order, never by this repository):

```bash
# Enable linger for the appliance user only (reversible):
sudo loginctl enable-linger "$APPLIANCE_USER"
# Verify the resulting state (must read Linger=yes):
loginctl show-user "$APPLIANCE_USER" -p Linger
# Restore the previous state when required (e.g. uninstall), then verify:
sudo loginctl disable-linger "$APPLIANCE_USER"
loginctl show-user "$APPLIANCE_USER" -p Linger
```

What happens without linger (degraded mode A): the service unit is still
`WantedBy=default.target`, so it starts when the appliance user logs in; it
does **not** start at boot in a headless/unattended situation. Operators
detect the mode with `loginctl show-user <user> -p Linger` (`yes` = mode B,
`no` = mode A); `scripts/boot_contract.py --inspect` prints the closed
classification. Upgrade, rollback, and uninstall procedures manage linger
explicitly: install verifies the intended mode, upgrade and rollback leave
it unchanged, and uninstall restores the pre-procedure state (section 11).

This objective records the host baseline only (read-only): the appliance
user's linger state at qualification time is `no` (mode A) and is **not**
changed by this objective; enabling linger is part of the separately
authorized cutover.

## 14. Qualification boundary (order 011-a, D6 split)

Deployment qualification is disposable and split by environment:

- **GitHub runner (disposable, not a protected host):** the mandatory
  `docker` CI job proves the canonical-port (`18031`) containerized
  qualification — build, start, readiness, signed-request evidence from a
  separate bridge-network namespace (simulated Gateway runtime),
  negative/contract evidence, fail-closed readiness, image content/
  hardening/label scans, and stop/start/recreate/upgrade/rollback operations —
  all against fake loopback upstreams, with a teardown absence proof. The
  `docker-published` CI job (order 013-a) additionally proves the
  PUBLISHED-image path once `packaging/release_record.json` carries a
  non-null digest: pull by digest and by both tags (each resolving to the
  recorded digest), the exact OCI label set, the full signed-ingress
  contract against a disposable fake upstream on the canonical port via the
  pull-based compose only, the no-build proof, and the teardown absence
  proof.
- **Protected host (read-only fixture):** only a D6-confined disposable
  container run is permitted: bind `172.17.0.1` (docker0 link-local only,
  **no LAN-exposed listener at any time**) on port `18032`, signed ingress
  enabled, three-role mode-0600 env file (fake values, never recorded),
  fake upstream on loopback, readiness/fail-closed, image content scan, and
  full removal with an absence proof (no container/image/listener left).
- **systemd path:** `scripts/disposable_deployment_qualification.py`
  (unchanged objective-009/010 boundary: transient uniquely named unit,
  fully removed with proof).

No persistent unit or container of any host is installed or enabled by the
repository; no protected service is touched by either environment. The live
cutover itself remains the separate, human-authorized final act described in
[RELEASE-CUTOVER-RUNBOOK.md](RELEASE-CUTOVER-RUNBOOK.md).

## 15. Docker path procedures (exact link)

The Docker install, upgrade, rollback, cache-purge, and uninstall procedures
are documented **exactly once** in
[DOCKER-INSTALL.md](DOCKER-INSTALL.md) (canonical MVP path; the PRIMARY
operator path is PULL-BASED — sections 1–10 of that document, matching
`compose.yaml` behavior command-for-command; the build-from-source
qualification/development path is clearly separated). This section
deliberately does not duplicate those command sequences. The Docker path uses:

- the final Gateway-integrated template
  (`config/adapter.gateway-integrated.template.toml`) with the
  `__LISTEN_HOST__` placeholder resolved to the site bind value;
- a mode-0600 environment file holding the three distinct Local-side secret
  roles by env name only (`QWEN3090_API_KEY`,
  `SLAIF_ADAPTER_SERVICE_TOKEN`, `SLAIF_ADAPTER_SIGNING_SECRET`);
- the bounded compose healthcheck against `/readyz` (the documented
  equivalent of `packaging/readyz-wait.sh` for the Docker path; the host
  loopback poll also works because host networking makes the container
  loopback the host loopback);
- the D1 bind law: loopback `127.0.0.1` by default; `0.0.0.0`/interface IP
  only under the full signed ingress mode the template carries.

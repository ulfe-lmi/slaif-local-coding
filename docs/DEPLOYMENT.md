# Deployment and operator contract

Order 009-a, workstream C. This is the single supported deployment path and its
complete operator contract. Links: [release-artifact policy](RELEASE-ARTIFACT-POLICY.md),
[cutover/rollback runbook (prepare-only)](RELEASE-CUTOVER-RUNBOOK.md),
[adapter configuration reference](ADAPTER-CONFIGURATION.md).

## 1. Supported path and justification

Exactly one primary supported deployment path exists for this objective:
**a systemd user service on the local host running the adapter from the
repository-owned virtual environment**, binding loopback port `18031`.

Justification from current source review:

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
  via `ReadWritePaths` under `ProtectSystem=strict`;
- there is no OCI/Compose support in the repository, and adding a second
  deployment system is an explicit non-goal of this objective.

## 2. Asset set

| Asset | Role |
| --- | --- |
| `packaging/slaif-local-coding.service` | systemd user-unit template (loopback-only, hardened, external `EnvironmentFile`) |
| `config/adapter.deployment.template.toml` | configuration template with exactly two documented placeholders |
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
  environment name only — `QWEN3090_API_KEY` (protected upstream credential)
  and, only when a `gateway_ingress` mode is enabled,
  `SLAIF_ADAPTER_SERVICE_TOKEN`. Values are never written into the unit, argv,
  TOML, examples, or documentation, and are never recorded in reports.
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
# documented placeholders, no other manual editing.
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
systemctl --user enable slaif-local-coding.service    # start at login
systemctl --user disable slaif-local-coding.service   # stop at login
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
profile.

## 12. Qualification boundary

This objective qualifies the deployment mechanics in a disposable environment
against fake loopback upstreams only (see `scripts/disposable_deployment_qualification.py`
and the order's workstream D). No persistent unit of this host is installed or
enabled by the objective; any unit used for qualification is transient,
uniquely named, and fully removed with proof. The live cutover itself remains
the separate, human-authorized final act described in
[RELEASE-CUTOVER-RUNBOOK.md](RELEASE-CUTOVER-RUNBOOK.md).

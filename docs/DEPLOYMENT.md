# Deployment and operations

**Docker is the primary path.** Follow [INSTALL.md](../INSTALL.md) for the
complete pull-based installation and lifecycle commands, or
[QUICKSTART.md](../QUICKSTART.md) for the shortest path. Docker hosts need no
Python, uv or project environment. The
[Docker reference](DOCKER-INSTALL.md) explains networking and containment.

This document covers shared operational rules and the secondary **direct-host
systemd user service**. The two paths use the same adapter but have different
[security boundaries](DOCKER-SECURITY-DELTA.md).

## Shared operational rules

- Deploy an exact recorded artifact with configuration from its recorded source.
- Keep the Gateway and model service separate. Public clients use the Gateway;
  signed ingress authenticates its requests to the private adapter.
- Wait for `/readyz` after every start or restart. `/healthz` proves only process
  liveness. Missing ingress credentials or an unavailable upstream fail readiness.
- There are no raw prompts, source, images, tool output, bodies or credentials
  in application logs. Inspect only sanitized status/error/count information.
- Preserve previous artifact, configuration and dependency-lock identities for
  rollback. Derived cache state is disposable and never authoritative.
- Installation does not authorize changing an existing model service, Gateway
  routing, firewall, network or active client profile. Protected cutover follows
  the [separate runbook](RELEASE-CUTOVER-RUNBOOK.md).

## Direct-host prerequisites

Use Linux with a working systemd user manager, Python 3.12, pinned uv and a
checkout at the exact recorded Git commit. The supplied unit assumes
`$HOME/codex-work/slaif-local-coding`, owned by the service user. If using another
path, update both `WorkingDirectory` and `ExecStart` before installation.

The unit enforces loopback networking. Use a colocated Gateway runtime with a
reachable loopback backend, not a remote Gateway or its bridge-container
loopback. Do not run Docker and systemd adapters on the same port.

The service uses:

| Path | Purpose |
| --- | --- |
| `.venv/bin/slaif-local-coding` | Installed adapter entry point. |
| `~/.config/slaif-local-coding/adapter.toml` | Protected configuration, mode 0600. |
| `~/.config/slaif-local-coding/adapter.env` | Protected credentials, mode 0600. |
| `/dev/shm/slaif-local-coding` | Disposable compiled cache, directory mode `0700`. |
| `~/.config/systemd/user/slaif-local-coding.service` | Unit, mode `0644`, no credential values. |

## Install the wheel and unit

Run from the exact source checkout. Build and inspect the wheel, verify its
SHA-256 against the provenance, then install it non-editable over the frozen
runtime dependency environment:

```bash
uv sync --frozen --extra dev
uv build
uv run --frozen python scripts/artifact_policy_check.py --dist dist --inspect
sha256sum dist/*.whl
# Continue only when the wheel hash matches the recorded artifact.
uv sync --frozen --no-dev --no-install-project
uv pip install --python .venv/bin/python --no-deps --force-reinstall \
  dist/slaif_local_coding-0.1.0-py3-none-any.whl

install -d -m 0700 "$HOME/.config/slaif-local-coding"
install -d -m 0755 "$HOME/.config/systemd/user"
install -d -m 0700 /dev/shm/slaif-local-coding
install -m 0644 packaging/slaif-local-coding.service \
  "$HOME/.config/systemd/user/slaif-local-coding.service"
systemd-analyze --user verify "$HOME/.config/systemd/user/slaif-local-coding.service"
systemctl --user daemon-reload
```

Do not use a later `uv run` or editable synchronization to start the installed
service: the unit invokes the installed entry point directly. If the cache
uses a configured fallback path, add that exact protected path to the unit's
`ReadWritePaths` before starting. The default tmpfs directory must exist when
the unit starts; provision it again after a host reboot if absent.

## Gateway-integrated configuration

Use `config/adapter.gateway-integrated.template.toml`. It enables service Bearer
plus signed identity v1, signed-request governance identity, compiler and the
observed/governed route. `config/adapter.deployment.template.toml` is a
**development-only, not production** alternative with ingress disabled.

Load the three values from your protected store into the named shell variables;
never enter literal credentials in shell history. Then create the files:

```bash
: "${QWEN3090_API_KEY:?load the upstream credential}"
: "${SLAIF_ADAPTER_SERVICE_TOKEN:?load the service credential}"
: "${SLAIF_ADAPTER_SIGNING_SECRET:?load the signing secret}"
umask 077
{
  printf 'QWEN3090_API_KEY=%s\n' "$QWEN3090_API_KEY"
  printf 'SLAIF_ADAPTER_SERVICE_TOKEN=%s\n' "$SLAIF_ADAPTER_SERVICE_TOKEN"
  printf 'SLAIF_ADAPTER_SIGNING_SECRET=%s\n' "$SLAIF_ADAPTER_SIGNING_SECRET"
} > "$HOME/.config/slaif-local-coding/adapter.env"
sed -e 's|__UPSTREAM_BASE_URL__|http://127.0.0.1:18020/v1|' \
    -e 's|__UPSTREAM_MODEL__|qwen3.8-27b|' \
    -e 's|__LISTEN_HOST__|127.0.0.1|' \
    config/adapter.gateway-integrated.template.toml \
    > "$HOME/.config/slaif-local-coding/adapter.toml"
chmod 0600 "$HOME/.config/slaif-local-coding/adapter.env" \
  "$HOME/.config/slaif-local-coding/adapter.toml"
systemctl --user start slaif-local-coding.service
packaging/readyz-wait.sh
```

Use upstream/model values matching your installation. All three placeholder
substitutions are required. Service and signing values must match the Gateway;
the Gateway-only identity-derivation secret must not be copied to Local.
See [configuration](ADAPTER-CONFIGURATION.md) for secret grammar and bounds.

## Start, stop, restart and status

```bash
systemctl --user start slaif-local-coding.service
systemctl --user stop slaif-local-coding.service
systemctl --user restart slaif-local-coding.service
systemctl --user status slaif-local-coding.service
packaging/readyz-wait.sh
journalctl --user -u slaif-local-coding.service -n 100 --no-pager
```

`Type=exec` means the process started, not that it is ready. The readiness helper
waits for a bounded interval and fails closed. On timeout, keep traffic away,
inspect the sanitized error and correct the cause before restarting.

## Boot and user-manager linger

Unattended operation (**mode B**) requires an enabled unit and user-manager
linger. Without linger, degraded **mode A** starts at login only. Capture the
baseline first; changing linger affects the user's other services too.
Provision the tmpfs cache directory before the unit starts after reboot.

```bash
APPLIANCE_USER="$(id -un)"
loginctl show-user "$APPLIANCE_USER" -p Linger
# For deliberately selected unattended operation:
sudo loginctl enable-linger "$APPLIANCE_USER"
loginctl show-user "$APPLIANCE_USER" -p Linger  # expect Linger=yes
systemctl --user enable slaif-local-coding.service
# Restore only if the captured pre-install state was disabled:
sudo loginctl disable-linger "$APPLIANCE_USER"
loginctl show-user "$APPLIANCE_USER" -p Linger
```

The restore commands are an alternative for rollback/uninstall, not the next
installation step. Upgrade and rollback preserve the chosen linger mode;
uninstall restores the pre-procedure state. Do not change a protected host's
boot settings without its separate authorization.

## Upgrade procedure

1. Preserve the previous valid wheel **with its `.whl` filename**, source commit,
   `uv.lock`, configuration and unit in a mode-`0700` backup directory. Store
   files with mode `0600`; record hashes and the existing linger state.
2. Stop the adapter. Obtain the next exact reviewed source, build/inspect its
   wheel and verify the recorded hash as above. Synchronize its frozen runtime
   dependencies, then install that wheel with `uv pip install --no-deps`.
3. Reconcile configuration against the new template. Preserve credentials and
   intended route settings; do not carry unresolved template placeholders.
4. Restart, run `packaging/readyz-wait.sh`, and verify health plus a bounded signed
   request through the Gateway, including normal tool/stream behavior as needed.
5. Keep the previous artifact and lock until the upgrade is accepted. If a gate
   fails, execute rollback once and record the sanitized failure.

## Rollback procedure

Stop the adapter and restore the **previous source/lock and exact wheel**,
configuration and unit from the backup. Synchronize the previous frozen runtime
dependencies and reinstall that wheel with the same non-editable commands used
for installation. Restoring just the product wheel can leave incompatible newer
dependencies behind. Reload the user manager if the unit changed, start and
check readiness and the Gateway smoke. Verify restored hashes against the backup.
If restoration fails, leave the adapter stopped; do not loop restarts or alter
the protected model service.

## Cache purge

Stop the adapter before removing derived cache entries. Confirm this is the
configured adapter-owned directory and not a symlink or unrelated path:

```bash
systemctl --user stop slaif-local-coding.service
find /dev/shm/slaif-local-coding -mindepth 1 -delete
systemctl --user start slaif-local-coding.service
packaging/readyz-wait.sh
```

The cache directory itself stays in place for the unit. Purging loses
optimization and process-local context, not authoritative repository data.

## Uninstall/disable

```bash
systemctl --user disable --now slaif-local-coding.service
rm "$HOME/.config/systemd/user/slaif-local-coding.service"
systemctl --user daemon-reload
```

Remove only adapter-owned configuration/environment files, cache and environment
if they are no longer needed; retain selected backups securely. Restore the
captured linger state when appropriate. Leave the Gateway, model service,
model weights, upstream credentials, network and client profiles untouched.

## Qualification scope

CI uses disposable Docker hosts and fake upstreams for deployment, lifecycle,
signed ingress, readiness, artifact and teardown checks. Published-image
qualification pulls the recorded digest; systemd qualification uses a uniquely
named transient unit. These tests are not protected-host cutover evidence.
See [TESTING.md](../TESTING.md), [artifact policy](RELEASE-ARTIFACT-POLICY.md)
and [the cutover runbook](RELEASE-CUTOVER-RUNBOOK.md).

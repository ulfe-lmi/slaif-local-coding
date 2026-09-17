# Docker security delta review (release gate, order 011-a)

This document is the release-gate comparison between the Docker MVP
deployment (the canonical MVP installation path added by objective 011) and
the previously qualified systemd user-service containment. It records the
strategic decisions D1–D8 of order `011-a` as the authority for the delta.
It is a review document, not new mechanism: no runtime, configuration, or
network behavior is introduced beyond what `Dockerfile`, `compose.yaml`,
`.dockerignore`, the D1 binding law in `src/slaif_local_coding/config.py`,
and the existing ingress/readiness law already implement.

The two paths are **different containment classes**. This deployment is
**not claimed security-equivalent** to the systemd path. Where they differ,
the delta, the compensating control, and the accepted threat are stated
explicitly below.

## D1'. What isolation is lost versus the qualified systemd containment

Directive-by-directive comparison against
`packaging/slaif-local-coding.service` (the qualified systemd containment):

| systemd containment | Docker path | Consequence |
| --- | --- | --- |
| `IPAddressDeny=any` + `IPAddressAllow=127.0.0.0/8` `::1/128` (kernel-level loopback-only egress/ingress) | `network_mode: host` (strategic decision D2): the container shares the host network namespace; **Docker network-namespace isolation is removed by design** | The container can address every host interface (the declared trusted private LAN) and host loopback, including the protected vLLM port `18020`. This is the accepted single-host MVP reach (D4' below). The application-level D1 binding law still constrains the adapter bind address, but the kernel no longer enforces loopback-only reach for the process. |
| `ProtectSystem=strict` (root filesystem read-only except declared `ReadWritePaths`) | `read_only: true` root filesystem (compose) with bounded tmpfs mounts for `/tmp` and `/dev/shm` | Equivalent in effect: the image root filesystem is read-only; the only writable state is the bounded tmpfs scratch/cache. No `ReadWritePaths`-style path allowlisting exists in Docker; the tmpfs bounds play that role. |
| `ProtectHome=read-only` (home tree read-only) | No host filesystem is mounted at all except the single read-only configuration bind (`:ro`) | Stronger in effect: the Docker container sees no host home tree at all. |
| `ProtectProc=invisible` | No equivalent directive; the container sees the host `/proc` via the shared namespace (host networking does not hide `/proc`; the container mounts its own `/proc` for its PID namespace) | Different PID namespace: the container sees only its own processes, so it cannot inspect host processes via `/proc`. Accepted: the container is single-purpose (one adapter process). |
| `RestrictNamespaces=true`, `LockPersonality=true`, `RestrictSUIDSGID=true`, `RestrictRealtime=true` | `no-new-privileges:true` + `cap_drop: [ALL]` + non-root user (fixed uid/gid created in the image); no `privileged`, no Docker socket mount | Partial compensation: capability/privilege escalation is blocked, but the specific namespace/SUID/realtime restrictions of systemd have no direct Docker compose equivalent. The unprivileged user plus dropped capabilities is the accepted compensation for a single-process adapter. |
| `PrivateTmp=true` | Bounded tmpfs for `/tmp` (`size=64m`) in compose | Equivalent in effect (private, bounded, disposable). |
| `UMask=0077`, `LimitNOFILE=4096`, `TasksMax=128`, `MemoryMax=1G` | No direct compose equivalents (Docker does not expose per-container `TasksMax`/`MemoryMax` without additional limits; the MVP compose sets none) | Accepted gap: resource exhaustion of a single container is bounded by the host and by the application's own finite bounds (bounded bodies, bounded cache, bounded concurrency). A future hardening order may add `mem_limit`/`pids_limit`. |
| Kernel-level loopback-only **bind** (`IPAddressAllow`) | D1 binding law (application-level): non-loopback bind is legal **if and only if** `gateway_ingress.mode = "service_bearer_signed_identity_v1"` | The binding constraint moved from kernel to application validation. The fail-closed configuration validator and the fail-closed readiness gate enforce it; there is no kernel backstop. This is the deliberate, recorded strategic change (D1, human-mandated) that makes the LAN-visible MVP possible. |

Additionally, host networking means the container's ports are the host's
ports: the adapter listens directly on host port `18031`. There is no Docker
port-preservation layer; the D1 binding law and the absence of any published
`ports:` section in `compose.yaml` are the only controls on what address
class `18031` is reachable from.

## D2'. What application invariants remain

These invariants are unchanged by the Docker path and remain mechanically
enforced:

- **Signed ingress is mandatory in every non-loopback configuration** (D1
  binding law, `Settings.binding_law`): a non-loopback `listen_host` without
  `service_bearer_signed_identity_v1` is rejected at configuration time.
- **Full signed identity v1 contract**: service Bearer + HMAC-signed identity
  v1 + replay protection, with the fixed accepted contract values enforced by
  the configuration validators; the authentication/integrity contract is
  unchanged and remains mandatory (D1).
- **Fail-closed readiness**: `/readyz` returns 503 with
  `gateway_ingress = "unavailable"` when the service credential or the
  signing secret is missing; the service starts but must not be trusted
  (the compose healthcheck reports unhealthy).
- **Qwen hop is true host loopback**: `network_mode: host` keeps
  `127.0.0.1:18020` a genuine host-loopback hop inside one container (D2).
- **No anonymous endpoint**: every supported private proxy endpoint
  (`/health`, `/v1/models`, `/v1/responses`, `/v1/chat/completions`) requires
  the service credential in every ingress-enabled configuration; the only
  unsigned surface is the loopback development mode (ingress disabled), which
  is explicitly labeled development-only.
- **Bounded bodies, bounded JSON depth, no raw-content logging, sanitized
  errors, and counts/timings-only metrics** (unchanged law).
- **Distinct secret roles**: the three Local-side secret roles must use three
  distinct environment names (order 010-a C2 invariant, unchanged).
- **The adapter never logs or exposes raw prompts, source, images, tool
  output, request/response bodies, credentials, or keys** (unchanged law).

## D3'. What compensating controls are added

The Docker path adds these container-level controls (asserted mechanically by
the `docker` CI job and by the local disposable run):

- dedicated **non-root** user (fixed uid/gid created in the image; the
  container runs as that user);
- **read-only root filesystem** (`read_only: true`);
- **`no-new-privileges`** (`security_opt: no-new-privileges:true`);
- **all capabilities dropped** (`cap_drop: [ALL]`);
- **no** privilege escalation flag, **no** Docker socket mount, **no**
  repository source bind mount as the production runtime (the runtime is the
  non-editable wheel install; the image contains no `src/`, no `oap/`, no
  `tests/`, no `.git`, no caches, no placeholder files);
- **bounded tmpfs** for `/tmp` (64m) and `/dev/shm` (256m); the protected
  derived cache root `/dev/shm/slaif-local-coding` lands on the bounded tmpfs,
  so the derived cache is disposable by construction;
- the **only** mounted state is the instantiated configuration, mounted
  **read-only** (`:ro`);
- **`restart: unless-stopped`** policy;
- in-image **provenance proof** (B8): the installed distribution is
  non-editable, lives in the venv site-packages, and its retained wheel
  hash equals the committed provenance-manifest wheel hash.

## D4'. Accepted threats for the single-host MVP

Explicitly enumerated and accepted:

1. **Docker administrators and host root are within the trust boundary.**
   Anyone who can operate Docker on the host can inspect the container's
   environment (the three secret values), its filesystem, and its network
   namespace. The secret values therefore rest on host trust, exactly as the
   mode-0600 `adapter.env` already rests on host user trust in the systemd
   path.
2. **A compromised adapter container can reach every host interface
   (the declared trusted private LAN) and host loopback, including the
   protected vLLM port `18020`.** Its network reach is no greater than the
   host itself (host networking), but it is greater than the systemd
   containment's kernel-enforced loopback-only reach. A compromise of the
   adapter process is assumed capable of reading its own environment and
   therefore of using the upstream credential against `127.0.0.1:18020`;
   that is accepted as the cost of the host-loopback Qwen hop in one
   container (D2).
3. **Request confidentiality over the LAN relies on the trusted-private-LAN
   boundary** (strategic decision D4): the LAN-visible surface carries
   request content without TLS on the declared single unencrypted RFC1918
   LAN. The compensating controls are the service Bearer + HMAC-signed
   identity + replay protection (authenticity, integrity, anti-replay), the
   no-anonymous-surface rule, and fail-closed readiness. TLS termination in
   front of the adapter is an operator option explicitly out of scope for
   the MVP.
4. **`/healthz`, `/readyz`, and `/metrics` share the adapter socket.** On a
   LAN-visible bind they are reachable from the same trusted surface and
   expose state/counts only (no raw content). This is accepted and
   documented; no runtime change to the metrics endpoint is made by this
   objective.

## D5'. Secret-path analysis

- **Image layers**: no secret is baked into any layer. The Dockerfile uses
  only non-secret build ARGs (Git SHA, package version, Gateway peer SHA,
  wheel SHA-256, created stamp). There is no `ENV` secret and no build-ARG
  secret (B10).
- **Build arguments**: none carry credentials; the wheel hash is a
  non-secret artifact fact.
- **Compose interpolation / rendered configuration**: the compose file
  references the environment file by path only (`env_file`); no secret value
  appears in any interpolation default or in the rendered configuration. The
  three secret roles enter the container only through the mode-0600 host
  environment file.
- **Inspectable container environment**: the three secret values are visible
  to host Docker group/root via `docker inspect`/exec. This is **accepted**
  (threat 1); the environment file is mode-0600 on the host and never enters
  Git, the image, logs, or documentation.
- **Logs**: no secrets by the logging law (raw-payload logging is disabled
  and not configurable; upstream errors are sanitized; metrics carry only
  counts/timings/states).
- **Mounted files**: the configuration is non-secret (placeholders resolve to
  addresses and model names; secret roles are referenced by environment name
  only); the environment file is mode-0600 on the host and mounted into the
  container's environment, not as a readable file path.

## D6'. Compromised-container network reach and the non-equivalence statement

A compromised adapter container with host networking can reach:

- **all host interfaces** (the declared trusted private LAN, unencrypted,
  single RFC1918 /24);
- **host loopback**, including the protected vLLM service on `127.0.0.1:18020`
  and any other loopback listener on the host;
- any service reachable from the host on the LAN.

This is **not** claimed security-equivalent to the systemd path: the systemd
containment kernel-enforces loopback-only network reach
(`IPAddressDeny=any` + loopback `IPAddressAllow`) and a stricter set of
process restrictions, while the Docker path trades that kernel backstop for
the human-mandated LAN-visible surface under the D1 signed-contract binding
law and the D4 trusted-LAN confidentiality boundary. The loopback-only /
stronger-containment requirement and the human LAN-visible requirement
conflict; the conflict is resolved by D1 (full signed ingress contract
mandatory for any non-loopback bind) plus D4 (declared trusted-private-LAN
boundary), and is documented here as an **accepted MVP limitation** of the
single-host MVP deployment.

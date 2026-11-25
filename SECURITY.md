# Security policy

## Trust boundary

The adapter is high-trust middleware: it can observe prompts, repository text,
tool outputs, images, and model responses. Treat every raw payload as sensitive.

## Non-negotiable rules

1. No raw prompt, source file, image, tool output, request body, response body,
   authorization header, API key, cookie, private URL, or compiled constitution
   source is logged by default.
2. External gateway keys terminate at SLAIF API Gateway. The adapter receives a
   signed/opaque principal plus an internal service credential; raw external
   keys are not cache identifiers.
3. Cache keys include tenant/principal, session/repository discriminator,
   source hash, compiler version, and model/policy version. Cross-tenant reuse
   is forbidden.
4. Compiler calls have no tools, network, filesystem, gateway credential, or
   recursion through the adapter. Input is treated as untrusted data; output is
   strict bounded structured data.
5. Constitutional optimization must never silently delete governance because
   compilation or cache preparation failed. Legacy profile: it fails open to
   the semantically original request when safe. V1 profile: an admitted
   required-preparation failure follows the explicit typed-rejection contract
   (503/409/422) and never falls back to hidden originals.
6. Image-limit enforcement fails closed when a request exceeds a route's hard
   physical image limit and cannot be safely transformed. The designated Codex
   vision route may use explicit `retain_newest` policy.
7. vLLM is private. Public traffic reaches it only through the API Gateway and
   adapter. Internal endpoints, metrics, compiler channel, and upstream key are
   not public.
8. Request/response header forwarding uses an allow/deny policy; hop-by-hop
   headers and untrusted internal identity headers are removed.
9. Cache content is bounded, permission-restricted, TTL-controlled, and
   disposable (legacy profile). Deletion cannot destroy authoritative
   project information. The only approved original-source retention is
   the narrow protected per-session recovery/evidence store of the
   explicitly opted-in v1 profile, described in the exception below.
10. Never mutate the live Qwen installation, model files, systemd service,
    firewall, VPN, API key, or active Codex provider/profile path unless an
    active OAP order explicitly authorizes that exact operation and rollback.
11. Optional gateway ingress uses a configured service Bearer secret with
    constant-time comparison. Signed v1 mode additionally verifies a separate
    bounded HMAC secret over method/path/raw-query-hash/exact-body-hash and
    opaque identity fields, then reserves only a nonce digest in bounded
    process-local replay state. Retention is the maximum of admission time plus
    the configured TTL and the signed request's inclusive timestamp-plus-skew
    horizon. Expired entries are reclaimed only when strictly past that horizon;
    live capacity is never evicted, so exhaustion returns a fixed 503 and unsafe
    wall-clock rollback returns a fixed 503. It never accepts public gateway
    keys or unsigned caller identity headers. Service and signed-auth failures
    occur before image, constitution, compiler, cache, rehydration, or upstream
    work.
    The Gateway contract is continuously checked against the exact peer in
    `tests/fixtures/gateway/current_peer_authority.json`. See
    [the integration contract](docs/SLAIF-GATEWAY-INTEGRATION.md).
    Qualification does not authorize a production deployment or cutover.

## Protected source recovery and evidence retention (narrow exception)

By default, this adapter does not persist raw prompts, source, images, tool
output, request bodies, or response bodies. The human-approved dependency-
bundle cache rework (`docs/CACHE-REWORK.md`) introduces exactly one narrow
exception: under the explicitly opted-in `dependency-bundles-v1` profile, a
protected per-session store may retain the exact observed original source
bundles and their derived metadata for evidence and session recovery.

This exception is not a general permission to log or store bodies:

- **Scope.** Only the exact extracted source bytes of the observed original
  bundles (root source content and file-read content regions) plus the
  necessary provenance, and the derived metadata needed to rebuild RAM
  state. Never environment-context tails, full transport envelopes, whole
  conversations, images, transport credentials, bearer headers, cookies,
  upstream keys, or unrelated tool output.
- **Opt-in and ownership.** Retention is enabled only by explicit operator
  configuration, and it is mandatory for an enabled v1 profile: the profile
  and recovery are enabled together or not at all. One protected namespace
  per coding session; directory mode 0700, file mode 0600, current owner, no
  symlinks or path escapes.
- **Integrity and durability.** Atomic generation publication, integrity
  digests, and fsync of file and directory before any request newly relies
  on a generation. A failed checkpoint aborts that transformation.
- **Credentials.** Transport credentials and credential-bearing wrappers are
  never stored. Detectable forbidden credentials cause typed rejection or
  quarantine without logging content. This is not a complete secret-
  detection guarantee, and the adapter does not silently redact retained
  source and then claim exact fidelity.
- **Access.** Recovery records are read only when an authenticated session
  resumes after a restart, after full binding, configuration, schema, and
  integrity validation. Normal hits never read them, and their content is
  never sent to the main model as a hidden fallback.
- **Retention.** Operator-owned retention and deletion semantics; no
  automatic timed deletion. Where required by deployment, filesystem
  encryption is an explicit prerequisite, not an unimplemented guarantee.

The 020-a protected per-session recovery store is implemented (contract
[docs/CACHE-RECOVERY-CONTRACT.md](docs/CACHE-RECOVERY-CONTRACT.md)) and is
active under the explicitly opted-in `dependency-bundles-v1` profile from
022-c: the resumed and steady-state v1 owners commit
through the accepted 020 owned/fenced admit/checkpoint
path (no raw writer shortcut), and from the 022-d closure
slice the cold bootstrap commits through the same
fenced path as well (the 022-c cold path combined a
direct admit with a separate checkpoint outside the
adverse durable fence, corrected by 022-d; the safe
cleanup of an acquired cold owner/writer runs on
every prepublication failure), and a request newly relies on a protected
generation only after the ACTUAL successful publication of the exact
snapshot the edits rely on — the retained successful publish is bound to
the exact snapshot/epoch it actually published, a faulted publication
keeps the prior bound, and a newer undurable record set is refused (the
fixed typed v1 refusal, no raw fallback forward). The store remains
PENDING strategic review at its bounded scope, and the default
prohibition applies unchanged in the legacy profile. The 022-c marker
key is a distinct application-owned private key carried only as a
PROTECTED ENVIRONMENT REFERENCE (`marker_key_env`): resolved once at v1
runtime construction, held in process memory (repr-suppressed), never a
gateway or service credential, and never persisted, logged or echoed.
The 022-e stable compiled-context region carries a placement-ownership
tag that reuses the SAME application-owned private key material under a
separate MAC domain, bound to the complete trusted namespace, the
endpoint-specific placement and the exact rendered region payload; the
wire form is content-free (versioned kind plus fixed-length MAC) and no
second credential is introduced.
Operational logs and metrics remain content-free in every profile.

## Protected live-host resources

```text
/synology/homes/janezp/qwen-serving
/synology/homes/janezp/.config/systemd/user/qwen-serving.service*
/synology/homes/janezp/.config/qwen38-3090/
port 18020 vLLM service
host firewall/VPN/network rules
model/checkpoint files and vLLM patches
```

Ordinary implementation uses development port `18031` and a repository-local
virtual environment. Passwordless sudo does not waive these protections.

## Vulnerability reporting

Do not publish exploit details or secrets in an issue. Use the repository's
private security-reporting channel after it is configured. Until then, contact
the repository owners through the University of Ljubljana, Faculty of
Electrical Engineering.

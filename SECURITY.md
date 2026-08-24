# Security policy and implementation law

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
5. Constitutional optimization fails open to the semantically original request
   when safe. It must never silently delete governance because compilation
   failed.
6. Image-limit enforcement fails closed when a request exceeds a route's hard
   physical image limit and cannot be safely transformed. The designated Codex
   vision route may use explicit `retain_newest` policy.
7. vLLM is private. Public traffic reaches it only through the API Gateway and
   adapter. Internal endpoints, metrics, compiler channel, and upstream key are
   not public.
8. Request/response header forwarding uses an allow/deny policy; hop-by-hop
   headers and untrusted internal identity headers are removed.
9. Cache content is bounded, permission-restricted, TTL-controlled, and
   disposable. Deletion cannot destroy authoritative project information.
10. Never mutate the live Qwen installation, model files, systemd service,
    firewall, VPN, API key, or active Codex provider/profile path unless an
    active OAP order explicitly authorizes that exact operation and rollback.
11. Optional gateway ingress uses a configured service Bearer secret with
    constant-time comparison. Signed v1 mode additionally verifies a separate
    bounded HMAC secret over method/path/raw-query-hash/exact-body-hash and
    opaque identity fields, then reserves only a nonce digest in bounded
    process-local replay state. It never accepts public gateway keys or
    unsigned caller identity headers. Service and signed-auth failures occur
    before image, constitution, compiler, cache, rehydration, or upstream work.
    The current gateway does not emit the signed contract; adapter preparation
    is not gateway acceptance or production cutover.

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

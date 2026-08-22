# Live development/test environment

This file records the initial known host contract. It is a verification target,
not permission to alter the host and not a substitute for live reconnaissance.

## Paths and identities

```text
Host/user home: /synology/homes/janezp
Coding repo: /synology/homes/janezp/codex-work/slaif-local-coding
Strategic workspace: /synology/homes/janezp/codex-supervision/slaif-local-coding
Qwen runtime: /synology/homes/janezp/qwen-serving
```

## Current host and endpoint contract

```text
Current host: hinton1
Preferred same-host upstream: http://127.0.0.1:18020/v1
Optional LAN upstream on hinton1: http://10.8.132.75:18020/v1
Historical upstream (not operational): http://10.8.132.76:18020/v1
Model ID: qwen3.8-27b
Verified launch class (2026-08-22): language-model-only
Verified image capacity: zero images per request
Authentication env: QWEN3090_API_KEY
vLLM: 0.27.1 in the recorded installation
Context: 150000 physical; Codex compaction configured around 125000
Tool parser: qwen3_coder
Reasoning parser: qwen3
Prefix caching: enabled in the recorded text configuration
Speculative/MTP: disabled in the recorded batch configuration
```

Endpoint values remain operational hypotheses unless confirmed live on the
current host. Prefer the same-host loopback for development and bounded tests;
the LAN value is a documented alternative for clients on that network. The
historical `.76` address remains only in merged provenance/reference material
and must not be silently rewritten there.

The currently verified service is text-only and declares capacity for zero
images. Do not describe it as a live vision service. Objective 000 previously
passed one- and two-image policy tests against the prior vision deployment;
that evidence remains historical provenance only. Objective 002's current live
image assertion is skipped because of the verified zero-image capability. Any
launch command, multimodal flag, catalog, service state, API shape, or port
ownership claim still requires fresh read-only reconnaissance.

## Current compatibility path

The supplied workaround prototype listened on `127.0.0.1:18021` in its original
environment. It is **reference code only** for this project; no such service is
assumed to be deployed on the target machine. The prototype recursively detects
`input_image` and `image_url` objects in Responses/Chat JSON and forwards only
the newest image to an upstream vLLM endpoint. Its newest-image retention algorithm is reference material for the common
server-side adapter; no OAP Codex agent depends on this prototype.

## Development topology

```text
OAP control path:
  strategic Codex -> default Codex provider
  coding Codex    -> default Codex provider

live system under test:
  Qwen/vLLM text-only service -> hinton1 loopback :18020 (verify live)

new adapter test path:
  curl/tests -> 127.0.0.1:18031 -> live Qwen/vLLM

internal compiler path:
  library caller -> hinton1 loopback vLLM :18020 directly
```

Rules:

- use `18031` for candidate development unless live reconnaissance requires another verified-free loopback port;
- do not stop/replace the live Qwen/vLLM service during ordinary development;
- do not restart or reconfigure `qwen-serving`;
- do not change firewall/VPN/network binding;
- use low-concurrency live tests and the existing key through its environment;
- never print or persist the key;
- cutover is a separate explicit order after the replacement is accepted.

## Reconnaissance evidence required by objective 000

Record without secrets:

```bash
hostname
pwd
codex --version
systemctl --user status qwen-serving --full --no-pager
ss -ltnp | rg ':(18020|18021|18031)\b'
ps -ef | rg '[v]llm|[s]laif-local-coding'
nvidia-smi
curl authenticated /health and /v1/models
```

Do not route either OAP Codex agent through the experimental adapter during
objective 000. Use synthetic OpenAI envelopes, the reference proxy algorithm,
and bounded direct API tests. Sanitized real Codex envelope capture belongs in a later explicit E2E
objective unless it can be obtained without changing the active profile/path.

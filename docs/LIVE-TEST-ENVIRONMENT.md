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

## Historically verified vLLM contract

```text
Private address: http://10.8.132.76:18020/v1
Model ID: qwen3.8-27b
Authentication env: QWEN3090_API_KEY
vLLM: 0.27.1 in the recorded installation
Context: 150000 physical; Codex compaction configured around 125000
Tool parser: qwen3_coder
Reasoning parser: qwen3
Prefix caching: enabled in the recorded text configuration
Speculative/MTP: disabled in the recorded batch configuration
```

The model is now reported by the human as running in vision mode. The exact
current launch command, multimodal flags, model catalog, service state, API
shape, image limit, and port ownership must be captured afresh before coding.
Old text-mode logs are evidence of prior behavior only.

## Current compatibility path

The supplied workaround prototype listened on `127.0.0.1:18021` in its original
environment. It is **reference code only** for this project; no such service is
assumed to be deployed on the target machine. The prototype recursively detects
`input_image` and `image_url` objects in Responses/Chat JSON and forwards only
the newest image to an upstream vLLM endpoint. Codex
vision profiles point to it. It must remain available while a coding Codex uses
that profile.

## Development topology

```text
coding Codex control path:
  Codex qwen38-vision -> current configured vision-mode Qwen/vLLM endpoint
  (discover live; historically vLLM :18020)

new adapter test path:
  curl/tests -> 127.0.0.1:18031 -> live vLLM :18020

internal compiler path:
  adapter process -> live vLLM :18020 directly
```

Rules:

- use `18031` for candidate development unless live reconnaissance requires another verified-free loopback port;
- do not stop/replace the current Codex/Qwen path during ordinary development;
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

Do not redirect the active coding Codex through a recorder during objective 000.
Use the proven reference proxy, synthetic OpenAI envelopes, and bounded direct
API tests. Sanitized real Codex envelope capture belongs in a later explicit E2E
objective unless it can be obtained without changing the active profile/path.

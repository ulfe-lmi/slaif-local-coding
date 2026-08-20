# Third-party notices

## syv-ai/qwen38-27b-rtx3090

Upstream project:
`https://github.com/syv-ai/qwen38-27b-rtx3090`

License: Apache License 2.0.

SLAIF Local Coding is designed and validated around the upstream project's work
for serving Qwen3.8-27B on a single 24 GB RTX 3090 through vLLM. The upstream
project supplies important installation, quantization, patch, launch,
verification, and optimization knowledge. It is not presented as work created
by SLAIF.

Repository policy:

- prefer pinned upstream revisions and separately maintained SLAIF integration
  code over wholesale source copying;
- retain upstream copyright/license headers for any copied file;
- mark modified copied files prominently;
- record exact upstream commit and applied patches in a lock/provenance file;
- preserve Apache-2.0 NOTICE obligations when applicable;
- do not bundle model weights in this repository.

The first historically validated installation used upstream commit
`a14543b1427de5705b2cd6e251b798f9ab78f044`; implementation must re-verify the
currently selected upstream revision rather than treating this historical SHA
as automatically current or production-approved.


## Orchestrated Agentic Programming reference workflow

The repository governance/FIFO/PR/report protocol is adapted from the OAP manual
and the Apache-2.0 `ulfe-lmi/slaif-agent-site` reference implementation. The
project preserves the central human/strategic/coding role split, exact two-byte
FIFO handshake, one-objective/one-PR continuation law, immutable versioned
orders/reports, report `SELF` convention, and strategic-only merge gate.

## Models and checkpoints

Qwen model weights and third-party quantized checkpoints are separate artifacts
with their own license/provenance terms. Installers must display and preserve
those terms, pin the selected revision, and record checksums. The software
license of this repository does not relicense model weights.

Historically used checkpoint:

```text
dbirks/Qwen3.8-27B-W4A16-AutoRound
```

This identifier is deployment evidence, not permission to redistribute it.
Commercial packaging requires explicit verification of the model and checkpoint
terms at the pinned revision.

## Other major dependencies

vLLM, Codex CLI, FastAPI/Starlette, HTTPX, Pydantic, Uvicorn, Prometheus client,
and their transitive dependencies retain their own licenses. The implementation
must generate an exact dependency/license inventory before release.

## SLAIF API Gateway

`ulfe-lmi/slaif-api-gateway` remains a separate Apache-2.0 repository. This
project integrates with it through documented OpenAI-compatible/internal service
interfaces; it does not silently copy the gateway implementation.

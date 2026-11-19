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

## Pinned tokenizer assets (objective 021)

The v1 dependency-bundle cache tokenizer component ships the CPU tokenizer
artifacts of the declared Qwen3.8-27B reference capability, pinned to the
Hugging Face repository `Qwen/Qwen3.8-27B` at revision
`37561816e66b5b9153b1b64c10968c18c1e6f4a0` (Apache-2.0):
`tokenizer.json`, `tokenizer_config.json`, `chat_template.jinja` and the
verbatim Apache-2.0 `LICENSE`, retained under
`src/slaif_local_coding/constitution/bundles/tokenizer_assets/` with a
`NOTICE` (see `docs/CACHE-TOKEN-COMPILER-CONTRACT.md`). Their exact sizes and
SHA-256 digests are closed contract constants verified at load time; a byte
change to any asset or template invalidates the tokenization identity and the
derived compiled-entry identity. These are tokenizer artifacts only: no model
weights, no training data, no serving configuration. The reference RTX 3090
serving work remains credited as `syv-ai/qwen38-27b-rtx3090`.

## Other major dependencies

vLLM, Codex CLI, FastAPI/Starlette, HTTPX, Pydantic, Uvicorn, Prometheus client,
and their transitive dependencies retain their own licenses. The implementation
must generate an exact dependency/license inventory before release.

The adapter uses FastAPI (MIT), Starlette (BSD-3-Clause), HTTPX (BSD-3-Clause),
Pydantic (MIT), Uvicorn (BSD-3-Clause), and Prometheus client_python
(Apache-2.0). Exact versions and transitive packages are fixed by `uv.lock`;
this review is dependency provenance, not a relicensing of those projects.
The objective-021 tokenizer component additionally uses the CPU-only
`tokenizers` library (Apache-2.0), pinned exactly in `pyproject.toml` and
`uv.lock`.

## SLAIF API Gateway

`ulfe-lmi/slaif-api-gateway` remains a separate Apache-2.0 repository. This
project integrates with it through documented OpenAI-compatible/internal service
interfaces; it does not silently copy the gateway implementation.

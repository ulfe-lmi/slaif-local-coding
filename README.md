# SLAIF Local Coding

SLAIF Local Coding is a self-hosted model-compatibility and context-
virtualization layer for constrained local hardware. It lets ordinary Codex
and OpenAI-compatible clients work reliably with local models that do not
support the full OpenAI feature surface — without modifying the clients.

## What it does

The adapter sits invisibly between the SLAIF API Gateway (a separate
repository) and a private local model server such as Qwen3.8-27B on vLLM:

```text
Codex / OpenAI client
      -> SLAIF API Gateway        (separate repository: public keys,
      ->                           permissions, quotas, accounting, TLS)
      -> SLAIF Local Coding adapter (this repository)
      -> private Qwen/vLLM         (OpenAI-compatible, host loopback)
```

- **Faithful OpenAI-compatible proxying** of `/health`, `/v1/models`,
  `/v1/responses`, and `/v1/chat/completions`: status codes, safe error
  envelopes, usage, ordinary function tools, SSE event order, incremental
  streaming, cancellation, and disconnect behavior are preserved; responses
  are never buffered whole.
- **Route-scoped image policy.** The designated Qwen Codex vision route
  accepts exactly one image per request and retains the newest image content
  item from multi-image history (full-image-then-crop); other routes
  explicitly reject or pass through. Unknown capabilities fail closed;
  explicit multi-image comparison is not claimed.
- **Governance observation.** Effective `AGENTS.md` content in model-bound
  traffic is detected from Codex envelope/path evidence only; referenced
  repository paths are enumerated deterministically before any model
  involvement.
- **Constitutional compilation and bounded derived cache.** One bounded,
  non-recursive internal model call compiles observed governance into a
  strict, validated index; a bounded, disposable, content-addressed cache
  keyed by principal, session/repository discriminator, and source hash
  stores validated indexes only; a stable bounded working set is injected
  idempotently on governance-bearing requests. Compiler or cache failure
  never silently deletes governance.
- **Gateway-ready signed ingress.** Service-Bearer plus signed-identity v1
  (HMAC over method/path/query/body-hash and opaque identity fields) with
  bounded process-local replay protection; public client keys terminate at
  the separate Gateway and never reach this adapter.
- **Private observability and privacy.** `/healthz`, `/readyz`, and a
  private `/metrics` (counts/timings/states only). Raw prompts, source,
  images, tool output, request/response bodies, and credentials are never
  logged or persisted.

This repository owns the adapter, route capability policies, packaging,
tests, and diagnostics. The Gateway remains a separate service, and the
cutover between them is a separate human-authorized act.

## Supported runtime and deployment assumptions

- **Linux Docker Engine + Compose v2** is the canonical installation path;
  the install host needs no Python, no uv, and no project dependencies. A
  secondary direct-host systemd user-service path (Python 3.12 + uv) is also
  documented.
- A **private OpenAI-compatible model server** (Qwen/vLLM) reachable from
  the adapter host, e.g. `http://127.0.0.1:18020/v1`. The container runs in
  host network mode so that hop stays true host loopback.
- A **separate SLAIF API Gateway** in front of public traffic. The adapter
  binds loopback by default; a non-loopback bind is accepted only under the
  full signed-ingress contract.
- **Private registry access** for container images: RC images are pulled
  from a private GHCR package with bounded read-only registry credentials;
  anonymous pull is not a prerequisite.
- **Evidence scope:** local-model behavior was qualified against a single
  RTX 3090 Qwen/vLLM fixture and a pinned Gateway compatibility authority.
  That is fixture-scoped evidence, not a generic or production-equivalence
  claim.

## Getting started

- **[QUICKSTART.md](QUICKSTART.md)** — the essential Docker path in
  roughly 5–10 minutes, assuming the upstream model server and the separate
  Gateway already exist.
- **[INSTALL.md](INSTALL.md)** — the full operator installation: supported
  platforms and prerequisites, image selection (digest preferred), private
  registry login, protected configuration, readiness, stop/restart,
  upgrade, digest-based rollback, uninstall, and the advanced direct-host
  path.

## Documentation

| Topic | Document |
| --- | --- |
| Quickstart (Docker) | [QUICKSTART.md](QUICKSTART.md) |
| Installation (Docker primary; direct-host secondary) | [INSTALL.md](INSTALL.md) |
| Human-facing architecture | [ARCHITECTURE.md](ARCHITECTURE.md) |
| Compact normative agent architecture | [ARCHITECTURE-for-agents.md](ARCHITECTURE-for-agents.md) |
| Runtime topology and transport decisions | [docs/TOPOLOGY.md](docs/TOPOLOGY.md) |
| Adapter configuration reference | [docs/ADAPTER-CONFIGURATION.md](docs/ADAPTER-CONFIGURATION.md) |
| Deployment and operator contract | [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) |
| Docker installation (canonical path) | [docs/DOCKER-INSTALL.md](docs/DOCKER-INSTALL.md) |
| Docker vs systemd containment review | [docs/DOCKER-SECURITY-DELTA.md](docs/DOCKER-SECURITY-DELTA.md) |
| Security policy | [SECURITY.md](SECURITY.md) |
| Verification contract | [TESTING.md](TESTING.md) |
| Release-artifact policy and provenance | [docs/RELEASE-ARTIFACT-POLICY.md](docs/RELEASE-ARTIFACT-POLICY.md) |
| RC artifact handoff (retrieval and identity verification) | [docs/RC-HANDOFF.md](docs/RC-HANDOFF.md) |
| Live cutover/rollback runbook (prepare-only) | [docs/RELEASE-CUTOVER-RUNBOOK.md](docs/RELEASE-CUTOVER-RUNBOOK.md) |
| Documentation index | [docs/README.md](docs/README.md) |
| Development contribution | [CONTRIBUTING.md](CONTRIBUTING.md) |
| OAP orchestration transcript (history) | [oap/README.md](oap/README.md) |

## Release status

SLAIF Local Coding 0.1.0 is being prepared and frozen as a release
candidate (RC). The RC is published to a **private** GHCR package under an
explicit candidate identity; the immutable image **digest** is the
authoritative identity and tags are aliases. A final public release is a
separate later decision; no timing is promised, and nothing in this
repository implies that the final release has happened.

The historical private `0.1.0` tag pushed during Objective 013 was written
to a non-public package and was never published to users. It is legacy
output, **not** the RC benchmark target, and must not be pulled or reused
for the RC. The cutover to the adapter has NOT been performed, and no
production deployment is claimed.

## Important limitations

- Compatibility claims are limited to the tested Qwen/vLLM fixture and the
  pinned Gateway compatibility authority; no multi-user, production,
  compliance, or frontier-equivalence claim is made.
- The governance pipeline is off by default and requires explicit
  configuration. It performs request-scoped observation plus bounded
  derived context; the source repository (files, Git, remote) remains
  authoritative over any reconstructed context.
- Docker deployment qualification is disposable/CI environments only.
- The sdist is a developer-only source archive; the wheel is the single
  supported native distributable.
- Single-fixture evidence is fixture-scoped; one RTX 3090 qualification
  does not establish generic production readiness.

## License and credits

Licensed under Apache-2.0 — see [LICENSE](LICENSE), [NOTICE](NOTICE), and
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

The reference RTX 3090 serving work for Qwen3.8-27B is credited to
[syv-ai/qwen38-27b-rtx3090](https://huggingface.co/syv-ai/qwen38-27b-rtx3090)
(Apache-2.0). Model weights are never committed to this repository.

## Developers

The locked gate (Python 3.12, uv) is documented in [TESTING.md](TESTING.md)
and [CONTRIBUTING.md](CONTRIBUTING.md); in short:

```bash
uv lock --check
uv sync --frozen --extra dev
uv run --frozen ruff check .
uv run --frozen ruff format --check .
uv run --frozen mypy src tests
uv run --frozen pytest -q
uv build
uv run --frozen python scripts/artifact_policy_check.py --dist dist --inspect
uv run --frozen python scripts/artifact_policy_check.py --dist dist --install-smoke
```

The governance pipeline details (observation grammar, compiler contract,
cache law, working-set selection and injection) are specified in
[ARCHITECTURE.md](ARCHITECTURE.md) (component model) and
[ARCHITECTURE-for-agents.md](ARCHITECTURE-for-agents.md); historical
objective/round state is recorded in the OAP transcript
([oap/README.md](oap/README.md)) and is not a product document.

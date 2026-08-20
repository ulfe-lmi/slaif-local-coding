# SLAIF Local Coding

SLAIF Local Coding is a self-hosted model-compatibility and context-
virtualization layer for practical SME coding/chat deployments on constrained
local hardware.

It sits invisibly between the SLAIF API Gateway and a local OpenAI-compatible
model server such as Qwen3.8-27B on vLLM. Ordinary Codex/OpenAI-compatible
clients remain unchanged.

Target capabilities, implemented incrementally through OAP:

- preserve only the newest image when a route physically supports one image;
- detect effective `AGENTS.md` governance in model-bound traffic;
- discover and rank referenced constitutional files;
- compile bounded pseudo-context with a separate internal model call;
- cache compiled constitution by content hash and tenant/session identity;
- inject the compact constitution into later requests, including after Codex
  compaction;
- preserve Responses/Chat Completions streaming and ordinary function tools;
- expose safe internal health/readiness/metrics without logging prompts, code,
  images, or raw request/response bodies.

Deployment boundary:

```text
Codex / OpenAI client
        -> SLAIF API Gateway
        -> SLAIF Local Coding adapter
        -> Qwen/vLLM
```

The API Gateway remains a separate repository and owns public access keys,
quotas, accounting, route permissions, and operator administration. This
repository owns the local-model appliance, compatibility transformations,
packaging, and live-model verification.

Read first:

- `ARCHITECTURE.md` — detailed human-facing design;
- `ARCHITECTURE-for-agents.md` — compact normative implementation law;
- `AGENTS.md` — coding-agent constitution;
- `SECURITY.md` and `TESTING.md`;
- `oap/README.md` — versioned transcript contract;
- `docs/OAP-RUNBOOK.md` — exact two-Codex startup/activation/recovery.

The project is developed through Orchestrated Agentic Programming. The coding
agent never merges. The strategic agent independently reviews GitHub state and
merges only when required CI is green and the objective is satisfactory.

Current status: architecture and OAP bootstrap; implementation begins with OAP
objective `000`.

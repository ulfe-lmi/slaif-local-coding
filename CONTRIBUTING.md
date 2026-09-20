# Contributing

Start with the [architecture](ARCHITECTURE.md), [security policy](SECURITY.md)
and [testing guide](TESTING.md). Develop on a branch and submit a pull request
with a clear problem statement, the resulting behavior and relevant validation.

## Development setup

Use Python 3.12 and the uv version recorded in the build provenance:

```bash
uv sync --frozen --extra dev
uv run --frozen ruff check .
uv run --frozen ruff format --check .
uv run --frozen mypy src tests
uv run --frozen pytest -q
```

Use synthetic requests and fake upstreams for ordinary development. Live model
and Codex tests require explicit fixture access and bounded execution. Never
change an existing model service, its credentials, network configuration or an
active client profile as a side effect of development.

## Pull requests

- Keep the scope and non-goals clear; explain any operational impact.
- Update user documentation when behavior or configuration changes.
- Report passed, failed, skipped and unrun tests separately.
- For new dependencies, explain the purpose and review the version lock and license.
- Never commit live user prompts, source fragments, images, tool output,
  credentials, raw request/response captures or cache contents.
- Preserve license notices and keep the separate Gateway's responsibilities separate.

README is embedded in wheel metadata. Changes to README, product source or
other artifact inputs require the reproducibility and provenance steps in the
[artifact policy](docs/RELEASE-ARTIFACT-POLICY.md) before an RC is frozen.

## Agent contributions

Agent work follows the repository's OAP process. Agents must read
[AGENTS.md](AGENTS.md), the [coding protocol](OAP-COMMUNICATION-coding-agent.md)
and [normative architecture](ARCHITECTURE-for-agents.md). The active order defines
scope and reporting; coding agents do not accept or merge their own work.
See the [OAP runbook](docs/OAP-RUNBOOK.md) for orchestration details.

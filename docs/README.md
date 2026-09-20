# Documentation

## Start here

- [Quickstart](../QUICKSTART.md): launch the Docker deployment.
- [Installation](../INSTALL.md): prerequisites, private registry access, image
  selection, protected configuration, readiness, upgrade, rollback and uninstall.
- [Architecture](../ARCHITECTURE.md): components, request flow, diagrams and limits.

## Operators

- [Docker reference](DOCKER-INSTALL.md): Compose behavior and troubleshooting.
- [Deployment and operations](DEPLOYMENT.md): shared rules and advanced systemd path.
- [Configuration reference](ADAPTER-CONFIGURATION.md): settings and validation.
- [Runtime topology](TOPOLOGY.md): addresses, namespaces and supported transports.
- [Gateway integration](SLAIF-GATEWAY-INTEGRATION.md): authentication and identity contract.
- [RC handoff](RC-HANDOFF.md): retrieve and verify the immutable artifact.
- [Cutover and rollback plan](RELEASE-CUTOVER-RUNBOOK.md): separately authorized live changes.

## Security and engineering

- [Security policy](../SECURITY.md): sensitive data, credentials and reporting.
- [Docker/systemd security comparison](DOCKER-SECURITY-DELTA.md): containment tradeoffs.
- [Contributing](../CONTRIBUTING.md): development setup and pull requests.
- [Testing](../TESTING.md): local checks, CI and fixture-dependent verification.
- [Gateway contract CI](GATEWAY-CONTRACT-CI.md): exact peer compatibility checks.
- [Artifact policy](RELEASE-ARTIFACT-POLICY.md): reproducibility, provenance and publication.
- [License](../LICENSE), [notice](../NOTICE) and [third-party attribution](../THIRD_PARTY_NOTICES.md).

## Agent instructions and engineering history

These are specialist materials, not installation instructions:

- [Agent constitution](../AGENTS.md), [coding protocol](../OAP-COMMUNICATION-coding-agent.md)
  and [normative architecture](../ARCHITECTURE-for-agents.md).
- [OAP runbook](OAP-RUNBOOK.md) and [immutable orchestration transcript](../oap/README.md).
- [Engineering history index](HISTORY.md): acceptance records and exact prior documentation.
- [Historical roadmap](IMPLEMENTATION-ROADMAP.md) and
  [historical host snapshot](LIVE-TEST-ENVIRONMENT.md).
- [Historical tool-filter proposal](GATEWAY-ROUTE-SCOPED-CODEX-TOOL-FILTER-PROPOSAL.md).

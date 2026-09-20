# Documentation index

The documents are grouped by audience. Current user-facing operator
documents are kept free of objective/round chronology; OAP and objective
history is retained explicitly as history.

## Operator

- [../QUICKSTART.md](../QUICKSTART.md) — the 5–10 minute Docker path.
- [../INSTALL.md](../INSTALL.md) — full operator installation (Docker
  primary; direct-host secondary/advanced), upgrade, digest-based
  rollback, uninstall.
- [DOCKER-INSTALL.md](DOCKER-INSTALL.md) — the detailed canonical Docker
  procedure (operator reference).
- [DEPLOYMENT.md](DEPLOYMENT.md) — the complete operator contract for both
  supported deployment paths.
- [ADAPTER-CONFIGURATION.md](ADAPTER-CONFIGURATION.md) — adapter
  configuration reference (templates, placeholders, route policy).
- [RELEASE-CUTOVER-RUNBOOK.md](RELEASE-CUTOVER-RUNBOOK.md) — the
  prepare-only live cutover/rollback runbook (the cutover itself is a
  separate human-authorized act).
- [RC-HANDOFF.md](RC-HANDOFF.md) — release-candidate artifact retrieval
  and identity verification (handoff; not an experimental procedure).

## Architecture and security

- [../ARCHITECTURE.md](../ARCHITECTURE.md) — human-facing architecture.
- [../ARCHITECTURE-for-agents.md](../ARCHITECTURE-for-agents.md) — compact
  normative agent architecture.
- [TOPOLOGY.md](TOPOLOGY.md) — runtime topology, hosts, transports,
  per-hop boundaries, and the supported LAN-visible signed variant.
- [../SECURITY.md](../SECURITY.md) — security policy and protected-host
  boundary.
- [DOCKER-SECURITY-DELTA.md](DOCKER-SECURITY-DELTA.md) — Docker vs systemd
  containment review (isolation lost, invariants kept, compensating
  controls, accepted threats).
- [SLAIF-GATEWAY-INTEGRATION.md](SLAIF-GATEWAY-INTEGRATION.md) — the
  adapter-side Gateway ingress contracts.
- [GATEWAY-CONTRACT-CI.md](GATEWAY-CONTRACT-CI.md) — the continuous
  Gateway-contract test against the pinned peer.
- [GATEWAY-ROUTE-SCOPED-CODEX-TOOL-FILTER-PROPOSAL.md](GATEWAY-ROUTE-SCOPED-CODEX-TOOL-FILTER-PROPOSAL.md) —
  scoped proposal (not implemented product behavior).

## Developer and testing

- [../TESTING.md](../TESTING.md) — the verification contract (required
  test layers, exact status labels).
- [../CONTRIBUTING.md](../CONTRIBUTING.md) — contribution and locked gate.
- [RELEASE-ARTIFACT-POLICY.md](RELEASE-ARTIFACT-POLICY.md) —
  supported-artifact policy, provenance model, and the RC publication
  machinery.

## OAP and history

- [../oap/README.md](../oap/README.md) — the versioned OAP transcript
  contract (orders, reports, active selection).
- [OAP-RUNBOOK.md](OAP-RUNBOOK.md) — two-Codex OAP startup/activation/
  recovery.
- [IMPLEMENTATION-ROADMAP.md](IMPLEMENTATION-ROADMAP.md) — roadmap state
  and objective history (strategic context; historical entries are
  explicitly dated).
- [OBJECTIVE-004-LEDGER.md](OBJECTIVE-004-LEDGER.md) — Objective-004
  criterion ledger (accepted evidence).
- [OBJECTIVE-005D-SECURITY-CONTAINMENT.md](OBJECTIVE-005D-SECURITY-CONTAINMENT.md) —
  Objective-005-d security containment record (historical).
- [VISION-ACCEPTANCE.md](VISION-ACCEPTANCE.md) — fixture-scoped vision
  acceptance record (historical).
- [LIVE-TEST-ENVIRONMENT.md](LIVE-TEST-ENVIRONMENT.md) — live-test
  environment facts (historical, protected-fixture descriptions).

Objective/round chronology, PR/merge ledgers, and acceptance dumps live
in the OAP transcript (`oap/`), not in the operator documents above.

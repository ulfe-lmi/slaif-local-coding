# Implementation roadmap

This roadmap is strategic context, not an activated order. Live GitHub/host
state and review outcomes control actual sequencing.

## Objective 000 — live contract and adapter foundation

- capture current vLLM/vision/Codex envelopes safely;
- establish locked Python project and CI;
- implement faithful async OpenAI-compatible pass-through on development port
  `18031`;
- integrate route-scoped newest-image-only policy from the proven prototype;
- preserve SSE and ordinary function tools;
- add health/readiness/metrics and fake-upstream plus bounded live tests;
- do not implement constitution compilation or cut over the current Codex/Qwen path.

## Objective 001 — constitution observation and deterministic discovery

- identify effective `AGENTS.md` blocks in captured Codex request shapes;
- extract path candidates deterministically with provenance/evidence spans;
- define strict schemas and hash/session/cache identities;
- store bounded disposable entries; no model-generated summary injection yet.

## Objective 002 — internal constitutional compiler

- direct non-recursive text-only call to vLLM;
- separate reference confidence from constitutional priority;
- preserve normative rules, exceptions, role boundaries, and source-of-truth
  statements;
- rank dependencies and acquisition urgency;
- validate/retry strict bounded JSON; cache by source/compiler/model hash.

## Objective 003 — pseudo-context injection and rehydration

- stable bounded injection into every model-bound request;
- unresolved dependency instructions and incremental acquisition from tool
  outputs;
- fail-open semantic preservation on compiler failure;
- cache invalidation, TTL, LRU/budget, session isolation;
- simulated compaction/new-turn recovery.

## Objective 004 — real Codex end-to-end and operational hardening

- long real `AGENTS.md` with sentinel rule and delegated files;
- actual Codex full-image then crop path;
- actual/forced compaction and immediate post-compaction compliance;
- disconnect/retry/timeouts/tool-streaming tests;
- no raw-content logs; metrics and operator diagnostics;
- documented service install on non-conflicting port.

## Objective 005 — gateway integration and controlled cutover

- coordinated internal identity/service-auth contract with
  `slaif-api-gateway`;
- route capability/policy configuration;
- deployment manifest and release provenance;
- replace the temporary client-side workaround only after independent acceptance and a
  rollback-proven cutover order;
- vLLM remains private.

## Objective 006 — SME package

- reproducible installer/upgrade/rollback;
- systemd and OCI/Compose options;
- pinned upstream Qwen/vLLM integration and third-party notices;
- admin/operator runbook, backup/cache purge, capacity guidance;
- release claim limited to tested hardware/configuration.

# Implementation roadmap

This roadmap is strategic context, not an activated order. Live GitHub/host
state and review outcomes control actual sequencing.

## Current state (2026-09-17, verified against GitHub)

Objectives 000–010 are **implemented and merged** (PR #1–#12; merge commits
`91463ae3`, `176bf4d8`, `867ed55e`, `68f212b5` + `7a2c36a0`, `570bd2b2`,
`e3f10e93`, `efc4dbcd`, `2041bddc`, `1a913bf3`,
`4fd4502deda23ef8815740f4db0c1e615a5a1936` (009),
`4aa805fdd197938f1f25c9ca034c2e3c3cf2fc87` (010) — see
`oap/COMPLETENESS.md` for the full table). Objective 004 real-Codex evidence
is **accepted (fixture-scoped)**; the Gateway pair is **continuously
Gateway-contract tested** (objective 007); durable acceptance evidence is
accepted (objective 008). Objective 009 is the accepted release candidate
(reproducible package, deployment-qualified in a disposable environment
only). Objective 010 closed the pre-cutover topology and signed-ingress
correctness work (prepare-only; the cutover was NOT performed). Objective 011
(PR #13, merged 2026-09-17 as `e860e0bff687afded7782fb2687b5b435792459a`) is
the Docker MVP release candidate: **Docker MVP packaging,
LAN-visible installation law, and release-readiness closure** —
deployment-qualified (disposable/CI environments only). Objective 012
(2026-09-17) re-pinned the current Gateway peer to
`1fccaa746df6cd44f1ddf8c2ec5cf6ea9f18b1cb` (contract surface byte-identical,
proven at the blob level), regenerated the release provenance manifest
(`objective: "012-a"`; wheel
`fceadc378130dd4ffcc3f75d17b5e098577652914f541245d31247911be23aeb` / sdist
`910b65db8abe331fb1ad0507697c1e089fd9ea4ede2ec1792b7fac5c8f5c1240`; artifact
record per `RELEASE-ARTIFACT-POLICY.md`), and closed the post-011
documentation drift. **Cutover NOT performed; NOT released.**

Identifier note: the original planned meanings of numeric objectives 006–008
in this file (for example "SME package") are **historical planning prose, not
live objective identifiers**. The live numeric identifiers 006/007/008 were
signed-request replay hardening, current Gateway contract CI, and durable
acceptance evidence respectively. The original milestone "reproducible SME
package and honest release evidence" is implemented under the Objective-009
milestone name.

## Objective 000 — live contract and adapter foundation

- capture current vLLM/vision/Codex envelopes safely;
- establish locked Python project and CI;
- implement faithful async OpenAI-compatible pass-through on development port
  `18031`;
- integrate route-scoped newest-image-only policy from the proven prototype;
- preserve SSE and ordinary function tools;
- add health/readiness/metrics and fake-upstream plus bounded live tests;
- do not implement constitution compilation or cut over the live Qwen/vLLM service.

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

## Objective 005 — gateway integration and controlled cutover (merged, PR #7)

Status: implemented and merged (merge commit `e3f10e93c1ea84bf4021fd15d566bf577d5a9dcf`);
the live cutover itself was NOT performed and remains the separate
human-authorized final act (runbook: `RELEASE-CUTOVER-RUNBOOK.md`).

- coordinated internal identity/service-auth contract with
  `slaif-api-gateway`;
- route capability/policy configuration;
- deployment manifest and release provenance;
- replace the temporary client-side workaround only after independent acceptance and a
  rollback-proven cutover order;
- vLLM remains private.

## Objective 006 — SME package (original planned meaning; historical)

This planned meaning was never executed as numeric objective 006. The live
objective 006 was signed-request replay hardening (merged PR #8). The
planned SME-package milestone is implemented under the **Objective-009
milestone name** (release candidate and operational closure): reproducible
package, upgrade/rollback procedures, and honest release evidence. The
planned "systemd and OCI/Compose options" item was deliberately narrowed: the
single supported path is the systemd local-host user service (OCI/Compose
remains out of scope by order).

- reproducible installer/upgrade/rollback;
- pinned upstream Qwen/vLLM integration and third-party notices;
- admin/operator runbook, backup/cache purge, capacity guidance;
- release claim limited to tested hardware/configuration.

## Objective 009 — release candidate and operational closure (PR #11)

- reconcile current-facing documentation with merged software truth;
- explicit supported-artifact policy with mechanically proven artifact
  contents (wheel = single supported distributable; sdist = developer-only);
- one supported deployment path (systemd user service, repository venv) with a
  complete operator contract;
- disposable operational qualification against fake loopback upstreams only;
- content-free release provenance manifest;
- exact final live-cutover/rollback runbook (prepare only, not executed);
- regression/CI gates (artifact policy inspection, fresh-venv install smoke).


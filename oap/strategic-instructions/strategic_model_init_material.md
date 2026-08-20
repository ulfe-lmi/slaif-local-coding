# OAP STRATEGIC INITIALIZATION — SLAIF LOCAL CODING

This is the project-specific compact initialization for the strategic Codex.
It applies OAP doctrine to `ulfe-lmi/slaif-local-coding`. Read strategic
constitution and communication protocol first. Full OAP/manual/reference files
remain provenance; this document supplies the operative project model.

## 1. OAP doctrine

OAP is human-governed, constitution-driven agentic software delivery:

```text
human supplies intent/domain/risk/release
strategic AI preserves architecture/continuity and compiles bounded orders
coding AI performs high-autonomy repository work
GitHub/PR/CI preserves durable software truth
```

AI makes code cheap; validation, architecture, security, continuity, operations,
documentation, and honest release claims become bottleneck. High autonomy is
useful only inside explicit authority/credential/runtime/PR boundaries. A fluent
report, large diff, or green CI is not completion. Strategy must interrogate
evidence and retain disagreement authority.

The coding context is disposable per PR-sized round. Strategic continuity is
long-lived but must also be reconstructed from constitution, architecture,
versioned OAP transcript, GitHub, and decision ledger. Never use remembered chat
instead of live remote state.

## 2. Human intent and product discovery

The intended SME package is a private “mini ChatGPT / mini Codex” appliance using
an affordable local GPU and ordinary OpenAI-compatible clients. The reference
installation is Qwen3.8-27B/vLLM on one RTX 3090 24 GB.

The product problem is not only model serving. Constrained local models expose
compatibility defects that ordinary clients cannot or should not solve:

1. Long Codex sessions compact; smaller models lose governance/project bearings.
2. Codex keeps prior viewed images and may resend an old image with a new crop;
   a one-image local vision route then fails.
3. SMEs still need keys, policy, quota/accounting, route administration, safe
   operation, provenance, and reproducibility.

Architecture decision:

```text
ordinary client
 -> separate SLAIF API Gateway (public control/access plane)
 -> SLAIF Local Coding adapter (private semantic/model compatibility plane)
 -> private vLLM/Qwen (inference)
```

Separate repositories, one deployment workflow. Gateway remains generic and
owns public keys/auth/permissions/quota/accounting/routing/admin/TLS. This repo
owns the invisible model frontend, constrained-model transforms, Qwen/vLLM
integration, tests, packaging. Do not collapse them.

## 3. Core product mechanisms

### 3.1 Constitutional context virtualization

When provider-bound traffic contains effective `AGENTS.md` material, adapter:

1. detects it using envelope/path evidence;
2. hashes exact observed content;
3. deterministically enumerates explicit candidate repository paths and evidence;
4. on cache miss makes a separate bounded direct model call;
5. compiler extracts binding rules and ranks candidates using independent:
   - `reference_confidence`;
   - `constitutional_priority`;
6. stores bounded derived indexes keyed by principal/session/source/compiler/
   model/policy versions;
7. injects a stable compact constitution into every applicable model request;
8. as referenced files later cross API boundary through Codex tool output,
   compiles them incrementally;
9. after compaction/new context, reinjection immediately restores orientation.

`AGENTS.md` is root, not magical authority over source truth. Cache is disposable.
Full repository/Git/GitHub/source documents override compiled representations.
Compiler cannot browse/filesystem/use tools. Mechanical candidate enumeration
prevents model omission. Model interprets semantics because middleware alone
cannot reliably preserve normative exceptions.

### 3.2 Multimodal compatibility

For explicit one-image Codex vision route, adapter scans complete outgoing
Responses/Chat request and retains only newest image content item while
preserving all non-image content/order. This solves full-image then crop history.
Policy is route-scoped; another route may reject or support multiple images.
Never globally discard images or claim multi-image comparison preserved.

Both mechanisms belong at same point: complete model-bound request immediately
before inference. They are transparent constrained-model compatibility policies.

## 4. Reference live environment and risk

Development occurs on the same valuable host as active model service. Historical
reference facts:

```text
Qwen checkout: /synology/homes/janezp/qwen-serving
vLLM model name: qwen3.8-27b
historical upstream: http://10.8.132.76:18020/v1
new development adapter: 127.0.0.1:18031
repo: /synology/homes/janezp/codex-work/slaif-local-coding
strategic: /synology/homes/janezp/codex-supervision/slaif-local-coding
```

These must be verified before every service-sensitive order. No pre-existing
image proxy is assumed. The current coding Codex vision profile/provider path
must be discovered live; changing that path can terminate the executor. Ordinary
work therefore cannot mutate port 18020, Qwen checkout/venv/model/patches/
systemd/launch flags, firewall/VPN/bindings/API keys, or active Codex profiles.

Use fake upstream for most tests and bounded authenticated live calls for
contract evidence. New adapter binds 18031. Cutover is a later isolated order
with backups, candidate health/tool/vision/Codex tests, explicit rollback, and no
active coding turn using endpoint being replaced.

This host is not a disposable OAP VM. Passwordless sudo remains useful for safe
repo-local tooling but does not override protected-fixture law.

## 5. Initial delivery sequence

Strategic default roadmap, revised only from evidence:

```text
000 adapter foundation + faithful proxy + route-scoped image cap + live contract
001 AGENTS observation + deterministic constitutional candidate extraction
002 internal compiler + strict schemas + bounded cache
003 working-set selection + injection + incremental acquisition + rehydration
004 actual Codex E2E + security/observability/operational hardening
005 SLAIF API Gateway integration + controlled cutover
006 reproducible SME package + release evidence
```

Each numeric objective is one coherent PR; follow-up letters repair/amend same
PR. Do not implement the entire product in one large “MVP” PR. Objective 000 is
still meaningful one-day proof: transparent adapter on 18031, faithful SSE/tools,
newest-image policy, fake/live tests, no constitution compiler, no cutover.

## 6. Work-order engineering

Before order, verify remote main/open PR/current checks and current host facts.
Order states exact behavior, observable evidence, non-goals, safety boundary,
and report. “Build proxy” is insufficient. Strong objective 000 order proves:

- async pass-through contract;
- no full-response buffering;
- tools/SSE/errors/usage preserved;
- zero/one image unchanged; multiple images leave exactly newest;
- policy route-scoped;
- live vLLM calls bounded and authenticated without secret output;
- candidate service on 18031;
- port 18020 and existing profiles/services unchanged;
- CI/docs/provenance established.

Do not require human to run commands/install packages/paste logs. Coding owns
safe setup. Do not authorize broad host/service changes merely because sudo
exists.

## 7. Evidence and review discipline

Treat report as index. Independently inspect GitHub. Tests prove only named
scope. Fake upstream proves envelope fidelity; live vLLM proves current provider
compatibility; real Codex proves full client chain. One does not substitute for
another.

For transform code require negative/edge proof:

- malformed/oversized JSON;
- image item shapes and traversal order;
- streaming disconnect/backpressure/timeouts;
- internal header spoofing;
- compiler recursion bypass;
- invalid model JSON/no cache pollution;
- source hash/version invalidation;
- cache isolation/bounds/TTL/LRU/idempotent injection;
- compiler failure preserves governance semantics;
- raw-content/log/metric leakage scans.

For live tests record sanitized endpoint, model, request shape, status/event/tool
facts, count/timing; never raw secret/body/source/image. Verify protected service
state before/after where order requires. An unavailable live fixture is
`BLOCKED|SKIPPED`, not pass.

Before merge ask strongest reason not to merge: silent semantic change, cross-
tenant cache, governance omission, response buffering, self-disconnection,
unbounded compiler GPU load, secret logging, scope creep into gateway/vLLM,
documentation overclaim.

## 8. Security/release position

The adapter handles sensitive prompts, source, tool output, and images. Default
no raw-content logs/persistence. External key terminates at gateway in production.
Adapter receives service auth and signed opaque identity. Multi-user release
requires identity-isolated cache; missing identity cannot fall back to shared
cache.

No model weights in Git. Pin component revisions/checksums, preserve Apache-2.0
notices, identify modifications, thank `syv-ai/qwen38-27b-rtx3090`. Verify model
checkpoint license separately before commercial SME distribution.

Release language ladder: experimental live proof -> tested reference appliance ->
SME beta -> operationally documented release. One successful RTX 3090 demo is
not generic compatibility, production certification, privacy/compliance audit,
or frontier-model equivalence.

## 9. Strategic operating loop

```text
verify live GitHub/host
 -> write one bounded order
 -> atomically activate and FIFO OK
 -> block for coding OK
 -> read immutable report
 -> independently inspect PR/commit parent/diff/checks
 -> merge only if all requirements/evidence/CI/risk satisfactory
 -> verify remote main
 -> activate next objective or escalate human
```

Preserve human intent and architecture; spend strategic context on decisions and
evidence, not terminal retries. Coding does routine implementation. GitHub and
the versioned transcript must make restart possible without trusting memory.

# OAP work order — 022-a: validated opt-in cache configuration

Numeric objective 022, CREATE_NEW_PR from verified remote main
`144af0bd5e34387afcb8e3f9ddf761eabd56e817` (accepted whole 021, PR 29).
Create one branch `oap/022-cache-source-replacement` and exactly one PR.
No 022 remote branch or PR exists. Preserve unrelated PR 23. Strategy owns
acceptance, continuation and merge.

## Scope

Implement the configuration and pure context contract at the start of the
existing 022 succession in docs/CACHE-IMPLEMENTATION-PLAN.md. Build on the
accepted 017–021 components. Save the typed configuration and its focused
tests, then the configuration entry-point/refusal tests and owning docs.
This is the first same-objective slice. Exact-span replacement, trusted
upstream issuance, protected checkpoint and forwarding integration, and the
full actual-upstream R01–R05/S01–S02 evidence remain mandatory before the
022 PR can merge. Do not implement those later slices in this round.

1. Add the explicit `[context_cache]` profile selector to the actual
   `Settings` and TOML loader in `config.py`. Omission keeps the existing
   legacy behavior, and `legacy` explicitly selects it. Accept
   `dependency-bundles-v1` with a closed, typed configuration. Admission
   defaults to `lean` and `greedy` must be explicit. Unknown, incompatible
   or ambiguous settings fail closed. Preserve existing legacy configuration
   and image/tool-policy parsing and their defaults. Detect explicitly
   provided legacy cache/TTL/LRU, derived rehydration, byte-injection,
   compiler and selector policies when they conflict with v1. An operator
   supplying an old setting at its default value still supplied a setting.
   Materialized defaults or an empty policy block alone do not conflict.
   Reuse existing `constitution.enabled`, route observation/constitution
   flags, and validated identity source/labels where they are common to both
   profiles. Apply the legacy compiler/selector rules only to legacy.
2. Validate the explicit effective context and existing 021 budget bounds
   against each enabled v1 route's declared model/vision contract. Reuse
   `BundleBudgetConfig`, the pinned tokenizer/render capability and
   `BundleCompilerConfig` or their validators. Bind compiler
   revision/compatibility and the actual configured effective C, reserves
   and render/tokenizer capability, never a model alias, executor setting
   or upstream maximum alone. The same contract may serve compatible
   routes that explicitly share it. Keep generation, tool, uncertainty,
   per-retained-image and compiler input/output/timeout bounds under the
   existing 021 laws. Prove that changed effective context or compiler
   compatibility is a distinct budget/compile policy through the existing
   021 identity recipe. Leave authenticated request/workspace joins and
   per-session namespace/opening to the later transaction. Never load a
   tokenizer at legacy startup merely to expose configuration types.
3. Require explicit v1 protected-recovery opt-in and configured root,
   the existing one-worker policy, and explicit bounded process/session
   RAM ownership using the accepted 019/020 types/laws. Explain
   operator-prepared directory/retention/encryption obligations from
   SECURITY.md. Configuration validation must not open/create, enumerate
   or probe a recovery store, resolve a request workspace, read
   credentials, or call an upstream. Runtime ownership and exact storage
   checks are earned only during later wiring. Keep configuration error
   messages fixed and avoid echoing private paths/credentials. The
   compiler uses a protected environment reference for direct upstream
   authentication. It must never accept a Gateway credential as its
   compiler credential.
4. Preserve the existing signed Gateway prerequisite and static private
   loopback identity contracts, dedicated credential roles and request
   auth ordering. Do not add caller identity headers or reimplement
   Gateway policy. At the current `create_app` entry point reject a valid
   selected v1 profile with a fixed startup refusal for unavailable v1
   runtime, before constructing an HTTP client, legacy cache or recovery
   owner. Legacy remains usable through its existing entry points. This
   guard is removed only when the same-022 transaction is wired. A
   settings model or an app refused before starting does not establish v1
   readiness, source replacement, native-format, streaming or recovery
   qualification.

## Verification

Extend the existing settings and app test surfaces. Cover real TOML loading
and direct settings construction, default/explicit legacy parity, compatible
v1 settings and strict migration negatives, missing/disabled recovery,
unsupported multi-worker/capability and incompatible identity, changed
effective C/compiler policy, unchanged route image/tool behavior, and
application refusal before any cache/store/client work. Use fake transports,
synthetic identity and no real secrets. Reuse accepted component validators
and run the existing focused config/app and relevant pinned
budget/compile-work tests. Assert actual exceptions and construction
boundaries, not just config flags.

Run the existing 15-command locked gate with diff from
`144af0bd5e34387afcb8e3f9ddf761eabd56e817`, source A and manifest-only B,
one clean exact-B archive artifact proof and fresh noneditable installation.
After focused verification and the exact candidate freeze, GitHub checks and
the managed local full gate may run in parallel. Use a foreground managed
terminal call with an absolute gate-script path, and collect its actual
exit/individual results. Keep the matching artifact and gate outputs under
the project work directory. All ten existing exact-B GitHub checks and the
required local/clean archive evidence must be complete before report
publication. Fix in-scope CI failures on the same PR. Preserve frozen
publications. Update the configuration documentation, both architecture maps
and all three compact mirrors as needed, and current ledger status only.
Keep full 022 and later runtime/client criteria unearned. No new planning or
audit framework.

## Execution and publication

Use only the existing visible RIGHT pane %19 worker, PID 598258 birth
150182858. The standard managed control helper is PID 1423988 birth
370179038 on original FIFO inode 10648021, tool handle 69203. Use only
its exact valid frame exit; read `oap/active` after that exit and require
this unique order. No replay. A new process is forbidden except actual
worker crash, when the only allowed restart is in RIGHT using exactly
`codex --yolo --profile early-beta`. No additional Codex/model-client
startup, service change, Gateway change, registry publication, deployment,
benchmark or cutover. Live model inference remains NOT RUN. Preserve
the protected Qwen/18020, profiles, launch/systemd, keys and network state.
No dev service is required. Use repo-local tools and only
`/home/janezp/codex-supervision/slaif-local-coding/work-artifacts/oap-022a-work`
for new manual artifacts with private modes. Original FIFOs remain under
`/home/janezp/codex-supervision/slaif-local-coding`.

Publish exact order/active bytes and implementation on the one PR. Record the
literal implementation SHA. Atomically create and push one immutable matching
report-only SELF child after verification. Verify exact remote report bytes,
parent and PR head before the one response FIFO `OK`. Start one managed
foreground control wait using the existing `oap_fifo.py wait` helper and
await the next activation. Coding never merges or enables auto-merge.

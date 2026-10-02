# OAP Work Order — 015-a

## Objective and authority

CREATE_NEW_PR; Objective 015; exactly one new PR. Independently confirmed
product defects P01 and P02 must be repaired, mechanically regressed, and
qualified in a new immutable private `0.1.0-rc8` image. The stopping point is a
repaired product artifact suitable for renewed independent benchmark
qualification. This order does not authorize benchmark work.

Human explicitly authorizes the bounded product repair, private RC8 publication,
pulled-image qualification, controlled fake/live defect qualification, and
standalone real-Codex VISION/CACHE/BOTH plus DIRECT-control smoke. Human does
not authorize any benchmark harness change or run, Minesweeper attempt, final
public release, public GHCR visibility, `v0.1.0`, final GitHub Release,
protected-host cutover, production Gateway/routing mutation, Codex modification,
or existing vLLM/model/checkpoint/quantization/context/parser/CUDA/GPU/service
change.

## Authoritative starting state

- Repository: `ulfe-lmi/slaif-local-coding`.
- Numeric objective/round: `015` / `015-a`.
- PR mode: `CREATE_NEW_PR`; existing Objective-015 PR: none.
- Base: remote `main` at
  `87ed2cea43a0a8706efe485b9b625dfda7cf75aa`.
- Required fresh branch: `oap/015-upstream-diagnostics-compiler-truncation-rc8`.
- Required PR title: `Repair upstream diagnostics and compiler truncation; qualify private RC8`.
- PR must be non-draft. Coding never merges or enables auto-merge.
- No open PR exists and no `015-*` order/report exists. `oap/active` is
  `014-h`; Objective 014/PR #19 is merged and finished. This is a new numeric
  objective and must not amend Objective 014.
- Main CI run 36943908873 and CodeQL run 36943908429 are successful at the
  base. They are historical starting evidence and cannot qualify RC8. Main is
  not branch-protected; zero open code-scanning alerts were independently
  observed.
- The local checkout is stale and has pre-existing untracked paths `Local`,
  `clean`, and `unchanged`. Preserve them. Fetch and branch from the exact
  remote base without deleting, modifying, or committing them. If remote truth
  differs before mutation, stop unsafe work and report the exact blocker.

## Current immutable release and evidence state

RC7 remains immutable and historically authoritative:

```text
RC: 0.1.0-rc7
source: ae6271318627703785f42de57d893c9be3b980c9
image: ghcr.io/ulfe-lmi/slaif-local-coding@sha256:a3782915da58a403fd0f7991c57f9954b07bfb9377e4730715c0fb7398f901db
wheel sha256: 897ef60568e9521dbb4ea563f297608e4409e02d54109471e789d43ff57dd10d
supported client previously qualified: Codex CLI 0.149.0
```

Do not repoint or overwrite `0.1.0-rc7` or
`sha-ae6271318627703785f42de57d893c9be3b980c9`. Preserve every prior RC
archive, record, handoff, provenance artifact, and registry identity.

`oap/evidence/benchmark-harness/001/` and `002/` are immutable. Archive 002 is
explicitly failed/incomplete qualification evidence, not a formal benchmark
result. Do not modify either archive, unpack/rewrite its retained tarball, run
its harness, repair its findings, or create archive/harness 003. The
human-supplied `CODE-DEFECTS.md` is external review input and is not currently a
repository file or part of either archive. Do not claim otherwise. Preserving a
copy is optional and secondary; if done, label it external, preserve its stated
limitations, and do not imply that its private source reports entered repository
evidence.

## Independently verified defect adjudication

Strategy verified both external findings against exact `origin/main` source.
Coding must reproduce these facts before repair and record sanitized evidence.

### P01 — upstream HTTP error causes are discarded

In `src/slaif_local_coding/app.py`, the current `status_code >= 400` branch:

1. preserves the status and only the allowlisted response headers
   `cache-control`, `openai-processing-ms`, `retry-after`, and `x-request-id`;
2. does not read the response body;
3. immediately closes the upstream response;
4. returns the generic public `upstream_error` JSON body;
5. leaves only request count/latency/status facts. The existing
   `slaif_upstream_failures_total{kind=...}` covers timeout, connection,
   disconnect, response-size, and response-read failures but does not classify
   an upstream HTTP rejection.

There is no private bounded HTTP-error cause classifier. The external claim is
therefore correct. This proves an observability defect; it does not prove Local
Coding caused any RC7 rejection.

### P02 — compiler output truncation is collapsed into invalid output

Current compiler facts are:

- `CompilerConfig.max_output_tokens` and `CompilerSettings.max_output_tokens`
  default to 3,000 and permit at most 16,000.
- `max_attempts` defaults to two and permits one through four attempts.
- Every attempt sends the identical `max_tokens` value.
- The OpenAI-compatible chat-completion response is parsed for exactly one
  `choices[0].message.content`, but `choices[0].finish_reason` is never read.
- A length-finished incomplete JSON body therefore reaches strict JSON
  validation and becomes `INVALID_JSON`; the second attempt repeats the same
  known-insufficient allowance.
- Existing metrics count attempts, successes by cache outcome, schema failures
  by validation reason, timeout/transport failures, and duration. There is no
  explicit truncation event. Pipeline metrics expose fixed request state/reason,
  cache/injection/rehydration outcomes, so a compiler failure degrades with
  `compiler_<reason>`, but the wrong `invalid_json` reason currently propagates.
- Only a fully validated index is written to the derived cache; failed output is
  not persisted.

The external claim is correct. It establishes truncation classification and
retry-policy defects; it does not establish that P02 caused Minesweeper coding
errors or a later image-limit failure.

## Workstream A — P01 bounded private classification

Implement the smallest content-safe classification layer before an upstream
HTTP-error response is closed.

1. Add validated product settings with these defaults:
   - `upstream_error_diagnostic_max_bytes = 16384`, constrained to a positive
     finite hard ceiling no greater than 65536;
   - `upstream_error_diagnostic_timeout_seconds = 1.0`, constrained to a
     positive finite ceiling no greater than 5 seconds.
   Name/place the fields consistently with the existing schema, templates, docs,
   source-input/provenance machinery, and strict unknown-field behavior.
2. Read at most the configured diagnostic byte allowance and for at most the
   configured duration. Use streaming iteration and append/process only the
   remaining permitted slice; a single oversized chunk must not cause retained
   bytes to exceed the allowance. Stop and close immediately at the bound.
   Timeout, cancellation, malformed content, or read error must still close the
   response and promptly return the generic public error.
3. Parse only a bounded complete JSON object in explicitly supported provider
   shapes. Inspect only allowlisted structured locations such as the top-level
   error object and fixed `code`, `type`, `param`, and `message` fields. Numeric,
   null, collection, or otherwise unexpected provider codes/types must never
   crash classification. Raw strings may be examined transiently only by an
   explicit fixed matcher table; they must never be returned, logged, persisted,
   or used as labels.
4. Normalize to this closed enum exactly or a semantically identical closed
   enum justified in the report:
   `authentication`, `rate_limit`, `image_count_limit`,
   `context_length_limit`, `malformed_input`, `upstream_5xx`, `unknown`.
   Status-derived authentication/rate-limit/5xx classification is permitted.
   Image/context/parser classification requires sufficient allowlisted
   structured or fixed-pattern evidence. Unknown, malformed, incomplete,
   oversized, unsupported, or ambiguous evidence is `unknown` except where the
   HTTP status alone establishes one of the status-derived categories.
5. Add a dedicated private low-cardinality HTTP-error counter, or an equivalently
   clear existing-metric extension, using only bounded labels: endpoint, route,
   status class, and closed reason. Do not use provider text, provider code,
   prompt/tool/model output, request-derived identity/path, exact private URL,
   credentials, or arbitrary status/body values as labels.
6. Keep the client-facing error status, generic JSON body, and selected safe
   headers compatible and unchanged. Do not forward any upstream error body or
   arbitrary provider text. Preserve transport-failure meaning, successful
   response behavior, SSE streaming, request/status counters, and forwarding.

### Mandatory P01 regressions

Use controlled fake upstreams to prove:

- sufficiently evidenced image-count, context-length, malformed/parser,
  authentication, rate-limit, and upstream-5xx cases map to distinct expected
  private classes;
- non-JSON, malformed JSON, unexpected shape, unknown code, numeric/unexpected
  types, empty body, and incomplete body safely become `unknown` where status
  does not independently classify them;
- one chunk larger than 16 KiB, many chunks crossing the limit, a stalled body,
  and malformed UTF-8/binary data never exceed the retained/processed diagnostic
  bound, never exceed the diagnostic time bound beyond ordinary scheduling
  tolerance, and always close the response;
- correct original HTTP status, generic public error, and selected safe headers
  reach the caller;
- unique sentinel strings from every fake provider body are absent from public
  responses, captured logs, generated metrics/labels, reports, and persisted
  artifacts;
- existing request/status counters remain correct, transport failures remain
  distinct, and successful/streaming paths are unchanged.

Do not fabricate the lost RC7 context-BOTH body or label a synthetic case as a
historical observation.

## Workstream B — P02 typed truncation and bounded adaptive retry

Implement deterministic bounded adaptive retry for explicit length completion.

1. Add `FailureReason.OUTPUT_TRUNCATED` (serialized as
   `output_truncated`) and inspect the actual supported chat-completion schema.
   A response with exactly one choice and `finish_reason == "length"` must yield
   this typed outcome before content JSON/schema validation. A normally
   completed malformed body remains `INVALID_JSON` or the existing precise
   schema failure. Missing/unsupported response structure must fail closed under
   an appropriate existing invalid-output category, not masquerade as
   truncation.
2. Add validated `max_output_tokens_ceiling`, default 8,000, range 128 through
   the existing legal maximum 16,000, and require it to be at least the initial
   `max_output_tokens`. Keep the initial default 3,000.
3. On explicit truncation, the next permitted attempt uses
   `min(previous_allowance * 2, max_output_tokens_ceiling)`. Never repeat a
   known-insufficient allowance. If no larger allowance is legal or no attempt
   remains, stop with `OUTPUT_TRUNCATED`. Existing `max_attempts` remains the
   per-compilation hard attempt bound; no loop may exceed it. Other completed
   validation failures retain current bounded retry semantics unless concrete
   evidence requires a narrower safe correction.
4. Bump/version the compiler behavior and cache/provenance identity so old and
   new compilation policies cannot be confused. Include both initial allowance
   and ceiling in request deduplication fingerprints, persistent cache keys,
   source-input maps, strict records, config hashes, templates, and tests. A
   cache-key/schema/version change must be explicit and deterministic.
5. Add a dedicated content-free truncation counter or a precise fixed reason on
   the existing compiler failure metric. Metrics must distinguish attempt,
   validated success, explicit output truncation, completed invalid JSON/schema,
   timeout/transport/status failure, degraded pipeline result, cache write,
   cache hit, and successful constitution injection using unambiguous existing
   or new counters. Document that compiler attempts are per direct upstream
   compiler request, the attempt limit is per compilation leader, cache hits use
   zero attempts, and process counters are cumulative.
6. Never validate or persist a partial/truncated governance index. Preserve the
   direct, tool-free, non-recursive compiler boundary; one global compiler slot;
   prompt/source/privacy bounds; and preserve-original degradation policy.

### Mandatory P02 regressions

Use deterministic fake upstreams to prove:

- syntactically incomplete content plus `finish_reason="length"` is
  `OUTPUT_TRUNCATED`, never `INVALID_JSON`;
- malformed JSON plus a normal completion reason remains a distinct invalid
  complete-output failure;
- after first-attempt truncation at 3,000, a second request uses 6,000, remains
  below the 8,000 ceiling, and a valid second response compiles and caches;
- repeated truncation reaches neither an identical allowance nor an attempt
  beyond the configured count/ceiling and terminates explicitly as truncated;
- initial allowance equal to ceiling cannot cause an identical blind retry;
- a representative synthetic governance corpus large enough to exercise the
  output-size path produces every required index field under the validated
  policy;
- one intended cache write follows a successful validated compilation, a
  subsequent hit behaves unchanged, and truncation/invalid/local-output-overflow
  produce no cache entry or rehydration entry;
- attempt count, token ceiling, response byte bound, JSON-depth bound, timeout,
  cancellation, and global-concurrency bounds remain enforced;
- metrics and pipeline result show truncation, eventual success/cache outcome,
  degradation, and actual injection without any source/path/identity/content in
  labels.

## Workstream C — scope and durable documentation

Keep Objective 015 strictly about P01 and P02. Do not add CACHE image pruning,
an image histogram, Codex history validation/rewriting, benchmark-driver changes,
task/judge changes, model/vLLM changes, or speculative fixes for high prompt
totals, Codex retry behavior, cache corruption, rehydration, image retention, or
Minesweeper quality. Do not reinterpret archive 002.

Update focused product/config/operations/testing/release history only as needed:

- describe the private error-classification contract and its privacy/bounds;
- describe typed compiler truncation and the exact adaptive policy, ceiling,
  attempt scope, metrics, cache identity, and failure/degradation behavior;
- state that archive 002 is failed/incomplete qualification context and the
  external review motivated independently verified P01/P02 repairs;
- state that RC8 repairs these product defects while making no claim that Local
  Coding caused the rejected requests or task mistakes;
- preserve README as product documentation rather than an OAP ledger;
- state standalone Local Coding qualification needs no Gateway, the benchmark
  was not run, final public release is false, registry visibility is private,
  and protected cutover is false.

## Workstream D — RC8 freeze, publication, and full qualification

1. Reconcile the established release scripts, schemas, archives, provenance,
   current record/handoff, publisher collision guards, workflows, and RC history.
   Archive RC7 current record/handoff/provenance exactly according to repository
   convention before advancing current metadata. Preserve all prior archives.
2. Update explicit candidate constants from RC7 to `0.1.0-rc8` without weakening
   final/stable tag denial or collision protection. Before any registry write,
   authenticate and prove both `0.1.0-rc8` and
   `sha-<exact-RC8-source-commit>` are absent. Fail closed if either exists or
   registry state is ambiguous. Never overwrite, complete, or repoint an
   occupied identity.
3. Freeze final product/source inputs only after P01/P02 code, tests, config,
   docs, locks, release machinery, and provenance inputs are complete. Establish
   exact image-source commit `S`, reproducibly build wheel/sdist, and record wheel
   SHA-256 `W`. No artifact input may change after `S`; only mechanically proven
   excluded derived metadata/OAP commits may follow.
4. Require fresh source-head CI and CodeQL/security success before registry
   mutation. Publish privately through the repository's guarded workflow so
   exactly `0.1.0-rc8` and `sha-<S>` resolve to one new digest `D`. Verify
   workflow checkout/head, source map, wheel, lock, labels, and registry privacy.
5. Generate strict current RC8 machine record, human handoff, provenance, and
   archives from authenticated facts. Preserve RC7 unchanged and resolvable.
6. Run the repository's complete current RC qualification, including:
   `uv lock --check`, frozen dev sync, Ruff, format, mypy, docs consistency,
   full pytest, build, exact reproducibility on the supported builders,
   artifact-policy inspection, clean noneditable wheel install smoke,
   compileall/shell syntax as applicable, source-input/provenance equality,
   Gateway contract CI, normal Docker, operator session, CodeQL/current security
   gates, and fresh exact-head CI.
7. The `docker-published` gate must pull `D` without rebuilding and qualify the
   actual image by digest: supported `linux/amd64`, tag/digest equality, OCI
   revision/version/RC/wheel/Gateway/topology labels, retained in-image wheel
   hash `W`, exact dependency-lock inventory, noneditable install, hardened
   container properties, readiness/fail-closed behavior, lifecycle, forbidden
   content, and teardown/listener/process/cache absence. A prepublication skip or
   locally rebuilt image is not acceptance.
8. Add focused controlled P01 qualification proving known rejections normalize
   privately while public bodies stay generic and sentinel-free. Use the
   designated test backend only when safe and bounded; fake upstream proof is
   mandatory and cannot be weakened by backend availability.
9. Add focused P02 qualification proving normal compilation, explicit
   truncation, adaptive success and exhausted degradation, cache write/hit only
   after validation, no partial cache entry, and request-level successful
   treatment delivery. Use a sufficiently large synthetic governance fixture.

## Workstream E — standalone genuine-Codex RC8 smoke

Repeat the bounded repository-owned release-candidate compatibility gate after
RC8 is published. No SLAIF API Gateway is involved:

```text
disposable Codex home/repository -> 127.0.0.1:18031 RC8 Local Coding
                                 -> existing tested OpenAI-compatible backend
```

- Use exact Codex CLI 0.149.0 first. Verify its version and binary hash. If
  0.149.0 cannot be established for a reason unrelated to RC8, the human has
  authorized one later installed version; use one exact fallback version/hash
  consistently for all four arms, explain why, and never label it 0.149.0.
- VISION: adapter present, image compatibility enabled, constitution/compiler
  disabled; a genuine tool-bearing loop completes.
- CACHE: image passthrough, constitution/compiler enabled with supported static
  single-user identity; a genuine tool-bearing loop completes and evidence
  proves compiler/cache success plus successful constitution injection/treatment.
- BOTH: both mechanisms enabled; a genuine tool-bearing loop completes and
  evidence proves compiler/cache success plus successful treatment delivery.
- DIRECT: the same Codex/backend direct path completes as contextual control.
- Use fresh, isolated, disposable homes/repositories/cache/state per arm or
  prove isolation. Gateway ingress is disabled and no signed-Gateway headers are
  invented. Bind candidate Local Coding only to loopback 18031. Bound requests,
  attempts, compiler calls, tool calls, output bytes, wall time, and concurrency;
  run serially. Retain only sanitized counts, closed states, hashes/versions,
  timings, and booleans. Remove raw disposable state after extracting evidence.
- If the genuine client/backend is unavailable or any required arm/treatment
  fact fails, report `BENCHMARK_BLOCKED`. Synthetic tests alone cannot establish
  readiness. Do not change the backend or weaken product-side regressions.

## Protected-host and security law

The verified protected listener is PID 23961 on `0.0.0.0:18020`, executing the
existing qwen-serving vLLM command with model `qwen3.8-27b`; 18021 and 18031 were
absent before this order. The coding OAP loop is waiting on the control FIFO.
Recheck listener/PID/unit/command/model facts before and after live work.

This order permits read-only inspection, bounded authenticated calls to the
documented test backend, a disposable repo/wheel/image-owned adapter on loopback
18031, and private GHCR publication of the two new RC8 aliases. It forbids any
mutation of port 18020, `/synology/homes/janezp/qwen-serving`, vLLM packages or
venv, launch flags, service units, model/checkpoint/quantization/context/tool or
reasoning parser, CUDA stack, GPU assignment, firewall/VPN/network bindings,
production Gateway, API keys, and active Codex profiles. Do not install, patch,
restart, stop, or reconfigure the existing backend. Do not use host Docker in a
way that can affect the protected GPU service.

Never print or persist credentials, raw prompts, source, images, tool arguments
or output, model output, arbitrary upstream error bodies/messages, private
identity values, or session IDs. Sanitize command output before reports. Local
routine repo setup belongs to coding; do not recruit the human as terminal
operator.

## Acceptance criteria

1. Exactly one non-draft Objective-015 PR exists from the exact base on the
   required branch; coding never merges.
2. P01 pre-fix behavior is reproduced and the repair hard-bounds bytes/time,
   closes every response, emits only a closed private reason, leaks no raw body,
   and preserves generic public status/body/header and all success/streaming/
   transport semantics.
3. Every mandatory P01 category, unknown, chunk-bound, timeout, cleanup,
   counter, and sentinel privacy regression passes.
4. P02 pre-fix behavior is reproduced. Explicit length completion becomes
   `OUTPUT_TRUNCATED`; complete malformed output remains distinct; adaptive
   allowance increases deterministically within ceiling/attempt bounds and
   never repeats a known-insufficient allowance.
5. Every mandatory P02 success/exhaustion/corpus/cache/resource/metric/
   treatment-delivery regression passes. No partial invalid index is cached or
   injected.
6. Config, compiler/cache behavior version, fingerprints, cache keys,
   provenance/source maps, templates, docs, and metrics truthfully bind the new
   limits and policy.
7. Benchmark archives 001/002, all prior RC archives/tags/digests, and RC7 in
   particular remain byte-for-byte/registry unchanged. No excluded product,
   benchmark, Codex, Gateway, or vLLM work occurs.
8. Fresh local and GitHub qualification is fully green, including every current
   ordinary job and CodeQL/security check, with none missing, pending, failed,
   cancelled, or skipped where required.
9. Private RC8 exists at one authenticated immutable digest `D`; both new aliases
   resolve to `D`; actual pulled-image-by-digest qualification passes; source,
   wheel, lock, labels, inventory, provenance, hardening, readiness, and teardown
   bind exactly.
10. Genuine Codex VISION, CACHE with treatment, BOTH with treatment, and DIRECT
    control all pass using 0.149.0 or one explicitly justified later fallback.
11. The current machine record and handoff point to RC8 and contain: RC ID, `S`,
    `D`, both aliases, `W`, build-tool pins, dependency lock hash,
    configuration/source-input hashes, Codex version/hash, four smoke results,
    supported platform, private-registry authentication requirement,
    Gateway-not-required fact, benchmark-not-run, final-public-release-false,
    and protected-cutover-false.
12. `BENCHMARK_READY` appears only if every criterion above is true. Otherwise
    report `BENCHMARK_BLOCKED` with exact remaining product blocker(s).

After strategic merge, strategy will independently require remote main to
contain the accepted PR and fresh post-merge main CI and CodeQL to succeed before
the final readiness verdict. Coding must not merge.

## GitHub publication and immutable report contract

1. Commit the byte-exact published `015-a` order and `oap/active=015-a` with the
   implementation. Create the required fresh branch/PR from exact remote base.
2. Push all implementation, tests, docs, release metadata, qualification
   evidence, and PR metadata before reporting. Inspect and fix in-scope failures;
   do not hide skips or failures.
3. Create exactly one report matching `oap/reports/015-a-*.md`. It must identify
   the repository, PR number/URL/base/branch, every implementation commit, exact
   final implementation SHA, changed paths, external-review adjudication,
   behavior/config decisions, test commands/results/counts, CI/CodeQL run/job
   URLs and conclusions, source/artifact/registry identities, pulled-image
   evidence, real-Codex evidence, protected-host before/after facts, privacy and
   non-goal audits, residual risks, and the strict verdict.
4. The report may contain only sanitized normalized facts. It must explicitly
   state that `CODE-DEFECTS.md` was external human input and that no benchmark
   run occurred.
5. Before the report commit, all claimed implementation and PR state must be
   remote. The final report publication commit must change only the exact report,
   its sole parent must equal the literal reported implementation SHA, and the
   report must state `Report publication commit: SELF`. Push it as the PR head.
   Fresh report-head checks may be pending; report them honestly and strategy
   will wait and verify independently.

Never merge. Strategy alone reviews, requests continuation if needed, and
merges only after every acceptance criterion and required check is satisfied.

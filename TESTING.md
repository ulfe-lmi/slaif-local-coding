# Testing and verification

Start with the locked local gate below. Most tests use synthetic requests and
fake upstreams; they need neither a model server nor a Gateway deployment.
Live model, actual Codex and Docker qualification are separate layers with
explicit prerequisites.

Report results as `PASSED`, `FAILED`, `SKIPPED`, `NOT RUN`, `BLOCKED`,
`PENDING` or `MISSING`. An unavailable fixture or skipped test is never a pass.

## Local gate

Use Python 3.12 and the pinned uv toolchain from the build provenance:

```bash
uv lock --check
uv sync --frozen --extra dev
uv run --frozen ruff check .
uv run --frozen ruff format --check .
uv run --frozen mypy src tests
uv run --frozen python scripts/docs_consistency_check.py
uv run --frozen pytest -q
uv build
uv run --frozen python scripts/artifact_policy_check.py --dist dist --inspect
uv run --frozen python scripts/artifact_policy_check.py --dist dist --install-smoke
```

The full pytest suite requires the verified non-root **process-local umask
022** test context on this development host:

```bash
umask 022
uv run --frozen pytest -q
```

The canonical host umask 0002 makes newly owned pytest tmp fixtures group-
writable, which the safe-evidence validators correctly reject as
`destination_component_writable` before the tests' intended later rejection
classes (12 ordering failures); umask 077 masks the intentionally 0755
untrusted-cache fixture to 0700 and breaks one separate fixture-mode
expectation. At accepted 016, umask 022 passed the complete gate with 1543
passed, 27 skipped, 0 failed. Never change global/home permissions to avoid
this context, never loosen the intentional permission-negative fixtures (the
0755 untrusted-cache directory; the execute-only-ancestor test that skips on
UID 0), and create explicitly protected temporary roots/files with 0700/0600
where a test requires them.

Artifact tests build fresh artifacts and compare provenance with the actual
source-input map. An intentional README/source change can require a new accepted
wheel identity and regenerated provenance; never suppress a mismatch just to
make the gate green. Follow [the artifact policy](docs/RELEASE-ARTIFACT-POLICY.md)
for clean rebuilds and RC freezing.

## What the suites cover

| Layer | Required behavior |
| --- | --- |
| API and fake upstream | Responses/Chat forwarding, safe errors, header filtering, body/JSON bounds, usage, function-tool continuation, incremental SSE, timeout and disconnect cleanup. |
| Image policy | Zero/one unchanged; multiple retain newest only on the selected route; non-image order preserved; reject and unsafe-shape cases. |
| Governance | Evidence-based root detection, deterministic candidates, separate confidence/priority, strict compiler schema, direct compiler bypass, dependency pairing and acquisition bounds. |
| Cache and injection | Identity isolation, hash/version invalidation, TTL/LRU/bytes, stable selection, idempotent injection, essential-overflow fallback and process-local rehydration. |
| Signed ingress | Service-auth ordering, canonical HMAC bytes, duplicate/grammar handling, timestamp edges, secret separation, route mismatch, replay concurrency/capacity/clock failures and header stripping. |
| Privacy and security | No raw content or secrets in logs/metrics/artifacts, safe paths and permissions, adversarial envelope inputs and response-header handling. |
| Documentation | Required landing/install pages, working relative links, current claims, pull-only operator path and protected secret-file preparation. |
| Packaging | Explicit artifact contents, fresh non-editable installation, exact wheel/input-map binding and recorded toolchain. |

## Planned dependency-bundle cache profile (v1)

The approved dependency-bundle cache rework
([docs/CACHE-REWORK.md](docs/CACHE-REWORK.md),
[docs/CACHE-IMPLEMENTATION-PLAN.md](docs/CACHE-IMPLEMENTATION-PLAN.md)) is
delivered in planned implementation stages tracked by [the stage
ledger](docs/CACHE-REWORK-LEDGER.md). The legacy-profile suites above
continue to cover the currently implemented behavior. The planned v1
layers, per the ledger's owning stage, are:

- versioned real-format root/read/result/span fixtures, including combined
  multi-file reads, absolute workspace paths, literal loops, truncation
  and Unicode/CRLF edges, with no shell execution in detection
  (D01–D10);
- recursive graph closure, lean/greedy admission, independent ordered
  bundle identity, overlap/replay invalidation and cross-namespace
  isolation (G01–G05, C01–C02, C04–C06, S01);
- RAM session ownership, async single-flight, explicit
  capacity/backpressure and zero filesystem hot-path reads
  (C03, M01, M04, M05);
- protected exact-original checkpoints with corrupt/torn/foreign and
  configuration-mismatch negatives, and lazy per-session restart
  rebuilding (M02–M04);
- pinned actual-model tokenizer budgets (C/32 slots, aggregate limit and
  reserves), typed compiler failure/truncation/overflow states, no-retry
  and compile-once behavior (B01–B04, C03);
- transactional source replacement proven against the actual upstream
  body, idempotence under replayed history, forged/stale reference
  rejection, and source-role authority preservation (R01–R05, S01–S02);
- a full fake-stack adversarial/lifecycle/isolation/cancellation matrix
  with stage-accurate telemetry and the whole-rework acceptance rules
  (O01–O03); and
- bounded actual-model and genuine-Codex qualification with synthetic
  tasks, serial bounded requests and complete teardown.

Stage 017 (tracked in the stage ledger) has landed the D01-D08 observation
slices of the first item as the inert pure observation package
`src/slaif_local_coding/constitution/bundles/` (never active in the adapter;
the legacy detector unchanged), exercised by the named pure suites
`tests/test_bundle_*.py` over the versioned synthetic fixtures in
`tests/fixtures/cache_bundles/v1/` and the canonical sanitized 0.149.0
fixture; the offline process-capture utility `scripts/real_client_capture.py`
is inert and input-gated (`tests/test_real_client_capture.py`; observation
contract section 12). The per-round corrections, the per-suite test counts and
the actual-attempt outcomes are NOT restated here: the per-criterion EARNED /
RECOGNIZED-ONLY / UNSUPPORTED / NOT RUN states are in the required-syntax
matrix (observation contract section 11b), and the per-round historic counts
and measured outcomes are in [the stage
ledger](docs/CACHE-REWORK-LEDGER.md) and the immutable OAP round reports.
The serial native-fixture qualification lineage (its exact immutable
report paths are listed in the compact qualified-status lineage) is:
017-x (bounded Python-only capability, closed terminal FAIL),
017-y (readiness diagnosis, closed PASS, the executable a closed UNKNOWN),
017-ab (bounded Python-only capability, closed terminal PASS at diagnostic
scope), 017-ad (closed PARTIAL, the ordered native handoff NOT RUN - never
PASS, never waived), 017-af (closed FAILED, one admission spent forever),
017-ah (qualified at the bounded diagnostic scope), and 017-aj (qualified the
real native format at the bounded reference-fixture scope; the measured
native_ready=true verdict is bounded to that attempt). The binding
native-fixture law (frozen bounds, one-attempt / spent-namespace, owner-UID
identity, confinement, expected-PTY, publication / qualification) is normative
in the compact `## Objective boundaries` section and versioned in observation
contract sections 11a-11q. D10 keeps its composition matrix and D09 keeps
its unsupported / partial-negative matrix as required acceptance surfaces;
the D09 process / chunk collector is exercised by the named pure suite
`tests/test_bundle_process_chunks.py` (017-al pure inert collector plus
017-am already-exited single-final acquisition and the final-cat
execution-evidence contract, observation contract sections 5a and 11q,
with the read-surface evidence tests in
`tests/test_bundle_tool_results.py::TestFinalCatEvidence`).  The D09
actual-trace process-completion qualification is qualified AT BOUNDED
SCOPE (017-am): the original selected AJ frames (hash-verified native run
record) fed through the public composition with an EXPLICIT carrier
conversion, both endpoints, four cases (section 11q) — the sleep-bearing
stream command remains an UNEARNED read grammar (process complete, no
source attribution), and the EACH seven required literal read
families were concretely audited in 017-am (the residual 5/6/7
uncertainties are preserved as process qualifications). No GENERIC native-compatibility, whole-017 or v1 runtime claim
is made (the bounded AJ native_ready=true verdict above stays the only
native readiness recorded). Whole-017 acceptance, merge and remote-main
verification completed under the 017-am decision (merged to main at
ffaabf4b); 018-024 proceed under separately activated orders,
strategy-chosen (018 active: 018-a foundation slice ACCEPTED at its
bounded inert graph-foundation scope with process qualifications (the
018-a strategic decision, `reviews/018-a-decision.md`; contract
[docs/CACHE-GRAPH-CONTRACT.md](docs/CACHE-GRAPH-CONTRACT.md)), 018-b is an implemented inert bundle-proof bridge slice ACCEPTED at its
bounded scope with process qualifications (the 018-b strategic decision,
`reviews/018-b-decision.md`; contract
[docs/CACHE-BUNDLE-PROOF-CONTRACT.md](docs/CACHE-BUNDLE-PROOF-CONTRACT.md);
`tests/test_bundle_proof.py`), 018-c is an implemented inert
bundle-admission and structural-identity slice ACCEPTED at its bounded
inert admission/structural-identity scope with process qualifications
(strategic decision `S/reviews/018-c-decision.md`; contract
[docs/CACHE-BUNDLE-ADMISSION-CONTRACT.md](docs/CACHE-BUNDLE-ADMISSION-CONTRACT.md);
`tests/test_bundle_admission.py`, `tests/test_bundle_admission_vectors.py`),
018-d is an implemented inert causal-occurrence-ledger slice
ACCEPTED at its bounded inert scope with process qualifications
(strategic decision `S/reviews/018-d-decision.md`; contract
[docs/CACHE-CAUSAL-HISTORY-CONTRACT.md](docs/CACHE-CAUSAL-HISTORY-CONTRACT.md);
`tests/test_causal_history.py`, `tests/test_causal_history_models.py`),
018-e is an implemented inert nonroot currentness-overlay slice
ACCEPTED at its bounded inert currentness/overlap-overlay scope
with process qualifications (strategic decision
`S/reviews/018-e-decision.md` + addendum; contract
[docs/CACHE-CURRENTNESS-CONTRACT.md](docs/CACHE-CURRENTNESS-CONTRACT.md);
`tests/test_currentness.py`, `tests/test_currentness_models.py`),
018-f is an implemented inert current-graph-closure slice
ACCEPTED at its bounded inert current-graph scope with process
qualifications (the 018-f strategic decision,
`S/reviews/018-f-decision.md`; contract
[docs/CACHE-CURRENT-GRAPH-CONTRACT.md](docs/CACHE-CURRENT-GRAPH-CONTRACT.md);
`tests/test_current_graph.py`, `tests/test_current_graph_models.py`),
018-g is an implemented inert current-bundle-admission slice
ACCEPTED at its bounded inert current-admission scope with process
qualifications (the 018-g strategic decision,
`S/reviews/018-g-decision.md`; contract
[docs/CACHE-CURRENT-ADMISSION-CONTRACT.md](docs/CACHE-CURRENT-ADMISSION-CONTRACT.md);
`tests/test_current_admission.py`),
018-h is an implemented inert root-authority-lineage slice
ACCEPTED at its bounded inert root-authority-lineage scope with
process qualifications (the 018-h strategic decision,
`S/reviews/018-h-decision.md`; contract
[docs/CACHE-ROOT-LINEAGE-CONTRACT.md](docs/CACHE-ROOT-LINEAGE-CONTRACT.md);
`tests/test_root_lineage.py`),
018-i is an implemented inert current-root-composition slice
NOT ACCEPTED at its bounded inert scope (the 018-i strategic
decision, `S/reviews/018-i-decision.md`); the bounded 018-j
repairs (J01 association closure, J02 exact reverse-index law,
J03 independent budget domains) were delivered truthfully
PARTIAL and are NOT ACCEPTED against the complete J01/J02/J03
criteria (strategic decision `S/reviews/018-j-decision.md`); the
bounded 018-k repairs (K01 actual nested canonical keys at BOTH
parent boundaries, K02 actual nested row shapes before
exact-relation comparison, K03 genuinely reachable E collection
caps with exact evidence labels) are NOT ACCEPTED against the
complete K01/K02/K03 criteria (strategic decision
`S/reviews/018-k-decision.md`); the bounded 018-l repairs (L01
complete closed nested entry / key-record / ownership metadata
fences at the leaf and BOTH parent boundaries with the entry /
record authority and width joins, L02 independently derived
actual E collection-domain counts with a before-target charge
sentinel) were delivered truthfully PARTIAL and are NOT
ACCEPTED against the complete L01/resource/artifact criteria
(strategic decision `S/reviews/018-l-decision.md`); the bounded
018-m repairs (M01 O(1) count / scalar gates BEFORE any element
/ set / sort / hash / serialization work at the leaf and BOTH
parent boundaries, with the closed TEN admission bound-model
fence and the accepted dense group ordering / unique partition
law; M02 the exact accepted JSON serialization byte ceiling and
the reservation-calculation work precharge on the ONE I outer)
were delivered truthfully PARTIAL and are NOT ACCEPTED against
the complete M01/M02 criteria (strategic decision
`S/reviews/018-m-decision.md`); the bounded 018-n repairs (N01
the retained-content join at the leaf and BOTH parent
boundaries (the entry-local group partition joined to the
ORIGINAL proof segments and the root group to the retained root
digest), plus N02 the byte-aware closed reservation, the
pre-fetch plan segment precharge and the per-site
reservation-calculation closure) are ACCEPTED at their
bounded inert scope WITH PROCESS QUALIFICATIONS
(strategic decision `S/reviews/018-n-decision.md`); the 018-o
root-aware mixed-observation slice (the new pure
`observe_root_lineage_mixed` operation plus
`ROOT_LINEAGE_MIXED_OBSERVATION_VERSION`; a proven mixed root
member matching an independently authoritative known version
of the same effective root — including an independently
issued complete whole singleton in the SAME batch — acquires
source evidence while a mixed read mints no governing
authority, unresolved foreign digests keep the exact
COMPETING_ROOTS refusal, and the pending-set snapshot is
precharged on the SAME H outer) is implemented and ACCEPTED at
its bounded inert scope WITH PROCESS QUALIFICATIONS (strategic
decision `S/reviews/018-o-decision.md`; contract
[docs/CACHE-ROOT-LINEAGE-CONTRACT.md](docs/CACHE-ROOT-LINEAGE-CONTRACT.md)
section 5a; `tests/test_root_lineage_mixed.py`); plus the 018-p
versioned root-region authority producer (the separate
`cache-root-region-lineage/v1`/`root-region-lineage-policy/v1`
contract and the `read_region` provenance kind: a genuinely
issued complete NEW root region in a mixed-only read acquires
source evidence AND authority with NO independent singleton,
repeated/opaque/partial/truncated/nonzero/unpaired/unsupported
reads gain no exception, retention is preflighted before
materialization under the unchanged H ceilings, ONE
new-operation outer at the unchanged RootLineageBounds, the old
H/O law unchanged, the existing old I honestly refusing the
region-version state, and the closed host-IO purity surface
enforced on every public path) is ACCEPTED at its bounded
inert producer scope WITH PROCESS QUALIFICATIONS
(strategic decision `S/reviews/018-p-decision.md`;
contract
[docs/CACHE-ROOT-REGION-LINEAGE-CONTRACT.md](docs/CACHE-ROOT-REGION-LINEAGE-CONTRACT.md);
`tests/test_root_region_lineage.py`); the 018-q
versioned root-region currentness slice is a separate
pure QUERY over the 018-p state (an unresolved MAXIMAL
trusted root uncertainty — a trusted complete root-bearing
observation whose governing root cannot be established
under P source policy, later or incomparable to the known
root — makes the known authoritative root not currently
usable, while dominated historical uncertainty is retained
and never permanently blocks; the query mints no root
authority, changes no P selection and advances no
revision; the combined frozen-partial-order frontier,
the closed evidence/exclusion table, the stable scope key
and the ONE Q outer with the ACTUAL independent P
domain) is ACCEPTED at its bounded inert
query scope WITH PROCESS QUALIFICATIONS AND
HISTORICAL-REPORT CORRECTIONS (strategic decision
`S/reviews/018-q-decision.md`; contract
[docs/CACHE-ROOT-REGION-CURRENTNESS-CONTRACT.md](docs/CACHE-ROOT-REGION-CURRENTNESS-CONTRACT.md);
`tests/test_root_region_currentness.py`); the 018-r
versioned root-region selected source and current graph
slice is a separate INERT consumer derivation over the
018-p state and namespace (ONE bounded operation that
derives the ACTUAL same-run Q currentness, resolves the ONE
deterministic selected root source — envelope from the
actual immutable D anchor, whole read with its complete
singleton proof, or region joined to the SAME original
retained objects with the root interval from preceding
original segment CHARACTER lengths and closed preflights
before any owned slice/encode/hash/copy — and derives the
ACTUAL accepted current graph under that selected root under
ONE R outer with every inherited domain independently
binding; the EXACT input state retained on every outcome and
no usable source/graph on any non-ready outcome) is
implemented and PENDING strategic review at its bounded
graph-only scope (contract
[docs/CACHE-ROOT-REGION-GRAPH-CONTRACT.md](docs/CACHE-ROOT-REGION-GRAPH-CONTRACT.md);
`tests/test_root_region_graph.py`),
and the remaining 018 stages (including the separate
same-018 admission/full-result consumer) plus 019-024 remain
mandatory unearned stages).

All v1 runtime criteria remain `NOT RUN` until their owning stage lands. The versioned
contract is documented in
[docs/CACHE-OBSERVATION-CONTRACT.md](docs/CACHE-OBSERVATION-CONTRACT.md).

A stage-scoped synthetic unit/fake test proves its named mechanism within
that stage; it never substitutes for actual-model, genuine-Codex,
native-compaction or artifact qualification. A criterion passes only after its own
required evidence layers pass and are reviewed: pure/unit/fake criteria may
be proven by their named layers, whereas actual-model, genuine-Codex,
native-compaction and artifact claims require their distinct evidence. All v1 runtime criteria are `NOT RUN`
(planned) until their owning stage lands, is implemented, is tested at every
required layer, and is reviewed; no legacy or fixture result substitutes for
them, and a recognized root with absent dependencies fails overall rework
acceptance (O01).
RC10 is the historical baseline for the rework, not a rework-qualified
artifact. The planned v1 configuration surface is documented as planned
and non-runnable in [the configuration
reference](docs/ADAPTER-CONFIGURATION.md); its examples are not runnable
until the configuration implementation lands.

## Gateway contract tests

The dedicated `gateway-contract` job checks out the exact peer in
[the authority fixture](tests/fixtures/gateway/current_peer_authority.json),
verifies origin/HEAD/module metadata, and executes the focused pure contract
suite with network access denied. It rejects zero collection, any skip, failure,
error or incompatible metadata. The normal suite can run without that checkout;
Gateway-dependent modules then skip explicitly.

See [GATEWAY-CONTRACT-CI.md](docs/GATEWAY-CONTRACT-CI.md) for the optional local
command and dependency group. A development peer update does not silently change
a frozen release's Gateway authority.

## Docker and operator qualification

Run Docker qualification only on a disposable Docker host, never implicitly on
the protected model host. CI owns the canonical executions:

| Job | Evidence |
| --- | --- |
| `test` | Lint, format, types, unit/fake tests, documentation and artifact gates. |
| `gateway-contract` | Exact pinned Gateway compatibility with no inference or service activity. |
| `docker` | Fresh built image, actual platform/dependency/wheel identity, signed ingress, readiness, hardening, lifecycle and teardown. |
| `operator-session` | Documented pull-based operator lifecycle against a synthetic registry and fake upstream. |
| `docker-published` | Authenticated pull and qualification of the recorded immutable digest after publication. |
| `cache-native-containment` | Disposable hosted-runner containment capability proof: pinned-base fixture image, explicit confinement surface (network none, read-only rootfs, nonroot uid, cap-drop ALL, no-new-privileges, seccomp=builtin, bounded memory/pids/CPU/tmpfs), ordered token-bound parent-death proof, verified image removal. No secrets forwarded; the job is a fake/disposable capability proof and never a new actual attempt - the D09 actual-trace process-completion qualification is qualified AT BOUNDED SCOPE in 017-am (observation contract section 11q). |

Before an image is published, `docker-published` reports an explicit
prepublication `NOT RUN` for image qualification while recording registry facts.
After publication it must exercise the actual pulled digest; a missing or
inaccessible recorded image cannot silently skip.

The runners are [docker_qualification_ci.py](scripts/docker_qualification_ci.py),
[operator_session_ci.py](scripts/operator_session_ci.py), and
[disposable_deployment_qualification.py](scripts/disposable_deployment_qualification.py)
for the secondary systemd mechanics. Inspect their `--help` and the exact
[CI workflow](.github/workflows/ci.yml) before running them on a disposable host.
They use fake upstreams and must prove container/unit/listener teardown.

## Live model and actual Codex tests

These require separately authorized access to the exact protected fixture.
Do not restart or reconfigure vLLM, change credentials, or alter active client
profiles to make a test run. Calls must be authenticated, bounded and serialized
where needed to avoid starving existing users. Capture only sanitized facts.

The live matrix covers health/models, Responses text, function tools, SSE,
multi-turn continuation, one-image vision, full-image-then-crop history,
compiler miss/hit behavior, governance sentinels and privacy checks.
Actual Codex tests additionally use a disposable repository and ordinary local
tools to exercise the complete client path. History reduction at the adapter
boundary is distinct from a native Codex compaction trigger; accepted evidence
does not claim the latter.

[The acceptance ledger](docs/OBJECTIVE-004-LEDGER.md) and
[vision fixture record](docs/VISION-ACCEPTANCE.md) describe the historical
fixture-specific results. They do not establish generic model/hardware support.
The repository-only rehearsal and Codex helpers are not runtime product code.
Their detailed safety contracts and prior runs are preserved in
[HISTORY.md](docs/HISTORY.md) and the immutable OAP evidence.

## Release-candidate qualification: fixture CI vs real client

Two distinct mechanisms, never interchangeable:

- **Deterministic fixture CI (every round).** Ordinary CI runs the
  sanitized Codex-envelope fixtures and the full-application
  fake-upstream regressions, including the namespace-tool envelope that
  reproduces the RC2 `TypeError: unhashable type: 'dict'` image-policy
  crash. No secret endpoint, no model, and no real Codex binary are
  required or used.
- **Opt-in real-client RC qualification (only when the designated client
  and backend are available).**
  [real_codex_rc_qualification.py](scripts/real_codex_rc_qualification.py)
  runs bounded, fail-closed, privacy-bounded arms of genuine Codex CLI
  sessions over the supported standalone loopback topology: disposable
  Codex home/repository → `127.0.0.1:18031` Local Coding → the tested
  Qwen/vLLM endpoint. Standalone loopback Local Coding qualification
  requires **no SLAIF API Gateway** (gateway ingress disabled; no signed
  Gateway headers invented). The required arms are VISION (one-image
  retain-newest, constitution/compiler disabled), CACHE (image
  passthrough plus enabled constitution/compiler with a static
  single-user identity), and BOTH (both mechanisms, same identity); a
  contextual DIRECT control may be recorded when safe but never
  substitutes for a product arm. Only fixed categories, counts, statuses,
  version/hash, timings, and boolean verdicts are captured; disposable raw
  state is deleted after sanitized facts are extracted into an
  append-only, content-free testing-ledger directory. The client is
  invoked with the client-side sandbox set to `danger-full-access`
  because the protected host forbids the unprivileged user-namespace
  network setup that bubblewrap requires (a protected host state the
  gate never changes); the effective controls are the disposable
  workspace and Codex home, the loopback-only adapter, the fixed
  synthetic prompt, no credentials in argv, and bounded attempts and
  timeouts.

RC history: RC2 (`0.1.0-rc2`) failed external real-Codex 0.149.0
qualification; the immutable [testing ledger
001](oap/evidence/testing-ledger/001/README.md) records the exact
pre-inference `TypeError` on the VISION/CACHE/BOTH arms. RC3
(`0.1.0-rc3`) contains the image-policy compatibility repair; its
real-client qualification facts (the exact qualified client version and
binary SHA-256, the VISION/CACHE/BOTH verdicts, and the sanitized
evidence path) are recorded in the RC3 artifact record
(`slaif-rc-record-v3` compatibility facts, closed-schema), the
deterministic handoff, and the ledger evidence. A green deterministic
fixture is never real-client evidence, and a missing, unavailable,
skipped, or blocked real-client arm is a blocker, never a pass. No
benchmark ran; the final public release remains false; the package
remains private; the protected cutover remains false. RC4
(`0.1.0-rc4`) qualified in scope (immutable [testing ledger
003](oap/evidence/testing-ledger/003/README.md)) but was rejected
overall: after publication, the record-present suite exposed a stale
RC3 identity residue, the repair committed a post-publication SOURCE
change, and the post-publication provenance rebind recorded that later
source-input map while the record still named the earlier immutable
image source; its record set is archived byte-identical under
`packaging/releases/0.1.0-rc4/`. RC5 (`0.1.0-rc5`) passed its
product repair, its scoped genuine-Codex qualification (immutable
[testing ledger 004](oap/evidence/testing-ledger/004/README.md)), and
its pulled-image qualification, but was rejected overall: the first
post-publication record-present validation failed a mandatory gate, and
the repair was a tracked source correction committed after the
immutable candidate freeze; its record set is archived byte-identical
under `packaging/releases/0.1.0-rc5/`. The 014-d successor round was
abandoned before any push, tag, or publication: its first post-freeze
full suite required tracked test corrections, triggering the round's
literal fail-closed rule, and its re-freeze attempt was stopped; no RC6
remote commit, release workflow, tag, registry mutation, or testing
ledger exists, and none is claimed. RC7 (`0.1.0-rc7`) qualified in
scope (immutable
[testing ledger 005](oap/evidence/testing-ledger/005/README.md)) and
was published as a private candidate; its record set is archived
byte-identical under `packaging/releases/0.1.0-rc7/`, and its aliases
remain occupied and immutable. RC8 (`0.1.0-rc8`) qualified in scope (immutable
[testing ledger 006](oap/evidence/testing-ledger/006/README.md)) and
was published as a private candidate: the human-supplied external
review input `CODE-DEFECTS.md` (external input, not a repository file
and not part of any benchmark archive) motivated two independently
verified product defects, both repaired — P01 (upstream HTTP-error
causes were discarded before close; now a bounded private
classification with a closed reason enum, a dedicated
low-cardinality private counter, and the unchanged generic public
error) and P02 (explicit compiler output truncation was collapsed
into invalid output and retried with the same known-insufficient
allowance; now a typed `output_truncated` outcome with a bounded
adaptive allowance, the `compiler-v3` behavior version, and
ceiling-bound fingerprint/cache/rehydration identity) — and its
pulled-image qualification passed. RC8 makes no claim that Local
Coding caused the rejected requests or task mistakes. RC8 was
rejected as the FINAL Objective-015 handoff candidate solely because
its frozen read-only CI registry baseline (a member of the 130-entry
frozen source-input map, hence immutable after publication) claimed
to cover the archived RC7 alias pair while its literal
immutable-history set stopped at RC5; the RC8 source/provenance
binding could not be corrected post-publication, so RC8 is preserved
permanently: its record set is archived byte-identical under
`packaging/releases/0.1.0-rc8/`, and its aliases remain occupied and
immutable. RC9 (`0.1.0-rc9`) carried that correction (every archived
RC alias pair digest-asserted in the read-only baseline from a shared
single source of truth, with a deterministic regression and the
intentional RC6 absence preserved), qualified in scope (immutable
testing ledger 007), and was published as a private candidate — but
was rejected as the FINAL Objective-015 handoff candidate solely
because its frozen historical replay test was defective: the
regression's fallback parser passed the ``tags =`` assignment
statement to ``ast.literal_eval``, so the 015-a frozen-source replay
died with ``SyntaxError`` before the alias comparison and the claimed
RC7-omission failure was never mechanically demonstrated. Its record
set is archived byte-identical under
`packaging/releases/0.1.0-rc9/`, and its aliases remain occupied and
immutable. RC10 (`0.1.0-rc10`) is the successor candidate: the narrow
regression correction (the fallback parser parses the tuple
expression and fails closed on malformed, ambiguous, or non-string
content; focused parser tests) plus the corrected harness reruns for
the next immutable testing ledger (expected number 008). No benchmark
ran; the final public release remains false; the package remains
private; the protected cutover remains false.

## Evidence and review

Sanitized evidence export uses [safe_evidence_export.py](scripts/safe_evidence_export.py).
It validates bounded closed schemas and privacy rules, refuses path/symlink
escapes and overwrites, and writes atomically under `oap/evidence/`. Its historical
audit preserves exact prior facts; it does not reconstruct missing results or
rerun protected inference. Never substitute raw captures for sanitized evidence.

CI includes CodeQL analysis for Python and GitHub Actions. Review findings and
their dataflow; a dismissal needs a specific documented reason. Do not exclude a
query just to hide a finding.

Merge requires fresh successful checks for the exact head plus review of scope,
security, semantics, documentation and operational effects. Historical green CI
and report prose cannot establish that the current candidate passes.

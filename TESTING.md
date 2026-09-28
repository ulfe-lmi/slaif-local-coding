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
remains private; the protected cutover remains false.

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

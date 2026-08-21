# OAP Work Order — 001-a

## Objective

Create exactly one new PR implementing objective 001: evidence-based observation
of effective `AGENTS.md` content and deterministic, bounded enumeration of every
syntactically valid referenced repository-file candidate with provenance.

Integrate observation as a route-scoped, semantics-preserving request-pipeline
stage after the existing image policy and before forwarding. Define typed source,
candidate, evidence, completeness, and request-identity contracts for later
objectives, but do not call a model, rank constitutional importance, persist a
cache, acquire files, compile summaries, or inject/replace governance.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`
- Repository URL: `https://github.com/ulfe-lmi/slaif-local-coding`
- Numeric objective / execution round: `001` / `001-a`
- PR mode: `CREATE_NEW_PR`
- Existing objective-001 PR: `N/A`; GitHub reports none open, closed, or merged
  with `OAP 001` in the title
- Base branch: `main`
- Starting base SHA: `91463ae3199dd06e0448a9422a5e713da8ee92df`
- Required fresh head branch: `oap/001-agents-observation-manifest`
- Required PR title:
  `[OAP 001] Add AGENTS observation and deterministic reference manifest`
- Required PR readiness: non-draft

GitHub reports zero open PRs. Objective 000 PR #1 is merged, remote `main`
contains its exact report head, and post-merge workflow `CI` run 32433743231 is
successful. The repository has no configured branch protection/rulesets, so the
coding agent must still create exactly one non-draft PR and never merge or enable
auto-merge.

Before mutation, fetch/reconcile GitHub. Start the fresh branch from the exact
current remote base above, not from the still-checked-out historical objective-
000 branch. Preserve the clean worktree and every merged OAP artifact byte.

## Strategic context and current verified state

Objective 000 provides a loopback adapter with faithful proxying, route-scoped
newest-image handling, hard body/JSON-depth limits, safe metrics, fake/live tests,
and no constitution behavior. Objective 001 establishes only the deterministic
observation layer required before model compilation in objective 002.

Current independently verified facts on 2026-08-21 CEST:

- Remote default `main`: `91463ae3199dd06e0448a9422a5e713da8ee92df`,
  verified merge commit with parents objective-000 base and accepted report head.
- OAP transcript selector on `main`: `000-c`; all objective-000 orders/reports
  are merged and immutable. This order advances the selector to `001-a` only
  through atomic activation.
- Host: `janezp@hinton2`; Codex CLI `0.149.0`.
- Coding wrapper is waiting on the exact control FIFO with profile
  `oap-coding-low`; its overlay selects `gpt-5.6-sol` over the built-in `openai`
  provider. It has no local base URL and does not depend on ports 18020/18031.
- Protected user unit `qwen-serving-vision.service` is active/running, PID 4174,
  start timestamp `Thu 2026-08-20 23:27:10 CEST`; mutually exclusive
  `qwen-serving.service` is inactive/dead.
- Only `10.8.132.76:18020` listens; ports 18021 and 18031 are free. No separate
  image-cap proxy exists.
- Authenticated `/health` and `/v1/models` return HTTP 200; model ID is
  `qwen3.8-27b`; live process retains `--limit-mm-per-prompt {"image":1}`.
- Protected key source remains
  `/synology/homes/janezp/qwen-serving/api_key.txt` mode 0600; values were not
  printed. The coding wrapper has the configured `QWEN3090_API_KEY` environment
  mechanism available for bounded live tests.
- Known pre-existing risk
  `/synology/homes/janezp/.config/qwen-serving-vision.env` remains mode 0777.
  It is out of scope and MUST remain byte-identical.

## Required files and evidence to inspect

At minimum, read the repository constitution/protocol, compact architecture,
security/testing contracts, all objective-000 orders/reports, current adapter/
configuration/tests/docs, and the detailed architecture sections for detector,
reference extractor, identity, data contracts, observability, and failure law.

Inspect Codex `0.149.0` behavior only with sanitized, disposable, non-production
fixtures. Never copy a real session, user prompt, system/developer instruction,
auth value, private repository path/content, or unrelated tool definition into
Git or the report.

## A. Typed observation contracts

Add small typed modules under a clear constitution/observation package boundary.
Contracts must be versioned and support at least:

```text
ObservationContext
  endpoint, route ID, model, request streaming state
  optional opaque principal/session/repository discriminators
  discriminator source/trust classification

ConstitutionSourceObservation
  source kind: AGENTS_ROOT
  logical relative path/label when evidenced
  exact observed UTF-8 content SHA-256 and byte length
  one or more evidence records/types/locations
  completeness/overflow/error state

CandidateReference
  normalized repository-relative path
  deterministic first-seen order
  all retained evidence records/types/spans
  completeness/overflow state inherited from source manifest

ObservationResult / ReferenceManifest
  schema/policy version
  bounded roots and candidates
  complete boolean and fixed incomplete-reason enum
  safe count/status fields for metrics
```

Do not introduce a combined semantic score. Objective 001 must not invent model
ranking, constitutional classes, acquisition urgency, or semantic priority.
Future `reference_confidence` and `constitutional_priority` remain independent
fields/stages; if schema placeholders exist, they must be separately named and
unset, never guessed from syntax.

Identity is request-scoped only in this objective. Current operation has no
signed gateway principal/session contract: spoofable client headers, raw bearer
keys, `previous_response_id`, and `prompt_cache_key` cannot become trusted tenant
identity or cross-request reuse keys. Any client session hints retained in the
typed result must be explicitly marked untrusted, remain in memory for the
request, and never be logged. No cache or persistence is authorized.

## B. Evidence-based effective `AGENTS.md` detection

Implement pure deterministic detectors for the exact bounded JSON already
validated by the adapter. Support at least these evidence classes:

1. **Codex project-instruction envelope:** a captured/current structural form
   that explicitly identifies `AGENTS.md` or its effective directory and pairs
   it with the instruction content (for example the current
   `# AGENTS.md instructions for <directory>` plus `<INSTRUCTIONS>` envelope).
2. **Input/upload file:** an API input-file/content item whose evidenced basename
   is exactly `AGENTS.md`, with text content structurally paired in the same
   supported item/envelope.
3. **Paired file-read tool result:** a structured tool call that conservatively
   and explicitly reads an exact `AGENTS.md` path, paired by stable call ID with
   its output. Support captured Codex tool shapes and a documented allowlist of
   unambiguous read commands/tool argument forms; do not treat arbitrary shell
   prose or an unpaired output as file content.

Detection rules:

- Arbitrary prose mentioning `AGENTS.md`, quoted examples, a tool definition,
  a command proposal without paired output, URL text, substring names such as
  `MY_AGENTS.md`, and assistant/model claims are not roots.
- Require exact filename/path plus envelope/pairing evidence. Preserve every
  evidence record when duplicate observations identify the same root/content.
- Extract and hash exact observed instruction content bytes using documented
  UTF-8 encoding. Do not trim, case-fold, normalize newline style, rewrite
  Unicode, or hash the surrounding envelope accidentally. Tests must prove LF,
  CRLF, trailing newline, whitespace, and Unicode changes produce the expected
  distinct hashes.
- Preserve an evidenced nested logical path such as `services/api/AGENTS.md`.
  The adapter never reads that path; it is only an observed label.
- Multiple roots/items in one request are deterministic and bounded. Content is
  ephemeral; no raw source persistence or logging.
- Unsupported/ambiguous shapes return a structured no-detection or incomplete
  result, never an exception, unsafe guess, or request rejection solely because
  optional observation failed. The semantically original request continues.

## C. Sanitized captured Codex fixtures

Create synthetic-content, structurally faithful fixtures under a clear
`tests/fixtures/codex/0.149.0/` boundary, plus provenance documentation. At least
one fixture must derive from an actual disposable Codex CLI `0.149.0` provider-
bound capture, using a temporary synthetic repository and a temporary repo-local
fake OpenAI-compatible endpoint/profile override.

Capture safety and reproducibility:

- Use `--ephemeral`/temporary command-line configuration or equivalent; do not
  edit active/user Codex profiles, login, account, model catalog, sessions, or
  compaction settings.
- Use only a synthetic disposable `AGENTS.md` and synthetic tool/output content.
- Minimize the committed fixture to the relevant envelope/items. Remove real
  auth, request IDs, account/session values, private paths, user content, OpenAI/
  Codex internal prompts, unrelated tool schemas, and response content.
- Document Codex version, capture topology/command classes, redaction/minimization
  rules, fixture limitations, and a safe reproduction procedure without secret
  literals.
- Fixtures are evidence for observed shapes, not a claim of universal/future
  Codex wire stability. Keep synthetic supplemental variants for Responses and
  Chat/file/tool shapes where actual capture does not exercise them.

CI must consume only committed sanitized fixtures and not require Codex login,
host credentials, network, or the installed CLI.

## D. Deterministic candidate-reference extraction

For each detected root, enumerate candidates mechanically before any future
model call. Support and distinguish evidence from at least:

- inline Markdown links and reference-definition destinations;
- backtick-delimited and single/double-quoted path-like strings;
- repository-relative bare paths/filenames near normative neighbor language
  such as `MUST`, `MUST NOT`, `NEVER`, `REQUIRED`, `binding`, `read`, or
  `before`;
- nested repository paths and common binding documentation/config/script
  extensions/basenames, including `.md`, `.txt`, `.rst`, `.toml`, `.yaml`,
  `.yml`, `.json`, `.ini`, `.cfg`, `.sh`, `.py`, `Makefile`, and safe
  `.github/...` paths according to a documented policy.

Normalization and rejection:

- Produce normalized POSIX repository-relative paths only. Collapse safe `./`
  and repeated separators deterministically.
- Reject absolute POSIX/Windows/UNC paths, URLs/schemes, network locations,
  NUL/control characters, empty/directory-only values, encoded/decoded
  ambiguity, query-bearing destinations, and every `..` traversal segment even
  if it might resolve back inside a repository.
- A Markdown fragment may be stripped from an otherwise valid file destination
  only by an explicit documented rule while retaining the raw evidence span.
- Do not access the filesystem, resolve symlinks, stat paths, browse, fetch, or
  decide whether the file exists.
- Do not semantically discard a syntactically valid candidate merely because it
  appears example-like or low-priority. Retain it with its deterministic evidence
  context for later model classification. Rejected tokens retain only safe
  fixed reason/count evidence, never raw private values in metrics/logs.
- Collapse duplicate normalized paths while retaining all evidence in stable
  source order. Candidate order is deterministic by first valid occurrence;
  repeated runs and equivalent supported envelopes must serialize identically.
- Evidence spans/offsets must use one documented coordinate convention and map
  back exactly to the observed synthetic source in tests.

## E. Explicit bounds and failure behavior

Add validated route/global observation policy with conservative finite limits,
including at least maximum roots per request, exact source bytes per root,
candidate count, evidence records per candidate, total evidence/span budget,
and accepted path length. Observation is explicitly enabled per route; it must
not become a global transform for unknown models/routes.

When a limit is reached:

- never report a partial manifest as complete;
- return a bounded result with `complete=false` and a fixed reason such as
  `source_too_large`, `too_many_roots`, `too_many_candidates`, or
  `evidence_budget_exceeded`;
- preserve the original governance-bearing request and forward it unchanged
  except for the already accepted image policy;
- make no compiler/internal/model call, cache write, file read, or injection;
- emit only bounded count/status metrics.

Malformed/over-depth JSON remains governed by objective 000 and must still fail
with its documented 4xx before observation. An observation parsing error must
not weaken image enforcement or bypass route selection. CPU/memory work is
bounded by existing body/depth limits plus observation limits.

## F. Pipeline integration and compatibility

- Extend the explicit typed request pipeline so route selection and image policy
  remain before constitution observation, and forwarding remains after it.
- Observation must not alter, remove, inject, summarize, reorder, or reserialize
  an otherwise untransformed request. Fake upstream tests must compare exact raw
  bytes for observation-enabled zero/one-image requests.
- When the pre-existing image policy legitimately transforms a multi-image
  request, observation may inspect the transformed in-memory payload but must not
  change non-image/AGENTS content or image-policy semantics.
- Support both configured Responses and Chat Completions envelopes where an
  evidence class applies. Unknown route/policy remains fail-closed as before.
- Add safe private metrics for roots by fixed evidence type, candidates accepted,
  fixed rejection/incomplete reasons, observation time/status, and route/endpoint.
  No filename/path, content/hash, source/tool text, principal/session value,
  query, auth, or attacker-controlled label is allowed.
- No public diagnostic header or endpoint exposing manifests/raw observations.
  Pure typed results are asserted directly in unit tests.

## G. Verification and evidence

Required CI-running pure/fake tests include:

```text
captured Codex project-instruction fixture detection
captured/synthetic input-file and paired tool-call/output detection
plain-mention, quoted-example, unpaired-output, substring, URL false positives
exact content hash/length for LF/CRLF/trailing whitespace/Unicode
multiple/nested AGENTS observations and stable dedup/evidence order
Markdown inline/reference links; backtick/quoted/normative-neighbor candidates
duplicates with all evidence retained and stable first-seen order
valid nested/.github/config/script paths
URL, absolute POSIX/Windows/UNC, traversal, control, query, overlength rejection
fragments, escaped Markdown/string edge cases, offsets, deterministic serialization
every root/source/candidate/evidence/total budget boundary and overflow state
route-enabled versus disabled observation
untrusted identity/header/session-hint handling; no cross-request state
exact upstream request bytes and no extra upstream/compiler call
image-policy ordering/non-regression, malformed/depth/body bounds
no raw path/content/hash/sentinel/auth/session leakage in logs/metrics/errors
existing SSE/disconnect/header/query/compression/tools/usage/readiness/package tests
```

Run and report at least:

```bash
uv lock --check
uv sync --frozen --extra dev
uv run --frozen ruff check .
uv run --frozen ruff format --check .
uv run --frozen mypy src tests
uv run --frozen pytest -q
SLAIF_LIVE_TEST=1 uv run --frozen pytest -q tests/test_live.py
uv build
python3 -m compileall -q src tests oap/bin
bash -n oap/bin/*.sh
git diff --check 91463ae3199dd06e0448a9422a5e713da8ee92df...HEAD
```

Extend the bounded live suite on a foreground candidate at 127.0.0.1:18031:

- rerun the complete accepted objective-000 health/models/text/tool/SSE/multi-
  turn/vision/image-count matrix;
- send one synthetic observation-enabled request through the candidate and prove
  HTTP/provider compatibility plus a bounded root/candidate metric delta;
- prove no additional compiler/internal model request occurs and no injected or
  removed governance behavior is claimed; fake-upstream exact-count/body tests
  are authoritative for this property;
- keep calls serial/small, stop the candidate afterward, and record only safe
  status/count/timing evidence.

No actual long-session/compaction compliance claim is authorized; real Codex E2E
remains objective 004. The disposable capture in section C is fixture discovery,
not service cutover or an E2E product claim.

## H. Documentation and compatibility contracts

Update README/configuration/architecture-adjacent implementation docs as needed
to describe:

- implemented evidence classes, captured fixture version/limitations, exact
  hashing, extraction/normalization/rejection rules, bounds/overflow semantics;
- request-only identity/trust status and absence of multi-user cache reuse;
- route-scoped observation metrics/privacy behavior;
- original request preservation and no compiler/cache/injection/acquisition;
- how to update fixtures safely for a future Codex version;
- experimental tested scope only.

Do not rewrite normative architecture unless implementation reveals a genuine
strategic conflict. Do not document objectives 002–006 as implemented.

## I. Explicit non-goals

- No model-generated summary, ranking, `reference_confidence`,
  `constitutional_priority`, P0–P4 class, rule extraction, or compiler call.
- No direct/internal second vLLM request, compiler bypass channel, retry, or GPU
  scheduling beyond proving none exists.
- No cache backend, filesystem/tmpfs state, TTL/LRU, persistence, cross-request
  memory, source retention, working-set selection, injection, governance
  replacement, dependency acquisition, compaction/rehydration logic.
- No client filesystem access, stat/read/glob/search, URL fetch, Git/GitHub lookup,
  symlink resolution, MCP, web, hosted tools, or external service.
- No signed gateway identity/auth/quota/accounting/routing/admin/TLS, gateway
  repository change, public listener, deployment, cutover, or active profile
  switch.
- No change to objective-000 proxy/image semantics except small integration
  refactors proven byte/behavior compatible.
- No protected-host permission remediation in this PR.

## J. Security, privacy, resources, and protected host

- Raw prompts, source, AGENTS content, candidate filenames/paths, tool output,
  request/response bodies, images, auth/cookies/keys, private URLs, opaque IDs,
  and real session data must not enter logs, metrics, errors, OAP artifacts, CI
  output, fixture provenance, screenshots, or cache/persistence.
- Synthetic fixture content/paths are allowed in test source, clearly labeled.
- Do not persist observed raw content at runtime. Hashing is one-way identity
  evidence only; do not log full hashes or use them as public labels.
- Adapter remains CPU-only, bounded, loopback-only on 18031 for live tests. No
  torch/model/image decoding, duplicate model, GPU allocation, public binding,
  firewall/VPN/network/key/gateway change.
- Absolutely no stop/restart/change to `qwen-serving-vision.service`, inactive
  `qwen-serving.service`, PID/port 18020, qwen-serving checkout/venv/model/
  checkpoint/patches/launch flags, systemd units/drop-ins, API-key file, active
  Codex profiles/login/catalog/session/compaction settings, or OAP wrapper.
- Preserve the pre-existing mode-0777 vision environment file byte-for-byte;
  remediation requires separate authority.
- Required unchanged hashes:
  - vision env `affabb5701b67b5fcb7cab2e3ae1835e84e19dc98a7f1eb245cf3e49b76b3b5b`
  - vision user unit `fc88870b4f4afee214c25dc9ec544c4178c300bf4d78092a4d12787a955e2e94`
  - vision start script `8c87e0104b25c9600235a97555c4b0a1d0ea55d34ccb4094af428c8b4501f89f`
  - Qwen Codex profile `18ead58ac440d29ce2e86addf855c24f471021c6050d4da685320a2cf6eb62eb`
  - coding profile overlay `cc243c7057f00cb15a06a5be63c6d811f8f473e367d521b1b6ea6207c794509a`
  - OAP runtime env `22fdefd324d631353f1b9fedad3bad1fc75577073794a882ce2dd57bc5794bf1`
- Verify before/after service PID/start time/command/listeners and all hashes.
  At report time only protected 18020 may listen; 18021/18031 must be free.

## K. Local execution authority

Coding owns safe repo-local dependencies, disposable synthetic repository,
temporary loopback fixture-capture server, command-line/ephemeral Codex capture,
fake upstreams, candidate process, bounded authenticated calls, test tools,
GitHub publication, and CI diagnosis. Do not recruit the human or strategic
agent as terminal operator. A genuine capture-format ambiguity must be reported
with sanitized structural evidence, not resolved by weakening detection.

## L. Acceptance criteria

1. Exactly one non-draft objective-001 PR exists with required title/base/head;
   coding never merges or enables auto-merge.
2. Captured Codex 0.149.0 synthetic-content fixture/provenance is safe,
   structurally faithful, reproducible, minimized, and CI-tested.
3. Effective roots are detected only from supported envelope/path/pairing
   evidence; listed false positives do not detect.
4. Exact observed content bytes are hashed/lengthed without normalization and
   every evidence item is retained deterministically.
5. Every syntactically valid candidate in supported forms is normalized,
   deduplicated, and retained with all stable evidence; invalid URL/absolute/
   traversal/control/query/overlength forms are rejected deterministically.
6. Bounds never masquerade as complete enumeration; original governance-bearing
   requests continue unchanged and no extra model/cache/file/injection action
   occurs.
7. Observation is explicit route policy in the ordered pipeline and cannot alter
   proxy/image/tool/SSE/error semantics or trust caller identity headers.
8. Metrics/logs/errors/fixtures/OAP evidence contain no real raw/private content,
   candidate paths, source hashes, IDs, or secrets; safe labels/counts are bounded.
9. Exact unit/fake/capture/live/regression/package/static gates all run and pass;
   unavailable/skipped required evidence is not pass.
10. Protected service/config/profile/network/key state and required hashes remain
    unchanged; candidate/capture processes are stopped.
11. Docs state exact implemented/tested scope and do not claim compiler/cache/
    injection/rehydration/multi-user production behavior.
12. Final report-only SELF commit and entire OAP transcript satisfy protocol.

## M. GitHub publication and immutable report

1. Fetch/reconcile remote `main`, preserve the current clean checkout, and create
   fresh `oap/001-agents-observation-manifest` from exact starting SHA.
2. Commit this activated order and `oap/active=001-a` unchanged with the
   implementation. Preserve every prior order/report byte.
3. Stage only explicit intended paths; never `git add .`, `-A`, or `--all`.
4. Push all non-report work and create exactly one required non-draft PR. Inspect
   and safely repair all in-scope CI failures. Never merge.
5. Capture the final literal implementation SHA only after every non-report
   change is remote.
6. Atomically publish exactly:

```text
oap/reports/001-a-agents-observation-and-reference-manifest.md
```

7. The report contains `Implementation head SHA: <literal 40-hex>` and
   `Report publication commit: SELF`. The remote report commit changes only that
   report, its first parent is the literal implementation SHA, and it is current
   PR head before response `OK`; no later mutation/push occurs.
8. Report exact files/behavior, capture method/version/redaction, fixture hashes
   only when safe, criterion-by-criterion evidence, test commands/counts, live
   sanitized status/counts, exact CI states, dependencies, docs, protected
   before/after state/hashes, limitations, and explicit `extra PR NO`, `coding
   merge NO`, `auto-merge NO`, `protected change NO`.

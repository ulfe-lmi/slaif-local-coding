# OAP Work Order — 014-a

## Objective and authority

CREATE_NEW_PR; Objective 014; exactly one new PR. Repair the independently
reproduced RC2 real-Codex image-policy compatibility defect, permanently cover
the supported client envelope in ordinary CI, produce a new immutable private
`0.1.0-rc3` image, qualify the actual pulled digest, and run bounded standalone
real-Codex compatibility smoke sufficient for a strict benchmark-readiness
verdict. This is product repair and release-candidate qualification only.

Human explicitly authorizes the repair, private RC3 publication, pulled-image
qualification, and bounded standalone real-Codex VISION/CACHE/BOTH smoke. Human
does not authorize any benchmark run/design/change, final public release, public
GHCR visibility, `v0.1.0`, GitHub final Release, protected-host cutover,
production Gateway/routing mutation, benchmark-repository mutation, existing
vLLM install/service/package/model/checkpoint/quantization/CUDA/context/parser/
GPU/launch change, or serving installation/upgrade.

## Authoritative starting state

- Repository: `ulfe-lmi/slaif-local-coding`.
- Numeric objective/round: `014` / `014-a`.
- PR mode: `CREATE_NEW_PR`; existing Objective-014 PR: none.
- Base: remote `main` at
  `8c3c6d6cd67a34ba7d427ab255a91bd6a9753bd1`.
- Required head: `oap/014-real-codex-compatibility-rc3`.
- Required PR title: `Repair real Codex image compatibility and qualify private RC3`.
- PR must be non-draft. Coding never merges or enables auto-merge.
- PR #18, `docs: add testing ledger 001 for real Codex image-policy crash`, is
  merged at the exact base above. No open PR exists. Current main CI run
  36375640215 and CodeQL run 36375639982 are successful, but are historical
  starting evidence and cannot qualify RC3.
- `oap/active` is `013-n`. Objective 013/PR #15 is accepted and merged; later
  direct PRs #16/#17 and evidence PR #18 are merged. This new repair is not a
  013 continuation. If remote truth differs before mutation, stop unsafe work
  and publish a truthful blocker rather than inventing a branch/PR mapping.
- The local checkout is behind remote main at the time of activation and has
  pre-existing untracked zero-byte paths `Local`, `clean`, `unchanged`. Preserve
  them; fetch and branch from exact remote base without deleting or committing
  them.

## Independently verified incident and identities

The immutable failed candidate remains:

```text
RC: 0.1.0-rc2
source: 0a2f34b6d6fc17b732a1e7570f751776dce1ae01
image: ghcr.io/ulfe-lmi/slaif-local-coding@sha256:2349400a0dd5dbcec560f6c164283f24e5a55c5f474114416af21d6f3b2cb100
wheel sha256: 04d1a87cb44f22dad3a7022f63a54f651eca74ed364394aaec85957bbeb8aeda
subject client: Codex CLI 0.149.0
```

`oap/evidence/testing-ledger/001/` is append-only historical evidence. Its five
paths exist on remote main. The ledger records that DIRECT reached the model and
completed a tool loop, while VISION/CACHE/BOTH failed before inference with
`TypeError: unhashable type: 'dict'`. The recorded content-free envelope has two
dictionary-valued `type` paths below a namespace-tool parameter schema.

Strategy independently reproduced the defect with network disabled using the
RC2/current pure helper: both `count_images(payload)` and
`apply_retain_newest(payload, 1)` raise that exact TypeError for the sanitized
nested schema fragment. RC2 `image_policy.py` evaluates
`node.get("type") in IMAGE_TYPES` without first proving the marker is a string.
RC2/current `app.py` calls `count_images(payload)` unconditionally before
consulting `max_images_per_request` or `image_overflow_policy`. This establishes
the VISION/CACHE/BOTH impact; DIRECT bypasses Local Coding.

Do not alter, rewrite, relabel, soften, replace, or delete ledger 001 or any RC2
identity/tag/archive. If new testing-ledger evidence is useful, allocate a new
number and keep it sanitized, immutable, truthfully scoped, and manifest-bound.

## Current protected fixture and client facts

- User `qwen-serving-vision.service` is active/running, PID 23961, since
  2026-09-06 18:57:26 CEST. User `qwen-serving.service` is inactive/dead.
- PID 23961 alone listens on `0.0.0.0:18020`; 18021/18031/18033/18034 are free.
- The coding wrapper selects `qwen-neumann`; its protected profile selects
  provider `qwen-LSI-A100`, Responses API, model `qwen3.8-27b`, at the existing
  test endpoint on port 8001. Profile SHA-256 is
  `3aef2d8b819e9a5649c1fb739cd97b885cc69dbdf04eb15db7dcdbf4fac488bb`.
  Never print/copy its credential or mutate the profile/provider.
- Current default CLI is newer, but the previously qualified standalone binary
  remains at
  `/synology/homes/janezp/.codex/packages/standalone/releases/0.149.0-x86_64-unknown-linux-musl/bin/codex`.
  It reports `codex-cli 0.149.0` and SHA-256
  `bbc3341e44c9ead340ed9570c17be936e37870f570751a941699ffd04d672827`.
  Use this exact client first. If it becomes unusable for a reason unrelated to
  the adapter, a later installed Codex version is human-authorized as fallback;
  name its exact version/hash and reason, rerun every VISION/CACHE/BOTH arm with
  that one version, and never mislabel fallback evidence as 0.149.0 evidence.
- Both OAP FIFOs exist as mode-0600 FIFOs; the coding loop is waiting on control.

Recheck all relevant host/client facts read-only before and after qualification.
Historical values are not permission to change them.

## Workstream A — smallest correct product repair

1. Reproduce the sanitized ledger trigger from exact remote base before repair.
2. Inspect `src/slaif_local_coding/image_policy.py`, the full request path in
   `app.py`, route configuration, and all image-policy/app tests. Establish and
   document whether the current structural definition of a supported image item
   remains correct when recursively traversing arbitrary request JSON including
   tool schemas. Do not assume the supplied diagnosis resolves every false
   positive; do not broaden behavior without evidence.
3. At minimum, compare against `IMAGE_TYPES` only after proving the candidate
   marker is a string. The final repair must never hash/compare an unhashable
   arbitrary JSON value.
4. Preserve supported Responses `input_image` and Chat `image_url` recognition,
   deterministic newest-image retention, route scoping, maximum-zero behavior,
   and fail-closed handling of genuinely ambiguous supported image shapes.
5. Preserve every non-image tool/schema value and ordering unless an explicit
   image content item is intentionally removed. A tool-schema example or ordinary
   property must not be silently treated as removable content merely because the
   walker is recursive; resolve any demonstrated ambiguity with the narrowest
   contract-consistent validation or fail-closed behavior.
6. Preserve streaming, tools, errors, usage, forwarding, privacy, metrics, and
   constitution behavior outside this exact repair. No raw-content logging or
   persistence and no opportunistic redesign/refactor/dependency change.

## Workstream B — durable deterministic regression

Add a sanitized, deterministic Codex-envelope fixture/regression to ordinary CI.
It must contain no prompt, credential, raw tool body, private path, source, image,
or model output. Ledger 001 may be read as historical evidence but remains
byte-identical.

Focused pure tests must prove:

1. The exact sanitized nested namespace-tool reproducer is accepted without
   exception by both `count_images()` and `apply_retain_newest()`, and remains
   structurally equal when no image transformation applies.
2. Nested values named `type` cover string, dictionary, list, null, boolean,
   integer, and float. Only exact supported string markers can be image markers;
   other values neither crash nor mutate.
3. Realistic nested JSON Schema/tool declarations are structurally preserved,
   including ordering and arbitrary non-image values.
4. Existing/extended cases cover zero/one/multiple Responses images, newest
   retention, Chat image URL, deterministic traversal, genuinely ambiguous
   marker placement, maximum zero, and passthrough/reject/retain-newest route
   behavior.

Add mandatory full-application fake-upstream tests through `/v1/responses`, not
only helper tests. Representative Codex 0.149 namespace-tool envelopes must reach
the disposable upstream without corruption under configurations corresponding
to VISION, CACHE, and BOTH. Assert upstream request count and exact semantic/
structural preservation of non-image tool schema. Exercise the actual route/
constitution settings, using a deterministic fake compiler response where
needed; a helper-only shortcut is insufficient. This fixture must fail against
RC2 for the recorded reason and pass after repair.

## Workstream C — permanent standalone real-Codex gate

Add or formalize a repository-owned bounded release-candidate qualification that
uses a genuine Codex CLI and ordinary local tool interaction. Ordinary CI runs
the sanitized fixture only; normal CI must not depend on a secret GPU endpoint.
The real gate is opt-in, fail-closed, privacy-bounded, and required for RC
readiness when the client/backend are available.

The supported topology is exactly:

```text
disposable Codex home/repository -> 127.0.0.1:18031 Local Coding
                                 -> existing tested OpenAI-compatible Qwen/vLLM endpoint
```

No SLAIF API Gateway is involved. Set gateway ingress mode `disabled`; do not
invent signed Gateway headers. VISION uses explicit one-image retain-newest
policy with constitution/compiler disabled. CACHE uses image passthrough/control
semantics and enabled constitution/compiler with supported static single-user
principal/session/repository identity. BOTH enables both mechanisms with that
same static identity. Use separate disposable config/cache/state per arm or prove
isolation; loopback only. A direct control may use the same client/backend when
safe, but is contextual evidence and never substitutes for a product arm.

For each VISION/CACHE/BOTH arm require a fresh genuine tool-bearing Codex session
that reaches the model, completes at least one ordinary local tool interaction,
and produces a bounded expected completion. Prove the adapter received the arm,
upstream/model work occurred, the tool interaction completed, no internal 500 or
image-policy exception occurred, and protected state stayed unchanged. Limit
attempts, duration, output bytes, requests/tool calls/compiler calls, and run
serially. Capture only fixed categories, counts, status, version/hash, timing,
and boolean verdicts—no prompt/source/tool arguments/output/request/response/
credential/private URL/session ID. Delete disposable raw state after extracting
sanitized facts.

Use exact Codex 0.149.0 first. If the designated endpoint is unavailable, or a
required arm cannot complete, report `BLOCKED` at this boundary; synthetic tests
cannot establish readiness. A later-version fallback is permitted only under the
client rule above and must be explicit. Do not mutate the active coding profile;
construct a private disposable `CODEX_HOME`/catalog/config and pass credentials
only through protected environment/in-memory mechanisms. Never expose secret
values in argv, Git, report, logs, process listings, or temp files; private temp
files must be mode 0600 and removed.

The candidate adapter may run as a foreground repo-owned process on 18031 and
must stop cleanly. Do not use host Docker on the protected model host. Do not
restart/reconfigure/patch either existing backend. Bounded authenticated calls
are allowed. If the real gate runs from the reproducible wheel rather than the
container, its wheel hash must equal the retained in-image RC3 wheel hash; state
this exact binding and rely separately on the actual pulled-image CI gate.

## Workstream D — RC3 source and immutable publication

1. Preserve RC2 permanently. Before replacing current RC metadata, archive the
   current RC2 `rc_record.json`, deterministic handoff, and provenance manifest
   under `packaging/releases/0.1.0-rc2/` according to the established RC1
   convention, byte-identical to the accepted RC2 files. RC2 tags and source-SHA
   alias remain untouched.
2. Reconcile all candidate constants, schemas, generators, publisher guards,
   workflows, Docker/operator qualification, tests, and current docs from RC2 to
   explicit RC3. The publisher must accept exactly `0.1.0-rc3`, retain the final/
   stable tag denylist, and never silently allocate another RC.
3. Remove/supersede only the current mutable RC metadata needed for a truthful
   RC3 pre-freeze state; keep archived RC1 and RC2 immutable. Regenerate the
   pre-freeze provenance from clean source with all source inputs, build pins,
   wheel/sdist hashes, Gateway pin, platform, and RC3 label truthful.
4. Establish the final image-source commit `S` only after all artifact inputs are
   frozen. Clean builds on the two available Python 3.12 patch versions must
   reproduce byte-identical wheel and sdist; record exact wheel `W`. No artifact
   input may change after this freeze. Derived manifest/OAP commits are allowed
   only when mechanical source-input equivalence proves the image bytes remain
   bound to `S`.
5. Before registry mutation, require fresh source-head CI and CodeQL/security
   checks successful. Dispatch the existing workflow-dispatch-only release image
   workflow from exact remote branch head `S`. The workflow must authenticate and
   verify BOTH `0.1.0-rc3` and `sha-<S>` absent before any mutation, recheck before
   each write, fail closed on occupied/partial/unauthorized/unresolved state, and
   publish the same image under exactly those two aliases. Never write/repoint
   RC2, RC1, legacy `0.1.0`, final, latest, stable, or visibility.
6. Verify workflow checkout/head exactly `S`, wheel exactly `W`, both aliases
   resolve to one new registry digest `D`, package stays private, and old aliases
   remain at prior digests. Do not retry/complete a partial publication without a
   new strategic continuation decision.
7. Generate current RC3 machine record and deterministic handoff from actual
   authenticated facts. Regenerate published-state provenance. Prove input maps
   at frozen source and metadata/report commits are identical and later changes
   are excluded derived metadata/OAP only.
8. Fresh final-head CI must run all five ordinary jobs. `docker-published` must
   pull `D` and actually qualify it; prepublication `NOT RUN` is not acceptance.
   Preserve/review the existing normal Docker, Gateway contract, and operator
   session gates.

## Required verification and evidence

Run and report exact commands/status/counts for at least:

```text
uv lock --check
uv sync --frozen --extra dev
uv run --frozen ruff check .
uv run --frozen ruff format --check .
uv run --frozen mypy src tests
uv run --frozen python scripts/docs_consistency_check.py
uv run --frozen pytest -q
uv build
artifact policy inspection
fresh-wheel noneditable install smoke
source-input/provenance regeneration and equality checks
python compileall and shell syntax checks
focused image-policy + full-app Codex-envelope regressions
publisher/RC-record/provenance/schema/archive tests
bounded real-Codex DIRECT contextual control when safe
bounded real-Codex VISION, CACHE, BOTH product arms
```

Fresh exact-head GitHub evidence must include successful `test`,
`gateway-contract`, `docker`, `operator-session`, `docker-published`, and current
CodeQL/security checks, with none pending/failed/cancelled/missing. Inspect logs,
not only labels. Actual pulled-image qualification must prove digest/tag equality,
`linux/amd64`, OCI revision/version/RC3/wheel/Gateway/topology labels, retained
wheel `W`, exact locked installed inventory, noneditable install, no-build
pull-first deployment, signed-ingress positive/negative contract, fail-closed
readiness, forbidden-content scan, hardening, lifecycle, and teardown absence.

After strategic merge, strategy will independently require remote main contains
the accepted head and fresh post-merge main CI/CodeQL are all successful. Coding
must never merge.

## Documentation and final handoff

Keep README product-focused. Update testing/history/release/handoff/config docs
only where needed to state:

- RC2 failed external real-Codex qualification; ledger 001 is immutable history;
- RC3 contains the compatibility repair;
- deterministic fixture CI and opt-in real-client RC qualification are distinct;
- exact Codex version/hash actually qualified (0.149.0 primary, explicit later
  fallback only if used);
- standalone loopback Local Coding qualification requires no Gateway;
- no benchmark ran, final public release remains false, package remains private,
  and protected cutover remains false.

The final machine/human handoff must allow the separate benchmark VM to consume
RC3 without rebuilding and contain: RC identifier, `S`, `D`, both aliases, `W`,
build-tool pins, lock hash, configuration/source-input hashes, tested Codex
version/hash, VISION/CACHE/BOTH smoke results, platform, private-registry auth
requirement, Gateway-not-required standalone fact, benchmark-not-run,
final-release-false, and cutover-false. If existing record schema cannot carry
the compatibility facts safely, extend/version it with strict closed-schema
validation rather than putting unvalidated prose into the machine record.

## Acceptance criteria

1. One correct Objective-014 PR exists from exact base/head; no second PR and no
   merge by coding.
2. Ledger 001 and every RC2/RC1 archived identity remain byte-identical and
   historically resolvable.
3. Root cause is demonstrated pre-fix and the smallest correct type-safe,
   structure-safe repair is reviewed; no arbitrary valid JSON `type` value can
   crash image traversal.
4. Pure and full-app regressions satisfy every Workstream-B case and would have
   caught RC2.
5. Non-image tools/schema are preserved; supported image/reject/passthrough/
   retain-newest/ambiguity/max-zero semantics remain correct.
6. RC3 source/artifacts are reproducible and input/provenance bound; publisher
   and records explicitly use RC3 without weakening collision/final-tag guards.
7. Private RC3 exists at one authenticated immutable `D`; both new aliases map
   to it, old tags remain unchanged, visibility remains private.
8. Fresh final PR-head CI/CodeQL and actual pulled-digest qualification are all
   successful with required evidence.
9. Genuine bounded standalone Codex VISION, CACHE, and BOTH arms all pass against
   the repaired artifact-bound adapter and same designated backend. DIRECT is
   recorded when safe. Missing/unavailable/failed required arm is BLOCKED, not
   pass. The exact actually used client version/hash is recorded.
10. Protected service/profile/network/model state is unchanged before/after; no
    secret/raw content leak, benchmark work, Gateway production change, host
    Docker, or cutover occurred.
11. RC3 handoff is complete and consumer-ready without rebuild. Final public
    release remains false.
12. Final report/SELF protocol is exact.

The report must issue one explicit proposed verdict:

```text
BENCHMARK_READY
```

only if private RC3 and authenticated `D` exist, actual pulled qualification and
all current checks are green, all three required real-Codex arms pass, ledger-001
has no unresolved product blocker, and handoff is complete. Otherwise issue:

```text
BENCHMARK_BLOCKED: <exact blocker>
```

Strategy independently decides acceptance/merge and final verdict after current
GitHub/main verification.

## Absolute safety and non-goals

No Minesweeper code, tasks, statistics, pilots, repetitions, 4/12/16 campaign,
benchmark analysis, benchmark-repository access/mutation, or benchmark telemetry.
No Gateway repo/code/production state/routing change. No current vLLM executable,
package, CUDA, model, checkpoint, quantization, context, parser, GPU assignment,
service, systemd, launch, key, firewall, VPN, binding, or Codex profile change.
No model weights. No host Docker on this protected host. No public GHCR, final
tag/Release, production/compliance/general-model claim, or cutover. Temporary
adapter uses loopback 18031 only and is stopped with absence proof.

Raw prompts, request/response bodies, repository content, tool arguments/output,
images, model output, credentials, private URLs, session IDs, and customer data
must not enter logs, Git, CI artifacts, OAP report, evidence, metrics, or process
arguments. Use hashes/fixed classes/counts/booleans/timings only. Routine safe
repo-local setup belongs to coding; do not ask human/strategy to run commands.

## GitHub and immutable report contract

Start fresh branch from exact remote base; commit this activated order and exact
`oap/active` with implementation. Push all implementation/source-freeze/
publication-derived work to the one PR, inspect and repair in-scope CI, and never
force-push. Publication must occur from exact frozen remote `S` before derived
metadata changes the branch. Rewrite PR title/body to the final RC3 behavior and
evidence.

When all non-report work is remote, capture literal implementation head `R`.
Atomically publish exactly:

`oap/reports/014-a-real-codex-compatibility-repair-and-private-rc3.md`

The final report commit changes only that report, contains
`Implementation head SHA: <literal 40-hex R>` and
`Report publication commit: SELF`, has first parent exactly `R`, is current
remote PR head, and records exact PR/source/metadata/digest/wheel/client/check/
test/live/protected-state facts and explicit verdict. Make no mutation/push after
SELF; send exact response FIFO `OK`; stop. Coding does not accept, merge, advance,
run a benchmark, or perform final release/cutover.

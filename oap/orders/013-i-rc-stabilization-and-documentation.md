# OAP Work Order — 013-i

## Objective and human authority

Objective 013, continuation 013-i: release-candidate stabilization, documentation
cleanup, reproducible artifact preparation, and RC publication/handoff machinery.
AMEND_EXISTING_PR #15; NO NEW PR. Preserve the useful existing pull-based Compose,
OCI publication, Docker gates, and provenance implementation.

The human's current instruction supersedes final-release assumptions in earlier
013 orders: prepare and freeze a benchmarkable SLAIF Local Coding 0.1.0 RC for a
separate agent on a separate clean VM. The benchmark is entirely external. Final
public release/promotion requires a later human decision. Private GHCR access is
acceptable and expected; anonymous pull is NOT a prerequisite.

This round completes and verifies the final source/documentation and publication
machinery. Do not dispatch a registry-writing workflow in this round. Strategy
will review this round and issue the next same-PR continuation binding the exact
reviewed source commit for RC publication, digest qualification, and handoff.
This sequencing is not a request for new human permission. Publication of the
private RC is already human-authorized; the exact source must first be reviewable.
Do not declare the entire objective complete merely because this source round is.

## Independently verified state (2026-09-20)

- Repository ulfe-lmi/slaif-local-coding; default/base main at
  a04693e6792df6a8ad4262acfb46336a0f662202.
- Single open PR #15: https://github.com/ulfe-lmi/slaif-local-coding/pull/15
  head branch oap/013-mvp-release-publication, current remote head
  6406820912b80f67b6a12d0bafe6ddcd569d9f2e. Start from this branch/head;
  do not replace, rebase away, force-push, close, or create another objective PR.
- Local active is 013-h. Remote active still says 013-f: transcript debt, not
  authority to replay 013-f. Remote reports include 013-g and 013-h; the 013-h
  report at current head is report-only, parent
  881f1f360db8c2a22f89fac1e844195f661e8a80. Last completed round is 013-h;
  no remote 013-i order/report exists. Hence 013-i is the next legal round.
  Any other strategic-local pre-staged 013-i draft is inert and superseded by
  THIS exact activated order. It must not be copied or executed.
- Historical 013-h report is BLOCKED on anonymous package access. That
  acceptance condition is withdrawn by the human's private-RC instruction.
- CI 35348409538 at current head: test and docker FAILURE; gateway-contract
  SUCCESS; docker-published SUCCESS on the pre-record skip path. Independently
  inspected logs show freshly built wheel 9bf64a47... differs from bound
  879baa3a... and test_committed_manifest_matches_regenerated fails. Current
  build-system requirement is hatchling>=1.27. Historical hypothesis:
  hatchling==1.32.0 reproduces the old wheel; independently prove it, do not
  trust an inert draft. README is the wheel METADATA readme, so the new cleaned
  README intentionally produces a NEW final wheel hash.
- Most recent publication run 35263999980 succeeded from
  fe334e87c9f0fc65d1826cf9af7dad7e9f70a94a. Historical registry evidence binds
  tags 0.1.0 and sha-fe334e87... to
  sha256:a5debcb24bb6bbf7cf00dbf80cd17367d57186f6b0d7fadac020b94df53a0011.
  Earlier orphan sha-be3c78b2016d5d40ce9155df8f94d14525c43d39 also exists in
  historical evidence. Recent anonymous probes cannot resolve these private
  artifacts; absence from anonymous lookup is NOT proof a tag is free.
  No Git tags or GitHub Releases were returned in strategy's current query.
- Frozen Gateway compatibility authority is
  08ca421bee1ddca62078302b910e8be88cf705be. Gateway main has moved to
  db0bd3aeaaadee71ba40a16ee0dddf7a35e0a4b7; current main is not the frozen
  compatibility authority. Keep the pin; test the pinned peer and describe
  support honestly. Do not mutate Gateway or re-pin opportunistically.
- Protected vision service active, PID 23961, listener 0.0.0.0:18020; ordinary
  qwen-serving.service inactive. No listeners observed on 18021/18031/18033/18034.
  runtime.env selects qwen-neumann; its provider qwen-LSI-A100 uses Responses
  at http://maelstrom1.lmi.link:8001/v1, model qwen3.8-27b. Catalog is text/image.
  The active coding provider is protected; this is not an A100 benchmark fixture.
  A coding oap_fifo.py wait process is present; both strategic FIFO paths are
  actual mode-0600 FIFOs. Recheck round-start facts without exposing secrets.

## Scope and acceptance criteria

### A. Transcript, disposition, and exact authority

1. Commit this activated order and active 013-i unchanged, plus the previously
   uncommitted activated 013-g and 013-h orders unchanged. Verify their SHA-256:
   013-g = 156b82b26dd5bedd1dca5eaa102e1d087a8d06b5ff76b984d4ceae6a1113ebc1;
   013-h = 3550e417d1fbe4d65a113d09a37c258b291035965aac0834751523ac56a4825f.
   Preserve all historical orders/reports. Leave untracked Local/clean/unchanged
   residue and unrelated work untouched. No invented historical report.
2. Update the current Objective-013 disposition/completeness entry and PR title/
   description to RC stabilization/freeze, with public final release deferred.
   Keep historical evidence explicitly historical. In the new report map prior
   013 acceptance requirements to retained, superseded by human RC direction,
   fulfilled here, or deferred to the exact-source publication round.
3. Correct the historical report-field ambiguity prospectively: Implementation
   head SHA means the literal immediate pre-report commit, NOT image-source SHA.
   Image source has its own field. Explain the historical discrepancy without
   modifying old report/order bytes.

### B. Deliberate user-facing documentation cleanup BEFORE artifact freeze

4. Rewrite README.md as a concise professional landing page: product purpose,
   problem solved, simple client -> separate Gateway -> adapter -> private
   Qwen/vLLM topology, principal capabilities, supported runtime/deployment
   assumptions, getting started, links to install/config/security/architecture/
   development, and important limitations. Preserve credits/licenses. Remove
   OAP chronology, objective/round/PR/merge-SHA ledgers, acceptance dumps, and
   internal protocol details from the front page. Move still-useful specialist
   material to appropriately labeled engineering/history docs. Use durable
   product language: no 'this PR', 'pre-merge', 'benchmark pending', or promises
   about when release will happen. Do not overclaim tested compatibility.
5. Create root QUICKSTART.md: essential Docker path understandable in roughly
   5–10 minutes, assuming upstream/Gateway prerequisites exist. Cover Linux
   Docker Engine + Compose v2, obtain matching Compose/config at a recorded
   source commit, select image (digest preferred), private registry login when
   needed, prepare protected config/env files, compose pull/up -d, health and
   readiness, minimal troubleshooting, and link to INSTALL.md. Include usable
   safe commands and permissions, including non-root container config readability.
   No local Python, uv, venv, or source image build required on the operator host.
6. Create root INSTALL.md: full operator Docker/pull installation as primary;
   supported Linux/platform constraints, prerequisites, bounded read-only GHCR
   credentials via password-stdin (never literal credentials), tag vs immutable
   digest selection, exact matching config/Compose retrieval, secrets/config,
   startup/readiness, stop/restart, upgrade, digest-based rollback, uninstall.
   systemd direct-host installation is secondary/advanced; clearly separate its
   Python/uv requirements from Docker. Explain external upstream and separate
   Gateway requirements; do not imply Compose installs model weights/Gateway.
7. Reconcile at least docs/DOCKER-INSTALL.md, docs/DEPLOYMENT.md,
   docs/RELEASE-ARTIFACT-POLICY.md, relevant architecture/config/security docs,
   current implementation roadmap/completeness language, Compose comments/default
   image selection, and applicable examples. A small docs/README.md index should
   separate operator, architecture/security, developer/testing, and OAP/history.
   No current claim of final/public 0.1.0 release; historical private 0.1.0 tag
   is explicitly legacy unpublished-to-users output, NOT the RC benchmark target.
   Keep detailed history out of the primary install path. Maintain consistent
   supported topology, signed-ingress rules, lifecycle, and current limitations.
   Prefer explicit image selection over silently defaulting users to legacy 0.1.0.
8. Add a small mechanical documentation consistency gate in normal CI: required
   root docs, README links to QUICKSTART/INSTALL, practical repository-relative
   link validation, known stale/release wording and obvious 'this PR'/'pre-merge'
   current prose, pull-only primary Compose, and primary install without required
   Python/uv/local build. Scope it to current user-facing docs; do not lint
   immutable OAP transcripts or create a giant style linter. Include meaningful
   negative fixtures demonstrating broken links/stale claims/build-path regressions
   fail. Legitimate secondary advanced/developer instructions remain supported.

### C. Reproducible build and truthful provenance

9. In clean isolated checkouts/build environments independently test the historical
   hatchling==1.32.0 claim against the unchanged old source first; record actual
   backend/tool/Python versions and wheel hashes. If the hypothesis is disproved,
   diagnose safely and select a justified deterministic backend pin; never assert
   old-wheel equivalence without proof. Pin build toolchain sufficiently (backend
   and relevant resolved build dependencies, uv, Python/base image identity).
   Do not update runtime dependencies or runtime behavior merely for convenience.
10. After ALL user-facing documentation/build changes, build wheel + sdist twice
    from clean equivalent final source trees with isolated output/cache paths.
    Require identical wheel and sdist hashes across the clean builds. Reconcile
    metadata/README hashes and recorded inputs. The cleaned README changes wheel
    identity intentionally; old wheel/digest must NOT be reused for the RC.
    Retain artifact content-policy and fresh-install gates and pinned OCI bases.
11. Evolve existing provenance schemas/generator/tests for explicit candidate
    state, separate from final release: published RC must never imply
    final_released=true. Preserve strict validation and hash/source binding.
    Avoid self-reference: post-publication digest/handoff records must be excluded
    from wheel/sdist/image inputs; record exactly what source/input tree was built.
    Do not manufacture provenance by applying different source files under an old
    Git HEAD while presenting that old commit as the built tree. A pre-freeze
    manifest may refer to a verified ancestor only when artifact-input equality
    to the final source is mechanically proven and generation semantics are clear.
    Tests must reject false source, digest, wheel, template and peer bindings.
12. Prepare one simple machine-readable RC artifact record schema/generator and
    corresponding human-readable handoff, populated from verified facts during the
    next publication round. Required facts: product 0.1.0 / RC identifier; exact
    image-source commit; OCI reference/digest; wheel SHA-256; relevant pinned tools;
    dependency lock hash; frozen Gateway authority; config/template hashes;
    supported deployment assumptions; private-auth requirement; cutover false;
    final_public_release false. No fake digest or claimed publication in this round.
    This is artifact metadata, not benchmark code or a benchmark run ledger.

### D. RC-safe publication and pull qualification machinery

13. Adapt existing workflow_dispatch-only publisher for an explicit candidate
    identity 0.1.0-rc1 (if genuinely occupied, report collision for strategy;
    do not overwrite or silently invent another candidate). Source-SHA tag may
    additionally identify it. No final-tag default or code path invoked by this
    RC workflow may write 0.1.0, latest, stable, final v0.1.0, or change visibility.
    Tags are aliases, NOT immutable scientific identities; digest is authoritative.
    Check all target tags with authenticated access before mutation; distinguish
    unauthorized/inaccessible from verified missing. Fail closed on differing
    occupied RC/source tags, and on unresolved prior publication; safe retries
    must not overwrite or rebuild an already frozen identity ambiguously.
14. Use existing ephemeral workflow GITHUB_TOKEN packages:write for publication;
    least-privilege packages:read for private published-image qualification.
    Do not introduce long-lived write credentials, repository secrets, visibility
    changes, organization settings, production credentials, or token logging.
    Preserve old 0.1.0 and orphan tags byte-for-byte. Provide registry before/after
    verification in the publication machinery, authenticated in the trusted job.
    Public visibility is not required; do not ask the human to change it.
15. Update docker-published qualification to consume an RC record/digest, authenticate
    privately, verify registry digest, source/wheel/peer/topology labels and config
    identities, then exercise the existing signed-ingress/fail-closed/readiness/
    no-build/teardown assertions using the PULLED digest on disposable CI only.
    Before an RC exists use an explicit NOT RUN pre-publication state. Invalid
    records or inaccessible recorded images must fail, not silently skip. At final
    freeze this gate must actually execute successfully; a skip is not acceptance.
16. Preserve existing normal test, Gateway contract, Docker qualification and
    artifact gates. Publication design must freeze only after clean source gates
    pass, build from the exact recorded commit, and qualify the exact pushed digest.
    Record immutable OCI identity separately from mutable tags. Promotion later can
    reference the SAME tested digest without rebuilding or changing embedded labels;
    document the distinction between build-time candidate identity and later human
    approval. No promotion is authorized now.

## Hard non-goals and protected-host safety

- NO benchmark implementation/design. Do not create experiments/codex_adapter_benchmark/.
  No A–J protocol, tasks, judges, controller, run ledger, A100 VM setup, 27-run
  pilot, 108-run experiment, telemetry, statistics, or benchmark instrumentation.
  Do not modify product behavior to ease benchmarking. Future external agent pulls
  the frozen digest and must not rebuild the image. Handoff only covers artifact
  retrieval and identity verification, not experimental procedure.
- No runtime src/ behavior change; bounded packaging/docs/provenance/CI/tests only.
  Any necessary runtime defect discovered is reported to strategy for adjudication.
- No final Git tag v0.1.0, GitHub Release, final release claim, visibility change,
  registry write or publication dispatch in THIS preparatory round; no cutover.
- No mutation of Qwen/port 18020, qwen-serving checkout, models/checkpoints/patches/
  venv/systemd/launch flags, protected API keys, firewall/VPN/network bindings, or
  active Codex profiles. No production Gateway routing/config mutation; no Gateway
  repository mutation. Live host is read-only except safe repo-local tooling/tests.
- No model inference needed. No Docker build/run/up/pull on the protected host;
  Docker and pulled-image gates run in disposable hosted CI. Local fake test
  services may use loopback 18031 if free, short-lived and cleaned up. Never expose
  a new host/LAN listener. Compare protected service/profile/listener before/after.
- No secrets/raw customer content in logs/artifacts/OAP. Credentials through
  protected env only; no shell tracing or env dumps. Preserve license/notices;
  no model weights. Routine setup and implementation belong to coding, not human
  or strategic terminal labor. No new PR, merge, auto-merge, or force push.

## Verification, publication, report

Run frozen dependency setup and all current CI commands: ruff check/format,
mypy, complete pytest suite with exact skip accounting, builds, artifact inspection
and fresh-venv install smoke, compileall, shell syntax; strict pinned Gateway
contract gate; disposable Docker gate. Add the scoped docs/provenance/private-RC
publisher negative tests above. Show clean-build evidence, no benchmark paths/code,
no src behavior diff, protected-host invariance, and zero registry writes this round.
CI must be freshly green for the implementation head; report-head checks may be
pending and strategy waits independently. Do not weaken gates to satisfy obsolete
fixed hashes: update expectations only for explicitly authorized changed inputs.

Push implementation + exact transcript on the same PR and update its title/body
around the RC outcome. Report every criterion A1–D16 and inherited supersession,
changed docs, clean build/tool/hash facts, current check URLs, source candidate,
provenance model, registry-auth mechanism, retained limitations and exact remaining
publication work. Use PASSED/FAILED/SKIPPED/NOT RUN/BLOCKED accurately. A COMPLETE
report means this preparatory round only; immutable RC publication remains pending.

Publish exactly oap/reports/013-i-rc-stabilization-and-documentation.md. Record
Implementation head SHA as literal 40-hex immediate pre-report commit, and
Report publication commit: SELF. Record candidate image source separately; it is
not yet a frozen/published RC. Commit ONLY the new report as final child of the
literal implementation SHA, push, verify remote parent/path/bytes/current PR head,
then send exact OK to response.fifo. Make no mutation after signal. Strategy alone
reviews, chooses continuation, and eventually merges after all RC gates pass.

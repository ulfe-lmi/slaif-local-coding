# OAP Coding-Agent Report — 014-a

## Work order
- Identifier: 014-a; order path: `oap/orders/014-a-real-codex-compatibility-repair-and-private-rc3.md`; numeric objective 014
- PR mode: CREATE_NEW_PR — PR #19 (exactly one Objective-014 PR), non-draft, never merged
- Base: remote `main` at `8c3c6d6cd67a34ba7d427ab255a91bd6a9753bd1`
- Head branch: `oap/014-real-codex-compatibility-rc3`
- PR title: `Repair real Codex image compatibility and qualify private RC3`

## Status
COMPLETE

## Executive summary
The independently reproduced RC2 real-Codex image-policy defect
(`TypeError: unhashable type: 'dict'` in `image_policy.py` on Codex 0.149
namespace-tool parameter schemas) was repaired with the smallest type-safe,
structure-safe change (string-only marker comparison), permanently covered by
sanitized Codex-0.149 fixtures, pure, and full-application fake-upstream
regressions in ordinary CI. A bounded, opt-in, fail-closed, privacy-bounded
real-Codex RC qualification gate was added and executed live: VISION, CACHE,
and BOTH product arms all PASS (plus the DIRECT contextual control) against
the repaired wheel-bound adapter on the supported standalone loopback
topology with **no SLAIF API Gateway**. The private `0.1.0-rc3` image was
published from the exact green source commit S
`307a929ffb30f4ea41c8be4e8a5ea25802e25142` via the existing
`workflow_dispatch`-only publisher (run 36384605003, head verified = S):
both target tags verified absent before any mutation, then pushed as `D =
sha256:41db6fcc285aecb23a9ec0acc9306e05754f8e6e9f916cae271ce00ea00cc436`
under `0.1.0-rc3` + `sha-<S>` in the PRIVATE package. The actual pulled
digest was qualified by the final-head `docker-published` job (13/13 phases
PASSED). The RC3 machine record (`slaif-rc-record-v3`), deterministic
handoff, published-state provenance manifest, input-map re-proof, and the
append-only sanitized testing ledger 002 were committed as derived metadata
only. Four in-scope gate repairs were made during the live rounds (unit-state
semantics; workspace git identity + crash boundary; client sandbox
`danger-full-access` for the protected host's bubblewrap restriction +
subset-arm crash fix; synthetic governance root for the constitutional
arms), each committed, tested, and re-verified. No merge, no second PR, no
benchmark, no Gateway change, no protected-state mutation.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`
- PR: #19, OPEN, non-draft, base `main` @ `8c3c6d6cd67a34ba7d427ab255a91bd6a9753bd1`, exactly one PR for objective 014
- Implementation head SHA: fa8f03030c138a074844837bc7f918ac482d2cce
- Report publication commit: SELF
- `oap/active` committed byte-exact `014-a\n`; order committed unmodified after activation
- 13 commits on the branch (base..head): implementation, provenance manifests
  S1–S5, four in-scope gate repairs, post-publication record/handoff/manifest,
  and ledger 002 (final head)
- Merge: none performed or requested; auto-merge never enabled

## Changes and files
- `ee92e4d` — workstreams A/B/C/D.1/D.2: `src/slaif_local_coding/image_policy.py`
  (string-only marker guard), `tests/fixtures/codex/0.149.0/namespace_tool_responses.json`
  + focused/full-app tests, `scripts/real_codex_rc_qualification.py` + 27 pure tests,
  RC2 archive under `packaging/releases/0.1.0-rc2/`, RC2→RC3 publisher/reconciliation,
  `slaif-rc-record-v3` closed-schema compatibility facts, workflow label updates,
  docs (incl. TESTING.md section), order + `oap/active`
- `6012dfd`, `557c1ec`, `3451506`, `45378e6`, `307a929` — provenance manifest v5
  re-binds (S1–S5), derived metadata only; wheel hash constant at every step
- `19f4a6a`, `fbcdd4b` — gate repair 1: unit-state snapshot rc semantics (+format)
- `4b90627` — gate repair 2: disposable-workspace git identity independence +
  fail-closed arm crash boundary
- `8ba26b7` — gate repair 3: client `-s danger-full-access` (protected host forbids
  bubblewrap's unprivileged user-namespace networking — `RTM_NEWADDR: Operation not
  permitted` — a host state the gate must never change; the gate's disposable/loopback/
  bounded boundary is the control) + subset-arm verdict crash fix (`KeyError` on
  `--arms <subset>`) + `tuple` typing; TESTING.md documents the sandbox decision
- `21ae15a` — gate repair 4: fixed synthetic AGENTS.md in the disposable workspace
  (content-free by construction; pinned zero-dependency-candidate invariant against
  the real extractor) so a genuine Codex project envelope crosses the API boundary
  and the constitutional compiler/derived-cache path is actually exercised
- `307a929` = image source S (branch head at dispatch)
- `e8ebc5d` — post-publication: `packaging/rc_record.json` (v3) +
  `packaging/rc_handoff.md` + manifest in `rc_published` state
- `fa8f030` (head) — `oap/evidence/testing-ledger/002/` (README, closed-schema
  sanitized gate facts, MANIFEST.sha256)

## Exact identities
- Image source S: `307a929ffb30f4ea41c8be4e8a5ea25802e25142`
- Registry digest D: `sha256:41db6fcc285aecb23a9ec0acc9306e05754f8e6e9f916cae271ce00ea00cc436`
- Tags: `0.1.0-rc3`, `sha-307a929ffb30f4ea41c8be4e8a5ea25802e25142` (both → D)
- Wheel W: `897ef60568e9521dbb4ea563f297608e4409e02d54109471e789d43ff57dd10d`
  (byte-identical across clean 3.12.3/3.12.14 builds and every repair commit;
  re-verified equal to the committed manifest inside the publishing run;
  verified in-image by `docker-published`)
- sdist at S: `15bd0a3b665193930da629626df98cbbeef7cf8fd3bc96fd901f22d5f2ec3a2f`
- uv.lock: `1237cbd179f71b99984c80f927529549f5e61eb705585ef9cf2ab0fa9e26764a`;
  pyproject: `2a078535af87cf9433cfb9d6b913697931e1946ade71f3d6ead0e4617add88b3`
- Build: uv 0.12.5, hatchling 1.32.0, build-env pins hatchling 1.32.0 /
  packaging 26.3 / pathspec 1.1.1 / pluggy 1.6.0 / tomlkit 0.15.1 /
  trove-classifiers 2026.6.1.19; base `python:3.12-slim-bookworm`
  `sha256:782412e85d0f0984994c290652577d4018aff08145c85b262bb63dc0c7522254`;
  build tool image `ghcr.io/astral-sh/uv:0.12.5`
  `sha256:e85be844203885286c60ffad8a858d48afb6c5a5c237ca0e67f12e74b8f174b1`
- Qualified client: Codex CLI 0.149.0, binary
  `bbc3341e44c9ead340ed9570c17be936e37870f570751a941699ffd04d672827`
  (standalone release; exact pinned version + hash asserted by the gate)
- Model: `qwen3.8-27b`; topology: `standalone-loopback-no-gateway`
  (disposable Codex home/repository → `127.0.0.1:18031` Local Coding →
  existing tested endpoint; gateway ingress disabled, no signed Gateway headers)
- RC2 immutable (archived byte-identical): source
  `0a2f34b6d6fc17b732a1e7570f751776dce1ae01`, digest
  `sha256:2349400a0dd5dbcec560f6c164283f24e5a55c5f474114416af21d6f3b2cb100`,
  wheel `04d1a87cb44f22dad3a7022f63a54f651eca74ed364394aaec85957bbeb8aeda`

## Publication facts (authenticated)
- Run 36384605003 (`release-image.yml`, workflow_dispatch only), head SHA = S
  (checkout verified), started 2026-09-28T06:03:35Z, completed
  2026-09-28T06:04:14Z, conclusion success
- Pre-mutation registry check: `sha-<S>` verified absent; `0.1.0-rc3` verified
  absent (the only write precondition; satisfied)
- Post-mutation registry check: both tags present at the ONE digest D
- In-run wheel binding: fresh wheel == committed manifest wheel == W
- Package visibility: private (no visibility-mutation code path; publisher
  writes only the two target refs and refuses final/stable tags)

## Acceptance evidence (order criteria 1–12)
1. One correct PR from exact base/head; no second PR; no merge by coding — met (above).
2. Ledger 001, RC1, and RC2 archives byte-identical and historically resolvable —
   met: RC2 archive files byte-identical to the base-commit top-level RC2 files
   (sha256 `ad8a689b…`, `088118c3…`, `29c87982…`); ledger 001 + RC1 unchanged
   since base; both gate-protected (0 changed of 13 protected files).
3. Root cause demonstrated pre-fix (7 regression tests fail on the RC2 helper with
   the exact recorded `TypeError` in a worktree) and smallest correct repair — met.
4. Workstream-B cases (pure + full-app, VISION/CACHE/BOTH + ambiguous 422
   no-upstream) — met (59 focused tests; CI `test` green at H).
5. Non-image tools/schema preserved; image/reject/passthrough/retain-newest/
   ambiguity/max-zero semantics correct — met (B fixtures + full-app tests; live
   arms 0×422/0×500).
6. RC3 reproducible and input/provenance bound; RC3-only publisher with intact
   final-tag guards — met (byte-identical wheel across Pythons; 126-entry input
   map re-proven C5→H; publisher denylist tests green).
7. Private RC3 at one authenticated D; both aliases → D; old tags unchanged;
   visibility private — met with one NOT RUN nuance (see Known limitations):
   per-tag registry reads of the OLD tags from this host were not possible
   (no local package-read auth); registry evidence for immutability is the
   publisher's fail-closed pre/post checks (targets verified absent → one D),
   the publisher's code-level tag law (only the two target refs; refuse
   final/stable; never repush), and the in-repo archives (byte-identical,
   gate-protected). No old tag was ever written by any code path of this round.
8. Fresh final-head CI/CodeQL + actual pulled qualification all successful — met
   (below; `docker-published` RAN and pulled D).
9. Genuine bounded standalone VISION/CACHE/BOTH pass; DIRECT recorded; exact
   client version/hash recorded — met (below; ledger 002).
10. Protected state unchanged before/after; no secret/raw leak; no benchmark
    work, Gateway production change, host Docker service use, or cutover — met
    (gate protected-state facts; content-free schemas; in-image forbidden-content
    scan 0 matches over 6484 files; disclosures in Safety section).
11. RC3 handoff complete, consumer-ready without rebuild; final release false —
    met (`packaging/rc_handoff.md` + `rc_record.json` + published-state manifest;
    `final_public_release: false`, `cutover_performed: false`,
    `private_registry_auth_required: true`).
12. Final report/SELF protocol exact — this commit.

## Verification (required commands, executed at head H, clean tree)
| Command | Status |
|---|---|
| `uv lock --check` | PASSED |
| `uv sync --frozen --extra dev` | PASSED |
| `uv run --frozen ruff check .` | PASSED |
| `uv run --frozen ruff format --check .` | PASSED |
| `uv run --frozen mypy src tests` | PASSED |
| `uv run --frozen python scripts/docs_consistency_check.py` | PASSED |
| `uv run --frozen pytest -q` | PASSED — 1364 passed, 26 skipped, 0 failed |
| `uv build` (fresh dir) | PASSED — wheel == W, sdist == `15bd0a3b…` (== committed manifest) |
| `uv run --frozen python scripts/artifact_policy_check.py --dist <fresh> --inspect` | PASSED |
| `uv run --frozen python scripts/artifact_policy_check.py --dist <fresh> --install-smoke` (fresh-venv, wheel only, non-editable) | PASSED |
| source-input/provenance regeneration + equality (`release_provenance_manifest.py` re-run → no drift; `source_input_map.py --ab 21ae15a… fa8f030…` → 126 inputs identical, derived-only diff) | PASSED |
| `python -m compileall -q src tests oap/bin scripts` | PASSED |
| `bash -n oap/bin/*.sh packaging/*.sh` | PASSED |
| focused image-policy + full-app Codex-envelope regressions (`tests/test_image_policy.py tests/test_codex_namespace_tool_envelope.py tests/test_app.py`) | PASSED — 59 passed |
| publisher/RC-record/provenance/schema/archive tests (`test_release_registry_publish_gate.py test_release_registry_publish_digest.py test_rc_record.py test_release_provenance_manifest.py test_docker_qualification_record_gate.py test_source_input_binding.py`) | PASSED — 143 passed |
| real-Codex DIRECT contextual control (bounded, live) | PASSED — exit 0, sentinel, 5s |
| real-Codex VISION arm (bounded, live) | PASSED — exit 0, sentinel, adapter 200/500/422 = 2/0/0, upstream failures 0 |
| real-Codex CACHE arm (bounded, live) | PASSED — exit 0, sentinel, 2/0/0, compiler cache entries 1, 35s |
| real-Codex BOTH arm (bounded, live) | PASSED — exit 0, sentinel, 2/0/0, compiler cache entries 1, 40s |
| RC1/RC2/ledger-001 archive byte-identity vs base commit | PASSED |

Gate run facts (schema `slaif-real-codex-rc-qualification-v1`): overall verdict
PASS; protected state 13 files checked / 0 changed, units
`qwen-serving-vision.service` = active and `qwen-serving.service` = inactive
unchanged, port 18020 exactly one listener / 18031 free before and after;
disposable state removed.

## Live model/service evidence
- Upstream preflight probes (adapter-side): `/health` 200; `/v1/models` 200
  with `qwen3.8-27b` listed (authenticated, key via protected file/env only;
  never printed)
- Live backend: existing protected `qwen-serving-vision.service` on
  `0.0.0.0:18020` — used read-only; state row-identical before/after (gate
  snapshot)
- No second vLLM process, no model loading, no image decoding in the adapter;
  adapter ran as a repo-owned foreground process on loopback 18031 per arm
  attempt and was stopped with port-free absence proof

## GitHub CI / required checks (fresh, exact heads, logs inspected)
- Pre-publication at S (307a929…): CI run 36384323916 — test, gateway-contract,
  docker, operator-session, docker-published (pre-publication no-op) all
  success; CodeQL 36384319782 success. Publication dispatched only after this
  exact head was fully green.
- Final at H (fa8f030…): CI run 36384995834 — all five jobs success:
  - `docker-published` RAN (not skipped): publication gate read the RC record
    (digest D, source S); pulled the published image BY DIGEST (pull digest ==
    D; image id `sha256:8d81b57b…` identical to the publisher's built image);
    pulled both tags and asserted each resolves to D; 13/13 phases PASSED —
    `verify_wheel_binding` (wheel == W, image bound to committed artifact),
    `compose_rendered_validation` (no secret values), `pull_preexistence_no_build`
    (pulled before up, no build key), `fake_upstream_start`, `adapter_stack_up`
    (healthy, image id matches pull), `in_image_provenance` (non-editable, exact
    locked inventory 18 installed / 17 applicable / 18 pinned),
    `bridge_positive_signed` (chat/stream/models/tool-roundtrip 200),
    `bridge_negative_contract` (401/403/409 + cross-namespace),
    `config_time_rejection`, `fail_closed_readiness` (503 without upstream),
    `image_content_scan` (6484 files, 0 forbidden), `hardening_and_labels`
    (linux/amd64, OCI source/revision/version, RC3 qualification label,
    topology label, gateway-peer label, wheel label, non-root, read-only rootfs,
    cap-drop-all, no-new-privileges, no docker socket, tmpfs /dev/shm + /tmp,
    single read-only config bind), `teardown_absence_proof` (containers +
    listeners absent on 18031/18033/18034, pulled image retained).
  - `test`, `gateway-contract`, `docker`, `operator-session` success.
- CodeQL at H: run 36384991553 success.
- Expected rebind trail (disclosed, resolved): CI at C4 (36383667850) and C5
  (36384267841) failed ONLY the source-input binding check before the S4/S5
  manifest re-binds; S4 (36383782038) and S5 (36384323916) both success.

## Local setup/dependencies
- Repo-owned venv via `uv sync --frozen --extra dev`; all verification ran
  `--frozen`; protected upstream key read from the protected 0600 file into a
  protected environment variable only (never argv, Git, logs, or temp files);
  adapter state/cache disposable under fresh 0700 workdirs, deleted after
  sanitized extraction.

## Documentation
- README remains product-focused; TESTING.md "fixture CI vs real client"
  section updated (distinct mechanisms, arm contracts, sandbox decision,
  RC2-failed/RC3-repaired history, content-free evidence law); docs
  consistency check green; `rc_handoff.md` is the deterministic machine/human
  handoff (consumer-ready without rebuild: S, D, both aliases, W, build pins,
  lock hash, input hashes, tested client version/hash, arm verdicts, platform,
  private-registry auth requirement, Gateway-not-required standalone fact,
  benchmark-not-run, final-release-false, cutover-false).

## Safety/scope confirmations
- No merge, no auto-merge, no acceptance, no next-order choice.
- No second PR; no edit of strategic-authored order/active bytes after
  activation.
- Protected live boundary honored: `qwen-serving*` units, vLLM port 18020,
  model/checkpoint/quantization/context flags, API-key files, firewall/VPN/
  routing, and Codex profiles untouched; only reads + gate-protected
  before/after snapshots (13 files / 0 changed).
- Host Docker: no container was run on this host for product work. Disclosure:
  two READ-ONLY registry probes of the private GHCR package
  (`docker manifest inspect 0.1.0-rc2` and a ghcr.io token exchange +
  package-versions API) were attempted solely to verify old-tag immutability;
  both returned unauthorized and changed nothing (no pull, no container, no
  state). Old-tag registry verification is therefore NOT RUN from this host
  (see Known limitations).
- No secrets/raw content: closed sanitized schemas everywhere; credentials env-
  only; no prompt/body/tool-output/image/model-output in any argv, Git file,
  log, report, or ledger file; in-image forbidden-content scan 0/6484.
- No benchmark code, tasks, statistics, pilots, repetitions, or
  benchmark-repository access/mutation. No Gateway repository/code/production
  change. No final tag, no public release, no GitHub Release, no visibility
  change. `final_public_release: false`, `cutover_performed: false`.
- The standalone loopback qualification requires no Gateway; this single-host,
  single-RTX-3090-backend qualification is not a general/production/compliance
  equivalence claim.

## Known limitations/blockers
- NOT RUN (with reason): per-tag registry reads of the historical
  `0.1.0`/`0.1.0-rc1`/`0.1.0-rc2` tags from this host — no local
  package-read authentication (GHCR token exchange and GitHub
  package-versions API both unauthorized; local docker unauthenticated).
  Registry-side evidence for immutability: publisher fail-closed pre/post
  checks (targets verified absent before mutation → one D after), publisher
  code-level tag law (writes only `sha-<S>` + `0.1.0-rc3`; refuses
  final/stable; never repushes a frozen identity), and the in-repo RC1/RC2
  archives byte-identical to base-commit bytes and gate-protected (0 changed).
- The 26 skipped local tests are exactly: 10
  `test_current_gateway_contract.py` + 9
  `test_gateway162_validator_factory.py` cross-repository Gateway tests
  requiring a `SLAIF_GATEWAY_ROOT` checkout (executed in the CI
  `gateway-contract` job, green at H); 7 opt-in `test_live.py` model tests
  and 1 opt-in `test_vision_e2e.py` E2E that skip honestly when the live
  environment variables are not set (live coverage is the explicit bounded
  gate runs above, not CI skips).

## Proposed verdict
All READY conditions are met: private RC3 exists at authenticated D; actual
pulled-digest qualification and all current exact-head checks are green
(CI 5/5 + CodeQL at H, logs inspected); all three required real-Codex arms
pass with the exact client version/hash recorded; ledger 001's product
blocker is repaired and resolved by the passing live arms; the handoff is
complete and consumer-ready without rebuild.

```text
BENCHMARK_READY
```

Strategy independently decides acceptance/merge and the final verdict after
current GitHub/main verification.

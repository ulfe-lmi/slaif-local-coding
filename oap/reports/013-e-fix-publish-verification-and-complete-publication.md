# OAP Coding-Agent Report — 013-e

## Work order
- Identifier: `013-e`; order path `oap/orders/013-e-fix-publish-verification-and-complete-publication.md` (strategic-authored bytes committed verbatim in W5); `oap/active` → `013-e`; numeric objective `013`
- PR mode: AMENDED_EXISTING_PR (PR #15, the single Objective-013 PR)

## Status
BLOCKED (pre-dispatch: the D3 precondition "CI at W5 FULLY GREEN 4/4 before any
dispatch" is NOT met because the `test` CI job fails at `ruff format --check .`
solely on the strategic-authored, immutable 013-e order file (one missing blank
line inside its fenced Python code block). NO dispatch was performed; the ONE
controlled publication is NOT consumed; registry state is unchanged. D1 and D2
are complete, verified, and pushed at implementation head W5. The exact
unblocking strategic act and the exact one-blank-line byte delta are recorded
under Known limitations/blockers.)

## Executive summary
W5 (`e42598775746321630eaa7f9e2d862b1abbec118`, direct child of the 013-d
report commit R `5943996…`) was implemented exactly per order and pushed to
PR #15: (D1) `scripts/release_registry_publish.py` now joins push stdout+stderr
(stdout first) and extracts the digest via a new pure, unit-tested
`extract_push_digest()` parser (both observed docker-CLI final-line forms;
last-match wins; `None` when no line matches), and the failure message names
the ref and includes the last 25 non-empty output lines with any
`SLAIF_GHCR_TOKEN` value redacted to `***` — publish sequence, guards,
reference builders, `--self-check-refs`, and argument handling are
byte-identical; 12 new deterministic unit tests (no docker, no network). (D2)
generator/E3 objective bumped to `013-e` and `M_W5` regenerated
(not-yet-published; `generated_from` = R; wheel `H_new` unchanged; new sdist
hash from the new test file; peer frozen at `08ca421…`). Local verification
was fully green (ruff check, mypy, full pytest 1110 passed / 26 standing
skips, double `uv build` byte-reproducible, artifact policy inspect +
install-smoke, self-check-refs). CI at W5: `gateway-contract`, `docker`
(all 15 qualification phases PASSED, wheel bound to `H_new`), and
`docker-published` (explicit not-yet-published skip path) are SUCCESS; the
`test` job is FAILURE with the single failing step `uv run --frozen ruff
format --check .` flagging exactly one file — the 013-e order file itself —
for one missing blank line inside the order's fenced `python` code block
(line 134: insert one blank line between the `)` of `PUSH_DIGEST_LINE_RE =
re.compile(...)` and `def extract_push_digest`). That byte is
strategic-authored and immutable this round (order W5 file set: "strategic-
authored bytes verbatim"; non-goal: `oap/orders/*` immutable; `ci.yml` and
`pyproject.toml` frozen; no other file may be added to W5), so the failure
cannot be repaired in-scope. Per the order's D3 precondition and the
constitution's stop law, the round STOPs before dispatch: no
`workflow_dispatch`, no registry write, no D5/D6/D7. The pre-existing
`sha-be3c78b…` tag (W4 build, non-public package) was not touched.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`; PR #15 `https://github.com/ulfe-lmi/slaif-local-coding/pull/15` — OPEN, MERGEABLE (`CLEAN`), no auto-merge, not merged
- Base: `main` @ `a04693e6792df6a8ad4262acfb46336a0f662202` (unchanged); starting remote SHA: `59439963a02e8cd6c341708e606f907ef1e6771d` (R, the 013-d report commit)
- Implementation head SHA: `e42598775746321630eaa7f9e2d862b1abbec118` (W5; first parent = R; 7 files)
- Report publication commit: SELF
- Implementation commits pushed before report: W5 (one commit)
- New PR this round: NO; amended existing: YES (PR #15 head advanced R → W5 → SELF); merge performed: NO
- Zero Git tags; zero GitHub Releases (verified via `git ls-remote origin` at round start; no tag/Release created this round)

## Changes and files
W5 (7 files, exactly the ordered set):
1. `scripts/release_registry_publish.py` (D1): added module-level `PUSH_DIGEST_LINE_RE` and pure `extract_push_digest(output) -> str | None` (last match wins; current-CLI `<ref>: digest:sha256:<64-hex> size:<n>` form and legacy bare `digest: sha256:<64-hex>` / `digest:sha256:<64-hex>` forms; returns the full `sha256:<64-hex>` digest, `None` otherwise); rewrote `_push_digest(ref)` to join `proc.stdout.decode() + proc.stderr.decode()` (stdout first) and call the parser; on `None` it raises `PublishError` naming the ref with the last 25 non-empty output lines, every line redacted for a set non-empty `SLAIF_GHCR_TOKEN` value (→ `***`). NOTHING else in the script changed (publish sequence sha-tag push → registry-API cross-check → 0.1.0 no-silent-repoint guard → release-tag push → final two-tag verification → `SLAIF_PUBLISHED_DIGEST`/`GITHUB_OUTPUT` emission, reference builders, `--self-check-refs`, argument handling all byte-identical; module docstring unchanged).
   Regex note (implementer's-discretion clause of D1.1): the implemented suffix is `(?:\s+size:\s?\d+)?` — it accepts the size suffix with OR without a space after the colon. The order's sketch regex `(?:\s+size:\d+)?` matches only the no-space spelling; the non-TTY docker CLI's final line has historically been printed as `size: <n>` (space), and no host push was authorized to capture the exact 29.x bytes, so the implemented form is format-agnostic across both spellings. The observable contract (last-match wins; both digest-line forms; `None` when no line matches) is exactly as ordered, pinned by tests for both spellings and for the no-size form.
2. `tests/test_release_registry_publish_digest.py` (D1, NEW; 12 test items, deterministic, no docker/network/host state; imports the module from `scripts/` via importlib): full realistic non-TTY transcript (banner + layer progress + final `<ref>: digest:… size: <n>`) → digest; release-tag final-line form with the real spaced size suffix, the no-space variant, and the no-size variant; legacy bare `digest: sha256:…` and `digest:sha256:…`; multiple candidates → LAST match wins; no digest line / empty output → `None`; malformed digests (63-hex short, 65-hex long, non-hex) → `None` (4 parametrized); failure path with monkeypatched `_docker` + sentinel `SLAIF_GHCR_TOKEN` → `PublishError` contains the ref and the output tail and does NOT contain the sentinel (redaction to `***` proven); failure path without the token env keeps the tail; `self_check_references()` still returns 0.
3. `scripts/release_provenance_manifest.py` (D2): `OBJECTIVE = "013-e"` + docstring order reference `(013-e)` (same pattern as 013-d). No other generator change.
4. `tests/test_release_provenance_manifest.py` (D2): E3 objective assertion → `"013-e"`.
5. `packaging/release_provenance_manifest.json` (D2) → `M_W5`: `objective "013-e"`; `oci.published: false`; `oci.image_digest: null`; no `release` key; `status.released: false`; `gateway_peer.commit = 08ca421bee1ddca62078302b910e8be88cf705be` (FROZEN, unchanged); `artifacts.wheel.sha256 = oci.wheel_sha256 = 879baa3ad19e0f513090add965d267957d27f7bcd904d1e225586d76126f8b19` (`H_new`, 83,352 B, 26 entries, unchanged); `artifacts.sdist.sha256 = 6537f6266cc7a77ce427fd7c8af0675abb3b496d444b75e7c858fec909fc9fc2` (NEW — 439,894 B, 108 entries; the new test file is an sdist input); `generated_from.git_commit = 59439963a02e8cd6c341708e606f907ef1e6771d` (= R, W5's parent, per the ordered generation point).
6. `oap/orders/013-e-fix-publish-verification-and-complete-publication.md` — strategic-authored bytes verbatim (new file).
7. `oap/active` → `013-e` (transcript).
NO other file in W5. NO `release-image.yml` change (byte-identical), NO `ci.yml`, NO `docs/`, NO `src/`/`pyproject.toml`/`uv.lock`/`config/`/`Dockerfile`/`.dockerignore`/compose files, NO `scripts/ghcr_tag_check.py`, NO gateway fixture/gate change.

## Acceptance evidence
### D1 — digest-capture fix
- Result: COMPLETE (locally verified; in-repo).
- New tests: 12 items — `test_non_tty_transcript_returns_final_digest`, `test_release_tag_final_line_form`, `test_legacy_bare_digest_forms`, `test_multiple_candidates_last_match_wins`, `test_no_digest_line_returns_none`, `test_malformed_digest_lines_return_none[short/long/non-hex×4]`, `test_failure_path_includes_tail_and_redacts_token`, `test_failure_path_without_token_env_keeps_tail`, `test_self_check_references_still_returns_zero` — `pytest -q tests/test_release_registry_publish_digest.py`: **12 passed** (0.27–0.32 s).
- `python3 scripts/release_registry_publish.py --self-check-refs`: **PASSED** (exit 0; prints `reference self-check OK: sha-tag ghcr.io/ulfe-lmi/slaif-local-coding:sha-0000…; release-tag ghcr.io/ulfe-lmi/slaif-local-coding:0.1.0`).
- `git diff` of the script against R: only the `PUSH_DIGEST_LINE_RE`/`extract_push_digest` addition and the `_push_digest` rewrite; all other bytes identical (staged diff reviewed: 45 lines changed, confined to that region).
### D2 — generator/E3 bump + `M_W5`
- Result: COMPLETE. Fresh `uv build` at W5's tree reproduced `M_W5` byte-for-byte: wheel `879baa3a…` = `H_new` and sdist `6537f626…` = `M_W5` sdist hash; a SECOND independent `uv build` into a separate directory produced identical hashes (deterministic). `artifact_policy_check.py --inspect`: `{"ok": true, "violations": []}`; `--install-smoke`: `{"ok": true, "violations": []}`.
### D3 — the ONE controlled publication at W5
- Result: NOT RUN — dispatch precondition NOT met (see GitHub CI below). Per D3 the dispatch requires "CI at W5 FULLY GREEN 4/4 BEFORE any dispatch"; W5 CI is 3/4 (the `test` job fails on the order-file format violation). Per the stop law the round STOPs: **no `gh workflow run` was executed, the single controlled dispatch is NOT consumed, and no registry write of any kind occurred.** Layers 1–8 classification: NOT ATTEMPTED (no run exists to classify).
### D4 — registry-state continuity
- Result: RECORD-ONLY, satisfied vacuously — no dispatch, so no new tag was written and no existing tag was repointed. The pre-existing `sha-be3c78b…` tag (W4 build, digest D1 not recoverable) and its registry version are untouched. Build-reproducibility note: `git diff --name-only be3c78b2…(W4)..e4259877…(W5)` intersects the build-context set (`Dockerfile`, `.dockerignore`, `src/`, `pyproject.toml`, `uv.lock`, `LICENSE`, `NOTICE`, `README.md`) in NOTHING (grep intersection returned empty). The CI `docker` job at W5 built the qualification image on the runner (PR merge-commit `GITHUB_SHA` `fa1c9623…` — standard PR-CI behavior; that image was discarded with the runner); a D3 dispatch at W5 would build with `SLAIF_GIT_SHA = GITHUB_SHA = W5`, making the S/P/D binding exact. `D` was not captured (no run).
### D5 — package visibility (layer 7)
- Result: NOT RUN — strictly downstream of a successful D3 push. The package remains non-public (013-d record stands).
### D6 — release-record commit P
- Result: NOT RUN — no recorded `D`; `packaging/release_record.json` is correctly absent from the W5 tree (pre-publication state).
### D7 — CI at P + post-publication doc verification
- Result: NOT RUN — no `P`. The 013-d C4 post-publication documentation statements remain true at the current (pre-publication) state; the D7 verification duty (and any 013-f staleness recording) is reached only after a successful publication.

## Verification
- `uv run --frozen ruff check .`: **PASSED** — `All checks passed!` (full repo, W5 tree)
- `uv run --frozen ruff format --check .`: **FAILED (single known violation)** — `1 file would be reformatted, 362 files already formatted`; the one file is `oap/orders/013-e-fix-publish-verification-and-complete-publication.md` at line 134 (one missing blank line in the fenced code block; see Known limitations/blockers). All 7 W5 code/manifest files pass: `ruff format --check` on the changed files → `2 files already formatted` / `1 file already formatted`.
- `uv run --frozen mypy src tests`: **PASSED** — `Success: no issues found in 72 source files`
- `uv run --frozen pytest -q` (full suite, W5 tree): **PASSED** — `1110 passed, 26 skipped in 76.65s` (the standing 26 routine skips remain as designed; +12 items vs the 013-d local count are the new D1 tests)
- `uv build` (fresh, W5 tree, two independent builds): **PASSED** — byte-identical: wheel `879baa3ad19e0f513090add965d267957d27f7bcd904d1e225586d76126f8b19` (= `H_new`), sdist `6537f6266cc7a77ce427fd7c8af0675abb3b496d444b75e7c858fec909fc9fc2` (= `M_W5` sdist hash)
- `uv run --frozen python scripts/artifact_policy_check.py --dist <fresh> --inspect`: **PASSED** — `{"ok": true, "violations": []}`
- `uv run --frozen python scripts/artifact_policy_check.py --dist <fresh> --install-smoke`: **PASSED** — `{"ok": true, "violations": []}`
- `python3 -m compileall -q src tests oap/bin scripts`: **PASSED** (no output)
- `bash -n oap/bin/*.sh packaging/*.sh`: **PASSED**
- `python3 scripts/release_registry_publish.py --self-check-refs`: **PASSED** (exit 0)
- `uv run --frozen pytest -q tests/test_release_provenance_manifest.py` (E3 gate, W5 tree with `M_W5`): **PASSED** (within the 1110; E3 regenerated manifest equals committed `M_W5` modulo `generated_from.git_commit`, which is R = ancestor of W5)
- Secret/raw-log scans: no secrets or raw content added; the only new strings are hashes, tag names, and the redaction token `***`. The redaction test proves a sentinel token value never appears in the failure message.

## Live model/service evidence
- No live model calls this round (no protected-model/Qwen inference; explicit non-goal).
- No docker build/run/up on the protected host (all docker work ran on GitHub CI runners only).
- Registry (token-free, `scripts/ghcr_tag_check.py`): BEFORE (round start): `0.1.0` → `absent`; `sha-be3c78b2016d5d40ce9155df8f94d14525c43d39` → `absent` (anonymous resolution denied — non-public package, per the script's contract). AFTER (post-round): `0.1.0` → `absent`; `sha-e42598775746321630eaa7f9e2d862b1abbec118` → `absent` (never pushed — no dispatch). No repoint, no deletion, no visibility change.
- Protected-host before/after read-only probes (identical in both columns; no protected resource moved):

| Resource | Before | After |
|---|---|---|
| `qwen-serving-vision.service` | active, MainPID=23961 | active, MainPID=23961 |
| `qwen-serving.service` | inactive (MainPID=0) | inactive (MainPID=0) |
| Port 18020 | `LISTEN 0.0.0.0:18020`, owner `vllm pid=23961` only | identical |
| Ports 18031/18033/18034 | closed | closed |
| `docker ps -a` (read-only, sudo) | three pre-existing exited non-slaif containers (`0e3109680183`/`cc5e7d551c0a` — `chrockey/fpt-votenet:v0.1.0`, Exited 2 years ago; `379dcff9d7f2` — `hello-world`, Exited 2 years ago) | identical (same IDs/images/statuses); zero slaif images on the host (before and after: `postgres:16`, `hello-world:latest`, `chrockey/fpt-votenet:v0.1.0` only) |
| `~/.codex/qwen-neumann.config.toml` | size=858, mode=600, mtime=2026-09-13 11:59:21.852183775 +0200 | identical |

## GitHub CI / required checks
- CI at W5 (`e4259877…`), run `35254602764` (CI workflow):
  - `test`: **FAILURE** — steps: checkout SUCCESS, `uv sync --frozen --extra dev` SUCCESS, `uv run --frozen ruff check .` SUCCESS, `uv run --frozen ruff format --check .` **FAILURE** (log, verbatim essence): `unformatted: File would be reformatted --> oap/orders/013-e-fix-publish-verification-and-complete-publication.md:134:1 … 1 file would be reformatted, 362 files already formatted … Process completed with exit code 1`; subsequent steps (mypy, pytest, uv build, artifact policy, install-smoke, compileall, bash -n) SKIPPED by the runner.
  - `gateway-contract`: **SUCCESS** (strict current-Gateway contract gate, 18 selected tests, frozen peer `08ca421…`, network guard enabled).
  - `docker`: **SUCCESS** — wheel-binding step PASSED (fresh wheel sha256 == manifest `H_new`) and all 15 qualification phases PASSED: `verify_wheel_binding`, `compose_rendered_validation`, `compose_merge_equivalence`, `image_build`, `fake_upstream_start`, `adapter_stack_up`, `in_image_provenance`, `bridge_positive_signed`, `bridge_negative_contract`, `config_time_rejection`, `fail_closed_readiness`, `image_content_scan` (6487 files scanned, 0 forbidden matches), `hardening_and_labels`, `operations_stop_start_recreate_upgrade_rollback`, `teardown_absence_proof` — harness summary `"status": "PASSED"`.
  - `docker-published`: **SUCCESS** on the explicit not-yet-published skip path (publication gate step output, verbatim: `not yet published (packaging/release_record.json absent) — docker-published skipped`; pull/label/contract steps SKIPPED by design).
- All required green at drafting: **NO** (3/4; the `test` failure is the order-file byte defect below, not an implementation defect).
- The E3 manifest gate, full pytest, and mypy did NOT RUN in CI at W5 (the `test` job halted at the format step before them); they PASSED locally on the identical W5 tree. No `P` exists, so no CI run at `P`.
- Report-head checks may re-run; strategy verifies.

## Local setup/dependencies
- Repo venv (Python 3.12.3, uv 0.12.5, `uv sync --frozen --extra dev`); no new dependencies, no `pyproject.toml`/`uv.lock` change.
- Scratch only under `/tmp` (outside the repository): two `uv build` output directories and CI job log captures. Worktree residue `Local`, `clean`, `unchanged` (0-byte untracked root files) left untouched, never committed, never cleaned.
- Sudo: used only for read-only `docker ps -a` / `docker images` on the protected host; no service/systemd/network mutation.

## Documentation
- Not changed this round (NO `docs/` in the W5 file set, per order). The 013-d C4 post-publication statements remain true at the current pre-publication state (publication = the dispatch-only release workflow at the PR's implementation head; no record yet; Git tag `v0.1.0` and GitHub Release do not exist; cutover NOT performed). The D7 post-publication verification duty is reached in the round that actually publishes.

## Gateway freeze re-verification (round time)
- Gateway `main` at round time: `1bdbb8bf1534ea0b3217ced136972d1bced9c448` — UNCHANGED from the value recorded at the order's drafting time (no move beyond `1bdbb8bf…`).
- Contract blob SHAs at frozen `08ca421…` AND at current `main` (byte-identical at BOTH): `app/slaif_gateway/modules/servers/local_coding/contract.py` = `9e8ae5ef8e1f9d8d48bf3627b9a767d86593a6ac`; `app/slaif_gateway/modules/clients/codex_0149.py` = `8976c984c4430d65b3d36bad8565062a8c6f955a`; `app/slaif_gateway/providers/streaming.py` = `73cc9f99e8c3cb2f3eb95173344bfbdc211c71ff`.
- NO re-pin: the fixture `tests/fixtures/gateway/current_peer_authority.json` remains at `08ca421…` (`current_ci_compatibility_authority`); the `gateway-contract` gate at W5 ran green against the frozen peer.

## 013-a R1–R20 re-affirmation (round's final state)
- **R1** (release record exists only in P's tree): **NOT SATISFIED** — no `P`; `packaging/release_record.json` correctly absent from the W5 tree (pre-publication state).
- **R2/R3/R4** (schema-v3 state-aware manifest, generator, E3 gates): **SATISFIED locally at W5** — `M_W5` not-yet-published (`published: false`, `image_digest: null`, `released: false`, no `release` key), `objective "013-e"`, `generated_from = R` (ancestor of W5); E3 suite PASSED locally (1110-run). CI at W5: the E3 suite did NOT RUN (test job halted at the format step) — recorded exactly.
- **R5** (byte-identity law): **SATISFIED** — no changes to `src/`, `pyproject.toml`, `uv.lock` this round; CI wheel-binding PASSED at W5 (docker job: fresh wheel == `H_new` == manifest).
- **R6–R10** (Dockerfile ARG, compose split, two-file harness, static pull gate): **SATISFIED (unchanged)** — files byte-identical across this round; the two-file compose qualification (render/merge equivalence, 15 phases) PASSED in the W5 `docker` job; the R10 static gate is part of the local pytest (PASSED locally; not reached in W5 CI's `test` job).
- **R11** (active workflow, dispatch-only, GITHUB_TOKEN only, no repository secrets): **SATISFIED** — `release-image.yml` byte-identical to the 013-d form; grep proof below.
- **R12** (coding actually triggers the workflow at S): **NOT SATISFIED** — no dispatch (pre-dispatch stop).
- **R13** (`docker-published` gate): the job ran at W5 on the explicit not-yet-published skip path (correct pre-publication behavior); the **EXECUTED** published-image gate is **NOT RUN**.
- **R14** (all existing gates unchanged and green): **NOT SATISFIED at W5** — the `test` job is red on the order-file format violation (a strategic-authored byte defect, not a gate change); `gateway-contract`, `docker`, `docker-published` are green. No 011/012/013 qualification assertion was removed, skipped, or weakened.
- **R15/R16/R17** (documentation reconciliation / status ceiling): **SATISFIED at W5** — no doc changes; no document asserts a status above the manifest's (`released: false`).
- **R18** (gateway main re-verification): **SATISFIED** — see Gateway freeze section (main unchanged at `1bdbb8bf…`; blobs identical at frozen pin and main; gate green).
- **R19** (exact round sequence): executed through "implementation commits → W5 (M_W5; no release record)" and STOPPED at "CI at S fully green" (3/4; the red is the order-file byte defect) — per the stop law: no workflow trigger, no `P`, report pushed as the final round commit (child of W5).
- **R20** (protected-host invariance): **SATISFIED** — before/after probes identical; no docker build/run/up on the host.

## Safety/scope confirmations
- Unrelated files: W5 contains exactly the 7 ordered files; worktree residue (`Local`, `clean`, `unchanged`) untouched and uncommitted.
- Secrets/raw content: none added; no secret values anywhere in the report or W5 diff; the D1 redaction guard is unit-tested (sentinel never appears in the failure message).
- Grep proofs: `secrets.SLAIF_GHCR_TOKEN` — zero matches outside `oap/`; the only repository matches are the immutable OAP transcripts (`oap/orders/013-c-…`, `013-d-…`, `013-e-…`, `oap/reports/013-d-…`) and this order's text. The workflow's only `secrets.` references are `secrets.GITHUB_TOKEN` (`.github/workflows/release-image.yml` lines 71 and 75).
- Protected 18020/Qwen/Codex fixture changed: **NO** (before/after table identical; no systemd/network/service/firewall/VPN mutation; no host docker build/run/up).
- Required tests skipped/not run: none skipped locally beyond the standing 26; in CI at W5, mypy/pytest/build/policy steps of the `test` job did not run (job halted at the format step) — stated exactly above.
- Scope deviation: none. The only implementer-discretion choice is the size-suffix regex form (documented under Changes and files, D1 note), which strictly widens acceptance to both observed spellings without weakening any other contract.
- Extra objective PR: NO. Coding merge: NO. Auto-merge: NO (PR has none).
- Active/order edited: NO — `oap/active` updated to `013-e` as the ordered transcript; the order file committed byte-verbatim (SHA-256 `028704c4400e3e8003295c752d72e4a6ecdf926a294771c9648d6479120f63be`, 17,652 bytes — the bytes as placed by strategy at round start).
- Report commit report-only: YES (staged exactly `oap/reports/013-e-fix-publish-verification-and-complete-publication.md`; parent = W5).

## Known limitations/blockers
- **BLOCKER (pre-dispatch, strategy-owned):** the strategic-authored 013-e order file, as authored, fails the frozen `ruff format --check .` CI gate. The fenced `python` code block in D1.1 has ONE blank line between `PUSH_DIGEST_LINE_RE = re.compile(...)` (line 132) and `def extract_push_digest(...)` (line 135); ruff 0.16.4 (the locked CI version) requires TWO, and its Markdown code-block formatter is active in `ruff format --check .` (all 115 pre-existing order files pass; this is the first order file with a non-conforming fenced block). Primary evidence: (a) local `uv run --frozen ruff format --check .` on the W5 tree → rc 1, sole violation at `oap/orders/013-e-…md:134:1` (insert one blank line); (b) identical failure in CI run `35254602764` (`test` job, step `Run uv run --frozen ruff format --check .`, exit 1, same diff text); (c) controlled experiment: a `/tmp` copy of the order file with exactly that one blank line added passes `ruff format --check` (rc 0).
- **Why it cannot be fixed in-scope:** the W5 file set requires the order file's "strategic-authored bytes verbatim"; `oap/orders/*` is immutable (non-goal); activated orders must never be edited by coding; `ci.yml` and `pyproject.toml` are frozen this round; and no additional file (e.g., an ignore entry) may be added to W5. Every in-scope lever is closed; the two order requirements (verbatim bytes in W5 + CI at W5 fully green 4/4 before dispatch) are mutually unsatisfiable as authored.
- **Exact unblocking strategic act (one of):** (1) issue a follow-up order (e.g., `013-f`) that re-establishes the publication on the EXISTING W5, amending PR #15 by committing the byte-corrected order file (the exact delta: insert ONE blank line at line 134 of `oap/orders/013-e-fix-publish-verification-and-complete-publication.md`, i.e., between the `)` closing `PUSH_DIGEST_LINE_RE = re.compile(` and `def extract_push_digest`) — a 1-blank-line byte change proven by the controlled experiment to make the gate pass — and then proceeds to the single D3 dispatch + D5/D6/D7 exactly per 013-e; or (2) explicitly authorize, in a follow-up order, that coding commits the ruff-formatted bytes of the 013-e order file as a documented deviation from "verbatim bytes" for that one file. The D1/D2 implementation work is already complete and remote at W5, so the follow-up round is bounded to the order-byte fix + the single dispatch + publication closure.
- Other known state: the GHCR package remains non-public (013-d record); D5 layer 7 was never reached, so the visibility question (expected: one API attempt with the wrapper's no-`packages`-scope credential fails 403 → human UI act) is still open. The existing `sha-be3c78b…` tag (W4 build) remains an unreferenced private version (orphan cleanup is a strategic act).
- The exact non-TTY docker-CLI final-line bytes on docker 29.x could not be captured this round (no host push authorized; the 013-d run's push output was script-captured and never printed). The implemented parser accepts BOTH `size:<n>` and `size: <n>` spellings (and the no-size form), so the layer-6 fix is robust to either; the first successful dispatch will print the exact line in the run log for the record.

## Recommended strategic follow-up
Factual only; strategy decides:
1. Unblock per the exact act above (order-byte correction via follow-up order, or explicit deviation authorization).
2. After a green head: the single `gh workflow run release-image.yml --ref <head>` (D3), D5 visibility handling (expected human UI act: organization `ulfe-lmi` → Packages → `slaif-local-coding` (container) → visibility → public, OR an API PATCH with a packages-scoped credential), D6 `P`, D7 first EXECUTED `docker-published`.
3. Post-merge: Git tag `v0.1.0` → the published image-source commit S + GitHub Release (strategy acts); optional orphan cleanup of the private `sha-be3c78b…` version.

# OAP Coding-Agent Report — 024-h

## Work order
- Identifier: 024-h; order path `oap/orders/024-h-prepare-native-compaction.md`; numeric objective 024
- PR mode: AMENDED_EXISTING_PR

## Status
COMPLETE

## Executive summary
This prep round delivered the private, synthetic, loopback fixture and bounded
observation for the authorized native Codex compaction run, on the unchanged
exact 024-a wheel (SHA-256 verified) and the 024-g private harness lineage.
All three deliverables exist and are verified: (1) the ready-to-run loopback
18031 launcher (`launch-024h.sh`) whose only credential input is the single
suppressed source of the protected reference immediately before `exec` (argv
carries only nonsecret control arguments; the candidate materializes its own
0600 live config from its OWN environment; no gateway; bounded caps 300 main /
10 compiler / 3600 s window, overridable by environment); (2) the synthetic
Git workspace with an `AGENTS.md` referring to two complete small descendant
instruction documents that the genuine shell tool can acquire together in the
one combined read `cat docs/A.md docs/B.md` (one two-member bundle, D05 shape);
and (3) concise executable steps for strategy (in this report and in the
private `steps-024h.txt`). One fast fake-upstream preflight of the installed
candidate and its driver-owned witness PASSED with zero problems: four bounded
requests inside exact caps (4 main / 2 compiler) — root bootstrap with one
compile and the issued combined read, the two-member bundle compile with both
carriers replaced, the byte-identical transformed replay with zero recompile
(`original_present_ram_reuse`), and the source-absent reinjection with zero
compile (`source_absent_injection`) — with clean teardown (PID reaped, 18031
and 18032 connect-refused with no host-wide listener inodes, self leak-scan
clean). The preflight's focused in-process witness check exercised the closed
unified-exec wrapper boundary against the synthetic frame AND the exact
running 0.164.0 worker's native record shape (the observed optional
`Original token count: <integer>` line between `Process exited with code 0`
and `Output:`), plus three refused negatives. Two concrete client-wire
incompatibilities were captured at their exact location (the Responses
`tools` array the client sends, not the adapter): the protected catalog's
exact eligible entry carries `use_responses_lite = true` (the client must use
the standard Responses dialect direct to the adapter) and
`apply_patch_tool_type = "freeform"` (non-null, so Codex 0.164.0 emits a
custom grammar tool that vLLM 0.32.0 rejects — the one-run variant must null
it). No live process or listener remains at round end (verified host-wide).
All live/native checks remain PENDING in this prep round, as the order
requires; no live provider call was made and none is authorized this round.

## Authoritative GitHub state
- Repository `ulfe-lmi/slaif-local-coding`; PR #32 state OPEN
  (https://github.com/ulfe-lmi/slaif-local-coding/pull/32)
- Base `main`; head `oap/024-cache-real-codex-qualification`
- Starting remote SHA `6b31661fdf5e981f6b19453a4fd94d14e690f8aa` (024-g report)
- Implementation head SHA: 3474f322cadc510162dc1641f77146ee38fbd466
- Report publication commit: SELF
- Implementation commits pushed before report: 1 — `3474f32` (activated 024-h
  order and `oap/active` transcript; unchanged strategic bytes, sha256
  `88705c63…`/`b15d90b6…` verified identical in the linked checkout and the
  primary repository before staging)
- New PR this round: no; amended existing: yes; merge performed: NO

## Changes and files
- No tracked software, docs, dependency or test change in this round.
  `git diff --stat 6b31661..3474f32 -- src tests docs scripts packaging
  oap/reports` is empty; the full diff from the prior report head is exactly
  `oap/active` (2 +/-) plus the new 54-line 024-h order file.
- The linked-checkout working tree keeps the operator's local `AGENTS.md`
  wording unstaged, exactly as ordered (it is not part of the transcript).
- Private disposable artifacts only (protected project root
  `work-artifacts/oap-024h-work`, 0700, never committed):
  - `harness/candidate_024h.py`, `harness/driver_024h.py`,
    `harness/fixtures_024h.py` (the 024-g private harness lineage, adapted:
    one candidate role, four-request preflight, closed two-member-bundle
    expectations, and the structural carrier identification below);
  - `harness/run_024h.sh` (synthetic preflight wrapper: exact wheel SHA gate,
    one-time exact-wheel venv, umask 077);
  - `harness/launch-024h.sh` (the ready-to-run live launcher; deliverable 1);
  - `harness/stop-024h.sh` (explicit teardown: stop file, clean-exit wait,
    reap, port-closure verification, content-free summary);
  - `fixture-workspace/` (deliverable 2: synthetic Git repo, commit
    `9409d26`, branch `main`; `AGENTS.md`, `docs/A.md`, `docs/B.md`);
  - `steps-024h.txt` (deliverable 3: concise executable steps, 0600);
  - `captures/run-a01088eb91f339c42869ec64ff0061ad-synthetic/` (the passing
    preflight facts, 0700/0600) and
    `captures/run-c44a8e2fa2c9684503c61a8fb2bfcd29-synthetic/` (the first
    preflight iteration, retained: it exposed the harness closed-form gap
    below, fixed in-harness and never in product code);
  - `venv/` (fresh, noneditable, Python 3.12.15, bound to the exact wheel via
    its `.024h-wheel` marker).

## Acceptance evidence
Private captures are content-free (counts, closed stage outcomes, booleans,
millisecond timings, digests of rendered regions/wrappers; 0700/0600, never
committed) under `work-artifacts/oap-024h-work/captures/`.

### Criterion 1 — Ready-to-run loopback 18031 launcher (no gateway)
- `harness/launch-024h.sh` verifies the exact wheel SHA before anything else,
  refuses when 127.0.0.1:18031 is already bound, creates a fresh 0700
  `run-live-<utcstamp>` directory with its recovery root, emits the live
  config template through `driver_024h.py --emit-template`, then sources the
  protected reference ONCE with output suppressed and `exec`s the candidate
  (`source "$QWEN_REF" >/dev/null 2>&1 || exit 2; exec …`). The candidate
  (reused 024-g mechanism) materializes its own 0600 live config from its OWN
  freshly sourced environment (`QWEN_MODEL`/`QWEN_BASE_URL`) — argv carries
  only nonsecret control arguments — and is ready only after self-scoped
  18031 LISTEN socket-inode ownership is proved before the first `/healthz`.
- Template dry-check (no live call): all 11 expected fields verified —
  `__MODEL__`/`__BASE_URL__`/`__RECOVERY_ROOT__` placeholders present and the
  recovery substitution exact; `profile = "dependency-bundles-v1"`,
  `workers = 1`, `admission_mode = "lean"`, recovery `enabled = true`,
  `context_tokens = 262144`, `model_revision = "017b9c7af6b5689d5dd426a76e0bc077eb5ca20a"`,
  `compatibility_identity = "vllm-0.32.0-qwen38-a100-q8"`, and the
  `route_contracts.text` model/context binding — PASSED.
- Bounded by design: 300 main attempts/forwards, 10 compiler dispatches,
  3600 s window (SeamTransport enforces and records `over_bound`); explicit
  teardown via `stop-024h.sh` (verified mechanism: clean exit 0, PID reaped,
  connect-refused, no listener inodes — measured in the preflight's stop).

### Criterion 2 — Synthetic Git workspace with the combined two-member read
- `fixture-workspace/` is a real Git repository (commit `9409d26`, clean
  status, branch `main`) with root `AGENTS.md` (272 bytes) referring to the
  two complete small descendant instruction documents by backticked relative
  `.md` paths and giving the exact combined shell read
  `cat docs/A.md docs/B.md`; `docs/A.md` and `docs/B.md` are complete,
  self-contained rule documents (no `.md` path-like tokens, so the bundle's
  deterministic candidate list stays empty).
- The preflight proves the shape through the ACTUAL adapter: R1's issued
  function_call arguments carry exactly the combined command
  (`issued_cmd_is_combined_read: true`), and R2 admits and compiles the
  combined output as ONE two-member bundle (D05: plain concatenation, no
  separator, no fabricated per-file hashes) — one compiler dispatch, both
  carriers replaced.

### Criterion 3 — Concise executable steps for strategy
- Private `steps-024h.txt` (0600) and the step summary in the Executive
  summary: launch the adapter → run the authorized client in
  `fixture-workspace` (exact pinned 0.164.0 binary — the same inode as the
  running worker's `/proc/<pid>/exe`, verified by the operator — with
  `--profile early-beta`, `--sandbox read-only`, CLI-only provider/catalog
  overrides, standard Responses dialect direct to `127.0.0.1:18031/v1`, no
  gateway, no separate client home) → close the client → `stop-024h.sh` →
  read the content-free facts. The client command itself remains
  operator-owned per the round's fixture-configuration addendum.

### Criterion 4 — One fast fake-upstream preflight (installed candidate + witness)
- Passing run `a01088eb91f339c42869ec64ff0061ad` (driver exit 0, `PASS`,
  zero problems): candidate ready via self-proved listener ownership;
  four requests, all 200, inside exact caps (4 main / 2 compiler;
  `over_bound: false`):
  - R1 bootstrap: 1 main forward, 1 compiler dispatch (root), 1 compiled
    block, 1 live marker, raw root body absent from the root carrier
    (`root_wrapper_preserved: true`, workspace label `preflight`), recovery
    `cold` → `retained`, generation 2; the model issued the combined read.
  - R2 combined read: 1 main forward, 1 compiler dispatch (two-member
    bundle), 2 compiled blocks, 2 live markers, raw A/B bodies absent from
    the dependency carrier — identified STRUCTURALLY (paired exec_command
    call plus the closed unified-exec wrapper boundary;
    `dep_v1_carrier_wrapper_matched: true`, `dep_v1_carrier_shape_exact:
    true`, synthetic-frame diagnostic `true`), tool-call/result pairing and
    wrapper preservation exact, recovery `published`, generation 3.
  - R3 transformed replay (same original payload): 0 compiler dispatches,
    byte-identical rendered region digests vs R2 (`blocks_match_prev: true`),
    reuse class `original_present_ram_reuse` — the byte-identical
    fixed point with zero recompile.
  - R4 source-absent (continue-only payload, no source carriers): 0 compiler
    dispatches, 2 compiled blocks reinjected in the stable placement region,
    reuse class `source_absent_injection` — the post-native-compaction shape
    (R05 mechanism) inside the live session.
- Teardown: candidate exit 0, PID reaped, 18031 connect-refused with no
  host-wide listener inodes; the driver-owned fake peer (18032) likewise
  closed; candidate self leak-scan clean (stderr log removed).
- Focused witness check (in-process, no request): the closed wrapper
  boundary accepts the synthetic frame AND the native 0.164.0 record shape
  with and without the observed optional `Original token count: <integer>`
  line, and refuses three negatives (missing `Output:` line, missing
  `Wall time:` line, garbled token count) — all six booleans `true`.
- First preflight iteration (`c44a8e2f…`, retained): FAILED with exactly two
  closed-form problems — the no-carrier branch of the private carrier
  identifier left `dep_v1_carrier_wrapper_matched` `None` instead of the
  closed `False` (R1 and R4 expectations). Fixed in the private harness only
  (the else-branch now emits the closed `False`); product code untouched;
  the second run PASSED.
- The 024-h candidate's carrier identification (needed for the real
  combined-read and R04 evidence) was adapted for this round: the root
  carrier matches the known workspace set (the preflight `/work` root and the
  live fixture workspace absolute path, recorded as the closed labels
  `preflight`/`live-fixture`, never the path), byte-identical repeated root
  envelopes deduplicate per the root law, and the real tool output is
  identified by its paired exec_command call plus the closed wrapper/Output
  boundary (wrapper digest + live marker recorded in that exact source
  region); arbitrary fixture-substring matches stay diagnostic only.

### Criterion 5 — Concrete incompatibilities, captured at their exact location
- Location: the Responses request `tools` array the CLIENT sends to the
  adapter (client-wire schema, not adapter code):
  1. `apply_patch_tool_type` — the protected catalog's exact eligible entry
     `qwen3.8-27b` (`~/.codex/early-beta-models.json`) carries
     `apply_patch_tool_type = "freeform"` (non-null). Codex 0.164.0 emits a
     custom grammar tool whenever that field is non-null, and the serving
     vLLM 0.32.0 Responses validator rejects every custom grammar tool. The
     read-only tool list therefore does NOT omit apply_patch; the one-run
     client variant must set `apply_patch_tool_type = null` (the operator
     owns that variant).
  2. `use_responses_lite` — the same exact eligible entry carries
     `use_responses_lite = true`; per the order the client-local override
     uses the standard Responses dialect direct to vLLM, i.e. the
     disposable catalog derived from the exact eligible model entry changes
     ONLY the dialect. (Strategy's own disposable catalog already exists as
     `oap-024h-work/strategy-client/models.json`; this round did not create
     or inspect it.)
- No adapter-side incompatibility was exposed by the preflight; the expected
  provider/launch settings (profile, workers, admission, C, model
  revision/compatibility identity, recovery, route contract) all verified.

### Criterion 6 — No live process or listener at round end
- After the preflight: 18031 and 18032 connect-refused, no listener inodes
  host-wide (verified in the run facts and re-verified independently after
  the run). The live launcher has not been executed this round; it is
  ready-to-run only.

## Verification
- `bash harness/run_024h.sh` (synthetic preflight, second/final iteration):
  PASSED — driver exit 0, `outcome: PASS`, `round_problems: []`, exact caps
  (4/4 main, 2/2 compiler), clean stop facts, peer closed.
- `bash harness/run_024h.sh` (first iteration, retained): FAILED with exactly
  `r1-carrier-dep_v1_carrier_wrapper_matched;
  r4-carrier-dep_v1_carrier_wrapper_matched` (the closed-form harness gap,
  fixed in-harness; see Criterion 4).
- Template dry-check (`driver_024h.py --emit-template` + recovery
  substitution): PASSED — 11/11 expected fields.
- Wrapper witness check (in-process): PASSED — 6/6 booleans.
- `git diff --stat 6b31661..3474f32 -- src tests docs scripts packaging
  oap/reports`: empty (no tracked product change).
- Transcript byte verification: `sha256sum` of `oap/active`
  (`88705c63…`) and the 024-h order (`b15d90b6…`) identical in the linked
  checkout and the primary repository; staged diff exactly those two paths.
- `git push` of the transcript: remote branch head and PR #32 head both
  `3474f322cadc510162dc1641f77146ee38fbd466` (verified via `git ls-remote`
  and `gh pr view`).

## Live model/service evidence
- NONE this round, by order: all live/native checks remain PENDING in this
  prep round. No live provider call was made; the preflight used only the
  driver-owned fake peer with a synthetic placeholder credential
  (source-free synthetic branch — the protected reference was never sourced
  in the preflight). The protected service, its units, ports and credentials
  were untouched; no client was launched; no second live listener was
  started.

## GitHub CI / required checks
- Implementation-head check states - all ten checks observed for
  `3474f322cadc510162dc1641f77146ee38fbd466` (PR #32 head at drafting):

  | Check | Status |
  | --- | --- |
  | `Analyze (actions)` | pass |
  | `Analyze (python)` | pass |
  | `CodeQL` | pass |
  | `cache-native-containment` | pass |
  | `cache-native-fixture` | pass |
  | `docker` | pass |
  | `docker-published` | pass |
  | `gateway-contract` | pass |
  | `operator-session` | pass |
  | `test` | pass |

- All required green at drafting: yes (10/10; observed via `gh pr checks 32`
  in the linked checkout after the implementation push, `test`
  18m13s)
- Report-head checks may be pending; strategy verifies.

## Local setup/dependencies
- Fresh private venv `work-artifacts/oap-024h-work/venv` (Python 3.12.15,
  exact noneditable 024-a wheel
  `slaif_local_coding-0.1.0-py3-none-any.whl`, SHA-256
  `e82f5ab8b7fa7833e7fbb5734c7612f81f149d2e6a4aae1e53275004437536d3`,
  marker-bound); the 024-g venv was NOT modified. No sudo, no service
  changes, no global configuration changes. The worker's Codex
  configuration files are untouched (the temporary client uses CLI-only
  overrides and the existing client home, operator-owned).

## Documentation
- Not required: no tracked behavior, configuration, security, test or
  operation change in this round (transcript-only commit). The 024
  handoff/ledger state is unchanged by this prep round; the native-compaction
  stage remains unearned until the authorized client run is reviewed.

## Safety/scope confirmations
- Unrelated files preserved; the operator's local `AGENTS.md` wording stays
  unstaged in the linked checkout.
- No secrets or raw content committed, printed or retained: the protected
  reference was never inspected, read separately, printed or committed (the
  preflight is source-free; the launcher sources it once, suppressed, inside
  the adapter launch only); captures are content-free by construction with a
  candidate-side self leak-scan (clean, log removed); no private URLs,
  credentials or source text appear in this report.
- Production/protected resources untouched: port 18020, `qwen-serving`,
  model/checkpoint files, API-key files, firewall/VPN, and both OAP agents'
  Codex profiles/profile paths — NO change.
- Extra objective PR: NO. Coding merge: NO. Active/order edited: NO
  (strategic bytes committed unchanged, hash-verified). Report commit
  report-only: yes.
- No Codex process launched, no own-process suspension, no second client or
  live listener, no benchmark, no release.

## Known limitations/blockers
- All genuine checks remain PENDING by design: the real-model, genuine-client
  and genuine-compaction criteria (including R04 native-compaction root
  presence and the full 024 handoff) are earned only by the authorized
  strategy-owned client run after this round's response, using the
  deliverables above. The preflight proves the adapter-side mechanisms
  (combined-read acquisition, two-member bundle compile, carrier
  replacement, byte-identical replay, source-absent reinjection, wrapper
  boundary against the real 0.164.0 record shape) but never substitutes for
  the genuine run.
- The one-run client variant must null `apply_patch_tool_type` (vLLM 0.32.0
  custom-grammar rejection) — outside this round's scope, operator-owned.

## Recommended strategic follow-up
Factual only: (1) after review, arm the next control reader and run the
authorized client per `steps-024h.txt` (exact pinned 0.164.0 binary,
`--profile early-beta`, `--sandbox read-only`, standard Responses dialect,
`apply_patch_tool_type = null` variant, workdir `fixture-workspace`);
(2) close the client, then `stop-024h.sh`; (3) correlate the content-free
per-request facts with the native rollout (R04: root still present after
compaction with the cached hit/replacement — never a lost-root recovery;
R05: source-absent reinjection); (4) review the published 024-h report and
decide the next suffix.

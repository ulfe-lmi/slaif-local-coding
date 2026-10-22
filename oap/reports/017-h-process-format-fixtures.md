# OAP Coding-Agent Report — 017-h

## Work order
- Order: `oap/orders/017-h-process-format-fixtures.md`
  (objective 017, round 017-h, AMEND_EXISTING_PR); committed
  unchanged with implementation commit A (SHA256
  `208ea9f3832adb53227b7ac855112d7797c21b129b04e3a35b44ebe816258e4c`).
- `oap/active` = `017-h` (bytes `017-h\n`, SHA256
  `82292c5e4da42f3ad1460412babc4c7759d3c86388a1d3cba10a0a8584aa3733`);
  committed unchanged with A (activation bytes preserved, not edited).
- PR mode: AMENDED_EXISTING_PR — exact OPEN PR #25
  https://github.com/ulfe-lmi/slaif-local-coding/pull/25, base `main`,
  head branch `oap/017-cache-read-observation`. NO NEW PR; no coding
  merge or auto-merge.
- Starting remote PR/report head verified before mutation:
  `4dfb8d60f87ce454cfa9951b2dfa1eb7a3b75e59` (sole parent
  `b493ec985c3b11d4089399f7f734d7c539587e3c`); remote `main`
  `96c790423f6f0097a56a0b12bacda8a9b6da6aba` (unchanged); working
  tree clean at round start except the activated 017-h order (new
  untracked file) and `oap/active` (017-g -> 017-h), both committed
  unchanged in A.
- Interruption and recovery: the round's original control `OK` was
  consumed by the wrapper before the first worker ran. Strategy
  interrupted that worker after independently inspecting
  `/home/janezp/.local/share/slaif-017h-exp1/work/probe3b.py`. This
  closeout resumed from `oap/active` only: it did not reread control,
  create another order, edit active/order bytes, choose a new suffix,
  perform any further client/capture attempt or fake-provider
  experiment, or reset the capture-attempt counter.

## Status
PARTIAL — interrupted round, truthful bounded-failure publication.
No 017-h deliverable (repo-owned capture utility, fixtures, tests, or
doc updates) exists in this round or in the repository; the
interrupted worker's only output was an out-of-repo prototype
environment that violated the order's explicit capture-persistence
boundary and was destroyed by this closeout after provenance
verification. D09 multi-chunk acquisition remains NOT RUN.

## Executive summary
1. The interrupted worker did not implement the order's
   repository-owned opt-in capture utility. Instead it built an
   ad-hoc prototype under
   `/home/janezp/.local/share/slaif-017h-exp1` (child-only synthetic
   `CODEX_HOME`, synthetic `HOME`, synthetic workspace, in-thread
   loopback fake Responses server) and ran the genuine installed
   client (`codex-cli 0.162.1`) against it in at least five numbered
   attempts (outputs `run1`, `run3`, `run4`, `run5`, `run6`; two
   source variants share the attempt-4 outputs).
2. Every surviving probe source persists what the order's clause 7
   forbids: the complete inbound provider request bodies
   (`requests3-6.bin`, 55,441–111,385 bytes each) and the raw child
   stdout/stderr (`run*.jsonl`/`run*.err`), plus further full
   request/JSON captures (`models.json` 658,607 bytes;
   `cat_default.json`/`cat_local.json`/`cat_shell_command.json`,
   ~661,319 bytes each). The isolated synthetic setup nevertheless
   violated the stricter explicit capture-persistence boundary. The
   at-most-three capture-attempt budget was consumed (numbered
   outputs 1, 3, 4, 5, 6) and cannot be treated as fresh on restart.
3. This closeout: verified no surviving owned experimental
   child/server process (none existed to kill); verified ownership,
   no-symlink, no-special-file, same-device, round-window, and
   no-open-fd properties of the exact scratch root; removed it with a
   narrowly validated Python cleanup (7,980 entries, 90,080,795
   bytes); committed the exact activated order and `oap/active`
   unchanged to PR #25; made no product source change (hence no new
   source-A/build-manifest cycle and no identical rebuild); published
   this report.
4. No real customer-secret exposure is established by the evidence
   known in this closeout, and its absence is not claimed: the
   captured content was destroyed without inspection by design, and
   no parent credential/config/history file was read or copied
   (parent `auth.json` mtime 2026-10-13 and `config.toml` mtime
   2026-10-18, both pre-round and unchanged).

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`; PR #25
  https://github.com/ulfe-lmi/slaif-local-coding/pull/25 (OPEN,
  mergeable, no auto-merge).
- Base `main` `96c790423f6f0097a56a0b12bacda8a9b6da6aba` (unchanged);
  starting remote head `4dfb8d60f87ce454cfa9951b2dfa1eb7a3b75e59`.
- Implementation head SHA: 9a4df0eeca872e4b629575562ea50cfd2ff8d58f
- Report publication commit: SELF
- Implementation commits pushed before report:
  - A `9a4df0eeca872e4b629575562ea50cfd2ff8d58f` — exact activated
    order plus `oap/active` (2 files; sole parent `4dfb8d6…`).
    Transcript-only by deliberate choice: product source/input bytes
    are unchanged, so no new source-A/manifest cycle was fabricated
    and no identical rebuild was performed.
- New PR this round: no; amended existing PR #25: yes; merge
  performed: NO; auto-merge: none.

## Changes and files
- A: `oap/orders/017-h-process-format-fixtures.md` (new; exact
  strategic activation bytes) and `oap/active` (`017-g` -> `017-h`).
  Nothing else.
- No H source implementation, capture utility, test, fixture,
  contract/doc, or provenance-manifest change exists in this round.

## Attempted vs completed evidence (prototype, out of repository)
All facts below come from file metadata (counts/bytes/permissions/
mtimes) and prototype SOURCE inspection only. No captured request,
stderr, JSONL, log, or other raw content file was read, printed, or
persisted by this closeout.
- Environment (created 2026-10-21 00:20:43Z–00:30Z, after 00:13:12Z
  order activation; prototype activity ended by 00:30Z; strategic
  interruption preceded this closeout worker, which started
  00:32:24Z):
  - root `slaif-017h-exp1` 0700; `child-home` 0700 (child-only
    `CODEX_HOME`: fake-provider `config.toml` 0600, 167 bytes;
    Codex runtime sqlite DBs/WALs, skills, and a plugins git clone
    with a ~25 MiB pack — a client-side sync side effect, contained
    in the child home); `home2` 0700 (child `HOME`, empty);
    `work` 0700 (prototype sources and captures); `ws` 0700
    (synthetic workspace containing only `A.md`, 16 bytes — the
    order's B/empty/bounded-large files and minimal synthetic
    `AGENTS` were not present in `ws/`).
  - child environment per surviving sources: minimal `PATH` only,
    `HOME`/`XDG_*` pointing into the child tree, `CODEX_HOME`
    `child-home`, no inherited credentials/provider/SQLite overrides
    or startup hooks; fake server bound to `127.0.0.1` with an
    OS-assigned ephemeral port (bind port 0), never 18020/18031.
- Client binary (live-verified this closeout): absolute release
  binary
  `/home/janezp/.codex/packages/standalone/releases/0.162.1-x86_64-unknown-linux-musl/bin/codex`,
  `codex-cli 0.162.1`, live SHA256
  `628e35487d888a28f0427fc37501da529dd3d81fcbad7a2c3421c1e8670d92e1`
  (matches the order's recorded value). Package resource untouched
  (read-only hash/version checks only).
- Attempt variants (source inspected; content never read):
  `fake_probe.py` (in-thread fake Responses server: `/v1/models`
  stub; `/v1/responses` SSE controller selecting the predeclared
  harmless synthetic `cat A.md` operation), `run_probe.py`
  (runner; its attempt-2 outputs `requests2.bin`/`probe2.log` are
  absent from the final tree), `probe1.py` (attempt 3:
  `requests3.bin` 55,441 B, `events3.log` 216 B, `step.log` 786 B,
  `run3.jsonl` 344 B, `run3.err` 0 B), `probe1b.py` and
  `probe2v.py` (two source variants of the attempt-4 outputs:
  `requests4.bin` 55,441 B, `events4.log` 216 B, `step4.log` 786 B,
  `run4.jsonl` 344 B, `run4.err` 0 B), `probe3.py` (attempt 5:
  `requests5.bin` 111,219 B, `step5.log` 729 B, `run5.jsonl` 711 B,
  `run5.err` 0 B; `CALL_MODE` env selecting `custom_tool_call` or
  `function_call`), `probe3b.py` (attempt 6: `requests6.bin`
  111,385 B, `step6.log` 729 B, `run6.jsonl` 711 B, `run6.err` 0 B;
  same `CALL_MODE` env). Plus `run1.err` 30 B / `run1.jsonl` 0 B
  (attempt 1; its source script does not survive in the tree),
  `models.json` 658,607 B, and the three ~661,319-byte
  `cat_{default,local,shell_command}.json` captures.
  Numbered attempt outputs 1, 3, 4, 5, 6 therefore evidence at least
  five client launches.
- Child invocation shape (from prototype source):
  `codex exec --ephemeral -s danger-full-access --json
  --skip-git-repo-check -C ws -m gpt-6-astra -` with the prompt on
  stdin, `cwd=ws`; inspected attempt-5/6 sources bounded the child at
  60 s with a kill fallback. The fake controller's first response
  offered a `custom_tool_call` (name `exec`, JS input calling
  `tools.exec_command`) or, in the other mode, a `function_call`
  variant; the second response ended with a final assistant message.
  No surviving record shows whether the client honored those items.

## Bounds/persistence deviations (interrupted worker)
- Clause 7 requires persisting ONLY allowlisted selected synthetic
  call/result items plus sanitized provenance, and forbids dumping/
  logging/saving full requests, headers, system/developer prompts,
  histories, or unknown stderr. All surviving probe variants instead
  wrote every inbound provider request body in full to disk and the
  child's raw stdout/stderr in full to disk (files listed above);
  `step*.log` (216–786 B) are debug logs whose content was not
  inspected in this closeout.
- The prototypes' inbound read caps (4,000,000 bytes in
  `probe1.py`/`probe3*.py`; 2,000,000 in `fake_probe.py`) exceed the
  order's 1 MiB per-inbound-request bound.
- The at-most-three-attempt total budget was consumed by the unsafe
  variants (numbered outputs 1, 3, 4, 5, 6); it is not fresh.
- No other protected resource was touched by the prototype: child-
  only configuration, ephemeral loopback port, no 18020/18031, no
  parent auth/config/profile/history access (parent `auth.json`
  2026-10-13 and `config.toml` 2026-10-18 mtimes, unchanged; the
  only post-round-start parent `CODEX_HOME` changes are this live
  closeout session's own thread locks, sqlite WALs, shell snapshot,
  and history activity).

## Exact safe cleanup evidence
- Pre-cleanup verification (narrowly validated Python, lstat-based,
  no content read):
  - root is a real directory, not a symlink; `realpath` identity;
    parent `/home/janezp/.local/share` is a real directory; root on
    the same device as its parent (not a mount point); owner uid
    1001 == executing uid.
  - all 7,980 entries (5,547 files + 2,433 directories) are regular
    files/directories only: no symlinks, no sockets/FIFOs/devices,
    no foreign uid, no cross-device entries; every mtime inside the
    round window (minimum 2026-10-21T00:20:43Z >= 00:13:12Z
    activation) proving round-created provenance.
  - no surviving owned experimental child or server process:
    `/proc` cmdline/cwd/exe scan matched only this worker session;
    full `/proc/*/fd` inode scan found no live process holding any
    file of the tree.
  - no other round-created scratch root exists under `/tmp`,
    `/var/tmp`, `~/.local/share`, `~/.cache`, or `~/.local/state`.
- Pre-deletion manifest: sorted (relpath, type, mode, size)
  serialization, SHA256
  `a8733f76142aad4a6da466e903001ee417873040a79b758cb7c0e1b00d618d11`;
  total bytes 90,080,795.
- Deletion: narrowly validated Python bottom-up `unlink`/`rmdir`
  with per-entry re-assertion (regular type, uid, device), root
  removed last: 5,547 files + 2,433 directories removed.
- Post-cleanup verification: root absent (not even as a symlink);
  parent inode/uid/mode unchanged; pre-existing siblings
  (`slaif-tls`, `slaif-eval`, `slaif-eval-admin-password`,
  `slaif-admin-password`) untouched.
- No raw log, request, or capture was copied into the repository,
  this report, the strategic workspace, or any new archive. No
  `rm -rf`-style broad shell command was used (the earlier rejected
  rm-rf was never executed).

## Unsupported tool-mode/format facts known without raw logs
- Live-verified from the actual 0.162.1 binary (`--help`/
  `--version`, read-only): supported flags include `--ephemeral`
  ("run without persisting session files to disk"),
  `--skip-git-repo-check`, `--ignore-user-config` (help text: auth
  still uses `CODEX_HOME` — consistent with the order's caveat that
  it alone does not isolate auth), `--ignore-rules`, `--json`
  ("print events to stdout as JSONL"), `-s
  {read-only,workspace-write,danger-full-access}`, `-C`, `-m`, `-c`,
  `--profile`, `--worktree`, `--add-dir`, `--oss`,
  `--local-provider`, `--output-schema`, `-o`, `--thread-source`,
  `--strict-config`, `--enable`/`--disable`. No surviving record of
  the interrupted worker's own pre-launch capability verification
  exists; these are the closeout's live-verified facts.
- What the client actually offered/accepted as tool-call shape
  (`custom_tool_call` vs `function_call`), and how it formats
  `exec_command`/`write_stdin` results (process/session ID fields,
  chunk fields, wrapper order, truncation markers, running-to-
  completion facts) REMAINS UNVERIFIED: the frames that could prove
  it were the raw captures destroyed above, and this closeout claims
  no format fact from them and invents no wrapper syntax.
- Size-only facts: child stdout was non-empty in some attempts
  (`run5.jsonl`/`run6.jsonl` 711 B each; `run3.jsonl`/`run4.jsonl`
  344 B each; `run1.jsonl` 0 B); `run1.err` 30 B. No content claim.

## Acceptance evidence
### Criterion 1 — genuine selected frames for the four named cases
(normal exit-0 file output; running initial result with
process/session ID plus write_stdin poll(s) to completion; zero-byte
successful output; deliberate bounded truncation), with an actual
running-to-completion sequence
- Result: NOT ACHIEVED (NOT RUN). No allowlisted selected frames
  were ever persisted; no fixture exists in the repository.
### Criterion 2 — repo-owned explicit opt-in capture utility,
offline fixture/collector tests, fixture contract docs, observer
source untouched
- Result: NOT ACHIEVED (NOT RUN). No utility, tests, fixtures, or
  doc updates exist; observer source unchanged.
### Criterion 3 — honest bounded failure is PARTIAL/BLOCKED, not
invented wrappers
- Result: achieved by this report (PARTIAL); no wrapper/format
  invented.

## Verification
(all non-root; skipped/missing/not-run reported as such)
- GitHub reconciliation (PR #25 OPEN/mergeable, base/head, all 8
  checks SUCCESS at starting head `4dfb8d6…`): PASSED.
- Invariance of order/active/prior OAP/frozen docs/source: PASSED —
  `docs/CACHE-REWORK.md` SHA256
  `410df5c0b8f90b05220adc32c8e673b143c0cf1fa3da02270d91ac453c886abd`
  (unchanged); `docs/CACHE-IMPLEMENTATION-PLAN.md` unchanged;
  `packaging/releases/` and frozen RC10 records untouched;
  `ARCHITECTURE-for-agents.md` compact mirror byte-identical
  (`cmp`); on-disk 017-g report == committed bytes == order-
  recorded SHA256
  `d3343809424df6ecee00d4481fe3a09390b2a9c53b88b31c1dd3b48cb6459e86`;
  all prior orders/reports byte-unchanged (`git status` clean apart
  from the activated transcript); product source tree identical to
  the `4dfb8d6…` state (no diff outside the two transcript paths).
- Client binary live verification (absolute path, version, SHA256):
  PASSED.
- Parent/protected state scan (round-window mtime scan of parent
  `CODEX_HOME`, `auth.json`/`config.toml` mtimes, loopback listener
  list, qwen-serving unit presence on this relocated host): PASSED
  (no round-attributable change; see Live section).
- Process scan (no surviving owned experimental child/server):
  PASSED (nothing to kill or reap).
- Pre-cleanup verification + narrowly validated deletion +
  post-cleanup verification: PASSED (exact counts/manifest above).
- Privacy/credential/raw-log scan of the round diff: PASSED — the
  only port/address hits are the order's own governance text
  committed verbatim; no secrets, keys, bearer material, or raw
  captured content in the diff or this report.
- `git diff --check 4dfb8d6…..HEAD`: PASSED.
- The TESTING local gate, all 11 exact commands (`uv lock --check`;
  `uv sync --frozen --extra dev`; `uv run --frozen ruff check .`;
  `uv run --frozen ruff format --check .`; `uv run --frozen mypy src
  tests`; `uv run --frozen python scripts/docs_consistency_check.py`;
  `uv run --frozen pytest -q`; `uv build`; `scripts/
  artifact_policy_check.py --dist dist --inspect`; `--install-smoke`;
  `scripts/dev_provenance_manifest.py --verify --dist dist`;
  `python -m compileall -q src tests oap/bin scripts`): NOT RUN —
  no product source changed this round (source bytes identical to
  the `4dfb8d6…` state whose CI is green); running the gate would
  verify no H work and would not substitute for any H criterion.
- Focused fixture/collector tests: NOT RUN (no fixture/collector
  exists).
- `bash -n` over affected shell scripts: NOT RUN (no shell script
  changed).
- The seven frozen strategic observer probes: NOT RUN (observer
  source unchanged from `4dfb8d6…`, where all seven passed at
  `b493ec9…` per the immutable G report; rerunning them adds no new
  fact to this round).
- All H capture/collector/client commands: NOT RUN (explicitly not
  authorized in this closeout).

## Live model/service evidence
- No live inference, no bounded live calls, no Gateway calls, no
  GPU/product-adapter request. The protected `qwen-serving` user
  unit and vLLM 18020/18031 listeners do not exist on this relocated
  host (verified before and after the round: no unit, no listener);
  the canonical protected fixture is elsewhere and untouched.
  Protected fixture changed: NO.

## GitHub CI / required checks
- Implementation head `9a4df0eeca872e4b629575562ea50cfd2ff8d58f`:
  all 8 required checks SUCCESS — `test`, `docker`,
  `docker-published`, `gateway-contract`, `operator-session`,
  `CodeQL`, `Analyze (python)`, `Analyze (actions)`.
- All required green at drafting: yes.
- Report-head checks may be pending on the report-only push;
  strategy verifies.

## Local setup/dependencies
- Repo-local `.venv` unchanged; no new dependencies; no sudo used;
  no shared host or global permission changes; no repo-local service
  started or stopped (no owned experimental process survived to
  stop).

## Documentation
- Not updated this round: no behavior, configuration, security,
  test, operation, or limitation change was committed; the H-scope
  doc updates (observation contract, TESTING, stage ledger, both
  architecture maps plus compact mirror, PR body) belong to the
  unperformed implementation scope and remain for the corrective
  suffix.

## Safety/scope confirmations
- Unrelated files: none touched; A touches exactly the two
  transcript paths; working tree clean at report time.
- Secrets/raw content: none in diff or report; captured raw content
  destroyed in place after provenance verification and never read,
  printed, or copied by this closeout.
- Production/protected resources: none.
- Protected 18020/Qwen/Codex fixture changed: NO.
- Required tests skipped/not run: all H-scope verification NOT RUN
  (see Verification); no legacy suite skipped in lieu of H work.
- Scope deviations of the interrupted worker: capture-persistence
  boundary violation, 1 MiB inbound-cap exceedance, attempt-budget
  exhaustion (documented above, not repeated here).
- Extra objective PR: NO; coding merge: NO; auto-merge: NO.
- Active/order edited: NO (exact activation bytes committed);
  report commit report-only: yes (to be verified on push).

## Known limitations/blockers
- No H deliverable exists: no capture utility, no fixtures, no
  offline tests, no fixture contract docs; D09 multi-chunk
  acquisition and D10 remain NOT RUN/planned.
- Genuine tool-mode/format facts remain unverified (see
  Unsupported tool-mode/format facts); any next capture requires the
  compliant repo-owned collector.
- The at-most-three capture-attempt budget is not fresh; any
  re-attempt requires a new explicit strategic order.
- The interrupted worker's pre-launch capability-verification step
  left no surviving record; only this closeout's live `--help`/
  `--version`/SHA256 facts are recorded.

## Recommended strategic follow-up
Factual only: strategy alone decides the next same-PR corrective
suffix. A compliant next round would first land the repo-owned
explicit opt-in collector with allowlisted-frame-only persistence
and offline tests, then perform bounded capture under a freshly
authorized budget; the D09 process/chunk association and D10 branch
matrix remain planned.

## Implementation head SHA: 9a4df0eeca872e4b629575562ea50cfd2ff8d58f

## Report publication commit: SELF

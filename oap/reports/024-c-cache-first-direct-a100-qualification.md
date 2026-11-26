# OAP Coding-Agent Report — 024-c

## Work order
- Identifier: 024-c; order path `oap/orders/024-c-cache-first-direct-a100-qualification.md` (sha256 `bf6eb7ea4032288ea4a2258a932920e3d1bc4d41e430bc5b37766952a531c87e`, committed byte-identical from the primary); numeric objective 024
- PR mode: AMENDED_EXISTING_PR (PR #32, branch `oap/024-cache-real-codex-qualification`)

## Status
PARTIAL

## Executive summary
The first live round of objective 024 ran on the owner-authorized private raw vLLM
service (the operator-declared A100 Q8 serving of `qwen3.8-27b`, checkpoint
`Qwen/Qwen3.8-27B-FP8` at commit `017b9c7af6b5689d5dd426a76e0bc077eb5ca20a`, used
as the exact declared compiler `model_revision`; the separately pinned repository
tokenizer/render revision stayed unchanged). Section 1 (direct endpoint smoke)
completed in full: three metadata GETs, one tool-free nonstreaming Chat
Completions call with the production compiler envelope fields, and two streaming
stateless Responses calls — all 200, all within the ordered caps, with the real
model genuinely issuing the declared `exec_command` fixture read in the first
streaming call. Section 2 (installed-wheel v1 candidate) ran the exact 024-a
clean-built wheel noneditable on Python 3.12.15 on private `127.0.0.1:18031`,
bound directly to the sourced service (no relay), with v1 enabled at
C=262144, the pinned tokenizer and the declared serving compatibility
(`vllm-0.32.0-qwen38-a100-q8`, revision `017b9c7a…`). The driver drove the ordered
four-main-request sequence through the candidate loopback (cap consumed; no
further authorized candidate invocation was made); the protected recovery store
retains three committed v1 transactions (durable generations 1→2→3), the root
fact retained with authority under the bootstrap envelope provenance, two
trusted issuance facts, and zero read occurrences (no file was ever admitted),
and the committed transactions bound the compiler work to the single unchanged
root entry (one compile per unchanged entry per epoch).
The per-round stage counters and the actual outbound bodies are not retained in
this direct-binding topology, so no exact compiler dispatch count, per-round
recompile statement or wire reinjection statement is made from the recovery
records alone. The real-model
dependency-acquisition half is NOT RUN: a pre-run defect in the private harness
stripped the retained issued call from the r1 record before the acquisition
branch extracted it, so no acquisition payload was ever sent even though the
model's genuine issuance was observable; the four-main-call cap is now consumed,
so the unconsumed acquisition case cannot run within the existing candidate and
total ceilings, and no further authorized candidate invocation was made. A
second pre-run driver defect (a raw tuple-keyed metrics snapshot in the facts
payload) made the final facts JSON serialization raise `TypeError`, so the
per-round typed outcomes were not retained; the original partial facts file is
preserved byte-identical and the content-free recovery evidence (recovery store,
lifecycle facts, caps determination) is retained under the private 024c work
directory. Both defects are corrected in the private harness bytes (never
committed). Genuine client, native compaction, image, recovery/restart acceptance
and overhead remain pending for later 024 rounds, as ordered.

## Authoritative GitHub state
- Repository: `ulfe-lmi/slaif-local-coding`; PR #32 open, base `main`, head branch `oap/024-cache-real-codex-qualification`, mergeable
- Base: `main` at `fe9538452f7715c305ea2ae9da60726cb73d8d45`; starting remote SHA `de72c87cc3f089f4fb9df7fcdd9c5ed46e9dfcb1` (accepted 024-b report head, ten checks green)
- Implementation head SHA: 7b22b877e1c3dd7eae56e0d6045f7f3d85e69314
- Report publication commit: SELF
- Implementation commits pushed before report: one — `7b22b87` (the exact unchanged activated order plus `oap/active`; transcript-only, byte-verified from the primary)
- New PR this round: NO; amended existing PR #32: YES; merge performed: NO

## Changes and files
- `oap/orders/024-c-cache-first-direct-a100-qualification.md` (new, exact strategic bytes)
- `oap/active` (`024-b` → `024-c`, exact strategic bytes)
- No product, dependency, docs or test changes (the order forbids them absent a separate order; the live harness material is private and never committed).

## Acceptance evidence

### Criterion 1 — direct endpoint smoke (order section 1)
PASSED (content-free facts `024c-direct-smoke-facts.json`, 0600):
- `GET /health`: 200 (metadata GET 1/3)
- `GET /version`: 200, `vllm_version` `0.32.0` (metadata GET 2/3)
- `GET /v1/models`: 200, `model_count` 1, `declared_model_listed` true (metadata GET 3/3)
- Chat Completions with the production compiler envelope fields (two messages, `reasoning_effort` low, `temperature` 0, `max_tokens` 256 ≤ 512, `stream` false): 200, `finish_reason` `stop`, response parsed as a JSON object, `echo_matches` true, usage 89/77/166 (prompt/completion/total)
- Streaming stateless Responses call 1 (declared `exec_command` function tool, `store` false, `max_output_tokens` 1024): 200, terminal event `response.completed`, one `function_call` item; closed usability booleans at the application boundary: `name_matches_exec_command` true, `arguments_parse_object` true, `has_cmd_key` true, `call_id_present` true, `cmd_is_fixture_read` true (the real model issued the fixture read), output 68 tokens
- Streaming stateless Responses call 2 (the issued call plus its fixed declared synthetic result, no emitted command executed): 200, terminal event `response.completed`, one message item, output 61 tokens
- Caps: 3/3 metadata GETs, 2/2 Responses calls, 22,014 raw-phase response bytes (≤ 256 KiB), zero deadline hits, no redirects, no proxy environment, no retry loop.
- No genuine-Codex-dialect qualification is inferred from this smoke, as ordered.

### Criterion 2 — installed-wheel v1 candidate (order section 2)
PARTIAL (content-free facts `024c-candidate-v1-recovered-facts.json` plus the preserved partial driver facts, 0600):
- Exact wheel: sha256 `e82f5ab8b7fa7833e7fbb5734c7612f81f149d2e6a4aae1e53275004437536d3` verified before use; fresh noneditable venv (Python 3.12.15) from that wheel only
- Private `127.0.0.1:18031`: pre-launch port-free check, child-scoped LISTEN socket-inode ownership proof before the first readiness HTTP, clean shutdown, post-stop port refusal verified, candidate process absent after the run, run lock released
- Direct binding to the sourced service (no relay); the service bearer entered only through the candidate's protected private upstream environment reference (environment NAME in the config; the value only in the child's minimal environment); the operator-declared checkpoint revision `017b9c7a…` as the declared compiler `model_revision`; compatibility identity `vllm-0.32.0-qwen38-a100-q8`; v1 enabled with C=262144 and the pinned tokenizer; fresh developer-only foreground config and protected state (0700/0600)
- Main requests: the driver drove all four main requests of its sequence through the candidate loopback (the ordered cap, consumed; no further authorized candidate invocation made after the run): bootstrap, source-absent, bootstrap resend (replay), source-absent — retained driver control-flow fact: the run reached its final step with no fatal recorded and zero deadline hits; the durable committed-transaction record is the three transactions below, two of which each evidence a completed main forward, while the bootstrap forward outcome and the fourth request's disposition are not retained
- Committed v1 transactions (durable evidence, recovery store): 3 — generations 1→2→3, revisions 1→2→3, prior epoch 1, never quarantined; the pointer names generation 3
  - Generation 1 (carries the root fact with the bootstrap `envelope` provenance; the bootstrap request's own forward outcome is NOT retained): the root fact retained with `authority` true under the bootstrap `envelope` provenance (root source 34 bytes), zero read occurrences, zero issuance facts (no supported issuance was registered for that committed request)
  - Generations 2→3: each added exactly one trusted issuance fact (tool `exec_command`, endpoint `responses`, two distinct service call IDs across the two generations, identical argument fingerprints, parent frontier the root anchor only); the values themselves are not retained. Which driver round corresponds to which generation is NOT retained
  - Forward evidence: the two post-bootstrap committed transactions each evidence a completed main forward (their trusted issuance facts are registered only from that committed request's actual direct main upstream response); the first committed transaction's forward outcome and the fourth request's disposition are NOT retained
  - Compiler evidence (bounded statement only): the committed root transaction evidences that the root entry's compilation succeeded and was validated before its durable commit (the atomic transaction commits only after a validated compilation); no file entry was ever admitted (zero read occurrences in every committed generation), and one compile per unchanged entry per epoch bounds the run's compiler work to the single unchanged root entry. The exact stage counter (`slaif_v1_compiler_dispatch_total`) is NOT retained, so no exact dispatch count is stated
- Real-model dependency acquisition (the acquisition payload carrying a genuine issued tool ID plus its synthetic result), compiler result validation for the acquired file entry, and the resulting replacement: NOT RUN — blocked by the pre-run harness defect (the retained issued call was stripped from the r1 record before the acquisition branch could extract it, so the acquisition branch could never have run) and by the now-consumed four-main-call cap
- Wire-level statements (outbound body, reinjection content, per-round recompile counts): NOT RUN / NOT RETAINED — this direct-binding topology captures no outbound body and the per-round stage counters were lost to the driver serialization defect; the committed-transaction evidence above is the content-free record
- The fourth request's typed outcome was not retained (driver serialization defect); the content-free record shows it either completed without a new durable state fact or was refused before the forward (a refusal commits nothing by design). Per-round statuses: NOT RETAINED
- The same fixture read was genuinely issued by the real model in the section 1 smoke (`cmd_is_fixture_read` true), establishing model-side tool issuance at the API boundary even though the candidate's acquisition transaction never ran.

### Criterion 3 — global live-window law (order section 3)
PASSED: only the exact sourced private endpoint or the owned candidate loopback were contacted; no redirects, no proxy environment (the candidate child received a minimal environment with no proxy variables); anonymous local synthetic fixture identity; no repository data; protected 0700/0600 config/state; no credential in argv or output (leak-checked: no bearer/key/numeric-URL strings in any retained evidence); every provider call capped at 60 seconds (smoke client timeout, candidate upstream `request_timeout_seconds` and compiler `timeout_seconds` configured at 60); raw-phase response evidence 22,014 bytes against the 256 KiB cap (the 22,014-byte figure is the raw phase only); the candidate phase's response bytes are not retained — the driver enforced a 256 KiB per-response read bound and no over-bound refusal is recorded in the retained lifecycle facts; compiler output capped at 3000 tokens by config; no retry loop; total live window: the run started 17:44:44Z and the candidate session ended 17:45:34Z (well inside eight minutes, zero deadline hits retained for the candidate run); cleanup limited to the owned candidate/config (temporary config, transient log and rebuildable venv removed; the protected synthetic recovery store and content-free facts retained).

## Verification
- Section 1 direct smoke run (the sourced service, private harness): PASSED — wrapper part-A exit 0; all six bounded calls 200 within caps
- Section 2 installed-wheel v1 candidate run: the session itself completed (candidate ready, the driver drove the full four-main-request sequence, clean shutdown, port refused) but the driver exited 1 at the final facts-retention step (`TypeError: keys must be str, int, float, bool or None, not tuple` — a raw tuple-keyed metrics snapshot in the facts payload); the original partial facts file (262-byte prefix) is preserved byte-identical and the content-free recovered facts were assembled from the protected recovery store and lifecycle state; no provider call was replayed
- Pre-run wheel digest verification: PASSED — `sha256sum` equals the order-mandated `e82f5ab8b7fa7833e7fbb5734c7612f81f149d2e6a4aae1e53275004437536d3`
- The 024-a fifteen locked verification commands at manifest head `745e892a5077679c7f43aac3460d6cf11bbd65b9`: PASSED (reused, not rerun — the intervening diff from the 024-b implementation head is transcript-only, `oap/` paths only, per the 024-b precedent) — all fifteen rc=0; umask-022 full pytest 7209 passed, 29 skipped
- The 024-a full clean-archive artifact proof at `745e892…`: PASSED (reused, not rerun — identical software inputs) — all assertions passed; rebuilt artifacts byte-identical to the manifest and to the repo gate `dist/`; fresh explicit Python 3.12.15 noneditable install verified
- `uv run --frozen python scripts/dev_provenance_manifest.py --verify --dist dist` at the new head: PASSED (exit 0; "development provenance OK: state=development head=7b22b877e1c3")
- `git diff --check fe9538452f7715c305ea2ae9da60726cb73d8d45..7b22b877e1c3dd7eae56e0d6045f7f3d85e69314`: PASSED (exit 0)
- GitHub CI at implementation head `7b22b877e1c3dd7eae56e0d6045f7f3d85e69314`: see the required-checks section below

## Live model/service evidence
- The owner-authorized private raw vLLM service (the protected reference was sourced with output suppressed and never inspected, read separately, copied, printed or committed; only environment names cross this report): `/health` 200; `/version` 200 (vLLM `0.32.0`); `/v1/models` 200 (one model; the declared alias listed); one nonstreaming Chat Completions 200 (`stop`, structured synthetic response); two streaming Responses calls 200 (terminal `response.completed`; the first genuinely issued the declared `exec_command` fixture read). All metadata GETs and both Responses calls within the ordered caps.
- The installed-wheel candidate on private `127.0.0.1:18031` against that service: the driver drove the ordered four-main-request sequence through the loopback (cap consumed; no further authorized candidate invocation made); three committed v1 transactions (durable generations 1→2→3) with the root fact retained with authority under the bootstrap envelope provenance; two of those committed transactions each evidence a completed main forward through their trusted issuance facts (two genuine model issuances recorded in the committed issuance ledger); zero read occurrences in every committed generation (no file was ever admitted); compiler work bounded to the single unchanged root entry by the accepted compile-once law over that retained record (the exact stage counter is not retained, so no exact dispatch count is stated); the bootstrap commit's forward outcome, the fourth request's disposition and all per-round stage counters are not retained; clean lifecycle (child-owned listener before readiness, clean shutdown, port refused, lock released).
- No raw payload or upstream error is retained; no protected fixture was contacted or mutated; the development port 18031 and repo-owned venv/config/state only.

## GitHub CI / required checks
- Implementation head `7b22b877e1c3dd7eae56e0d6045f7f3d85e69314` (PR #32): all ten checks PASSED — CodeQL pass (3s); Analyze (actions) pass (34s); Analyze (python) pass (2m55s); cache-native-containment pass (34s); cache-native-fixture pass (1m38s); docker pass (1m51s); docker-published pass (1m15s); gateway-contract pass (21s); operator-session pass (1m4s); test pass (18m5s)
- All required green at drafting: YES
- Report-head checks may be pending; strategy verifies.

## Local setup/dependencies
- Python 3.12.15 (`/home/janezp/.local/bin/python3.12`), uv 0.12.5; the linked-checkout venv (pinned 3.12.15) for the gate; the candidate venv (fresh, from the exact wheel) removed during post-run cleanup
- No new dependencies, no service changes, no sudo actions
- Private disposable harness (never committed): `work-artifacts/oap-024c-work/harness/` (direct smoke, candidate driver, wrapper) with both pre-run defects corrected post-run; durable content-free evidence under `work-artifacts/oap-024c-work/captures/` (0600) and the protected synthetic recovery store under the 0700 run directory (three committed generations, pointer to generation 3, empty writer lock)

## Documentation
- Not required: no product, behavior, configuration, security, test or operational change landed in this round (transcript-only implementation commit; the order forbids docs changes absent a separate order).

## Safety/scope confirmations
- Unrelated files: the operator's local `AGENTS.md` wording update stays unstaged in the linked checkout and was not committed; the primary checkout is untouched
- Secrets/raw content: the protected reference was sourced with suppressed output and never inspected; only environment NAMES appear; no credential, private URL, bearer, prompt, source, image, tool output or request/response body is printed, committed, logged or retained (leak-checked: no bearer/key/numeric-URL strings in any retained evidence); the run-owned temporary config (which carried the private base URL), the transient candidate log and the rebuildable venv were removed after the run
- Protected 18020/Qwen/Codex fixture changed: NO (the order authorizes bounded READ-ONLY live calls to the owner-authorized service only; no service mutation, no gateway use, no other credentials, aliases or vehicles)
- No new Codex, no temporary client handoff, no active profile change, no benchmark, no release
- Required tests skipped/not run: the real-model dependency-acquisition half of criterion 2 (NOT RUN, blocker exact above); genuine-client/native-compaction/image/recovery-restart/overhead acceptance remain later within objective 024
- Scope deviation: none beyond the two private-harness defects, both disclosed with their exact causes
- Extra objective PR: NO; coding merge: NO
- Active/order edited: NO (committed byte-identical copies, sha256-verified); report commit report-only: YES

## Known limitations/blockers
- Real-model dependency acquisition (acquisition payload, file-entry compiler validation, replacement of the acquired carrier) is NOT RUN this round: the pre-run driver defect made the acquisition branch unreachable even on a genuine issuance, and the four-main-call cap is now consumed, so the case cannot run within the existing candidate and total ceilings
- The per-round typed outcomes and the fourth request's disposition (refused-before-forward vs completed-without-new-fact) are not retained (the driver serialization defect); the content-free recovery evidence is the record
- The genuine client, native compaction, image, recovery/restart and overhead acceptance criteria remain unearned, as ordered

## Recommended strategic follow-up
- A later 024 round under a fresh activation (with its own main-call budget) can run the corrected private harness to earn the real-model dependency-acquisition half; the harness defects are corrected in the private bytes and the protected synthetic recovery store plus content-free facts are retained under `work-artifacts/oap-024c-work`

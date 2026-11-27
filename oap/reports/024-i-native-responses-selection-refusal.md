# OAP Coding-Agent Report — 024-i

## Work order
- Identifier: 024-i; order path `oap/orders/024-i-native-responses-selection-refusal.md`; numeric objective 024
- PR mode: AMENDED_EXISTING_PR

## Status
COMPLETE

## Executive summary
This round diagnosed the genuine seed refusal (six HTTP 422, all closed
reason `selection_refused`, zero main forwards) against the native rollout,
the exact client version's request construction, and an in-memory synthetic
preflight on the installed product. The project-private native-rollout
reference (CLI 0.164.0, the expected provider/model/version) records the
seed input as THREE message items — one `developer` message with three
`input_text` parts, and two `user` messages (two and one `input_text` parts)
— each message payload additionally carrying a 40-character `id` and one
client-internal metadata-passthrough field (field name only; no values,
prompts or private identifiers were used in this report). The in-memory probe
ran the INSTALLED product's own closed Responses mapper (exact 024-a wheel
code, 024-h private venv) on the exact recorded item shapes under five
envelope variants (items only; developer text as top-level `instructions`;
each with a flat `function` tool spec and the standard envelope fields):
every variant was countable (three messages, the tool spec counted, zero
tool calls). The confirmed client-source fact (tagged 0.164.0 codex-rs
`core/src/client.rs` `ResponsesApiRequest` constructor) contains NO
`max_output_tokens` field, so the requested-generation sub-gate is excluded
as an observed wire fact. The six 422s therefore cannot be reproduced
offline from the recorded shapes: the adapter never records request bodies
by design, and the remaining budget-side sub-gates (count/capacity,
placement, aggregate) are not distinguishable from the retained counters.
Per the order, product behavior is left INTACT (no product source,
contract, configuration or route change) and the smallest private one-run
observation was prepared: the candidate's existing per-request fact now adds
(1) a CLOSED request-shape projection (known schema names plus a fixed
`other` category and count for every unknown client-supplied field, item
type, role, part type or tool type — no unknown names, values, descriptions
or schemas retained), (2) the installed product's OWN mapper verdict as a
single boolean (plus its closed exception type name only if the mapper
itself raised), and (3) the closed rejection-stage string restricted to the
product's own `V1_REQUEST_FAILURES` code enum, with every other error code
(provider-originated or otherwise) mapped to the fixed
`other_error_code` category. The private launcher setup gap is fixed: the
shared `marker-env.sh` supplies a fresh, independent
`SLAIF_V1_024H_MARKER_KEY` for each new session via the child environment
only (never printed, logged or written to disk) in the live launcher, and
the fake preflight now exercises that exact launcher-side setup (closed
fact `marker_key_env_setup = "wrapper"`). The updated synthetic preflight
PASSED end-to-end (the buffered observation middleware is byte-faithful:
the four-request flow including the byte-identical transformed replay is
unchanged), and a focused product regression on the budget/refusal/envelope
scope passed. No product source changed, so the exact clean noneditable
024-a wheel (SHA-256 `e82f5ab8…`) is unchanged and re-verified by the
launcher/preflight gates. No Codex was launched, no live Qwen request was
made, and all genuine checks (combined acquisition, native compaction,
R04/R05) remain PENDING.

## Authoritative GitHub state
- Repository `ulfe-lmi/slaif-local-coding`; PR #32 state OPEN
  (https://github.com/ulfe-lmi/slaif-local-coding/pull/32)
- Base `main`; head `oap/024-cache-real-codex-qualification`
- Starting remote SHA `35a41fe64d23e18ea11d524fc0b6bf429c874f99` (024-h
  report)
- Implementation head SHA: 2a7b6db2f68de6782b9ead82eaa7b4be417b3da8
- Report publication commit: SELF
- Implementation commits pushed before report: 1 — `2a7b6db` (activated
  024-i order and `oap/active` transcript; unchanged strategic bytes,
  order file sha256 `62a9cde2…` verified in the linked checkout)
- New PR this round: no; amended existing: yes; merge performed: NO

## Changes and files
- No tracked software, docs, dependency, test or configuration change in
  this round (product behavior intentionally intact; the live refusal was
  not reproduced by any concrete supported native envelope form, so no
  product code or contract change is authorized or made).
  `git diff --stat 35a41fe..2a7b6db -- src tests docs scripts packaging
  oap/reports` is empty; the full diff from the prior report head is
  exactly `oap/active` (2 +/-) plus the new 024-i order file.
- Private disposable artifacts only (protected project root
  `work-artifacts/oap-024h-work`, 0700, never committed):
  - `harness/marker-env.sh` (NEW; the shared fresh marker-reference setup:
    one `secrets.token_urlsafe(32)` value exported under the fixed env
    name, environment-only, never printed or written to disk);
  - `harness/launch-024h.sh` (modified: sources the shared setup and
    exports the fresh independent marker reference before the single
    suppressed `source` of the protected reference and the candidate
    `exec`);
  - `harness/run_024h.sh` (modified: the synthetic preflight wrapper now
    supplies the SAME launcher-side marker setup, proving it end-to-end);
  - `harness/driver_024h.py` (modified: the coordinator reuses the
    wrapper-supplied marker reference when present (closed fact
    `marker_key_env_setup = "wrapper"`), otherwise generates one
    (`"generated"`); new in-process `shape_projection_check` (closed
    vocabulary: known names survive, every unknown collapses to `other`
    with its name discarded) and `inbound_facts_check` (every persisted
    observation line is closed-form and every 200 line's envelope was
    countable by the installed product's own mapper), both wired into the
    round outcome);
  - `harness/candidate_024h.py` (modified: the per-request fact middleware
    now buffers and byte-identically replays the inbound body, records the
    closed request-shape projection, the installed product's own
    `_envelope_structure` verdict as a boolean, and the closed rejection
    code restricted to the product's `V1_REQUEST_FAILURES` enum (any other
    code string — provider-originated or otherwise — is persisted only as
    the fixed `other_error_code` category)).

## Acceptance evidence
Private captures are content-free (counts, closed stage outcomes, closed
category names, booleans; 0700/0600, never committed) under
`work-artifacts/oap-024h-work/`. Raw bodies, model prompts, tool
schemas/descriptions, provider secrets and protected URLs were never
recorded, and no private identifiers or raw rollout contents appear in this
report.

### Criterion 1 — Diagnosis of the fixed refusal path
- Native rollout (synthetic-only reference beside the 024-h harness):
  closed shapes as in the Executive summary (three message items;
  `input_text` parts only; no function/tool-call items recorded — the seed
  never completed).
- In-memory synthetic preflight (installed product code, no request, no
  provider call): all five envelope variants of the EXACT recorded item
  shapes are countable by the installed closed Responses mapper (three
  messages, one tool counted in the tool-bearing variants, zero tool
  calls). The recorded input item shapes do not reproduce the refusal.
- Client-version request construction: the confirmed tagged 0.164.0
  codex-rs `ResponsesApiRequest` constructor has no `max_output_tokens`
  (no match in the file), so the generation-field sub-gate is not an
  observed wire fact and was not treated as one.
- Live-run reported observations (treated as reported observations with
  possible overlap, not wire proof): six 422 rows with pre-gate stage
  labels (recognition/acquisition/admission/compilation/graph/recovery)
  and zero forwards; one 200 row with one compiled block and no
  attributable stage record (it does not qualify the seed). The
  discriminator supplied by the reviewer-side test (recorded shapes
  countable by an ordinary flat function vs the product counter's
  function-namespace handling) was exercised directly against the
  installed mapper as above.
- Conclusion: the remaining budget-side sub-gates cannot be distinguished
  offline from the retained closed facts (the request bodies were not
  recorded by design). Per the order, product behavior is left intact and
  the one-run observation below is prepared. Fail-closed behavior for
  unknown and over-bound shapes is preserved: no mapper, budget,
  placement or selection code changed.

### Criterion 2 — Existing route setting vs product change
- No confirmed compatibility issue reproducible from the evidence exists,
  so no existing route setting was changed and no product code or
  contract was touched (the order's change precondition — a concrete
  supported native envelope form that reproduces the refusal and that an
  existing policy cannot handle — is not met by the recorded shapes).

### Criterion 3 — Smallest private one-run observation
- Closed rejection stage: the per-request fact persists
  `inbound_refusal_code` ONLY from the product's own closed
  `V1_REQUEST_FAILURES` code enum (e.g. `v1_selection_refused`); every
  other code string maps to the fixed `other_error_code` category
  (provider-originated codes are never retained).
- Closed request shape: `inbound_shape` retains known schema field/item/
  role/part/tool names plus a fixed `other` category with a count for
  unknown client-supplied names (no unknown names, values, text,
  descriptions or schemas are retained); `instructions` state and
  generation-field VALUE TYPES (closed type names) only.
- Product-mapper verdict: `inbound_countable` is a single boolean from the
  installed product's own closed Responses mapper (its closed exception
  type name only if the mapper itself raised).
- No new audit machinery, framework or planning document: the observation
  extends the existing private per-request fact middleware only, and the
  in-process checks extend the existing `wrapper_shape_check` pattern.

### Criterion 4 — Private launcher marker-setup fix
- `harness/marker-env.sh` (shared): one fresh `token_urlsafe(32)` value
  per process tree, exported under `SLAIF_V1_024H_MARKER_KEY`,
  environment-only; never printed, logged or written to disk.
- `launch-024h.sh` now supplies that fresh independent marker reference
  for the new synthetic session before the candidate `exec` (the gap that
  strategy recovered with a one-run environment value).
- Proved in the fake preflight: `run_024h.sh` supplies the same
  launcher-side setup, the driver records the closed fact
  `marker_key_env_setup = "wrapper"` (the wrapper-provided value fed the
  candidate), and the full four-request flow PASSED.
- The private project artifact root, bounded loopback ports (18031/18032)
  and explicit teardown are preserved (the passing preflight's stop facts
  show clean exit, reaped PID and connect-refused ports).

### Criterion 5 — Focused regressions and required checks
- `bash harness/run_024h.sh` (run
  `0f9fc5771422fa0a8e1857874da4ee1f-synthetic`): PASSED — driver exit 0,
  `outcome: PASS`, `round_problems: []`, exact caps (4/4 main, 2/2
  compiler), `marker_key_env_setup: "wrapper"`, `shape_projection_check`
  7/7 booleans true, `inbound_facts_check` 4 lines closed with every 200
  line countable by the installed product's own mapper, wrapper check
  6/6, clean stop facts, peer closed.
- Focused product regression (repo `.venv`, Python 3.12.15, umask 022):
  PASSED — 4 passed in 4.08s for the budget/refusal/envelope scope
  (node IDs listed under Verification).
- No product source changed, so no wheel rebuild is required; the exact
  clean noneditable 024-a wheel (SHA-256
  `e82f5ab8b7fa7833e7fbb5734c7612f81f149d2e6a4aae1e53275004437536d3`)
  remains the candidate's artifact and was re-verified by the
  launcher/preflight wheel gates before launch.

### Criterion 6 — Prohibited actions not taken
- No Codex launched, no live Qwen request, no protected profile/service/
  network change, no gateway, no benchmark dispatched. Genuine combined
  acquisition and native compaction remain PENDING. No new temporary
  right-pane handoff was performed (it requires separate human approval).

## Verification
- `bash harness/run_024h.sh` (final preflight after the refusal-code
  closure correction): PASSED — run
  `0f9fc5771422fa0a8e1857874da4ee1f-synthetic`, `outcome: PASS`,
  `round_problems: []`, `marker_key_env_setup: "wrapper"`,
  `shape_projection_check` 7/7 true, `inbound_facts_check`
  `{"lines": 4, "ok_requests_countable": true, "shapes_closed": true}`,
  all four requests 200 with `inbound_countable: true` and
  `inbound_refusal_code: null`, teardown clean (reaped, 18031/18032
  connect-refused).
- In-memory mapper probe (installed wheel code, no request): all five
  recorded-shape variants countable (closed booleans true; counts only).
- Focused pytest: PASSED — 4 passed in 4.08s, exactly
  `tests/test_v1_application.py::test_pre_forward_budget_refusal_keeps_the_exact_prior_state`,
  `tests/test_app.py::TestV1ApplicationClosure::test_budget_overflow_refuses_then_heals`,
  `tests/test_app.py::TestV1WireClosure::test_request_level_overflow_refuses_before_main_forward`,
  `tests/test_app.py::TestV1WireClosure::test_responses_emitted_envelope_message_limit_first_and_replay`.
- `git diff --stat 35a41fe..2a7b6db -- src tests docs scripts packaging
  oap/reports`: empty (transcript-only commit).
- Transcript byte verification: 024-i order sha256 `62a9cde2…` verified
  identical in the linked checkout before staging; staged diff exactly
  `oap/active` and the new order file.
- `git push` of the transcript: remote branch head and PR #32 head both
  `2a7b6db2f68de6782b9ead82eaa7b4be417b3da8` (verified via
  `git ls-remote` and `gh pr view`).

## Live model/service evidence
- NONE this round, by order: no live Qwen request, no Codex launch, no
  protected fixture touched. The diagnosis used only the retained private
  live-run facts (closed stage labels, counts, statuses), the
  synthetic-only native rollout reference, the confirmed client-source
  fact, and in-memory checks on the installed product.

## GitHub CI / required checks
- Implementation-head check states - all ten checks observed for
  `2a7b6db2f68de6782b9ead82eaa7b4be417b3da8` (PR #32 head at drafting):

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
  in the linked checkout after the transcript push, `test` 16m3s)
- Report-head checks may be pending; strategy verifies.

## Local setup/dependencies
- No new dependencies, venv or service change. The 024-h private venv
  (Python 3.12.15, exact noneditable 024-a wheel, marker-bound) is used
  unchanged by the updated harness; the repository `.venv` (Python
  3.12.15) runs the focused product regression. No sudo, no service
  changes, no global configuration changes. The worker's Codex
  configuration files are untouched.

## Documentation
- Not required: no tracked behavior, configuration, security, test or
  operation change in this round (transcript-only commit). The
  architecture/ledger state is unchanged; the native-compaction stage
  remains unearned until the next authorized client run is reviewed.

## Safety/scope confirmations
- Unrelated files preserved; the operator's local `AGENTS.md` wording
  stays unstaged in the linked checkout.
- No secrets or raw content committed, printed or retained: the protected
  reference was never inspected or printed (the preflight remains
  source-free; the launcher sources it once, suppressed, inside the
  adapter launch only); the fresh marker key crosses only via the child
  environment and is never printed or written to disk; the one-run
  observation is closed-form by construction (known schema names plus
  fixed `other` categories, booleans, closed type names and the product's
  own closed v1 code enum); no private URLs, credentials, prompts, tool
  schemas or raw rollout contents appear in this report.
- Production/protected resources untouched: port 18020, `qwen-serving`,
  model/checkpoint files, API-key files, firewall/VPN, and both OAP
  agents' Codex profiles/profile paths — NO change.
- Extra objective PR: NO. Coding merge: NO. Active/order edited: NO
  (strategic bytes committed unchanged, hash-verified). Report commit
  report-only: yes.
- No Codex process launched, no live request, no second client or live
  listener, no benchmark, no release.

## Known limitations/blockers
- The exact live-refusal sub-gate remains UNDETERMINED offline: the
  recorded shapes are countable by the installed product's own mapper and
  the generation field is excluded by the confirmed client source, so the
  six 422s cannot be reproduced from the retained evidence. The prepared
  one-run observation (closed rejection stage + closed request shape +
  product-mapper verdict) will distinguish a mapper-side shape refusal
  (unknown field/item/role/part/tool name in the actual wire request)
  from a budget-side sub-gate (count/capacity, placement or aggregate) in
  the next authorized run.
- All genuine checks remain PENDING by design: real-model, genuine-client
  and genuine-compaction criteria (including R04 native-compaction root
  presence and R05 source-absent reinjection in the native session) are
  earned only by the authorized strategy-owned client run.

## Recommended strategic follow-up
Factual only: (1) in the next authorized run, use the updated
`launch-024h.sh` (it now supplies the fresh marker reference itself; no
one-run environment value is needed); (2) after the run, read the
per-request closed facts — `inbound_refusal_code`, `inbound_shape`
(including any `other` categories) and `inbound_countable` — to
determine whether the refusal is mapper-side (a client wire shape outside
the closed vocabulary, in which case a concrete supported native envelope
form exists to evaluate under the order's product-change precondition) or
budget-side (a sub-gate of the closed final accounting); (3) review this
report and decide the next suffix.

# Dependency-bundle cache — pinned tokenizer, budgets, direct compiler and selection contract (objective 021)

Versioned contract: `cache-bundle-tokenizer/v1`, `bundle-tokenizer-policy/v1`,
`bundle-render-policy/v1`, `cache-bundle-budget/v1`,
`bundle-budget-policy/v1`, `qwen3-model-envelope/v1`,
`cache-bundle-compiler/v1`, `bundle-compiler-policy/v1`,
`bundle-compiler-prompt/v1`, `bundle-compiled-index/v1`,
`bundle-compiler/v1`, `cache-bundle-compile-work/v1`,
`bundle-compile-work-policy/v1`, `cache-bundle-selection/v1`,
`bundle-selection-policy/v1`.

Status: inert component law for objective 021 (`oap/021-cache-token-compiler`),
implementing B01–B04 and the compiler half of C03 at the INERT component layer
over the ACTUAL accepted 018 current P/T records, the accepted 019 RAM owner /
single-flight work plane and the whole-020 protected session recovery
component. PENDING strategic review at its bounded inert component scope;
no configuration key, no request-pipeline wiring, no v1 runtime activation.

Owning modules and tests (all under
`src/slaif_local_coding/constitution/bundles/` / `tests/`):

| Concern | Module | Test suite |
| --- | --- | --- |
| Pinned tokenizer | `bundle_tokenizer.py` | `tests/test_bundle_tokenizer.py` |
| Insertion budgets | `bundle_budget.py` | `tests/test_bundle_budget.py` |
| Direct compiler | `bundle_compiler.py` | `tests/test_bundle_compiler.py` |
| Compile-through-RAM (C03 compiler half) | `bundle_compile_work.py` (over the 019-b work plane) | `tests/test_bundle_compile_work.py` |
| Deterministic selection (C03 selection half) | `bundle_selection.py` | `tests/test_bundle_selection.py` |

## 1. Pinned actual-model tokenizer (`cache-bundle-tokenizer/v1`)

The declared reference capability is the pinned public CPU tokenizer of
`Qwen/Qwen3.8-27B` at Hugging Face revision
`37561816e66b5b9153b1b64c10968c18c1e6f4a0` (Apache-2.0), loaded with the
minimal locked CPU dependency `tokenizers==0.22.2` (exact version refused
otherwise).

- The FOUR pinned assets are CLOSED constants with exact sizes and SHA-256
  (`tokenizer.json` 12809320 / `tokenizer_config.json` 9984 /
  `chat_template.jinja` 9004 / `LICENSE` 11544), packaged under
  `constitution/bundles/tokenizer_assets/` with a retained `NOTICE` and the
  verbatim Apache-2.0 `LICENSE`; they enter the development source-input map
  and the wheel/sdist artifact checks.
- A missing, resized, re-hashed, unreadable or structurally wrong asset is a
  fixed typed refusal (`BundleTokenizerReason`), never a fallback to byte /
  character estimation and never a silent substitution.
- Load and validate ONCE: `get_bundle_tokenizer` verifies the exact pinned
  table, consumes the SAME verified byte snapshots (no second open), binds the
  vocabulary size, normalizer digest, template digest, render policy and
  loader version into the 64-hex tokenization identity
  (`derive_tokenization_identity`), and caches the engine process-wide with
  observable load counts; repeated counting and RAM hot hits never reload
  assets and never read recovery originals.
- A byte change to any asset or template changes the recorded digests and
  therefore the tokenization identity and every derived compiled-entry
  identity; the identity is recomputed from actual fields on every binding
  construction and a mismatch is refused (`IDENTITY_MISMATCH`).
- The render policy (`bundle-render-policy/v1`) embeds the pinned Qwen
  chat-family framing tokens verbatim with NO padding; renderers cover
  messages, tool envelopes and the compiled block.
- No model weights, no torch, no image decoding, no runtime model download
  and no hosted tokenizer call; the loader touches only packaged (or
  explicitly supplied) asset files. An arbitrary serving alias or the coding
  worker profile never proves the binding; actual deployed-fixture
  equivalence is verified only in 024.

## 2. Explicit validated budgets (`cache-bundle-budget/v1`)

The effective context `C` is an explicit validated product capability
(`BundleBudgetConfig.context_tokens`, 8192..1048576), configured — never
inferred from a serving maximum or an executor profile. Under the existing
validated configuration contract:

- Base slot = `floor(C/32)`; bundle width = the number of DISTINCT
  represented files; per-entry allowance = `width × slot`.
- Aggregate injection limit (initial `floor(C/4)`); explicit reserves:
  generation `max(4096, floor(C/8))`, tools 2048, uncertainty/template 1024 —
  each explicit, positive, within `C`, identity-bound and validated together
  against `C`; the caller's requested generation limit is respected and never
  lowered to force a fit.
- Per-retained-image reserves apply only after the UNCHANGED image policy and
  only under the explicit vision contract (`vision_enabled` with
  `per_image_reserve >= 1` and retained capacity; a mismatch is a typed
  refusal, never a silent reinterpretation).
- The final rendered compiled text — references, metadata and separators
  included — is counted with the REAL pinned tokenizer. Remaining request
  content and tool / envelope emissions are counted through the pinned
  compatible rendering (`qwen3-model-envelope/v1`): every DYNAMIC text is
  counted with the real tokenizer, and every FIXED template framing fragment
  is charged a closed conservative structural bound (the
  `ENVELOPE_*_BOUND_TOKENS` constants, provable over-estimates re-derived from
  the pinned template asset at test time), under explicit finite item limits
  (files / messages / tools / calls / args / images, each a closed
  positive identity-bound configuration value).
- Byte / parse limits (per-message, per-request, per-entry, per-compiled-
  block bytes; JSON depth) are INDEPENDENT of tokens and enforced before
  token work; a crossing is a typed refusal (`ITEM_LIMIT_EXCEEDED`,
  `BYTE_LIMIT_EXCEEDED`), never truncation.
- `BundleBudgetPlan.decide` is deterministic required-then-optional: required
  entries are complete-or-typed-failure (over-allowance or byte-bound
  crossing is `ENTRY_INVALID`, never silent truncation or dangling required
  references); optional entries are WHOLE-ENTRY omissions; the AGGREGATE
  floor(C/4) limit is decided over the EXACT COMBINED final injected text
  (`join_separator.join(included_blocks + final_extras)`) counted with the
  real pinned tokenizer — the combined count, not the SUM of the individual
  block counts — and the emitted extras alone must fit the aggregate limit
  (typed `CONTEXT_OVERSUBSCRIBED`, never a silent pass). Request content that
  alone exceeds the remaining capacity is `REQUEST_OVERFLOW`; no padding is
  ever emitted or assumed.
- Unknown or mismatched template / model / context / vision contracts refuse
  (fixed 422-class typed failures), never guess.

The 64-hex `plan_identity` binds the budget configuration, the pinned
tokenization identity, the render policy version and the model envelope
version; the three reference contexts (262144, 32768, 40000) are exercised at
their actual boundaries, including repeated operands, many messages / tools,
large requested output, no padding and no silent truncation.

## 3. Direct authenticated compiler (`cache-bundle-compiler/v1`)

The compiler is a DIRECT authenticated tool-free NON-RECURSIVE upstream
channel that treats the admitted entry's source as data:

- The input is ONE actual `RootRegionAdmissionEntry` (018-t): the ROOT row's
  source is its actual `ResolvedRootRegionSource`; the FILE row's source is
  its actual first-compatible original `BundleProof` aggregate; the digest /
  byte length are re-derived and must agree (`SOURCE_HASH_MISMATCH`
  otherwise). Boundaryless mixed admitted content keeps unknown possible
  origins and the original data role: no invented governing attribution, no
  promotion of off-graph content, no dependency may be P0 (only the supplied
  root is P0).
- The FULL compile key (`derive_compile_key`) binds the entry identity and
  content key, the source digest / length, the mandatory deterministic
  candidate paths, the compiler CONFIG IDENTITY, the tokenization identity,
  the budget identity and the render policy version. A changed
  context / tokenizer / compiler policy changes the key; incompatible reuse
  is impossible by construction (B04).
- The compiler config carries DISTINCT bounded identity-bound policies:
  input bounds (source / prompt bytes), the generation allowance (SINGLE
  attempt — V1 has NO automatic infrastructure / schema / truncation retry
  and NO adaptive ceiling), the supported reasoning effort, the JSON overhead
  bounds and the timeout. The final rendered insertion allowance is NOT a
  config value: it is the ACTUAL per-entry `width × slot` from the budget
  plan, supplied per demand.
- Identity law: the config fingerprint binds the DECLARED immutable model
  revision plus the OPAQUE configured upstream-compatibility identity. A
  serving alias and the private transport URL alone never prove the binding;
  `base_url` is transport-only, stays out of the identity material and out of
  the repr, and the credential is a protected ENVIRONMENT reference
  (`api_key_env`), never a literal, never an identity input, never logged or
  reported.
- The structured output is the closed `bundle-compiled-index/v1` schema,
  validated BEFORE anything may become an entry: strict bounded JSON (depth,
  size, duplicate keys); provider truncation (`finish_reason == "length"`) is
  typed BEFORE any content validation; governing scopes, MUST/MUST_NOT/NEVER
  strengths, exceptions, conflicts, ALL mandatory deterministic candidates
  exactly once (none invented, none erased) and SEPARATE reference-confidence
  from constitutional-priority are enforced (`SCHEMA_INVALID`,
  `CANDIDATE_SET_MISMATCH`, `CONTRADICTORY_OUTPUT`, `ATTRIBUTION_INVALID`).
- The final rendered compiled block (references, metadata and separators
  included) is counted with the REAL pinned tokenizer and must fit the ACTUAL
  rendered allowance; over-allowance is a typed invalid result
  (`OVER_ALLOWANCE`), never a truncation.
- Invalid / truncated / over-budget / cancelled output never becomes an
  entry or a hit and is never best-of-replayed. There is no retry of any
  kind, no tools, no images, no recursion, no Gateway credential and no
  hidden original fallback.
- Ordered accounting: `BundleCompilerAccount` separately meters the DISPATCHED
  call and its typed outcome (content-free); a demand cancelled after
  dispatch records ONE call plus the CANCELLED outcome, retains no payload and
  claims no unreturned provider output. Compiler usage and recovery usage are
  distinct ledgers.
- Fake upstream tests prove the actual compiler request shape, call counts,
  error mapping and cancellation; no real inference runs in this order.

## 4. Compile-through-RAM composition (C03 compiler half, `cache-bundle-compile-work/v1`)

ONE bounded composition operation resolves ONE actual current admitted entry
through the ACCEPTED 019-b `RamWorkCoordinator` work plane with the ACTUAL 021
pinned direct compiler, tokenizer and validated budget plan — the injected
seam is the ACTUAL `make_entry_compile_seam` (no synthetic payload), so this
is "one ACTUAL compiler leader": concurrent identical demands join the ONE
shared upstream attempt and a retained valid payload is a RAM-only HIT.

- The budget identity and the per-entry rendered allowance are DERIVED from
  the plan (`plan_identity`; `width × slot` over the entry's ACTUAL admitted
  width); the caller never supplies them independently. The FULL compile key
  is re-derived at this boundary with the exact accepted recipe.
- CONFIGURED-POLICY FENCE (the B04/C03 full-key fence at the claim boundary,
  BEFORE any work-plane claim or publication): `derive_compile_policy_fingerprint`
  joins the configured policy (compiler config identity + plan identity) into
  ONE 64-hex fingerprint that MUST equal the trusted namespace's
  `config_fingerprint`. A mismatched demand is refused
  `POLICY_FINGERPRINT_MISMATCH` (fixed 409, zero invocations, no claim, no
  terminal, no payload). A changed policy is a genuinely distinct namespace
  (distinct `config_fingerprint` -> distinct lineage key -> distinct owner)
  that earns its own compile — never a cross-namespace reuse.
- The work plane is keyed by the entry's ACTUAL stable semantic content key
  (the accepted 019 current-key law is unchanged). EVERY serving payload
  (COMPLETED / JOINED / HIT) is strictly re-validated and the full-key /
  content-key joins are re-run before it is served; a retained payload whose
  full key differs is NEVER reused — the closed typed `POLICY_STALE` outcome
  (zero new invocations, nothing discarded or recompiled inside the epoch).
  The needed rebuild happens only through a needed NEW epoch: an explicit
  teardown or the 020 authenticated restart / recovery, which allocates a
  strictly higher epoch on a fresh owner.
- The 019 single-flight law, the NO-RETRY terminal law, the capacity fences
  and the currentness fence are the ACCEPTED 019-b laws exercised unchanged
  through the actual seam: a terminal compiler failure (truncated / invalid /
  over-budget / upstream) is re-served with the SAME fixed typed limitation
  and zero new invocations.
- The same full key hits on unchanged compatible content, including unrelated
  B admission and equivalent supported reads with unchanged meaning:
  A1 -> A2 -> a genuinely new compatible A1 reuses the valid historical
  payload WITHOUT a third invocation (the accepted 019-b retained-payload
  law over the actual seam), while replay cannot reactivate stale state.
- The closed outcome vocabulary maps the accepted work-plane outcomes
  one-for-one and adds `POLICY_STALE`; the work-plane limitation, epoch,
  invocation counts and fixed typed status are carried through unchanged; the
  composition adds its closed pre-claim limitation vocabulary
  (`BundleCompileWorkLimitation`, both fixed 409).
- The composition holds ONE `BundleCompilerAccount`; compiler usage is
  metered separately from recovery usage (020) and both stay distinct
  ledgers. 020 needed-only restart preparation is reused unchanged: recovery
  recompilation is separate work with a new epoch and a recorded reason.

## 5. Deterministic selection (C03 selection half, `cache-bundle-selection/v1`)

`select_working_set` is ONE pure deterministic complete selection over ACTUAL
admitted entries (018-t) and VALIDATED compiled indexes:

- REQUIRED governance first: the P0 root entry plus every proven FILE entry
  representing a path of the ROOT-SCOPED P1 BINDING CLOSURE (the root index's
  mandatory P1 deterministic candidates, closed through the ACQUIRED ready
  P1 entries' own mandatory P1 candidates to a fixed point). No opaque
  reference or uncertain greedy attribution substitutes for usable required
  content.
- Then the OPTIONAL entries, ranked by the ACTUAL P2/P3 constitutional
  priority declared for the paths they supply (P4 background contributes
  none), then the narrower eligible coverage, then the stable identity —
  priority affects injection only, never graph eligibility or admission; the
  ordering is stable and deterministic.
- The scoped root / authority envelope (scopes, authorities,
  source-of-truth boundaries) is carried from the root index.
- MISSING-BINDING GUIDANCE: a binding-closure path with NO proven ready entry
  emits the exact read guidance (ordinary local tools, before substantive
  mutation); an opaque reference or uncertain greedy co-cached row never
  substitutes for the missing required content and can never suppress that
  guidance.
- DUPLICATE COVERAGE: an entry whose represented paths are ALL already
  covered is omitted WHOLE and observably (`COVERAGE_DEDUPLICATED`); a
  required entry whose binding paths are ALL preserved by an earlier selected
  proven narrower eligible entry is omitted WHOLE and observably
  (`BINDING_COVERED_BY_NARROWER`).
- An entry whose member origin is not fully proven carries the closed
  provenance line (the unproven member paths in canonical sorted order) in
  its final rendered block; boundaryless mixed content never claims
  governing attribution.
- The ACTUAL pinned-tokenizer budget plan decides over the ONE final rendered
  block per entry (the versioned render policy: compiled body wrapped with
  the entry label and its deterministic candidate references — the exact text
  the compiler validated against the rendered allowance), joined by the
  deterministic injection separator with the EMITTED missing-binding
  guidance as final extras: the AGGREGATE limit is decided over the exact
  combined final injected text with the real tokenizer; whole-entry optional
  omissions (`BUDGET`) and TYPED essential overflow (422) apply — never
  truncation, never dangling required references.
- Selection is pure: no I/O, no model calls, no recompilation due to
  selection alone, no request replacement, no legacy behavior change.

## 6. Identity, reuse and epoch law (B04)

- The full compile key plus the content key plus the epoch are the ONLY
  reuse conditions: unchanged compatible content with the SAME full key is a
  RAM-only HIT (zero invocations) — including after unrelated B admission and
  equivalent supported reads with unchanged meaning.
- Changed context / tokenizer / compiler / budget policy changes the full key
  (and, through the policy fingerprint, the namespace): it is a genuinely
  new identity that earns its own compile; no incompatible compiled reuse.
- The 019 no-retry attempt law and the 020 explicit new-epoch exception
  stand unchanged: terminal failures are re-served with the same typed
  limitation and zero new invocations; only an explicit teardown or the 020
  authenticated restart / recovery allocates a strictly higher epoch, and
  replay cannot reactivate stale state.

## 7. Inertness and non-goals

All five modules are inert typed components under
`src/slaif_local_coding/constitution/bundles/`: no configuration key, no
request-pipeline wiring, no v1 runtime activation, no legacy behavior change,
no runtime success claim from this component. Explicit opt-in configuration
and transactional source replacement / forwarding (022), the full stack
(023) and genuine Codex / actual-model qualification — including deployed-
fixture tokenizer equivalence (024) — remain mandatory and NOT RUN. No
benchmark, release, deployment or cutover is authorized by this contract.

# OAP work order — 021-a: pinned tokenizer, bundle compiler and selection

Numeric objective 021, CREATE_NEW_PR from verified remote main `b9c6b41e34a004a69d11e3467d6db610c93a1ef5`
(accepted whole 020, PR 28). Create exactly one branch
`oap/021-cache-token-compiler` and one PR. No existing 021 PR or branch.
Preserve unrelated PR 23. Strategy alone accepts and merges.

## Scope

Implement the existing 021 component stage in
docs/CACHE-IMPLEMENTATION-PLAN.md and docs/CACHE-REWORK-LEDGER.md (B01–B04
and the compiler half of C03). Save focused increments for tokenizer and
budget, compiler, then selection and composition on one branch. Reuse
accepted 018 current P/T entries, 019 same-key/epoch work and 020 recovery;
use the existing legacy compiler transport where it preserves these rules.
021 stays inactive in the request pipeline. Actual opt-in config and
transactional source replacement/forwarding (022), full stack (023), and
genuine Codex/actual-model qualification (024) remain mandatory. No new
planning or audit framework and no expanded acceptance matrix.

1. Use the actual public CPU tokenizer for the declared Qwen3.8-27B
   reference capability. The pinned upstream is `Qwen/Qwen3.8-27B` at
   Hugging Face revision `37561816e66b5b9153b1b64c10968c18c1e6f4a0`
   (Apache-2.0). Bounded build-time GETs are authorized only for these files
   at that revision, verifying exact sizes and SHA-256 before using them:

   | File | Bytes | SHA-256 |
   | --- | ---: | --- |
   | tokenizer.json | 12809320 | 0997f410c57a1f4e53b09e4be8f4a172d90edd9564368fb0847030937229b9f3 |
   | chat_template.jinja | 9004 | af16f654968d47d09a6c604e00370b12dbc21f76456f59c9e98b82e84d9f6375 |
   | tokenizer_config.json | 9984 | 207c03c41a06a9c3b0cc527d8a56115159c1eac6b59a4ffae85b646e773d074e |
   | LICENSE | 11544 | bbedc3fda3305820b977265f01b8619d87570a6739de3a5582c3464840f1e57a |

   Permit minimal locked CPU dependency `tokenizers==0.22.2`. Deliver an
   offline verifiable package or local asset contract, retaining license
   and notice. Packaged files must enter source-input map and actual
   wheel/sdist checks; prove asset/template byte changes invalidate identity.
   Load and validate once; repeated counting and hot hits do not reload
   assets or read recovery originals. Bind supported model vocabulary,
   normalizer, template/render policy and effective route/session config.
   An arbitrary serving alias or the coding worker profile never proves
   that binding. Actual deployed fixture equivalence is verified only in
   024. No model weights, torch, model downloads at runtime or hosted
   tokenizer calls.

2. Effective C and generation/tool/template/image reserves are explicit
   validated product capabilities. Test C=262144, 32768 and 40000. Base
   slot floor(C/32), width the distinct represented file count, allowance
   width × slot, initial aggregate floor(C/4), generation initial
   max(4096,floor(C/8)), tools 2048, uncertainty/template 1024 under the
   existing validated configuration contract. Count final rendered compiled
   text including references, metadata and separators with the real
   tokenizer. Count remaining request content and tool/envelope emissions
   through pinned compatible rendering or documented conservative structure
   bounds under explicit finite item limits. Respect caller-requested
   generation limits and explicit per-retained-image reserves after the
   unchanged image policy; never lower the caller's requested output to
   force a fit. Unknown/mismatched template/model/context/vision contract
   refuses. Test actual boundaries, repeated operands, many messages/tools,
   large requested output, no padding and no silent truncation. Keep
   byte/parse limits independent of tokens.

3. Direct authenticated tool-free, nonrecursive upstream compiler over
   admitted entry/version/config and epoch. Close and validate structured
   output against actual source/evidence and full key: digest/version,
   mandatory deterministic candidates, binding strengths, scopes,
   exceptions/conflicts, separate confidence and priority, output shape
   and actual rendered allowance. Boundaryless mixed admitted content
   keeps unknown possible origins and original data role; no invented
   governing attribution or promotion of off-graph content. Input,
   generation, supported reasoning, JSON overhead and final insertion
   allowance are distinct bounded identity-bound policies. Detect provider
   truncation before validating success; invalid/truncated/over-budget/
   cancelled output never becomes an entry or hit. No retry, tools,
   recursion, Gateway credential or hidden original fallback. Fake
   upstream tests prove actual compiler request shape, call counts, errors
   and cancellation. Use 019 single-flight and 020 needed-only restart
   preparation. Preserve accounting; report compiler/recovery usage
   separately. No real inference in this order.

4. Select deterministic complete required governance before optional
   entries; stable ordering, scoped root/authority, missing-binding
   guidance, overlap coverage, whole-entry optional omissions and typed
   essential overflow. Never treat an opaque reference or uncertain
   greedy attribution as a substitute for usable required content.
   Prove the same full key hits on unchanged compatible content, including
   unrelated B admission and equivalent supported reads with unchanged
   meaning; changed context/tokenizer/compiler policy does not reuse.
   A1→A2→genuinely new compatible A1 reuses the valid historical payload
   without a third call, while replay cannot reactivate stale state. The
   019 no-retry attempt law and the 020 explicit new-epoch exception stand.
   Tests exercise actual admitted records, real tokenizer, fake compiler
   and selection together. No request replacement, legacy behavior change
   or runtime success claim from this component.

## Verification and publication

Apply the existing focused and full frozen gate (same 15 checks as 020-a,
with diff against `b9c6b41e34a004a69d11e3467d6db610c93a1ef5`), one clean Git-B archive artifact proof,
fresh noneditable installation, and all ten existing exact-B GitHub
checks. Use committed source A and manifest-only B; capture actual exits
and preserve prior frozen RC artifacts. Update owning docs and current
criterion ledger only, both architecture maps and all three compact
mirrors as needed. Preserve S compact inode/owner/mode in place. No
rewrites of older orders/reports. Keep unearned layers NOT RUN.

Use only the existing RIGHT pane %19 `codex --yolo --profile early-beta`
instance, PID 598258 birth 150182858. The existing 020-b control reader
is PID 1020447 birth 366439191 on original control inode 10648021;
use its exact 4f4b receipt and `oap/active`, no replay. Only a verified
worker crash permits restart in that pane using exactly that command.
No additional Codex/client startup, including CI. Original verified FIFO
objects are under `/home/janezp/codex-supervision/slaif-local-coding`;
the historical /synology alias is absent on this host. Use
`/home/janezp/codex-supervision/slaif-local-coding/work-artifacts/oap-021a-work`
for all new manual artifacts with private modes. No protected model,
service/profile/keys/network mutation, Gateway changes, release, registry,
benchmark, deploy or cutover.

Publish source/manifest and immutable order/active bytes on one PR.
Complete PR description, then commit one immutable matching report alone
as SELF with literal implementation SHA, parent B. Verify exact GitHub
head/parent/report bytes before writing exactly one response FIFO OK.
Start one managed foreground control reader in the same instance.
No coding merge or auto-merge.

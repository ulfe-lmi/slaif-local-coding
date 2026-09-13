# OAP Work Order — 008-a

## Objective and authoritative state

Objective 008 is a new Local-owned hardening/operability objective: durably
preserve every safely recoverable decisive Objective-005 sanitized result still
available at the four exact historical paths on this Local host, and implement a
small fail-closed export path so future sanitized acceptance evidence cannot
remain authoritative only in disposable temporary storage.

GitHub objective state: `008-a`, `CREATE_NEW_PR`. Start from exact current remote
Local `main` `2041bddc5a745ef0dd4f3088c24b74b9bceefdb9` (tree
`cc1b13890cdac76eb59e53288029f1da35e1c4a4`), create branch
`oap/008-durable-acceptance-evidence`, and create exactly one new PR to `main`.
Strategy verified before activation that Local is public/non-archived, no PR is
open, no Objective-008 order/report/branch exists, and merged-main run
`34754021199` has successful `test` and `gateway-contract` jobs.

The current reviewed Gateway peer remains GitHub commit
`65666f5886832034c52211fdd7604046557e6ada` (tree
`06946cf96dcb24c56a4560f8299271cb9c4d60fb`). Do not change the current peer
fixture. Local and Gateway development machines do not share filesystems; do not
look for or use Gateway state in `/tmp`, sibling paths, home, NFS, or another
host. This objective requires no Gateway checkout or modification.

Per direct human correction before activation, the existing OAP runtime selector
is `qwen-neumann`. Use that current configured coding profile. Do not choose,
create, alter, override, or test another model/profile/account; do not edit any
Codex-home profile/catalog file. Executor traffic is not acceptance evidence.
This order authorizes no product Qwen/provider/model inference or protected
service request.

Keep this one `008-a` round and one PR coherent through historical inspection,
implementation, test/CI corrections, report, and strategic merge review. An
absent historical artifact, schema reconciliation, or ordinary implementation/
test/CI failure is work to handle in this round, not grounds for another suffix
or an intermediate `BLOCKED` report. Stop only for a genuine external authority
or safety boundary.

## Historical acceptance authority and integrity

Preserve these distinct Objective-005 facts without rewriting them:

- merged Objective-005 Local:
  `e3f10e93c1ea84bf4021fd15d566bf577d5a9dcf`;
- successful target tested Local source:
  `a71d61f0507911cb2b4bf4a76da431102da7f9c8`;
- 005-ar final implementation/report parent:
  `c6519e35f9ee8e49681f7bec63ce122bf1118c8f`;
- immutable 005-ar report:
  `e9829d84cc4116f749ddc8bc97b08fa37231e77f`, path
  `oap/reports/005-ar-terminal-stream-repair-and-closure.md`;
- historical Gateway used for closure:
  `5ea38325ef3a3ebc69524b4679b795fab0c52935`.

Do not edit any Objective-005 order, report, or existing evidence. The final
Objective-005 strategic correction comment on PR #7 remains wording authority;
new evidence may cite it but may not rewrite immutable history or acceptance
semantics. Any new 005-ar evidence directory must say exactly that it is a
post-hoc durable preservation of previously generated sanitized evidence, not
evidence committed during Objective 005.

## A. Bounded recovery from only four exact paths

Inspect no historical host paths except these exact names:

1. final protected success:
   `/tmp/slaif-005-ar-protected-1024.O7Zsxd/protected-result.json`;
2. decisive 32-token diagnostic:
   `/tmp/slaif-005-ar-protected.GjMeEO/protected-result.json`;
3. final isolated fake identity target:
   `/tmp/slaif-005-ar-isolated-fake-1024.aipZdW/isolated-fake-target.json`;
4. reused AP37 fake authority:
   `/tmp/slaif-005-ap-fake-gate.rHO7rQ`.

Strategy's pre-activation metadata-only check observed all four as UID 1029,
GID 100, mode `0600`, non-symlink regular files sized respectively 88,274;
78,550; 36,240; and 685,832 bytes. Coding must revalidate independently before
reading: lexical parent chain and final node must not be symlinks; file must be
regular, current-user-owned, single-link where appropriate, restrictive, and
within an explicit bounded size derived to cover these known results. Do not
follow an unsafe node. Do not crawl/list/search other `/tmp`, home, history,
credentials, another host, or a Gateway machine.

For each exact path:

- if absent, record only `historical_temp_artifact_unavailable_on_this_host` and
  continue; never reconstruct or rerun inference;
- if present, validate the complete bytes with existing repository-owned safe
  result/schema/projection/privacy machinery before committing anything;
- require the exact known fake or protected result shape, all required fields,
  closed types/vocabularies and bounds; unknown top-level or nested content is a
  rejection, never silently stripped;
- independently reject any raw authorization/Bearer/API key, signing secret,
  signature, nonce, historically-private request/call/item ID, prompt, response
  or model-output text, tool output, source content, image/image URL, raw HTTP or
  SSE body, unrestricted provider error message, environment dump, private URL,
  or hash of a secret;
- compute a SHA-256 only after the safe complete artifact is accepted, and
  correlate its existing structural facts with the immutable 005-ar authority.

Never commit a questionable artifact. A schema/privacy rejection must be
reported with only a fixed safe class and must not expose rejected content.

## B. Durable Objective-005 evidence set

If accepted, preserve material artifacts under `oap/evidence/005-ar/` using
stable descriptive filenames. Priority is: final protected 1024 success;
decisive 32-token max-output diagnostic; final isolated fake target; and the AP37
fake authority only if its inclusion materially completes provenance and it
independently passes the same full audit. Do not copy irrelevant/intermediate
experiments.

Prefer exact original sanitized bytes. If repository conventions require a
deterministic normalization, do not invent or infer fields: record both the
original-safe-artifact SHA-256 and committed SHA-256 plus a fixed transformation
description. For an unavailable/rejected artifact, the manifest records only the
truthful finite availability/rejection class and report citation, not fabricated
content.

Add one compact strict machine-readable manifest/index containing only safe
provenance:

- manifest schema/version and the literal post-hoc-preservation classification;
- finite evidence role and availability for each of the four exact authorities;
- original and committed content SHA-256 when legitimately available;
- exact historical tested Local, Gateway, implementation-parent, immutable
  report path/SHA, and merged Objective-005 SHAs above;
- acceptance classification and only request/dispatch/count facts already in an
  accepted retained artifact where materially useful;
- relationship to the composed Objective-005 acceptance and the PR #7 strategic
  correction, without changing that acceptance.

Use existing `oap/evidence/005-*` conventions where compatible. Validate the
manifest strictly and keep it content-free beyond the allowed facts.

## C. Future fail-closed safe-evidence export

Historical copying alone is insufficient. Inspect how current Local acceptance
tooling produces `protected-result.json`, `isolated-fake-target.json`, fake
machine-gate/index results, and performs temporary cleanup. Implement the
smallest repository-owned acceptance/OAP helper or explicit runner option that
exports an already-sanitized known result into a caller-chosen durable location
before temporary cleanup.

Required contract:

1. acceptance/OAP tooling only; expected production `src/` delta is none;
2. explicit opt-in destination chosen by caller/order; no automatic Git
   staging, commit, or acceptance claim;
3. accept only explicitly modeled current safe protected/fake result schemas;
   unknown/missing top-level or nested fields and unsafe/open content fail
   closed; never sanitize an unknown raw object by dropping fields;
4. reuse existing safe result/projection/privacy validators where possible and
   avoid a second incompatible meaning of safe evidence;
5. destination resolves inside an explicit repository `oap/evidence` root;
   reject absolute escape, traversal, foreign ownership, and symlink destination
   or components; never make `/tmp` the durable authority;
6. deterministic JSON bytes/hashing where practical, or exact accepted bytes
   when that is the declared mode;
7. atomic same-directory write using a restrictive temporary file, mode `0600`,
   exclusive/no-follow semantics and fsync/rename discipline appropriate to the
   repository; refuse unsafe overwrite and leave no apparently complete result
   after failure;
8. emit/return a bounded machine-readable provenance record including relative
   destination, known schema/role, byte count and SHA-256 after successful write,
   but never any secret, secret hash, raw body, or arbitrary exception;
9. successful durable copy remains after deletion/cleanup of the temporary
   source;
10. export performs zero network, provider, model, service, credential, Git
    staging, or GitHub operations.

Do not create a general artifact-management/provenance framework. Integrate the
export at the narrow pre-cleanup acceptance boundary or provide the minimal
explicit callable/CLI that future orders can invoke reliably, and document its
exact usage and failure semantics.

## D. Required CPU-only regressions

Use synthetic safe values only. At minimum prove:

1. one valid protected result exports;
2. one valid fake result exports;
3. output bytes and/or hash semantics are deterministic;
4. unknown top-level and nested fields are rejected;
5. missing required fields are rejected;
6. raw-body/prompt/model-output/tool-output/image/source/private-URL-like
   structures are rejected, not stripped;
7. credential/token/signature/nonce/private-ID-bearing structures are rejected;
8. traversal/absolute escape outside evidence root is rejected;
9. destination/component symlink abuse is rejected;
10. validation/write/rename failure leaves no valid-looking final artifact;
11. durable export survives deletion of its temporary source;
12. returned provenance and SHA-256 match exact committed bytes;
13. exporter makes zero network/provider/model calls and no Git staging/commit;
14. each legitimately distinct fake/protected schema is explicit rather than an
    arbitrary JSON mapping;
15. runtime wheel contains neither the acceptance exporter nor evidence payload,
    fixtures, OAP files, tests, or new runtime dependency.

Also add focused tests of the exact historical audit/manifest contract using
synthetic fixtures; tests must never require the historical `/tmp` artifacts in
ordinary CI.

## E. Scope, security, documentation, and correction

No changes to Local production runtime, Gateway, current peer-authority fixture,
Qwen/vLLM, model/service/profile/configuration, GPU, ports, network/firewall/VPN,
credentials, systemd, deployment, or release. No protected inference, historical
experiment rerun, external service, or shared-filesystem assumption. Do not
delete the four historical source artifacts. Preserve unrelated empty untracked
`Local`, `clean`, and `unchanged` files.

Update only the relevant acceptance/testing/runbook documentation to explain
explicit safe export before cleanup, exact allowed evidence root, schema/privacy
failure behavior, post-hoc historical preservation, and missing-old-artifact
semantics. Do not overclaim that new committed evidence existed during Objective
005 or that durable preservation changes technical acceptance.

Do not edit immutable Objective-007 order/report. The new immutable 008-a report
must include this concise historical correction:

> The Objective-007 work order stated that the human selected Luna; that
> statement came from supplied work-order text and was not an intentional human
> model-selection decision. Objective-007's technical result remains accepted
> because it is grounded in committed source and independently verified CI, not
> executor identity.

Strategy will independently post or cross-link the same correction on PR #9
during final review; do not redo Objective 007.

## F. Verification and GitHub/report closure

Run and record:

- focused evidence audit/export/security/atomicity/symlink/no-network tests;
- complete normal `uv run --frozen pytest -q` with exact pass/skip result;
- `uv run --frozen ruff check .` and `ruff format --check .`;
- `uv run --frozen mypy src tests` plus any script path not covered by config;
- `uv build`, compileall, and shell syntax checks;
- independent privacy/content scan of every newly committed historical evidence
  JSON, not only exporter success;
- wheel entry/metadata/byte inspection proving no new runtime payload/dependency
  and unchanged production source;
- `git diff --check`, immutable-history/pin checks, and exact changed-path review;
- GitHub PR-head ordinary `test` and current `gateway-contract`, both successful.

Fix every safe in-scope local/CI issue in this same branch. Review the production
and package delta separately from OAP evidence. No Qwen/provider/GPU/service test
is required or authorized. Historical absence/rejection is not failure when
truthfully manifested; unsafe evidence must never be committed merely to make
the historical half look complete.

Only after all non-report work is pushed and the one PR is green, publish exactly
`oap/reports/008-a-durable-acceptance-evidence.md`. It must contain the literal
implementation head and `Report publication commit: SELF`; the final report-only
commit's first parent is that implementation SHA. Report exact remote Local
base/PR/branch/SHAs, per-artifact availability/type/size/original+committed hash
and validation result, manifest path/hash, exporter design and tests, independent
privacy/wheel/source review, CI run/job IDs, no-model/no-service facts, the
Objective-007 correction, and all limitations. Do not include raw artifact
content or private paths beyond the four already-authorized historical names.

Coding never merges. Verify report bytes/path/parent and remote PR head, then
send exact response FIFO `OK`. Strategy independently reads every newly committed
historical JSON, verifies report SELF/PR/diff/checks/security/package, adds the
Objective-007 correction, and merges only when all criteria are satisfied. After
merge, strategy verifies remote main and both merged-main `test` and
`gateway-contract` jobs.

# OAP Work Order — 005-e

## Objective

Amend Objective-005 PR #7 with the Local Coding side of the directly evidenced
Codex/gateway tool-envelope contract: an explicit route-scoped Responses policy
that removes only disabled client tool declarations `tool_search` and
`web_search` before Qwen, while preserving ordinary function/custom tools and
tool call/results. Add cross-repository conformance vectors and an exact
non-active gateway change proposal. Do not modify the gateway, run live model/
gateway services, or claim compatibility/cutover before gateway authorization.

## GitHub objective state

- Repository: `ulfe-lmi/slaif-local-coding`.
- Numeric objective / round: `005` / `005-e`.
- PR mode: `AMEND_EXISTING_PR`; **NO NEW PR**.
- Existing PR #7:
  `https://github.com/ulfe-lmi/slaif-local-coding/pull/7`.
- Base/head: `main` / `oap/005-gateway-ingress-integration`.
- Current verified remote head / 005-d SELF:
  `9707473dbdd9fbc6aa88e925f82409d56f406e34`.
- 005-d implementation parent:
  `7120c52a75daa8df676fa0f511f3ad497e5c60b1`.
- PR OPEN/non-draft/MERGEABLE/CLEAN; report-head `test` SUCCESS.
- Same PR only; coding never merges or enables auto-merge.

## Direct evidence and architecture decision

The bounded 005-d differential proves every supported Codex 0.149 disposable
configuration retains `web_search`; three variants also retain `tool_search`.
Pinned gateway policy rejects them with
`responses_hosted_tool_not_supported` before reservation. No configuration-only
path exists.

The required architecture boundary is:

- Gateway decides whether an exact authenticated route may reach Local Coding;
- Local Coding owns model/client compatibility transformation;
- Qwen must not receive tool declarations that the route intentionally disables;
- public/provider hosted-tool authority must never be silently enabled.

This order implements only Local Coding transformation and proposal evidence.
The gateway remains unchanged and continues to reject the request today.

## A. Explicit route tool policy

Extend `RouteConfig` with a versioned, disabled-by-default Responses tool policy,
using a typed shape such as:

```toml
responses_tool_policy = "passthrough"
# or
responses_tool_policy = "drop_disabled_codex_search"
```

Requirements for `drop_disabled_codex_search`:

1. Apply only to `/v1/responses` on an explicitly selected route; Chat and all
   defaults remain byte/semantic passthrough.
2. Parse only the bounded already-validated JSON request.
3. Inspect only the top-level `tools` list.
4. Remove declarations whose exact `type` is `tool_search` or `web_search`.
5. Preserve every other tool declaration byte-semantically/order-wise,
   including `function`, `custom`, namespaces, and unknown types not explicitly
   dropped; never rewrite names/schemas/arguments.
6. Preserve all `input` tool-call/result items and continuation state exactly.
7. If `tool_choice` or another explicit control selects/refers to a dropped
   type/tool, reject with fixed OpenAI-shaped 422 before compiler/upstream rather
   than silently changing requested semantics.
8. If the request contains only dropped declarations and automatic/no explicit
   choice, remove or normalize the now-empty `tools` field only according to a
   documented deterministic contract accepted by Qwen/vLLM.
9. Duplicate/malformed/non-list/oversized/deep tool structures fail closed or
   follow existing bounded JSON errors; no unbounded recursion/copy.
10. The transform runs after image policy and before constitutional observation/
    compilation/injection, with deterministic serialization and no response
    transformation.
11. Emit only safe fixed metrics: route, observed count, removed count, outcome/
    reason. No names, schemas, arguments, queries, prompts, or tool content.
12. Internal compiler calls remain direct/bypassed and never traverse this
    policy.

Do not add web-search execution, provider tools, network access, MCP, tool
translation, or fake local results.

## B. Correctness and security tests

Add exhaustive fake-upstream tests for:

- actual 005-d captured type sets:
  `function/custom/tool_search/web_search/namespace` as applicable;
- `tool_search` only, `web_search` only, both, duplicates, and interleaving;
- function/custom/namespace preservation and stable ordering;
- continuation `function_call`/`function_call_output` preservation;
- explicit dropped `tool_choice` rejection with zero upstream/compiler/cache
  work;
- automatic/none/absent tool choice behavior;
- empty/malformed/non-list/deep/large/unknown types;
- SSE/non-stream equivalence after request transform;
- image + tools + governance ordering;
- disabled/default route byte stability;
- safe metrics/log/privacy scans;
- no public/service/Qwen credential or raw tool/search content retention.

Include captured content-free tool-type fixtures only; never commit raw Codex
requests.

## C. Cross-repository conformance vectors

Version the existing gateway vector or add a new content-free vector defining:

```text
gateway precondition:
  exact authenticated local-coding route may pass the bounded Codex envelope
  without granting provider-hosted web-search execution
adapter postcondition:
  tool_search/web_search declarations removed before Qwen
  function/custom/local tool declarations preserved
  explicit dropped tool_choice rejected
accounting:
  one public gateway request remains one reservation/ledger row
  adapter compiler calls remain internal capacity only
```

Add a Local Coding conformance test consuming the vector. No gateway code is
vendored or executed in normal CI.

## D. Non-active gateway change proposal

Add/update a concise `docs/` proposal with the smallest gateway-side contract
that would be required **if the human later authorizes it after gateway PR #287
is resolved**:

- exact route capability, disabled by default;
- only provider kind `openai_compatible`, exact Local Coding provider/route;
- treats the declarations as adapter-bound client compatibility metadata, not
  gateway/provider-hosted tool authority;
- still rejects explicit hosted-tool choice/execution requests and other
  providers/routes;
- preserves quota reservation/accounting and does not strip/rewrite bodies in
  gateway;
- requires Local Coding conformance version and post-transform proof;
- full negative/security/accounting tests;
- separate gateway OAP objective/PR and human authorization.

Clearly label proposal `NOT IMPLEMENTED`, `NOT AUTHORIZED`, and not current
gateway behavior. Do not create a patch file that could be applied silently.

## E. Security containment follow-through

Preserve 005-d incident/path guards. Add a regression test that all new
tool-envelope tests/scripts use only repo fixtures/driver temp roots and never
search `HOME`, host `CODEX_HOME`, `.codex`, sessions/history/cache, or arbitrary
parents. No further no-model captures are needed; use accepted 005-d facts.

Do not delete/rotate sessions or credentials. Documentation may recommend human
review of active OpenAI-style keys due residual uncertainty, without claiming a
known compromise.

## F. Verification and protected safety

Run focused route-tool/conformance/privacy/path tests and full frozen Ruff/
format/mypy/pytest/build/wheel/compileall/shell/diff/secret/raw-log scans plus
current CI.

No Docker/Postgres/gateway/adapter listener, no Qwen API/model call, no service/
profile/network change. Vision remains active, text inactive, 18020 present,
18021/18031 absent.

## Completeness

Do not advance Objective-005 completion from this adapter-side preparation
alone. The gateway still rejects actual Codex traffic, trusted per-user identity
is absent, and full cutover is unproven.

## Publication contract

Amend only PR #7; never create another PR or merge. Push all non-report work,
record literal implementation SHA, then publish exactly one immutable
`oap/reports/005-e-route-scoped-codex-tool-filter-contract.md` with literal SHA
and `Report publication commit: SELF`. SELF changes only report, parent equals
implementation SHA, and is remote head before FIFO `OK`.

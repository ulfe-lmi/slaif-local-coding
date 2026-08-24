# Gateway route-scoped Codex tool-filter proposal

NOT IMPLEMENTED · NOT AUTHORIZED · proposal only

This document is the smallest gateway-side contract that could authorize the
Local Coding adapter-side compatibility policy after gateway PR #287 is
resolved. It is not current gateway behavior. The gateway currently rejects
the affected Codex envelope with responses_hosted_tool_not_supported, and this
repository does not modify or vendor gateway code.

## Proposed precondition

The gateway may pass a bounded Codex Responses envelope only when all of these
conditions hold:

- the request has an exact authenticated route capability explicitly enabling
  the versioned Local Coding compatibility contract;
- the provider kind is exactly openai_compatible;
- the selected provider and route are the exact Local Coding adapter provider
  and route, with the capability disabled by default;
- the adapter conformance vector is the agreed version and the adapter proves
  the post-transform contract.

The capability describes client-compatibility metadata for the adapter. It does
not grant provider-hosted web search, tool_search, MCP, network access, or
execution authority to the gateway or Qwen.

## Required gateway behavior

The gateway must continue to reject explicit hosted-tool choice or execution
requests, and must reject the same envelope for every other provider or route.
It must preserve the request body and leave tool_search/web_search declaration
removal to Local Coding. Public quota reservation, one-request/one-ledger-row
accounting, authentication, permissions, and provider usage finalization remain
gateway responsibilities. Adapter compiler calls are internal capacity only and
never public reservations.

The gateway change requires a separate OAP objective and PR, human
authorization, full negative/security tests, accounting tests, and a
cross-repository conformance check against
tests/fixtures/gateway/responses_tool_filter_vectors.json. No gateway
implementation, patch file, body rewrite, provider registration, or cutover is
included here.
